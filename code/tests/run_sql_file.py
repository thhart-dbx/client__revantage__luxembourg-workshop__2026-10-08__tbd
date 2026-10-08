"""Run a ${catalog}/${schema}-templated SQL file statement by statement on a warehouse."""
import argparse
from pathlib import Path

from sqlclient import query

ap = argparse.ArgumentParser()
ap.add_argument("file")
for a in ("profile", "warehouse", "catalog", "schema"):
    ap.add_argument(f"--{a}", required=True)
args = ap.parse_args()
text = Path(args.file).read_text().replace("${catalog}", args.catalog).replace("${schema}", args.schema)
# Split on ';' at line end, but not inside $$ ... $$ blocks.
stmts, buf, in_dollar = [], [], False
for line in text.splitlines():
    if line.count("$$") % 2:
        in_dollar = not in_dollar
    buf.append(line)
    if not in_dollar and line.rstrip().endswith(";"):
        stmts.append("\n".join(buf).strip().rstrip(";"))
        buf = []
if "".join(buf).strip():
    stmts.append("\n".join(buf).strip())
for s in stmts:
    body = "\n".join(l for l in s.splitlines() if not l.strip().startswith("--")).strip()
    if body:
        query(body, args.profile, args.warehouse)
        print("ok:", body.splitlines()[0][:100])
