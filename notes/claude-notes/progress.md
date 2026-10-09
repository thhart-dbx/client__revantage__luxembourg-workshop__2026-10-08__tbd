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
- [~] **>>> S9 IN PROGRESS <<<**: DONE: D3 all, D7 S1–3, D8 S1–5+8 (dashboard editor), D11 S1/S3/S5 (pipeline editor), D13 S2–5, D14 S1–3 (7919b36, 0d2572c + next commit). Prompt fixes baked into D7/D8/D11 guides. Remaining: D11 S6 (scratch pipeline `s9-property-pipeline-test` id 6eb4514d… + `s9_*` tables kept for it; re-inject bad batch, run, ask Genie Code; then delete pipeline + s9 tables), D9 apps editor, D1 S4–5, D4 S4–5, D5 S4, D6 S6, D10 S2/S4, D12 S2/S4, D16 S2/S4. Chrome DevTools MCP disconnected at 23:12; needs reconnect. Type with type_text (single line); read Genie Code output via evaluate_script on panel innerText.
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
