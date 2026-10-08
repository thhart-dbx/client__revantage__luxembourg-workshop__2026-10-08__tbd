# Handoff: Lakeflow Demo 11 & Track C (Demo 15)

**Agent:** lakeflow · **Task:** Build reference pipeline and prompts for D11 "Bronze-Silver-Gold in 20 minutes" and Track C "Build Your Own Pipeline"  
**Status:** COMPLETE (assets created; verification pending)  
**Artifacts:** 9 files created; bundle validates; tests ready to run  

---

## Assets Created

### Bundle Resources

| Key | Type | Location | Status |
|-----|------|----------|--------|
| `ref_property_pipeline` | DLT Pipeline | `code/resources/lakeflow_ref.yml` | ✓ Defined, bundle validates |

### Pipeline Code

| Name | Type | Path | Tables (prefix) | Status |
|------|------|------|-----------------|--------|
| Revantage Property Pipeline (Reference) | Spark DLT | `code/pipelines/ref_property_pipeline/dlt_pipeline.sql` | ref_d11_* (14 tables/views) | ✓ Created |

### Tables & Views (to be created at deploy time)

**Bronze layer** (streaming, Auto Loader):
- `<catalog>.<schema>.ref_d11_bronze_regions` (3 rows)
- `<catalog>.<schema>.ref_d11_bronze_properties` (10 rows, includes 2 with NULL region_id)
- `<catalog>.<schema>.ref_d11_bronze_tenants` (~40 rows)
- `<catalog>.<schema>.ref_d11_bronze_leases` (52 rows)
- `<catalog>.<schema>.ref_d11_bronze_gl_accounts` (15 rows)
- `<catalog>.<schema>.ref_d11_bronze_gl_transactions` (~2,700 rows, includes 3 with malformed fiscal_period)
- `<catalog>.<schema>.ref_d11_bronze_quarterly_targets` (80 rows)

**Silver layer** (typed, filtered, deduplicated):
- `<catalog>.<schema>.ref_d11_silver_regions` (3 rows)
- `<catalog>.<schema>.ref_d11_silver_properties` (8 rows, NULL regions dropped)
- `<catalog>.<schema>.ref_d11_silver_tenants` (~40 rows)
- `<catalog>.<schema>.ref_d11_silver_leases` (50 rows, latest per lease_id)
- `<catalog>.<schema>.ref_d11_silver_gl_accounts` (15 rows)
- `<catalog>.<schema>.ref_d11_silver_gl_transactions` (~2,680 rows, malformed fiscal_period dropped by expectation)
- `<catalog>.<schema>.ref_d11_silver_quarterly_targets` (80 rows)

**Gold layer** (certified facts):
- `<catalog>.<schema>.ref_d11_gold_property_quarterly` (80 rows = 8 properties × 10 quarters, materialized view with expectations)

### Test & Verification

| Name | Type | Path | Status |
|------|------|------|--------|
| check_ref_pipeline.py | Test | `code/tests/check_ref_pipeline.py` | ✓ Created, ready to run |

Verification checks:
1. Row count: `ref_d11_gold_property_quarterly` = 80 rows (oracle)
2. Numeric columns: all within 0.01 tolerance
3. Bronze row counts: baseline (loaded via Auto Loader)
4. Silver row counts: after filters/dedup
5. Expectation metrics: malformed fiscal_period rows dropped

### Demo Infrastructure

| Name | Type | Path | Status |
|------|------|------|--------|
| Bad batch CSV | Reference | `code/reference/d11_bad_batch/gl_transactions_late_batch.csv` | ✓ Created |
| Inject script | Script | `code/scripts/d11_inject_bad_batch.sh` | ✓ Created, executable |
| Remove script | Script | `code/scripts/d11_remove_bad_batch.sh` | ✓ Created, executable |
| Meter data (D15 Track C) | Reference | `code/reference/d15/utility_meter_readings.csv` | ✓ Created |

### Prompts & Documentation

| Name | Type | Path | Stages | Status |
|------|------|------|--------|--------|
| d11-lakeflow.md | Genie Prompt | `code/prompts/d11-lakeflow.md` | 7 + wrap-up | ✓ Created |
| d15-track-c-data-engineer.md | Genie Prompt | `code/prompts/d15-track-c-data-engineer.md` | 5 + wrap-up | ✓ Created |

D11 stages:
1. Set up the pipeline (5 min)
2. Bronze layer — Auto Loader ingestion (10 min)
3. Silver layer — Cleansing and deduplication (8 min)
4. Gold layer with expectations (12 min)
5. Run the pipeline (5 min)
6. Diagnose a failed expectation (15 min, optional)
7. Verify your pipeline matches the oracle (5 min)

D15 Track C stages (mini pipeline end-to-end):
1. Create a small source dataset (5 min)
2. Create a Lakeflow pipeline for meter data (20 min)
3. Create a Lakeflow Job with schedule (12 min)
4. Set up a quality alert (10 min)
5. Test end-to-end (10 min)

---

## Implementation Details

### Pipeline Architecture

**File:** `code/pipelines/ref_property_pipeline/dlt_pipeline.sql`

- **Format:** Spark Declarative Pipelines (DLT SQL)
- **Bronze:** Streaming tables via `cloud_files()` with Auto Loader for incremental ingestion
- **Silver:** Typed, cast, filtered, deduplicated (leases by latest `updated_at` using QUALIFY ROW_NUMBER)
- **Gold:** Materialized view with aggregations, window functions (LAG for QoQ), and expectations
- **Expectations:** Two in gold:
  1. `revenue_not_null`: "revenue IS NOT NULL"
  2. `valid_fiscal_quarter`: "fiscal_quarter RLIKE '^[0-9]{4}-Q[1-4]$'"
  - Violation mode: `ON VIOLATION DROP ROW` (silent drop; stage 6 allows `FAIL UPDATE` to diagnose)
- **Prefix:** All tables prefixed `ref_d11_` to avoid collisions with starting-state tables

### Bundle Integration

**File:** `code/resources/lakeflow_ref.yml`

```yaml
resources:
  pipelines:
    ref_property_pipeline:
      name: "Revantage Property Pipeline (Reference)"
      catalog: ${var.catalog}
      schema: ${resources.schemas.demo_schema.name}
      serverless: true
      photon: true
      channel: CURRENT
      continuous: false
      libraries:
        - file:
            path: ../pipelines/ref_property_pipeline/dlt_pipeline.sql
```

**Deploy:**
```bash
cd code
databricks bundle deploy -t dev      # deploys pipeline definition
databricks bundle run ref_property_pipeline -t dev  # triggers first run
```

### Failure Injection for Stage 6 Diagnosis

**Files:**
- `code/reference/d11_bad_batch/gl_transactions_late_batch.csv` — CSV with malformed fiscal_period entries (e.g., `2026Q3` instead of `2026-Q3`)
- `code/scripts/d11_inject_bad_batch.sh` — injects the bad batch into the raw volume
- `code/scripts/d11_remove_bad_batch.sh` — removes it after testing

**Usage:**
```bash
# Inject bad batch
./code/scripts/d11_inject_bad_batch.sh <profile> <catalog> <schema>

# Run pipeline — will see expectation violations in event log
# Participants diagnose the issue and fix it

# Clean up
./code/scripts/d11_remove_bad_batch.sh <profile> <catalog> <schema>
```

### Test Verification

**File:** `code/tests/check_ref_pipeline.py`

Comprehensive test that:
1. Verifies row counts (ref vs oracle)
2. Checks numeric columns within 0.01 tolerance
3. Reports bronze, silver, and gold row counts
4. Confirms expectation metrics (malformed rows dropped)

**Run:**
```bash
python -I code/tests/check_ref_pipeline.py \
  --profile fevm-thhart-october-2026 \
  --warehouse 0fb3aaac7c7d373c \
  --catalog thhart_october_2026_catalog \
  --schema revantage_20261008
```

---

## Prompt Files

### D11: `code/prompts/d11-lakeflow.md`

**Genie Code prompts** for participants to build bronze-silver-gold pipeline:
- Stage 1: Create pipeline in Lakeflow Designer
- Stage 2: Bronze layer with Auto Loader (7 streaming tables)
- Stage 3: Silver layer with cleansing/dedup (7 tables)
- Stage 4: Gold layer with expectations (materialized view, 80 rows)
- Stage 5: Run pipeline and monitor
- Stage 6: Diagnose failed expectation (optional, with failure injection)
- Stage 7: Verify against oracle

Each stage includes:
- **Prompt:** Exact text to paste into Genie Code
- **Expected:** What should appear (with planted numbers)
- **Checkpoint:** Query or click to verify
- **If stuck:** Recovery steps

**Snowflake comparison:** Tasks + Streams vs Lakeflow pipelines + jobs

**Verification:** [TBD] Mark as VERIFIED after running on live workspace

### D15 Track C: `code/prompts/d15-track-c-data-engineer.md`

**Hands-on lab for data engineers** — mini end-to-end pipeline:
- Source: Utility meter readings (electricity, water, gas)
- Tasks:
  - Bronze: ingest CSV via Auto Loader
  - Silver: cleanse, enrich (join to properties, calculate deltas)
  - Gold: daily aggregates with expectations
  - Schedule: Lakeflow Job running daily at 6 AM UTC
  - Alert: SQL alert for consumption spikes >50%

Reference data: `code/reference/d15/utility_meter_readings.csv` (40 rows, 8 properties, 5 days)

---

## Known Issues & Verification Status

### VERIFIED

- [x] Bundle syntax validates (`databricks bundle validate -t dev`)
- [x] Resource YAML correct format (file: path, no clusters/spark_version for serverless, no invalid permission levels)
- [x] Pipeline SQL compiles (no syntax errors visible)
- [x] DLT table definitions use correct syntax (CREATE STREAMING LIVE TABLE, CREATE LIVE TABLE, EXPECT(), ON VIOLATION DROP ROW)
- [x] Prefix `ref_d11_` applied to all tables
- [x] Injection/removal scripts created and marked executable
- [x] Prompts follow format from `code/prompts/README.md`
- [x] Track C data reference created

### UNVERIFIED (Requires Workspace Deployment)

- [ ] Pipeline deploys and runs successfully (`databricks bundle run`)
- [ ] Bronze tables created with correct row counts (~2,700 GL transactions, 52 leases, etc.)
- [ ] Silver tables drop/filter correctly (8 properties not 10, malformed fiscal_period dropped)
- [ ] Gold table produces exactly 80 rows matching oracle `gold_property_quarterly`
- [ ] Numeric columns within 0.01 tolerance
- [ ] Expectations captured in event log (violations recorded)
- [ ] Expectation failure mode: `ON VIOLATION DROP ROW` silently drops 3 malformed rows
- [ ] Injection scripts work: bad batch copied to raw volume, pipeline fails with `ON VIOLATION FAIL UPDATE`
- [ ] Removal scripts work: bad batch removed, pipeline succeeds
- [ ] Verification test `check_ref_pipeline.py` passes
- [ ] Genie Code prompts execute as written and produce expected results
- [ ] Prompt checkpoints pass
- [ ] Snowflake equivalent notes are accurate

---

## Next Steps (for Orchestrator / D11 Owner)

1. **Deploy pipeline:**
   ```bash
   cd code
   databricks bundle deploy -t dev
   databricks bundle run ref_property_pipeline -t dev
   ```

2. **Run verification test:**
   ```bash
   python -I code/tests/check_ref_pipeline.py \
     --profile fevm-thhart-october-2026 \
     --warehouse 0fb3aaac7c7d373c \
     --catalog thhart_october_2026_catalog \
     --schema revantage_20261008
   ```

3. **Test failure mode:**
   - Run `code/scripts/d11_inject_bad_batch.sh <profile> <catalog> <schema>`
   - Verify pipeline drops 3 rows by expectation
   - Run `code/scripts/d11_remove_bad_batch.sh <profile> <catalog> <schema>`
   - Verify pipeline returns to 80 rows

4. **Record verification:**
   - Create `code/prompts/verification/d11.md` with:
     - Row counts per layer
     - Expectation metrics from event log
     - Failure-loop transcript
     - Query results for oracle comparison

5. **Prompts refinement:**
   - Run D11 prompts in Genie Code and record actual results
   - Adjust checkpoints/expected values if needed
   - Mark VERIFIED in prompt file

---

## RUNBOOK Steps (for inclusion in main RUNBOOK.md)

### Demo 11 Setup & Run

**Prerequisites:**
- `code/resources/lakeflow_ref.yml` and `code/pipelines/ref_property_pipeline/dlt_pipeline.sql` deployed
- Raw CSVs in `/Volumes/<catalog>/<schema>/raw/` (via setup job)

**Steps:**

1. Deploy the pipeline:
   ```bash
   cd code
   databricks bundle deploy -t dev
   ```

2. Run the pipeline:
   ```bash
   databricks bundle run ref_property_pipeline -t dev
   ```

3. Monitor the run:
   - Open Lakeflow → Pipelines → "Revantage Property Pipeline (Reference)"
   - Check DAG, row counts, expectations in event log
   - Verify all 14 tables created with correct row counts

4. Verify against oracle:
   ```bash
   python -I code/tests/check_ref_pipeline.py \
     --profile fevm-thhart-october-2026 \
     --warehouse 0fb3aaac7c7d373c \
     --catalog thhart_october_2026_catalog \
     --schema revantage_20261008
   ```

5. Test expectation failure (optional):
   ```bash
   ./code/scripts/d11_inject_bad_batch.sh fevm-thhart-october-2026 thhart_october_2026_catalog revantage_20261008
   ```
   - Rerun pipeline
   - Verify expectation violations in event log
   - Edit pipeline: change `ON VIOLATION DROP ROW` to `ON VIOLATION FAIL UPDATE` and rerun
   - See failure message
   - Revert and clean up:
   ```bash
   ./code/scripts/d11_remove_bad_batch.sh fevm-thhart-october-2026 thhart_october_2026_catalog revantage_20261008
   ```

### Teardown

```bash
databricks bundle destroy -t dev  # removes pipeline and all tables
```

---

## Blockers & Known Gotchas

None at this time. All code created and validated against bundle schema. Deployment and runtime behavior require workspace testing.

---

## Files Summary

```
code/
├── pipelines/
│   └── ref_property_pipeline/
│       └── dlt_pipeline.sql              (DLT table definitions, 200+ lines)
├── resources/
│   └── lakeflow_ref.yml                  (bundle pipeline resource)
├── prompts/
│   ├── d11-lakeflow.md                   (7 stages + wrap-up, ~350 lines)
│   └── d15-track-c-data-engineer.md      (5 stages + wrap-up, ~280 lines)
├── reference/
│   ├── d11_bad_batch/
│   │   └── gl_transactions_late_batch.csv  (4 rows with malformed fiscal_period)
│   └── d15/
│       └── utility_meter_readings.csv      (40 rows, meter readings)
├── scripts/
│   ├── d11_inject_bad_batch.sh             (injects bad batch to raw volume)
│   └── d11_remove_bad_batch.sh             (removes bad batch)
└── tests/
    └── check_ref_pipeline.py               (verification test, ~150 lines)
```

**Total additions:** 9 files, ~1,000 lines of code + tests + documentation.

---

**Created by:** lakeflow agent  
**Date:** 2026-10-08  
**Time:** ~1 hour  
**Status:** Ready for deployment & verification testing
