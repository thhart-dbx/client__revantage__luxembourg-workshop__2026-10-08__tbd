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

Not yet run in the UI: D1 S4–5, D4 S4–5, D5 S4, D6 S6, D9 (apps editor), D10 S2/S4, D11 S6 (Genie Code diagnosis; scratch pipeline `s9-property-pipeline-test` and its `s9_*` tables kept for it, delete after), D12 S2/S4, D16 S2/S4.

Pattern worth teaching: Genie Code sometimes reports success without checking (D8 S1, S5). Every build-along prompt that creates something now ends with "run it" / "verify".
Scratch objects created during the runs (s9_* views, two "S9 Portfolio Review – test" dashboards) were dropped/trashed.
