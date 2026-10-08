"""Run SQL against a Lakebase instance with a short-lived OAuth credential (as the CLI user).

Usage: uv run --with "psycopg[binary]" lakebase/lakebase_sql.py --profile P --instance NAME --db DB "<sql>" | -f file.sql
"""
import argparse
import json
import subprocess
import uuid

import psycopg

ap = argparse.ArgumentParser()
ap.add_argument("--profile", required=True)
ap.add_argument("--instance", required=True)
ap.add_argument("--db", default="databricks_postgres")
ap.add_argument("-f", "--file")
ap.add_argument("sql", nargs="?")
args = ap.parse_args()


def cli(*a):
    return json.loads(subprocess.run(["databricks", *a, "-p", args.profile, "-o", "json"], capture_output=True, text=True, check=True).stdout)


inst = cli("database", "get-database-instance", args.instance)
cred = cli("database", "generate-database-credential", "--json",
           json.dumps({"instance_names": [args.instance], "request_id": str(uuid.uuid4())}))
user = cli("current-user", "me")["userName"]
sql = open(args.file).read() if args.file else args.sql
with psycopg.connect(host=inst["read_write_dns"], port=5432, dbname=args.db, user=user,
                     password=cred["token"], sslmode="require", autocommit=True) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
        if cur.description:
            cols = [c.name for c in cur.description]
            print(" | ".join(cols))
            for row in cur.fetchall():
                print(" | ".join(str(v) for v in row))
        else:
            print("ok:", cur.statusmessage)
