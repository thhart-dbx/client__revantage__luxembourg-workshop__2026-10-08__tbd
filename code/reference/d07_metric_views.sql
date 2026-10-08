-- D7 reference: three governed UC metric views over gold_property_quarterly.
-- Placeholders: ${catalog}, ${schema}. Query them with MEASURE(), e.g.
--   SELECT region_name, MEASURE(net_profit_margin) FROM ${catalog}.${schema}.ref_mv_net_profit_margin
--   WHERE fiscal_quarter = '2026-Q2' GROUP BY ALL;

CREATE OR REPLACE VIEW ${catalog}.${schema}.ref_mv_net_profit_margin
WITH METRICS LANGUAGE YAML
COMMENT 'Approved Finance definition of net profit margin, with the Asset Management variant alongside for reconciliation.'
AS $$
version: 1.1
source: ${catalog}.${schema}.gold_property_quarterly
dimensions:
  - name: property_name
    expr: property_name
  - name: property_type
    expr: property_type
  - name: region_name
    expr: region_name
  - name: market
    expr: market
  - name: fiscal_quarter
    expr: fiscal_quarter
  - name: fiscal_quarter_date
    expr: fiscal_quarter_date
measures:
  - name: revenue
    expr: SUM(revenue)
    comment: Total revenue (EUR)
  - name: net_profit
    expr: SUM(net_profit)
    comment: "Finance net profit = revenue - operating expense - management fee (excludes capex and intercompany). The approved definition."
  - name: net_profit_margin
    expr: SUM(net_profit) / SUM(revenue)
    comment: Finance net profit / revenue. The approved definition.
  - name: asset_mgmt_net_profit
    expr: SUM(net_profit - capex)
    comment: "Asset Management variant: also subtracts capex. Not the approved definition; shown for reconciliation."
  - name: asset_mgmt_net_profit_margin
    expr: SUM(net_profit - capex) / SUM(revenue)
    comment: Asset Management variant of the margin (not approved).
$$;

CREATE OR REPLACE VIEW ${catalog}.${schema}.ref_mv_target_attainment
WITH METRICS LANGUAGE YAML
COMMENT 'Share of property-quarters that met their net profit target (Finance definition).'
AS $$
version: 1.1
source: ${catalog}.${schema}.gold_property_quarterly
dimensions:
  - name: property_name
    expr: property_name
  - name: property_type
    expr: property_type
  - name: region_name
    expr: region_name
  - name: market
    expr: market
  - name: fiscal_quarter
    expr: fiscal_quarter
  - name: fiscal_quarter_date
    expr: fiscal_quarter_date
measures:
  - name: properties
    expr: COUNT(DISTINCT property_id)
  - name: properties_met_target
    expr: COUNT(DISTINCT property_id) FILTER (WHERE met_target)
  - name: target_attainment
    expr: COUNT(DISTINCT property_id) FILTER (WHERE met_target) / COUNT(DISTINCT property_id)
    comment: Share of properties meeting net_profit_target. Use with one fiscal_quarter.
  - name: net_profit_vs_target
    expr: SUM(net_profit) - SUM(net_profit_target)
    comment: Net profit minus target (EUR); negative = shortfall
$$;

-- Prior-quarter revenue is computed in the source, so QoQ growth is correct at any grouping.
CREATE OR REPLACE VIEW ${catalog}.${schema}.ref_mv_qoq_revenue_growth
WITH METRICS LANGUAGE YAML
COMMENT 'Quarter-over-quarter revenue and net profit growth.'
AS $$
version: 1.1
source: >
  SELECT *,
         LAG(revenue) OVER (PARTITION BY property_id ORDER BY fiscal_quarter) AS prior_quarter_revenue
  FROM ${catalog}.${schema}.gold_property_quarterly
dimensions:
  - name: property_name
    expr: property_name
  - name: property_type
    expr: property_type
  - name: region_name
    expr: region_name
  - name: market
    expr: market
  - name: fiscal_quarter
    expr: fiscal_quarter
  - name: fiscal_quarter_date
    expr: fiscal_quarter_date
measures:
  - name: revenue
    expr: SUM(revenue)
  - name: qoq_revenue_growth
    expr: SUM(revenue) / SUM(prior_quarter_revenue) - 1
    comment: Revenue vs the prior quarter for the same properties
  - name: qoq_net_profit_growth
    expr: SUM(net_profit) / SUM(prior_quarter_net_profit) - 1
    comment: Finance net profit vs the prior quarter for the same properties
$$;
