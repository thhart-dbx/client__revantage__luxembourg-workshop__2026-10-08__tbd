# Demo 14: Time Series Forecasting — "Where is revenue heading?"

**Session:** Day 2, 12:15–12:30 (15 min) · **You build:** a revenue forecast for 2026-Q3/Q4 vs target · **Reference:** `<catalog>.<schema>.ref_d14_revenue_forecast` (`code/reference/d14_forecast.sql`), dashboard page "Forecast"
**Starting state:** `gold_property_quarterly` (10 quarters per property, 2024-Q1..2026-Q2, `fiscal_quarter_date` = quarter start), `silver_quarterly_targets` (includes 2026-Q3/Q4 targets)
**Where:** SQL editor (a SQL warehouse: `ai_forecast` is disabled on serverless job compute)

## Stage 1: One property (4 min)
**Prompt** (Genie Code):
> Forecast Harbor Tower's (property_id 3) quarterly revenue through 2026-12-31 with ai_forecast from <catalog>.<schema>.gold_property_quarterly.

**Expected SQL** (the agenda's `horizon => 2` form doesn't run; `frequency => 'Q'` fails on DATE columns, `'QS'` works):
```sql
SELECT * FROM AI_FORECAST(
  TABLE(SELECT fiscal_quarter_date, revenue FROM <catalog>.<schema>.gold_property_quarterly WHERE property_id = 3),
  horizon => '2026-12-31', time_col => 'fiscal_quarter_date', value_col => 'revenue', frequency => 'QS')
```
**Expected:** 2026-07-01 **≈ €1.71–1.72M** (95% interval ≈ 1.54–1.89M), 2026-10-01 ≈ €1.78–1.79M (values vary slightly run to run).
**Watch for (seen in pre-build):** Genie Code may *probe* `ai_forecast` on its own serverless compute, get `AI_FUNCTION_PREVIEW`, and tell you the function is disabled and an admin must enable a preview. That's misleading: click **Run** in the SQL editor (SQL warehouse) and the query it wrote works.

## Stage 2: Every property at once (3 min)
> Do the same for all properties at once using group_col.

**Expected:** 16 rows (8 properties × 2 quarters), columns `property_id, fiscal_quarter_date, revenue_forecast, revenue_upper, revenue_lower`.

## Stage 3: Who will miss budget? (4 min)
> Join the forecast to silver_quarterly_targets (fiscal_quarter = year-Qn of fiscal_quarter_date) and list properties whose 2026-Q3 forecast is below revenue_target.

**Expected:** exactly **Harbor Tower** (€1.72M vs €1.86M target) and **Zuidas Residences** (€1.32M vs €1.43M).

## Stage 4: Know the limits (4 min, talk)
Harbor Tower's actual Q2 revenue was **€1.51M** after the anchor tenant left on 31 March, yet the forecast says €1.72M for Q3.
`ai_forecast` sees only the revenue history, not the lease roll. When the drivers are known (lease expiries, vacancy), use **Prophet with regressors** or a lease-roll model in a notebook (MLflow-tracked); ARIMA for smooth series; GARCH/AR when the volatility itself matters (rates, FX), not for rent.
**So what for FP&A:** `ai_forecast` is a fast, governed first pass across hundreds of properties in one SQL statement; spend data-science time on the exceptions it flags.
Show the dashboard's **Forecast** page (Demo 8 reference): actual, forecast, 95% interval, target.

## Wrap-up
- **Snowflake equivalent:** `SNOWFLAKE.ML.FORECAST` (create a model object, then call it). `ai_forecast` is a single table-valued function call, no model object to manage.
- **Verified:** 2026-10-08 on the FEVM warehouse: single-property numbers above; grouped forecast + target join returns exactly Harbor Tower and Zuidas for 2026-Q3; `ref_d14_revenue_forecast` = 80 actual + 16 forecast rows; dashboard page checked in the browser. Stage 1 run in the Genie Code UI (S9): correct query (`QS`, `fiscal_quarter_date`, through 2026-12-31) returning €1,709,781 for 2026-Q3 on the warehouse, after the misleading 'disabled' probe noted above. Stages 2–3: UI pending.
