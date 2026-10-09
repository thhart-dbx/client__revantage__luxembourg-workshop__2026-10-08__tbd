# Progress — Revantage Luxembourg workshop (request 2)
Status: in-progress · Last updated: 2026-10-08 22:00 ET · Current group: G2/G3 (fan-out)

| Group | Steps | Status |
|-------|-------|--------|
| scaffold | new-demo phases 0–7 | DONE (0acfb21) |
| G1 | S1 data + docs, S2 setup job + smoke test | DONE (5e885a5) — 28/28 checks pass; ai_forecast verified |
| G2/G3 | 7 parallel agents (below) | IN PROGRESS |
| G4 | S9 live Genie Code prompt runs in browser (serialized), S10 README/RUNBOOK/smoke, S12 pre-flight + `revantage` target + sandboxes | pending |
| G5 | S11 deliverables (build-along click-path, handout, decks, architecture, hero) | pending |

## Status by demo (orchestrator-verified) · updated 2026-10-08 ~18:30 ET
All 16 demos: reference built + verified, prompt guide rewritten from verified numbers (see README demo table).
Commits: 827c401 (D3/D7/D14) · f823962 (D2/D6) · ac87dcd (D8/D10) · 1e4fc99 (D4) · 977abf6 (D5/D11) · 3521d6a (D9) · 4dd2739 (D12) · 0b56f42 (D13/D16) · b6c0eaf (D1/D15) · 3b8659d (README/RUNBOOK)

## Open
- [x] S9 DONE (2026-10-09): every participant Genie Code prompt run in the UI across SQL editor, dashboard editor, pipeline editor, Lakebase SQL, job file and app source (7919b36, 0d2572c, 3d56ca6, 565a93d, 45525fd + final). Log: code/prompts/verification/s9-genie-code-ui.md. Prompt fixes baked into D7/D8/D10/D11/D12/D16/D9 guides; D5 KA 6/8 turned into a verification lesson. Only D16 S2 blocked on FEVM (monitor limit) → Revantage pre-flight. All scratch objects removed; starting state ALL PASS.
- [x] Deliverables DONE (2026-10-09): click-path + handout (md/docx, generated from guides), internal (23) + client (24) decks (vendored databricks-slides kit + screenshot/demo/build-step slide types, visually checked via PowerPoint PDF export), architecture.png/.drawio, hero. Also found D13 FM traffic lands in system.serving.endpoint_usage (Q6 + new prompt, UI-verified).
- [ ] **>>> NEXT: Revantage workspace <<<**: access, preflight.py, fill `revantage` target, deploy, setup + sandboxes, starting-state check, D16 S2 + D2/D9 show-items, D13 usage-table check (Unity Gateway migration).
- [ ] D13: confirm the 21:18 UTC sonnet-4-6 traffic (40 ok + 3 errors) lands in system.ai_gateway.usage
- [x] Stale lock cleared with user-approved --force-lock (2026-10-08 ~21:30 ET); dev deployed clean
- [ ] Deliverables: build-along click-path (md + docx), participant handout, internal + client decks, architecture diagram (hero done)
- [ ] Revantage workspace: access, pre-flight, fill `revantage` target

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
