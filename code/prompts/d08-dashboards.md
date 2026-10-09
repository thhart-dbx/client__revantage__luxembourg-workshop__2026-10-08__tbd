# Demo 8: AI/BI Dashboards — "Executive Portfolio Review"

**Session:** Day 1, 2:15–3:15 (60 min) · **You build:** dashboard "Portfolio Review – <your_name>" · **Reference:** "Revantage Portfolio Review (Reference)"
**Starting state:** metric views `ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth` (or your own from Demo 7), `gold_property_quarterly`, `ref_d14_revenue_forecast`
**Where:** Dashboards → Create dashboard; Genie Code panel in the dashboard editor

## Stage 1: Create and add data (5 min)
Dashboards → **Create dashboard** → rename "Portfolio Review – <your_name>". **Data** tab → **Add data source** →
pick `ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `gold_property_quarterly`.

**Prompt** (Genie Code, dashboard editor):
> Add a dataset kpi_latest that returns, for fiscal_quarter 2026-Q2, revenue, net profit and net profit margin from ref_mv_net_profit_margin and target attainment from ref_mv_target_attainment, one row. Metric views can't be joined: aggregate each with MEASURE() in its own subquery and cross join the two results. Run the dataset and check it.

**Expected:** one row: revenue 10,744,919; net_profit 6,375,345; margin 0.5933; target_attainment 0.625.
**Watch for (seen in pre-build):** without the MEASURE()/subquery sentence Genie Code joined the two metric views `ON 1 = 1` and said "created" without running it; the dataset fails with `METRIC_VIEW_JOIN_NOT_SUPPORTED`. Teach: always ask Genie Code to run and check what it builds.
**If stuck:** copy the `kpi_latest` query from the reference dashboard (open it → Data tab).

## Stage 2: Page 1, Executive Summary (10 min)
**Prompt:**
> On a page "Executive Summary", add counters for Revenue 2026-Q2 (EUR, compact), Net profit margin (%), and Target attainment (%) from kpi_latest, and a line chart of net profit by fiscal_quarter colored by region_name from ref_mv_net_profit_margin.

**Expected:** €10.7M · 59.3% · 62.5%; the line chart shows Southeast dropping in 2026-Q2.
**Checkpoint:** the counters match the reference dashboard's Executive Summary.

## Stage 3: Page 2, Regional Performance (12 min)
**Prompt:**
> Add a page "Regional Performance" with a bar chart of net profit by region and a scatter of revenue vs revenue_target by property, both from one dataset on gold_property_quarterly, and a heatmap of quarter-over-quarter net profit growth by market and quarter from ref_mv_qoq_revenue_growth. Add a single-select fiscal_quarter filter defaulting to 2026-Q2 that applies to the bar and scatter.

**Expected:** bar (2026-Q2): Western Europe highest, Southeast **€2,094,950**; heatmap: Miami Beach 2026-Q2 is the darkest negative cell (−44%), Luxembourg City +10%.
**Checkpoint:** if the bar shows ~€24.5M for Southeast, it isn't filtered (all 10 quarters summed): the filter only binds to datasets it was created on. Ask: "Make the Fiscal Quarter filter apply to the bar too, and check the 2026-Q2 Southeast value." Without "from gold_property_quarterly" Genie Code looks only in the metric views, can't find revenue_target, and substitutes net_profit.
**If stuck:** switch the widget type in the widget panel; Genie Code sometimes picks a table first.

## Stage 4: Page 3, Exceptions & Risks (8 min)
**Prompt:**
> Add a page "Exceptions & Risks" with a table of properties from gold_property_quarterly showing net profit, target, variance (net_profit - net_profit_target), qoq_change_pct (already in percent units, -44.05 means -44.05%) and a flag "Sharp decline" when qoq_change_pct < -10, with filters for fiscal_quarter (default 2026-Q2) and met_target.

**Expected:** filtering met_target = false gives 3 rows: Peachtree Center −€71,293, Harbor Tower −€43,235 (Sharp decline, −44%), Zuidas Residences −€41,701.

## Stage 5: Global filters (5 min)
**Prompt:**
> Add global filters for region_name and property_type that apply to all pages. Bind them to every dataset that has those columns, then set Region = Western Europe and verify each page.

**Checkpoint:** Region = Western Europe: the bar shows one bar (€2.69M), the Exceptions table 3 properties, the heatmap 2 markets. The three counters don't change: `kpi_latest` is a one-row portfolio dataset (a good talking point: which KPIs should be filterable?).
**Watch for (seen in pre-build):** with the short prompt Genie Code bound the filters to one dataset and still said they apply to all pages; Exceptions kept showing 8 rows. A filter only applies to the datasets listed in its fields.

## Stage 6: Ask Genie on the dashboard (8 min)
**Publish** the dashboard. In the published view use the **Ask Genie** bar at the bottom (or select a chart, then ask about it):
> Why did Southeast net profit drop in Q2?

**Expected:** Genie drills down by property type, then property: **Harbor Tower** net profit €1.15M → €0.64M (−44%) while revenue fell only 18%, so a cost spike sits on top of the revenue loss. Other Southeast properties were flat or up.
Follow-up for Demo 5: "What made Harbor Tower's operating expense jump?" → repairs & maintenance (the chiller invoice HV-2026-0417).

## Stage 7: Share, schedule, cache (5 min)
- **Share** → add the `revantage_consumers` group as *Can view* (viewers use the publisher's or their own credentials, as you choose).
- **Schedule** → daily 07:00 refresh + email snapshot to yourself.
- Explain caching: published dashboards serve cached results, refreshed on schedule or on demand.
- Talk track: Tableau/Power BI import, custom visuals, and embedding are available; show only if enabled in the workspace (pre-flight).

## Stage 8 (optional, with Demo 14): Forecast page
**Prompt:**
> Add a page "Forecast" with a line chart from ref_d14_revenue_forecast showing actual, forecast, lower and upper interval and target over fiscal_quarter_date for one property, with a property filter defaulting to Harbor Tower.

## Wrap-up
- **So what:** the quarterly review pack is a live, governed dashboard with Genie for the follow-up questions. No Excel, no emailed PDFs.
- **Snowflake equivalent:** Snowsight dashboards are SQL tiles. AI/BI adds a semantic layer (metric views), Genie Q&A, and publishing/sharing on the same governed data.
- **Verified:** 2026-10-08 on the FEVM workspace. The reference dashboard renders all 4 pages with correct numbers (screenshots `notes/agent-notes/screenshots/d08-*.png`). The dashboard Genie answered the Southeast question correctly in the browser. **Stages 1–5 and 8 run in the dashboard editor's Genie Code (S9)** on a scratch dashboard: S1 one row 10,744,918.88 / 6,375,345.36 / 0.5933 / 0.625 (first-time right with the prompt above; the original prompt produced a failing join); S2 counters €10.7M · 59.3% · 62.5% and the line chart with the Southeast drop (Genie Code fixed its own `METRIC_VIEW_MISSING_MEASURE_FUNCTION` error); S3 needed the two follow-ups now baked into the prompt/checkpoint, then Southeast €2,094,949.91 and the heatmap Miami Beach −44%; S4 8 rows, Harbor Tower "Sharp decline", variances −71.3K/−43.2K/−41.7K; S5 after the binding follow-up every page filters; S8 Harbor Tower actual + forecast + interval + target (the Forecast page didn't pick up the global filters). Screenshots `s9-d08-*.png`. Stage 6–7 (Ask Genie, share/schedule) are UI clicks, not Genie Code prompts.
