-- Demo 11 reference pipeline, silver: typed, cleaned, deduplicated, with expectations.
CREATE OR REFRESH MATERIALIZED VIEW ref_d11_silver_regions AS
SELECT CAST(region_id AS INT) AS region_id, region_name FROM ref_d11_bronze_regions;

CREATE OR REFRESH MATERIALIZED VIEW ref_d11_silver_properties (
  CONSTRAINT has_region EXPECT (region_id IS NOT NULL) ON VIOLATION DROP ROW
) COMMENT 'One row per active property, standardized market names' AS
SELECT CAST(p.property_id AS INT) AS property_id, p.property_name, p.property_type,
       CAST(p.region_id AS INT) AS region_id, r.region_name,
       CASE p.market WHEN 'Miami Bch' THEN 'Miami Beach' WHEN 'NYC' THEN 'New York'
                     WHEN 'Lux-Ville' THEN 'Luxembourg City' ELSE p.market END AS market
FROM ref_d11_bronze_properties p
LEFT JOIN ref_d11_silver_regions r ON CAST(p.region_id AS INT) = r.region_id;

CREATE OR REFRESH MATERIALIZED VIEW ref_d11_silver_tenants AS
SELECT CAST(tenant_id AS INT) AS tenant_id, tenant_name, industry, credit_rating, contact_name, contact_email,
       CAST(contact_phone AS STRING) AS contact_phone
FROM ref_d11_bronze_tenants;

CREATE OR REFRESH MATERIALIZED VIEW ref_d11_silver_leases COMMENT 'Latest version of each lease' AS
SELECT lease_id, CAST(property_id AS INT) AS property_id, CAST(tenant_id AS INT) AS tenant_id,
       CAST(lease_start AS DATE) AS lease_start, CAST(lease_end AS DATE) AS lease_end,
       CAST(monthly_rent AS DECIMAL(18,2)) AS monthly_rent, lease_status, CAST(updated_at AS TIMESTAMP) AS updated_at
FROM ref_d11_bronze_leases
QUALIFY ROW_NUMBER() OVER (PARTITION BY lease_id ORDER BY CAST(updated_at AS TIMESTAMP) DESC) = 1;

CREATE OR REFRESH MATERIALIZED VIEW ref_d11_silver_gl_accounts AS
SELECT CAST(account_id AS INT) AS account_id, account_name, category FROM ref_d11_bronze_gl_accounts;

-- Malformed fiscal periods (e.g. '2026Q2' from a manual upload) are dropped and counted;
-- an amount that didn't parse (NULL) stops the update: never silently lose money.
CREATE OR REFRESH STREAMING TABLE ref_d11_silver_gl_transactions (
  CONSTRAINT valid_fiscal_period EXPECT (fiscal_period RLIKE '^[0-9]{4}-Q[1-4]$') ON VIOLATION DROP ROW,
  CONSTRAINT amount_parsed EXPECT (amount IS NOT NULL) ON VIOLATION FAIL UPDATE
) COMMENT 'Validated GL postings' AS
SELECT transaction_id, property_id, account_id, posting_date, fiscal_period,
       try_cast(amount AS DECIMAL(18,2)) AS amount, amount AS amount_raw, currency, description, source_system
FROM STREAM ref_d11_bronze_gl_transactions;

CREATE OR REFRESH MATERIALIZED VIEW ref_d11_silver_quarterly_targets AS
SELECT property_id, fiscal_quarter, net_profit_target, revenue_target FROM ref_d11_bronze_quarterly_targets;
