"""Give each workshop participant a personal sandbox schema and read access to the starting state.

Participants read the shared starting data in <catalog>.<schema> and build their own objects
(metric views, pipelines, dashboards' datasets...) in <catalog>.<schema>_<name>, so live builds
don't collide. Idempotent: re-run to add people.

Params: --catalog --schema --participants "a@x.com,b@x.com" [--group revantage_workshop]
"""
import argparse
import re

from pyspark.sql import SparkSession

ap = argparse.ArgumentParser()
ap.add_argument("--catalog", required=True)
ap.add_argument("--schema", required=True)
ap.add_argument("--participants", default="")
ap.add_argument("--group", default="")
args = ap.parse_args()
spark = SparkSession.builder.getOrCreate()
base = f"`{args.catalog}`.`{args.schema}`"

principals = [p.strip() for p in args.participants.split(",") if p.strip()]
readers = principals + ([args.group] if args.group else [])
for who in readers:
    spark.sql(f"GRANT USE CATALOG ON CATALOG `{args.catalog}` TO `{who}`")
    spark.sql(f"GRANT USE SCHEMA, SELECT, READ VOLUME, EXECUTE ON SCHEMA {base} TO `{who}`")

for email in principals:
    name = re.sub(r"[^a-z0-9]+", "_", email.split("@")[0].lower()).strip("_")
    sandbox = f"`{args.catalog}`.`{args.schema}_{name}`"
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {sandbox} COMMENT 'Workshop sandbox for {email}'")
    spark.sql(f"GRANT ALL PRIVILEGES ON SCHEMA {sandbox} TO `{email}`")
    print(f"{email} -> {args.catalog}.{args.schema}_{name}")
print(f"granted read on {args.catalog}.{args.schema} to {readers or 'nobody (no participants/group given)'}")
