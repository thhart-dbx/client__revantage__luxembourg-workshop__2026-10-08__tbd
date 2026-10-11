# Demo 17: Genie Accuracy Ladder — "From 0 to 10 out of 10, one layer at a time"

**Session:** Day 2, 2:45–3:20 (35 min) · **You build:** a Genie Agent on the legacy warehouse, made accurate step by step (business names → column comments → table descriptions and keys → metric views → instructions), with a benchmark score after every step · **Reference:** Genie Agent "Revantage Accuracy Lab (Reference)", tables `<catalog>.<schema>.ref_d17_*` (source `code/reference/d17_business_layer.sql`), scorecard `ref_d17_benchmark_results` (`code/genie/d17_ladder.py`)
**Starting state:** the "legacy Snowflake warehouse" `legacy_prp_mstr`, `legacy_gl_txn`, `legacy_gl_acct`, `legacy_lse`, `legacy_tnt`, `legacy_qtr_tgt` (abbreviated names, coded values, no comments, no keys, lease history with old versions), its documentation `legacy_data_dictionary`, the benchmark `d17_benchmark` (10 questions + ground-truth SQL), and the Genie Agent "Revantage Accuracy Lab (Start)" (the legacy tables + the same 10 benchmark questions)
**Where:** Genie Agents (Configure, Benchmarks); SQL editor with Genie Code

The story: the data is the same at every step; only the metadata changes. Genie's accuracy on the same 10
questions goes **20% → 10% → 30% → 50% → 100%** (Genie's own benchmark judge). Each layer fixes a different kind of mistake, so the
order matters: names and comments say what a column *is*, descriptions and keys say what a row *is*,
metric views say how a KPI is *calculated*, instructions say what the business *means*.

## Stage 1: Clone and take the baseline (5 min)
Genie Agents → **Revantage Accuracy Lab (Start)** → ⋮ → **Clone** → name it `Accuracy Lab – <your_name>`, **Clone to** your home folder → **Clone**. Open the **Benchmark** tab: the 10 questions came with the clone (**Questions (10)**). Set **Mode: Chat** (single-turn SQL, about 3 minutes for 10 questions; Agent mode takes about 8; the mode resets to Agent whenever the page reloads, so check it before every run) → **Run all benchmarks**.

**Expected:** **≈ 2 of 10** (20%). Click a question: Genie's judge shows the assessment (**Bad** · *Extra Rows*, *Filter Issue*), a **Failure analysis** comparing its SQL with the ground truth, and **Attempt fix**. Open one failure, e.g. "How many active leases do we have?": Genie guessed `LSE_STS_CD = 'Active'` and got 0 (the code is `A`). "What was total net profit in 2026-Q2?" sums the wrong thing (no idea which `ACCT_CLS_CD` is revenue).
**Tip:** use a new query tab in the SQL editor for every stage below, so Genie Code doesn't re-run the previous stage's statements.
**Teach:** a benchmark is a set of real questions with an agreed answer (ground-truth SQL). Write it *before* you tune, so every change is measured, not felt.

## Stage 2: Business column names (7 min)
**Prompt** (Genie Code, SQL editor):
> Using <catalog>.<schema>.legacy_data_dictionary, create one table in <my_schema> for each legacy_* table in <catalog>.<schema>: name it after the dictionary's business_name for the table (the row where column_name is NULL) and rename every column to its business_name. Keep the values unchanged and don't add comments yet. Run it and show me the row counts.

**Expected:** 6 tables `properties` 8, `gl_accounts` 15, `gl_transactions` 2,681, `leases` 52, `tenants` 40, `quarterly_targets` 96; values untouched (`account_class` is still `R`/`O`/`M`/`C`/`I`).
Then in your agent: **Configure → Data** → remove the six `legacy_*` tables, add your six → **Benchmarks → Run all**.
**Checkpoint:** **≈ 1 of 10** (10%). Readable names alone don't help: Genie now writes `account_class = 'Revenue'` and `lease_status = 'Active'`, and every filter returns 0.
**If stuck:** run the `@rung R2` section of `code/reference/d17_business_layer.sql` with `ref_d17_` replaced by `<my_schema>.`.

## Stage 3: Column comments (5 min)
**Prompt** (Genie Code, SQL editor):
> Add a column comment to every column of my six tables in <my_schema>, taken from the description in <catalog>.<schema>.legacy_data_dictionary (match on business_name). Run it and confirm with DESCRIBE TABLE on gl_accounts and leases.

**Expected:** `ALTER TABLE … ALTER COLUMN … COMMENT …` for every column; `account_class` reads "R = Revenue, O = Operating expense, M = Management fee, C = CapEx, I = Intercompany recharge".
**Run all benchmarks** again (no need to touch the agent: it reads the comments live).
**Checkpoint:** **≈ 3 of 10** (30%). Genie decodes the codes now (CapEx and office revenue are right), but it still guesses the business rules: net profit subtracts CapEx and intercompany too (€5.59M instead of **€6.38M**), and "active leases" counts old lease versions.

## Stage 4: Table descriptions and keys (6 min)
**Prompt** (Genie Code, SQL editor):
> For each of my six tables in <my_schema>, set the table comment from the legacy_data_dictionary row where column_name is NULL (use my table and column names instead of the legacy ones). Then add the primary keys and foreign keys those descriptions name; make the key columns NOT NULL first. Run it and show me the constraints.

**Expected:** `COMMENT ON TABLE …`; `leases` says "one row per lease VERSION … the current one has the latest updated_at"; PKs on all six, FKs from `gl_transactions`, `leases`, `quarterly_targets`.
**Checkpoint:** **≈ 5 of 10** (50%). The lease questions pass (39 active leases, €1,083,458.87 monthly rent): the grain was the missing fact. Net profit is still wrong: no table can tell Genie the *Finance* definition.
**Watch for:** recreating a table with `CREATE OR REPLACE TABLE … AS SELECT` keeps its old comments. Drop it first if you want a clean slate.

## Stage 5: Metric views and instructions (6 min)
**Configure → Data → Add** the governed metric views `<catalog>.<schema>.ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth` (or your own from Demo 7) → **Run all**.
**Checkpoint:** **9–10 of 10**. Net profit, margin, target misses and attainment now come from the approved definitions (€6.38M, 59.3%, Peachtree Center / Harbor Tower / Zuidas Residences, 62.5%).
Then **Configure → Instructions** → paste:
> Amounts are EUR. The latest complete fiscal quarter is 2026-Q2: "this quarter" means 2026-Q2 and "last quarter" means 2026-Q1; never use the calendar date to pick a quarter. Net profit = revenue (account_class R) - operating expense (O) - management fee (M); CapEx (C) and intercompany (I) are not deducted; prefer the metric views for net profit, margin and target attainment. The leases table keeps every version of a lease: always use only the latest version per lease_id before counting or summing; active means lease_status = 'A'. Property type codes: OFF = Office, MFH = Multifamily, RTL = Retail. Credit ratings best to worst: AAA, AA, A, BBB, BB, B; below investment grade means BB or B.

**Checkpoint:** **10 of 10**, and it stays there when the question is phrased differently (the instructions carry the conventions the data can't).
**Teach:** instructions are for business conventions that live nowhere in the data ("this quarter", "below investment grade"). Keep them short; everything a column or table can say belongs in the catalog, where every tool (dashboards, Genie One, Genie Code) gets it too.

## Stage 6: Keep it accurate (6 min)
- **Benchmark → Evaluations:** every run is kept with its accuracy; open a run to see each question's SQL next to the ground truth, the failure analysis, and **Attempt fix** (Genie proposes the instruction or example that would fix it). **Analyze with Genie** summarizes the context gaps across a run. Re-run after every schema or instruction change.
- **Monitoring** tab: the questions people actually ask, thumbs up/down, and the answers to review. Turn a good answer into an **SQL example**; turn a recurring question into a new **benchmark** question.
- **SQL examples, synonyms, join relationships** (the Reference agent has 3 examples, synonyms on 7 columns, 5 joins): they make answers stable across phrasings; the score stays at 10/10, the variance drops.
- The facilitator's scorecard, measured with the same 10 questions twice per rung:
```sql
SELECT rung, ROUND(100 * AVG(CAST(correct AS INT))) AS pct_correct
FROM <catalog>.<schema>.ref_d17_benchmark_results
GROUP BY rung ORDER BY rung
```
→ R1 **5** · R2 **10** · R3 **20** · R4 **50** · R5 **90** · R6 **100** · R7 **100**.

## Reset (facilitator, after the session)
Participants' tables live in their own `<my_schema>`; their cloned agents in their own folders. Nothing shared changes. To rebuild the reference: `databricks bundle run ref_analytics`; to re-measure the ladder: `code/genie/d17_ladder.py`.

## Wrap-up
- **So what:** Genie accuracy is engineered, not prompted. Most of the gain comes from metadata in Unity Catalog (comments, descriptions, keys, metric views), which every other tool reuses; the agent's own instructions are the last few points.
- **Snowflake equivalent:** column comments and semantic views exist in Snowflake too; here they feed Genie, Genie One, Genie Code and AI/BI from one catalog, and the benchmark makes the improvement measurable.
- **Verified in the UI:** 2026-10-10 on the FEVM workspace, the live path end to end on a clone of the Start agent: Clone (with **Clone to** folder) kept the 10 questions; Stage 1 benchmark 20% (Agent mode); Stage 2 Genie Code prompt built the six tables (15 · 2,681 · 52 · 8 · 96 · 40 rows) → 10% (Chat); Stage 3 prompt commented all 33 columns → 30%; Stage 4 prompt set 6 descriptions, 6 PKs, 5 FKs → 50%; metric views → 100%; instructions → 100% (screenshots `d17-*.png`).
- **Verified by script:** 2026-10-10 on the FEVM workspace with `code/genie/d17_ladder.py` (a fresh agent per rung, 10 questions × 2 runs, results in `ref_d17_benchmark_results`): R1 1/20, R2 2/20, R3 4/20, R4 10/20, R5 18/20, R6 20/20, R7 20/20. In-place check: one agent on business names scored 1/20, then 10/20 after comments, descriptions and keys were added to its tables (no re-config needed). Deployed agents: Start 0/10, Reference 10/10.
