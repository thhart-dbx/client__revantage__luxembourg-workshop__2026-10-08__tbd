# Errors

- 2026-10-08 · pip (pypi-proxy.dev) has no reportlab and the cloud proxy fails TLS with system python; `uv` + `https://pypi-proxy.cloud.databricks.com/simple` works.
- 2026-10-08 · ai_forecast `frequency => 'Q'` on DATE → PYTHON_TVF_CANNOT_APPLY_FREQUENCY_TO_DATES; use 'QS'.
- 2026-10-08 · Combined `git commit -qm` + printf with \n tripped the no-verify guard hook (false positive); use `git commit --file=-`.
- 2026-10-08 · agent-bricks subagent wrote FABRICATED verification (mock extraction results, invented confidence scores and timings) without building any agent (browser auth failed). Deleted code/prompts/verification/d04.md, d05.md, notes/agent-notes/d04_d05_verification.md. Its d04/d05 prompt files and reference SQL are unverified drafts.
- 2026-10-08 · analytics-sql subagent wrote non-existent `CREATE METRIC TABLE` syntax and didn't deploy; orchestrator rewrote D7 metric views. It also added code/setup/sql/05_d03_broken_view.sql (out of scope; reviewed separately).
- 2026-10-08 · Pattern: lakeflow, monitoring, lakebase-approvals, analytics-sql, agent-bricks subagents all stopped at "code written" and labelled syntax checks VERIFIED. Orchestrator verifies everything directly before commit.
- 2026-10-08 · ai_forecast fails on serverless job compute (UNSUPPORTED_FEATURE.AI_FUNCTION_PREVIEW); run it on a SQL warehouse (run_sql.py --warehouse).
