# Agent Coordination Thread

## analytics-sql → genie-dashboard

Hi, I've completed the reference assets for D1, D3, D6, D7, D10, and D14.

### For D6 (Data Exploration): 
I've created 5 reference quality-check queries in `code/reference/d06_quality_checks.py` (Databricks notebook). These should run on serverless. The expected results are:
- Q1: bronze 10 vs gold 8 properties
- Q2: IDs 9, 10 not in gold
- Q3: NULL rates (region_id has 2 NULLs)
- Q4: Harbor Tower duplicated (IDs 3, 10)
- Q5: 3 market spelling mismatches (Miami Bch→Beach, NYC→New York, Lux-Ville→Luxembourg City)

You'll need to test the Genie One prompts against the Genie Conversation API and verify they produce the right SQL. The prompt file is in `code/prompts/d06-genie-one-data-exploration.md`.

### For D7 (Metric Views):
I've created three UC metric views:
- `ref_mv_net_profit_margin` (with Finance vs Asset Management split measures)
- `ref_mv_target_attainment` (% properties meeting target: expected 62.5% for 2026-Q2 = 5/8)
- `ref_mv_qoq_revenue_growth` (quarter-over-quarter change)

These are in `code/reference/d07_metric_views.sql`. The metric views need to be deployed by the `ref_metric_views` job (in analytics_ref.yml), which also creates the D14 forecast table.

Expected numbers for 2026-Q2:
- Finance net profit margin: 59.4%
- Asset Mgmt net profit margin: 46.0% (10.1% gap, per F4)
- Target attainment: 62.5% (5 of 8 met)
- Highest QoQ growth: Luxembourg City +10.0%
- Lowest QoQ growth: Miami Beach −44.1%

The genie-dashboard needs these metric views for the D8 dashboard to reference. Please verify via Genie One that it recognizes these views and can query them.

### For D14 (Forecast):
I've created `ref_d14_revenue_forecast` via `code/reference/d14_forecast.sql`. Expected results:
- 96 total rows: 80 historical + 16 forecast (8 properties × 2 quarters Q3/Q4 2026)
- Harbor Tower: forecast €1.72M vs target €1.86M (−€140k miss)
- Zuidas: forecast €1.32M vs target €1.43M (−€110k miss)
- All others: forecast ≥ target (will meet)

This table can be embedded in the D8 dashboard as a trend line with CI.

### For D10 (Governance):
I've created:
- `code/reference/d10_governance.sql`: Apply governance (descriptions, comments, tags, PII mask function)
- `code/reference/d10_reset.sql`: Remove governance (so participants build live with clean starting state)

The prompt file `code/prompts/d10-unity-catalog-governance.md` walks through adding descriptions, column comments, tags, and a mask function. After running the `ref_d10_governance` job, the reset job clears everything so the starting state is clean.

---

## All Reference Assets Created

### SQL/Notebooks
- `code/sql/d03_snowflake_property_view.sql` — broken view (for D3 build-along)
- `code/reference/d03_property_performance_v.sql` — fixed view with YoY comparison (80 rows when fixed)
- `code/reference/d06_quality_checks.py` — 5-query quality audit notebook
- `code/reference/d07_metric_views.sql` — 3 metric views + populate
- `code/reference/d10_governance.sql` — apply governance metadata
- `code/reference/d10_reset.sql` — remove governance metadata
- `code/reference/d14_forecast.sql` — forecast table (96 rows: 80 historical + 16 forecast)

### Prompt Files
- `code/prompts/d01-platform-overview.md` — 4 stages, navigation + Genie Code intro
- `code/prompts/d03-genie-code-builder.md` — 4 stages, debug + fix Snowflake SQL
- `code/prompts/d06-genie-one-data-exploration.md` — 5 queries, data quality audit
- `code/prompts/d07-semantic-layer-metric-views.md` — 3 metric views + Genie One verification
- `code/prompts/d10-unity-catalog-governance.md` — descriptions, comments, tags, PII
- `code/prompts/d14-time-series-forecasting.md` — single-property, grouped, vs-target forecasts

### Bundle Resources
- `code/resources/analytics_ref.yml` — jobs to deploy all reference assets

### Setup
- `code/setup/sql/05_d03_broken_view.sql` — broken view deployed as part of setup

---

## Next Steps for You (genie-dashboard)

1. **D6:** Test 5 Genie One prompts via API; verify expected SQL and answers
2. **D7:** Deploy metric views (via ref_metric_views job); test Genie One queries against them
3. **D14:** Verify forecast table is created and embedded in D8 dashboard
4. **D8:** Build dashboard with metric views + forecast page

---

## Still Pending

- **D4, D5:** Agent Bricks (invoices, policies)
- **D11:** Lakeflow pipeline
- **D9, D12:** Apps (lease tracker, invoice approvals)
- **D13, D16:** Monitoring (AI Gateway, data quality)
- **Prompt verification:** Live Genie Code runs in browser (S9)
- **Deliverables:** Click-path, decks, architecture, hero (S11)
