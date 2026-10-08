-- Demo 11 reference pipeline, bronze: Auto Loader (STREAM read_files) over the raw CSV extracts.
-- Every table is prefixed ref_d11_ so the pipeline never touches the starting-state tables.
-- The raw volume path comes from the pipeline configuration key raw_path.
CREATE OR REFRESH STREAMING TABLE ref_d11_bronze_regions COMMENT 'Raw regions extract' AS
SELECT *, _metadata.file_path AS source_file FROM STREAM read_files('${raw_path}/regions*.csv', format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE ref_d11_bronze_properties COMMENT 'Raw property master extract' AS
SELECT *, _metadata.file_path AS source_file FROM STREAM read_files('${raw_path}/properties*.csv', format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE ref_d11_bronze_tenants COMMENT 'Raw tenant master extract' AS
SELECT *, _metadata.file_path AS source_file FROM STREAM read_files('${raw_path}/tenants*.csv', format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE ref_d11_bronze_leases COMMENT 'Raw lease extract (may contain several versions per lease)' AS
SELECT *, _metadata.file_path AS source_file FROM STREAM read_files('${raw_path}/leases*.csv', format => 'csv', header => true);

CREATE OR REFRESH STREAMING TABLE ref_d11_bronze_gl_accounts COMMENT 'Raw chart of accounts' AS
SELECT *, _metadata.file_path AS source_file FROM STREAM read_files('${raw_path}/gl_accounts*.csv', format => 'csv', header => true);

-- amount stays a string in bronze: a CSV reader will happily turn "980,40" into 98040.00.
CREATE OR REFRESH STREAMING TABLE ref_d11_bronze_gl_transactions COMMENT 'Raw monthly GL postings, EUR (amount as delivered)' AS
SELECT *, _metadata.file_path AS source_file FROM STREAM read_files('${raw_path}/gl_transactions*.csv', format => 'csv', header => true,
  schemaHints => 'transaction_id BIGINT, property_id INT, account_id INT, posting_date DATE, fiscal_period STRING, amount STRING, currency STRING, description STRING, source_system STRING');

CREATE OR REFRESH STREAMING TABLE ref_d11_bronze_quarterly_targets COMMENT 'Raw budget targets' AS
SELECT *, _metadata.file_path AS source_file FROM STREAM read_files('${raw_path}/quarterly_targets*.csv', format => 'csv', header => true,
  schemaHints => 'property_id INT, fiscal_quarter STRING, net_profit_target DECIMAL(18,2), revenue_target DECIMAL(18,2)');
