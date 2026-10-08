-- D3 reference: the Snowflake view migrated to Databricks SQL, join fixed, YoY column added.
-- Expected: 64 rows (8 properties x last 8 quarters, 2024-Q3..2026-Q2). The unfixed join gives 176.
CREATE OR REPLACE VIEW ${catalog}.${schema}.ref_d03_property_performance_v AS
SELECT
    g.property_id,
    p.property_name,
    p.property_type,
    p.region_name,
    p.market,
    g.fiscal_quarter,
    date_format(g.fiscal_quarter_date, 'yyyy-MM') AS period_start,           -- was TO_VARCHAR(..., 'YYYY-MM')
    CAST(g.revenue AS DECIMAL(18,2)) AS revenue,                               -- NUMBER -> DECIMAL
    CAST(COALESCE(g.net_profit, 0) AS DECIMAL(18,2)) AS net_profit,
    CAST(g.net_profit_target AS DECIMAL(18,2)) AS net_profit_target,
    try_divide(g.net_profit, g.revenue) AS net_profit_margin,                  -- was DIV0
    IF(g.net_profit >= g.net_profit_target, 'On target', 'Missed') AS target_status,
    DATEADD(quarter, -1, g.fiscal_quarter_date) AS prior_quarter_start,        -- runs as-is on Databricks
    CAST(g.net_profit - LAG(g.net_profit, 4) OVER (PARTITION BY g.property_id ORDER BY g.fiscal_quarter) AS DECIMAL(18,2))
        AS yoy_net_profit_change,                                              -- vs same quarter last year
    current_timestamp() AS refreshed_at                                        -- was SYSDATE()
FROM ${catalog}.${schema}.gold_property_quarterly g
JOIN ${catalog}.${schema}.silver_properties p
    ON g.property_id = p.property_id                                           -- the missing join key
QUALIFY DENSE_RANK() OVER (ORDER BY g.fiscal_quarter DESC) <= 8;
