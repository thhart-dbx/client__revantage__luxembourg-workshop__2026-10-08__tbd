# Demo 16: Data Quality & Observability — "Trust scorecard"

**Session:** Day 2, 3:45–4:15 (30 min) · **You build:** quality monitoring on the gold table, a bad-load detector, and the blast radius · **Reference:** data profiling monitor on `gold_property_quarterly` (bundle target `revantage`), alert "[Revantage workshop] Revenue > 3 sigma from property mean (Reference)", `code/reference/d16_revenue_outliers.sql`, `d16_blast_radius.sql`
**Starting state:** clean `gold_property_quarterly` (80 rows, 2024-Q1..2026-Q2); seed/reset scripts `code/sql/d16_seed_bad_row.sql` / `d16_reset.sql` (`${table}` = `gold_property_quarterly`)
**Where:** Catalog Explorer → table → **Quality** tab; SQL editor with Genie Code; Alerts

## Stage 1: Turn on monitoring (5 min)
Catalog → `gold_property_quarterly` → **Quality → Enable data profiling** (Snapshot, slice by `region_name`), and at schema level **anomaly detection** (freshness, completeness).
**Expected:** a profile dashboard and two output tables (`…_profile_metrics`, `…_drift_metrics`) after the first refresh (a few minutes).
**FEVM note:** the FEVM metastore is at its 1,000-monitor limit, so we couldn't create one here. In Revantage's workspace the bundle target creates it; show the profile from the Oct 5 workshop's monitor if needed.

## Stage 2: Read the profile (5 min)
Profile dashboard: per-column null %, distinct counts, min/max/quantiles, per region slice. Freshness = last commit time.
**Prompt** (Genie Code):
> Using <catalog>.<schema>.gold_property_quarterly_profile_metrics, show null rate and max for revenue and net_profit in the latest window.

## Stage 3: A bad load arrives (facilitator, 2 min)
Run `code/sql/d16_seed_bad_row.sql` with `${table}` = `gold_property_quarterly`: inserts **Harbor Tower 2026-Q3** with revenue **10× its average (€17.2M)** and **NULL net_profit**.

## Stage 4: Detect it (8 min)
- **Completeness:** `SELECT COUNT(*) FROM <catalog>.<schema>.gold_property_quarterly WHERE net_profit IS NULL` → 1. Refresh the monitor: net_profit null % > 0, revenue max jumps, drift on revenue flagged.
- **Outlier rule:** run `code/reference/d16_revenue_outliers.sql`.
  **Expected:** exactly one row: Harbor Tower 2026-Q3, **z ≈ 172** vs its other quarters (mean €1.72M).
  **Teach:** a plain "> 3σ" rule on smooth financial series also flags real business moves. Before the seed it flagged Harbor Tower's vacancy and a new Kirchberg suite. The rule therefore uses leave-one-out σ **and** a > 50% materiality guard: **0 rows on clean data, 1 after the seed**.
**Prompt** (Genie Code):
> Write a query that flags property-quarters whose revenue is more than 3 standard deviations from that property's other quarters and more than 50% away from their mean.

## Stage 5: Blast radius (5 min)
Catalog Explorer → **Lineage** on the table, or run `code/reference/d16_blast_radius.sql`.
**Expected downstream:** `ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth`, the Portfolio Review dashboard (DASHBOARD_V3), `ref_d14_revenue_forecast`, `ref_d03_property_performance_v`, `ref_d06_property_quality_checks`, `customer_performance`, and the Genie Agents that read them. One bad row reaches every board number.

## Stage 6: Alert (5 min)
Open the reference alert (daily 07:00 Luxembourg, notifies the owner): it counts outliers and fires when > 0. Create your own from the Stage 4 query, wrapped as `SELECT COUNT(*) AS outliers FROM (…)`.

## Reset (facilitator, immediately after)
Run `code/sql/d16_reset.sql` (deletes the 2026-Q3 row). Re-check: outlier query → 0 rows, NULL count → 0.

## Wrap-up
- **So what:** quality issues are caught by the platform (profiling, expectations, alerts) before a business user finds them, and lineage shows exactly what they would have broken.
- **Snowflake equivalent:** Data Metric Functions + ACCESS_HISTORY. Here profiling, anomaly detection, pipeline expectations, alerts, and lineage come together in Unity Catalog.
- **Verified:** 2026-10-08 on the FEVM workspace, rehearsed on a deep clone (`ref_d16_gold_sandbox`, since dropped): seed inserted €17.2M / NULL; outlier query 0 rows on clean gold, 1 row (z 171.9) after the seed; the reference alert is deployed. Lineage query returns the downstream list above. **Not verified on the FEVM:** creating the profiling monitor (metastore limit); Genie Code prompts (S9).
