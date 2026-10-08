"""Starting-state smoke test: the warehouse tables must equal the generator's oracle, and the
planted facts (notes/agent-notes/data-contract.md) must hold in SQL.

Usage: python check_starting_state.py --profile P --warehouse W --catalog C --schema S
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

from sqlclient import query

ap = argparse.ArgumentParser()
for a in ("profile", "warehouse", "catalog", "schema"):
    ap.add_argument(f"--{a}", required=True)
args = ap.parse_args()
T = f"{args.catalog}.{args.schema}"
exp_dir = Path(__file__).resolve().parents[1] / "data-gen" / "out" / "expected"
q = lambda sql: query(sql, args.profile, args.warehouse)
fails = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    if not ok:
        fails.append(name)


# 1. Gold equals the oracle, value for value.
num = ["revenue", "operating_expense", "mgmt_fee", "capex", "intercompany", "net_profit", "net_profit_target",
       "revenue_target", "prior_quarter_net_profit", "qoq_change_pct"]
got = q(f"SELECT * FROM {T}.gold_property_quarterly ORDER BY property_id, fiscal_quarter")
exp = pd.read_csv(exp_dir / "gold_property_quarterly.csv")
check("gold rows", len(got) == len(exp) == 80, f"{len(got)} vs {len(exp)}")
for c in num:
    diff = (pd.to_numeric(got[c]).fillna(0) - exp[c].fillna(0)).abs().max()
    check(f"gold.{c}", diff <= 0.02, f"max abs diff {diff:.4f}")
check("gold.met_target", (got.met_target.map({"true": True, "false": False}) == exp.met_target).all())
check("gold.market", (got.market == exp.market).all())

for t, n in [("bronze_properties", 10), ("silver_properties", 8), ("silver_leases", 50), ("silver_tenants", 40),
             ("bronze_gl_transactions", 2696), ("silver_gl_transactions", 2681), ("customer_performance", 470)]:
    c = int(q(f"SELECT COUNT(*) AS n FROM {T}.{t}").n[0])
    check(f"{t} rows", c == n, f"{c} (expected {n})")

cp = q(f"SELECT ROUND(SUM(revenue_allocated), 0) AS r FROM {T}.customer_performance")
cpe = pd.read_csv(exp_dir / "customer_performance.csv").revenue_allocated.sum()
check("customer_performance revenue", abs(float(cp.r[0]) - cpe) < 5, f"{cp.r[0]} vs {cpe:.0f}")

# 2. Planted facts, asked the way a participant would.
m = q(f"SELECT property_name FROM {T}.gold_property_quarterly WHERE fiscal_quarter = '2026-Q2' AND NOT met_target ORDER BY 1")
check("F1 missed 2026-Q2", list(m.property_name) == ["Harbor Tower", "Peachtree Center", "Zuidas Residences"], list(m.property_name))
se = q(f"""SELECT ROUND((SUM(IF(fiscal_quarter='2026-Q2', net_profit, 0)) / SUM(IF(fiscal_quarter='2026-Q1', net_profit, 0)) - 1) * 100, 1) AS pct
           FROM {T}.gold_property_quarterly WHERE region_name = 'Southeast'""")
check("F2 Southeast Q1->Q2", -19.5 < float(se.pct[0]) < -17.5, f"{se.pct[0]}%")
mk = q(f"""SELECT market, SUM(IF(fiscal_quarter='2026-Q2', net_profit, 0)) / SUM(IF(fiscal_quarter='2026-Q1', net_profit, 0)) - 1 AS g
           FROM {T}.gold_property_quarterly GROUP BY market ORDER BY g DESC LIMIT 1""")
check("F3 top QoQ market", mk.market[0] == "Luxembourg City", mk.market[0])
gap = q(f"SELECT ROUND(SUM(capex) / SUM(net_profit) * 100, 1) AS g FROM {T}.gold_property_quarterly")
check("F4 Finance vs AM gap", 8 <= float(gap.g[0]) <= 16, f"{gap.g[0]}%")
f5 = q(f"""SELECT (SELECT COUNT(*) FROM {T}.bronze_properties WHERE region_id IS NULL) AS null_region,
                  (SELECT COUNT(*) FROM {T}.bronze_properties WHERE property_name = 'Harbor Tower') AS dup_name,
                  (SELECT COUNT(*) FROM {T}.bronze_properties b JOIN {T}.silver_properties s USING (property_id) WHERE b.market <> s.market) AS mism""")
check("F5 bronze issues", tuple(int(x) for x in f5.iloc[0]) == (2, 2, 3), tuple(f5.iloc[0]))
hv = q(f"SELECT ROUND(SUM(amount), 2) AS a FROM {T}.silver_gl_transactions WHERE description LIKE 'HV-2026-0417%' AND account_id = 5000")
check("F7 HVAC booked to OpEx", abs(float(hv.a[0]) - 312390.76) < 0.01, hv.a[0])
docs = q(f"SELECT COUNT(*) AS n FROM read_files('/Volumes/{args.catalog}/{args.schema}/documents/', format => 'binaryFile', recursiveFileLookup => true)")
check("documents in volume", int(docs.n[0]) == 15, docs.n[0])

print(f"\n{'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}'}")
sys.exit(1 if fails else 0)
