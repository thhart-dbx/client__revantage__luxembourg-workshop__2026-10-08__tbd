-- Demo 17 reference: the legacy warehouse turned into a documented business layer (ref_d17_*).
-- Generated from legacy_data_dictionary. The ladder (code/genie/d17_ladder.py) runs the rungs in order and
-- scores a fresh Genie space after each; participants build the same thing in <my_schema> with Genie Code.

-- @rung R2: business column names (values and codes unchanged)
-- Drop first: CREATE OR REPLACE TABLE ... AS SELECT keeps the old table and column comments.
DROP TABLE IF EXISTS ${catalog}.${schema}.ref_d17_gl_transactions;
DROP TABLE IF EXISTS ${catalog}.${schema}.ref_d17_leases;
DROP TABLE IF EXISTS ${catalog}.${schema}.ref_d17_quarterly_targets;
DROP TABLE IF EXISTS ${catalog}.${schema}.ref_d17_properties;
DROP TABLE IF EXISTS ${catalog}.${schema}.ref_d17_gl_accounts;
DROP TABLE IF EXISTS ${catalog}.${schema}.ref_d17_tenants;
CREATE OR REPLACE TABLE ${catalog}.${schema}.ref_d17_properties AS SELECT PRP_ID AS property_id, PRP_NM AS property_name, PRP_TYP_CD AS property_type, RGN_NM AS region_name, MKT_NM AS market FROM ${catalog}.${schema}.legacy_prp_mstr;
CREATE OR REPLACE TABLE ${catalog}.${schema}.ref_d17_gl_accounts AS SELECT ACCT_ID AS account_id, ACCT_NM AS account_name, ACCT_CLS_CD AS account_class FROM ${catalog}.${schema}.legacy_gl_acct;
CREATE OR REPLACE TABLE ${catalog}.${schema}.ref_d17_gl_transactions AS SELECT TXN_ID AS transaction_id, PRP_ID AS property_id, ACCT_ID AS account_id, PSTG_DT AS posting_date, FSCL_PRD AS fiscal_quarter, AMT AS amount, CRNCY_CD AS currency, TXN_DSC AS description, SRC_SYS_CD AS source_system FROM ${catalog}.${schema}.legacy_gl_txn;
CREATE OR REPLACE TABLE ${catalog}.${schema}.ref_d17_leases AS SELECT LSE_ID AS lease_id, PRP_ID AS property_id, TNT_ID AS tenant_id, LSE_STRT_DT AS lease_start, LSE_END_DT AS lease_end, MTH_RNT_AMT AS monthly_rent, LSE_STS_CD AS lease_status, UPD_DT AS updated_at FROM ${catalog}.${schema}.legacy_lse;
CREATE OR REPLACE TABLE ${catalog}.${schema}.ref_d17_tenants AS SELECT TNT_ID AS tenant_id, TNT_NM AS tenant_name, IND_NM AS industry, CR_RTG AS credit_rating FROM ${catalog}.${schema}.legacy_tnt;
CREATE OR REPLACE TABLE ${catalog}.${schema}.ref_d17_quarterly_targets AS SELECT PRP_ID AS property_id, FSCL_QTR AS fiscal_quarter, NP_TGT_AMT AS net_profit_target, REV_TGT_AMT AS revenue_target FROM ${catalog}.${schema}.legacy_qtr_tgt;

-- @rung R3: column comments
ALTER TABLE ${catalog}.${schema}.ref_d17_properties ALTER COLUMN property_id COMMENT 'Property identifier.';
ALTER TABLE ${catalog}.${schema}.ref_d17_properties ALTER COLUMN property_name COMMENT 'Property name, e.g. Harbor Tower.';
ALTER TABLE ${catalog}.${schema}.ref_d17_properties ALTER COLUMN property_type COMMENT 'Property type code: OFF = Office, MFH = Multifamily, RTL = Retail.';
ALTER TABLE ${catalog}.${schema}.ref_d17_properties ALTER COLUMN region_name COMMENT 'Region: Southeast, Northeast, Western Europe.';
ALTER TABLE ${catalog}.${schema}.ref_d17_properties ALTER COLUMN market COMMENT 'Market (city), standardized, e.g. Miami Beach, Luxembourg City.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_accounts ALTER COLUMN account_id COMMENT 'GL account identifier.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_accounts ALTER COLUMN account_name COMMENT 'GL account name, e.g. Base Rent, Repairs & Maintenance.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_accounts ALTER COLUMN account_class COMMENT 'Account class: R = Revenue, O = Operating expense, M = Management fee, C = CapEx, I = Intercompany recharge.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN transaction_id COMMENT 'Posting identifier.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN property_id COMMENT 'Property the posting belongs to.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN account_id COMMENT 'GL account of the posting.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN posting_date COMMENT 'Posting date.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN fiscal_quarter COMMENT 'Fiscal quarter of the posting, YYYY-Qn.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN amount COMMENT 'Posting amount in EUR, always positive.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN currency COMMENT 'Currency code (EUR).';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN description COMMENT 'Posting text, e.g. invoice number and vendor.';
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN source_system COMMENT 'Source ledger (YARDI, SAP-LUX).';
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN lease_id COMMENT 'Lease identifier.';
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN property_id COMMENT 'Property leased.';
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN tenant_id COMMENT 'Tenant.';
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN lease_start COMMENT 'Lease start date.';
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN lease_end COMMENT 'Lease end (expiry) date.';
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN monthly_rent COMMENT 'Monthly rent in EUR.';
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN lease_status COMMENT 'Lease status code: A = Active, P = Pending Renewal, X = Expired.';
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN updated_at COMMENT 'Date this version of the lease was recorded.';
ALTER TABLE ${catalog}.${schema}.ref_d17_tenants ALTER COLUMN tenant_id COMMENT 'Tenant identifier.';
ALTER TABLE ${catalog}.${schema}.ref_d17_tenants ALTER COLUMN tenant_name COMMENT 'Tenant (company) name.';
ALTER TABLE ${catalog}.${schema}.ref_d17_tenants ALTER COLUMN industry COMMENT 'Tenant industry.';
ALTER TABLE ${catalog}.${schema}.ref_d17_tenants ALTER COLUMN credit_rating COMMENT 'Credit rating (S&P scale).';
ALTER TABLE ${catalog}.${schema}.ref_d17_quarterly_targets ALTER COLUMN property_id COMMENT 'Property.';
ALTER TABLE ${catalog}.${schema}.ref_d17_quarterly_targets ALTER COLUMN fiscal_quarter COMMENT 'Fiscal quarter, YYYY-Qn.';
ALTER TABLE ${catalog}.${schema}.ref_d17_quarterly_targets ALTER COLUMN net_profit_target COMMENT 'Net profit target in EUR.';
ALTER TABLE ${catalog}.${schema}.ref_d17_quarterly_targets ALTER COLUMN revenue_target COMMENT 'Revenue target in EUR.';

-- @rung R4: table descriptions, primary and foreign keys (informational)
COMMENT ON TABLE ${catalog}.${schema}.ref_d17_properties IS 'Property master: one row per active property. Primary key property_id.';
COMMENT ON TABLE ${catalog}.${schema}.ref_d17_gl_accounts IS 'Chart of accounts: one row per GL account. Primary key account_id.';
COMMENT ON TABLE ${catalog}.${schema}.ref_d17_gl_transactions IS 'General-ledger postings: one row per posting. Primary key transaction_id; property_id references ref_d17_properties, account_id references ref_d17_gl_accounts. All amounts are positive; the account class gives the sign.';
COMMENT ON TABLE ${catalog}.${schema}.ref_d17_leases IS 'Lease history: one row per lease VERSION. A lease can have several versions; the current one has the latest updated_at. Primary key (lease_id, updated_at); property_id references ref_d17_properties, tenant_id references ref_d17_tenants.';
COMMENT ON TABLE ${catalog}.${schema}.ref_d17_tenants IS 'Tenant master: one row per tenant. Primary key tenant_id.';
COMMENT ON TABLE ${catalog}.${schema}.ref_d17_quarterly_targets IS 'Quarterly targets: one row per property and fiscal quarter. Primary key (property_id, fiscal_quarter); property_id references ref_d17_properties.';
ALTER TABLE ${catalog}.${schema}.ref_d17_properties ALTER COLUMN property_id SET NOT NULL;
ALTER TABLE ${catalog}.${schema}.ref_d17_properties ADD CONSTRAINT ref_d17_properties_pk PRIMARY KEY (property_id);
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_accounts ALTER COLUMN account_id SET NOT NULL;
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_accounts ADD CONSTRAINT ref_d17_gl_accounts_pk PRIMARY KEY (account_id);
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ALTER COLUMN transaction_id SET NOT NULL;
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ADD CONSTRAINT ref_d17_gl_transactions_pk PRIMARY KEY (transaction_id);
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN lease_id SET NOT NULL;
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ALTER COLUMN updated_at SET NOT NULL;
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ADD CONSTRAINT ref_d17_leases_pk PRIMARY KEY (lease_id, updated_at);
ALTER TABLE ${catalog}.${schema}.ref_d17_tenants ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE ${catalog}.${schema}.ref_d17_tenants ADD CONSTRAINT ref_d17_tenants_pk PRIMARY KEY (tenant_id);
ALTER TABLE ${catalog}.${schema}.ref_d17_quarterly_targets ALTER COLUMN property_id SET NOT NULL;
ALTER TABLE ${catalog}.${schema}.ref_d17_quarterly_targets ALTER COLUMN fiscal_quarter SET NOT NULL;
ALTER TABLE ${catalog}.${schema}.ref_d17_quarterly_targets ADD CONSTRAINT ref_d17_quarterly_targets_pk PRIMARY KEY (property_id, fiscal_quarter);
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ADD CONSTRAINT ref_d17_gl_transactions_property_id_fk FOREIGN KEY (property_id) REFERENCES ${catalog}.${schema}.ref_d17_properties;
ALTER TABLE ${catalog}.${schema}.ref_d17_gl_transactions ADD CONSTRAINT ref_d17_gl_transactions_account_id_fk FOREIGN KEY (account_id) REFERENCES ${catalog}.${schema}.ref_d17_gl_accounts;
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ADD CONSTRAINT ref_d17_leases_property_id_fk FOREIGN KEY (property_id) REFERENCES ${catalog}.${schema}.ref_d17_properties;
ALTER TABLE ${catalog}.${schema}.ref_d17_leases ADD CONSTRAINT ref_d17_leases_tenant_id_fk FOREIGN KEY (tenant_id) REFERENCES ${catalog}.${schema}.ref_d17_tenants;
ALTER TABLE ${catalog}.${schema}.ref_d17_quarterly_targets ADD CONSTRAINT ref_d17_quarterly_targets_property_id_fk FOREIGN KEY (property_id) REFERENCES ${catalog}.${schema}.ref_d17_properties;
