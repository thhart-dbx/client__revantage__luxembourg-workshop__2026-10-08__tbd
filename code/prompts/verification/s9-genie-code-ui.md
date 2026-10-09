# S9 — participant Genie Code prompts run in the UI (2026-10-08, FEVM)

| Demo / stage | Prompt surface | Result | Matches reference |
|---|---|---|---|
| D3 S1 | SQL editor run | `UNSUPPORTED_DATATYPE NUMBER(18,2)`; Quick Fix proposed a wrong fix (CAST AS NUMBER) | ✅ (+ facilitator warning) |
| D3 S2–3 | Genie Code chat | 5 translations (NUMBER, TO_VARCHAR, DIV0, IFF, SYSDATE); paused for approval of CREATE OR REPLACE; view = 176 rows | ✅ |
| D3 S4 | Genie Code chat | region fan-out explained, 72+72+32 = 176, proposed property_id join | ✅ |
| D3 S5 | Genie Code chat | LAG(…, 4) YoY; 64 rows; Harbor Tower 2026-Q2 −478,309.66 | ✅ identical |
| D7 S1 | Genie Code chat | loaded metric-view skill; valid DDL; 0.5933 / 0.5395 | ✅ identical |
| D14 S1 | Genie Code chat | correct `QS` query; Genie's own probe on serverless said "disabled" (misleading); on the warehouse €1,709,781 | ✅ (+ facilitator warning) |
| D13 S2 | Genie Code chat | 8 rows, gpt-5-6-sol 1,577,845 tokens | ✅ identical |
| D3 S6 | Genie Code chat | full-outer-join diff with per-column mismatch list; 0 rows vs reference | ✅ |
| D7 S2 | Genie Code chat | 8 / 5 / 0.625; 3 shortfalls; formatted as USD → prompt now says EUR | ✅ (+ prompt fix) |
| D7 S3 | Genie Code chat | LAG in source; matches ref on every market; guide checkpoint relabelled (+10.0% / −44.1% / −18.6% are *net-profit* growth; revenue growth is +9.2% / −17.6% / −6.4%) | ✅ (+ guide fix) |
| D13 S2b | Genie Code chat | new prompt on system.serving.endpoint_usage: sonnet-4-6 37 req / 10,387 tok / 3 errors (the ai_query test traffic that never reached system.ai_gateway.usage) | ✅ |
| D13 S3 | Genie Code chat | 1 masked user; gpt-5-6-sol 2.17% errors | ✅ |
| D13 S4 | Genie Code chat | billing × list_prices validity join; 19 rows ~$19; VECTOR_SEARCH $14.02 top | ✅ |
| D13 S5 | Genie Code chat | `tokens_today` single column = 0 | ✅ |
| D14 S2–3 | Genie Code chat | 'disabled' probe again, then ran on warehouse: Harbor Tower 1,709,780.95 vs 1,858,200; Zuidas 1,326,134.51 vs 1,425,400 | ✅ |
| D8 S1 | dashboard editor | original prompt: joined metric views ON 1=1, failed, claimed success → prompt now says MEASURE() subqueries + run it; revised prompt right first time | ✅ (+ prompt fix) |
| D8 S2 | dashboard editor | €10.7M · 59.3% · 62.5% + line chart; self-fixed a MEASURE error | ✅ |
| D8 S3 | dashboard editor | needed revenue_target source + filter binding follow-ups (now in prompt/checkpoint); Southeast €2,094,949.91 | ✅ (+ prompt fix) |
| D8 S4 | dashboard editor | 8 rows, Sharp decline flag; qoq % double-scaled → prompt states units | ✅ (+ prompt fix) |
| D8 S5 | dashboard editor | filters bound to one dataset while claiming all pages → prompt asks to bind + verify | ✅ (+ prompt fix) |
| D8 S8 | dashboard editor | Forecast page with 5 series for Harbor Tower | ✅ |
| D11 S1 | pipeline editor | sampled CSVs, wrote 3 files, self-fixed dry-run error; gold = oracle on 80 rows; but exact-filename globs + amount DOUBLE → both now in the S1 prompt | ✅ (+ prompt fix) |
| D11 S3 | pipeline editor | STRING→try_cast, 4 expectations; full refresh; 3 / 2 / 80 exactly | ✅ |
| D11 S5 | CLI start-update | FAILED `EXPECTATION_VIOLATION 'amount_not_null' "1.850,75"` | ✅ |
| D11 S6 | pipeline editor | diagnosed from events, 3 offending rows, European-decimal fix applied + run; silver 1850.75 / 2410.00 / 980.40 | ✅ |
| D10 S2 | Genie Code chat | description + 3 comments correct; applied after a retry (long tab) | ✅ |
| D10 S4 | Genie Code chat | masks correct; tagged with governed `pii` key → rejected → tried to extend the account tag policy; stopped (policy unchanged); prompt now names class.* tags | ✅ masks / ⚠️ tags (+ prompt fix) |
| D12 S2 | SQL editor on Lakebase Postgres | DDL with both CHECKs + generated column; 37.7k false / 312k true | ✅ |
| D12 S4 | Genie Code on job file | correct explanation (REST credential, Approved filter, idempotent MERGE) | ✅ |
| D16 S4 | Genie Code chat | original prompt: inclusive σ (seed z 3.01, near-miss by construction) → prompt now says leave-one-out; revised: 0 rows clean, Harbor Tower 2026-Q3 z 171.89 on seeded clone | ✅ (+ prompt fix) |
| D16 S2 | — | needs `_profile_metrics`; FEVM can't create the monitor (1,000 limit) → Revantage pre-flight | ⏭ blocked on FEVM |
| D1 S4 | Genie Code chat | layer explanation (sees ref_* objects too); €2.69M / €2.09M / €1.59M | ✅ |
| D1 S5 | Genie Code chat | 3 lease PDFs, 21/20/21 elements, Harbor Tower first element "EXPIRED" | ✅ |
| D4 S4 | Genie Code in agent's Run-in-SQL tab | step-by-step explanation + CTAS; 8 rows, HV 339,600 (mislabelled €; it's USD) | ✅ |
| D4 S5 | Genie Code chat | exactly HV-2026-0417 USD 339,600 ↔ €312,390.76 R&M OpEx | ✅ |
| D5 S4 | Genie Code chat + KA via ai_query | approval pause, 8 answers; **6/8 correct** (KA named Asset Manager for two €25–50k invoices) → guide turns it into a verify-against-a-rule lesson | ⚠️ (+ guide teach) |
| D6 S6 | Genie Code chat | 5-check view 2,2,2,1,3 = reference | ✅ |
| D9 S1–4 | Genie Code on app source (Streamlit template) | wrong app.yaml valueFrom → "No SQL warehouse configured" → prompt now names `sql-warehouse`; then 6 / 14 rows, risk, cards €103,046.05 / €1,236,552.60 / BBB+, CSV | ✅ (+ prompt fix) |

**All participant Genie Code prompts have now been run in the UI** (except D16 S2, blocked on FEVM by the monitor limit → Revantage pre-flight).

Pattern worth teaching: Genie Code sometimes reports success without checking (D8 S1, S5). Every build-along prompt that creates something now ends with "run it" / "verify".
Scratch objects created during the runs (s9_* views/tables, two scratch dashboards, scratch pipeline + its internal tables, approvals_s9 Postgres schema, scratch Streamlit app + source folder + grants) were all removed; starting-state check ALL PASS afterwards.
