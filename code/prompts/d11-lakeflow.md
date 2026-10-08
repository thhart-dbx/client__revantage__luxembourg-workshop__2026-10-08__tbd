# Demo 11: Lakeflow — "Bronze-Silver-Gold in 20 minutes"

**Session:** Day 2, 9:30–10:30 (60 min) · **You build:** a Lakeflow Spark Declarative Pipeline from the raw CSVs into `<my_schema>` · **Reference:** pipeline "[Revantage workshop] Property Pipeline (Reference)", tables `<catalog>.<schema>.ref_d11_*`, source `code/pipelines/ref_property_pipeline/`
**Starting state:** 7 CSVs in `/Volumes/<catalog>/<schema>/raw/` (regions, properties, tenants, leases, gl_accounts, gl_transactions, quarterly_targets); oracle `gold_property_quarterly`
**Where:** Jobs & Pipelines → Create → ETL pipeline (Lakeflow Pipelines Editor), Genie Code in Agent mode

## Stage 0: Show, don't build (5 min)
- **Lakeflow Connect:** Data Ingestion → show the connector tiles (Salesforce, Workday, SQL Server, SharePoint…): authenticate once, pick objects, schedule. Revantage's Yardi/SAP extracts land as files today, so we use Auto Loader.
- **Lakeflow Designer / Visual Data Prep:** left nav *Visual Data Prep*: drag-and-drop for analysts; it generates the same pipeline code.

## Stage 1: Create the pipeline and ask for a design (8 min)
Create an ETL pipeline named `property-pipeline-<your_name>`, default catalog `<catalog>`, schema `<my_schema>`, SQL. Open Genie Code (Agent mode):
> I have raw CSV files in /Volumes/<catalog>/<schema>/raw/ for regions, properties, tenants, leases, gl_accounts, gl_transactions and quarterly_targets. Design a Bronze → Silver → Gold Lakeflow Declarative Pipeline in SQL. Bronze: Auto Loader streaming tables with read_files. Silver: typed and cleaned, latest lease version per lease_id by updated_at, properties without a region removed, market names standardized (Miami Bch → Miami Beach, NYC → New York, Lux-Ville → Luxembourg City). Gold: a materialized view gold_property_quarterly with revenue, operating_expense, mgmt_fee, capex, intercompany by property and fiscal quarter, net_profit = revenue - operating_expense - mgmt_fee, joined to quarterly_targets, with met_target and qoq_change_pct.

**Expected:** Genie Code proposes 3 files (bronze / silver / gold) with `CREATE OR REFRESH STREAMING TABLE … FROM STREAM read_files(...)` and `CREATE OR REFRESH MATERIALIZED VIEW`. Accept.
**If stuck:** copy the three files from `code/pipelines/ref_property_pipeline/` and replace `${raw_path}` with your raw path.

## Stage 2: Bronze (5 min)
**Checkpoint:** every bronze table uses `read_files('<raw path>/<entity>*.csv', format => 'csv', header => true)`.
**Teach:** keep `amount` as **STRING** in bronze (`schemaHints => '... amount STRING ...'`). Stage 6 shows why.

## Stage 3: Expectations (7 min)
**Prompt:**
> Add data quality expectations: on silver gl_transactions drop rows whose fiscal_period doesn't match YYYY-Qn and fail the update if amount is NULL after casting; on silver properties drop rows without a region; on gold expect revenue IS NOT NULL and fiscal_quarter in YYYY-Qn format.

**Expected:**
```sql
CONSTRAINT valid_fiscal_period EXPECT (fiscal_period RLIKE '^[0-9]{4}-Q[1-4]$') ON VIOLATION DROP ROW,
CONSTRAINT amount_parsed EXPECT (amount IS NOT NULL) ON VIOLATION FAIL UPDATE
```
(the agenda's `MATCHES` isn't SQL; `RLIKE` is), with `try_cast(amount AS DECIMAL(18,2))` in silver.

## Stage 4: Run and inspect (10 min)
Click **Run pipeline**. Open the **graph**: 7 bronze → silver → 1 gold.
**Expected** (data quality tab): `valid_fiscal_period` **3 failed** (a zero-sum manual accrual with period "2026Q2"); `has_region` **2 failed** (Riverside Annex, the duplicate Harbor Tower); gold **80 rows**.
**Checkpoint:**
```sql
SELECT COUNT(*) FROM <my_schema>.gold_property_quarterly g
JOIN <catalog>.<schema>.gold_property_quarterly r USING (property_id, fiscal_quarter)
WHERE abs(g.net_profit - r.net_profit) > 0.01      -- expect 0
```

## Stage 5: A late batch arrives (facilitator, 2 min)
Facilitator runs `scripts/d11_bad_batch.sh inject <profile> <catalog> <schema>`: it drops
`gl_transactions_late_batch_lux.csv` (3 rows from SAP-LUX, amounts like `"1.850,75"`) into the raw volume. Everyone clicks **Run pipeline** again.

**Expected:** the update **fails**: `EXPECTATION_VIOLATION … Violated expectations: 'amount_parsed' … "amount":"1.850,75" … source_file …/gl_transactions_late_batch_lux.csv`.

## Stage 6: Diagnose and fix with Genie Code (10 min)
**Prompt** (Genie Code, on the failed update):
> Why did this pipeline update fail? Show me the offending rows and propose a fix.

**Expected:** Genie Code points at `amount_parsed` and the European decimal format. A good fix in silver:
```sql
CASE WHEN amount RLIKE ',[0-9]{1,2}$' THEN CAST(replace(replace(amount, '.', ''), ',', '.') AS DECIMAL(18,2))
     ELSE try_cast(amount AS DECIMAL(18,2)) END AS amount
```
(verified: `1.850,75` → 1850.75, `980,40` → 980.40, `258689.5` unchanged).
**The lesson:** during pre-build we first read `amount` as DECIMAL in bronze. The CSV reader silently turned
`"980,40"` into **98,040.00** and `"1.850,75"` into **1.85**, with no error and no rescued data.
The string-in-bronze + expectation pattern is what caught it.

## Stage 7: Clean up (facilitator, 3 min)
`scripts/d11_bad_batch.sh remove …`, then **Full refresh all** (streaming tables keep already-ingested rows until a full refresh).
Note: production-mode pipelines retry failed updates automatically, so expect several failed retries in the history until the fix or removal lands.

## Wrap-up
- **So what:** a governed bronze-silver-gold pipeline from a paragraph of requirements, with quality rules that stop bad money from reaching the board pack.
- **Snowflake equivalent:** Snowpipe + Streams + Tasks + dynamic tables, stitched together. Lakeflow is one declarative pipeline with lineage, expectations, retries, and monitoring built in.
- **Verified:** 2026-10-08 on the FEVM workspace: reference pipeline gold = oracle (80 rows, all numeric columns exact, `code/tests/check_ref_pipeline.py`); expectation metrics as above; inject → FAILED with the message shown → remove → full refresh → COMPLETED and oracle match again. Genie Code Agent-mode prompts (Stages 1, 3, 6): UI verification pending (S9).
