"""Pre-flight: is a workspace ready to run the 16 workshop demos? Read-only; creates nothing.

Usage (from code/):
  data-gen/.venv/bin/python preflight/preflight.py --profile <profile> --warehouse <id> --catalog <catalog>
Prints one line per check and a go / no-go table per demo. Run it in the client workspace as the
facilitator, and again as one participant (system tables and Agent Bricks are often admin-gated).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from sqlclient import query  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--profile", required=True)
ap.add_argument("--warehouse", required=True)
ap.add_argument("--catalog", required=True)
args = ap.parse_args()


def cli(*a):
    r = subprocess.run(["databricks", *a, "-p", args.profile, "-o", "json"], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1][:200])
    return json.loads(r.stdout or "null")


def api(path):
    r = subprocess.run(["databricks", "api", "get", path, "-p", args.profile], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1][:200])
    return json.loads(r.stdout or "null")


def sql(s):
    return query(s, args.profile, args.warehouse)


results = {}


def check(key, label, fn):
    try:
        detail = fn() or ""
        results[key] = True
        print(f"  OK    {label}  {detail}")
    except Exception as e:  # noqa: BLE001 - report every failure, keep going
        results[key] = False
        print(f"  FAIL  {label}  {str(e)[:220]}")


def warehouse():
    w = cli("warehouses", "get", args.warehouse)
    assert w.get("enable_serverless_compute") or w.get("warehouse_type") == "PRO", f"type {w.get('warehouse_type')}"
    return f"{w['name']} ({w['state']})"


def catalog_create_schema():
    eff = cli("grants", "get-effective", "catalog", args.catalog)
    privs = {p["privilege"] for a in eff.get("privilege_assignments", []) for p in a.get("privileges", [])}
    assert privs & {"ALL_PRIVILEGES", "CREATE_SCHEMA"} or not privs, f"privileges: {sorted(privs)}"
    return "CREATE SCHEMA ok" if privs else "owner/admin (no explicit grants listed)"


def pay_per_token():
    eps = cli("serving-endpoints", "list")
    names = [e["name"] for e in eps if e["name"].startswith("databricks-")]
    assert names, "no databricks-* foundation model endpoints"
    rank = lambda n: (0 if "claude-sonnet" in n else 1 if "llama" in n else 2 if "claude" in n else 3)
    results["_llms"] = sorted(names, key=rank)
    return f"{len(names)} endpoints"


def ai_query():
    # Not every foundation endpoint supports ai_query (batch inference); find one that does.
    errors = []
    for name in results["_llms"][:6]:
        try:
            r = sql(f"SELECT ai_query('{name}', 'Reply with the single word OK') AS r")
            return f"{name}: {r.r[0][:20]}"
        except RuntimeError as e:
            errors.append(f"{name}: {str(e)[:80]}")
    raise RuntimeError("; ".join(errors))


def ai_forecast():
    sql("""SELECT * FROM AI_FORECAST(TABLE(SELECT * FROM VALUES
             (DATE'2025-01-01', 1.0), (DATE'2025-04-01', 2.0), (DATE'2025-07-01', 3.0), (DATE'2025-10-01', 4.0),
             (DATE'2026-01-01', 5.0), (DATE'2026-04-01', 6.0) AS t(d, v)),
           horizon => '2026-12-31', time_col => 'd', value_col => 'v', frequency => 'QS')""")


def ai_parse():
    sql("DESCRIBE FUNCTION ai_parse_document")


def system(table):
    return lambda: sql(f"SELECT 1 FROM {table} LIMIT 1") is not None and "SELECT ok"


checks = [
    ("warehouse", "Serverless/Pro SQL warehouse", warehouse),
    ("uc", "Unity Catalog: CREATE SCHEMA in catalog", catalog_create_schema),
    ("fm", "Foundation model (pay-per-token) endpoints", pay_per_token),
    ("ai_query", "ai_query() on a foundation model", ai_query),
    ("ai_forecast", "ai_forecast() quarterly", ai_forecast),
    ("ai_parse", "ai_parse_document() available", ai_parse),
    ("genie", "Genie Agents API", lambda: f"{len(api('/api/2.0/genie/spaces').get('spaces', []))} spaces visible"),
    ("apps", "Databricks Apps", lambda: f"{len(cli('apps', 'list'))} apps visible"),
    ("pipelines", "Lakeflow pipelines API", lambda: cli("pipelines", "list-pipelines") is not None and "ok"),
    ("lakebase", "Lakebase", lambda: f"{len(cli('database', 'list-database-instances') or [])} instances visible"),
    ("dashboards", "AI/BI dashboards API", lambda: api("/api/2.0/lakeview/dashboards?page_size=1") is not None and "ok"),
    ("sys_gateway", "system.ai_gateway.usage (SELECT)", system("system.ai_gateway.usage")),
    ("sys_serving", "system.serving.served_entities (SELECT)", system("system.serving.served_entities")),
    ("sys_billing", "system.billing.usage + list_prices (SELECT)",
     lambda: system("system.billing.usage")() and system("system.billing.list_prices")()),
    ("sys_lineage", "system.access.table_lineage (SELECT)", system("system.access.table_lineage")),
]
print(f"Pre-flight for profile {args.profile}, catalog {args.catalog}, warehouse {args.warehouse}\n")
for key, label, fn in checks:
    check(key, label, fn)

# Agent Bricks (Information Extraction, Knowledge Assistant) and Genie Code have no stable public
# API to probe; confirm them in the UI (left nav > Agents; Genie Code side panel in the SQL editor).
manual = {"agent_bricks": "Agents > Information Extraction + Knowledge Assistant tiles visible",
          "genie_code": "Genie Code panel opens in SQL editor, notebook, pipeline editor, dashboard"}
print("\n  MANUAL  " + "\n  MANUAL  ".join(f"{k}: {v}" for k, v in manual.items()))

DEMOS = {
    "D1 Platform overview": ["warehouse", "uc"],
    "D2 Genie One": ["warehouse", "genie"],
    "D3 Genie Code / Snowflake view": ["warehouse"],
    "D4 Extraction agent": ["warehouse", "ai_parse", "fm"],
    "D5 Knowledge Assistant": ["fm"],
    "D6 Data exploration": ["genie"],
    "D7 Metric views": ["warehouse", "uc"],
    "D8 Dashboards": ["dashboards", "warehouse"],
    "D9 Apps": ["apps", "warehouse"],
    "D10 Governance": ["uc", "sys_lineage"],
    "D11 Lakeflow": ["pipelines", "uc"],
    "D12 Lakebase": ["lakebase", "apps"],
    "D13 AI Gateway": ["fm", "ai_query", "sys_gateway", "sys_serving", "sys_billing"],
    "D14 Forecasting": ["ai_forecast"],
    "D15 Lab": ["genie", "dashboards", "pipelines"],
    "D16 Data quality": ["uc", "sys_lineage"],
}
print("\nDemo readiness (manual checks above still apply to D2-D6, D8, D11):")
for demo, need in DEMOS.items():
    missing = [n for n in need if not results.get(n)]
    print(f"  {'GO   ' if not missing else 'NO-GO'}  {demo}" + (f"  (missing: {', '.join(missing)})" if missing else ""))
sys.exit(0 if all(results.get(k) for k, _, _ in checks) else 1)
