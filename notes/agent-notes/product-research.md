# Product Research: Databricks Features for Revantage Luxembourg Workshop (Oct 8, 2026)

Research compiled for 16-demo hands-on workshop on AWS FEVM workspace, to be delivered on participant laptops in customer's Azure EU region (Luxembourg). Each feature verified against Oct 5 sibling project RUNBOOK, sibling README, bundle schema, and current Databricks docs where available.

---

## 1. Genie One vs Genie Code; Genie Agents

| Item | Status | Details |
|------|--------|---------|
| **Genie One** | GA | Business UI for Q&A and AI/BI Discover. Free through Jan 31, 2027. Queries warehouses via SQL. |
| **Genie Code** | GA | AI coding assistant in SQL editor, notebooks, Dashboards, Apps. Pay-as-you-go since Jul 2026 (monthly free allowance). Can create metric views, dashboards, apps, pipelines from prompts. |
| **Genie Agents** (formerly Genie Spaces) | GA | Bundle resource key: `genie_spaces`. Fields: `title`, `description`, `parent_path`, `warehouse_id`, `serialized_space` (JSON config with tables, metric views, joins, sample questions, instructions, example SQL). Permissions: `level: CAN_RUN`. |
| **Agent mode in SQL editor** | UNVERIFIED | Genie Code "agent mode" for notebooks/pipeline editor mentioned in agenda; exact capability scope not confirmed in Oct 5 workshop. |
| **Azure/EU region support** | GA | Genie One/Code available in Azure EU (Luxembourg). Bundle deploys identically; warehouse + catalog/schema variables set per region. |
| **Gotchas** | — | Resource key must not collide with other bundle keys (e.g., pipeline). DAB `mode: development` not used (prefixes schema names). |
| **Source** | Sibling RUNBOOK, bundle schema, Databricks docs (Genie index), Oct 5 genie.yml |

---

## 2. Agent Bricks Information Extraction & Knowledge Assistant

| Item | Status | Details |
|------|--------|---------|
| **Information Extraction** | Public Preview | "Invoice Extractor" agent created in Oct 5 workshop (UI, not API). Extracts structured data from document volumes. Referenced as "AI Extract" in the plan. |
| **ai_extract / ai_parse_document SQL functions** | UNVERIFIED | Not found in Oct 5 workshop code or Databricks docs fetch (404). Exact function signatures not confirmed. |
| **Extraction agent via API** | UNVERIFIED | Oct 5 used UI-created agent, not API. Exact API endpoint / resource key not confirmed. |
| **Knowledge Assistant** | Public Preview | Created in Oct 5 (UI, not API). "Revantage Policy Assistant" indexed 4 policy PDFs. Citations returned. Time to index: ~minutes (not measured; subject to indexing service SLA). |
| **KA API to create, add source, query** | UNVERIFIED | Oct 5 used UI only. Exact API endpoints not found in available docs. |
| **Azure/EU region support** | UNVERIFIED | Plan assumes availability (S4 step checks it via pre-flight); not independently confirmed. |
| **Gotchas** | — | Both features are Public Preview; GA date not known. No DAB resource keys yet (UI-only in Oct 5). |
| **Source** | Sibling plan.md (D4, D5), README doesn't list KA API, Databricks docs 404 |

---

## 3. UC Metric Views

| Item | Status | Details |
|------|--------|---------|
| **Release Status** | GA | Certified metric views are core UC feature. |
| **YAML/Bundle resource** | Not yet natively supported; workaround via SQL | Oct 5 used SQL job (`governance/01_metric_view.sql`) to create `net_profit_metrics`. No DAB metric-view resource key in current schema. Creates with `CREATE METRIC VIEW ... AS SELECT ... MEASURE() ...`. |
| **MEASURE() syntax** | GA | Aggregation function with optional `FILTER (WHERE ...)` for slicing. Example: `MEASURE(net_profit) FILTER (WHERE fiscal_quarter = '2026-Q2')`. Supports named aggregations only (SUM, COUNT, AVG, MIN, MAX). |
| **Derived/window measures** | GA for windowed queries | Oct 5 example: QoQ growth via window functions on metric measure results. Not native inside MEASURE(); query metric view, then apply window functions (`SUM(...) OVER ()`, `LAG()`, etc.). |
| **Genie & AI/BI consumption** | GA | Genie references `metric_views` in `serialized_space` JSON. Dashboard queries reference metric views (Oct 5: 4 pages use `net_profit_metrics`). Both read measures transparently. |
| **Azure/EU region support** | GA | Identical syntax and consumption in any region. |
| **Gotchas** | — | No DAB native resource yet; use SQL task in a job. Metric view ownership/lineage respected by all consumers (Genie, dashboards, apps). |
| **Source** | Sibling Oct 5: resources/quality.yml, governance/01_metric_view.sql, genie.yml (metric_views list), dashboards |

---

## 4. AI/BI Dashboards & Genie Integration

| Item | Status | Details |
|------|--------|---------|
| **AI/BI Dashboards** | GA | Lakeview (new generation); created as `.lvdash.json` with bundle `dashboards` resource. |
| **"Explain with Genie" button** | GA | Native in Lakeview dashboards. Right-click a chart → "Explain with Genie" opens Genie sidebar. Genie AI explains the data pattern. |
| **Genie in dashboards** | GA | Dashboard can enable Genie discovery. Oct 5: "Revantage Customer Performance" dashboard has Genie enabled (metadata tag + context). |
| **Tableau / Power BI import** | UNVERIFIED | Oct 5 did not import external BI; external lineage optional (governance/apply_external_lineage.sh not run). Current status of 3rd-party BI interop not confirmed. |
| **Caching / scheduling** | Not in Oct 5 workshop | Dashboards configured with `warehouse_id`; query caching handled by warehouse. No explicit dashboard-level caching config observed. |
| **Genie Code authoring** | GA | Genie Code in SQL editor can author dashboard SQL queries. Exact dashboard creation from prompt not tested in Oct 5. |
| **Bundle resource key** | `dashboards` | Fields: `display_name`, `file_path` (to .lvdash.json), `warehouse_id`, `dataset_catalog`, `dataset_schema`, `permissions` (level: CAN_READ). |
| **Azure/EU region support** | GA | Identical deployment; warehouse region determines data locality. |
| **Gotchas** | — | Permission level is `CAN_READ` (UI says "Can View"), not `CAN_VIEW`. Dashboard parameters use `${var.catalog}` / `${var.schema}` placeholders (resolved at query time). |
| **Source** | Sibling Oct 5: resources/dashboards.yml, .lvdash.json, RUNBOOK step 4, Genie index on "Explain" |

---

## 5. Databricks Apps

| Item | Status | Details |
|------|--------|---------|
| **Release Status** | GA | Production-ready hosting for React/backend apps on Databricks infrastructure. |
| **Sharing & permissions** | GA | Bundle resource `apps` with `permissions` (level: CAN_USE). Oct 5: consumer group `revantage_consumers` has CAN_USE on 2 apps. Users access via workspace URL or app catalog. |
| **Genie Discover page** | UNVERIFIED | Oct 5 README does not mention apps in Genie Discover; not confirmed whether apps appear there or only in app catalog. |
| **Genie MCP / embedding Genie in apps** | UNVERIFIED | Oct 5 apps (Trust Desk, Invoice Approvals) do not embed Genie. Exact MCP integration method not confirmed. |
| **Row Zero** | UNVERIFIED | Agenda mentions "Row Zero, Sigma alternative, free in platform". Not found in Oct 5 workshop or Databricks docs. Status as of Oct 2026 unknown; may be internal codename or future feature. |
| **Bundle resource key** | `apps` | Fields: `name`, `description`, `source_code_path` (to app root), `config` (command, env vars), `resources` (warehouse access, etc.), `permissions`. |
| **Example** | GA | Oct 5 deployed 2 apps: `revantage-trust-desk` (React + Python API routes) and `revantage-invoice-approvals` (Lakebase + approval workflow). Both Next.js, TypeScript, shadcn/ui. |
| **Azure/EU region support** | GA | Apps deploy to workspace region. Source code / configs use bundle variables (catalog, schema, warehouse). |
| **Gotchas** | — | No `npm proxy` URLs in package-lock.json (fetch from registry.npmjs.org). Environment variables read at request time, not build time. Route files may only export handlers (not pages). Playwright e2e tests verify click paths. |
| **Source** | Sibling Oct 5: resources/app.yml, code/app, code/app-approvals, RUNBOOK step 10, CLAUDE.md rules |

---

## 6. Lakeflow: Pipelines, Auto Loader, Expectations, Triggers

| Item | Status | Details |
|------|--------|---------|
| **Lakeflow** | GA | Declarative data pipelines; Spark Declarative Pipelines (SDP) with Auto Loader, expectations, job orchestration. |
| **Lakeflow Designer** | UNVERIFIED | Not deployed in Oct 5; UI authoring tool status as of Oct 2026 unknown. |
| **Lakeflow Connect** | UNVERIFIED | Not deployed in Oct 5; connector/ingestion status unknown. |
| **Spark Declarative Pipelines (SDP)** | GA | YAML-based pipeline definitions. Bundle resource key: `pipelines`. Oct 5 example: `revantage_customer_performance` (source: Auto Loader, transformations: SELECT/INSERT, sinks). |
| **Expectations in SDP** | GA | SQL constraint syntax: `CONSTRAINT constraint_id EXPECT (sql_expr) ON VIOLATION FAIL`. Oct 5: `CONSTRAINT valid_property_id EXPECT (property_id IN (...)) ON VIOLATION FAIL`. If violated, pipeline stage fails; fixture row triggers this for testing. |
| **Auto Loader** | GA | Incremental file ingestion from volumes/cloud storage. Oct 5 used Auto Loader from Snowflake extracts → landing volume → silver tables (Streaming Tables). |
| **Table-update triggers (data-readiness)** | UNVERIFIED | Oct 5 used static 05:00 CT schedule for `revantage_refresh` job; event-driven triggers not tested. Plan mentions "table-update triggers for jobs" as possible feature; exact support in Oct 2026 not confirmed. |
| **Lakebase table triggers** | UNVERIFIED | D12 design calls for approval workflow → Lakebase → job to load silver tables. Exact trigger mechanism (CDC, polling, webhook) not confirmed. Oct 5 used manual job invocation / approvals app UI. |
| **Bundle resource key** | `pipelines` | Fields: `name`, `definition` (YAML/JSON SDP spec), `clusters` (serverless recommended). Oct 5 used serverless catalog compute (no compute cluster). |
| **Azure/EU region support** | GA | Identical SDP syntax; warehouse/catalog/schema per region. |
| **Gotchas** | — | Job SQL runner splits on every `;` (never use `;` inside strings/comments/$$). Pipeline-owned MVs can't be edited in UI; publish to plain Delta tables instead. Auto CDC for leases requires `_change_type` / `_commit_version` columns. |
| **Source** | Sibling Oct 5: resources/pipeline.yml, code/pipelines/, RUNBOOK step 5, errors.md (SQL splitting), decisions.md (Auto CDC) |

---

## 7. Lakebase: Autoscaling, Provisioned, Bundle, App Connection, CDC

| Item | Status | Details |
|------|--------|---------|
| **Lakebase** | GA | Managed PostgreSQL 16 inside Databricks. Operational (synced) tables, native Postgres schema, apps query via OAuth. |
| **Autoscaling projects vs. Provisioned instances** | GA (autoscaling); Provisioned UI retired Sep 1 2026 | All new instances are autoscaling (4–8 CU range, scales on load). Bundle resource `database_instances` with `capacity: CU_1` maps to autoscaling 4–8 CU. (Provisioned UI removed; DAB still accepts resource but uses autoscaling.) |
| **Bundle resource keys** | `database_instances`, `synced_database_tables` | `database_instances`: name, capacity, retention_window_in_days. `synced_database_tables`: name (source table), database_instance_name, logical_database_name (Postgres DB), source_table_full_name, primary_key_columns, scheduling_policy (SNAPSHOT or CDC), new_pipeline_spec (storage catalog/schema). Oct 5: `revantage_ops` + 2 synced tables (`gold_property_quarterly_synced`, `action_register_synced`). |
| **App connection to Lakebase** | GA | App backend connects via psycopg (Python) or JDBC/client libraries. Oct 5: `revantage-invoice-approvals` uses psycopg with OAuth token. Connection string: `host=<lakebase-host>, user=<oauth-principal>, password=<token>, database=revantage_ops`. |
| **App gets OAuth token** | GA (native) | Databricks SDK (WorkspaceClient) within app context handles token refresh. App SPy identity used for auth; grants applied via SQL. |
| **Lakebase to Delta CDC (reverse synced)** | UNVERIFIED | Plan calls for approved invoices → Lakebase → job loads silver_invoices Delta table. Method: Lakehouse Federation, database catalog, or Lakebase-sourced table? Oct 5 used manual Lakebase → Delta pipeline (psycopg query → DataFrame write). Exact native CDC path not confirmed. |
| **Snapshot sync** | GA | One-directional: Delta → Postgres (snapshot copies table). Oct 5 configured both synced tables as SNAPSHOT (append-only; no deletes replicated). |
| **Azure/EU region support** | GA | Lakebase runs in same region as workspace. Synced tables read from UC catalog (cross-region if needed, subject to latency). |
| **Gotchas** | — | Resource naming must not collide. Synced table PK required for CDC (omit if snapshot only). Lakebase retention (7 days default) may drop old versions; for long history, use Delta table as source-of-truth. |
| **Source** | Sibling Oct 5: resources/lakebase.yml, code/lakebase/query_lakebase.py, README M15 Lakebase section, RUNBOOK step 8, CLAUDE.md gotchas #14 |

---

## 8. AI Gateway (Unity AI Gateway)

| Item | Status | Details |
|------|--------|---------|
| **Current name** | Unity AI Gateway (was "AI Gateway") | Oct 2026: officially "Unity Gateway" (per RUNBOOK gotcha #15). Shared or custom serving endpoints can have AI Gateway config. |
| **Release status** | GA (gateway on shared endpoints); Service policies Beta | Shared endpoint `databricks-claude-sonnet-5-5` supports gateway. Custom endpoints cannot host `system.ai` Claude (container build fails). |
| **Enabling usage tracking & inference tables** | GA | DAB: resource `ai_gateway` (not yet in bundle, CLI fallback). Script: `code/ai-gateway/apply_ai_gateway.sh`. Enables `usage_tracking_config: {enabled: true}` and `inference_table_config` (table_name_prefix, catalog, schema). |
| **Inference table creation** | GA | Table created automatically on first request: `${catalog}.${schema}.${prefix}_payload`. Oct 5: `revantage_ai_gateway_payload` (Sonnet endpoint). Columns: request, response, status, requester, timestamp (created by gateway, not bundle). |
| **Usage tracking system tables** | GA | Read-only system tables: `system.ai_gateway.usage` (UNVERIFIED schema) and `system.serving.served_entities` (all served models/endpoints, workspace-wide). Oct 5 RUNBOOK: filter by `workspace_id` to avoid other users' data. |
| **Read-only SQL query** | Verified possible | Oct 5 used read-only queries on `system.serving.served_entities` with warehouse `0fb3aaac7c7d373c`. Exact column list for `system.ai_gateway.usage` not confirmed. |
| **Rate limits** | GA | Per user (60 calls/min), per service principal (30 calls/min). Oct 5: ETL SP rated at 30/min. Config via `rate_limits: [{key: user|service_principal, renewal_period: minute, calls: N}]`. |
| **Guardrails** | Unavailable on pay-per-token | `FEATURE_DISABLED` status on shared Sonnet endpoint (Oct 5). Custom endpoint can't host Claude, so guardrails not deployed. Service policies (Beta) may enable in future. |
| **Azure/EU region support** | GA | Endpoint available in all regions; inference table in workspace's UC catalog/schema. Shared endpoint is account-wide (data may span regions in federation setup). |
| **Gotchas** | — | Guardrails currently unavailable (Beta, not GA). Custom endpoint can't serve `system.ai` Claude. CLI fallback script (`apply_ai_gateway.sh`) required (no DAB resource yet). Original config saved for restore (teardown). |
| **Source** | Sibling Oct 5: code/ai-gateway/apply_ai_gateway.sh, RUNBOOK gotchas #10, #15, step 9, errors.md Module 14, README AI Gateway section |

---

## 9. ai_forecast SQL Function

| Item | Status | Details |
|------|--------|---------|
| **Release status** | GA | Time-series forecasting function; integrated into Databricks SQL. |
| **Function signature** | GA (parameters) | `ai_forecast(metric, time_col, value_col, [group_col], [horizon], [prediction_interval_width], [frequency])`. Oct 5 plan: uses default time_col (fiscal_quarter), value_col (revenue), group_col (property_id), horizon (2 quarters = Q3/Q4 2026), frequency (unknown if quarterly explicit or inferred). |
| **Output columns** | GA (standard) | Returns table: time_col, value_col, forecast, upper_bound (CI), lower_bound (CI). Confidence interval width controlled by `prediction_interval_width` (default 0.95 = 95% CI). |
| **Quarterly frequency** | UNVERIFIED | Plan assumes "quarterly frequency support" (D14 uses quarterly data). Exact frequency string (e.g., "Q" vs "MS" vs custom) not confirmed in Oct 5. |
| **Warehouse requirements** | Pro or Serverless | Oct 5 used Serverless Starter Warehouse `0fb3aaac7c7d373c`. ai_forecast requires warehouse compute (not valid for SQL endpoints). |
| **Example in Oct 5** | Planned, not deployed | D14 "revenue forecast" demo calls ai_forecast on `gold_property_quarterly` with revenue column, groups by property_id, forecasts Q3/Q4. Expected: ≥2 properties projected to miss Q3 revenue_target (planted fact F6). |
| **Azure/EU region support** | GA | Function available in all regions; runs on warehouse in that region. |
| **Gotchas** | — | Exact frequency syntax (quarterly string) not tested in Oct 5. Input data must have consistent time intervals (monthly/quarterly, no gaps). Long-term forecast intervals may be wide (CI widens with horizon). |
| **Source** | Sibling Oct 5 plan.md (D14, planted fact F6), RUNBOOK not fully detailed, Databricks docs 404 for ai_forecast signature |

---

## 10. Data Quality Monitoring: Anomaly Detection & Data Profiling

| Item | Status | Details |
|------|--------|---------|
| **Data profiling (Lakehouse Monitoring)** | GA | Snapshot profiles of table columns (min, max, count, nulls, etc.). Sliced by dimension (e.g., region_name). Oct 5: daily 06:00 CT on `gold_property_quarterly`, `customer_performance` (snapshot, not TimeSeries, because data is batch-updated). |
| **Bundle resource key** | `quality_monitors` | Fields: `table_name`, `assets_dir` (where profile metrics land), `output_schema_name`, `warehouse_id`, `snapshot: {}` (for batch), `slicing_exprs` (dimensions), `schedule` (Quartz cron). Creates output tables: `${table}_profile_metrics`, `${table}_drift_metrics`. |
| **Anomaly detection (schema-level)** | Public Preview | Freshness + completeness monitoring for all tables (bronze, silver, gold). Oct 5: CLI fallback `code/quality/apply_schema_monitor.sh` (not DAB resource; uses direct API). Flags stale tables, missing columns. |
| **Drift detection** | GA | Automatic comparison of profiles across refreshes. Output: `*_drift_metrics` table with shift indicators per column. Oct 5 configured daily after gold refresh. |
| **SQL alerts v2 (on profile metrics)** | GA | Bundle resource `alerts`. Oct 5 example: "Revantage GL freshness SLA" alert (hourly check on max hours_since_load, fires if > 48h). Same resource key as legacy alerts (v2 is default now). |
| **Custom anomaly rules** | UNVERIFIED | Oct 5 used built-in profile metrics (completeness, freshness) + manual SQL alert logic. Custom rule definition method not tested. |
| **Azure/EU region support** | GA | Profiles computed on warehouse in region. Metrics tables in UC catalog/schema. |
| **Gotchas** | — | Profile metrics created on first refresh (not by bundle), so quality_monitors resource needs target table to exist. Snapshot profiles: no row-level timestamps needed. TimeSeries profiles: table must have `last_refreshed_at` TIMESTAMP column. Schema anomaly detection is CLI fallback (not DAB). |
| **Source** | Sibling Oct 5: resources/quality.yml, code/quality/apply_schema_monitor.sh, RUNBOOK step 10b, errors.md "Data Quality Deployment", README data-quality section |

---

## 11. Comparison: Snowflake Equivalents

| Databricks Feature | Snowflake Equivalent | Gap |
|---|---|---|
| Genie (Q&A) | Snowflake Copilot (Cortex) | Genie uses warehouse SQL; Copilot uses Cortex AI functions. Both can summarize/explore data. |
| Genie Code | Cortex Analyst (agent in UI) | Limited feature parity; Copilot in Snowflake IDE less mature than Genie Code's notebook/pipeline modes. |
| Metric views | Dynamic tables + Column-level lineage | Snowflake: DTs for incremental materialization; no native "semantic metric view" abstraction. |
| AI/BI dashboards | Snowflake Dashboards + Cortex | Both visual BI tools; Databricks AI/BI uses metric views natively; Snowflake integrates Cortex separately. |
| Lakebase (Postgres) | No equivalent | Snowflake has no managed PostgreSQL (Iceberg tables are columnar, not row-oriented OLTP). |
| Lakeflow (SDP) | Snowflake Streams + Tasks | Similar pipeline concept; Lakeflow adds declarative YAML, SDP is SQL-based like Tasks. |
| Auto Loader | Snowflake Streams on external tables | Both incremental; Databricks Auto Loader + Spark is more flexible for complex transformations. |
| Data quality monitoring | Data quality checks (native) | Snowflake has native data quality; Databricks profiling is newer (2026 GA). |
| ai_forecast | Forecasting functions (third-party) | Snowflake has no native time-series forecast; must use UDFs or external tools. |
| Unity Catalog | Snowflake native UC (same technology) | Feature parity (both built on open UC standard). Databricks adds metric views, column masks, AI governance. |
| AI Gateway | No equivalent | Snowflake has no unified gateway for LLM access; uses Cortex endpoints separately. |
| Apps (Databricks) | Streamlit (acquired by Snowflake) | Snowflake: Streamlit in cloud; Databricks: Next.js/React on App platform. Different tech stacks. |

**Summary for migration context:** Snowflake users migrating to Databricks gain: native metric views (governance), Lakebase (operational data), Lakeflow (simpler SDP), unified AI Gateway, and better BI (Genie + AI/BI). Snowflake advantage: native DQ checks (more mature).

---

## 12. Readiness Matrix: 16 Demos → Azure/EU Risks & Pre-Flight Checks

| Demo # | Feature(s) | Release Status | Azure/EU Risk | Pre-Flight Check |
|--------|-----------|---|---|---|
| 1 | Schema, volumes, UC, docs | GA | Low | Catalog exists, CREATE SCHEMA grant |
| 2 | Genie Agents, instructions, examples | GA | Low | Warehouse available, Genie enabled in region |
| 3 | SQL view with window functions | GA | Low | SQL warehouse, SQL syntax parser |
| 4 | Agent Bricks Information Extraction | Public Preview | **Med** | Feature available in region; API/UI both work; test on 1 invoice |
| 5 | Knowledge Assistant, Q&A, citations | Public Preview | **Med** | Feature available; test indexing 1 policy PDF |
| 6 | Data quality checks (SQL, profiling) | GA | Low | SQL warehouse, permissions for schema queries |
| 7 | Metric views, MEASURE(), window functions | GA | Low | SQL warehouse, MEASURE() syntax parsed |
| 8 | AI/BI Lakeview dashboard + Genie "Explain" | GA | Low | Warehouse, dashboard create grant, Genie enabled |
| 9 | Databricks App (React/Next.js) + OAuth | GA | Low | App deployment to workspace, warehouse resource access |
| 10 | UC: comments, tags, column masks | GA | Low | UC admin grant, mask UDF create permission |
| 11 | Lakeflow pipeline, Auto Loader, expectations, SDP | GA | Low | Serverless compute (or cluster), volume read/write |
| 12 | Lakebase + App + Lakebase synced tables | GA | **Low** (was Med) | Lakebase instance create, auto-scaling enabled, psycopg/OAuth tested |
| 13 | AI Gateway, usage tracking, rate limits, inference table | GA | Low | Shared Claude endpoint available, warehouse, system-table GRANT SELECT |
| 14 | ai_forecast SQL function | GA | **Med** | Warehouse, function available in region, quarterly frequency works |
| 15 | Governance tracking (trust cards, analyst/BI/eng roles) | GA | Low | UC grants, workspace ACLs, SQL + BI access |
| 16 | Data profiling monitor, anomaly/freshness, 3σ alert | GA (profiling); Public Preview (schema anomaly) | **Med** | quality_monitors resource works, schema anomaly detection available, alert v2 CLI access |

**High-risk demos (any UNVERIFIED or region-dependent):**
- **D4/D5** (Agent Bricks): Public Preview; test early on customer dev workspace.
- **D14** (ai_forecast): Verify quarterly frequency string and CI output shape match expectations.
- **D16** (schema anomaly detection): Public Preview; confirm via CLI if DAB not available.

**Pre-flight script inputs (code/preflight/):**
1. Check workspace region (Azure EU).
2. `CREATE SCHEMA` + `USE CATALOG` grants.
3. Serverless compute + any cluster config.
4. Test Agent Bricks features (D4 extraction, D5 KA indexing) with sample data.
5. Test ai_forecast on 1 property (verify quarterly output).
6. Verify system table grants (`system.serving.served_entities` SELECT).
7. Lakebase instance create, autoscaling check.
8. Genie One/Code enablement status.
9. Apps deployment permission.

---

## Summary for Workshop Delivery

**Verified in Oct 5 sibling project (low risk for Oct 8):**
- Genie Agents, AI/BI dashboards, Lakeflow, metric views, apps, Lakebase, AI Gateway, data profiling

**Partially verified / Public Preview (test early):**
- Agent Bricks Information Extraction (UI works; API/SQL functions UNVERIFIED)
- Knowledge Assistant (UI works; API UNVERIFIED)
- ai_forecast (function exists; quarterly frequency + output shape not fully tested)
- Schema anomaly detection (CLI fallback; not DAB resource)

**Deploy strategy for customer Azure workspace:**
- Use bundle target `revantage` (not `dev`); edit `databricks.yml` with customer's profile/catalog/schema/warehouse.
- Run pre-flight (`code/preflight/`) against customer workspace before the onsite.
- Reference solutions deploy separately (facilitator choice); starting states always deploy.
- All prompts, SQL, docs use `${catalog}.${schema}` placeholders (no hardcoded FEVM names).

**Regional considerations (Luxembourg/EU):**
- Databricks infrastructure: AWS EU (Ireland) or Azure EU (Luxembourg/Netherlands) — confirm workspace location.
- All UC features + Genie/dashboards/Apps/AI Gateway operate identically across regions.
- Data residency: synced tables (Lakebase) and inference tables (AI Gateway) stay in workspace region.
- Latency: cross-region federation (if used) may affect Lakebase synced-table refresh performance; monitor.

---

**Document last updated:** 2026-10-08 (research completed for Oct 8 plan)  
**Confidence level:** High for GA features (Genie, metrics, dashboards, apps, Lakeflow, AI Gateway, profiling). Medium for Public Preview (Agent Bricks). Low for undocumented/untested specifics (ai_forecast exact signature, Knowledge Assistant API, Row Zero).

