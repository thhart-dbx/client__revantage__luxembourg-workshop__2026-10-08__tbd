"""Score a Genie Agent against the Demo 17 benchmark (d17_benchmark) and record the result.

For each benchmark question: ask the space (fresh conversation), fetch the rows of the SQL Genie ran,
run the ground-truth SQL, and compare. An answer is correct when it has the same number of rows and
every ground-truth column matches some column of Genie's result (any order, values within 0.5 %;
a ratio also matches when Genie gives it in percent). Extra columns are fine.

Usage (from the project root):
    code/data-gen/.venv/bin/python code/tests/score_genie.py --profile P --warehouse W --catalog C \
        --schema S --space SPACE_ID --rung R1 [--record] [--runs 1]
--record appends one row per question and run to <catalog>.<schema>.ref_d17_benchmark_results.
"""
import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
for a in ("profile", "warehouse", "catalog", "schema", "space", "rung"):
    ap.add_argument(f"--{a}", required=True)
ap.add_argument("--record", action="store_true")
ap.add_argument("--runs", type=int, default=1)
ap.add_argument("--only", help="comma-separated question ids")
args = ap.parse_args()
T = f"{args.catalog}.{args.schema}"


def api(method, path, body=None):
    cmd = ["databricks", "api", method, path, "-p", args.profile] + (["--json", json.dumps(body)] if body else [])
    for attempt in range(4):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout or "{}")
        if "RESOURCE_EXHAUSTED" in r.stderr or "429" in r.stderr or "REQUEST_LIMIT" in r.stderr:
            time.sleep(10 * (attempt + 1))
            continue
        raise RuntimeError(r.stderr.strip())
    raise RuntimeError(r.stderr.strip())


def sql(statement):
    r = api("post", "/api/2.0/sql/statements", {"warehouse_id": args.warehouse, "statement": statement,
                                                "wait_timeout": "50s", "format": "JSON_ARRAY"})
    while r["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(2)
        r = api("get", f"/api/2.0/sql/statements/{r['statement_id']}")
    if r["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(r["status"].get("error", {}).get("message", r["status"]["state"]))
    return r.get("result", {}).get("data_array", []) or []


def num(v):
    try:
        return None if v is None or isinstance(v, bool) else float(v)
    except (TypeError, ValueError):
        return None


def same(a, b, tol=0.005):
    fa, fb = num(a), num(b)
    if fa is not None and fb is not None:
        if abs(fa - fb) <= tol * max(abs(fa), abs(fb), 1e-9):
            return True
        return 0 < abs(fb) <= 1 and abs(fa - 100 * fb) <= tol * max(abs(fa), 1e-9)  # ratio given in percent
    return str(a).strip().lower() == str(b).strip().lower()


def column_match(truth_col, genie_col):
    key = lambda v: (num(v) is None, num(v) if num(v) is not None else str(v).strip().lower())
    return all(same(g, t) for g, t in zip(sorted(genie_col, key=key), sorted(truth_col, key=key)))


def correct(genie_rows, truth_rows):
    if len(genie_rows) != len(truth_rows) or not truth_rows:
        return False
    gcols = list(zip(*genie_rows))
    return all(any(column_match(tc, gc) for gc in gcols) for tc in zip(*truth_rows))


def ask(question):
    base = f"/api/2.0/genie/spaces/{args.space}"
    r = api("post", f"{base}/start-conversation", {"content": question})
    conv, msg = r["conversation_id"], r["message"]
    mid = msg.get("message_id") or msg.get("id")
    t0 = time.time()
    while msg.get("status") not in ("COMPLETED", "FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"):
        if time.time() - t0 > 300:
            return None, [], "TIMEOUT", time.time() - t0
        time.sleep(4)
        msg = api("get", f"{base}/conversations/{conv}/messages/{mid}")
    secs = time.time() - t0
    query = next((a["query"] for a in msg.get("attachments") or [] if a.get("query")), None)
    if not query:
        text = next((a["text"].get("content", "") for a in msg.get("attachments") or [] if a.get("text")), "")
        return None, [], f"{msg['status']}: no SQL ({text[:80]})", secs
    stmt = query.get("statement_id") or (msg.get("query_result") or {}).get("statement_id")
    rows = []
    if stmt:
        res = api("get", f"/api/2.0/sql/statements/{stmt}")
        rows = res.get("result", {}).get("data_array", []) or []
    else:
        rows = sql(query["query"])
    return query.get("query"), rows, msg["status"], secs


bench = sql(f"SELECT question_id, question, answer_sql FROM {T}.d17_benchmark ORDER BY question_id")
if args.only:
    bench = [b for b in bench if b[0] in args.only.split(",")]
truth = {qid: sql(a) for qid, _, a in bench}


def one(item):
    (qid, question, _), run = item
    try:
        gsql, rows, status, secs = ask(question)
        ok = correct(rows, truth[qid])
    except Exception as e:  # one bad question never aborts the run
        gsql, rows, status, secs, ok = None, [], f"ERROR: {e}"[:200], 0.0, False
    return qid, question, run, ok, status, secs, gsql, rows


with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    results = list(ex.map(one, [(b, r) for r in range(1, args.runs + 1) for b in bench]))

score = sum(r[3] for r in results)
for qid, question, run, ok, status, secs, gsql, rows in sorted(results):
    print(f"{'PASS' if ok else 'FAIL'}  {qid} run{run} {secs:5.1f}s  {question}  → {str(rows[:3])[:90]}  [{status}]")
print(f"\n{args.rung}: {score}/{len(results)} correct ({100 * score / len(results):.0f}%)")

if args.record:
    sql(f"""CREATE TABLE IF NOT EXISTS {T}.ref_d17_benchmark_results (
        rung STRING, space_id STRING, question_id STRING, question STRING, run INT, correct BOOLEAN,
        status STRING, seconds DOUBLE, genie_sql STRING, scored_at TIMESTAMP)
        COMMENT 'Demo 17: benchmark results per rung of the metadata ladder (code/tests/score_genie.py).'""")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    esc = lambda s: "NULL" if s is None else "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"
    values = ",\n".join(
        f"({esc(args.rung)}, {esc(args.space)}, {esc(qid)}, {esc(q)}, {run}, {str(ok).upper()}, {esc(status)}, "
        f"{secs:.1f}, {esc(gsql)}, TIMESTAMP'{now}')"
        for qid, q, run, ok, status, secs, gsql, _ in results)
    sql(f"INSERT INTO {T}.ref_d17_benchmark_results VALUES {values}")
    print(f"recorded {len(results)} rows in {T}.ref_d17_benchmark_results")
sys.exit(0)
