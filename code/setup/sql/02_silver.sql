-- Silver: cleansed, typed, deduplicated. Rules match code/data-gen/generate.py (the test oracle).
CREATE OR REPLACE TABLE ${catalog}.${schema}.silver_regions AS
SELECT CAST(region_id AS INT) AS region_id, region_name FROM ${catalog}.${schema}.bronze_regions;

-- Drop properties without a region (ids 9, 10) and standardize raw market spellings.
CREATE OR REPLACE TABLE ${catalog}.${schema}.silver_properties AS
SELECT CAST(p.property_id AS INT) AS property_id, p.property_name, p.property_type,
       CAST(p.region_id AS INT) AS region_id, r.region_name,
       CASE p.market WHEN 'Miami Bch' THEN 'Miami Beach' WHEN 'NYC' THEN 'New York'
                     WHEN 'Lux-Ville' THEN 'Luxembourg City' ELSE p.market END AS market
FROM ${catalog}.${schema}.bronze_properties p
JOIN ${catalog}.${schema}.silver_regions r ON p.region_id = r.region_id
WHERE p.region_id IS NOT NULL;

CREATE OR REPLACE TABLE ${catalog}.${schema}.silver_tenants AS
SELECT CAST(tenant_id AS INT) AS tenant_id, tenant_name, industry, credit_rating,
       contact_name, contact_email, CAST(contact_phone AS STRING) AS contact_phone
FROM ${catalog}.${schema}.bronze_tenants;

-- Latest version of each lease.
CREATE OR REPLACE TABLE ${catalog}.${schema}.silver_leases AS
SELECT lease_id, CAST(property_id AS INT) AS property_id, CAST(tenant_id AS INT) AS tenant_id,
       CAST(lease_start AS DATE) AS lease_start, CAST(lease_end AS DATE) AS lease_end,
       CAST(monthly_rent AS DECIMAL(18,2)) AS monthly_rent, lease_status,
       CAST(updated_at AS TIMESTAMP) AS updated_at
FROM ${catalog}.${schema}.bronze_leases
QUALIFY ROW_NUMBER() OVER (PARTITION BY lease_id ORDER BY updated_at DESC) = 1;

CREATE OR REPLACE TABLE ${catalog}.${schema}.silver_gl_accounts AS
SELECT CAST(account_id AS INT) AS account_id, account_name, category FROM ${catalog}.${schema}.bronze_gl_accounts;

-- Valid fiscal period and a known property only.
CREATE OR REPLACE TABLE ${catalog}.${schema}.silver_gl_transactions AS
SELECT t.* FROM ${catalog}.${schema}.bronze_gl_transactions t
WHERE t.fiscal_period RLIKE '^[0-9]{4}-Q[1-4]$'
  AND t.property_id IN (SELECT property_id FROM ${catalog}.${schema}.silver_properties);

CREATE OR REPLACE TABLE ${catalog}.${schema}.silver_quarterly_targets AS
SELECT * FROM ${catalog}.${schema}.bronze_quarterly_targets;
