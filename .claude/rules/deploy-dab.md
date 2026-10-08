---
paths:
  - "code/databricks.yml"
  - "code/resources/**"
  - "RUNBOOK.md"
---

# Deploy & test with the bundle

The whole demo deploys from the Declarative Automation Bundle at `code/databricks.yml`. Nothing is
created by undocumented clicking, so the demo can be rebuilt in another workspace by editing one file.

## One source of environment config

`code/databricks.yml` holds every environment-specific value (profile, catalog, schema, warehouse,
workspace paths, app name) as bundle variables with per-target values. Resource files under
`code/resources/` reference `${var.*}` and never hardcode a workspace, catalog, or path. If porting
ever needs an edit outside `databricks.yml`, move that value into a variable.

When you change the profile, catalog, schema, or paths, update `databricks.yml`, the table in
`CLAUDE.md`, and `.claude/hooks/scope.json` together.

## Declare resources natively

Bundles cover nearly everything a demo needs. Define each as a resource under `code/resources/`:

| Need | Resource key |
|------|--------------|
| Schema, volumes | `schemas`, `volumes` |
| Data loads, setup, grants | `jobs` (serverless tasks) |
| Streaming/batch ETL | `pipelines` (Lakeflow Spark Declarative Pipelines) |
| AI/BI dashboards | `dashboards` (`file_path: ../dashboards/x.lvdash.json`, `parent_path: ${var.dashboard_path}`) |
| Genie spaces | `genie_spaces` (`parent_path: ${var.genie_space_path}`, `warehouse_id`, `file_path`) |
| SQL alerts | `alerts` (`parent_path: ${var.alerts_path}`) |
| App | `apps` (see `code/resources/app.yml`) |
| Lakebase Postgres | `postgres_projects`, `postgres_branches`, `postgres_databases`, `postgres_synced_tables` |
| ML / GenAI | `experiments` (`name: ${var.experiment_path}/…`), `registered_models`, `model_serving_endpoints`, `vector_search_endpoints`, `vector_search_indexes` |

Run `databricks bundle schema` to see every field. The Databricks agent skills (`databricks-dabs`,
`databricks-apps`, `databricks-aibi-dashboards`, `databricks-pipelines`, `databricks-lakebase`, …)
have worked examples.

For dashboards, Genie spaces, and alerts, it is often fastest to author the object in the UI, then
pull its definition into the bundle and bind the live object to it:

```bash
cd code
databricks bundle generate dashboard --existing-id <id> -t dev        # also: genie-space, alert, app, job, pipeline
databricks bundle deployment bind <resource_key> <id> -t dev
```

Use a scripted fallback (`code/scripts/*.sh`, reading the same variables) only for something a
bundle genuinely can't declare. Document it as an ordered step in RUNBOOK.md, with its teardown.

## Incremental loop

```bash
cd code
databricks bundle validate -t dev     # config errors
databricks bundle plan -t dev         # what will change
databricks bundle deploy -t dev       # pushes only what changed
databricks bundle run <key> -t dev    # run/test only the affected job, pipeline, or app
```

Then rerun only the tests for the changed piece. Run a full clean deploy plus smoke test at least
once before the demo is called done, and again after any change to the deploy graph.

## Teardown

`databricks bundle destroy -t dev` removes everything the bundle manages; any scripted fallback
has a matching teardown in `RUNBOOK.md > Teardown`. The environment should end up as it was found.
