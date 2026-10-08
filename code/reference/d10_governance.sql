-- D10 reference: what participants apply live in Demo 10. Reverse with d10_reset.sql.
-- Placeholders: ${catalog}, ${schema}. Unmasked PII is for members of revantage_finance_stewards.

COMMENT ON TABLE ${catalog}.${schema}.gold_property_quarterly IS
  'How each property performed each quarter: revenue, costs, and net profit in euros, compared with its budget (target) and the previous quarter. Certified by Finance; use it for executive and board reporting. One row per property per quarter, 2024-Q1 to 2026-Q2.';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN net_profit COMMENT
  'Net profit in EUR, Finance definition: revenue minus operating expenses minus management fees. Capital expenditure and intercompany charges are not deducted.';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN met_target COMMENT
  'True when net_profit is at or above net_profit_target for the quarter.';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN qoq_change_pct COMMENT
  'Change in net profit vs the previous quarter, in percent. Empty for 2024-Q1 (no earlier quarter).';
-- Governed tags: certification shows a Certified badge in Catalog Explorer and search.
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly SET TAGS ('system.certification_status' = 'certified');

-- PII: tag and mask tenant contact details.
CREATE OR REPLACE FUNCTION ${catalog}.${schema}.ref_mask_email(email STRING)
  RETURNS STRING
  COMMENT 'Column mask: full email for revantage_finance_stewards, otherwise first letter + domain.'
  RETURN CASE WHEN is_account_group_member('revantage_finance_stewards') THEN email
              ELSE concat(left(email, 1), '***@', split_part(email, '@', 2)) END;
CREATE OR REPLACE FUNCTION ${catalog}.${schema}.ref_mask_phone(phone STRING)
  RETURNS STRING
  COMMENT 'Column mask: full phone for revantage_finance_stewards, otherwise last 3 digits.'
  RETURN CASE WHEN is_account_group_member('revantage_finance_stewards') THEN phone
              ELSE concat('*** *** ', right(phone, 3)) END;
ALTER TABLE ${catalog}.${schema}.customer_performance ALTER COLUMN contact_email SET MASK ${catalog}.${schema}.ref_mask_email;
ALTER TABLE ${catalog}.${schema}.customer_performance ALTER COLUMN contact_phone SET MASK ${catalog}.${schema}.ref_mask_phone;
ALTER TABLE ${catalog}.${schema}.customer_performance ALTER COLUMN contact_email SET TAGS ('class.email_address');
ALTER TABLE ${catalog}.${schema}.customer_performance ALTER COLUMN contact_phone SET TAGS ('class.phone_number');
