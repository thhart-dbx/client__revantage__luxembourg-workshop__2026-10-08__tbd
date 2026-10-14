"""Expected-output screenshot for every step of every demo (module deck).

Key: (demo number, stage key, prompt index). Stage key = the start of the guide's stage heading
("Stage 3", "Track A", "Closing"); prompt index = 1-based position of the prompt inside that stage
(0 for steps without a prompt). Value: how the expected output is captured:
  ("file", name)        existing live screenshot in notes/agent-notes/screenshots/ (or assets/)
  ("sql", query)        saved query on the workshop warehouse (catalog/schema preset), run, captured
  ("url", path)         workspace page, captured as is
  ("genie", agent, q)   question asked in a Genie Agent ("start" / "reference"), answer captured
  ("ka", question)      question asked in the Knowledge Assistant
  ("pg", query)         Lakebase SQL (SQL editor attached to revantage-lux-ops / revantage_ops)
  ("talk", None)        talk-track step: no screenshot
Captured files are named m-d{demo:02d}-{stage}-{prompt}.png in notes/agent-notes/screenshots/modules/.
"""
WS = "7474657569423450"  # FEVM workspace id used for the captures
VOL = "/Volumes/thhart_october_2026_catalog/revantage_20261008"

STEPS = {
    # D0 Getting started (UI captures; Stage 4 run into the scratch schema revantage_20261008_m0test)
    (0, "Stage 1", 0): ("file", "modules/m-d00-stage1-0.png"),
    (0, "Stage 2", 0): ("file", "modules/m-d00-stage2-0.png"),
    (0, "Stage 3", 1): ("file", "modules/m-d00-stage3-1.png"),
    (0, "Stage 4", 0): ("file", "modules/m-d00-stage4-0.png"),
    (0, "Stage 5", 1): ("file", "modules/m-d00-stage5-1.png"),
    # D1 Platform overview
    (1, "Stage 1", 0): ("url", "/?o=" + WS),
    (1, "Stage 2", 0): ("url", "/explore/data/volumes/thhart_october_2026_catalog/revantage_20261008/documents?o=" + WS),
    (1, "Stage 3", 0): ("sql", "SELECT COUNT(*) AS rows, COUNT(DISTINCT property_id) AS properties,\n       MIN(fiscal_quarter) AS first_quarter, MAX(fiscal_quarter) AS last_quarter\nFROM gold_property_quarterly"),
    (1, "Stage 4", 1): ("url", "/explore/data/thhart_october_2026_catalog/revantage_20261008?o=" + WS),
    (1, "Stage 4", 2): ("sql", "SELECT region_name, SUM(net_profit) AS net_profit_2026_q2\nFROM gold_property_quarterly\nWHERE fiscal_quarter = '2026-Q2'\nGROUP BY region_name ORDER BY net_profit_2026_q2 DESC"),
    (1, "Stage 5", 1): ("sql", f"SELECT regexp_extract(path, '([^/]+)$', 1) AS file,\n       ai_parse_document(content, map('version','2.0')):document.elements[0].content::string AS first_element\nFROM read_files('{VOL}/documents/leases/', format => 'binaryFile')"),
    # D2 Genie One (participants use the Start agent)
    (2, "Stage 1", 1): ("genie", "start", "Which properties missed their quarterly target in 2026-Q2?"),
    (2, "Stage 2", 1): ("genie", "start", "What changed from Q1 to Q2 for the Southeast region?"),
    (2, "Stage 2", 2): ("file", "d02-genie-southeast.png"),
    (2, "Stage 3", 1): ("genie", "start", "Show me revenue by property type as a bar chart"),
    (2, "Stage 4", 1): ("genie", "start", "Which market has the highest quarter-over-quarter net profit growth?"),
    (2, "Stage 5", 1): ("genie", "start", "Summarize the top 3 risks across the portfolio this quarter"),
    (2, "Stage 6", 0): ("talk", None),
    # D3 Genie Code: Snowflake migration
    (3, "Stage 1", 0): ("file", "s9-d03-error-autofix.png"),
    (3, "Stage 2", 1): ("file", "s9-d03-genie-code.png"),
    (3, "Stage 3", 1): ("sql", "-- The view after the syntax fix, before the join fix\nSELECT COUNT(*) AS row_count FROM (\n  SELECT g.property_id, g.fiscal_quarter\n  FROM gold_property_quarterly g\n  JOIN silver_properties p ON g.region_name = p.region_name\n  QUALIFY DENSE_RANK() OVER (ORDER BY g.fiscal_quarter DESC) <= 8)"),
    (3, "Stage 4", 1): ("sql", "-- After the join fix (ON g.property_id = p.property_id)\nSELECT COUNT(*) AS row_count, COUNT(DISTINCT property_id, fiscal_quarter) AS distinct_keys\nFROM ref_d03_property_performance_v"),
    (3, "Stage 5", 1): ("sql", "SELECT property_name, fiscal_quarter, net_profit, yoy_net_profit_change\nFROM ref_d03_property_performance_v\nWHERE fiscal_quarter = '2026-Q2'\nORDER BY yoy_net_profit_change"),
    (3, "Stage 6", 1): ("sql", "-- Row-by-row check against the reference (shown here on the reference itself)\nSELECT COUNT(*) AS differences FROM (\n  SELECT * EXCEPT (refreshed_at) FROM ref_d03_property_performance_v\n  EXCEPT ALL\n  SELECT * EXCEPT (refreshed_at) FROM ref_d03_property_performance_v)"),
    # D4 Information Extraction agent
    (4, "Stage 1", 0): ("file", "d04-agents-home.png"),
    (4, "Stage 2", 1): ("file", "d04-schema.png"),
    (4, "Stage 3", 0): ("file", "d04-extraction.png"),
    (4, "Stage 4", 1): ("sql", "SELECT response:response.invoice_number::string AS invoice_number,\n       response:response.vendor_name::string AS vendor,\n       response:response.total::double AS total,\n       response:response.currency::string AS currency\nFROM ref_invoices_extracted ORDER BY total DESC"),
    (4, "Stage 5", 1): ("sql", "SELECT i.response:response.invoice_number::string AS invoice_number,\n       i.response:response.total::double AS invoice_total,\n       i.response:response.currency::string AS currency,\n       t.amount AS gl_amount_eur, a.account_name, a.category\nFROM ref_invoices_extracted i\nJOIN silver_gl_transactions t ON t.description LIKE concat(i.response:response.invoice_number::string, '%')\nJOIN silver_gl_accounts a ON a.account_id = t.account_id"),
    (4, "Stage 6", 0): ("file", "d04-use-agent.png"),
    # D5 Knowledge Assistant
    (5, "Stage 1", 0): ("file", "d05-ka-building.png"),
    (5, "Stage 2", 1): ("ka", "What is the approval threshold for expenses over €50,000?"),
    (5, "Stage 2", 2): ("ka", "If a tenant's lease expires in 90 days, what steps should I take?"),
    (5, "Stage 2", 3): ("ka", "Is a new HVAC system for Harbor Tower classified as CapEx or OpEx?"),
    (5, "Stage 3", 1): ("ka", "What credit rating threshold requires Head of Asset Management sign-off for lease renewal?"),
    (5, "Stage 4", 1): ("sql", "SELECT ai_query('ka-234e391f-endpoint',\n  'Does invoice HV-2026-0417 (USD 339,600 chiller replacement) need CFO approval? Answer in one sentence.') AS answer"),
    (5, "Stage 5", 0): ("file", "d05-agent-types.png"),
    # D6 Genie One data exploration (Start agent) + SQL editor
    (6, "Stage 1", 1): ("genie", "start", "How many properties are in the bronze layer vs. the gold layer?"),
    (6, "Stage 2", 1): ("genie", "start", "Which properties exist in bronze but not in gold?"),
    (6, "Stage 3", 1): ("genie", "start", "Show me the null rate for every column in bronze_properties"),
    (6, "Stage 4", 1): ("genie", "start", "Are there any duplicate property names with different IDs?"),
    (6, "Stage 5", 1): ("genie", "start", "Compare market names between bronze and silver for mismatches"),
    (6, "Stage 6", 1): ("sql", "SELECT * FROM ref_d06_property_quality_checks"),
    # D7 Metric views
    (7, "Stage 1", 1): ("sql", "SELECT MEASURE(net_profit_margin) AS approved_margin,\n       MEASURE(asset_mgmt_net_profit_margin) AS asset_mgmt_margin\nFROM ref_mv_net_profit_margin\nWHERE fiscal_quarter = '2026-Q2'"),
    (7, "Stage 2", 1): ("sql", "SELECT property_name, MEASURE(net_profit_vs_target) AS net_profit_vs_target\nFROM ref_mv_target_attainment\nWHERE fiscal_quarter = '2026-Q2'\nGROUP BY property_name\nHAVING MEASURE(net_profit_vs_target) < 0\nORDER BY net_profit_vs_target"),
    (7, "Stage 3", 1): ("sql", "SELECT market, MEASURE(qoq_net_profit_growth) AS qoq_net_profit_growth,\n       MEASURE(qoq_revenue_growth) AS qoq_revenue_growth\nFROM ref_mv_qoq_revenue_growth\nWHERE fiscal_quarter = '2026-Q2'\nGROUP BY market ORDER BY qoq_net_profit_growth DESC"),
    (7, "Stage 4", 0): ("file", "d07-metric-view.png"),
    (7, "Stage 5", 1): ("genie", "reference", "Which properties missed their quarterly target in 2026-Q2?"),
    (7, "Stage 5", 2): ("genie", "reference", "What is our net profit margin this quarter, and how would it differ under the Asset Management definition?"),
    # D8 AI/BI dashboard
    (8, "Stage 1", 1): ("sql", "-- kpi_latest: each metric view aggregated on its own, then cross joined\nSELECT npm.revenue, npm.net_profit, npm.net_profit_margin, ta.target_attainment\nFROM (SELECT MEASURE(revenue) AS revenue, MEASURE(net_profit) AS net_profit,\n             MEASURE(net_profit_margin) AS net_profit_margin\n      FROM ref_mv_net_profit_margin WHERE fiscal_quarter = '2026-Q2') npm\nCROSS JOIN (SELECT MEASURE(target_attainment) AS target_attainment\n            FROM ref_mv_target_attainment WHERE fiscal_quarter = '2026-Q2') ta"),
    (8, "Stage 2", 1): ("file", "d08-p1-executive.png"),
    (8, "Stage 3", 1): ("file", "d08-p2-regional.png"),
    (8, "Stage 4", 1): ("file", "d08-p3-exceptions.png"),
    (8, "Stage 5", 1): ("file", "s9-d08-exceptions-global-filter.png"),
    (8, "Stage 6", 1): ("file", "d08-genie-southeast.png"),
    (8, "Stage 7", 0): ("url", "dashboard-share"),
    (8, "Stage 8", 1): ("file", "d08-p4-forecast.png"),
    # D9 Apps
    (9, "Stage 1", 0): ("file", "d09-create-app.png"),
    (9, "Stage 2", 1): ("file", "s9-d09-template-app.png"),
    (9, "Stage 3", 1): ("file", "d09-app.png"),
    (9, "Stage 4", 1): ("file", "s9-d09-template-app-stage4.png"),
    (9, "Stage 5", 0): ("url", "/apps-v2/app/revantage-lease-tracker/overview?o=" + WS),
    (9, "Stage 6", 0): ("talk", None),
    # D10 Unity Catalog governance
    (10, "Stage 1", 0): ("url", "/explore/data/thhart_october_2026_catalog/revantage_20261008/gold_property_quarterly/lineage?o=" + WS),
    (10, "Stage 2", 1): ("file", "d10-gold-certified.png"),
    (10, "Stage 3", 0): ("file", "d10-gold-certified.png"),
    (10, "Stage 4", 1): ("file", "d10-masked-pii.png"),
    (10, "Stage 5", 0): ("url", "/explore/data/thhart_october_2026_catalog/revantage_20261008/gold_property_quarterly/permissions?o=" + WS),
    # D11 Lakeflow
    (11, "Stage 0", 0): ("url", "/ingestion/add?o=" + WS),
    (11, "Stage 1", 1): ("url", "pipeline-editor"),
    (11, "Stage 2", 0): ("url", "pipeline-bronze"),
    (11, "Stage 3", 1): ("url", "pipeline-silver"),
    (11, "Stage 4", 0): ("file", "d11-pipeline-graph.png"),
    (11, "Stage 5", 0): ("url", "pipeline-failed-update"),
    (11, "Stage 6", 1): ("url", "pipeline-failed-genie"),
    # D12 Lakebase
    (12, "Stage 1", 0): ("talk", None),
    # Lakebase SQL tab can't switch to revantage_ops on FEVM (database dropdown stays empty) → app frame
    (12, "Stage 2", 1): ("file", "d12-approvals-app.png"),
    (12, "Stage 3", 0): ("file", "d12-approvals-app.png"),
    (12, "Stage 4", 1): ("url", "job-approved-to-silver"),
    (12, "Stage 5", 0): ("sql", "-- The synced table is also a Unity Catalog object\nSELECT count(*) AS rows, sum(net_profit) AS net_profit\nFROM ref_d12_gold_property_quarterly_synced"),
    (12, "Stage 6", 0): ("url", "/jobs/runs?o=" + WS),
    # D13 AI Gateway
    (13, "Stage 1", 0): ("sql", "SELECT ai_query('databricks-claude-sonnet-4-6',\n  'In one sentence: why did Harbor Tower miss its Q2 target? Context: anchor tenant left on 31 March; a USD 339,600 chiller replacement was booked to operating expense.') AS answer"),
    (13, "Stage 2", 1): ("sql", f"SELECT coalesce(endpoint_name, service_name) AS endpoint_or_service, service_type,\n       COUNT(*) AS requests, SUM(total_tokens) AS total_tokens, ROUND(AVG(latency_ms)) AS avg_latency_ms\nFROM system.ai_gateway.usage\nWHERE workspace_id = '{WS}' AND event_time >= current_date() - INTERVAL 30 DAYS\nGROUP BY ALL ORDER BY total_tokens DESC NULLS LAST, requests DESC"),
    (13, "Stage 2", 2): ("sql", f"SELECT e.endpoint_name, COUNT(*) AS requests,\n       SUM(u.input_token_count + u.output_token_count) AS tokens,\n       COUNT_IF(u.status_code >= 400) AS errors\nFROM system.serving.endpoint_usage u\nJOIN system.serving.served_entities e USING (served_entity_id)\nWHERE u.workspace_id = '{WS}' AND u.request_time >= current_date() - INTERVAL 30 DAYS\nGROUP BY ALL ORDER BY requests DESC"),
    (13, "Stage 3", 1): ("sql", f"SELECT coalesce(endpoint_name, service_name) AS endpoint_or_service,\n       COUNT(*) AS requests, COUNT_IF(status_code >= 400) AS errors,\n       ROUND(100 * COUNT_IF(status_code >= 400) / COUNT(*), 1) AS error_rate_pct\nFROM system.ai_gateway.usage\nWHERE workspace_id = '{WS}' AND event_time >= current_date() - INTERVAL 30 DAYS\nGROUP BY ALL ORDER BY errors DESC, requests DESC"),
    (13, "Stage 4", 1): ("sql", f"SELECT u.billing_origin_product, coalesce(u.usage_metadata.endpoint_name, '(n/a)') AS endpoint,\n       ROUND(SUM(u.usage_quantity), 2) AS dbus,\n       ROUND(SUM(u.usage_quantity * p.pricing.effective_list.default), 2) AS est_list_cost_usd\nFROM system.billing.usage u\nJOIN system.billing.list_prices p\n  ON p.sku_name = u.sku_name AND p.cloud = u.cloud AND p.usage_unit = u.usage_unit\n AND u.usage_end_time >= p.price_start_time AND (p.price_end_time IS NULL OR u.usage_end_time < p.price_end_time)\nWHERE u.workspace_id = '{WS}' AND u.usage_date >= current_date() - INTERVAL 30 DAYS\n  AND u.billing_origin_product IN ('MODEL_SERVING','AI_GATEWAY','AI_FUNCTIONS','AGENT_BRICKS','VECTOR_SEARCH')\nGROUP BY ALL ORDER BY est_list_cost_usd DESC"),
    (13, "Stage 5", 1): ("url", "alert-tokens"),
    (13, "Stage 6", 0): ("file", "d13-ai-gateway.png"),
    # D14 Forecast
    (14, "Stage 1", 1): ("sql", "SELECT * FROM AI_FORECAST(\n  TABLE(SELECT fiscal_quarter_date, revenue FROM gold_property_quarterly WHERE property_id = 3),\n  horizon => '2026-12-31', time_col => 'fiscal_quarter_date', value_col => 'revenue', frequency => 'QS')"),
    (14, "Stage 2", 1): ("sql", "SELECT * FROM AI_FORECAST(\n  TABLE(SELECT property_id, fiscal_quarter_date, revenue FROM gold_property_quarterly),\n  horizon => '2026-12-31', time_col => 'fiscal_quarter_date', value_col => 'revenue',\n  group_col => 'property_id', frequency => 'QS')\nORDER BY property_id, fiscal_quarter_date"),
    (14, "Stage 3", 1): ("sql", "SELECT property_name, fiscal_quarter, revenue_forecast, revenue_target\nFROM ref_d14_revenue_forecast\nWHERE fiscal_quarter = '2026-Q3' AND revenue_forecast < revenue_target\nORDER BY property_name"),
    (14, "Stage 4", 0): ("file", "d08-p4-forecast.png"),
    # D15 Hands-on lab (tracks reuse the finished assets)
    (15, "Track A", 0): ("file", "d02-genie-southeast.png"),
    (15, "Track B", 0): ("file", "d08-p1-executive.png"),
    (15, "Track C", 0): ("file", "d11-pipeline-graph.png"),
    (15, "Closing", 0): ("talk", None),
    # D16 Data quality
    (16, "Stage 1", 0): ("url", "/explore/data/thhart_october_2026_catalog/revantage_20261008/gold_property_quarterly/quality?o=" + WS),
    (16, "Stage 2", 1): ("talk", None),  # needs the profile tables (monitor can't be created on FEVM)
    (16, "Stage 3", 0): ("sql", "-- Seeded copy of gold (the facilitator's bad load)\nSELECT property_name, fiscal_quarter, revenue, net_profit\nFROM s9_d16_gold_clone\nWHERE property_id = 3 AND fiscal_quarter >= '2026-Q1'\nORDER BY fiscal_quarter"),
    (16, "Stage 4", 1): ("file", "d16-outlier-flagged.png"),
    (16, "Stage 5", 0): ("url", "/explore/data/thhart_october_2026_catalog/revantage_20261008/gold_property_quarterly/lineage?o=" + WS),
    (16, "Stage 6", 0): ("url", "alert-outliers"),
    # D17 Genie accuracy ladder (UI run on a scratch clone, 2026-10-10)
    (17, "Stage 1", 0): ("file", "d17-benchmark-failure-analysis.png"),
    (17, "Stage 2", 1): ("file", "d17-s2-business-names.png"),
    (17, "Stage 3", 1): ("file", "d17-s3-benchmark.png"),
    (17, "Stage 4", 1): ("file", "d17-s4-descriptions-keys.png"),
    (17, "Stage 5", 1): ("file", "d17-s5-benchmark-metric-views.png"),
    (17, "Stage 6", 0): ("file", "d17-evaluations-history.png"),
    # D18 Domains, Pages & Metrics (draft Page in an existing domain on FEVM)
    (18, "Stage 1", 0): ("file", "d18-domain-discover.png"),
    (18, "Stage 2", 1): ("file", "d18-genie-one-before-pages.png"),
    (18, "Stage 3", 1): ("file", "d18-page-genie-code.png"),
    (18, "Stage 4", 1): ("file", "d18-genie-one-reads-page.png"),
    (18, "Stage 5", 0): ("file", "d18-page-draft.png"),
}

# Overview image per demo: the finished asset participants will have built.
OVERVIEW = {0: "m-d00-stage4-0.png", 1: "architecture.png", 2: "d02-genie-southeast.png", 3: "s9-d03-genie-code.png",
            4: "d04-extraction.png", 5: "d05-ka-building.png", 6: "m-d06-stage6-1.png",
            7: "d07-metric-view.png", 8: "d08-p1-executive.png", 9: "d09-app.png",
            10: "d10-pii-columns.png", 11: "d11-pipeline-graph.png", 12: "d12-approvals-app.png",
            13: "d13-ai-gateway.png", 14: "d08-p4-forecast.png", 15: "architecture.png",
            16: "d16-outlier-flagged.png", 17: "d17-evaluations-history.png", 18: "d18-page-draft.png"}


def fname(key):
    d, stage, p = key
    return f"m-d{d:02d}-{stage.lower().replace(' ', '')}-{p}.png"
