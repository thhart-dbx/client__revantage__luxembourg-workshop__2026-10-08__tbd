-- Demo 11 reference pipeline, gold: property x quarter P&L. Must equal gold_property_quarterly.
CREATE OR REFRESH MATERIALIZED VIEW ref_d11_gold_property_quarterly (
  CONSTRAINT revenue_present EXPECT (revenue IS NOT NULL),
  CONSTRAINT quarter_format EXPECT (fiscal_quarter RLIKE '^[0-9]{4}-Q[1-4]$')
) COMMENT 'Quarterly P&L per property (Finance net profit), targets and QoQ change' AS
WITH pq AS (
  SELECT t.property_id, t.fiscal_period AS fiscal_quarter,
         ROUND(SUM(CASE WHEN a.category = 'Revenue' THEN t.amount ELSE 0 END), 2) AS revenue,
         ROUND(SUM(CASE WHEN a.category = 'OpEx' THEN t.amount ELSE 0 END), 2) AS operating_expense,
         ROUND(SUM(CASE WHEN a.category = 'MgmtFee' THEN t.amount ELSE 0 END), 2) AS mgmt_fee,
         ROUND(SUM(CASE WHEN a.category = 'CapEx' THEN t.amount ELSE 0 END), 2) AS capex,
         ROUND(SUM(CASE WHEN a.category = 'Intercompany' THEN t.amount ELSE 0 END), 2) AS intercompany
  FROM ref_d11_silver_gl_transactions t
  JOIN ref_d11_silver_gl_accounts a ON t.account_id = a.account_id
  GROUP BY ALL
), np AS (
  SELECT p.property_id, p.property_name, p.property_type, p.region_name, p.market, pq.fiscal_quarter,
         make_date(CAST(left(pq.fiscal_quarter, 4) AS INT), (CAST(right(pq.fiscal_quarter, 1) AS INT) - 1) * 3 + 1, 1) AS fiscal_quarter_date,
         pq.revenue, pq.operating_expense, pq.mgmt_fee, pq.capex, pq.intercompany,
         pq.revenue - pq.operating_expense - pq.mgmt_fee AS net_profit,
         tg.net_profit_target, tg.revenue_target
  FROM pq
  JOIN ref_d11_silver_properties p ON pq.property_id = p.property_id
  LEFT JOIN ref_d11_silver_quarterly_targets tg ON tg.property_id = pq.property_id AND tg.fiscal_quarter = pq.fiscal_quarter
)
SELECT *, net_profit >= net_profit_target AS met_target,
       LAG(net_profit) OVER (PARTITION BY property_id ORDER BY fiscal_quarter) AS prior_quarter_net_profit,
       ROUND((net_profit - LAG(net_profit) OVER (PARTITION BY property_id ORDER BY fiscal_quarter))
             / ABS(LAG(net_profit) OVER (PARTITION BY property_id ORDER BY fiscal_quarter)) * 100, 2) AS qoq_change_pct
FROM np;
