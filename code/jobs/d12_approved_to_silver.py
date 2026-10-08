"""Demo 12: load Approved invoices from Lakebase (approvals.invoice_approvals) into Delta silver_invoices.

Reads with a short-lived Lakebase credential for the job's run-as identity, then MERGEs by invoice_id,
so re-runs are idempotent. Only approved records ever reach the lakehouse.
Params: --catalog --schema --instance --database
"""
import argparse
import uuid

import psycopg
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession

ap = argparse.ArgumentParser()
for a in ("catalog", "schema", "instance", "database"):
    ap.add_argument(f"--{a}", required=True)
args = ap.parse_args()

w = WorkspaceClient()
# REST rather than w.database.*, which older SDKs on serverless environments don't have.
inst = w.api_client.do("GET", f"/api/2.0/database/instances/{args.instance}")
cred = w.api_client.do("POST", "/api/2.0/database/credentials",
                       body={"instance_names": [args.instance], "request_id": str(uuid.uuid4())})
with psycopg.connect(host=inst["read_write_dns"], port=5432, dbname=args.database, user=w.current_user.me().user_name,
                     password=cred["token"], sslmode="require") as conn:
    rows = conn.execute("""
        SELECT invoice_id, vendor_name, property_name, total_amount::float8, currency, total_eur::float8,
               first_approver, reviewed_by, reviewed_at, notes
        FROM approvals.invoice_approvals WHERE status = 'Approved'""").fetchall()
print(f"approved invoices in Lakebase: {len(rows)}")

spark = SparkSession.builder.getOrCreate()
target = f"`{args.catalog}`.`{args.schema}`.silver_invoices"
spark.sql(f"""CREATE TABLE IF NOT EXISTS {target} (
    invoice_id STRING, vendor_name STRING, property_name STRING, total_amount DECIMAL(18,2), currency STRING,
    total_eur DECIMAL(18,2), first_approver STRING, approved_by STRING, approved_at TIMESTAMP, notes STRING,
    loaded_at TIMESTAMP) COMMENT 'Approved invoices from the Lakebase approval workflow (Demo 12)'""")
if rows:
    schema = ("invoice_id STRING, vendor_name STRING, property_name STRING, total_amount DOUBLE, currency STRING, "
              "total_eur DOUBLE, first_approver STRING, approved_by STRING, approved_at TIMESTAMP, notes STRING")
    spark.createDataFrame(rows, schema).createOrReplaceTempView("approved")
    spark.sql(f"""MERGE INTO {target} t USING (
        SELECT invoice_id, vendor_name, property_name, CAST(total_amount AS DECIMAL(18,2)) total_amount, currency,
               CAST(total_eur AS DECIMAL(18,2)) total_eur, first_approver, approved_by, approved_at, notes,
               current_timestamp() loaded_at FROM approved) s
      ON t.invoice_id = s.invoice_id
      WHEN MATCHED THEN UPDATE SET *
      WHEN NOT MATCHED THEN INSERT *""")
print(f"silver_invoices rows: {spark.table(target).count()}")
