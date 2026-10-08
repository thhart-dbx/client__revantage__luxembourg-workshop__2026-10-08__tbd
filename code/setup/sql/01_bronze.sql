-- Bronze: raw source-system extracts, loaded as-is from the raw volume (starting state).
-- Placeholders: ${catalog}, ${schema}. Run by setup_starting_state.py.
CREATE OR REPLACE TABLE ${catalog}.${schema}.bronze_regions AS
SELECT * FROM read_files('/Volumes/${catalog}/${schema}/raw/regions.csv', format => 'csv', header => true, inferSchema => true);

CREATE OR REPLACE TABLE ${catalog}.${schema}.bronze_properties AS
SELECT * FROM read_files('/Volumes/${catalog}/${schema}/raw/properties.csv', format => 'csv', header => true, inferSchema => true);

CREATE OR REPLACE TABLE ${catalog}.${schema}.bronze_tenants AS
SELECT * FROM read_files('/Volumes/${catalog}/${schema}/raw/tenants.csv', format => 'csv', header => true, inferSchema => true);

CREATE OR REPLACE TABLE ${catalog}.${schema}.bronze_leases AS
SELECT * FROM read_files('/Volumes/${catalog}/${schema}/raw/leases.csv', format => 'csv', header => true, inferSchema => true);

CREATE OR REPLACE TABLE ${catalog}.${schema}.bronze_gl_accounts AS
SELECT * FROM read_files('/Volumes/${catalog}/${schema}/raw/gl_accounts.csv', format => 'csv', header => true, inferSchema => true);

CREATE OR REPLACE TABLE ${catalog}.${schema}.bronze_gl_transactions AS
SELECT * FROM read_files('/Volumes/${catalog}/${schema}/raw/gl_transactions.csv', format => 'csv', header => true,
  schemaHints => 'transaction_id BIGINT, property_id INT, account_id INT, posting_date DATE, fiscal_period STRING, amount DECIMAL(18,2), currency STRING, description STRING, source_system STRING');

CREATE OR REPLACE TABLE ${catalog}.${schema}.bronze_quarterly_targets AS
SELECT * FROM read_files('/Volumes/${catalog}/${schema}/raw/quarterly_targets.csv', format => 'csv', header => true,
  schemaHints => 'property_id INT, fiscal_quarter STRING, net_profit_target DECIMAL(18,2), revenue_target DECIMAL(18,2)');
