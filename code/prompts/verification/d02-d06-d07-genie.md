# Genie One verification (Conversation API), 2026-10-08, FEVM workspace

Tester: `code/tests/ask_genie.py`. Raw transcripts (SQL + rows + text): `verification/raw/`.
Agents: Start `01f1c34be4d710108435324ff679d6d0`, Reference `01f1c34be4d01738b7f2b3edb0d6519e` (bundle `resources/genie.yml`).

| Demo | Question | Agent | Result | Matches contract |
|---|---|---|---|---|
| D2 Q1 | Which properties missed their quarterly target in 2026-Q2? | Start | Peachtree −71,293; Harbor Tower −43,235; Zuidas −41,701 | ✅ F1 |
| D2 Q2 | What changed from Q1 to Q2 for the Southeast region? | Start | Revenue −267k (−6.4%), opex +221k, NP 2.58M → 2.09M | ✅ F2 (aggregate only) |
| D2 Q2b | (follow-up) Which property drove that, and was it revenue or costs? | Start | Harbor Tower −506,697: revenue −321k, costs +185k; others up | ✅ F2 |
| D2 Q3 | Show me revenue by property type as a bar chart | Start | Office 46.7M, Multifamily 37.2M, Retail 19.7M (all quarters) | ✅ |
| D2 Q4 | Which market has the highest QoQ net profit growth? | Start | Luxembourg City +10.02% (2026-Q2 vs Q1) | ✅ F3 — only after adding the default-period instruction; before it, Genie ranked all history (Boston 2024-Q4) |
| D2 Q5 | Summarize the top 3 risks across the portfolio this quarter | Start | target-miss gap 156k (3 props); 1 QoQ decline; 0 loss-making | ⚠️ grounded but shallow |
| D2 Q5 | same | Reference | 14 leases expiring ≤180 d; 3 missed targets; 1 QoQ decline | ✅ (first try hit a transient UC rate limit, retry OK) |
| D6 Q1 | How many properties are in bronze vs gold? | Start | 10 vs 8 | ✅ F5 |
| D6 Q2 | Which properties exist in bronze but not in gold? | Start | 9 Riverside Annex, 10 Harbor Tower (both NULL region) | ✅ F5 |
| D6 Q3 | Null rate for every column in bronze_properties | Start | region_id 20%; `_rescued_data` 100% (Auto Loader column) | ✅ F5 |
| D6 Q4 | Duplicate property names with different IDs? | Start | Harbor Tower: ids 3, 10 | ✅ F5 |
| D6 Q5 | Compare market names bronze vs silver | Start | Miami Bch/Miami Beach, NYC/New York, Lux-Ville/Luxembourg City | ✅ F5 |
| D7 s6 | Which properties missed their quarterly target in 2026-Q2? | Reference | same 3, answered from `ref_mv_target_attainment.net_profit_vs_target` and names the metric view | ✅ |
| D8 | Why did Southeast net profit drop in Q2? | Reference | Harbor Tower −506,697 = revenue −321,490 + opex +194,852; others improved | ✅ F2 |
| D7 | Net profit margin this quarter vs Asset Management definition | Reference | 59.33% vs 53.95% (−5.38 pp), names the metric view | ✅ F4 |

Facilitator notes
- Q5 on the Start agent is the "before" for Demo 7: the Reference agent's instructions (lease expiry, credit rating) make it a real risk summary.
- Shared FEVM metastore can return `REQUEST_LIMIT_EXCEEDED` (UC rate limit); just ask again.
- `_rescued_data` in bronze is Auto Loader's column for unparseable fields; a good aside in Demo 6.
