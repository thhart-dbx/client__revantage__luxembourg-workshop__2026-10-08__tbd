"""Run ${catalog}/${schema}-templated SQL files on serverless, statement by statement.

Usage (job task): run_sql.py --catalog C --schema S --bundle-root ${workspace.file_path} [--warehouse ID] <file> ...
File paths are relative to the bundle root. Handles $$ ... $$ blocks (metric view YAML).
With --warehouse, statements run on that SQL warehouse instead of the task's compute; needed for
ai_forecast, which is disabled on serverless job compute.
"""
import argparse
from pathlib import Path

from pyspark.sql import SparkSession

ap = argparse.ArgumentParser()
ap.add_argument("--catalog", required=True)
ap.add_argument("--schema", required=True)
ap.add_argument("--bundle-root", required=True)
ap.add_argument("--warehouse", default="")
ap.add_argument("files", nargs="+")
args = ap.parse_args()
root = Path(args.bundle_root if args.bundle_root.startswith("/Workspace") else "/Workspace" + args.bundle_root)
spark = SparkSession.builder.getOrCreate()


def run(stmt):
    if not args.warehouse:
        spark.sql(stmt)
        return
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.sql import StatementState

    w = WorkspaceClient()
    r = w.statement_execution.execute_statement(statement=stmt, warehouse_id=args.warehouse, wait_timeout="50s")
    while r.status.state in (StatementState.PENDING, StatementState.RUNNING):
        r = w.statement_execution.get_statement(r.statement_id)
    if r.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(f"{r.status.error.message if r.status.error else r.status.state}\n{stmt[:300]}")


def statements(text):
    out, buf, in_dollar = [], [], False
    for line in text.splitlines():
        if line.count("$$") % 2:
            in_dollar = not in_dollar
        buf.append(line)
        if not in_dollar and line.rstrip().endswith(";"):
            out.append("\n".join(buf))
            buf = []
    out.append("\n".join(buf))
    for s in out:
        body = "\n".join(l for l in s.splitlines() if not l.strip().startswith("--")).strip().rstrip(";").strip()
        if body:
            yield body


for f in args.files:
    text = (root / f).read_text().replace("${catalog}", args.catalog).replace("${schema}", args.schema)
    n = 0
    for stmt in statements(text):
        run(stmt)
        n += 1
    print(f"{f}: {n} statements")
