-- Business descriptions for the starting state. gold_property_quarterly's table description and the
-- comments on net_profit, met_target, and qoq_change_pct are deliberately left empty: participants
-- write them with Genie Code in Demo 10 (reference: code/reference/d10_governance.sql).
COMMENT ON TABLE ${catalog}.${schema}.bronze_properties IS 'Raw property master extract from the property-management system (YARDI). Unvalidated: may contain duplicates, missing regions, and non-standard market names.';
COMMENT ON TABLE ${catalog}.${schema}.bronze_gl_transactions IS 'Raw monthly general-ledger postings per property and account, EUR. Unvalidated.';
COMMENT ON TABLE ${catalog}.${schema}.silver_properties IS 'Clean property master: one row per active property with region and standardized market name.';
COMMENT ON TABLE ${catalog}.${schema}.silver_leases IS 'Current rent roll: latest version of each lease with start/end dates, monthly rent (EUR), and status (Active, Pending Renewal, Expired).';
COMMENT ON TABLE ${catalog}.${schema}.silver_tenants IS 'Tenant master with industry, credit rating, and leasing contact (contains PII).';
COMMENT ON TABLE ${catalog}.${schema}.silver_gl_transactions IS 'Validated GL postings for known properties with a well-formed fiscal period.';
COMMENT ON TABLE ${catalog}.${schema}.silver_gl_accounts IS 'Chart of accounts. category drives the P&L: Revenue, OpEx, MgmtFee, CapEx, Intercompany.';
COMMENT ON TABLE ${catalog}.${schema}.customer_performance IS 'Property x tenant x fiscal quarter: rent billed and the property revenue/net profit allocated to each tenant by share of rent.';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN revenue COMMENT 'Total revenue for the quarter in EUR (base rent, service charge recoveries, other income).';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN operating_expense COMMENT 'Operating expenses in EUR (repairs, utilities, property tax, insurance, cleaning/security, leasing, professional fees).';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN mgmt_fee COMMENT 'Property management fee in EUR (3% of revenue).';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN capex COMMENT 'Capital expenditure in EUR. Not deducted from Finance net profit.';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN intercompany COMMENT 'Group shared-services recharges and intercompany interest in EUR. Not deducted from Finance net profit.';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN fiscal_quarter COMMENT 'Fiscal quarter as YYYY-Qn, e.g. 2026-Q2.';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN fiscal_quarter_date COMMENT 'First day of the fiscal quarter (use for time series and forecasting).';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN net_profit_target COMMENT 'Budgeted net profit for the quarter in EUR.';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN revenue_target COMMENT 'Budgeted revenue for the quarter in EUR.';
