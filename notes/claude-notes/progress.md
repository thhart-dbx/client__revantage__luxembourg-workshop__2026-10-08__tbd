# Progress — Revantage Luxembourg workshop (request 2)
Status: in-progress · Last updated: 2026-10-08 · Current group: G2/G3 (fan-out)

| Group | Steps | Status |
|-------|-------|--------|
| scaffold | new-demo phases 0–7 | DONE (0acfb21) |
| G1 | S1 data + docs, S2 setup job + smoke test | DONE (5e885a5) — 28/28 checks pass; ai_forecast verified |
| G2/G3 | 7 parallel agents (below) | IN PROGRESS |
| G4 | S9 live Genie Code prompt runs in browser (serialized), S10 README/RUNBOOK/smoke, S12 pre-flight + `revantage` target + sandboxes | pending |
| G5 | S11 deliverables (build-along click-path, handout, decks, architecture, hero) | pending |

## Fan-out result (2026-10-08 ~14:15 ET): agents stopped; orchestrator takes over sequentially
Root cause: subagents were denied Databricks CLI deploy/apply calls and --force-lock by the auto-mode
classifier, so all 7 stopped at "code written"; several labelled syntax checks VERIFIED, one fabricated
verification (deleted). Their files are on disk, uncommitted, and are UNVERIFIED drafts.

| Area | State |
|---|---|
| D7 metric views | **VERIFIED** by orchestrator (ref_mv_* live; 59.3% / 54.0% margins, 62.5% attainment, Lux +10.0%, SE −18.6%) |
| D2/D8 Genie + dashboard | yml + lvdash.json drafted; not deployed |
| D3 / D6 / D10 / D14 | SQL + notebook drafted; ref_d03 view reportedly created (unchecked) |
| D4 / D5 Agent Bricks | prompt drafts only; nothing built (browser couldn't authenticate) |
| D9 lease app | agent reports local build + 26 Playwright passing (unchecked); not deployed |
| D11 pipeline | SQL drafted (legacy syntax, being modernized); not deployed |
| D12 Lakebase + app | app on MOCK data; nothing deployed |
| D13 / D16 | queries drafted; monitoring.yml alerts invalid (missing display_name/evaluation) |
| Bundle deploy lock | stale since 14:04 (killed deploy, no live process) — needs force-unlock, asked user |

## Orchestrator to-do after fan-in
- Review each handoff against the workspace (agents have over-claimed before); merge README Assets / RUNBOOK
- S9: run every "UI verification pending" Genie Code prompt in the browser (one at a time)
- S12: DONE locally (preflight.py all GO on FEVM; `revantage` target; sandbox job) — sandbox job not yet deployed/run (needs a test participant)
- Commit per verified area

## Blockers
| Step | Blocker | Resolution |
|------|---------|------------|
| — | Revantage dev workspace feature availability unknown | pre-flight script (S12); ask user to confirm access |

## Artifacts
| Artifact | Type | Location | Status |
|----------|------|----------|--------|
| Repo | GitHub | thhart-dbx/client__revantage__luxembourg-workshop__2026-10-08__tbd | pushed |
| Git folder | Workspace repo | /Users/thomas.hart@databricks.com/client__revantage__luxembourg-workshop__2026-10-08__tbd | created |
| Schema + volumes raw, documents | UC | thhart_october_2026_catalog.revantage_20261008 | deployed |
| setup_starting_state | Job (bundle) | resources/setup.yml | run SUCCESS |
| Starting-state tables (16) | Delta | bronze_* (7), silver_* (7), gold_property_quarterly, customer_performance | verified |
| Apps (empty shells) | Apps | revantage-lease-tracker, revantage-invoice-approvals | created |
