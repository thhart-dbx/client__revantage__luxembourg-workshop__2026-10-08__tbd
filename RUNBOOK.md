# Runbook — client__revantage__luxembourg-workshop__2026-10-08__tbd

> **Purpose**: This runbook is the authoritative, step-by-step recipe to reproduce this
> demo from scratch in **any** Databricks environment. A new operator — human or Claude —
> who has never seen this project should be able to follow it top to bottom and end up
> with a fully working demo. Keep it current as the demo is built (it is a commit blocker —
> see CLAUDE.md). The demo deploys through a **Declarative Automation Bundle** (`code/databricks.yml`),
> which is the single source of environment config. Don't hardcode workspace-specific values into
> the steps; every such value is a bundle variable in `code/databricks.yml`. Porting to a new
> environment = add a target to that file + `databricks bundle deploy` + `bundle run`.

## 1. Prerequisites

What an operator must have BEFORE starting. Fill in exact versions/scopes as the demo grows.

- **Databricks workspace** — any workspace on cloud(s): _<AWS / Azure / GCP — note any restrictions>_
- **Permissions** — _<UC privileges: CREATE CATALOG/SCHEMA/TABLE/FUNCTION, USE CATALOG; workspace admin if needed; ability to create Apps/Genie/dashboards/jobs>_
- **Tooling** — Databricks CLI (`databricks -v` ≥ 1.18), `git`, `gh`, Node ≥ 20 + npm (Next.js app and Playwright), Python 3 _<if used>_
- **Workspace features** — Databricks Apps; serverless compute; Lakebase _<if used>_; user authorization for apps _<if the app uses `user_api_scopes`>_
- **Compute** — a SQL warehouse (serverless preferred) and/or serverless notebook compute
- **Source** — clone of this repo: `gh repo clone thhart-dbx/client__revantage__luxembourg-workshop__2026-10-08__tbd`

## 2. Configuration — all in `code/databricks.yml`

There is no separate config to maintain here: every environment-specific value is a **bundle
variable** in `code/databricks.yml`, and each target (`dev`, the customer env, etc.) overrides
them. To reproduce in a new environment, edit that file only — add/adjust a target and its
variables — then deploy. The variables below must exist in `databricks.yml`:

| Bundle variable | This demo's value | What to change it to in a new env |
|-----------------|-------------------|-----------------------------------|
| `profile` (target) | `fevm-thhart-october-2026` | your `databricks auth profiles` entry |
| `catalog` | `thhart_october_2026_catalog` | a catalog you can write to |
| `schema` | `revantage_20261008` | any schema name (created on deploy) |
| `warehouse_id` | `0fb3aaac7c7d373c` | a warehouse in the target workspace |
| `experiment_path` | `/Users/thomas.hart@databricks.com/experiments` | `/Users/<you>/experiments` |
| `genie_space_path` | `/Users/thomas.hart@databricks.com/spaces` | `/Users/<you>/spaces` |
| `dashboard_path` | `/Users/thomas.hart@databricks.com/dashboards` | `/Users/<you>/dashboards` |
| `alerts_path` | `/Users/thomas.hart@databricks.com/alerts` | `/Users/<you>/alerts` |
| `app_name` | `revantage-lease-tracker` | unique per workspace; lowercase, hyphens, ≤ 30 chars |
| _<other>_ | _<value>_ | _<guidance>_ |

```bash
# Point the CLI at the target and confirm the bundle resolves:
cd code
databricks bundle validate -t <target>     # <target> is defined in databricks.yml
```

## 3. Reproduction Steps — in order

Everything is created by the bundle: schema, jobs, pipelines, dashboards, Genie spaces, alerts,
the app, and Lakebase. A scripted fallback appears here only for something a bundle genuinely can't
declare. Keep the
order in sync with the dependency graph in `notes/claude-notes/plan.md` and the inventory in
`README.md`. Every asset in `README.md > Assets Created` must be produced by a step here.

### Step 1 — Deploy the bundle
- **Run**:
  ```bash
  cd code
  databricks bundle validate -t <target>
  databricks bundle plan -t <target>       # review what will be created
  databricks bundle deploy -t <target>     # schema, jobs, pipelines, dashboards, Genie, alerts, app, ...
  ```
- **Verify**: `databricks bundle summary -t <target>` lists the resources; no deploy errors.

### Step 2 — Run the setup jobs / pipelines (data → functions/models)
- **Run**: `databricks bundle run <resource> -t <target>` for each data-load / model / pipeline resource, in dependency order
- **Verify**: _<expected row counts / tables / functions present>_

### Step 3 — Grant the app access and start it
- **Run**:
  ```bash
  # One-time: the app's service principal needs USE CATALOG (schema grants come from the bundle)
  SP=$(databricks apps get <app_name> -o json | python3 -c "import sys,json;print(json.load(sys.stdin)['service_principal_client_id'])")
  databricks grants update catalog <catalog> --json "{\"changes\":[{\"principal\":\"$SP\",\"add\":[\"USE_CATALOG\"]}]}"
  databricks bundle run demo_app -t <target>       # deploys code/app (npm install → build → start)
  ```
- **Verify**: `databricks apps get <app_name>` shows the app as running; `databricks apps logs <app_name>` has no errors

### Step 4 — Verify the surfaces & app
- **Run**: open the dashboards, Genie space, and app URL (`databricks bundle summary -t <target>` or `databricks bundle open <key>`)
- **Verify**: _<dashboard renders with data; Genie answers a sample question; app loads and the primary CUJ works>_

_(Scripted fallbacks, only if any exist: `bash code/scripts/<name>.sh -t <target>`, which reads the same bundle variables.)_

_(Incremental changes: `databricks bundle deploy -t <target>` pushes only what changed; use
`databricks bundle run <resource> -t <target>` to re-test just the affected resource.)_

## 4. Smoke Test — prove the demo works

The minimum checks that confirm a fresh deployment is functional end-to-end.

- [ ] _<query returns expected result>_
- [ ] _<dashboard renders with data>_
- [ ] _<Genie answers a sample question>_
- [ ] _<app loads and the primary CUJ click-path succeeds>_

## 5. Teardown — remove everything

How to fully clean up so the environment is left as it was found.

- **Run**:
  ```bash
  cd code
  # Revoke the one-time catalog grant first (the bundle doesn't manage it, and the SP is deleted with the app)
  SP=$(databricks apps get <app_name> -o json | python3 -c "import sys,json;print(json.load(sys.stdin)['service_principal_client_id'])")
  databricks grants update catalog <catalog> --json "{\"changes\":[{\"principal\":\"$SP\",\"remove\":[\"USE_CATALOG\"]}]}"
  databricks bundle destroy -t <target>    # removes everything the bundle manages: app, schema (and all its tables), Genie spaces, ...
  # then the matching teardown for any scripted fallback
  ```
- **Verify**: _<schema/tables gone, app deleted, dashboards/Genie/jobs removed — nothing left behind>_

## 6. Known Gotchas

Environment-specific pitfalls and how to work around them (auth, grants, warehouse types,
serverless vs. classic, region/cloud differences, ordering constraints).

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| App service principal missing UC grants | App queries fail with `PERMISSION_DENIED` | Run the USE CATALOG grant (Step 3); schema grants are in `code/resources/schema.yml` |
| App crashes on start | `apps logs` shows a port or `EADDRINUSE` error | `package.json` start must be `next start -H 0.0.0.0 -p ${DATABRICKS_APP_PORT:-3000}` |
| Page shows stale or empty data | Data was fetched at build time | Mark data pages `export const dynamic = "force-dynamic"` |
| `NEXT_PUBLIC_*` value wrong after porting | It's inlined at build time | Keep env-specific values server-side, via `app.yaml` `valueFrom` |
| `bundle destroy` drops data you wanted | Destroying the schema deletes every table in it, bundle-managed or not | Export anything worth keeping before teardown |
| `next build` fails: `non-ecmascript placeable asset` in `@databricks/sql` / `lz4-napi` | Turbopack bundling the SQL driver's native modules | Keep `serverExternalPackages: ["@databricks/sql"]` in `code/app/next.config.ts` |
| Local `npm install` hangs or fails with `ETARGET` | npm is pointed at `npm-proxy.dev.databricks.com`, which keeps only ~100 recent versions per package | `npm config set registry https://npm-proxy.cloud.databricks.com/` |
| App deploy fails at "Installing packages" (`TAR_BAD_ARCHIVE`, `E404` on `npm-proxy…` URLs) | `package-lock.json` points at the internal proxy, which Databricks Apps can't reach | Rewrite the lockfile URLs to `registry.npmjs.org` (`.claude/rules/app-nextjs.md`) and redeploy |
| Local dev 401s | `DATABRICKS_TOKEN` in `.env.local` expired (~1 h) | Re-run `databricks auth token --profile <profile>` |
