"""Generate code/resources/genie.yml (two Genie Agents) from the readable specs below.

Run after editing a spec:  code/data-gen/.venv/bin/python code/genie/build_spaces.py
- "Revantage Portfolio Q&A (Start)": Day 1 morning (Demo 2, Demo 6). Tables + light instructions.
- "Revantage Portfolio Q&A (Reference)": adds the ref_mv_* metric views, example SQL, and join specs
  (Demo 7 step 6 onward, Demo 8 "Explain with Genie", Demo 15 Track A answer key).
- "Revantage Accuracy Lab (Start)" / "(Reference)": Demo 17 rungs R1 and R7 (code/genie/d17_ladder.py).
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d17_ladder  # noqa: E402  (Demo 17 rung specs + benchmark)

T = "${var.catalog}.${var.schema}"


def sid(text):
    return hashlib.md5(text.encode()).hexdigest()


def table(name, description, synonyms=None):
    t = {"identifier": f"{T}.{name}", "description": [description]}
    if synonyms:
        t["column_configs"] = [{"column_name": c, "synonyms": s} for c, s in sorted(synonyms.items())]
    return t


GOLD = table("gold_property_quarterly",
             "Certified quarterly P&L per property, 2024-Q1 to 2026-Q2, EUR. net_profit is the Finance definition "
             "(revenue - operating_expense - mgmt_fee); targets and prior-quarter comparison included.",
             {"property_name": ["property", "asset", "building"], "region_name": ["region"],
              "met_target": ["hit target", "on plan", "on budget"], "net_profit": ["profit", "NOI", "net income"],
              "net_profit_target": ["target", "budget", "plan"], "qoq_change_pct": ["quarter over quarter", "QoQ"]})
BRONZE_PROPS = table("bronze_properties",
                     "Raw property master as extracted from the source system (bronze). Unvalidated: may contain "
                     "duplicates, NULL regions, and non-standard market names.")
SILVER_PROPS = table("silver_properties", "Clean property master (silver): one row per active property.",
                     {"property_name": ["property", "asset"], "market": ["city"]})
LEASES = table("silver_leases", "Current rent roll: lease start/end, monthly rent (EUR), status.",
               {"lease_end": ["expiry", "expiration date"], "monthly_rent": ["rent"]})
TENANTS = table("silver_tenants", "Tenant master: industry, credit rating, leasing contact.",
                {"tenant_name": ["tenant", "customer"]})

START_INSTRUCTIONS = """You answer questions from Revantage portfolio and asset managers about property performance.
- Amounts are EUR. The latest complete fiscal quarter is 2026-Q2; "this quarter" means 2026-Q2 and "last quarter" means 2026-Q1.
- Net profit means the Finance definition in gold_property_quarterly.net_profit: revenue - operating expense - management fees (capex and intercompany are excluded).
- If a question doesn't name a period, answer for 2026-Q2. Quarter-over-quarter questions without a period compare 2026-Q2 with 2026-Q1; never rank across all historical quarters unless asked.
- A property missed its target when met_target is false.
- bronze_properties is the raw source extract; silver_properties and gold_property_quarterly are the cleaned layers. Use bronze only for data-quality questions."""

REF_INSTRUCTIONS = START_INSTRUCTIONS + """
- Prefer the governed metric views for KPIs: ref_mv_net_profit_margin (net profit, margin, and the non-approved Asset Management variant), ref_mv_target_attainment (share of properties meeting target, net_profit_vs_target), ref_mv_qoq_revenue_growth (QoQ growth). Say which metric view and definition you used.
- The Asset Management net profit (also subtracts capex) is not the approved definition. Only show it when asked to compare definitions, and label it.
- When explaining a change, break it down by property and by component (revenue, operating expense, management fee) and name the largest drivers. Compute totals and percentages in SQL, never by hand.
- For risks, consider: missed targets, quarter-over-quarter declines, leases expiring within 180 days (silver_leases.lease_end vs current_date()), and tenants rated below BB."""

EXAMPLES = [
    ("Which properties missed their quarterly target in 2026-Q2?",
     f"""SELECT property_name, MEASURE(net_profit_vs_target) AS net_profit_vs_target
FROM {T}.ref_mv_target_attainment
WHERE fiscal_quarter = '2026-Q2'
GROUP BY property_name
HAVING MEASURE(net_profit_vs_target) < 0
ORDER BY net_profit_vs_target"""),
    ("Why did Southeast net profit drop in Q2?",
     f"""SELECT q2.property_name,
  q2.net_profit - q1.net_profit AS net_profit_change,
  q2.revenue - q1.revenue AS revenue_change,
  q2.operating_expense - q1.operating_expense AS opex_change,
  q2.mgmt_fee - q1.mgmt_fee AS mgmt_fee_change
FROM {T}.gold_property_quarterly q2
JOIN {T}.gold_property_quarterly q1 ON q1.property_id = q2.property_id AND q1.fiscal_quarter = '2026-Q1'
WHERE q2.fiscal_quarter = '2026-Q2' AND q2.region_name = 'Southeast'
ORDER BY net_profit_change"""),
    ("Which market has the highest quarter-over-quarter net profit growth?",
     f"""SELECT market, MEASURE(qoq_net_profit_growth) AS qoq_net_profit_growth
FROM {T}.ref_mv_qoq_revenue_growth
WHERE fiscal_quarter = '2026-Q2'
GROUP BY market
ORDER BY qoq_net_profit_growth DESC"""),
    ("What is our net profit margin this quarter?",
     f"""SELECT MEASURE(net_profit) AS net_profit, MEASURE(revenue) AS revenue, MEASURE(net_profit_margin) AS net_profit_margin
FROM {T}.ref_mv_net_profit_margin
WHERE fiscal_quarter = '2026-Q2'"""),
]

SAMPLE_QUESTIONS = [
    "Which properties missed their quarterly target in 2026-Q2?",
    "What changed from Q1 to Q2 for the Southeast region?",
    "Show me revenue by property type as a bar chart",
    "Which market has the highest quarter-over-quarter net profit growth?",
    "Summarize the top 3 risks across the portfolio this quarter",
]


def space(tables, instructions, metric_views=(), examples=(), joins=()):
    s = {
        "version": 2,
        "config": {"sample_questions": sorted(({"id": sid(q), "question": [q]} for q in SAMPLE_QUESTIONS), key=lambda x: x["id"])},
        "data_sources": {"tables": sorted(tables, key=lambda t: t["identifier"])},
        "instructions": {"text_instructions": [{"id": sid(instructions), "content": [instructions]}]},
    }
    if metric_views:
        s["data_sources"]["metric_views"] = sorted(metric_views, key=lambda t: t["identifier"])
    if examples:
        s["instructions"]["example_question_sqls"] = sorted(
            ({"id": sid(q), "question": [q], "sql": [sql]} for q, sql in examples), key=lambda x: x["id"])
    if joins:
        s["instructions"]["join_specs"] = sorted(joins, key=lambda x: x["id"])
    return s


def join(left, right, cond, rt="MANY_TO_ONE"):
    return {"id": sid(left + right), "left": {"identifier": f"{T}.{left}", "alias": left},
            "right": {"identifier": f"{T}.{right}", "alias": right},
            "sql": [cond, f"--rt=FROM_RELATIONSHIP_TYPE_{rt}--"]}


JOINS = [
    join("silver_leases", "silver_properties", "`silver_leases`.`property_id` = `silver_properties`.`property_id`"),
    join("silver_leases", "silver_tenants", "`silver_leases`.`tenant_id` = `silver_tenants`.`tenant_id`"),
    join("gold_property_quarterly", "silver_properties", "`gold_property_quarterly`.`property_id` = `silver_properties`.`property_id`"),
]
MVS = [
    {"identifier": f"{T}.ref_mv_net_profit_margin", "description": ["Approved Finance net profit and margin (+ Asset Mgmt variant)."]},
    {"identifier": f"{T}.ref_mv_target_attainment", "description": ["Share of properties meeting net profit target; shortfall vs target."]},
    {"identifier": f"{T}.ref_mv_qoq_revenue_growth", "description": ["Quarter-over-quarter revenue and net profit growth."]},
]

SPACES = {
    "portfolio_qa_start": ("Revantage Portfolio Q&A (Start)",
                           "Day 1 Genie One space: property performance Q&A and data-quality exploration (Demos 2, 6).",
                           space([GOLD, BRONZE_PROPS, SILVER_PROPS, LEASES, TENANTS], START_INSTRUCTIONS)),
    "portfolio_qa_reference": ("Revantage Portfolio Q&A (Reference)",
                               "Answer key: governed metric views, example SQL, and joins (Demo 7 step 6, Demo 8, Demo 15A).",
                               space([GOLD, BRONZE_PROPS, SILVER_PROPS, LEASES, TENANTS], REF_INSTRUCTIONS, MVS, EXAMPLES, JOINS)),
    "accuracy_lab_start": ("Revantage Accuracy Lab (Start)",
                           "Demo 17 starting point: the legacy tables only (rung R1) with the 10-question benchmark. Clone it, then add one metadata layer at a time and re-run the benchmarks.",
                           d17_ladder.spec("R1", d17_ladder.load_benchmark())),
    "accuracy_lab_reference": ("Revantage Accuracy Lab (Reference)",
                               "Demo 17 answer key (rung R7): documented ref_d17_* tables, metric views, instructions, SQL examples, synonyms and joins, with the same benchmark.",
                               d17_ladder.spec("R7", d17_ladder.load_benchmark())),
}

lines = ["# Generated by code/genie/build_spaces.py: edit the specs there, then re-run it.", "resources:", "  genie_spaces:"]
for key, (title, desc, spec) in SPACES.items():
    lines += [f"    {key}:", f"      title: {json.dumps(title)}", f"      description: {json.dumps(desc)}",
              "      parent_path: ${var.genie_space_path}", "      warehouse_id: ${var.warehouse_id}",
              f"      serialized_space: {json.dumps(json.dumps(spec, indent=2))}",
              "      permissions:", "        - group_name: ${var.consumer_group}", "          level: CAN_RUN"]
out = Path(__file__).resolve().parents[1] / "resources" / "genie.yml"
out.write_text("\n".join(lines) + "\n")
print(f"wrote {out}")
