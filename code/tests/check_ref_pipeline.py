"""Demo 11 check: ref_d11_gold_property_quarterly must equal the oracle; report layer counts and expectations.

Usage: python check_ref_pipeline.py --profile P --warehouse W --catalog C --schema S
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from sqlclient import query

ap = argparse.ArgumentParser()
for a in ("profile", "warehouse", "catalog", "schema"):
    ap.add_argument(f"--{a}", required=True)
args = ap.parse_args()
T = f"{args.catalog}.{args.schema}"
q = lambda s: query(s, args.profile, args.warehouse)
fails = []
got = q(f"SELECT * FROM {T}.ref_d11_gold_property_quarterly ORDER BY property_id, fiscal_quarter")
exp = pd.read_csv(Path(__file__).resolve().parents[1] / "data-gen/out/expected/gold_property_quarterly.csv")
if len(got) != len(exp):
    fails.append(f"rows {len(got)} vs {len(exp)}")
for c in ["revenue", "operating_expense", "mgmt_fee", "capex", "intercompany", "net_profit", "net_profit_target", "qoq_change_pct"]:
    d = (pd.to_numeric(got[c]).fillna(0).values - exp[c].fillna(0).values)
    if abs(d).max() > 0.02:
        fails.append(f"{c} max diff {abs(d).max()}")
print(f"gold: {len(got)} rows; numeric columns vs oracle: {'OK' if not fails else fails}")
for t in ["bronze_properties", "silver_properties", "bronze_gl_transactions", "silver_gl_transactions", "bronze_leases", "silver_leases"]:
    print(f"  ref_d11_{t}: {q(f'SELECT COUNT(*) n FROM {T}.ref_d11_{t}').n[0]}")
ev = q(f"""SELECT origin.flow_name AS flow, details:flow_progress.data_quality.expectations AS e
           FROM event_log(TABLE({T}.ref_d11_gold_property_quarterly))
           WHERE event_type = 'flow_progress' AND details:flow_progress.data_quality.expectations IS NOT NULL
           ORDER BY timestamp DESC""")
seen = set()
for _, r in ev.iterrows():
    for e in json.loads(r.e):
        if e["name"] not in seen:
            seen.add(e["name"])
            print(f"  expectation {e['name']} on {e['dataset'].split('.')[-1]}: passed {e['passed_records']}, failed {e['failed_records']}")
sys.exit(1 if fails else 0)
