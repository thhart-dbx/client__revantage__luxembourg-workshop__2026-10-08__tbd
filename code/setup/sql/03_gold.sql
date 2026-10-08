-- Gold: certified property-quarter fact and tenant-level performance.
-- net_profit is the Finance definition: revenue - operating_expense - mgmt_fee (excludes capex and intercompany).
CREATE OR REPLACE TABLE ${catalog}.${schema}.gold_property_quarterly AS
WITH pq AS (
  SELECT t.property_id, t.fiscal_period AS fiscal_quarter,
         ROUND(SUM(CASE WHEN a.category = 'Revenue' THEN t.amount ELSE 0 END), 2) AS revenue,
         ROUND(SUM(CASE WHEN a.category = 'OpEx' THEN t.amount ELSE 0 END), 2) AS operating_expense,
         ROUND(SUM(CASE WHEN a.category = 'MgmtFee' THEN t.amount ELSE 0 END), 2) AS mgmt_fee,
         ROUND(SUM(CASE WHEN a.category = 'CapEx' THEN t.amount ELSE 0 END), 2) AS capex,
         ROUND(SUM(CASE WHEN a.category = 'Intercompany' THEN t.amount ELSE 0 END), 2) AS intercompany
  FROM ${catalog}.${schema}.silver_gl_transactions t
  JOIN ${catalog}.${schema}.silver_gl_accounts a USING (account_id)
  GROUP BY ALL
), np AS (
  SELECT p.property_id, p.property_name, p.property_type, p.region_name, p.market, pq.fiscal_quarter,
         make_date(CAST(left(pq.fiscal_quarter, 4) AS INT), (CAST(right(pq.fiscal_quarter, 1) AS INT) - 1) * 3 + 1, 1) AS fiscal_quarter_date,
         pq.revenue, pq.operating_expense, pq.mgmt_fee, pq.capex, pq.intercompany,
         pq.revenue - pq.operating_expense - pq.mgmt_fee AS net_profit,
         tg.net_profit_target, tg.revenue_target
  FROM pq
  JOIN ${catalog}.${schema}.silver_properties p USING (property_id)
  LEFT JOIN ${catalog}.${schema}.silver_quarterly_targets tg USING (property_id, fiscal_quarter)
)
SELECT *, net_profit >= net_profit_target AS met_target,
       LAG(net_profit) OVER (PARTITION BY property_id ORDER BY fiscal_quarter) AS prior_quarter_net_profit,
       ROUND((net_profit - LAG(net_profit) OVER (PARTITION BY property_id ORDER BY fiscal_quarter))
             / ABS(LAG(net_profit) OVER (PARTITION BY property_id ORDER BY fiscal_quarter)) * 100, 2) AS qoq_change_pct
FROM np;

-- Tenant-level view of each property-quarter: revenue and net profit allocated by rent billed.
CREATE OR REPLACE TABLE ${catalog}.${schema}.customer_performance AS
WITH q AS (
  SELECT property_id, property_name, region_name, fiscal_quarter, revenue, net_profit,
         fiscal_quarter_date AS qs, last_day(add_months(fiscal_quarter_date, 2)) AS qe
  FROM ${catalog}.${schema}.gold_property_quarterly
), billed AS (
  SELECT q.*, l.tenant_id, l.monthly_rent,
         GREATEST(0, LEAST(3, (year(LEAST(l.lease_end, q.qe)) - year(GREATEST(l.lease_start, q.qs))) * 12
                              + month(LEAST(l.lease_end, q.qe)) - month(GREATEST(l.lease_start, q.qs)) + 1)) AS months
  FROM q JOIN ${catalog}.${schema}.silver_leases l
    ON l.property_id = q.property_id AND l.lease_start <= q.qe AND l.lease_end >= q.qs
), shares AS (
  SELECT *, monthly_rent * months AS rent_billed,
         monthly_rent * months / SUM(monthly_rent * months) OVER (PARTITION BY property_id, fiscal_quarter) AS share
  FROM billed
)
SELECT s.property_id, s.property_name, s.region_name, s.tenant_id, t.tenant_name, t.industry, t.credit_rating,
       t.contact_email, t.contact_phone, s.fiscal_quarter,
       ROUND(s.rent_billed, 2) AS rent_billed,
       ROUND(s.revenue * s.share, 2) AS revenue_allocated,
       ROUND(s.net_profit * s.share, 2) AS net_profit_allocated
FROM shares s JOIN ${catalog}.${schema}.silver_tenants t USING (tenant_id);
