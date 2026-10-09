# Demo 4: Extraction Agent — "Invoice-to-Table"

**Session:** Day 1, 11:00–11:45 (45 min) · **You build:** an Information Extraction agent over the invoices + a Delta table of extracted fields · **Reference:** agent `extract-invoices-2026-10-08-15-39-15` ("Invoice Extractor (Reference)"), table `<catalog>.<schema>.ref_invoices_extracted`
**Starting state:** 8 invoice PDFs in `/Volumes/<catalog>/<schema>/documents/invoices/` (5 vendors' layouts, EUR ×5, USD ×2, GBP ×1); ground truth `code/documents/out/invoices_ground_truth.json`
**Where:** left nav **Agents** → **Create Agent** → **Information Extraction**; then the SQL editor

**Timing reality (measured 2026-10-08):** clicks take ~3 minutes; file parsing + schema generation ~6 minutes;
the first extraction ~2 minutes. Plan ~12 minutes wall-clock from "Create" to results. Start it, then
talk through the platform story while it parses. The agenda's "3–4 minutes" is the clicking, not the waiting.

## Stage 1: Create and point at the documents (3 min)
**Agents → Create Agent → Information Extraction → Select volume**. Choose **All volumes**, search
`documents`, click the volume, then expand it and click **invoices** (the breadcrumb must end in
`/documents/invoices`) → **Select**.

**Expected:** "Processing 5 files…"; the build view samples 5 of the 8 invoices.
**If stuck:** if expanding the volume shows "Request access", wait a few seconds and expand again: the folder list loads late.
Don't select the volume root, or the policies and leases get sampled too.

## Stage 2: Describe what to extract (3 min)
**Prompt** (the "Describe what you want to extract" box):
> Extract from each vendor invoice: vendor_name, invoice_number, invoice_date, due_date, line_items (an array where each item has description, quantity, unit_price, amount), subtotal, tax, total, and currency (ISO code like EUR, USD, GBP). Dates as YYYY-MM-DD. Amounts as numbers without currency symbols.

Click **Generate schema**.
**Expected:** the 9 fields, with `line_items` as `array[obj]` of 4 sub-fields.
**Checkpoint (important):** open `line_items › quantity`. Genie generates **integer**; change it to **Number**.
The legal invoice bills 4.5 / 2.5 / 1.5 hours, and integer would truncate them.

## Stage 3: Run and review (5 min)
Click **Run extraction**. Click each file to see the PDF next to the JSON.
**Expected (Coastal Climate Systems, HV-2026-0417):** total **339600**, currency **USD**, 4 line items (chiller 214,500; crane 38,900; installation 61,200; commissioning 25,000), tax null.
Also check the bilingual Luxembourg tax notice (ACD-2026-IF-55120, €27,826.50) and the UK insurance statement (£55,272 incl. 12% IPT).

## Stage 4: Use the agent in production (5 min)
Click **Use Agent**. Show the five paths: **Run in SQL**, Run in Notebook, REST API, **Create a Lakeflow Job**, **Create a Spark Declarative Pipeline**.
Click **Run in SQL → Start extraction**. A SQL editor tab opens with the generated query:
`read_files(..., format => 'binaryFile')` → `ai_parse_document(content, map('version','2.0'))` → `ai_extract(parsed, '<json schema>', options => map('version','2.0'))`.

**Prompt** (Genie Code, in that SQL editor tab):
> Explain this query step by step, then wrap it in CREATE OR REPLACE TABLE <my_schema>.invoices_extracted so the results are saved as a Delta table.

**Expected:** a CTAS over the same query; 8 rows; `response` is a VARIANT with `response.response.<field>`.
**Checkpoint:** `SELECT response:response.invoice_number::string, response:response.total::double FROM <my_schema>.invoices_extracted` → 8 rows incl. `HV-2026-0417 | 339600`.
**If stuck:** run `code/reference/d04_extract_invoices.sql` (the captured agent SQL as a CTAS).

## Stage 5: Reconcile to the GL (6 min)
**Prompt** (Genie Code):
> Join the extracted invoices to <catalog>.<schema>.silver_gl_transactions where the GL description starts with the invoice number, and show invoice total, currency, GL amount in EUR, and the GL account name and category.

**Expected:** HV-2026-0417: USD 339,600 ↔ **€312,390.76** booked to **Repairs & Maintenance (OpEx)**. The others don't
match by invoice number (the GL has monthly accruals). Hold that thought: in Demo 5 the policy says this chiller is **CapEx**.

## Stage 6: Into a pipeline (3 min, show)
Back in the agent: **Use Agent → Create a Spark Declarative Pipeline**. Show that new PDFs dropped into the volume
are extracted incrementally on schedule. Don't run it in the room; it's the production path.

## Wrap-up
- **So what:** an analyst built an invoice extractor without code, verified it against the PDFs, and got production SQL, a job, or a pipeline from the same agent.
- **Snowflake equivalent:** Document AI (model building + `!PREDICT`). On Databricks it's ai_parse_document + ai_extract in SQL, governed in Unity Catalog, with one-click pipelines.
- **Verified:** 2026-10-08 in the browser on the FEVM workspace: agent built from the invoices folder; the reference CTAS over all 8 invoices scored **72/72 fields (100%)** vs ground truth (`code/reference/d04_score_extraction.py`); the GL reconciliation returned the €312,390.76 R&M posting. **Stages 4–5 run in the Genie Code UI (S9)** in the agent's *Run in SQL* tab: S4 explained read_files → ai_parse_document → ai_extract step by step, wrapped it in a CTAS, 8 rows incl. HV-2026-0417 339,600 (it called that "€339,600"; the invoice is USD: point at the currency column); S5 the join returned exactly HV-2026-0417, USD 339,600 ↔ €312,390.76, Repairs & Maintenance (OpEx). Screenshots: `notes/agent-notes/screenshots/d04-*.png`.
