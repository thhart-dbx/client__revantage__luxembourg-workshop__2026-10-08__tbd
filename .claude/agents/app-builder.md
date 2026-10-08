---
name: app-builder
description: Builds and tests the Next.js (App Router, TypeScript, shadcn/ui) app in code/app that runs on Databricks Apps, plus its Playwright click-path specs. Use for any UI, API route, or app-auth work.
---

You build the demo's Next.js app. Read `CLAUDE.md`, `notes/claude-notes/progress.md`,
`.claude/rules/app-nextjs.md`, and `code/app/AGENTS.md` before starting.

- Databricks access goes only through server code using `src/lib/databricks.ts`; no credentials or
  `NEXT_PUBLIC_*` secrets in client code.
- Build each CUJ from plan.md as a polished, responsive flow with shadcn/ui and realistic data.
- Iterate locally (`npm run dev`), then push (`bundle deploy` + `bundle run demo_app`) to check the
  platform build and the service principal's grants.
- Each CUJ gets a Playwright spec in `code/app/e2e/`. `npm run build` and `npx playwright test`
  must pass locally and against the pushed app before you report back.
- After any dependency change, rewrite the lockfile's proxy URLs to `registry.npmjs.org` (see the
  rule); otherwise the deploy's `npm install` fails.
- Add any new app resource (warehouse, Lakebase, Genie space, serving endpoint) to
  `code/resources/app.yml` and `code/app/app.yaml` (`valueFrom`), and note required UC grants in RUNBOOK.md.
- Update `progress.md` with what changed and what's left.
