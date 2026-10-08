# Demo 12: Lakebase & Production Operations — "Approval workflow state machine"

**Session:** Day 2, 10:45–11:30 (45 min) · **You build:** an approval table in Lakebase, approvals through an app, and a job that loads only approved invoices to Delta · **Reference:** Lakebase instance `revantage-lux-ops` (db `revantage_ops`, schema `approvals`), app `revantage-invoice-approvals`, job "[Revantage workshop] Approved invoices -> silver (Reference)", Delta `silver_invoices`, synced table `ref_d12_gold_property_quarterly_synced`
**Starting state:** 5 Pending invoices in `approvals.invoice_approvals` (from Demo 4's extraction; HV-2026-0417 €312,391 and TM-POL-2026-3391 €64,730 need two approvers); `silver_invoices` empty
**Where:** Compute → Lakebase Postgres; SQL editor connected to Lakebase; the Invoice Approvals app; Jobs & Pipelines

## Stage 1: Why Lakebase (5 min, talk)
A dashboard can show invoices; it can't hold *who approved what, when*, enforce two signatures, or stop unapproved rows reaching the GL.
That's transactional state: row-level updates, constraints, millisecond reads. Lakebase is managed Postgres next to the lakehouse; analytical data stays in Delta.

## Stage 2: Create the database objects (10 min)
Open **Compute → Lakebase Postgres → revantage-lux-ops → New query** (or your own instance: **Create database instance**, CU_1; ~5 min to provision).
**Prompt** (Genie Code / Lakebase SQL editor):
> Create a Postgres schema approvals with a table invoice_approvals (invoice_id primary key, vendor_name, property_name, total_amount, currency, total_eur, status Pending/Approved/Rejected with a check constraint, first_approver, first_approved_at, reviewed_by, reviewed_at, notes, and a generated column requires_two_approvers = total_eur > 50000) and an audit table approval_events. The final approver must differ from the first approver.

**Expected:** DDL like `code/lakebase/d12_invoice_approvals.sql` (generated column + CHECK constraint).
**Checkpoint:** insert the 5 invoices (`code/lakebase/d12_reset.sql`), then
`SELECT invoice_id, total_eur, requires_two_approvers FROM approvals.invoice_approvals ORDER BY total_eur DESC` → HV-2026-0417 and TM-POL-2026-3391 are `true`.

## Stage 3: Approve in the app (10 min)
Open **Invoice Approvals** (the reference app). Everyone signs in with their own identity.
- Approve **PE-2026-06-0088** (€37.7k) with a note → *Invoice approved.*
- Approve **HV-2026-0417** (€312k) → *First approval recorded. Awaiting a second approver.* The panel shows "First approval: <you>".
- Try to approve HV-2026-0417 again yourself → **"The second approval must come from a different person (Expense Approval Policy)."**
- A second participant approves HV-2026-0417 → Approved.
**Checkpoint (Lakebase SQL):** `SELECT * FROM approvals.approval_events ORDER BY at` shows every action with the actor.
How it's wired: the app has a **database resource** (Lakebase) that injects PGHOST/PGUSER/PGDATABASE; its service principal logs in with an OAuth token; `code/app-approvals/src/lib/lakebase.ts` does each decision in a transaction with `SELECT … FOR UPDATE`.

## Stage 4: Only approved invoices reach the lakehouse (10 min)
Run the job **Approved invoices -> silver (Reference)** (Jobs & Pipelines → Run now).
**Expected:** `approved invoices in Lakebase: N`; `SELECT * FROM <catalog>.<schema>.silver_invoices` holds exactly the Approved ones. An invoice with only one signature isn't there.
Show on the job: **retries** (2, 60 s apart), **failure email**, **run history**, and the trigger (periodic 15 min, paused for the workshop).
**Prompt** (Genie Code, on the job's Python file):
> Explain how this job reads from Lakebase and why the MERGE makes re-runs safe.

Talk track on triggers: table-update ("data-readiness") triggers fire on Unity Catalog Delta tables, not on Postgres tables, so this job runs on a schedule or on demand. To trigger downstream work on approval, have the next job use a **table-update trigger on `silver_invoices`**.

## Stage 5: Reverse ETL (5 min)
**Catalog → `ref_d12_gold_property_quarterly_synced`**: a synced table copying certified gold into Postgres (snapshot mode).
**Checkpoint:** in Lakebase SQL, `SELECT count(*), sum(net_profit) FROM revantage_20261008.ref_d12_gold_property_quarterly_synced` → **80 rows, 64,214,088.70**, identical to gold. Apps read it in milliseconds without hitting a warehouse.

## Stage 6: Production health (5 min, show)
Pipeline and job health in one place: Jobs & Pipelines → runs, durations, failures; Demo 11's expectation metrics; Demo 16's data quality monitors and freshness.

## Reset (facilitator)
`uv run --with "psycopg[binary]" code/lakebase/lakebase_sql.py --profile <p> --instance revantage-lux-ops --db revantage_ops -f code/lakebase/d12_reset.sql` and `TRUNCATE TABLE <catalog>.<schema>.silver_invoices`.

## Wrap-up
- **So what:** the approval workflow from Demo 4's extraction to the GL has state, a two-signature rule, an audit trail, and a hard gate, all next to the governed lakehouse.
- **Snowflake equivalent:** Hybrid Tables / Unistore for operational rows. Lakebase is full Postgres (extensions, drivers, apps) with synced tables from Delta and branching.
- **Verified:** 2026-10-08 on the FEVM workspace. Local Playwright 5/5 against Lakebase (queue order, single approval, reject, two-approver rule, same-person 409). Deployed app in the browser: first approval recorded, same-person second approval rejected with 409, single approval OK. Job run SUCCESS: only the Approved invoice landed in `silver_invoices`. Synced table online, 80 rows, sums match gold. State reset afterwards. Genie Code prompts (Stages 2, 4): UI verification pending (S9).
