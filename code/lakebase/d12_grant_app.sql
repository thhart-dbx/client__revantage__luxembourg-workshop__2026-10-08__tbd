-- Let an app's service principal read and write the approval state. Replace the role name with
-- the app's service_principal_client_id (`databricks apps get <app> -o json`).
GRANT USAGE ON SCHEMA approvals TO "${app_sp}";
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA approvals TO "${app_sp}";
GRANT USAGE ON ALL SEQUENCES IN SCHEMA approvals TO "${app_sp}";
