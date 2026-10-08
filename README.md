# client__revantage__luxembourg-workshop__2026-10-08__tbd

Revantage Luxembourg two-day onsite workshop: Genie One/Code, Agent Bricks, metric views, AI/BI, Apps, Lakeflow, Lakebase, AI Gateway, ai_forecast, data quality

<!-- HERO SCREENSHOT — MANDATORY. A screenshot of the most visually stunning element of the
     demo, captured live from the deployed asset. Subject preference (use the first that exists):
     (1) the app, (2) a Genie space, (3) a dashboard, (4) a notebook. Store the image in assets/. -->
![client__revantage__luxembourg-workshop__2026-10-08__tbd](assets/hero.png)

## Setup

Deploy the whole demo from the Declarative Automation Bundle. Porting to a new environment means
editing `code/databricks.yml` (bundle variables/targets) — nothing else.

```bash
databricks auth profiles                 # confirm your profile
cd code
databricks bundle validate -t <target>
databricks bundle deploy -t <target>     # schema, jobs, pipelines, dashboards, Genie, alerts, app
databricks bundle run demo_app -t <target>
```

Full ordered steps, smoke test, and teardown are in [RUNBOOK.md](RUNBOOK.md).

### App local development

```bash
cd code/app
# .env.local: DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_WAREHOUSE_ID (see .claude/rules/app-nextjs.md)
npm ci                    # registry: https://npm-proxy.cloud.databricks.com/
npm run dev               # http://localhost:3000
npx playwright test       # click-path specs in code/app/e2e/
# then push: cd .. && databricks bundle deploy && databricks bundle run demo_app
```

## Databricks

- Workspace: `fevm-thhart-october-2026`
- Catalog: `thhart_october_2026_catalog`
- Schema: `revantage_20261008`
- App: `revantage-lease-tracker` (Next.js on Databricks Apps)

## Deliverables

Located in `assets/` (see `CLAUDE.md > Deliverables` for how each is produced):

| Deliverable | File | What it is |
|-------------|------|------------|
| Hero screenshot | `assets/hero.png` | The demo's most striking view (app › Genie › dashboard › notebook), embedded above |
| Click-path walkthrough | `assets/click-path.md` → `assets/click-path.docx` | Human step-by-step of the built demo, with screenshots |
| Internal enablement deck | `assets/<demo>-internal.pptx` | Per-scenario value prop + "Why Databricks?" for colleagues; live screenshots + architecture |
| External client deck | `assets/<demo>-client.pptx` | Customer narrative of how Databricks solves the issue; live screenshots as proof |
| Architecture diagram | `assets/architecture.png` | Every Databricks object created, linked together |

## Assets Created

All Databricks assets created by this demo. **This section must be kept up to date as assets are added or removed.**

### Data Assets

| Asset | Type | Location |
|-------|------|----------|
| _e.g. portfolio_companies_ | _table_ | _`thhart_october_2026_catalog.revantage_20261008.portfolio_companies`_ |

### Workspace Assets

| Asset | Type | Location |
|-------|------|----------|
| _e.g. Portfolio Dashboard_ | _AI/BI Dashboard_ | _`/Users/thomas.hart@databricks.com/dashboards/Portfolio Dashboard`_ |

Asset types include: AI/BI Dashboard, Genie Space, App, Lakebase Project/Database, Notebook, Lakeflow Job, Lakeflow Pipeline, MLflow Experiment, SQL Alert, Metric View, Model Serving Endpoint, Vector Search Index, Function (UDF), Volume, and any other Databricks resource.

## Cleanup

Remove everything the bundle manages, then run the documented fallback teardowns:

```bash
cd code
databricks bundle destroy -t <target>
# plus the teardown for any scripted fallback (see RUNBOOK.md > Teardown)
```
