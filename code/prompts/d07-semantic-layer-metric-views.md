# Demo 7: Semantic Layer & UC Metric Views — "Define Net Profit Margin once"

**Session:** Day 1, 1:30–2:15 (45 min) · **You build:** three metric views in `<my_schema>` · **Reference:** `<catalog>.<schema>.ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth` (source `code/reference/d07_metric_views.sql`)
**Starting state:** `gold_property_quarterly` with revenue, operating_expense, mgmt_fee, capex, intercompany, net_profit (Finance), targets
**Where:** SQL editor with Genie Code; Catalog Explorer; Genie One

The story: Finance's net profit = revenue − opex − management fees. Asset Management also subtracts capex.
Same portfolio, two "net profit margins": **59.3% vs 54.0%** in 2026-Q2. A metric view puts the approved one in the catalog.

## Stage 1: Net profit margin (12 min)
**Prompt** (Genie Code, SQL editor):
> Create a Unity Catalog metric view <my_schema>.mv_net_profit_margin over <catalog>.<schema>.gold_property_quarterly with dimensions property_name, property_type, region_name, market, fiscal_quarter, fiscal_quarter_date and measures revenue = SUM(revenue), net_profit = SUM(net_profit), net_profit_margin = SUM(net_profit) / SUM(revenue), plus asset_mgmt_net_profit_margin = SUM(net_profit - capex) / SUM(revenue) labelled as not approved.

**Expected:** `CREATE OR REPLACE VIEW … WITH METRICS LANGUAGE YAML AS $$ version: 1.1 … $$`. (Metric views are views with a YAML body; there is no `CREATE METRIC TABLE`.)
**Checkpoint:**
```sql
SELECT MEASURE(net_profit_margin), MEASURE(asset_mgmt_net_profit_margin)
FROM <my_schema>.mv_net_profit_margin WHERE fiscal_quarter = '2026-Q2'
```
→ **0.5933 · 0.5395**. By region: `GROUP BY region_name`.
**If stuck:** copy the first statement of `code/reference/d07_metric_views.sql`, change the view name.
**Teach:** ratios belong in measures (`SUM/SUM`), never as a stored column: the margin re-aggregates correctly at any grouping.

## Stage 2: Target attainment (8 min)
> Add a metric view mv_target_attainment with measures properties = COUNT(DISTINCT property_id), properties_met_target = COUNT(DISTINCT property_id) FILTER (WHERE met_target), target_attainment = their ratio, and net_profit_vs_target = SUM(net_profit) - SUM(net_profit_target).

**Checkpoint (2026-Q2):** properties **8**, met **5**, attainment **0.625**; `GROUP BY property_name HAVING MEASURE(net_profit_vs_target) < 0` → Peachtree Center −71,293; Harbor Tower −43,235; Zuidas Residences −41,701.

## Stage 3: QoQ growth (10 min)
> Add mv_qoq_revenue_growth whose source is a query adding prior_quarter_revenue = LAG(revenue) per property, with measures qoq_revenue_growth = SUM(revenue) / SUM(prior_quarter_revenue) - 1 and qoq_net_profit_growth using prior_quarter_net_profit.

**Checkpoint (2026-Q2, by market):** Luxembourg City **+10.0%** (highest), Miami Beach **−44.1%**; by region Southeast **−18.6%**.
**Teach:** compute "prior" in the source; then growth is correct for any grouping (property, market, region, portfolio).

## Stage 4: Govern it (5 min)
Catalog Explorer → your metric view → owner, comment, **Certified** tag (`system.certification_status`), grants. Point out lineage back to gold.

## Stage 5: Genie answers from the definition (10 min)
In Genie One open **Revantage Portfolio Q&A (Reference)** (it includes the `ref_mv_*` views):
> Which properties missed their quarterly target in 2026-Q2?

**Expected:** the same 3 properties, answered from `ref_mv_target_attainment` (net_profit_vs_target). The answer names the metric view.
> What is our net profit margin this quarter, and how would it differ under the Asset Management definition?

**Expected:** 59.33% vs 53.95% (−5.38 pp), labelled as the approved vs the non-approved definition.

## Wrap-up
- **So what:** the KPI argument happens once, in the catalog, and every dashboard, Genie answer, and query uses that answer.
- **Snowflake equivalent:** semantic views in Snowflake. UC metric views are queried with plain SQL (`MEASURE()`), used natively by AI/BI dashboards and Genie, and governed like any table.
- **Verified:** 2026-10-08 on the FEVM workspace: reference views created and every checkpoint number above returned by SQL; the Genie Stage 5 answers via the Conversation API (`verification/d02-d06-d07-genie.md`). **Stage 1 run in the Genie Code UI (S9):** Genie Code loaded its metric-view skill, wrote valid YAML 1.1 DDL (4 measures, no join), ran it and the query, and reported 59.33% / 53.95% with the capex explanation; the view it created returned 0.5933 / 0.5395. Stages 2–3: UI pending.
