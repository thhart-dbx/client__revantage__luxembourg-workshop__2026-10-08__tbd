# Plan: Revantage Luxembourg two-day onsite (16 demos)

Source: agenda + Hands-On Demo Playbook pasted by the user 2026-10-08 (request 2).
Model: **build live**. Participants build every asset on their laptops with Genie Code. For each
demo we ship (a) a pre-provisioned **starting state**, (b) a pre-built **reference solution**
(`ref_` prefix / "(Reference)" title) proving the build works, and (c) a **Genie Code prompt
library**: one prompt per stage, with the expected result and an "if stuck" recovery.

Environment: `fevm-thhart-october-2026`, `thhart_october_2026_catalog.revantage_20261008` (single
schema, user choice), Serverless Starter Warehouse `0fb3aaac7c7d373c`.

## 1. Common dataset: "Revantage Luxembourg portfolio"

One generator (`code/data-gen/generate.py`, seeded, deterministic) writes raw CSVs + documents to
volumes, and a setup job materializes bronze/silver/gold. Every number below is a planted fact a
demo depends on, so the generator asserts them.

### Entities

| Entity | Rows | Notes |
|---|---|---|
| regions | 3 | Southeast (US), Northeast (US), Western Europe |
| properties | **10 raw → 8 clean** | ids 1–10 (INT, so `property_id = 1` works in Demo 14). 3 types: Office / Multifamily / Retail |
| tenants | ~40 | tenant_name, industry, credit_rating (AAA…B), contact_email (for governance) |
| leases | ~50 | lease_start, lease_end, monthly_rent, lease_status (Active / Expired / Pending Renewal). Ends are **relative to the generation date**: ~6 ≤ 90d, ~8 ≤ 180d, ~10 ≤ 365d, 4 already expired |
| gl_accounts | ~15 | category: Revenue / OpEx / MgmtFee / CapEx / Intercompany |
| gl_transactions | ~6–8k | monthly, 2024-01 … 2026-06, per property × account |
| quarterly_targets | 80 | net_profit_target, revenue_target per property × quarter |

### Gold: `gold_property_quarterly` (main fact)

Grain property × fiscal_quarter; **8 properties × 10 quarters (2024-Q1 … 2026-Q2) = 80 rows**.
Columns: property_id, property_name, property_type, region_name, market, fiscal_quarter
(`'2026-Q2'`), fiscal_quarter_date (DATE, quarter start), revenue, operating_expense, mgmt_fee,
capex, intercompany, net_profit (Finance: revenue − opex − mgmt_fee), net_profit_target,
revenue_target, met_target, prior_quarter_net_profit, qoq_change_pct.

Also `customer_performance` (property × tenant × quarter, ~400 rows) for continuity with the Oct 5
workshop and the Knowledge Assistant / governance demos.

### Planted facts (each is asserted by the generator and checked by tests)

| # | Fact | Used in |
|---|---|---|
| F1 | 2026-Q2: exactly 3 properties miss net_profit_target (incl. Harbor Tower) | D2, D7, D8 |
| F2 | Southeast net profit falls Q1→Q2 2026 (~−18%), driven by Harbor Tower: HVAC replacement booked as R&M OpEx (~€310k) + an anchor tenant lease that expired | D2, D8 "Explain with Genie", D5 |
| F3 | One market (Luxembourg City, Western Europe) has the highest QoQ net-profit growth | D2 Q4 |
| F4 | Finance vs Asset-Mgmt net profit differ (AM subtracts capex) — portfolio gap ~10–15% | D7 |
| F5 | bronze_properties: 10 rows; ids 9,10 have NULL region_id (filtered in silver); id 10's name duplicates "Harbor Tower" (id 3); 3 rows have raw market spellings ("Lux-Ville", "NYC", "Miami Bch") ≠ silver ("Luxembourg City", "New York", "Miami Beach") | D6 |
| F6 | Revenue is trending with seasonality, so ai_forecast gives sensible 2026-Q3/Q4; ≥2 properties are projected to miss 2026-Q3 revenue_target | D14 |
| F7 | Invoice HV-2026-0417 (Harbor Tower HVAC, €312,400) exceeds the €50k approval threshold and is CapEx under policy | D4, D5, D12 |

### Documents (synthetic, generated as PDFs)

- `documents/invoices/` — 8 invoices, varied vendors, layouts, currencies (EUR ×5, USD ×2, GBP ×1),
  1–9 line items: maintenance, utilities, insurance, property tax, HVAC (F7), cleaning, security, legal.
- `documents/policies/` — 4 PDFs: Expense Approval Policy (thresholds incl. €50k → CFO + Asset
  Mgmt Director), Capital Expenditure Guidelines (HVAC replacement > €25k and > 3y life = CapEx),
  Lease Renewal Procedures (180/90/30-day steps), Intercompany Transfer Policy.
- `documents/leases/` — 3 sample lease agreements (light, for D1 "any data type").
- `raw/` — the CSVs Demo 11 ingests (same data as bronze, so the participant pipeline reproduces gold).
- `code/sql/snowflake_property_view.sql` — broken Snowflake view for D3 (NVL, DATEADD, QUALIFY,
  missing join condition → row duplication; expected corrected row count documented).

### Deviations from the agenda (record in decisions.md, tell user)

1. Single schema with `bronze_` / `silver_` / `gold_` / `mv_` prefixes instead of `revantage.bronze.*`
   (no CREATE CATALOG on this metastore; user chose single schema).
2. Gold has 80 rows (8 × 10 quarters), not ~200: the agenda's "~8 properties" and "10 vs 8" (D6) win.
3. Gold ends at 2026-Q2 (Q3 close "in progress" as of October). D14 forecasts Q3/Q4 from 10 quarters
   as specified; D16 inserts the bad 2026-Q3 row, so it's a real "new load broke things" story.
4. `served_entities` is `system.serving.served_entities`, not `system.ai_gateway`. The system tables
   span the shared FEVM metastore, so every D13 query filters to this workspace (no other users' data on screen).

## 2. Build plan per demo

Legend: **Start** = pre-provisioned; **Ref** = pre-built answer key; **Prompts** = Genie Code / Genie
prompt library entries (`code/prompts/dNN-*.md`), each stage → prompt → expected → if stuck.

| D | Start (bundle) | Ref (bundle, pre-built and verified) | Owner |
|---|---|---|---|
| 1 | schema, tables, volumes, docs | — (click-path only) | data-engineer |
| 2 | gold + Genie Agent "(Reference)" with instructions/examples | Genie answers to 5 questions verified vs F1–F3 | data-engineer |
| 3 | broken SQL file in workspace | `ref_d03_property_view` (fixed view + YoY) and expected row count | data-engineer |
| 4 | invoices volume | Agent Bricks Information Extraction agent "Invoice Extractor (Reference)" + `ref_invoices_extracted` via generated SQL | data-engineer |
| 5 | policies volume | Knowledge Assistant "Revantage Policy Assistant (Reference)"; 3 questions verified with citations | data-engineer |
| 6 | bronze_properties with F5 issues | `ref_d06_quality_checks` notebook (the 5 checks) | data-engineer |
| 7 | gold with opex/mgmt_fee/capex/intercompany | `mv_net_profit_margin`, `mv_target_attainment`, `mv_qoq_revenue_growth` (ref) | data-engineer |
| 8 | metric views | Dashboard "Revantage Portfolio Review (Reference)", 3 pages + filters, Genie enabled | data-engineer |
| 9 | silver_leases/tenants/properties | App `revantage-lease-tracker` (filters, sortable table, cards, CSV export) + Playwright | app-builder |
| 10 | gold without descriptions (participants add them) | `ref` comments/tags applied script (toggle), grants to consumer group | data-engineer |
| 11 | raw CSVs volume | Lakeflow pipeline `ref_property_pipeline` (Auto Loader → silver → gold, expectations); a seeded bad row to fail an expectation for stage 7 | data-engineer |
| 12 | Lakebase project `revantage-lux-ops` + `invoice_approvals` seeded 5 Pending | App `revantage-invoice-approvals` (approve/reject → Lakebase) + job loading approved → `silver_invoices` with retries + failure alert | app-builder + data-engineer |
| 13 | AI Gateway on a pay-per-token endpoint, some generated traffic | `ref_d13_*` queries + SQL alert (daily tokens > 1M) | data-engineer |
| 14 | gold with fiscal_quarter_date | `ref_d14_revenue_forecast` table + dashboard page with forecast + CI | data-engineer |
| 15 | everything above | track cards (A analyst / B dashboard / C engineer), no new assets | deliverables-author |
| 16 | `code/sql/d16_seed_bad_row.sql` + `d16_reset.sql` | data-profiling monitor on gold, anomaly/freshness, SQL alert (3σ revenue) | data-engineer |

## 3. Steps

| Step | What | Owner | Depends | Group |
|---|---|---|---|---|
| S1 | Data generator + planted-fact assertions; docs PDFs; broken SQL | data-engineer | — | G1 |
| S2 | Setup job: volumes, raw → bronze/silver/gold, comments, grants | data-engineer | S1 | G1 |
| S3 | Ref: metric views, Genie Agent, dashboard, forecast, quality notebook, D3 view | data-engineer | S2 | G2 |
| S4 | Ref: Agent Bricks extraction + Knowledge Assistant (UI/API, captured in RUNBOOK) | data-engineer | S2 | G2 |
| S5 | Ref: Lakeflow pipeline + job + expectation failure fixture | data-engineer | S2 | G2 |
| S6 | Lease tracker app | app-builder | S2 | G2 |
| S7 | Lakebase + approvals app + approved→silver job | app-builder | S2, S4 | G3 |
| S8 | AI Gateway traffic + D13 queries + alerts; D16 monitor + alert | data-engineer | S3 | G3 |
| S9 | Prompt library `code/prompts/d01…d16.md`, each prompt **run live** in Genie Code / Genie and expected results recorded | orchestrator + data-engineer | S3–S8 | G4 |
| S10 | README / RUNBOOK / smoke test (planted facts + every ref asset) | deployer | S3–S8 | G4 |
| S12 | Pre-flight readiness script + `revantage` bundle target + participant sandbox option | deployer | S2 | G3 |
| S11 | Deliverables: build-along click-path (per demo: goal, time box, prompts, checkpoints, if-stuck), participant handout, internal deck, client deck (build-along structure), architecture, hero | deliverables-author | S9 | G5 |

## 4. Expectations / done checks

- Every planted fact F1–F7 holds in gold (SQL assertions in the smoke test).
- Every prompt in the library was run once in the live product and its expected result recorded;
  prompts that don't work reliably are rewritten or marked "facilitator demo only".
- Every Ref asset deploys from the bundle (or a documented, tested script where no bundle resource exists).
- Both apps: `npm run build` + Playwright pass locally and against the deployed app.

## 5. Delivery target (user answers 2026-10-08)

- **Dates:** day 1 = 2026-10-13 (user). Note: that's a Tuesday; agenda says Wed/Thu. Data anchor
  `--as-of 2026-10-13`; regenerate the day before if dates move.
- **Participants build in the Revantage dev workspace**, not this FEVM. So:
  - Everything is pre-built and verified here first (FEVM `dev` target).
  - Ship a portable kit: bundle target `revantage` (profile/catalog/schema/warehouse as variables),
    `setup_starting_state` job that lays down data + documents only, and an optional
    `participants` variable that creates one sandbox schema per participant with the starting
    data cloned in. Reference solutions deploy separately (`ref` resources, opt-in), so the
    facilitator can choose whether answer keys exist in the client workspace.
  - Prompts, SQL, and docs: no FEVM names; `${catalog}.${schema}` placeholders.
  - Feature-readiness checklist for their workspace (cloud/region, Agent Bricks Information
    Extraction + Knowledge Assistant, Lakebase, Genie One/Code, Apps, AI Gateway, system-table
    grants for D13, serverless) → `assets/` handout + pre-flight script `code/preflight/`.
  - S12 (new): pre-flight script that checks each feature via API and reports go/no-go per demo.
