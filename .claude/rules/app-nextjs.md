---
paths:
  - "code/app/**"
  - "code/app-approvals/**"
---

# App: Next.js on Databricks Apps

Any user-facing UI in this demo is one of the two Next.js apps, `code/app/` (lease tracker) and `code/app-approvals/` (invoice approvals); everything below applies to both: App Router, TypeScript,
Tailwind, and shadcn/ui components. Don't add Streamlit, Gradio, Dash, or hand-rolled HTML UIs; one
consistent stack keeps the demo deployable through the bundle and testable with Playwright.
`code/app/AGENTS.md` (from create-next-app) has version-specific Next.js guidance; read it before
writing Next.js code.

## Data access

- Call Databricks only from server code: Route Handlers (`src/app/api/**/route.ts`), Server
  Components, and Server Actions, through `src/lib/databricks.ts` (it imports `server-only`).
  Client components fetch from Route Handlers. Credentials must never reach the browser, and nothing
  secret goes in `NEXT_PUBLIC_*` (those values are inlined into the client bundle at build time).
- Use parameterized SQL (`query(sql, { name: value })` with `:name` markers). Don't interpolate user input.
- Fully qualify tables as `thhart_october_2026_catalog.revantage_20261008.<table>`, and only that schema.
- Auth: by default the app runs as its service principal (`DATABRICKS_CLIENT_ID/SECRET`, injected by
  Databricks Apps). To show per-user Unity Catalog permissions (row filters, masks), enable
  `user_api_scopes` in `code/resources/app.yml` and pass
  `(await headers()).get("x-forwarded-access-token")` as `query`'s third argument.
- The app's service principal gets `USE_SCHEMA` + `SELECT` from the `grants` block in
  `code/resources/schema.yml` (add `MODIFY` there if the app writes to Delta). `USE CATALOG` is a
  one-time grant documented in RUNBOOK Step 3.
- If the app writes transactional state (forms, approvals, carts), use Lakebase Postgres bound as an
  app resource (`postgres` in `app.yml`) via `pg`, not Delta tables through the warehouse.
- Mark pages that read live data `export const dynamic = "force-dynamic"`, so they aren't
  prerendered at build time (no credentials exist then).

## Runtime contract (Databricks Apps)

- On deploy, the platform runs `npm install`, then `npm run build`, then `app.yaml`'s command (`npm run start`).
- `package.json` `start` script: `next start -H 0.0.0.0 -p ${DATABRICKS_APP_PORT:-3000}`.
- `code/app/.gitignore` must exclude `node_modules/`, `.next/`, `.env*`, `test-results/`, and
  `playwright-report/`. The bundle uploads whatever isn't ignored.
- Keep `serverExternalPackages: ["@databricks/sql"]` in `next.config.ts`. Turbopack can't bundle the
  driver's native modules, and the build fails on deploy without it. Do the same for any other
  package with native bindings.
- Bound resources reach the app through `app.yaml` `env` + `valueFrom` (e.g. `DATABRICKS_WAREHOUSE_ID`).
  Add a resource in `app.yml` first, then reference it here.

## Dev loop: local first, then push

Build locally, where an edit shows up in about a second, and push to Databricks Apps to verify.
A push (`bundle deploy` + `bundle run demo_app`) takes about a minute.

1. **Local** (`npm run dev` + `npx playwright test`). Queries run as *you*, through your token.
2. **Push** before committing app changes: `cd code && databricks bundle deploy && databricks bundle run demo_app`,
   then run Playwright against the app URL (below). This is the only check of the platform build and
   of the app service principal's grants, which local dev never exercises.

### Dependencies and the lockfile

Commit `package-lock.json`, but only with `registry.npmjs.org` URLs. Databricks Apps can't reach the
internal npm proxy, so a lockfile pointing at it fails the deploy (`TAR_BAD_ARCHIVE`, `E404`). After
**every** `npm install` / `npx shadcn add` that touches the lockfile, run:

```bash
perl -pi -e 's#https://npm-proxy\.cloud\.databricks\.com/#https://registry.npmjs.org/#g' package-lock.json
grep -c npm-proxy package-lock.json   # must print 0
```

Locally npm still installs from the proxy (it rewrites `registry.npmjs.org` URLs to the configured
registry). The registry must be `https://npm-proxy.cloud.databricks.com/`; the `dev` proxy is
missing versions. Don't pin `@latest` from the cloud proxy, because its `latest` tag can point at a canary.

### Local setup

```bash
cd code/app
cat > .env.local <<EOF
DATABRICKS_HOST=https://fevm-thhart-october-2026.cloud.databricks.com
DATABRICKS_TOKEN=$(databricks auth token --profile fevm-thhart-october-2026 | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
DATABRICKS_WAREHOUSE_ID=0fb3aaac7c7d373c
EOF
npm run dev
```

The token expires after about an hour; rerun the snippet when queries start returning 401s.

## UI quality

- Responsive at desktop, tablet, and mobile widths. Use populated, realistic data; empty states
  make poor screenshots, and the README hero shot comes from this app.
- Use shadcn/ui components (`npx shadcn@latest add <component>`) rather than building primitives,
  and recharts-based shadcn charts for visualizations.

## Playwright click-path tests

These are automated *validation* of each Critical User Journey (CUJ). The `assets/click-path.docx`
deliverable is the human narration of the same journeys; both are needed.

- Config: `code/app/playwright.config.ts` with `testDir: "./e2e"`, a `webServer` running
  `npm run dev`, and `screenshot: "only-on-failure"`.
- One spec per CUJ in the plan, named after it (e.g. `code/app/e2e/create-portfolio.spec.ts`).
  Cover navigation, CRUD where it applies, form validation, data loading, and error states.
- Run `cd code/app && npx playwright test`. The tests must pass before committing app changes.
- Against the deployed app (after a push), pass its URL and your token; the config sends it as a bearer header:

  ```bash
  BASE_URL=$(databricks apps get revantage-lease-tracker --profile fevm-thhart-october-2026 -o json | python3 -c "import sys,json;print(json.load(sys.stdin)['url'])") \
  DATABRICKS_TOKEN=$(databricks auth token --profile fevm-thhart-october-2026 | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])") \
  npx playwright test
  ```
