-- D3 starting point: a business view as it exists in Snowflake today. Participants paste it into the
-- SQL editor and migrate it with Genie Code. It doesn't run on Databricks as-is, and even once it
-- runs it's wrong: the join is missing its key, so every property is repeated per region.
CREATE OR REPLACE VIEW ${catalog}.${schema}.property_performance_v AS
SELECT
    g.property_id,
    p.property_name,
    p.property_type,
    p.region_name,
    p.market,
    g.fiscal_quarter,
    TO_VARCHAR(g.fiscal_quarter_date, 'YYYY-MM') AS period_start,
    g.revenue::NUMBER(18,2) AS revenue,
    NVL(g.net_profit, 0)::NUMBER(18,2) AS net_profit,
    g.net_profit_target::NUMBER(18,2) AS net_profit_target,
    DIV0(g.net_profit, g.revenue) AS net_profit_margin,
    IFF(g.net_profit >= g.net_profit_target, 'On target', 'Missed') AS target_status,
    DATEADD(quarter, -1, g.fiscal_quarter_date) AS prior_quarter_start,
    SYSDATE() AS refreshed_at
FROM ${catalog}.${schema}.gold_property_quarterly g
JOIN ${catalog}.${schema}.silver_properties p
    ON g.region_name = p.region_name
QUALIFY DENSE_RANK() OVER (ORDER BY g.fiscal_quarter DESC) <= 8;
