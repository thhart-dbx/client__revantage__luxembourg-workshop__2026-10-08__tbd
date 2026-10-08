"""Lay down the workshop's starting state: raw CSVs and documents in volumes, then bronze/silver/gold.

Runs as a serverless job task (resources/setup.yml). Portable: everything is parameterized, so the
same job builds the starting state in the client workspace.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--catalog", required=True)
ap.add_argument("--schema", required=True)
ap.add_argument("--as-of", required=True)
ap.add_argument("--bundle-root", required=True)
args = ap.parse_args()

root = Path(args.bundle_root.removeprefix("/Workspace").join(["/Workspace", ""]) if not args.bundle_root.startswith("/Workspace") else args.bundle_root)
volume = Path(f"/Volumes/{args.catalog}/{args.schema}")

# 1. Generate the dataset and copy it into the raw volume.
subprocess.run([sys.executable, str(root / "data-gen" / "generate.py"), "--as-of", args.as_of, "--out", "/tmp/rvlux"], check=True)
raw = volume / "raw"
for f in Path("/tmp/rvlux/raw").glob("*.csv"):
    shutil.copy(f, raw / f.name)
print(f"raw: {sorted(p.name for p in raw.iterdir())}")

# 2. Copy the documents (invoices, policies, leases) into the documents volume.
docs = volume / "documents"
for sub in ("invoices", "policies", "leases"):
    (docs / sub).mkdir(parents=True, exist_ok=True)
    for f in (root / "documents" / "out" / sub).glob("*.pdf"):
        shutil.copy(f, docs / sub / f.name)
    print(f"documents/{sub}: {len(list((docs / sub).iterdir()))} files")

# 3. Build bronze, silver, gold.
from pyspark.sql import SparkSession  # noqa: E402

spark = SparkSession.builder.getOrCreate()
for sql_file in sorted((root / "setup" / "sql").glob("*.sql")):
    text = sql_file.read_text().replace("${catalog}", args.catalog).replace("${schema}", args.schema)
    statements = [s.strip() for s in text.split(";\n") if s.strip() and not all(
        line.strip().startswith("--") or not line.strip() for line in s.strip().splitlines())]
    for stmt in statements:
        spark.sql(stmt)
    print(f"{sql_file.name}: {len(statements)} statements")

for t in ("bronze_properties", "silver_properties", "bronze_gl_transactions", "silver_gl_transactions",
          "silver_leases", "gold_property_quarterly", "customer_performance"):
    print(t, spark.table(f"{args.catalog}.{args.schema}.{t}").count())
