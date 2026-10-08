# Demo 15: Hands-On Lab — Build Your Own

**Session:** Day 2, 1:30–2:30 (60 min) · Pick one track. Each starts from an asset you've already seen working, so you always have a fallback.
**Where:** your sandbox schema `<my_schema>` (or `<schema>` with `_<your_name>` suffixes), Genie Code throughout

## Track A — Analyst: a Genie Agent for your domain
1. Genie → **New** → name `<your domain> Q&A – <your_name>`; add `gold_property_quarterly`, `silver_leases`, `silver_tenants` (and your own tables if you have dev access).
2. **Instructions:** start from the Reference agent's text (open *Revantage Portfolio Q&A (Reference)* → Configure → Instructions) and adapt the definitions to your domain: latest quarter, net profit definition, what "risk" means.
3. Add 3 **SQL examples** for your hardest questions, synonyms on 3 columns, and join specs.
4. Test 5 questions; for each wrong answer, fix the *context* (instruction, example, synonym), not the question.
   **Benchmark** (should pass after Stage 3): "Which leases expire in the next 90 days and what is the monthly rent at risk?" → 6 leases, €103k (as of 2026-10-08).
- **Fallback:** duplicate the Reference agent and edit it.

## Track B — Dashboard builder: your portfolio company's page
1. New dashboard; datasets on the metric views (`ref_mv_*` or your Demo 7 views) filtered to your region or property type.
2. **Prompt** (Genie Code in the dashboard editor):
   > Build a page for <region> with net profit margin and target attainment counters for 2026-Q2, a net profit trend by property, and a table of leases expiring in 180 days from silver_leases.
3. Add the dashboard's **Ask Genie**; publish; share with a colleague.
- **Fallback:** clone "Revantage Portfolio Review (Reference)" and filter it.

## Track C — Data engineer: a new source, end to end
1. Pick a source: a CSV you bring, or the `documents/invoices` extraction from Demo 4 (`ai_extract` in a pipeline).
2. **Prompt** (Genie Code, pipeline editor, Agent mode):
   > Create a pipeline that ingests <path> with Auto Loader into bronze, cleans it into silver with an expectation that drops rows missing <key> and fails the update when <amount> doesn't parse, and builds a gold summary.
3. **Jobs & Pipelines → Create job**: task 1 = your pipeline, task 2 = a SQL task that checks row counts; schedule daily 06:00; email on failure; 2 retries.
4. Add a SQL alert on a gold metric (copy the pattern from "Daily AI tokens > 1M (Reference)").
- **Fallback:** copy `code/pipelines/ref_property_pipeline/` (Demo 11) and change the paths.

## Closing the lab (5 min)
Each person shows one thing they built. Collect follow-ups for the 4:15 "Next steps" session.

- **Verified:** the starting assets for each track are verified (Demos 2, 7, 8, 9, 11, 13). The lab itself is open-ended; the Track A benchmark numbers come from the lease tracker app (Demo 9).
