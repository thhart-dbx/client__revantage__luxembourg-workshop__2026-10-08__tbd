# Demo 9: Databricks Apps — "Lease Expiry Tracker"

**Session:** Day 1, 3:30–4:15 (45 min) · **You build:** a lease-expiry quick tool as a Databricks App · **Reference:** app `revantage-lease-tracker` (Next.js + TypeScript, `code/app/`)
**Starting state:** `silver_leases` (50), `silver_tenants` (40), `silver_properties` (8); a SQL warehouse; the reference app deployed and shared
**Where:** Apps (new Apps UI: **New → App**), the app's source folder in the workspace with Genie Code

Expected numbers (live, from `current_date()`; as of 2026-10-13 the planted windows are 4 expired · 6 ≤ 90 d · 8 more ≤ 180 d · 10 more ≤ 365 d):
on 2026-10-08 the reference app shows **6 / 14 / 23** leases in the 90 / 180 / 365-day windows and 50 incl. expired; 90-day monthly rent at risk **€103k**.

## Stage 1: Start from a template (5 min)
**New → App → Install from templates → Hello world → Streamlit**. Name `lease-tracker-<your_name>`, Create. Wait for **Running** (~2–3 min), open it.
The hello-world create flow only asks for compute, so add the warehouse afterwards: app page → **Edit → App resources → Add resource → SQL warehouse** (Can use), resource key **`sql-warehouse`**, Save.
**Checkpoint:** the template renders. Open **Edit in workspace** to see the source folder.

## Stage 2: Query the leases (10 min)
Open the app's main file (e.g. `app.py`) and Genie Code:
> The app has a SQL warehouse resource named sql-warehouse; in app.yaml read it into DATABRICKS_WAREHOUSE_ID with valueFrom: sql-warehouse (no resources block in app.yaml). Change this app to query <catalog>.<schema>.silver_leases joined to silver_tenants and silver_properties through that warehouse, and show property, tenant, lease end, monthly rent, and days remaining (datediff from current_date) for leases ending in the next 90 days, sorted by days remaining.

**Expected:** a table with 6 rows (today), earliest Harbor Tower / Willow Partners (11 days on 9 Oct; the count is from `current_date`).
**Watch for (seen in pre-build):** without the first sentence Genie Code wrote `valueFrom: resources.sql_warehouse.id` plus a `resources:` block in app.yaml; the app deployed but showed "No SQL warehouse configured". One follow-up naming `sql-warehouse` fixed it.
**Checkpoint:** redeploy (**Deploy**) and refresh. Grant your app's service principal `USE CATALOG` + `USE SCHEMA` + `SELECT` if it errors with permission denied (the facilitator can run it for everyone).
**If stuck:** open the reference app and compare its query: `code/app/src/app/api/leases/route.ts`.

## Stage 3: Filters and risk (10 min)
> Add filters for expiry window (90 / 180 / 365 days / all including expired), region, and property type, and a risk column: High if within 90 days and not 'Pending Renewal' or the tenant's credit rating is below BB; Medium if within 180 days; otherwise Low.

**Expected:** 180-day window → 14 rows; Southeast filter shows Peachtree Center and Harbor Tower leases.
Watch for: the forward windows must exclude leases that have already expired (the reference app had this bug in pre-build).

## Stage 4: Summary cards and export (8 min)
> Add summary cards at the top: number of leases expiring in the window, monthly and annualised rent at risk in EUR, and the average credit rating of the tenants. Add a button that downloads the filtered table as CSV.

**Expected (90 days):** 6 leases · €103k / month · €1.2M / year · average rating BBB (Genie Code's version showed **BBB+**: it rounds the averaged rating scale differently; either is fine, discuss the method).

## Stage 5: Share it like a Google Doc (5 min)
App page → **Permissions** → add `revantage_consumers` (Can use). Send the URL. Viewers sign in with their
Databricks identity; the app reads data as its service principal (or, with on-behalf-of-user auth enabled, as the viewer, so UC row filters and masks apply).
Show where the app is listed for business users: the app list and Genie One's **Discover** page (facilitator show-item: check it in the Revantage workspace pre-flight).

## Stage 6: Talk track (7 min)
- **When an app instead of a dashboard:** workflows (sort, flag, export, write back). Demo 12 adds approve/reject writes on Lakebase.
- **Embedding Genie and agents:** apps can call a Genie Agent (Conversation API) or the Knowledge Assistant endpoint (Demo 5), or use Databricks-managed MCP servers for Genie, UC functions, and vector search.
- **Row Zero / spreadsheet-style analytics:** UNVERIFIED in the Databricks context. Confirm with the account team before mentioning it. Don't present it as a Databricks feature without confirmation.
- **No per-seat cost:** apps bill compute (shown on the create page: Medium ≈ 0.5 DBU/hour), not users.

## Wrap-up
- **So what:** an always-current lease tool on governed data, shared with a link, with no separate hosting stack and no per-seat licences.
- **Verified:** 2026-10-08 on the FEVM workspace: reference app deployed (`databricks bundle run demo_app`), 27 Playwright tests pass locally (filters, sort, cards, export, live-data match, no-expired-in-window); deployed API returns 6 / 14 / 23 / 50 for the four windows, checked in the browser (`notes/agent-notes/screenshots/d09-app.png`). **Template → Genie Code path (Stages 1–4) run in the UI (S9)** on a scratch Streamlit app (deleted afterwards, grants revoked): S1 Running in ~3 min; S2 6 rows after the warehouse-wiring follow-up (now in the prompt); S3 filters + risk, 90 d → 6 (4 High), 180 d → 14, expired excluded from forward windows; S4 cards 6 · €103,046.05 · €1,236,552.60 · BBB+ and a working Download CSV button. Screenshots `s9-d09-template-app*.png`.
