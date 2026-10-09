# S9 — participant Genie Code prompts run in the UI (2026-10-08, FEVM, SQL editor)

| Demo / stage | Prompt surface | Result | Matches reference |
|---|---|---|---|
| D3 S1 | SQL editor run | `UNSUPPORTED_DATATYPE NUMBER(18,2)`; Quick Fix proposed a wrong fix (CAST AS NUMBER) | ✅ (+ facilitator warning) |
| D3 S2–3 | Genie Code chat | 5 translations (NUMBER, TO_VARCHAR, DIV0, IFF, SYSDATE); paused for approval of CREATE OR REPLACE; view = 176 rows | ✅ |
| D3 S4 | Genie Code chat | region fan-out explained, 72+72+32 = 176, proposed property_id join | ✅ |
| D3 S5 | Genie Code chat | LAG(…, 4) YoY; 64 rows; Harbor Tower 2026-Q2 −478,309.66 | ✅ identical |
| D7 S1 | Genie Code chat | loaded metric-view skill; valid DDL; 0.5933 / 0.5395 | ✅ identical |
| D14 S1 | Genie Code chat | correct `QS` query; Genie's own probe on serverless said "disabled" (misleading); on the warehouse €1,709,781 | ✅ (+ facilitator warning) |
| D13 S2 | Genie Code chat | 8 rows, gpt-5-6-sol 1,577,845 tokens | ✅ identical |

Not yet run in the UI: D1 S4–5, D3 S6, D4 S4–5, D5 S4, D6 S6, D7 S2–3, D8 (dashboard editor), D9 (apps editor), D10 S2/S4, D11 (pipeline editor Agent mode), D12 S2/S4, D13 S3–5, D14 S2–3, D16 S2/S4.
Scratch objects created during the runs (s9_property_performance_v, s9_mv_net_profit_margin) were dropped.
