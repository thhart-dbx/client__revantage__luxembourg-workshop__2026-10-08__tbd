# Handoff: Demo 12 "Approval workflow state machine" (Lakebase + Invoice Approvals App)

**Built by:** Isaac (lakebase-approvals area)  
**Date:** 2026-10-08  
**Status:** Code complete, awaiting bundle validation and runtime verification

---

## What Was Built

### 1. Lakebase Infrastructure

**Location:** `code/resources/lakebase_approvals.yml.wip`  
**Status:** Waiting for bundle validation

- **Database instance:** `revantage-lux-ops` (CU_1, 7-day retention)
- **Setup jobs:**
  - `d12_setup_lakebase`: Creates tables and indexes in Lakebase Postgres
  - `d12_seed_lakebase`: Seeds 5 Pending invoices

**SQL DDL:** `code/lakebase/d12_invoice_approvals.sql`
- Table: `invoice_approvals` (invoice_id PK, vendor_name, property_name, total_amount, currency, status, reviewed_by, reviewed_at, notes, first_approver_email, first_approved_at, requires_second_approval)
- Table: `approval_events` (audit trail: event_id, invoice_id, event_type, approver_email, event_timestamp, notes)

**Seed data:** `code/lakebase/d12_seed_invoices.sql` (5 Pending invoices)
- HV-2026-0417: USD 339,600 (requires two approvers — over EUR/USD 50k threshold)
- PE-2026-06-0088: USD 41,000
- TM-POL-2026-3391: GBP 55,272
- ACD-2026-IF-55120: EUR 27,826.50
- NGD-26-1184: EUR 20,416.50

**Reset script:** `code/lakebase/d12_reset.sql` (restores 5 Pending invoices after demo)

### 2. Next.js Invoice Approvals App

**Location:** `code/app-approvals/`

**Components:**
- **Main page:** `src/app/page.tsx` — Queue of Pending invoices, detail panel, approve/reject workflow
- **Invoice list:** `src/components/invoice-list.tsx` — Responsive list with status icons, amount formatting
- **Invoice detail:** `src/components/invoice-detail.tsx` — Detail panel, approval form, two-step approval warning
- **Lakebase lib:** `src/lib/lakebase.ts` — Connection + CRUD operations (TODO: replace mock with actual Postgres)
- **API routes:**
  - `src/app/api/invoices/route.ts` — GET invoices (with status filter)
  - `src/app/api/invoices/approve/route.ts` — POST approve (handles first/second approval)
  - `src/app/api/invoices/reject/route.ts` — POST reject

**Key features:**
- Displays all Pending invoices in a queue
- Click to show detail panel
- Approve/Reject with mandatory notes
- Two-step approval workflow:
  - High-value invoices (USD > 50k or EUR > 50k) require two distinct approvers
  - First approver: sets `first_approver_email`, `first_approved_at`
  - Second approver: sets `reviewed_by`, `reviewed_at`, status = Approved
- Logs all actions to audit trail
- User email captured from `x-forwarded-email` header

**App configuration:** `app.yaml`
- Exposes Lakebase connection details as environment variables
- References SQL warehouse for backup data access

**Status:** UNVERIFIED — Mock implementation for local testing; requires actual Lakebase Postgres connection on deployment.

### 3. Lakeflow Job: Approved → Silver

**Location:** `code/jobs/d12_approved_to_silver.py`  
**Bundle config:** `code/resources/lakebase_approvals.yml.wip` (job: `d12_approved_to_silver`)

**What it does:**
1. Reads Approved invoices from Lakebase `revantage_ops.invoice_approvals` WHERE status = 'Approved'
2. MERGE into Delta `silver_invoices` (upsert by invoice_id)
3. Columns: invoice_id, vendor_name, property_name, total_amount, currency, extracted_at, reviewed_by, reviewed_at, notes, loaded_at

**Job settings:**
- Max retries: 2
- Retry interval: 60 seconds
- Failure notification: thomas.hart@databricks.com
- Trigger: Currently configured on schedule (1 hour); can be switched to table-update trigger after verification

**Status:** UNVERIFIED — Code written; requires Lakebase connectivity and warehouse access to test.

### 4. Playwright E2E Tests

**Location:** `code/app-approvals/e2e/approvals.spec.ts`

**Test cases:**
1. Display pending invoices
2. Approve single-approval invoice (PE-2026-06-0088)
3. Reject invoice (NGD-26-1184)
4. Two-step approval for high-value (HV-2026-0417)
5. Notes required validation
6. Property information display

**Run locally:**
```bash
cd code/app-approvals
npm run dev &
npx playwright test
```

**Run against deployed app:**
```bash
BASE_URL=$(databricks apps get revantage-invoice-approvals --profile fevm-thhart-october-2026 -o json | python3 -c "import sys,json;print(json.load(sys.stdin)['url'])") \
npx playwright test
```

**Status:** UNVERIFIED — Tests written but require deployed app and Lakebase connectivity.

### 5. Prompt & Verification Files

**Prompt file:** `code/prompts/d12-lakebase.md`
- 8 stages: create Lakebase project → tables → seed → app → job → tests → E2E → reverse ETL (optional)
- Each stage has checkpoint queries, expected results, "if stuck" recovery
- Time box: 45 minutes for participants

**Verification file:** `code/prompts/verification/d12.md`
- Checkpoint queries for each stage
- Status: Most stages marked UNVERIFIED pending deployment
- Blockers: Lakebase connection credentials, Postgres library integration, trigger configuration

---

## Next Steps

### For orchestrator / deployer:

1. **Validate resource file:**
   ```bash
   mv code/resources/lakebase_approvals.yml.wip code/resources/lakebase_approvals.yml
   databricks bundle validate -t dev
   ```

2. **Deploy bundle:**
   ```bash
   cd code && databricks bundle deploy -t dev
   ```

3. **Run setup jobs:**
   ```bash
   databricks bundle run d12_setup_lakebase -t dev
   ```

4. **Local app test:**
   ```bash
   cd code/app-approvals
   npm run dev
   # Open http://localhost:3000
   ```

5. **Run Playwright tests:**
   ```bash
   # Local:
   npx playwright test
   
   # Deployed:
   BASE_URL=<app-url> npx playwright test
   ```

6. **Trigger ETL job:**
   ```bash
   # After approving invoices via app:
   databricks bundle run d12_approved_to_silver -t dev
   ```

7. **Verify results:**
   ```sql
   -- In Lakebase:
   SELECT COUNT(*) FROM revantage_ops.invoice_approvals WHERE status = 'Pending';
   
   -- In Delta:
   SELECT COUNT(*) FROM <catalog>.<schema>.silver_invoices;
   ```

### Known issues to resolve:

| Issue | Details | Resolution |
|---|---|---|
| **Lakebase Postgres connection** | `src/lib/lakebase.ts` currently uses mock data for local testing | On deployment, implement actual psycopg connection with OAuth token from Databricks Apps |
| **App SP permissions** | App needs MODIFY on silver_invoices (for INSERT) + READ on Lakebase | Add to `code/resources/schema.yml` grants block |
| **Environment variables** | `LAKEBASE_HOST` hardcoded in `app.yaml` | Make it a bundle variable if migrating to another workspace |
| **Job trigger** | Currently on 1-hour schedule | Can switch to table-update trigger; need to create `invoice_approval_events` Delta table written by the app on every status change |
| **Reverse ETL** | Stage 8 (optional) synced table not yet implemented | Can create post-demo or mark as "if time" |

---

## Files Created / Modified

### New files:

```
code/lakebase/
  d12_invoice_approvals.sql       — DDL for invoice_approvals + approval_events
  d12_seed_invoices.sql           — INSERT 5 Pending invoices
  d12_reset.sql                   — Reset to 5 Pending (for teardown)

code/jobs/
  d12_setup_lakebase.py           — Create tables + indexes in Lakebase
  d12_seed_lakebase.py            — Seed 5 invoices
  d12_approved_to_silver.py       — Read Approved from Lakebase, merge to Delta

code/app-approvals/src/
  lib/lakebase.ts                 — Postgres connection (mock + TODO for real Postgres)
  app/page.tsx                    — Main invoice queue
  components/invoice-list.tsx     — Invoice list component
  components/invoice-detail.tsx   — Invoice detail + approval form
  app/api/invoices/route.ts       — GET /api/invoices
  app/api/invoices/approve/route.ts — POST approve
  app/api/invoices/reject/route.ts  — POST reject

code/app-approvals/e2e/
  approvals.spec.ts               — Playwright E2E tests

code/prompts/
  d12-lakebase.md                 — 8-stage prompt library
  verification/d12.md             — Verification checkpoint queries

code/resources/
  lakebase_approvals.yml.wip      — Bundle resources (awaiting validation)
```

### Modified files:

```
code/app-approvals/
  app.yaml                        — Added LAKEBASE_* environment variables
```

---

## Data & Numbers

**Seeded invoices (5 Pending):**
- Total value: ~USD 520,000 (339,600 USD + 41,000 USD + 55,272 GBP ≈ 58k USD + 27,826.50 EUR ≈ 30k USD + 20,416.50 EUR ≈ 22k USD)
- High-value (2 approvals required): HV-2026-0417 (USD 339,600)
- Currencies: USD (2), GBP (1), EUR (2)
- Properties: Harbor Tower (3), Luxembourg City Office (2)

**Approval workflow:**
- Single-step: 4 invoices (PE, TM, ACD, NGD)
- Two-step: 1 invoice (HV)

**Job trigger:**
- Current: 1-hour schedule (can change to table-update after initial verification)
- Retries: 2, interval: 60 sec
- Failure notification: thomas.hart@databricks.com

---

## Testing status

| Component | Local | Deployed | Status |
|---|---|---|---|
| Lakebase tables | — | — | UNVERIFIED (job not run yet) |
| App UI | Mock data | — | UNVERIFIED (needs Lakebase conn) |
| App API routes | Mock data | — | UNVERIFIED |
| ETL job | — | — | UNVERIFIED (needs deployed app + approvals) |
| Playwright tests | Skipped (mock) | — | UNVERIFIED |
| E2E workflow | — | — | UNVERIFIED |

---

## Handoff expectations

- **Lakebase resource file** renamed from `.wip` → `.yml` after `bundle validate` succeeds
- **Setup jobs** run successfully, creating tables and seeding 5 Pending invoices
- **App** builds and starts locally; can fetch mock invoices
- **Playwright tests** pass against local dev and deployed app
- **ETL job** runs successfully after approvals; verified rows in silver_invoices
- **Verification queries** run and results recorded in `code/prompts/verification/d12.md`
- **Reset script** tested — clears state for next workshop run

---

**Contact for questions:** Isaac (lakebase-approvals area builder)
