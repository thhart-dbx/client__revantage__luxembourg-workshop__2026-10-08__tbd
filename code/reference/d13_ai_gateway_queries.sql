-- Demo 13 reference queries. Parameter :workspace_id = the number after ?o= in your workspace URL.
-- System tables span the whole account/metastore, so always filter to your workspace.
-- Needs SELECT on system.ai_gateway, system.billing (an admin grants these once).

-- Q1. Requests and tokens by endpoint / service, last 30 days
SELECT coalesce(endpoint_name, service_name) AS endpoint_or_service, service_type,
       COUNT(*) AS requests, SUM(total_tokens) AS total_tokens,
       ROUND(AVG(latency_ms)) AS avg_latency_ms
FROM system.ai_gateway.usage
WHERE workspace_id = :workspace_id AND event_time >= current_date() - INTERVAL 30 DAYS
GROUP BY ALL ORDER BY total_tokens DESC NULLS LAST, requests DESC;

-- Q2. Top 5 users by tokens (emails masked for screen sharing)
SELECT regexp_replace(requester, '^(.).*(@.*)$', '$1***$2') AS requester_masked, requester_type,
       COUNT(*) AS requests, SUM(total_tokens) AS total_tokens
FROM system.ai_gateway.usage
WHERE workspace_id = :workspace_id AND event_time >= current_date() - INTERVAL 30 DAYS AND total_tokens IS NOT NULL
GROUP BY ALL ORDER BY total_tokens DESC LIMIT 5;

-- Q3. Error rate by endpoint
SELECT coalesce(endpoint_name, service_name) AS endpoint_or_service,
       COUNT(*) AS requests, COUNT_IF(status_code >= 400) AS errors,
       ROUND(100 * COUNT_IF(status_code >= 400) / COUNT(*), 1) AS error_rate_pct
FROM system.ai_gateway.usage
WHERE workspace_id = :workspace_id AND event_time >= current_date() - INTERVAL 30 DAYS
GROUP BY ALL ORDER BY errors DESC, requests DESC;

-- Q4. Estimated AI cost by product and endpoint (list price), last 30 days
SELECT u.billing_origin_product, coalesce(u.usage_metadata.endpoint_name, '(n/a)') AS endpoint,
       ROUND(SUM(u.usage_quantity), 2) AS dbus,
       ROUND(SUM(u.usage_quantity * p.pricing.effective_list.default), 2) AS est_list_cost_usd
FROM system.billing.usage u
JOIN system.billing.list_prices p
  ON p.sku_name = u.sku_name AND p.cloud = u.cloud AND p.usage_unit = u.usage_unit
 AND u.usage_end_time >= p.price_start_time AND (p.price_end_time IS NULL OR u.usage_end_time < p.price_end_time)
WHERE u.workspace_id = :workspace_id AND u.usage_date >= current_date() - INTERVAL 30 DAYS
  AND u.billing_origin_product IN ('MODEL_SERVING', 'AI_GATEWAY', 'AI_FUNCTIONS', 'AGENT_BRICKS', 'VECTOR_SEARCH')
GROUP BY ALL ORDER BY est_list_cost_usd DESC;

-- Q5. Daily token monitor (the alert query): tokens per day, flag days over 1M
SELECT date(event_time) AS day, SUM(total_tokens) AS tokens, SUM(total_tokens) > 1000000 AS over_1m
FROM system.ai_gateway.usage
WHERE workspace_id = :workspace_id AND event_time >= current_date() - INTERVAL 30 DAYS
GROUP BY ALL ORDER BY day DESC;
