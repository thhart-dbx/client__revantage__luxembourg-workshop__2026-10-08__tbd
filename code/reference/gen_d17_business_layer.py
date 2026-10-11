"""Regenerate code/reference/d17_business_layer.sql from legacy_data_dictionary (run after editing the
dictionary in code/setup/sql/05_d17_legacy.sql and reloading it).

Usage (from the project root): python3 code/reference/gen_d17_business_layer.py PROFILE WAREHOUSE CATALOG SCHEMA
"""
import json
import subprocess
import sys

PROFILE, WAREHOUSE, CATALOG, SCHEMA = sys.argv[1:5]
FQ = f"{CATALOG}.{SCHEMA}"


def run(sql):
    r = json.loads(subprocess.run(["databricks", "api", "post", "/api/2.0/sql/statements", "-p", PROFILE, "--json", json.dumps(
        {"warehouse_id": WAREHOUSE, "statement": sql, "wait_timeout": "50s", "format": "JSON_ARRAY"})],
        capture_output=True, text=True).stdout)
    return r["result"]["data_array"]


rows = run(f"SELECT table_name, column_name, business_name, description FROM {FQ}.legacy_data_dictionary")
order = ["legacy_prp_mstr","legacy_gl_acct","legacy_gl_txn","legacy_lse","legacy_tnt","legacy_qtr_tgt"]
T = "${catalog}.${schema}"
tables = {t: next(r for r in rows if r[0]==t and r[1] is None) for t in order}
cols = {t: [r for r in rows if r[0]==t and r[1] is not None] for t in order}
# keep the column order of the legacy tables
colorder = {t: [c[0] for c in run(f"DESCRIBE {FQ}.{t}") if c[0] and not c[0].startswith('#')] for t in order}
q = lambda s: s.replace("'", "\\'")
out = ["-- Demo 17 reference: the legacy warehouse turned into a documented business layer (ref_d17_*).",
       "-- Generated from legacy_data_dictionary. The ladder (code/genie/d17_ladder.py) runs the rungs in order and",
       "-- scores a fresh Genie space after each; participants build the same thing in <my_schema> with Genie Code.",
       "", "-- @rung R2: business column names (values and codes unchanged)",
       "-- Drop first: CREATE OR REPLACE TABLE ... AS SELECT keeps the old table and column comments."]
for bn in ["gl_transactions", "leases", "quarterly_targets", "properties", "gl_accounts", "tenants"]:
    out.append(f"DROP TABLE IF EXISTS {T}.ref_d17_{bn};")
for t in order:
    bn = tables[t][2]
    m = {c[1]: c[2] for c in cols[t]}
    sel = ", ".join(f"{c} AS {m[c]}" for c in colorder[t])
    out.append(f"CREATE OR REPLACE TABLE {T}.ref_d17_{bn} AS SELECT {sel} FROM {T}.{t};")
out += ["", "-- @rung R3: column comments"]
for t in order:
    bn = tables[t][2]
    for c in cols[t]:
        out.append(f"ALTER TABLE {T}.ref_d17_{bn} ALTER COLUMN {c[2]} COMMENT '{q(c[3])}';")
out += ["", "-- @rung R4: table descriptions, primary and foreign keys (informational)"]
for t in order:
    bn = tables[t][2]
    desc = tables[t][3].replace("legacy_prp_mstr","ref_d17_properties").replace("legacy_gl_acct","ref_d17_gl_accounts").replace("legacy_tnt","ref_d17_tenants")
    for a,b in [("PRP_ID","property_id"),("ACCT_ID","account_id"),("TXN_ID","transaction_id"),("LSE_ID","lease_id"),("UPD_DT","updated_at"),("TNT_ID","tenant_id"),("FSCL_QTR","fiscal_quarter"),("ACCT_CLS_CD","account_class")]:
        desc = desc.replace(a,b)
    out.append(f"COMMENT ON TABLE {T}.ref_d17_{bn} IS '{q(desc)}';")
pk = {"properties":["property_id"],"gl_accounts":["account_id"],"gl_transactions":["transaction_id"],"leases":["lease_id","updated_at"],"tenants":["tenant_id"],"quarterly_targets":["property_id","fiscal_quarter"]}
for bn, keys in pk.items():
    for k in keys:
        out.append(f"ALTER TABLE {T}.ref_d17_{bn} ALTER COLUMN {k} SET NOT NULL;")
    out.append(f"ALTER TABLE {T}.ref_d17_{bn} ADD CONSTRAINT ref_d17_{bn}_pk PRIMARY KEY ({', '.join(keys)});")
fks = [("gl_transactions","property_id","properties"),("gl_transactions","account_id","gl_accounts"),("leases","property_id","properties"),("leases","tenant_id","tenants"),("quarterly_targets","property_id","properties")]
for t,c,r in fks:
    out.append(f"ALTER TABLE {T}.ref_d17_{t} ADD CONSTRAINT ref_d17_{t}_{c}_fk FOREIGN KEY ({c}) REFERENCES {T}.ref_d17_{r};")
open("code/reference/d17_business_layer.sql","w").write("\n".join(out)+"\n")
print(len(out), "lines")
