
- 2026-10-08 · S1 v1 (subagent) rejected: flat revenue, nonsensical targets, raw market names in gold, text instead of PDF, multi-pass mutating scripts. Rewritten by orchestrator as a single generator; documents via HTML → headless Chrome PDF (PyPI only reachable via `uv` + pypi-proxy.cloud.databricks.com).
- 2026-10-08 · Group reporting currency EUR for all GL/gold amounts (US properties converted); invoices keep their source currency.
- 2026-10-08 · Starting state built by one serverless job (`setup_starting_state`): generator → volumes → SQL files with ${catalog}/${schema}. Plain Delta tables (not a pipeline), so Demo 11's participant pipeline writes its own tables; ref pipeline output is checked against the same oracle.
- 2026-10-08 · gold_property_quarterly ships without a table description and without comments on net_profit / met_target / qoq_change_pct; participants write them in Demo 10.
