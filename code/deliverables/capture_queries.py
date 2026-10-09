"""Check every SQL step of the module manifest on the warehouse, then save it as a query for capture.

Usage (from the project root):
    code/data-gen/.venv/bin/python code/deliverables/capture_queries.py --profile <p> --warehouse <id> \
        --catalog <catalog> --schema <schema> --parent <workspace folder>
Prints each step's first rows (to compare with the guide's checkpoint) and writes the saved-query IDs
to notes/agent-notes/module_query_ids.json. D16 Stage 3 reads s9_d16_gold_clone (create it first).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from module_manifest import STEPS, fname  # noqa: E402

ap = argparse.ArgumentParser()
for a in ("profile", "warehouse", "catalog", "schema", "parent"):
    ap.add_argument(f"--{a}", required=True)
ap.add_argument("--only", help="comma-separated file names to (re)create")
args = ap.parse_args()


def api(method, path, body=None):
    cmd = ["databricks", "api", method, path, "-p", args.profile]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)


def run(sql):
    res = api("post", "/api/2.0/sql/statements", {
        "warehouse_id": args.warehouse, "statement": sql, "catalog": args.catalog, "schema": args.schema,
        "wait_timeout": "50s", "disposition": "INLINE", "format": "JSON_ARRAY"})
    while res["status"]["state"] in ("PENDING", "RUNNING"):
        res = api("get", f"/api/2.0/sql/statements/{res['statement_id']}")
    if res["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(res["status"])
    cols = [c["name"] for c in res["manifest"]["schema"]["columns"]]
    return cols, res.get("result", {}).get("data_array", []) or []


out = ROOT / "notes" / "agent-notes" / "module_query_ids.json"
ids = json.loads(out.read_text()) if out.exists() else {}
only = set(args.only.split(",")) if args.only else None
for key, spec in STEPS.items():
    if spec[0] != "sql":
        continue
    name = fname(key)
    if (only and name not in only) or (not only and name in ids):
        continue
    cols, rows = run(spec[1])
    print(f"== {name}: {len(rows)} rows · {cols}")
    for r in rows[:6]:
        print("   ", [str(v)[:40] for v in r])
    q = api("post", "/api/2.0/sql/queries", {"query": {
        "display_name": name.removesuffix(".png"), "warehouse_id": args.warehouse,
        "parent_path": args.parent, "catalog": args.catalog, "schema": args.schema,
        "query_text": spec[1]}})
    ids[name] = q["id"]
    out.write_text(json.dumps(ids, indent=1))
out.write_text(json.dumps(ids, indent=1))
print("saved", len(ids), "query ids →", out)
