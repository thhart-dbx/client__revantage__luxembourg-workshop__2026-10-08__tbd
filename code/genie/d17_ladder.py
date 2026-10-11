"""Demo 17 metadata ladder: build the Genie space one layer at a time and score every rung.

Rungs (same as the participants' stages, and the Spectrix ladder):
  R1 legacy tables (abbreviated names, coded values, no metadata)
  R2 business column names              (code/reference/d17_business_layer.sql @rung R2)
  R3 + column comments                  (@rung R3)
  R4 + table descriptions, PK/FK        (@rung R4)
  R5 + governed metric views (ref_mv_*)
  R6 + text instructions
  R7 + SQL examples, synonyms, joins
Each rung gets a fresh scratch space (so Genie reads the current metadata), is scored by
code/tests/score_genie.py --record into ref_d17_benchmark_results, then the scratch space is deleted.
The spec helpers are shared with code/genie/build_spaces.py (Start = R1, Reference = R7).

Usage (from the project root):
    code/data-gen/.venv/bin/python code/genie/d17_ladder.py --profile P --warehouse W --catalog C --schema S \
        --parent /Users/<you>/spaces [--rungs R1,R2,...] [--runs 1]
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = "${var.catalog}.${var.schema}"  # placeholder in specs; replaced for API calls


def sid(text):
    return hashlib.md5(text.encode()).hexdigest()


LEGACY = ["legacy_gl_acct", "legacy_gl_txn", "legacy_lse", "legacy_prp_mstr", "legacy_qtr_tgt", "legacy_tnt"]
BUSINESS = ["ref_d17_gl_accounts", "ref_d17_gl_transactions", "ref_d17_leases", "ref_d17_properties",
            "ref_d17_quarterly_targets", "ref_d17_tenants"]
MVS = ["ref_mv_net_profit_margin", "ref_mv_qoq_revenue_growth", "ref_mv_target_attainment"]

INSTRUCTIONS = """You answer questions from Revantage finance and asset managers about the property portfolio.
- Amounts are EUR. The latest complete fiscal quarter is 2026-Q2: "this quarter" means 2026-Q2 and "last quarter" means 2026-Q1. Never use the calendar date to pick a quarter.
- Net profit (approved Finance definition) = revenue (account_class R) - operating expense (O) - management fee (M). CapEx (C) and intercompany recharges (I) are NOT deducted. Prefer the metric view ref_mv_net_profit_margin for net profit, revenue and margin.
- A property met its target when its net profit >= net_profit_target for that quarter. "Share of properties that met target" is the count of properties meeting target divided by all properties (ref_mv_target_attainment).
- ref_d17_leases keeps every version of a lease. Always use only the latest version per lease_id (highest updated_at) before counting or summing. Active means lease_status = 'A' (P = Pending Renewal, X = Expired).
- Property type codes: OFF = Office, MFH = Multifamily, RTL = Retail.
- Credit ratings from best to worst: AAA, AA, A, BBB, BB, B. "Below investment grade" means BB or B."""

EXAMPLES = [
    ("What was net profit by property in 2026-Q1?",
     f"""SELECT p.property_name,
  SUM(CASE a.account_class WHEN 'R' THEN t.amount WHEN 'O' THEN -t.amount WHEN 'M' THEN -t.amount ELSE 0 END) AS net_profit
FROM {T}.ref_d17_gl_transactions t
JOIN {T}.ref_d17_gl_accounts a ON a.account_id = t.account_id
JOIN {T}.ref_d17_properties p ON p.property_id = t.property_id
WHERE t.fiscal_quarter = '2026-Q1'
GROUP BY p.property_name"""),
    ("How many leases are pending renewal per property?",
     f"""WITH current_leases AS (
  SELECT * FROM {T}.ref_d17_leases
  QUALIFY ROW_NUMBER() OVER (PARTITION BY lease_id ORDER BY updated_at DESC) = 1)
SELECT p.property_name, COUNT(*) AS pending_renewal
FROM current_leases l JOIN {T}.ref_d17_properties p ON p.property_id = l.property_id
WHERE l.lease_status = 'P'
GROUP BY p.property_name"""),
    ("Which properties beat their net profit target last quarter?",
     f"""SELECT property_name, MEASURE(net_profit_vs_target) AS net_profit_vs_target
FROM {T}.ref_mv_target_attainment
WHERE fiscal_quarter = '2026-Q1'
GROUP BY property_name
HAVING MEASURE(net_profit_vs_target) >= 0"""),
]
SYNONYMS = {"ref_d17_properties": {"property_name": ["property", "asset", "building"], "region_name": ["region"]},
            "ref_d17_leases": {"monthly_rent": ["rent"], "lease_end": ["expiry", "expiration date"]},
            "ref_d17_quarterly_targets": {"net_profit_target": ["target", "budget", "plan"]},
            "ref_d17_tenants": {"tenant_name": ["tenant", "customer"], "credit_rating": ["rating"]}}
JOINS = [("ref_d17_gl_transactions", "ref_d17_properties", "property_id"),
         ("ref_d17_gl_transactions", "ref_d17_gl_accounts", "account_id"),
         ("ref_d17_leases", "ref_d17_properties", "property_id"),
         ("ref_d17_leases", "ref_d17_tenants", "tenant_id"),
         ("ref_d17_quarterly_targets", "ref_d17_properties", "property_id")]


def load_benchmark():
    """(question_id, question, answer_sql) from the d17_benchmark INSERT in code/setup/sql/05_d17_legacy.sql,
    with the answer SQL templated for the bundle (${var.catalog}.${var.schema})."""
    text = (ROOT / "code/setup/sql/05_d17_legacy.sql").read_text().split("d17_benchmark VALUES", 1)[1]
    lit = r"'((?:[^'\\]|\\.)*)'"
    rows = re.findall(r"\(" + r",\s*".join([lit] * 4) + r"\)", text)
    unq = lambda v: v.replace("\\'", "'").replace("${catalog}.${schema}", T)
    return [(qid, unq(q), unq(a)) for qid, q, _, a in rows]


def benchmarks(rows):
    """Native Genie benchmark block from d17_benchmark rows (question_id, question, answer_sql)."""
    qs = [{"id": sid(qid), "question": [q], "answer": [{"format": "SQL", "content": [a]}]} for qid, q, a in rows]
    return {"questions": sorted(qs, key=lambda x: x["id"])}


def spec(rung, bench_rows=()):
    """serialized_space for a rung (R1..R7)."""
    n = int(rung[1])
    tables = LEGACY if n == 1 else BUSINESS
    tbls = []
    for t in tables:
        entry = {"identifier": f"{T}.{t}"}
        if n >= 7 and t in SYNONYMS:
            entry["column_configs"] = [{"column_name": c, "synonyms": s} for c, s in sorted(SYNONYMS[t].items())]
        tbls.append(entry)
    s = {"version": 2, "config": {"sample_questions": []},
         "data_sources": {"tables": sorted(tbls, key=lambda x: x["identifier"])}}
    if n >= 5:
        s["data_sources"]["metric_views"] = [{"identifier": f"{T}.{m}"} for m in MVS]
    ins = {}
    if n >= 6:
        ins["text_instructions"] = [{"id": sid(INSTRUCTIONS), "content": [INSTRUCTIONS]}]
    if n >= 7:
        ins["example_question_sqls"] = sorted(({"id": sid(q), "question": [q], "sql": [x]} for q, x in EXAMPLES),
                                              key=lambda x: x["id"])
        ins["join_specs"] = sorted(({"id": sid(l + r), "left": {"identifier": f"{T}.{l}", "alias": l},
                                     "right": {"identifier": f"{T}.{r}", "alias": r},
                                     "sql": [f"`{l}`.`{c}` = `{r}`.`{c}`", "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--"]}
                                    for l, r, c in JOINS), key=lambda x: x["id"])
    if ins:
        s["instructions"] = ins
    if bench_rows:
        s["benchmarks"] = benchmarks(bench_rows)
    return s


def main():
    ap = argparse.ArgumentParser()
    for a in ("profile", "warehouse", "catalog", "schema", "parent"):
        ap.add_argument(f"--{a}", required=True)
    ap.add_argument("--rungs", default="R1,R2,R3,R4,R5,R6,R7")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--keep", action="store_true", help="don't delete the scratch spaces")
    args = ap.parse_args()
    fq = f"{args.catalog}.{args.schema}"
    py = sys.executable

    def api(method, path, body=None):
        cmd = ["databricks", "api", method, path, "-p", args.profile] + (["--json", json.dumps(body)] if body else [])
        return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout or "{}")

    def sql_file_section(rung):
        text = (ROOT / "code/reference/d17_business_layer.sql").read_text()
        part = re.split(r"^-- @rung ", text, flags=re.M)
        body = next(p for p in part if p.startswith(rung + ":"))
        tmp = Path(f"/tmp/d17_{rung}.sql")
        tmp.write_text(body.split("\n", 1)[1])
        subprocess.run([py, str(ROOT / "code/tests/run_sql_file.py"), str(tmp), "--profile", args.profile,
                        "--warehouse", args.warehouse, "--catalog", args.catalog, "--schema", args.schema],
                       check=True, capture_output=True)

    bench = json.loads(subprocess.run(
        ["databricks", "api", "post", "/api/2.0/sql/statements", "-p", args.profile, "--json", json.dumps(
            {"warehouse_id": args.warehouse, "statement": f"SELECT question_id, question, answer_sql FROM {fq}.d17_benchmark",
             "wait_timeout": "50s", "format": "JSON_ARRAY"})], capture_output=True, text=True).stdout)["result"]["data_array"]
    for rung in args.rungs.split(","):
        if rung in ("R2", "R3", "R4"):
            sql_file_section(rung)
        serialized = json.dumps(spec(rung, bench)).replace("${var.catalog}", args.catalog).replace("${var.schema}", args.schema)
        space = api("post", "/api/2.0/genie/spaces", {
            "title": f"[scratch] Demo 17 ladder {rung}", "warehouse_id": args.warehouse,
            "parent_path": args.parent, "serialized_space": serialized})
        space_id = space["space_id"]
        print(f"== {rung}: space {space_id}", flush=True)
        subprocess.run([py, str(ROOT / "code/tests/score_genie.py"), "--profile", args.profile, "--warehouse",
                        args.warehouse, "--catalog", args.catalog, "--schema", args.schema, "--space", space_id,
                        "--rung", rung, "--runs", str(args.runs), "--record"], check=False)
        if not args.keep:
            api("delete", f"/api/2.0/genie/spaces/{space_id}")


if __name__ == "__main__":
    main()
