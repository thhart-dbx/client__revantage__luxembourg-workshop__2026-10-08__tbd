# Runbook — client__revantage__luxembourg-workshop__2026-10-08__tbd

> Reproduce the Revantage Luxembourg build-along workshop (16 demos) from scratch in any Databricks
> workspace. Everything environment-specific is a bundle variable in `code/databricks.yml`; porting =
> fill in a target (the `revantage` target is pre-staged) + the steps below. Each step lists how to
> verify it. Steps that the bundle can't declare (Agent Bricks agents, AI Gateway config, Lakebase DDL)
> are scripted or listed as exact clicks.

## 1. Prerequisites

- **Workspace:** AWS or Azure; Unity Catalog; serverless SQL warehouse and serverless jobs/pipelines; Databricks Apps; Lakebase; Agent Bricks (Information Extraction, Knowledge Assistant); Genie (One + Code); AI/BI dashboards; data profiling.
- **Facilitator permissions:** `USE CATALOG` + `CREATE SCHEMA` on the target catalog; create apps, jobs, pipelines, Lakebase instances, alerts; `CAN_MANAGE` on one pay-per-token endpoint (AI Gateway config); grant `USE CATALOG` to app service principals.
- **Admin grants for participants (Demo 13):** `SELECT` on `system.ai_gateway`, `system.serving`, `system.billing`, `system.access` (lineage).
- **Tooling:** Databricks CLI ≥ 0.27x, `uv`, Node ≥ 20 + npm (cloud npm proxy locally), Chrome for UI steps.
- **Pre-flight (read-only):** `code/data-gen/.venv/bin/python code/preflight/preflight.py --profile <p> --warehouse <id> --catalog <catalog>` → go/no-go per demo. FEVM result 2026-10-08: all 16 GO.

## 2. Configuration (`code/databricks.yml`)

| Variable | dev (FEVM) | Revantage (`revantage` target) |
|---|---|---|
| profile (target) | `fevm-thhart-october-2026` | `revantage-dev` (TODO: `databricks auth login`) |
| `catalog` | `thhart_october_2026_catalog` | TODO |
| `schema` | `revantage_20261008` | `databricks_workshop` |
| `warehouse_id` | `0fb3aaac7c7d373c` | TODO |
| `workspace_id` | `7474657569423450` | TODO (`?o=` in the URL) |
| `as_of` | `2026-10-13` (default) | workshop day 1; lease windows are relative to it |
| `*_path` | `/Users/<you>/{experiments,spaces,dashboards,alerts}` | same pattern |
| `app_name` / `approvals_app_name` | `revantage-lease-tracker` / `revantage-invoice-approvals` | unique per workspace |
| `consumer_group` | `revantage_consumers` | the participants' group |

The `revantage` target also creates the Demo 16 data-profiling monitor (the FEVM metastore is at its 1,000-monitor limit).

## 3. Steps (in order)

### Step 1 — Deploy the bundle
```bash
cd code
databricks workspace mkdirs /Users/<you>/alerts -p <p>     # alerts need an existing folder
databricks bundle validate -t <target> && databricks bundle deploy -t <target>
```
Creates: schema + volumes `raw`, `documents`; jobs `setup_starting_state`, `setup_participant_sandboxes`, `ref_analytics`, `d12_approved_to_silver`; pipeline `ref_property_pipeline`; Genie Agents (Start, Reference); dashboard; alerts (2); apps (2); Lakebase instance `revantage-lux-ops` + synced table.
**Verify:** `databricks bundle summary -t <target>`; Lakebase instance `AVAILABLE` (`databricks database get-database-instance revantage-lux-ops`).

### Step 2 — Starting state
```bash
databricks bundle run setup_starting_state -t <target>
code/data-gen/.venv/bin/python code/tests/check_starting_state.py --profile <p> --warehouse <id> --catalog <c> --schema <s>
```
**Verify:** 28/28 PASS (gold = oracle; planted facts F1–F7; 15 documents).
Optional: `databricks bundle run setup_participant_sandboxes -t <target> --params participants=a@x.com,b@x.com,group=<group>`.

### Step 3 — Reference answer keys
```bash
databricks bundle run ref_analytics -t <target>             # D3 view, D6 checks, D7 metric views, D14 forecast
databricks bundle run ref_property_pipeline -t <target>     # D11 pipeline (ref_d11_*)
code/data-gen/.venv/bin/python code/tests/check_ref_pipeline.py --profile <p> --warehouse <id> --catalog <c> --schema <s>
```
**Verify:** job SUCCESS; pipeline gold = oracle (80 rows); expectations: 3 bad periods + 2 regionless properties dropped.

### Step 4 — Apps (both)
```bash
for app in <app_name> <approvals_app_name>; do
  SP=$(databricks apps get $app -o json | python3 -c "import sys,json;print(json.load(sys.stdin)['service_principal_client_id'])")
  databricks grants update catalog <catalog> --json "{\"changes\":[{\"principal\":\"$SP\",\"add\":[\"USE_CATALOG\"]}]}"
done
L(){ uv run -q --with "psycopg[binary]" code/lakebase/lakebase_sql.py --profile <p> --instance revantage-lux-ops --db revantage_ops "$@"; }
L -f code/lakebase/d12_invoice_approvals.sql && L -f code/lakebase/d12_reset.sql
SP=<approvals app service_principal_client_id>; sed "s/\${app_sp}/$SP/g" code/lakebase/d12_grant_app.sql > /tmp/g.sql && L -f /tmp/g.sql
databricks bundle run demo_app -t <target> && databricks bundle run approvals_app -t <target>
```
**Verify:** lease tracker shows the 90/180/365 windows (FEVM 2026-10-08: 6/14/23); approvals app lists 5 Pending, HV-2026-0417 "Requires 2 Approvals". Local: `cd code/app && npx playwright test` (27 pass), `cd code/app-approvals && npx playwright test --project=desktop` (5 pass).

### Step 5 — UI-only builds (Agent Bricks), ~45 min incl. indexing
1. **Invoice Extractor (D4):** Agents → Create Agent → Information Extraction → Select volume → All volumes → `documents` → expand (wait for the folder list) → `invoices` → Select. Paste the description from `code/prompts/d04-extraction-agent.md` → Generate schema → change `line_items.quantity` to **Number** → Run extraction. Then run `code/reference/d04_extract_invoices.sql` (CTAS) and `code/reference/d04_score_extraction.py` → **72/72**.
2. **Policy Assistant (D5):** Agents → Create Agent → Knowledge Assistant, name `revantage-policy-assistant`, source `documents/policies/` (text in `code/prompts/d05-knowledge-assistant.md`). Wait **~25 min** for the index; then `code/tests/ask_ka.py --endpoint <ka-…-endpoint> "<question>"`: all 6 ground-truth questions answered with citations.
List agents: `databricks api get /api/2.0/tiles`.

### Step 6 — AI Gateway (D13)
`BUNDLE_TARGET=<target> DATABRICKS_CONFIG_PROFILE=<p> code/ai-gateway/apply_ai_gateway.sh` (saves the endpoint's original config, enables usage tracking + inference table `ref_d13_*`). Send some traffic (e.g. 40 `ai_query` calls). Usage rows appear in `system.ai_gateway.usage` with a delay.
**Verify:** the 5 queries in `code/reference/d13_ai_gateway_queries.sql` return rows (`:workspace_id` = workspace ID).

### Step 7 — Genie accuracy ladder (D17)
Starting state comes with Step 2 (`setup/sql/05_d17_legacy.sql`); the reference tables with Step 3 (`reference/d17_business_layer.sql` in `ref_analytics`); the agents *Revantage Accuracy Lab (Start/Reference)* with Step 1.
Re-measure the ladder (fresh agent per rung, results in `ref_d17_benchmark_results`, scratch agents deleted):
```bash
code/data-gen/.venv/bin/python code/genie/d17_ladder.py --profile <p> --warehouse <id> --catalog <c> --schema <s> --parent <genie_space_path> --runs 2
```
**Verify:** R1 ≈ 5 % … R4 ≈ 50 %, R5–R7 ≥ 90 %; `code/tests/score_genie.py --space <Start id> --rung start` ≈ 0–2/10, `--space <Reference id> --rung ref` 10/10.

### Step 8 — Domain and Pages (D18)
```bash
code/scripts/d18_domain.sh <p>     # governed tag + domain "Revantage Workshop" (needs MANAGE DISCOVER)
```
Then in the UI: Discover → Revantage Workshop → **Publish**; ⋮ → Manage Domains → Permissions → MANAGE for the participants' group; **Add to domain**: `ref_mv_*`, `gold_property_quarterly`; create and **Publish** the four Pages in `code/reference/d18_pages.md` (Create page → Genie Code, prompt in the D18 guide).
**Verify:** Genie One "What is our NOI this quarter?" → thought process reads the Page; €6,375,345.36 for 2026-Q2. Not yet run end to end (FEVM account at its governed-tag limit): do it in the Revantage pre-flight.

## 4. Smoke test
- [ ] `check_starting_state.py` 28/28 · `check_ref_pipeline.py` OK
- [ ] Genie: `code/tests/ask_genie.py --space <Start id> "Which properties missed their quarterly target in 2026-Q2?"` → Peachtree Center, Harbor Tower, Zuidas Residences
- [ ] Dashboard renders 4 pages; KPI counters €10.7M · 59.3% · 62.5% · −3.3%
- [ ] `SELECT MEASURE(target_attainment) FROM <c>.<s>.ref_mv_target_attainment WHERE fiscal_quarter='2026-Q2'` → 0.625
- [ ] D16: `code/reference/d16_revenue_outliers.sql` (`${table}`=gold) → 0 rows
- [ ] Both apps load; approvals queue has 5 Pending
- [ ] D17: `score_genie.py` Start ≤ 2/10, Reference 10/10
- [ ] D18: Genie One reads the Net profit Page (Step 8)

## 5. Workshop-day resets (run before each session that mutates state)
| After | Run |
|---|---|
| D10 | `code/reference/d10_reset.sql` |
| D11 | `code/scripts/d11_bad_batch.sh remove <p> <c> <s>`, then `databricks bundle run ref_property_pipeline --full-refresh-all` |
| D12 | `L -f code/lakebase/d12_reset.sql` and `TRUNCATE TABLE <c>.<s>.silver_invoices` |
| D16 | `code/sql/d16_reset.sql` (`${table}` = `gold_property_quarterly`) |
Rerun `setup_starting_state` the day before if the date moves (lease windows) and re-check.

## 6. Teardown
```bash
code/ai-gateway/apply_ai_gateway.sh --teardown            # restores the endpoint's original AI Gateway config
# delete the two Agent Bricks agents (Agents → ⋮ → Delete): their vector-search endpoints bill while idle
for app in <app_name> <approvals_app_name>; do  # revoke the one-time catalog grants
  SP=$(databricks apps get $app -o json | python3 -c "import sys,json;print(json.load(sys.stdin)['service_principal_client_id'])")
  databricks grants update catalog <catalog> --json "{\"changes\":[{\"principal\":\"$SP\",\"remove\":[\"USE_CATALOG\"]}]}"
done
code/scripts/d18_domain.sh <p> --teardown                # domain + governed tag (delete the Pages first: Discover → Pages → ⋮ → Delete)
databricks bundle destroy -t <target>                     # apps, schema (all tables), Genie, dashboard, alerts, jobs, pipeline, Lakebase
```
**Verify:** schema gone, apps deleted, `databricks api get /api/2.0/tiles` no longer lists the two agents.

## 7. Known gotchas (all found during the FEVM pre-build)
| Gotcha | Symptom | Fix |
|---|---|---|
| `ai_forecast` on job compute | `UNSUPPORTED_FEATURE.AI_FUNCTION_PREVIEW` | run on a SQL warehouse (`setup/run_sql.py --warehouse`) |
| `ai_forecast` frequency | `'Q'` / `'3M'` fail on DATE | `frequency => 'QS'`, `horizon => '<end date>'` |
| `current_workspace_id()` | doesn't exist | filter system tables with `:workspace_id` / `${var.workspace_id}` |
| CSV decimals | `"980,40"` read as 98040.00, silently | keep amounts as STRING in bronze; `try_cast` + `FAIL UPDATE` expectation |
| Pipeline retries | production mode retries failed updates ~5× | expect several failed runs; full refresh after removing bad files |
| Governed tags | `UC_TAG_POLICY_VALUE_NOT_ALLOWED` for `data_owner` | use `system.certification_status` and `class.*` tags, or values the policy allows |
| Volume picker | "Request access" on a folder you own | wait for the folder list to load, expand again |
| Extraction schema | generator types `quantity` as integer | change to Number (fractional hours) |
| Knowledge Assistant | "Vector index … is not ready" | ~25 min after create; start it early |
| UC rate limits (shared metastore) | `REQUEST_LIMIT_EXCEEDED` from Genie/Agent Bricks | retry |
| Data profiling | "exceeds the number of limit 1000" on the FEVM | monitor only in the `revantage` target |
| Bundle deploy hangs | a create can't succeed (monitor limit) and the lock goes stale | fix the resource; `--force-lock` only once you're sure nothing else is deploying |
| Alerts | `Tree node … alerts does not exist` | `databricks workspace mkdirs` the alerts folder |
| Apps + Lakebase | Postgres permission denied | grant the app SP's role on schema `approvals` (`d12_grant_app.sql`) |
| Serverless env 4 SDK | `WorkspaceClient has no attribute database` | call `/api/2.0/database/...` via `w.api_client.do` |
| Spark from Python rows | `CANNOT_DETERMINE_TYPE` with NULL columns | pass an explicit schema |
| `NUMBER`, `DIV0`, `TO_VARCHAR(fmt)`, `SYSDATE` | fail on Databricks (NVL/IFF/DATEADD/QUALIFY/`::` work) | D3's teaching point |
| npm / PyPI locally | dev proxies miss versions; pip TLS fails | npm cloud proxy; `uv --index-url https://pypi-proxy.cloud.databricks.com/simple` |
| App lockfile | `TAR_BAD_ARCHIVE` on deploy | rewrite npm-proxy URLs to registry.npmjs.org |
