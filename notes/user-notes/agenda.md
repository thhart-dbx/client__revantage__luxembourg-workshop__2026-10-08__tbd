# Revantage Luxembourg Onsite — Two-Day Workshop Agenda (as provided by the user, 2026-10-08)

> Verbatim from the user's paste, except for whitespace. Deviations decided during the build are in
> `notes/agent-notes/decisions.md` (single schema with prefixes; gold = 80 rows ending 2026-Q2; etc.).
> Day 1 = 2026-10-13 per the user.

**Dates:** Wednesday & Thursday (Luxembourg local time) · **Format:** Hands-on with laptops — participants follow along and build live
**Venues:** Wednesday @ The Hub, Thursday @ New York · **Facilitators:** Thomas Hart, Raouf Zaghab
**Attendees:** Revantage Luxembourg data team + 2 additional guests for Extraction Agent demo · **Optional:** Michael Dietrich

## Pre-Workshop Preparation
- Confirm participant access to Databricks demo environment (or Revantage dev workspace if permissions granted)
- Request Thomas Hart access to Revantage dev environment for building demo assets
- Revantage team to provide 2–3 real use cases and sample documents (invoices, etc.) for realistic demos
- Prepare backup demo environment with Revantage sample data (gold_property_quarterly, etc.) if dev access is not available
- GitHub repo with workshop materials ready as fallback
- Ensure laptops are fully charged + chargers available

## Day 1 — Wednesday: Genie, Agents, Dashboards & Apps

| Time | Dur | Session | Details |
|---|---|---|---|
| 9:00–9:30 | 30 | **Welcome & Platform Overview** | Open platform: Delta/Iceberg, data in your BLOB storage (S3/ADLS/GCP), any model (GPT, Claude, open source), any data type (PDFs, Excel). Quick orientation of the workspace. |
| 9:30–10:15 | 45 | **Genie One — Business-Facing Analytics** | NL queries against Revantage data ("Which properties missed their quarterly target?"). Thought process, table references, generated SQL, charts. Desktop app vs browser vs mobile. Connectors (Slack, Microsoft 365). File attachments. Scheduled tasks. |
| 10:15–10:45 | 30 | **Genie Code — Builder's Assistant** | Genie One (business) vs Genie Code (builders). Explain queries, draft SQL, debug errors, build metric views. Compare to Snowflake's CoPilot. Hands-on: ask Genie Code about their data. |
| 10:45–11:00 | 15 | Break | |
| 11:00–11:45 | 45 | **Extraction Agent Demo** (2 extra guests) | Invoice extraction with AI Extract / AI Parse. Build an extraction agent in 3–4 minutes. Extracted fields from real documents. "Use Agent" → SQL script generation for production pipelines. |
| 11:45–12:15 | 30 | **Knowledge Assistant & Genie Agents Overview** | KA Q&A over a document corpus (internal docs, receipts, rules). Tour of other agent types. How agents scale to production via SQL. |
| 12:15–12:30 | 15 | **Genie One Data Exploration — Hands-On** | Completeness checks, data quality, cross-source comparisons, aggregated reports. Get the query behind the answer. |
| 12:30–1:30 | 60 | Lunch | |
| 1:30–2:15 | 45 | **Semantic Layer & UC Metric Views** | Why business users expect specific metric definitions. Codify KPIs in SQL via UC Metric Views. Hands-on: define 2–3 metrics with Genie Code. How Genie uses the semantic layer. |
| 2:15–3:15 | 60 | **AI/BI Dashboards** | HTML, custom visualizations, interactive charts. Import Tableau/Power BI. "Explain with Genie". Caching and refresh schedules. Build a dashboard with Genie Code. Hands-on: simple dashboard from governed metrics. |
| 3:15–3:30 | 15 | Break | |
| 3:30–4:15 | 45 | **Databricks Apps** | When dashboards aren't enough → Apps ("quick tools"). Next.js / React. Sharing like a Google Doc. Row Zero (Sigma alternative, free in platform, no per-seat). Embedding Genie endpoints/agents in apps via MCP. |
| 4:15–4:45 | 30 | **Unity Catalog & Governance Overview** | Catalogs, schemas, ownership, permissions. Sharing dashboards, apps, agents, data, code. Git versioning. Unity AI Gateway: monitor inputs/outputs. Foundation for Day 2. |
| 4:45–5:00 | 15 | Day 1 Wrap-Up & Q&A | |

## Day 2 — Thursday: Data Engineering, ML & Office Hours (data engineers join)

| Time | Dur | Session | Details |
|---|---|---|---|
| 9:00–9:30 | 30 | **Day 1 Recap & DE Context** | Raw sources → business outputs. |
| 9:30–10:30 | 60 | **Lakeflow — Managed Ingestion & ETL** | Lakeflow Connect (Workday, Salesforce…). Medallion. Lakeflow Designer. Spark Declarative Pipelines: streaming tables, MVs, expectations. Genie Code Agent mode for pipelines. Hands-on: pipeline from NL requirements. |
| 10:30–10:45 | 15 | Break | |
| 10:45–11:30 | 45 | **Lakebase & Production Operations** | Operational DB for apps/agents. Reverse ETL. Lakeflow Jobs: orchestration, dependencies, retries, triggers. Pipeline health, freshness, quality monitoring. |
| 11:30–12:15 | 45 | **AI Gateway & Monitoring** | Deployed models already available. Use LLMs without deploying. Who's sending what. System tables: `system.ai_gateway`, billing. Hands-on: usage and cost attribution. |
| 12:15–12:30 | 15 | **Time Series Forecasting** | `ai_forecast` in SQL. Prophet, ARIMA, GARCH/AR overview. Quick demo with property data. |
| 12:30–1:30 | 60 | Lunch | |
| 1:30–2:30 | 60 | **Hands-On Lab: Build Your Own** | DEs: pipelines/ETL/monitoring. Analysts: dashboards, Genie spaces, metric views. All: Genie Code. |
| 2:30–2:45 | 15 | Break | |
| 2:45–3:45 | 60 | **Office Hours: Q&A & Deep Dives** | Revantage use cases, architecture, migration planning from Snowflake. |
| 3:45–4:15 | 30 | **Data Quality & Observability** | Profiling: freshness, completeness, drift. Alerts on DQ metrics. Lineage: table, column, dashboard impact. |
| 4:15–4:45 | 30 | **Next Steps & Action Items** | Follow-ups, quick wins, adoption roadmap, resources. |
| 4:45–5:00 | 15 | Closing | |

**Key themes:** hands-on first; real data when possible; Genie Code as constant companion; end-to-end
journey raw → governed → semantic → Genie/dashboards/apps; Snowflake migration comparisons.

**Demo checklist:** Extraction Agent (invoices) · Genie One exploration · Genie Code builder workflow ·
AI/BI dashboard with Genie · Databricks App · Lakeflow pipeline · AI Gateway + system tables · ai_forecast ·
Row Zero / spreadsheet-style analytics.

---

## Hands-On Demo Playbook (each demo builds on the previous one)

### Demo 1 — Welcome & Platform Overview · "Where does my data live?"
Problem: migrating from Snowflake; need to find catalogs, schemas, tables, volumes, compute. Value: no Day-1 friction.
Dataset: `bronze` raw CSVs (regions, properties, tenants, leases, gl_accounts, gl_transactions, quarterly_targets); `silver` cleansed; `gold`: gold_property_quarterly, customer_performance; `documents` volume (invoices, lease agreements, policy PDFs).
Builds: navigate catalog, three-level namespace, SQL editor, `SELECT * FROM gold.gold_property_quarterly LIMIT 10`, open Genie Code side panel.

### Demo 2 — Genie One: Business-Facing Analytics · "Property Performance Q&A"
Problem: PMs/asset managers need answers without SQL. Dataset: gold_property_quarterly (property_id, property_name, property_type, region_name, market, fiscal_quarter, revenue, net_profit, net_profit_target, revenue_target, met_target, prior_quarter_net_profit, qoq_change_pct).
Questions: 1 "Which properties missed their quarterly target in 2026-Q2?" 2 "What changed from Q1 to Q2 for the Southeast region?" 3 "Show me revenue by property type as a bar chart" 4 "Which market has the highest quarter-over-quarter net profit growth?" 5 "Summarize the top 3 risks across the portfolio this quarter". Show thought process, SQL, chart, sharing a thread.

### Demo 3 — Genie Code: Builder's Assistant · "Fix and enhance a broken Snowflake view"
Pre-written Snowflake SQL with NVL(), DATEADD(), QUALIFY, and a missing join condition that duplicates rows; gold_property_quarterly joined to silver_properties.
Builds: paste into SQL editor → "Explain this query and identify any issues for Databricks" → "Fix the syntax errors and adapt for Databricks SQL" → "Add a YoY comparison column showing net_profit change versus the same quarter last year" → "Why are there duplicate rows?" → run corrected query, verify row counts.

### Demo 4 — Extraction Agent · "Invoice-to-Table in 4 minutes"
5–10 invoice PDFs in documents/invoices (varied vendors, layouts, currencies). Builds: Agent Bricks → new AI Extract agent "Invoice Extractor" → point to volume → schema vendor_name, invoice_number, invoice_date, due_date, line_items[] (description, quantity, unit_price, amount), subtotal, tax, total, currency → run, review side-by-side → "Use Agent" → SQL script → drop into a Lakeflow pipeline.

### Demo 5 — Knowledge Assistant · "Ask the Policy Book"
Policies: Expense Approval, Capital Expenditure Guidelines, Lease Renewal Procedures, Intercompany Transfer. Builds: KA "Revantage Policy Assistant" → add docs → ask "What is the approval threshold for expenses over €50,000?", "If a tenant's lease expires in 90 days, what steps should I take?", "Is a new HVAC system for Harbor Tower classified as CapEx or OpEx?" → citations → share.

### Demo 6 — Genie One Data Exploration · "Audit your data before you trust it"
bronze_properties issues: 2 NULL region_id, 1 duplicate property_name with different IDs, 3 market mismatches vs silver; bronze 10 vs gold 8.
Builds: "How many properties are in the bronze layer vs. the gold layer?" · "Which properties exist in bronze but not in gold?" · "Show me the null rate for every column in bronze_properties" · "Are there any duplicate property names with different IDs?" · "Compare market names between bronze and silver for mismatches" · copy SQL into a notebook as a recurring check.

### Demo 7 — Semantic Layer & UC Metric Views · "Define Net Profit Margin once"
Finance NP = revenue − opex − mgmt fees; asset management also subtracts CapEx. Builds: "Help me create a UC metric view for net_profit_margin defined as net_profit / revenue" → `metrics.net_profit_margin` (MEASURE) → `metrics.target_attainment` (% properties meeting net_profit_target) → `metrics.qoq_revenue_growth` → test `WHERE fiscal_quarter = '2026-Q2'` → ask Genie One Demo 2 Q1 again; answer references the governed metric.

### Demo 8 — AI/BI Dashboards · "Executive Portfolio Review" (3 pages, built with Genie Code)
P1 Executive Summary: KPIs (total revenue, NP margin, target attainment %), portfolio trend by quarter. P2 Regional Performance: NP by region bar, revenue vs target scatter by property, heat map QoQ by market. P3 Exceptions & Risks: missed-target table, QoQ decline flags, filters region/type/quarter. Filters fiscal_quarter and region_name. "Explain with Genie" on Southeast bar: "Why did Southeast net profit drop in Q2?" Caching, refresh schedule, sharing via Genie One.

### Demo 9 — Databricks Apps · "Lease Expiry Tracker"
silver_leases, silver_tenants, silver_properties (~50 leases, some within 90/180/365 days, some expired).
Builds: "Create a Databricks App that shows leases expiring in the next 90, 180, and 365 days" → filters (window, region, type) → sortable table (property, tenant, lease end, monthly rent, days remaining, risk flag) → summary cards (leases expiring, revenue at risk, avg credit rating) → export → deploy + share → visible in Genie One Discover.

### Demo 10 — Unity Catalog & Governance · "Who can see what, and why?"
Builds: open gold_property_quarterly in Catalog Explorer → owner, description, comments, tags, lineage → "Write a description for the gold_property_quarterly table suitable for a non-technical business user" → apply + column comments for net_profit, met_target, qoq_change_pct → permissions panel, inheritance → AI Gateway briefly.

### Demo 11 — Lakeflow · "Bronze-Silver-Gold in 20 minutes"
Raw CSVs in raw volume. Builds: "I have raw CSV files for properties, leases, and GL transactions. Design a Bronze → Silver → Gold pipeline using Lakeflow" → Auto Loader bronze → silver (cast, nulls, dedupe by PK, business names) → gold (GL to property-quarter, join targets, met_target, qoq_change_pct) → expectations `revenue IS NOT NULL`, `fiscal_quarter MATCHES '\d{4}-Q[1-4]'` → run, DAG, row counts → Genie Code diagnoses a failed expectation.

### Demo 12 — Lakebase & Production Operations · "Approval workflow state machine"
Lakebase `invoice_approvals` (invoice_id, vendor_name, total_amount, extracted_at, status Pending/Approved/Rejected, reviewed_by, reviewed_at); job loads Approved into `silver_invoices`.
Builds: create Lakebase project + DB → table → insert 5 Pending → app reads Lakebase, writes approval → Lakeflow Job depending on approved records → retries, failure alerts, run history.

### Demo 13 — AI Gateway & Monitoring · "Who's using what, and what's it costing us?"
system.ai_gateway usage, served entities, system.billing.usage, list_prices.
Builds: "Show me total tokens consumed by AI Gateway endpoint in the last 30 days" → top 5 users by tokens → error rate by endpoint → estimated cost (usage × list_prices) → "Alert me if daily token usage exceeds 1M tokens" → SQL Alert with email.

### Demo 14 — Time Series Forecasting · "Where is revenue heading?"
gold_property_quarterly, 10 quarters (2024-Q1..2026-Q2), horizon 2026-Q3/Q4. Builds: single-property ai_forecast → grouped with group_col → compare Q3 forecast vs revenue_target → when ai_forecast vs Prophet/ARIMA/GARCH → embed into Portfolio Review dashboard as trend line with CI.

### Demo 15 — Hands-On Lab: Build Your Own
Track A Analyst: new Genie space, tables, context, synonyms, example SQL, test 5 questions. Track B Dashboard: dashboard for a portfolio company using Demo 7 metric views + Genie. Track C DE: new pipeline, expectations, incremental, Job with schedule and alerting.

### Demo 16 — Data Quality & Observability · "Trust scorecard"
Seed: insert a 2026-Q3 row with NULL net_profit and revenue 10× historical average. Builds: enable monitoring on gold_property_quarterly → profile → freshness → drift flags 10× outlier → completeness flags NULL → lineage gold → metric views → dashboard → Genie (blast radius) → SQL Alert: revenue > 3σ from property's historical mean.
