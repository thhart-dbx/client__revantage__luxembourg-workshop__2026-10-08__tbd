# client__revantage__luxembourg-workshop__2026-10-08__tbd

Revantage Luxembourg two-day onsite workshop: Genie One/Code, Agent Bricks, metric views, AI/BI, Apps, Lakeflow, Lakebase, AI Gateway, ai_forecast, data quality

## Environment

| Setting | Value |
|---------|-------|
| Workspace profile | `fevm-thhart-october-2026` (https://fevm-thhart-october-2026.cloud.databricks.com) |
| Data | `thhart_october_2026_catalog.revantage_20261008` |
| SQL warehouse | `0fb3aaac7c7d373c` |
| Git folder | `/Users/thomas.hart@databricks.com/client__revantage__luxembourg-workshop__2026-10-08__tbd` |
| Bundle root | `/Users/thomas.hart@databricks.com/.bundle/client__revantage__luxembourg_workshop__2026_10_08__tbd` |
| MLflow experiments | `/Users/thomas.hart@databricks.com/experiments` |
| Genie spaces | `/Users/thomas.hart@databricks.com/spaces` |
| AI/BI dashboards | `/Users/thomas.hart@databricks.com/dashboards` |
| SQL alerts | `/Users/thomas.hart@databricks.com/alerts` |
| Apps | `revantage-lease-tracker` (`code/app`, Demo 9), `revantage-invoice-approvals` (`code/app-approvals`, Demo 12) |

The same values live in `code/databricks.yml` (deployment) and `.claude/hooks/scope.json` (scope
guard). Change all three together.

## Workshop model: build live

This is a hands-on, two-day onsite (Revantage Luxembourg). Participants build each asset themselves
on their laptops, guided by Genie Code. So every demo has two layers:

- **Starting state** (pre-provisioned by the bundle): data, documents, the broken Snowflake SQL, and
  anything a participant needs *before* they start building. It must be in place and correct on
  the morning of the workshop.
- **Reference solution** (answer key, names prefixed `ref_` / titled "(Reference)"): the finished
  asset, deployed by the bundle, used as a fallback when a live build stalls and as the source of
  truth for expected results.

Decks and the click-path are build-along guides: exact prompts to type, the expected result at
each checkpoint, an "if you're stuck" recovery to the reference, and a time box. They aren't product
tours. Testing covers the live path too: run the documented Genie Code / Genie prompts and confirm
they produce the expected result, not just that the reference asset exists.

## Scope

This demo shares a workspace with other work, so everything it does stays inside its own footprint:

- **Local files**: only inside this project directory.
- **Data**: create, read, and write only in `thhart_october_2026_catalog.revantage_20261008`. Don't read other catalogs
  either (copy any sample data in with a setup job), so the demo ports cleanly to a customer workspace.
  **Exception:** Demo 13 (AI Gateway & Monitoring) reads `system.ai_gateway.*` and `system.billing.*`
  by design. Read-only, and only those schemas.
- **Workspace objects**: only under the paths in the table above.
- **Account objects (Demo 18, approved 2026-10-09)**: one governed tag `Revantage Workshop` and its
  Domain "Revantage Workshop" (Discover), plus the Pages inside that domain. Nothing else at account
  level: don't edit other tag policies or domains. Remove them in `RUNBOOK.md > Teardown`.

`.claude/hooks/guard_scope.py` blocks `databricks` CLI calls that use another profile, touch
workspace paths outside the table, or name another catalog. `.claude/settings.json` asks before
destructive commands. The hook can't see SQL inside notebooks, pipeline code, or the app, so check
those yourself.

## Layout

```
CLAUDE.md  README.md  RUNBOOK.md   # the only files at the root
.claude/   settings.json, hooks/, rules/, agents/
code/      everything that builds the demo
  databricks.yml  resources/        # the bundle; single source of env config
  app/                              # Lease Expiry Tracker app (Demo 9); Playwright specs in app/e2e/
  app-approvals/                    # Invoice Approvals app on Lakebase (Demo 12); same conventions
  # notebooks, sql, pipelines, dashboards, scripts …
assets/    the five deliverables only
notes/     user-requests.md, claude-notes/ (plan, progress), agent-notes/ (decisions,
           dead-ends, errors, architecture.mmd), agent-comms/thread.md, user-notes/
```

If you're unsure where a file goes, it almost certainly belongs in `code/`.

## Stack

- **Deploy**: Declarative Automation Bundle at `code/databricks.yml`. Details are in `.claude/rules/deploy-dab.md`.
- **Data**: Unity Catalog managed tables; Lakeflow Spark Declarative Pipelines and Lakeflow Jobs on
  serverless; UC metric views for shared business metrics.
- **Analytics**: AI/BI dashboards, Genie spaces, SQL alerts, all as bundle resources. Don't use legacy
  dashboards or legacy alerts.
- **App**: Next.js (App Router, TypeScript, shadcn/ui) on Databricks Apps, with Lakebase Postgres for
  app writes and Playwright for e2e tests. Details are in `.claude/rules/app-nextjs.md`.
- **Product guidance**: use the Databricks agent skills (`databricks-dabs`, `databricks-apps`,
  `databricks-pipelines`, `databricks-aibi-dashboards`, `databricks-lakebase`, …) rather than guessing
  APIs. Install them with `databricks aitools install --agents claude-code` if they're missing.

## How work runs

1. **On session start**, read `notes/claude-notes/progress.md`, then `plan.md`, and resume from there.
   If neither exists, this is a fresh start. Format and resume rules are in `.claude/rules/workflow.md`.
2. **Plan before building.** `plan.md` lists the CUJs, a step table (owner, dependencies, parallel group),
   and expectations for each asset.
3. **Delegate to the subagents** in `.claude/agents/` (data-engineer, app-builder, deployer,
   deliverables-author). Launch independent steps in parallel.
4. **Keep `progress.md` current** at every step transition.
5. **Log**: user requests go in `notes/user-requests.md`; decisions, dead ends, and errors go in
   `notes/agent-notes/`.

## Before each commit

Every user request ends in a commit once these hold for what changed:

1. `databricks bundle validate` passes, and the changed resources are deployed and run successfully
   in the workspace (`bundle deploy` + `bundle run <key>`).
2. If the app changed, `npm run build` and `npx playwright test` pass in `code/app` locally *and*
   against the pushed app, and `package-lock.json` has no `npm-proxy` URLs (`.claude/rules/app-nextjs.md`).
3. `README.md > Assets Created` matches what exists in the workspace.
4. `RUNBOOK.md` reproduces the current state from scratch, with tested steps and no hardcoded
   environment values.
5. Commit, then record the short hash next to the request in `notes/user-requests.md`.

## Done

The demo is complete only when a clean deploy from scratch passes the RUNBOOK smoke test **and** all
five deliverables are in `assets/`: click-path walkthrough, internal deck, client deck, architecture
diagram, and README hero shot. See `.claude/rules/deliverables.md`.
