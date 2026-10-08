"""Shared dataset for the Revantage Luxembourg workshop (all 16 demos).

Writes, deterministically (fixed seed):
  out/raw/*.csv        source-system extracts (= bronze), with the planted quality issues
  out/expected/*.csv   silver + gold + customer_performance as the pipeline must produce them
  out/facts.json       the planted facts F1-F6 with actual numbers
and asserts every planted fact (see notes/claude-notes/plan.md). Amounts are EUR, the group
reporting currency; lease windows are relative to --as-of (workshop day 1).

Usage: python generate.py [--as-of 2026-10-13] [--out out]
"""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261013
QUARTERS = [f"{y}-Q{q}" for y in (2024, 2025, 2026) for q in (1, 2, 3, 4)][:10]  # 2024-Q1..2026-Q2
TARGET_QUARTERS = QUARTERS + ["2026-Q3", "2026-Q4"]
MONTHS = pd.period_range("2024-01", "2026-06", freq="M")
USD_EUR = 1.0871  # ECB reference rate used for the HVAC invoice (USD 339,600 → EUR)
HVAC_EUR = round(339_600 / USD_EUR, 2)
ANCHOR_RENT_EUR = round(118_000 / USD_EUR, 2)

REGIONS = [(1, "Southeast"), (2, "Northeast"), (3, "Western Europe")]

# id, name, region_id, clean market, property_type, monthly base revenue (EUR), quarterly growth
PROPERTIES = [
    (1, "Biscayne Point", 1, "Miami", "Multifamily", 310_000, 0.012),
    (2, "Peachtree Center", 1, "Atlanta", "Office", 420_000, 0.006),
    (3, "Harbor Tower", 1, "Miami Beach", "Office", 560_000, 0.010),
    (4, "Chelsea Lofts", 2, "New York", "Multifamily", 480_000, 0.014),
    (5, "Back Bay Commons", 2, "Boston", "Retail", 290_000, 0.008),
    (6, "Kirchberg Plaza", 3, "Luxembourg City", "Office", 520_000, 0.011),
    (7, "Cloche d'Or Retail Park", 3, "Luxembourg City", "Retail", 340_000, 0.009),
    (8, "Zuidas Residences", 3, "Amsterdam", "Multifamily", 380_000, 0.013),
]
# Raw spellings in the source system (F5); silver standardizes them.
RAW_MARKET = {3: "Miami Bch", 4: "NYC", 6: "Lux-Ville"}
# Rows the silver layer drops: NULL region_id; id 10 duplicates Harbor Tower's name (F5).
REJECTED_PROPERTIES = [(9, "Riverside Annex", None, "Charlotte", "Retail"),
                       (10, "Harbor Tower", None, "Miami Bch", "Office")]

GL_ACCOUNTS = [
    (4000, "Base Rent", "Revenue"), (4100, "Service Charge Recoveries", "Revenue"),
    (4200, "Parking & Other Income", "Revenue"),
    (5000, "Repairs & Maintenance", "OpEx"), (5100, "Utilities", "OpEx"),
    (5200, "Property Tax", "OpEx"), (5300, "Insurance", "OpEx"),
    (5400, "Cleaning & Security", "OpEx"), (5500, "Leasing & Marketing", "OpEx"),
    (5600, "Professional & Legal Fees", "OpEx"),
    (6000, "Management Fees", "MgmtFee"),
    (7000, "Building Improvements", "CapEx"), (7100, "Tenant Improvements", "CapEx"),
    (8000, "Intercompany Charges", "Intercompany"), (8100, "Intercompany Interest", "Intercompany"),
]
REVENUE_SPLIT = {4000: 0.85, 4100: 0.11, 4200: 0.04}
OPEX_RATIO = {"Office": 0.34, "Multifamily": 0.38, "Retail": 0.30}
OPEX_SPLIT = {5000: 0.24, 5100: 0.22, 5200: 0.18, 5300: 0.10, 5400: 0.16, 5500: 0.05, 5600: 0.05}
MGMT_FEE_RATE = 0.03
INTERCO_RATE = 0.015
SEASONALITY = {  # by property type, quarter-of-year multiplier
    "Office": {1: 1.00, 2: 1.00, 3: 0.99, 4: 1.01},
    "Multifamily": {1: 0.98, 2: 1.00, 3: 1.03, 4: 0.99},
    "Retail": {1: 0.95, 2: 1.00, 3: 0.99, 4: 1.08},
}
Q2_MISSES = {2, 3, 8}           # F1: Peachtree Center, Harbor Tower, Zuidas Residences
Q3_REVENUE_MISSES = {3, 8}      # F6: projected to miss 2026-Q3 revenue_target

INDUSTRIES = ["Healthcare", "Financial Services", "Technology", "Retail", "Food & Beverage",
              "Professional Services", "Logistics", "Media", "Education", "Public Sector"]
RATINGS = ["AAA", "AA", "A", "BBB", "BB", "B"]


def quarter_of(period):
    return f"{period.year}-Q{(period.month - 1) // 3 + 1}"


def build_gl(rng):
    rows, tx = [], 1
    q_index = {q: i for i, q in enumerate(QUARTERS)}

    def add(pid, acct, month, amount, desc, period=None):
        nonlocal tx
        rows.append(dict(transaction_id=tx, property_id=pid, account_id=acct,
                         posting_date=month.to_timestamp(how="end").date().isoformat(),
                         fiscal_period=period or quarter_of(month), amount=round(amount, 2),
                         currency="EUR", description=desc, source_system="YARDI"))
        tx += 1

    for pid, name, _, _, ptype, base, growth in PROPERTIES:
        capex_months = set(rng.choice(len(MONTHS), size=5, replace=False))
        for mi, m in enumerate(MONTHS):
            q = quarter_of(m)
            qi, qoy = q_index[q], (m.month - 1) // 3 + 1
            revenue = base * (1 + growth) ** qi * SEASONALITY[ptype][qoy] * rng.normal(1, 0.012)
            if pid == 3 and m >= pd.Period("2026-04", "M"):
                revenue -= ANCHOR_RENT_EUR  # anchor tenant Meridian Health Partners left 2026-03-31
            if pid in (6, 7) and q == "2026-Q2":
                revenue *= 1.07  # Luxembourg City: new Kirchberg suite + Cloche d'Or spring leasing (F3)
            for acct, share in REVENUE_SPLIT.items():
                add(pid, acct, m, revenue * share, f"{dict((a, n) for a, n, _ in GL_ACCOUNTS)[acct]} {m}")
            opex = revenue * OPEX_RATIO[ptype] * rng.normal(1, 0.03)
            for acct, share in OPEX_SPLIT.items():
                if acct == 5200 and m.month % 3 != 1:
                    continue  # property tax is assessed once per quarter
                amt = opex * share * (3 if acct == 5200 else 1)
                add(pid, acct, m, amt, f"{dict((a, n) for a, n, _ in GL_ACCOUNTS)[acct]} {m}")
            add(pid, 6000, m, revenue * MGMT_FEE_RATE, f"Property management fee {m}")
            if m.month % 3 == 0:
                q_rev = revenue * 3
                add(pid, 8000, m, q_rev * INTERCO_RATE, f"Shared-services recharge {q}")
                add(pid, 8100, m, q_rev * 0.004, f"Intercompany loan interest {q}")
            if mi in capex_months:
                add(pid, int(rng.choice([7000, 7100])), m, base * rng.uniform(0.25, 0.55),
                    f"Capital project {m}")
        if pid == 3:  # F2/F7: the chiller replacement, booked to R&M (OpEx) instead of CapEx
            add(3, 5000, pd.Period("2026-05", "M"), HVAC_EUR,
                "HV-2026-0417 Coastal Climate Systems LLC - rooftop chiller replacement (USD 339,600 @ 1.0871)")

    # Malformed fiscal_period: a zero-sum accrual set the pipeline's expectation must drop (Demo 11).
    for amt in (500.0, 700.0, -1200.0):
        add(5, 5400, pd.Period("2026-05", "M"), amt, "Accrual adjustment (manual upload)", period="2026Q2")
    # Transactions for the two properties the silver layer rejects (Demo 6 bronze vs gold gap).
    for pid in (9, 10):
        for m in MONTHS[-6:]:
            add(pid, 4000, m, 95_000 * rng.normal(1, 0.02), f"Base Rent {m}")
    return pd.DataFrame(rows)


def build_tenants_leases(rng, as_of):
    named = [("Meridian Health Partners", "Healthcare", "BBB"),
             ("Nordlicht Asset Advisory S.A.", "Financial Services", "A"),
             ("Grachten Coffee B.V.", "Food & Beverage", "BB")]
    first = ["Atlas", "Beacon", "Cedar", "Delta", "Ember", "Fjord", "Granite", "Helix", "Iris", "Juniper",
             "Kestrel", "Lumen", "Mosaic", "Nimbus", "Orchid", "Pinnacle", "Quarry", "Rhine", "Summit",
             "Tidal", "Umbra", "Vertex", "Willow", "Xylo", "Yarrow", "Zenith", "Alder", "Brook",
             "Cobalt", "Dune", "Elm", "Flint", "Grove", "Harbor", "Indigo", "Jade", "Keel"]
    suffix = ["Group", "Partners", "Labs", "S.A.", "LLC", "B.V.", "Holdings", "& Co"]
    tenants = []
    for i in range(40):
        if i < 3:
            nm, ind, rating = named[i]
        else:
            nm = f"{first[i - 3]} {suffix[i % len(suffix)]}"
            ind = INDUSTRIES[i % len(INDUSTRIES)]
            rating = RATINGS[int(rng.choice(6, p=[0.05, 0.15, 0.3, 0.3, 0.12, 0.08]))]
        slug = "".join(c for c in nm.lower().split()[0] if c.isalpha())
        tenants.append(dict(tenant_id=i + 1, tenant_name=nm, industry=ind, credit_rating=rating,
                            contact_name=f"{['Anna', 'Luc', 'Sofia', 'Marc', 'Elena', 'Tom'][i % 6]} {first[i % len(first)]}",
                            contact_email=f"leasing@{slug}.example.com",
                            contact_phone=f"+352 {int(rng.integers(200, 699))} {int(rng.integers(100, 999))} {int(rng.integers(100, 999))}"))

    # Bucket plan relative to as_of: 4 expired, 6 ≤90d, 8 91-180d, 10 181-365d, 22 >365d (50 leases).
    fixed = [  # leases that match the lease PDFs
        dict(property_id=3, tenant_id=1, lease_start=date(2021, 4, 1), lease_end=date(2026, 3, 31), monthly_rent=ANCHOR_RENT_EUR),
        dict(property_id=6, tenant_id=2, lease_start=date(2022, 1, 1), lease_end=date(2027, 1, 15), monthly_rent=46_500.0),
        dict(property_id=8, tenant_id=3, lease_start=date(2023, 7, 1), lease_end=date(2026, 12, 31), monthly_rent=9_800.0),
    ]
    buckets = {"expired": (-240, -20, 4), "90": (5, 90, 6), "180": (91, 180, 8), "365": (181, 365, 10), "long": (366, 1500, 22)}
    for lease in fixed:
        days = (lease["lease_end"] - as_of).days
        key = "expired" if days < 0 else "90" if days <= 90 else "180" if days <= 180 else "365" if days <= 365 else "long"
        lo, hi, n = buckets[key]
        buckets[key] = (lo, hi, n - 1)
    leases = list(fixed)
    tenant_cycle = iter(rng.permutation(np.arange(4, 41)).tolist() * 2)
    pids = [p[0] for p in PROPERTIES]
    for key, (lo, hi, n) in buckets.items():
        for _ in range(n):
            end = as_of + timedelta(days=int(rng.integers(lo, hi + 1)))
            start = end - timedelta(days=int(rng.choice([3, 5, 7, 10])) * 365)
            leases.append(dict(property_id=int(rng.choice(pids)), tenant_id=int(next(tenant_cycle)),
                               lease_start=start, lease_end=end,
                               monthly_rent=round(float(rng.uniform(6_000, 60_000)), 2)))
    df = pd.DataFrame(leases)
    df = df.sort_values(["lease_end", "property_id"]).reset_index(drop=True)
    df.insert(0, "lease_id", [f"L-{1001 + i}" for i in range(len(df))])
    days = (pd.to_datetime(df.lease_end) - pd.Timestamp(as_of)).dt.days
    status = np.where(days < 0, "Expired", "Active").astype(object)
    soon = df.index[(days >= 0) & (days <= 180)]
    status[soon[::2]] = "Pending Renewal"
    df["lease_status"] = status
    df["updated_at"] = pd.Timestamp(as_of) - pd.Timedelta(days=3)
    # Two stale versions of the same lease_id (silver keeps the latest by updated_at).
    stale = df[df.lease_status == "Pending Renewal"].head(2).copy()
    stale["lease_status"], stale["updated_at"] = "Active", pd.Timestamp(as_of) - pd.Timedelta(days=60)
    raw = pd.concat([df, stale]).sort_values(["lease_id", "updated_at"]).reset_index(drop=True)
    return pd.DataFrame(tenants), raw, df


def build_gold(gl, accounts, props):
    g = gl.merge(accounts[["account_id", "category"]], on="account_id")
    g["fiscal_quarter"] = g.fiscal_period
    piv = g.pivot_table(index=["property_id", "fiscal_quarter"], columns="category", values="amount",
                        aggfunc="sum", fill_value=0).reset_index()
    piv = piv.rename(columns={"Revenue": "revenue", "OpEx": "operating_expense", "MgmtFee": "mgmt_fee",
                              "CapEx": "capex", "Intercompany": "intercompany"})
    gold = props.merge(piv, on="property_id")
    gold["net_profit"] = gold.revenue - gold.operating_expense - gold.mgmt_fee  # Finance definition
    for c in ["revenue", "operating_expense", "mgmt_fee", "capex", "intercompany", "net_profit"]:
        gold[c] = gold[c].round(2)
    gold["fiscal_quarter_date"] = pd.PeriodIndex(gold.fiscal_quarter.str.replace("-", ""), freq="Q").start_time.date
    return gold.sort_values(["property_id", "fiscal_quarter"]).reset_index(drop=True)


def build_targets(rng, gold):
    rows = []
    for pid, grp in gold.groupby("property_id"):
        grp = grp.set_index("fiscal_quarter")
        # simple seasonal-naive-with-trend projection for the two future quarters
        rev = grp.revenue
        trend = (rev.iloc[-4:].mean() / rev.iloc[-8:-4].mean()) ** 0.25
        proj = {"2026-Q3": rev["2025-Q3"] * trend ** 4, "2026-Q4": rev["2025-Q4"] * trend ** 4}
        for q in TARGET_QUARTERS:
            if q in grp.index:
                np_actual, rev_actual = grp.at[q, "net_profit"], grp.at[q, "revenue"]
                if q == "2026-Q2":
                    f = rng.uniform(1.04, 1.09) if pid in Q2_MISSES else rng.uniform(0.90, 0.97)
                else:
                    f = rng.uniform(0.90, 1.04)
                npt, rvt = np_actual * f, rev_actual * rng.uniform(0.97, 1.03)
            else:
                rvt = proj[q] * (1.07 if (q == "2026-Q3" and pid in Q3_REVENUE_MISSES) else 0.96)
                npt = rvt * float((grp.net_profit / grp.revenue).iloc[-4:].mean())
            rows.append(dict(property_id=pid, fiscal_quarter=q, net_profit_target=round(npt, -2),
                             revenue_target=round(rvt, -2)))
    return pd.DataFrame(rows)


def finish_gold(gold, targets):
    gold = gold.merge(targets, on=["property_id", "fiscal_quarter"], how="left")
    gold["met_target"] = gold.net_profit >= gold.net_profit_target
    gold["prior_quarter_net_profit"] = gold.groupby("property_id").net_profit.shift(1)
    gold["qoq_change_pct"] = ((gold.net_profit - gold.prior_quarter_net_profit)
                              / gold.prior_quarter_net_profit.abs() * 100).round(2)
    cols = ["property_id", "property_name", "property_type", "region_name", "market", "fiscal_quarter",
            "fiscal_quarter_date", "revenue", "operating_expense", "mgmt_fee", "capex", "intercompany",
            "net_profit", "net_profit_target", "revenue_target", "met_target", "prior_quarter_net_profit",
            "qoq_change_pct"]
    return gold[cols]


def build_customer_performance(gold, leases, tenants):
    rows = []
    for _, g in gold.iterrows():
        q = pd.Period(g.fiscal_quarter.replace("-", ""), freq="Q")
        qs, qe = q.start_time.date(), q.end_time.date()
        act = leases[(leases.property_id == g.property_id) & (leases.lease_start <= qe) & (leases.lease_end >= qs)]
        if act.empty:
            continue
        months = act.apply(lambda r: max(0, min(3, ((min(r.lease_end, qe).year - max(r.lease_start, qs).year) * 12
                                                    + min(r.lease_end, qe).month - max(r.lease_start, qs).month + 1))), axis=1)
        billed = act.monthly_rent * months
        share = billed / billed.sum()
        for (_, l), b, s in zip(act.iterrows(), billed, share):
            rows.append(dict(property_id=g.property_id, property_name=g.property_name, region_name=g.region_name,
                             tenant_id=l.tenant_id, fiscal_quarter=g.fiscal_quarter, rent_billed=round(b, 2),
                             revenue_allocated=round(g.revenue * s, 2), net_profit_allocated=round(g.net_profit * s, 2)))
    cp = pd.DataFrame(rows).merge(tenants, on="tenant_id")
    return cp[["property_id", "property_name", "region_name", "tenant_id", "tenant_name", "industry", "credit_rating",
               "contact_email", "contact_phone", "fiscal_quarter", "rent_billed", "revenue_allocated",
               "net_profit_allocated"]].sort_values(["property_id", "tenant_id", "fiscal_quarter"])


def assert_facts(gold, bronze_props, silver_props, targets):
    facts = {}
    q2 = gold[gold.fiscal_quarter == "2026-Q2"]
    missed = q2[~q2.met_target]
    facts["F1_q2_2026_missed_target"] = sorted(missed.property_name)
    assert set(missed.property_id) == Q2_MISSES, missed

    se = gold[gold.region_name == "Southeast"].groupby("fiscal_quarter").net_profit.sum()
    se_chg = (se["2026-Q2"] / se["2026-Q1"] - 1) * 100
    ht = gold[(gold.property_id == 3)].set_index("fiscal_quarter")
    facts["F2_southeast_np_q1_q2_2026_pct"] = round(se_chg, 1)
    facts["F2_southeast_np"] = {"2026-Q1": round(se["2026-Q1"]), "2026-Q2": round(se["2026-Q2"])}
    facts["F2_harbor_tower_np"] = {"2026-Q1": round(ht.at["2026-Q1", "net_profit"]), "2026-Q2": round(ht.at["2026-Q2", "net_profit"])}
    facts["F2_harbor_tower_revenue"] = {"2026-Q1": round(ht.at["2026-Q1", "revenue"]), "2026-Q2": round(ht.at["2026-Q2", "revenue"])}
    facts["F2_hvac_booked_to_opex_eur"] = HVAC_EUR
    facts["F2_anchor_rent_lost_per_quarter_eur"] = round(ANCHOR_RENT_EUR * 3)
    assert -25 <= se_chg <= -12, se_chg
    # The other Southeast properties are roughly flat, so Harbor Tower explains the drop.
    others = gold[(gold.region_name == "Southeast") & (gold.property_id != 3)].groupby("fiscal_quarter").net_profit.sum()
    assert abs(others["2026-Q2"] / others["2026-Q1"] - 1) < 0.06

    mk = gold.groupby(["market", "fiscal_quarter"]).net_profit.sum().unstack()
    growth = ((mk["2026-Q2"] / mk["2026-Q1"] - 1) * 100).sort_values(ascending=False).round(1)
    facts["F3_market_qoq_np_growth_2026_q2_pct"] = growth.to_dict()
    assert growth.index[0] == "Luxembourg City" and growth.iloc[0] - growth.iloc[1] > 2, growth

    fin, am = gold.net_profit.sum(), (gold.net_profit - gold.capex).sum()
    gap = (fin - am) / fin * 100
    q2fin, q2am = q2.net_profit.sum(), (q2.net_profit - q2.capex).sum()
    facts["F4_finance_vs_asset_mgmt_gap_pct_all_quarters"] = round(gap, 1)
    facts["F4_q2_2026_finance_np"], facts["F4_q2_2026_asset_mgmt_np"] = round(q2fin), round(q2am)
    assert 8 <= gap <= 16, gap

    assert len(bronze_props) == 10 and len(silver_props) == 8
    assert bronze_props.region_id.isna().sum() == 2
    assert (bronze_props.property_name == "Harbor Tower").sum() == 2
    mism = bronze_props.merge(silver_props, on="property_id", suffixes=("_raw", "_clean"))
    mism = mism[mism.market_raw != mism.market_clean]
    assert len(mism) == 3
    facts["F5_market_mismatches"] = {r.property_name_raw: [r.market_raw, r.market_clean] for r in mism.itertuples()}

    t3 = targets[targets.fiscal_quarter == "2026-Q3"].set_index("property_id")
    proj_miss = []
    for pid, grp in gold.groupby("property_id"):
        rev = grp.set_index("fiscal_quarter").revenue
        trend = (rev.iloc[-4:].mean() / rev.iloc[-8:-4].mean()) ** 0.25
        if rev["2025-Q3"] * trend ** 4 < t3.at[pid, "revenue_target"]:
            proj_miss.append(grp.property_name.iloc[0])
    facts["F6_projected_to_miss_2026_q3_revenue_target_naive"] = sorted(proj_miss)
    assert len(proj_miss) >= 2

    hist = gold[gold.fiscal_quarter != "2026-Q2"]
    facts["met_target_rate_before_2026_q2_pct"] = round(hist.met_target.mean() * 100, 1)
    facts["portfolio_revenue_2026_q2"] = round(q2.revenue.sum())
    facts["portfolio_net_profit_2026_q2"] = round(q2fin)
    return facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default="2026-10-13")
    ap.add_argument("--out", default=str(Path(__file__).parent / "out"))
    args = ap.parse_args()
    as_of = date.fromisoformat(args.as_of)
    rng = np.random.default_rng(SEED)
    out = Path(args.out)
    (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "expected").mkdir(parents=True, exist_ok=True)

    regions = pd.DataFrame(REGIONS, columns=["region_id", "region_name"])
    clean = pd.DataFrame([p[:5] for p in PROPERTIES],
                         columns=["property_id", "property_name", "region_id", "market", "property_type"])
    bronze_props = pd.concat([clean.assign(market=[RAW_MARKET.get(i, m) for i, m in zip(clean.property_id, clean.market)]),
                              pd.DataFrame(REJECTED_PROPERTIES, columns=clean.columns)], ignore_index=True)
    bronze_props["region_id"] = bronze_props.region_id.astype("Int64")
    accounts = pd.DataFrame(GL_ACCOUNTS, columns=["account_id", "account_name", "category"])
    gl = build_gl(rng)
    tenants, raw_leases, leases = build_tenants_leases(rng, as_of)

    silver_props = clean.merge(regions, on="region_id")[["property_id", "property_name", "property_type", "region_id",
                                                         "region_name", "market"]]
    silver_gl = gl[gl.fiscal_period.str.fullmatch(r"\d{4}-Q[1-4]") & gl.property_id.isin(silver_props.property_id)]
    gold = build_gold(silver_gl, accounts, silver_props[["property_id", "property_name", "property_type", "region_name", "market"]])
    targets = build_targets(rng, gold)
    gold = finish_gold(gold, targets)
    cp = build_customer_performance(gold, leases, tenants)
    facts = assert_facts(gold, bronze_props, silver_props, targets)
    facts["as_of"] = args.as_of
    days = (pd.to_datetime(leases.lease_end) - pd.Timestamp(as_of)).dt.days
    facts["leases_by_window"] = {"expired": int((days < 0).sum()), "0-90": int(((days >= 0) & (days <= 90)).sum()),
                                 "91-180": int(((days > 90) & (days <= 180)).sum()),
                                 "181-365": int(((days > 180) & (days <= 365)).sum()), ">365": int((days > 365).sum())}
    facts["rows"] = {"bronze_gl_transactions": len(gl), "silver_gl_transactions": len(silver_gl), "gold_property_quarterly": len(gold),
                     "customer_performance": len(cp), "leases": len(leases), "raw_leases": len(raw_leases), "tenants": len(tenants)}

    raw = {"regions": regions, "properties": bronze_props, "tenants": tenants, "leases": raw_leases,
           "gl_accounts": accounts, "gl_transactions": gl, "quarterly_targets": targets}
    for name, df in raw.items():
        df.to_csv(out / "raw" / f"{name}.csv", index=False)
    expected = {"silver_regions": regions, "silver_properties": silver_props, "silver_tenants": tenants,
                "silver_leases": leases.drop(columns="updated_at"), "silver_gl_accounts": accounts,
                "silver_gl_transactions": silver_gl, "silver_quarterly_targets": targets,
                "gold_property_quarterly": gold, "customer_performance": cp}
    for name, df in expected.items():
        df.to_csv(out / "expected" / f"{name}.csv", index=False)
    (out / "facts.json").write_text(json.dumps(facts, indent=2, default=str))
    print(json.dumps(facts, indent=2, default=str))


if __name__ == "__main__":
    main()
