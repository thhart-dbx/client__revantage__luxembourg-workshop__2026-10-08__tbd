# Common brief for every build agent (read fully before starting)

Project root: `/Users/thomas.hart/ldrive/projects/builder/client__revantage__luxembourg-workshop__2026-10-08__tbd`

Read first: `CLAUDE.md`, `.claude/rules/*.md`, your role file in `.claude/agents/`, `notes/claude-notes/plan.md`,
`notes/agent-notes/data-contract.md` (the planted facts every expected result must match),
`code/prompts/README.md` (prompt-library format), and `notes/agent-notes/product-research.md` (partly
UNVERIFIED; verify before relying on it). The sibling project
`/Users/thomas.hart/ldrive/projects/builder/client__revantage__workshop__2026-10-05__tbd` built many of the
same products on this workspace 3 days ago. Its `code/`, `RUNBOOK.md` gotchas, and `notes/agent-notes/`
(dead-ends, errors) are the best reference for working API shapes. Read them; don't modify them.

## Environment

- Profile `fevm-thhart-october-2026`, catalog `thhart_october_2026_catalog`, schema `revantage_20261008`,
  warehouse `0fb3aaac7c7d373c`, user `thomas.hart@databricks.com`.
- Starting state already exists and is verified (`code/tests/check_starting_state.py` passes): tables
  `bronze_*`, `silver_*`, `gold_property_quarterly`, `customer_performance`; volumes `raw`, `documents`
  (`invoices/`, `policies/`, `leases/`).
- Run SQL with `code/tests/sqlclient.py` (`query(sql, profile, warehouse)`) using
  `code/data-gen/.venv/bin/python`. Install extra Python packages with
  `VIRTUAL_ENV=code/data-gen/.venv uv pip install --index-url https://pypi-proxy.cloud.databricks.com/simple <pkg>`
  (plain pip can't reach PyPI here).

## Build-live model (the point of the workshop)

Participants build every asset live on laptops with **Genie Code**. For each of your demos deliver:

1. **Starting state** additions (only if your demo needs something before participants begin).
2. **Reference solution**: the finished asset, pre-built and verified. Name it `ref_<...>` (tables, views,
   functions) or suffix the title with "(Reference)" (dashboards, Genie Agents, agents, jobs, pipelines).
   It must deploy from the bundle, or from a tested script in `code/scripts/` if no bundle resource exists.
3. **Prompt library file** `code/prompts/dNN-<slug>.md` in the exact format of `code/prompts/README.md`:
   one Genie Code (or Genie One) prompt per build stage, with expected result (quote real numbers from
   data-contract.md), a checkpoint query/click, and an "if stuck" recovery to the reference. Use
   `<catalog>.<schema>` placeholders, never FEVM names. Time boxes must fit the agenda slot.
4. **Verification** `code/prompts/verification/dNN.md`: for each stage, what you ran and what came back.
   Run every checkpoint query. Where a prompt targets Genie One (a Genie Agent), run it through the
   Genie Conversation API and record the answer and generated SQL. Prompts that can only run in the
   Genie Code UI get "UI verification pending (S9)" — S9 runs them in the browser later; don't fake it.

## Rules for working in parallel (six agents share this workspace and bundle)

- **Bundle files.** Put your resources in your own `code/resources/<area>.yml`. While it's in progress,
  name it `<area>.yml.wip` (not included by the bundle); rename to `.yml` only once `databricks bundle
  validate` passes with it. Never edit another agent's resource file or `databricks.yml`. If you need a
  variable, declare it with a default under top-level `variables:` in your own resource file.
- **Deploys.** `cd code && databricks bundle deploy` is shared. If it reports a lock, wait 60 s and retry
  (never `--force-lock`). Never run `bundle destroy`. Run only your own jobs/pipelines (`bundle run <your key>`).
- **Browser.** The Chrome DevTools MCP has one shared page. Only the agent whose brief says "browser:
  yes" may use it. Everyone else uses CLI/API/SQL.
- **Don't modify the starting-state tables** (bronze_*/silver_*/gold_*/customer_performance) or
  `code/setup/`, `code/data-gen/`, `code/documents/`. If you think they need a change, write it in
  `notes/agent-comms/thread.md` and continue.
- **Shared docs.** Don't edit README.md, RUNBOOK.md, CLAUDE.md, plan.md, progress.md. Write everything the
  orchestrator needs into `notes/agent-comms/handoff-<your-area>.md`: assets created (exact FQN / IDs /
  URLs), bundle keys, RUNBOOK steps (tested, in order, with teardown), README "Assets Created" rows, gotchas,
  and anything unverified. Log errors and dead ends in `notes/agent-notes/errors.md` / `dead-ends.md` (append only).
- Don't commit or push; the orchestrator does.
- **Honesty.** A previous agent claimed facts passed that didn't. In your final report, separate
  VERIFIED (you ran it and saw the result) from UNVERIFIED. If something doesn't work, say so and say what you tried.
