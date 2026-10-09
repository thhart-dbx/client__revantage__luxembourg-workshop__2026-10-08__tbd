# Demo 13: AI Gateway & Monitoring — "Who's using what, and what's it costing us?"

**Session:** Day 2, 11:30–12:15 (45 min) · **You build:** a usage + cost query pack and a SQL alert · **Reference:** `code/reference/d13_ai_gateway_queries.sql`, alert "[Revantage workshop] Daily AI tokens > 1M (Reference)"
**Starting state:** AI Gateway usage tracking (+ inference table `ref_d13_payload`) on `databricks-claude-sonnet-4-6`; read access to `system.ai_gateway`, `system.serving`, `system.billing` (**admin grant, check in pre-flight**)
**Where:** Serving → endpoint → AI Gateway; SQL editor with Genie Code; Alerts

**Important:** system tables cover the whole account/metastore. Every query filters on your workspace ID
(`:workspace_id`, the number after `?o=` in your browser URL). There's no `current_workspace_id()` function. Usage rows arrive with a delay of up to a few hours.

## Stage 1: Models without deploying (5 min)
**Serving** → show the pay-per-token endpoints already there (Claude, GPT, Llama, Qwen…). Open `databricks-claude-sonnet-4-6` → **AI Gateway**: usage tracking, inference table, rate limits, guardrails, fallbacks. Then call it from SQL:
```sql
SELECT ai_query('databricks-claude-sonnet-4-6', 'In one sentence: why did Harbor Tower miss its Q2 target?')
```

## Stage 2: Tokens by endpoint (7 min)
**Prompt** (Genie Code, SQL editor):
> Using system.ai_gateway.usage, show total requests, total tokens and average latency by endpoint (or service_name when endpoint_name is null) for workspace :workspace_id over the last 30 days.

**Expected:** like Q1 in the reference file. On the FEVM: `system.ai.gpt-5-6-sol` ~1.58M tokens (46 requests), plus ~135–145 calls each to **MCP services** (Gmail, Slack, Google Drive, Atlassian, Microsoft 365, GitHub). Those are Genie One connectors, governed through the same gateway.

## Stage 3: Who, and what fails (8 min)
> Show the top 5 users by tokens with their email masked like t***@domain, then the error rate (status_code >= 400) by endpoint.

**Expected:** masked requesters; error rate per endpoint (FEVM: gpt-5-6-sol 2.2%). Point out `routing_information` (fallback attempts) and `mcp_metadata` (which tool was called).

## Stage 4: What it costs (10 min)
> Estimate list-price cost by product and endpoint for the last 30 days by joining system.billing.usage to system.billing.list_prices on sku_name, cloud, usage_unit and the price validity window, for billing_origin_product in MODEL_SERVING, AI_GATEWAY, AI_FUNCTIONS, AGENT_BRICKS, VECTOR_SEARCH.

**Expected:** Q4 in the reference file. On the FEVM the biggest AI line was **VECTOR_SEARCH** for a Knowledge Assistant's index (~180 DBU in 30 days), more than all LLM calls. Lesson: KA indexes cost money while idle; delete the ones you don't use.

## Stage 5: Alert before the bill does (10 min)
> Write a query returning today's total tokens for workspace :workspace_id from system.ai_gateway.usage as a single column tokens_today.

**Alerts → Create alert** on that query: condition `tokens_today > 1000000`, schedule hourly, notify yourself (email).
**Checkpoint:** open the reference alert "Daily AI tokens > 1M (Reference)"; it evaluates OK today. Q5 shows **2026-10-05 at 1.47M tokens**, a day it would have fired.

## Stage 6: Governance tie-in (5 min, talk)
Usage and inference tables are Unity Catalog tables: grant, lineage, and retention like any data. Guardrails (PII, safety) and rate limits per user/group live on the gateway. The same view covers Genie, agents, Genie Code sessions, and MCP connectors.

## Wrap-up
- **So what:** one place to see every AI call, by person, model, and cost, with an alert before budget surprises.
- **Snowflake equivalent:** Cortex usage views (ACCOUNT_USAGE). The AI Gateway adds runtime controls (rate limits, guardrails, fallbacks, inference logging) across external and hosted models and MCP.
- **Verified:** 2026-10-08 on the FEVM workspace: all 5 reference queries run with real results (above); the alert deployed and ACTIVE, query returns `tokens_today`. 40 ai_query requests + 3 deliberate 400 errors were sent to sonnet-4-6 at 21:18 UTC; their arrival in `system.ai_gateway.usage` is pending (system-table delay; recheck). Stage 2 run in the Genie Code UI (S9): Genie Code read the table schema, wrote and ran the query; 8 rows identical to reference Q1 (7 MCP services + gpt-5-6-sol 1,577,845 tokens). Stages 3–5: UI pending.
