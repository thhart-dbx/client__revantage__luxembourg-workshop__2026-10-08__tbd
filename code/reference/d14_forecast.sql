-- D14 reference: actuals + ai_forecast for 2026-Q3/Q4 per property, with interval and target.
-- One row per property x quarter (80 actual + 16 forecast). Placeholders: ${catalog}, ${schema}.
CREATE OR REPLACE TABLE ${catalog}.${schema}.ref_d14_revenue_forecast
COMMENT 'Quarterly revenue: actuals 2024-Q1..2026-Q2 and ai_forecast for 2026-Q3/Q4 with 95% interval, vs revenue_target.'
AS
WITH fc AS (
  SELECT * FROM AI_FORECAST(
    TABLE(SELECT property_id, fiscal_quarter_date, revenue FROM ${catalog}.${schema}.gold_property_quarterly),
    horizon => '2026-12-31', time_col => 'fiscal_quarter_date', value_col => 'revenue',
    group_col => 'property_id', frequency => 'QS')
), rows AS (
  SELECT property_id, fiscal_quarter_date, revenue AS revenue_actual, CAST(NULL AS DOUBLE) AS revenue_forecast,
         CAST(NULL AS DOUBLE) AS revenue_lower, CAST(NULL AS DOUBLE) AS revenue_upper, FALSE AS is_forecast
  FROM ${catalog}.${schema}.gold_property_quarterly
  UNION ALL
  SELECT property_id, fiscal_quarter_date, NULL, revenue_forecast, revenue_lower, revenue_upper, TRUE FROM fc
)
SELECT r.property_id, p.property_name, p.property_type, p.region_name, p.market,
       concat(year(r.fiscal_quarter_date), '-Q', quarter(r.fiscal_quarter_date)) AS fiscal_quarter,
       r.fiscal_quarter_date, r.is_forecast,
       CAST(r.revenue_actual AS DECIMAL(18,2)) AS revenue_actual,
       CAST(r.revenue_forecast AS DECIMAL(18,2)) AS revenue_forecast,
       CAST(r.revenue_lower AS DECIMAL(18,2)) AS revenue_lower,
       CAST(r.revenue_upper AS DECIMAL(18,2)) AS revenue_upper,
       COALESCE(CAST(r.revenue_actual AS DECIMAL(18,2)), CAST(r.revenue_forecast AS DECIMAL(18,2))) AS revenue_plot,
       t.revenue_target,
       r.is_forecast AND r.revenue_forecast < t.revenue_target AS projected_miss
FROM rows r
JOIN ${catalog}.${schema}.silver_properties p USING (property_id)
LEFT JOIN ${catalog}.${schema}.silver_quarterly_targets t
  ON t.property_id = r.property_id
 AND t.fiscal_quarter = concat(year(r.fiscal_quarter_date), '-Q', quarter(r.fiscal_quarter_date));
