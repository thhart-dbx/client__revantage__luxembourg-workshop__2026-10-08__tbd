# Demo 8: AI/BI Dashboards — "Executive Portfolio Review"

**Session:** Day 1, 2:15–3:15 (60 min) · **You build:** dashboard "Portfolio Review – <your_name>" · **Reference:** "Revantage Portfolio Review (Reference)"
**Starting state:** metric views `ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth` (or your own from Demo 7), `gold_property_quarterly`, `ref_d14_revenue_forecast`
**Where:** Dashboards → Create dashboard; Genie Code panel in the dashboard editor

## Stage 1: Create and add data (5 min)
Dashboards → **Create dashboard** → rename "Portfolio Review – <your_name>". **Data** tab → **Add data source** →
pick `ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `gold_property_quarterly`.

**Prompt** (Genie Code, dashboard editor):
> Add a dataset kpi_latest that returns, for fiscal_quarter 2026-Q2, revenue, net profit and net profit margin from ref_mv_net_profit_margin and target attainment from ref_mv_target_attainment, one row.

**Expected:** one row: revenue 10,744,919; net_profit 6,375,345; margin 0.5933; target_attainment 0.625.
**If stuck:** copy the `kpi_latest` query from the reference dashboard (open it → Data tab).

## Stage 2: Page 1, Executive Summary (10 min)
**Prompt:**
> On a page "Executive Summary", add counters for Revenue 2026-Q2 (EUR, compact), Net profit margin (%), and Target attainment (%) from kpi_latest, and a line chart of net profit by fiscal_quarter colored by region_name from ref_mv_net_profit_margin.

**Expected:** €10.7M · 59.3% · 62.5%; the line chart shows Southeast dropping in 2026-Q2.
**Checkpoint:** the counters match the reference dashboard's Executive Summary.

## Stage 3: Page 2, Regional Performance (12 min)
**Prompt:**
> Add a page "Regional Performance" with a bar chart of net profit by region, a scatter of revenue vs revenue_target by property, and a heatmap of quarter-over-quarter net profit growth by market and quarter from ref_mv_qoq_revenue_growth. Add a single-select fiscal_quarter filter defaulting to 2026-Q2 that applies to the bar and scatter.

**Expected:** bar (2026-Q2): Western Europe highest, Southeast ~€2.1M; heatmap: Miami Beach 2026-Q2 is the darkest negative cell (−44%), Luxembourg City +10%.
**If stuck:** switch the widget type in the widget panel; Genie Code sometimes picks a table first.

## Stage 4: Page 3, Exceptions & Risks (8 min)
**Prompt:**
> Add a page "Exceptions & Risks" with a table of properties showing net profit, target, variance (net_profit - net_profit_target), qoq_change_pct and a flag "Sharp decline" when qoq_change_pct < -10, with filters for fiscal_quarter (default 2026-Q2) and met_target.

**Expected:** filtering met_target = false gives 3 rows: Peachtree Center −€71,293, Harbor Tower −€43,235 (Sharp decline, −44%), Zuidas Residences −€41,701.

## Stage 5: Global filters (5 min)
**Prompt:**
> Add global filters for region_name and property_type that apply to all pages.

**Checkpoint:** choosing Region = Western Europe changes every page.

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
- **Verified:** 2026-10-08 on the FEVM workspace. The reference dashboard renders all 4 pages with correct numbers (screenshots `notes/agent-notes/screenshots/d08-*.png`). The dashboard Genie answered the Southeast question correctly in the browser. Participant Genie Code prompts (Stages 1–5, 8): UI verification pending (S9).
