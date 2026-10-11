-- Demo 17 starting state: the "legacy warehouse" (as migrated from Snowflake) that participants turn into
-- an accurate Genie space, one metadata layer at a time. Same data as silver, but with abbreviated column
-- names, coded values, no comments, no keys, and the lease history (two leases have two versions).
-- legacy_data_dictionary is the documentation participants feed to Genie Code; d17_benchmark holds the
-- questions and ground-truth SQL (on these legacy tables, so the truth is valid for every rung).
CREATE OR REPLACE TABLE ${catalog}.${schema}.legacy_prp_mstr AS
SELECT property_id AS PRP_ID, property_name AS PRP_NM,
       CASE property_type WHEN 'Office' THEN 'OFF' WHEN 'Multifamily' THEN 'MFH' WHEN 'Retail' THEN 'RTL' END AS PRP_TYP_CD,
       region_name AS RGN_NM, market AS MKT_NM
FROM ${catalog}.${schema}.silver_properties;

CREATE OR REPLACE TABLE ${catalog}.${schema}.legacy_gl_acct AS
SELECT account_id AS ACCT_ID, account_name AS ACCT_NM,
       CASE category WHEN 'Revenue' THEN 'R' WHEN 'OpEx' THEN 'O' WHEN 'MgmtFee' THEN 'M'
                     WHEN 'CapEx' THEN 'C' WHEN 'Intercompany' THEN 'I' END AS ACCT_CLS_CD
FROM ${catalog}.${schema}.silver_gl_accounts;

CREATE OR REPLACE TABLE ${catalog}.${schema}.legacy_gl_txn AS
SELECT transaction_id AS TXN_ID, property_id AS PRP_ID, account_id AS ACCT_ID, posting_date AS PSTG_DT,
       fiscal_period AS FSCL_PRD, amount AS AMT, currency AS CRNCY_CD, description AS TXN_DSC,
       source_system AS SRC_SYS_CD
FROM ${catalog}.${schema}.silver_gl_transactions;

CREATE OR REPLACE TABLE ${catalog}.${schema}.legacy_lse AS
SELECT l.lease_id AS LSE_ID, CAST(l.property_id AS INT) AS PRP_ID, CAST(l.tenant_id AS INT) AS TNT_ID,
       CAST(l.lease_start AS DATE) AS LSE_STRT_DT, CAST(l.lease_end AS DATE) AS LSE_END_DT,
       CAST(l.monthly_rent AS DECIMAL(12,2)) AS MTH_RNT_AMT,
       CASE l.lease_status WHEN 'Active' THEN 'A' WHEN 'Pending Renewal' THEN 'P' WHEN 'Expired' THEN 'X' END AS LSE_STS_CD,
       CAST(l.updated_at AS DATE) AS UPD_DT
FROM ${catalog}.${schema}.bronze_leases l
WHERE CAST(l.property_id AS INT) IN (SELECT property_id FROM ${catalog}.${schema}.silver_properties);

CREATE OR REPLACE TABLE ${catalog}.${schema}.legacy_tnt AS
SELECT tenant_id AS TNT_ID, tenant_name AS TNT_NM, industry AS IND_NM, credit_rating AS CR_RTG
FROM ${catalog}.${schema}.silver_tenants;

CREATE OR REPLACE TABLE ${catalog}.${schema}.legacy_qtr_tgt AS
SELECT property_id AS PRP_ID, fiscal_quarter AS FSCL_QTR, net_profit_target AS NP_TGT_AMT,
       revenue_target AS REV_TGT_AMT
FROM ${catalog}.${schema}.silver_quarterly_targets;

CREATE OR REPLACE TABLE ${catalog}.${schema}.legacy_data_dictionary (
  table_name STRING, column_name STRING, business_name STRING, description STRING
) COMMENT 'Data dictionary of the legacy Snowflake warehouse (Demo 17). column_name NULL = the table itself (grain, keys).';

INSERT INTO ${catalog}.${schema}.legacy_data_dictionary VALUES
('legacy_prp_mstr', NULL, 'properties', 'Property master: one row per active property. Primary key PRP_ID.'),
('legacy_prp_mstr', 'PRP_ID', 'property_id', 'Property identifier.'),
('legacy_prp_mstr', 'PRP_NM', 'property_name', 'Property name, e.g. Harbor Tower.'),
('legacy_prp_mstr', 'PRP_TYP_CD', 'property_type', 'Property type code: OFF = Office, MFH = Multifamily, RTL = Retail.'),
('legacy_prp_mstr', 'RGN_NM', 'region_name', 'Region: Southeast, Northeast, Western Europe.'),
('legacy_prp_mstr', 'MKT_NM', 'market', 'Market (city), standardized, e.g. Miami Beach, Luxembourg City.'),
('legacy_gl_acct', NULL, 'gl_accounts', 'Chart of accounts: one row per GL account. Primary key ACCT_ID.'),
('legacy_gl_acct', 'ACCT_ID', 'account_id', 'GL account identifier.'),
('legacy_gl_acct', 'ACCT_NM', 'account_name', 'GL account name, e.g. Base Rent, Repairs & Maintenance.'),
('legacy_gl_acct', 'ACCT_CLS_CD', 'account_class', 'Account class: R = Revenue, O = Operating expense, M = Management fee, C = CapEx, I = Intercompany recharge.'),
('legacy_gl_txn', NULL, 'gl_transactions', 'General-ledger postings: one row per posting. Primary key TXN_ID; PRP_ID references legacy_prp_mstr, ACCT_ID references legacy_gl_acct. All amounts are positive; the account class gives the sign.'),
('legacy_gl_txn', 'TXN_ID', 'transaction_id', 'Posting identifier.'),
('legacy_gl_txn', 'PRP_ID', 'property_id', 'Property the posting belongs to.'),
('legacy_gl_txn', 'ACCT_ID', 'account_id', 'GL account of the posting.'),
('legacy_gl_txn', 'PSTG_DT', 'posting_date', 'Posting date.'),
('legacy_gl_txn', 'FSCL_PRD', 'fiscal_quarter', 'Fiscal quarter of the posting, YYYY-Qn.'),
('legacy_gl_txn', 'AMT', 'amount', 'Posting amount in EUR, always positive.'),
('legacy_gl_txn', 'CRNCY_CD', 'currency', 'Currency code (EUR).'),
('legacy_gl_txn', 'TXN_DSC', 'description', 'Posting text, e.g. invoice number and vendor.'),
('legacy_gl_txn', 'SRC_SYS_CD', 'source_system', 'Source ledger (YARDI, SAP-LUX).'),
('legacy_lse', NULL, 'leases', 'Lease history: one row per lease VERSION. A lease can have several versions; the current one has the latest UPD_DT. Primary key (LSE_ID, UPD_DT); PRP_ID references legacy_prp_mstr, TNT_ID references legacy_tnt.'),
('legacy_lse', 'LSE_ID', 'lease_id', 'Lease identifier.'),
('legacy_lse', 'PRP_ID', 'property_id', 'Property leased.'),
('legacy_lse', 'TNT_ID', 'tenant_id', 'Tenant.'),
('legacy_lse', 'LSE_STRT_DT', 'lease_start', 'Lease start date.'),
('legacy_lse', 'LSE_END_DT', 'lease_end', 'Lease end (expiry) date.'),
('legacy_lse', 'MTH_RNT_AMT', 'monthly_rent', 'Monthly rent in EUR.'),
('legacy_lse', 'LSE_STS_CD', 'lease_status', 'Lease status code: A = Active, P = Pending Renewal, X = Expired.'),
('legacy_lse', 'UPD_DT', 'updated_at', 'Date this version of the lease was recorded.'),
('legacy_tnt', NULL, 'tenants', 'Tenant master: one row per tenant. Primary key TNT_ID.'),
('legacy_tnt', 'TNT_ID', 'tenant_id', 'Tenant identifier.'),
('legacy_tnt', 'TNT_NM', 'tenant_name', 'Tenant (company) name.'),
('legacy_tnt', 'IND_NM', 'industry', 'Tenant industry.'),
('legacy_tnt', 'CR_RTG', 'credit_rating', 'Credit rating (S&P scale).'),
('legacy_qtr_tgt', NULL, 'quarterly_targets', 'Quarterly targets: one row per property and fiscal quarter. Primary key (PRP_ID, FSCL_QTR); PRP_ID references legacy_prp_mstr.'),
('legacy_qtr_tgt', 'PRP_ID', 'property_id', 'Property.'),
('legacy_qtr_tgt', 'FSCL_QTR', 'fiscal_quarter', 'Fiscal quarter, YYYY-Qn.'),
('legacy_qtr_tgt', 'NP_TGT_AMT', 'net_profit_target', 'Net profit target in EUR.'),
('legacy_qtr_tgt', 'REV_TGT_AMT', 'revenue_target', 'Revenue target in EUR.');

CREATE OR REPLACE TABLE ${catalog}.${schema}.d17_benchmark (
  question_id STRING, question STRING, trap STRING, answer_sql STRING
) COMMENT 'Demo 17 benchmark: 10 questions with ground-truth SQL on the legacy_* tables (valid for every rung of the ladder).';

INSERT INTO ${catalog}.${schema}.d17_benchmark VALUES
('Q01', 'What was total net profit in 2026-Q2?', 'Net profit = R - O - M (not all costs; CapEx and Intercompany excluded)',
 'SELECT SUM(CASE a.ACCT_CLS_CD WHEN \'R\' THEN t.AMT WHEN \'O\' THEN -t.AMT WHEN \'M\' THEN -t.AMT ELSE 0 END) AS net_profit FROM ${catalog}.${schema}.legacy_gl_txn t JOIN ${catalog}.${schema}.legacy_gl_acct a ON a.ACCT_ID = t.ACCT_ID WHERE t.FSCL_PRD = \'2026-Q2\''),
('Q02', 'Show net profit by region for 2026-Q2.', 'Net profit definition + join to property master',
 'SELECT p.RGN_NM AS region_name, SUM(CASE a.ACCT_CLS_CD WHEN \'R\' THEN t.AMT WHEN \'O\' THEN -t.AMT WHEN \'M\' THEN -t.AMT ELSE 0 END) AS net_profit FROM ${catalog}.${schema}.legacy_gl_txn t JOIN ${catalog}.${schema}.legacy_gl_acct a ON a.ACCT_ID = t.ACCT_ID JOIN ${catalog}.${schema}.legacy_prp_mstr p ON p.PRP_ID = t.PRP_ID WHERE t.FSCL_PRD = \'2026-Q2\' GROUP BY p.RGN_NM'),
('Q03', 'Which properties missed their net profit target in 2026-Q2?', 'Net profit vs NP_TGT_AMT',
 'WITH np AS (SELECT t.PRP_ID, SUM(CASE a.ACCT_CLS_CD WHEN \'R\' THEN t.AMT WHEN \'O\' THEN -t.AMT WHEN \'M\' THEN -t.AMT ELSE 0 END) AS net_profit FROM ${catalog}.${schema}.legacy_gl_txn t JOIN ${catalog}.${schema}.legacy_gl_acct a ON a.ACCT_ID = t.ACCT_ID WHERE t.FSCL_PRD = \'2026-Q2\' GROUP BY t.PRP_ID) SELECT p.PRP_NM AS property_name FROM np JOIN ${catalog}.${schema}.legacy_qtr_tgt g ON g.PRP_ID = np.PRP_ID AND g.FSCL_QTR = \'2026-Q2\' JOIN ${catalog}.${schema}.legacy_prp_mstr p ON p.PRP_ID = np.PRP_ID WHERE np.net_profit < g.NP_TGT_AMT'),
('Q04', 'What share of properties met their net profit target in 2026-Q2?', 'Share of properties, not average attainment ratio',
 'WITH np AS (SELECT t.PRP_ID, SUM(CASE a.ACCT_CLS_CD WHEN \'R\' THEN t.AMT WHEN \'O\' THEN -t.AMT WHEN \'M\' THEN -t.AMT ELSE 0 END) AS net_profit FROM ${catalog}.${schema}.legacy_gl_txn t JOIN ${catalog}.${schema}.legacy_gl_acct a ON a.ACCT_ID = t.ACCT_ID WHERE t.FSCL_PRD = \'2026-Q2\' GROUP BY t.PRP_ID) SELECT AVG(CASE WHEN np.net_profit >= g.NP_TGT_AMT THEN 1.0 ELSE 0.0 END) AS share_met_target FROM np JOIN ${catalog}.${schema}.legacy_qtr_tgt g ON g.PRP_ID = np.PRP_ID AND g.FSCL_QTR = \'2026-Q2\''),
('Q05', 'What is our net profit margin this quarter?', '"This quarter" = latest complete quarter 2026-Q2, not the calendar quarter',
 'SELECT SUM(CASE a.ACCT_CLS_CD WHEN \'R\' THEN t.AMT WHEN \'O\' THEN -t.AMT WHEN \'M\' THEN -t.AMT ELSE 0 END) / SUM(CASE WHEN a.ACCT_CLS_CD = \'R\' THEN t.AMT ELSE 0 END) AS net_profit_margin FROM ${catalog}.${schema}.legacy_gl_txn t JOIN ${catalog}.${schema}.legacy_gl_acct a ON a.ACCT_ID = t.ACCT_ID WHERE t.FSCL_PRD = \'2026-Q2\''),
('Q06', 'How many active leases do we have?', 'Lease history: count only the latest version per lease',
 'SELECT COUNT(*) AS active_leases FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY LSE_ID ORDER BY UPD_DT DESC) AS rn FROM ${catalog}.${schema}.legacy_lse) WHERE rn = 1 AND LSE_STS_CD = \'A\''),
('Q07', 'What is the total monthly rent of our active leases?', 'Latest version + status code A',
 'SELECT SUM(MTH_RNT_AMT) AS monthly_rent FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY LSE_ID ORDER BY UPD_DT DESC) AS rn FROM ${catalog}.${schema}.legacy_lse) WHERE rn = 1 AND LSE_STS_CD = \'A\''),
('Q08', 'What was total revenue of our office properties in 2026-Q2?', 'Type code OFF + class R',
 'SELECT SUM(t.AMT) AS revenue FROM ${catalog}.${schema}.legacy_gl_txn t JOIN ${catalog}.${schema}.legacy_gl_acct a ON a.ACCT_ID = t.ACCT_ID JOIN ${catalog}.${schema}.legacy_prp_mstr p ON p.PRP_ID = t.PRP_ID WHERE t.FSCL_PRD = \'2026-Q2\' AND a.ACCT_CLS_CD = \'R\' AND p.PRP_TYP_CD = \'OFF\''),
('Q09', 'How much CapEx did we spend in 2026-Q2?', 'Class C only',
 'SELECT SUM(t.AMT) AS capex FROM ${catalog}.${schema}.legacy_gl_txn t JOIN ${catalog}.${schema}.legacy_gl_acct a ON a.ACCT_ID = t.ACCT_ID WHERE t.FSCL_PRD = \'2026-Q2\' AND a.ACCT_CLS_CD = \'C\''),
('Q10', 'Which tenants rated below investment grade have active leases?', 'Below investment grade = BB or B; latest lease version, status A',
 'SELECT DISTINCT n.TNT_NM AS tenant_name FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY LSE_ID ORDER BY UPD_DT DESC) AS rn FROM ${catalog}.${schema}.legacy_lse) l JOIN ${catalog}.${schema}.legacy_tnt n ON n.TNT_ID = l.TNT_ID WHERE l.rn = 1 AND l.LSE_STS_CD = \'A\' AND n.CR_RTG IN (\'BB\', \'B\')');
