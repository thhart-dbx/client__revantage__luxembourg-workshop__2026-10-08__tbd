-- D10 reset: put gold_property_quarterly and customer_performance back to the shipped starting state
-- (no gold description, no comments on the 3 columns, no tags, no masks).
COMMENT ON TABLE ${catalog}.${schema}.gold_property_quarterly IS NULL;
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN net_profit COMMENT '';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN met_target COMMENT '';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly ALTER COLUMN qoq_change_pct COMMENT '';
ALTER TABLE ${catalog}.${schema}.gold_property_quarterly UNSET TAGS ('system.certification_status');
ALTER TABLE ${catalog}.${schema}.customer_performance ALTER COLUMN contact_email DROP MASK;
ALTER TABLE ${catalog}.${schema}.customer_performance ALTER COLUMN contact_phone DROP MASK;
ALTER TABLE ${catalog}.${schema}.customer_performance ALTER COLUMN contact_email UNSET TAGS ('class.email_address');
ALTER TABLE ${catalog}.${schema}.customer_performance ALTER COLUMN contact_phone UNSET TAGS ('class.phone_number');
DROP FUNCTION IF EXISTS ${catalog}.${schema}.ref_mask_email;
DROP FUNCTION IF EXISTS ${catalog}.${schema}.ref_mask_phone;
