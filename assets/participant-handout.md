# Revantage workshop: participant handout

You build every asset yourself in **your own schema** (`<my_schema>`). For each step: type the prompt into Genie Code, compare with the checkpoint, and if you're stuck open the finished reference (objects named `ref_…` or titled "(Reference)").

| Placeholder | Means |
|---|---|
| `<catalog>.<schema>` | the shared workshop data (given by your facilitator) |
| `<my_schema>` | your sandbox schema |
| `:workspace_id` | the number after `?o=` in your browser URL |

**Tip:** end every prompt that creates something with *"run it and check the result"*.

## Demo 0: Getting Started — "Your own copy of the workshop"

**Session:** Day 1, 8:30–9:00 (30 min) · **You build:** a Git folder with the workshop repo, and your own copy of the workshop data in `<my_schema>` · **Reference:** the shared starting state in `<catalog>.<schema>` (same data, value for value)
**Where:** Settings (Linked accounts), Workspace (Git folder), notebook on serverless, Catalog Explorer, Genie Code side panel

### Stage 1: Link your GitHub account (5 min)

Profile (top right) → **Settings** → **Linked accounts** → **Git integration** → **Add Git credential** → Git provider **GitHub** → **Link Git account** and approve the Databricks app in GitHub (or choose **Personal access token** and paste a GitHub token with the `repo` scope).
**Checkpoint:** Git integration lists your GitHub user with **GitHub (Linked)**.
**If stuck:** the repo is private: check that your GitHub user has accepted the invitation to `thhart-dbx/client__revantage__luxembourg-workshop__2026-10-08__tbd` (github.com → your notifications).

### Stage 2: Create the Git folder (5 min)

**Workspace** → **Home** → **Create** → **Git folder**. Paste the Git repository URL `https://github.com/thhart-dbx/client__revantage__luxembourg-workshop__2026-10-08__tbd`: the provider (**GitHub**) and the Git folder name fill in by themselves → **Create Git folder**.
**Checkpoint:** the folder shows the branch **main** at the top and contains `README.md`, `RUNBOOK.md`, `assets/` and `code/`.
**If stuck:** "Repository not found" or "Invalid Git credentials" means the GitHub link (Stage 1) or the repo invitation is missing: fix that and create the Git folder again.

### Stage 3: Find your way around the repo (5 min)

Open `code/prompts/`: one guide per module (`d01-…` to `d18-…`), each with the prompts to type, the expected result and an "if stuck" fallback. `code/reference/` holds the answer-key SQL, `code/setup/` the data setup.
Open `code/setup/participant_setup`, then the Genie Code panel (top right):
> Explain what this notebook does, step by step, and which objects it will create.

**Expected:** Genie Code walks through the cells (your settings, your schema with the `raw` and `documents` volumes, `setup_starting_state.py` generating the CSVs, copying the PDFs and building bronze → silver → gold, the PASS/FAIL checks) and lists what it creates: **1 schema, 2 volumes, 24 tables** (16 starting tables + 8 for Module 17) and **22 files** (7 CSVs + 15 PDFs).

### Stage 4: Build your copy of the data (10 min)

In `participant_setup`, first code cell: type `CATALOG = "<catalog>"` and `SHARED_SCHEMA = "<schema>"` (the names shared at the start of the session); leave `MY_SCHEMA` blank (it becomes `<schema>_<your name>`) and `AS_OF` as is. Compute **Serverless** → **Run all**. (A banner "This file is part of a bundle" can be dismissed.)
**Expected:** after about 3 minutes, the last cell prints 8 **PASS** lines: gold 80 rows / 8 properties / 2024-Q1–2026-Q2, Southeast 2026-Q2 net profit ≈ €2.09M, 16 starting tables, 8 Module 17 legacy tables, 7 CSVs, 8 / 4 / 3 PDFs, and *"Done. In the module prompts, <my_schema> is …"*.
**If stuck:** `AssertionError: Type the catalog and shared schema names…`: the first code cell is still empty; type both names, keep the quotes. `PERMISSION_DENIED` on CREATE SCHEMA: your schema hasn't been created for you yet; ask for the sandbox job to be run, then **Run all** again (the notebook is safe to re-run). Until then, every module works on the shared data in `<catalog>.<schema>`.

### Stage 5: Check your copy (5 min)

**Catalog** → `<catalog>` → `<my_schema>`: the bronze, silver and gold tables, the `legacy_*` tables, and the volumes `raw` and `documents`.
**SQL Editor** → **+** → **Query** (a new, empty query), then open the Genie Code panel:
> Compare <my_schema>.gold_property_quarterly with <catalog>.<schema>.gold_property_quarterly: same number of rows, and how many rows differ? Run it and check the result.

**Expected:** Genie Code checks both schemas, writes the query into the editor, runs it and reports **80** rows in each and **0** rows that differ (a full outer join on `property_id` + `fiscal_quarter`, or `EXCEPT ALL`). Click **Reject** on the suggested edit if you don't want to keep the query. Your copy is the workshop data, value for value, so every expected result in the modules holds for it.
**If stuck:**
```sql
SELECT COUNT(*) AS differences FROM (
  SELECT * FROM <my_schema>.gold_property_quarterly
  EXCEPT ALL
  SELECT * FROM <catalog>.<schema>.gold_property_quarterly)
```

## Demo 1: Welcome & Platform Overview — "Where does my data live?"

**Session:** Day 1, 9:00–9:30 (30 min) · **You build:** your bearings: catalog, SQL editor, Genie Code · **Reference:** none (navigation)
**Where:** Catalog Explorer, SQL editor, Genie Code side panel

### Stage 1: Open platform, 3 minutes of talk

Delta/Iceberg in your own cloud storage (S3/ADLS/GCS); any model (Claude, GPT, open source, behind the AI Gateway); any data type (tables, PDFs, Excel). Unity Catalog governs all of it.

### Stage 2: The three-level namespace (7 min)

**Catalog** → `<catalog>` → `<schema>`: point out tables, views, metric views (later), volumes, functions.
Snowflake mapping: database ≈ catalog, schema = schema, stage ≈ volume, warehouse ≈ SQL warehouse.
**Checkpoint:** open `documents` → `invoices/` → preview `HV-2026-0417.pdf` in the browser.

### Stage 3: First query (5 min)

SQL editor, Serverless warehouse:
```sql
SELECT * FROM <catalog>.<schema>.gold_property_quarterly LIMIT 10;
SELECT COUNT(*) AS rows, COUNT(DISTINCT property_id) AS properties, MIN(fiscal_quarter), MAX(fiscal_quarter)
FROM <catalog>.<schema>.gold_property_quarterly;
```
**Expected:** **80** rows · **8** properties · 2024-Q1 · 2026-Q2.

### Stage 4: Meet Genie Code (10 min)

Open the Genie Code panel (top right):
> What tables are in <catalog>.<schema> and how do the bronze, silver and gold tables relate?

**Expected:** Genie Code explains raw → cleaned → aggregated and names `gold_property_quarterly` as the fact table.
> Write a query showing 2026-Q2 net profit by region from gold_property_quarterly.

**Expected:** Western Europe ≈ €2.69M, Northeast ≈ €1.59M, Southeast ≈ €2.09M.

### Stage 5: Any data type (5 min)

**Prompt:**
> Read the PDFs in /Volumes/<catalog>/<schema>/documents/leases/ with read_files as binaryFile and parse them with ai_parse_document.

**Expected:** 3 rows, ~20 elements each; the first element of `lease-harbor-tower-anchor.pdf` is **"EXPIRED"** (the anchor tenant who left on 31 March; we'll see the impact all day).
```sql
SELECT path, ai_parse_document(content, map('version','2.0')):document.elements[0].content::string AS first_element
FROM read_files('/Volumes/<catalog>/<schema>/documents/leases/', format => 'binaryFile')
```

## Demo 2: Genie One — Property Performance Q&A

**Session:** Day 1, 9:30–10:15 (45 min) · **You build:** five answered, shareable business questions · **Reference:** Genie Agent "Revantage Portfolio Q&A (Reference)"
**Where:** Genie One (browser), then the desktop/mobile app if installed

### Stage 1: Who missed target? (6 min)

**Prompt** (Genie One):
> Which properties missed their quarterly target in 2026-Q2?

**Expected:** 3 properties: Peachtree Center (−€71,293), Harbor Tower (−€43,235), Zuidas Residences (−€41,702).
**Checkpoint:** open *Show code*: `WHERE fiscal_quarter = '2026-Q2' AND met_target = false` on `gold_property_quarterly`.
**If stuck:** ask the same question in the Reference agent; it answers from the metric view `ref_mv_target_attainment`.

### Stage 2: What changed in the Southeast? (8 min)

**Prompt:**
> What changed from Q1 to Q2 for the Southeast region?

**Expected:** revenue down ~€267k (−6.4%), operating expense up ~€221k, net profit €2.58M → €2.09M (−18.6%).
Then follow up in the same thread:
> Which property drove that, and was it revenue or costs?

**Expected:** **Harbor Tower**, net profit −€507k: revenue −€321k (anchor tenant left on 31 March) and costs +€185k.
**Checkpoint:** Harbor Tower is the only Southeast property whose net profit fell.
**If stuck:** in the Reference agent, ask "Why did Southeast net profit drop in Q2?".

### Stage 3: Charts (6 min)

**Prompt:**
> Show me revenue by property type as a bar chart

**Expected:** bar chart for **2026-Q2** (the agent's default period): Office €4.69M, Multifamily €3.96M, Retail €2.10M. Add "across all quarters" for the totals: Office €46.7M, Multifamily €37.2M, Retail €19.7M. Ask
"Only for 2026-Q2" to refine; use the chart menu to switch type.

### Stage 4: Growth (5 min)

**Prompt:**
> Which market has the highest quarter-over-quarter net profit growth?

**Expected:** **Luxembourg City, +10.0%** (2026-Q2 vs Q1).
**Checkpoint:** *Show code* compares 2026-Q2 with 2026-Q1. The agent's instructions set that default;
without them Genie ranked every quarter in history (Boston 2024-Q4). That's the lesson for Demo 13 (context matters).

### Stage 5: Risks (8 min)

**Prompt:**
> Summarize the top 3 risks across the portfolio this quarter

**Expected (Start agent):** target misses (€156k shortfall across 3 properties), the Harbor Tower QoQ decline, and (seen 2026-10-09) lease-expiry risk concentrated at Peachtree Center. Grounded; compare with the Reference agent, whose instructions add the business context.
Ask the same in the **Reference** agent: 14 leases expiring within 180 days, 3 missed targets, 1 QoQ decline. Same data, better context.

### Stage 6: Share and take it with you (7 min)

- **Share** the thread with a colleague (share icon, top right): they see the same answers and SQL.
- Show the **desktop** and **mobile** apps, the **Slack / Microsoft 365** connectors, attaching a file
  to a question (e.g. the Q2 board pack PDF from `documents/`), and **scheduling** a question

## Demo 3: Genie Code — migrate and fix a Snowflake view

**Session:** Day 1, 10:15–10:45 (30 min) · **You build:** `<my_schema>.property_performance_v` · **Reference:** `<catalog>.<schema>.ref_d03_property_performance_v`
**Where:** SQL editor, Genie Code side panel

### Stage 1: Paste and run (3 min)

Paste the Snowflake view into a new SQL editor tab. Replace the table prefixes with `<catalog>.<schema>`
and the view name with `<my_schema>.property_performance_v`. Run it.

**Expected:** `[UNSUPPORTED_DATATYPE] Unsupported data type "NUMBER(18,2)"`.
**Checkpoint:** the error appears in the results panel.
**If stuck:** check the three-part names. The error must be about `NUMBER`, not "table not found".

### Stage 2: Explain and find the issues (5 min)

**Prompt** (Genie Code, SQL editor, with the query selected):
> Explain this query and identify any issues for Databricks SQL. It was written for Snowflake.

**Expected:** Genie Code flags `NUMBER(18,2)` (use `DECIMAL`), `TO_VARCHAR(date, 'YYYY-MM')` (use
`date_format(date, 'yyyy-MM')`), `DIV0` (use `try_divide`), and `SYSDATE()` (use `current_timestamp()`).
It may also note that `NVL`, `IFF`, `DATEADD`, and `QUALIFY` work as-is.
**Checkpoint:** all four incompatibilities are listed.
**If stuck:** ask the follow-up "Which functions in this query don't exist in Databricks SQL?"

### Stage 3: Fix the syntax (5 min)

**Prompt:**
> Fix the syntax errors and adapt this for Databricks SQL. Keep the logic the same.

**Expected:** the view is created. Then run:
`SELECT COUNT(*) FROM <my_schema>.property_performance_v` → **176**.
**Checkpoint:** 176 rows. That's suspicious: 8 properties × 8 quarters should be 64.
**If stuck:** copy the syntax lines from the reference view (`SHOW CREATE TABLE <catalog>.<schema>.ref_d03_property_performance_v`), but keep your join as it is.

### Stage 4: Why are there duplicate rows? (5 min)

**Prompt:**
> Why does this view return 176 rows when there are 8 properties and 8 quarters? Are there duplicate rows?

**Expected:** Genie Code spots the join `ON g.region_name = p.region_name`: each property row matches
every property in its region (3 in Southeast, 2 in Northeast, 3 in Western Europe), and `property_name`
comes from the wrong side of the join. Fix: `ON g.property_id = p.property_id`.
**Checkpoint:** after the fix, `COUNT(*)` = **64** and `COUNT(DISTINCT property_id, fiscal_quarter)` = 64.
**If stuck:** "Compare row counts with and without the join to silver_properties."

### Stage 5: Add YoY (7 min)

**Prompt:**
> Add a column yoy_net_profit_change showing net_profit change versus the same quarter last year.

**Expected:** `net_profit - LAG(net_profit, 4) OVER (PARTITION BY property_id ORDER BY fiscal_quarter)`.
Watch for `LAG(..., 1)`: that's quarter-over-quarter, not YoY. Ask Genie Code "Is that the same quarter last year or the previous quarter?" if it uses 1.
**Checkpoint:**
```sql
SELECT property_name, yoy_net_profit_change FROM <my_schema>.property_performance_v
WHERE fiscal_quarter = '2026-Q2' ORDER BY yoy_net_profit_change LIMIT 1
```
→ **Harbor Tower, −478,309.66**. 2024-Q3 and 2024-Q4 are NULL (no 2023 data).
**If stuck:** compare with the reference view.

### Stage 6: Verify (5 min)

**Prompt:**
> Write a query that checks my view against <catalog>.<schema>.ref_d03_property_performance_v row by row and returns any differences.

**Expected:** an `EXCEPT` or full-outer-join check returning 0 rows (ignore `refreshed_at`).

## Demo 4: Extraction Agent — "Invoice-to-Table"

**Session:** Day 1, 11:00–11:45 (45 min) · **You build:** an Information Extraction agent over the invoices + a Delta table of extracted fields · **Reference:** agent `extract-invoices-2026-10-08-15-39-15` ("Invoice Extractor (Reference)"), table `<catalog>.<schema>.ref_invoices_extracted`
**Where:** left nav **Agents** → **Create Agent** → **Information Extraction**; then the SQL editor

### Stage 1: Create and point at the documents (3 min)

**Agents → Create Agent → Information Extraction → Select volume**. Choose **All volumes**, search
`documents`, click the volume, then expand it and click **invoices** (the breadcrumb must end in
`/documents/invoices`) → **Select**.

**Expected:** "Processing 5 files…"; the build view samples 5 of the 8 invoices.
**If stuck:** if expanding the volume shows "Request access", wait a few seconds and expand again: the folder list loads late.
Don't select the volume root, or the policies and leases get sampled too.

### Stage 2: Describe what to extract (3 min)

**Prompt** (the "Describe what you want to extract" box):
> Extract from each vendor invoice: vendor_name, invoice_number, invoice_date, due_date, line_items (an array where each item has description, quantity, unit_price, amount), subtotal, tax, total, and currency (ISO code like EUR, USD, GBP). Dates as YYYY-MM-DD. Amounts as numbers without currency symbols.

Click **Generate schema**.
**Expected:** the 9 fields, with `line_items` as `array[obj]` of 4 sub-fields.
**Checkpoint (important):** open `line_items › quantity`. Genie generates **integer**; change it to **Number**.
The legal invoice bills 4.5 / 2.5 / 1.5 hours, and integer would truncate them.

### Stage 3: Run and review (5 min)

Click **Run extraction**. Click each file to see the PDF next to the JSON.
**Expected (Coastal Climate Systems, HV-2026-0417):** total **339600**, currency **USD**, 4 line items (chiller 214,500; crane 38,900; installation 61,200; commissioning 25,000), tax null.
Also check the bilingual Luxembourg tax notice (ACD-2026-IF-55120, €27,826.50) and the UK insurance statement (£55,272 incl. 12% IPT).

### Stage 4: Use the agent in production (5 min)

Click **Use Agent**. Show the five paths: **Run in SQL**, Run in Notebook, REST API, **Create a Lakeflow Job**, **Create a Spark Declarative Pipeline**.
Click **Run in SQL → Start extraction**. A SQL editor tab opens with the generated query:
`read_files(..., format => 'binaryFile')` → `ai_parse_document(content, map('version','2.0'))` → `ai_extract(parsed, '<json schema>', options => map('version','2.0'))`.

**Prompt** (Genie Code, in that SQL editor tab):
> Explain this query step by step, then wrap it in CREATE OR REPLACE TABLE <my_schema>.invoices_extracted so the results are saved as a Delta table.

**Expected:** a CTAS over the same query; 8 rows; `response` is a VARIANT with `response.response.<field>`.
**Checkpoint:** `SELECT response:response.invoice_number::string, response:response.total::double FROM <my_schema>.invoices_extracted` → 8 rows incl. `HV-2026-0417 | 339600`.
**If stuck:** run `code/reference/d04_extract_invoices.sql` (the captured agent SQL as a CTAS).

### Stage 5: Reconcile to the GL (6 min)

**Prompt** (Genie Code):
> Join the extracted invoices to <catalog>.<schema>.silver_gl_transactions where the GL description starts with the invoice number, and show invoice total, currency, GL amount in EUR, and the GL account name and category.

**Expected:** HV-2026-0417: USD 339,600 ↔ **€312,390.76** booked to **Repairs & Maintenance (OpEx)**. The others don't
match by invoice number (the GL has monthly accruals). Hold that thought: in Demo 5 the policy says this chiller is **CapEx**.

### Stage 6: Into a pipeline (3 min, show)

Back in the agent: **Use Agent → Create a Spark Declarative Pipeline**. Show that new PDFs dropped into the volume
are extracted incrementally on schedule. Don't run it in the room; it's the production path.

## Demo 5: Knowledge Assistant — "Ask the Policy Book"

**Session:** Day 1, 11:45–12:15 (30 min) · **You build:** a Knowledge Assistant over the group policies · **Reference:** agent `revantage-policy-assistant` (endpoint `ka-234e391f-endpoint` on the FEVM; a new ID in your workspace)
**Where:** Agents → Create Agent → Knowledge Assistant

### Stage 1: Create (3 min, start it early)

**Agents → Create Agent → Knowledge Assistant.**
- **Name:** `policy-assistant-<your_name>` (letters, numbers, dashes; ≤ 64 characters; clear the default name first)
- **Description:**
  > Answers questions about Revantage Europe group policies: expense approval thresholds, capital expenditure vs operating expense classification, lease renewal procedures, and intercompany transfers. Always cite the policy and section.
- **Knowledge source:** Type *Files in a Volume* → Source → *All volumes* → `documents` → expand → **policies** → Select. Name `revantage_group_policies`.
- **Describe the content:**
  > Four Revantage Europe group policy PDFs with numbered sections: Expense Approval Policy (delegation of authority and approval thresholds in EUR), Capital Expenditure Guidelines (CapEx vs OpEx rules, depreciation), Lease Renewal Procedures (180/120/90/30-day steps), Intercompany Transfer Policy (recharges, settlement, reconciliation).

**Create Agent.** **If stuck:** "REQUEST_LIMIT_EXCEEDED" → wait a few seconds and click Create again; if the button spins for minutes, reload, re-enter, and check the agent list first (it may already exist).

### Stage 2: Ask the three business questions (10 min)

In the agent's **Test** panel (or the reference agent while yours indexes):
> What is the approval threshold for expenses over €50,000?

**Expected:** co-signature of the **CFO and the Asset Management Director**, two different people, with supporting documentation. Cites `expense-approval-policy.pdf`.
> If a tenant's lease expires in 90 days, what steps should I take?

**Expected:** Day-90 step: formal written notice by registered letter if there's no response to the renewal proposal, escalate to the Head of Asset Management, start re-letting marketing in parallel; final decision at day 30. Cites `lease-renewal-procedures.pdf`.
> Is a new HVAC system for Harbor Tower classified as CapEx or OpEx?

**Expected:** **CapEx**: replaces a building system, > €25,000, useful life 20 years (> 3); routine servicing would be OpEx. Cites `capital-expenditure-guidelines.pdf`.
**Land it:** Demo 4 showed this exact chiller (HV-2026-0417, €312k) booked to **Repairs & Maintenance (OpEx)**. That's why Harbor Tower "missed" its Q2 target by €43k. The policy says reclassify it.

### Stage 3: Citations and follow-ups (5 min)

Open the citation on each answer: it links to the source PDF passage. Try:
> What credit rating threshold requires Head of Asset Management sign-off for lease renewal?

**Expected:** tenants rated **below BB**.

### Stage 4: Share and use from SQL (7 min)

- **Share:** agent page → Permissions → add the team (Can Query). Anyone with access can use it in the Playground or through the endpoint.
- **From SQL** (the "agents scale to production via SQL" point):
```sql
SELECT ai_query('<your KA endpoint name>',
  'Does invoice HV-2026-0417 (USD 339,600 chiller replacement) need CFO approval? Answer in one sentence.') AS answer
```
**Expected:** "Yes … exceeds the €50,000 threshold that requires co-signature of the CFO and Asset Management Director."
**Prompt** (Genie Code, SQL editor):
> Use ai_query with my Knowledge Assistant endpoint to add a column policy_check to a copy of <catalog>.<schema>.ref_invoices_extracted in <my_schema> that says, for each invoice, which approvers it needs under the Expense Approval Policy.

### Stage 5: Tour of other agent types (5 min, show)

In **Create Agent** point out: **Information Extraction** (Demo 4), **Document Parsing**, **Text Classification**,
**Supervisor Agent** (combine Genie Agents, Knowledge Assistants, and MCP tools, e.g. "Portfolio Q&A + Policy Assistant"),
**Knowledge Assistant**, **code your own agent** (Apps template), **Genie Agent**.

## Demo 6: Genie One Data Exploration — "Audit your data before you trust it"

**Session:** Day 1, 12:15–12:30 (15 min) · **You build:** a recurring quality check from Genie's SQL · **Reference:** view `<catalog>.<schema>.ref_d06_property_quality_checks`
**Where:** Genie One, then SQL editor with Genie Code

### Stage 1: Layer counts (2 min)

**Prompt** (Genie One):
> How many properties are in the bronze layer vs. the gold layer?

**Expected:** bronze **10**, gold **8**.

### Stage 2: What got dropped (2 min)

**Prompt:**
> Which properties exist in bronze but not in gold?

**Expected:** id 9 **Riverside Annex** (Charlotte) and id 10 **Harbor Tower** (Miami Bch), both with no region.

### Stage 3: Completeness (2 min)

**Prompt:**
> Show me the null rate for every column in bronze_properties

**Expected:** `region_id` **20%** (2 of 10). `_rescued_data` 100% NULL: that's Auto Loader's column for
values that didn't fit the schema, and all-NULL is good news.

### Stage 4: Duplicates (2 min)

**Prompt:**
> Are there any duplicate property names with different IDs?

**Expected:** **Harbor Tower**, ids **3** and **10**. Id 10 is the bad record from Stage 2.

### Stage 5: Cross-source consistency (2 min)

**Prompt:**
> Compare market names between bronze and silver for mismatches

**Expected:** 3: Miami Bch → Miami Beach, NYC → New York, Lux-Ville → Luxembourg City.

### Stage 6: Keep the checks (5 min)

Copy the SQL from Stages 1–5 (Show code → copy) into a SQL editor tab, then:

**Prompt** (Genie Code, SQL editor):
> Combine these five checks into one view <my_schema>.property_quality_checks with columns check_name, observed, issue_count, one row per check.

**Expected:** a view returning 5 rows with issue counts **2, 2, 2, 1, 3**.
**Checkpoint:** `SELECT * FROM <my_schema>.property_quality_checks` matches `SELECT * FROM <catalog>.<schema>.ref_d06_property_quality_checks`.
**If stuck:** `SHOW CREATE TABLE <catalog>.<schema>.ref_d06_property_quality_checks` and copy it.
Teaser for Demo 16: schedule this view as an alert so the next bad load is caught automatically.

## Demo 7: Semantic Layer & UC Metric Views — "Define Net Profit Margin once"

**Session:** Day 1, 1:30–2:15 (45 min) · **You build:** three metric views in `<my_schema>` · **Reference:** `<catalog>.<schema>.ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth` (source `code/reference/d07_metric_views.sql`)
**Where:** SQL editor with Genie Code; Catalog Explorer; Genie One

### Stage 1: Net profit margin (12 min)

**Prompt** (Genie Code, SQL editor):
> Create a Unity Catalog metric view <my_schema>.mv_net_profit_margin over <catalog>.<schema>.gold_property_quarterly with dimensions property_name, property_type, region_name, market, fiscal_quarter, fiscal_quarter_date and measures revenue = SUM(revenue), net_profit = SUM(net_profit), net_profit_margin = SUM(net_profit) / SUM(revenue), plus asset_mgmt_net_profit_margin = SUM(net_profit - capex) / SUM(revenue) labelled as not approved.

**Expected:** `CREATE OR REPLACE VIEW … WITH METRICS LANGUAGE YAML AS $$ version: 1.1 … $$`. (Metric views are views with a YAML body; there is no `CREATE METRIC TABLE`.)
**Checkpoint:**
```sql
SELECT MEASURE(net_profit_margin), MEASURE(asset_mgmt_net_profit_margin)
FROM <my_schema>.mv_net_profit_margin WHERE fiscal_quarter = '2026-Q2'
```
→ **0.5933 · 0.5395**. By region: `GROUP BY region_name`.
**If stuck:** copy the first statement of `code/reference/d07_metric_views.sql`, change the view name.

### Stage 2: Target attainment (8 min)

> Add a metric view mv_target_attainment with measures properties = COUNT(DISTINCT property_id), properties_met_target = COUNT(DISTINCT property_id) FILTER (WHERE met_target), target_attainment = their ratio, and net_profit_vs_target = SUM(net_profit) - SUM(net_profit_target). Format amounts as EUR.

**Checkpoint (2026-Q2):** properties **8**, met **5**, attainment **0.625**; (Without "Format amounts as EUR" Genie Code tends to add a USD format.) `GROUP BY property_name HAVING MEASURE(net_profit_vs_target) < 0` → Peachtree Center −71,293; Harbor Tower −43,235; Zuidas Residences −41,701.

### Stage 3: QoQ growth (10 min)

> Add mv_qoq_revenue_growth whose source is a query adding prior_quarter_revenue = LAG(revenue) per property, with measures qoq_revenue_growth = SUM(revenue) / SUM(prior_quarter_revenue) - 1 and qoq_net_profit_growth using prior_quarter_net_profit.

**Checkpoint (2026-Q2, by market):** `qoq_net_profit_growth`: Luxembourg City **+10.0%** (highest), Miami Beach **−44.1%**; by region Southeast **−18.6%** (the Demo 2 Genie numbers). `qoq_revenue_growth` is smaller: Luxembourg City +9.2%, Miami Beach −17.6%, Southeast −6.4%. Make sure participants compare the right measure.

### Stage 4: Govern it (5 min)

Catalog Explorer → your metric view → owner, comment, **Certified** tag (`system.certification_status`), grants. Point out lineage back to gold.

### Stage 5: Genie answers from the definition (10 min)

In Genie One open **Revantage Portfolio Q&A (Reference)** (it includes the `ref_mv_*` views):
> Which properties missed their quarterly target in 2026-Q2?

**Expected:** the same 3 properties, answered from `ref_mv_target_attainment` (net_profit_vs_target). The answer names the metric view.
> What is our net profit margin this quarter, and how would it differ under the Asset Management definition?

**Expected:** 59.33% vs 53.95% (−5.38 pp), labelled as the approved vs the non-approved definition.

## Demo 8: AI/BI Dashboards — "Executive Portfolio Review"

**Session:** Day 1, 2:15–3:15 (60 min) · **You build:** dashboard "Portfolio Review – <your_name>" · **Reference:** "Revantage Portfolio Review (Reference)"
**Where:** Dashboards → Create dashboard; Genie Code panel in the dashboard editor

### Stage 1: Create and add data (5 min)

Dashboards → **Create dashboard** → rename "Portfolio Review – <your_name>". **Data** tab → **Add data source** →
pick `ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `gold_property_quarterly`.

**Prompt** (Genie Code, dashboard editor):
> Add a dataset kpi_latest that returns, for fiscal_quarter 2026-Q2, revenue, net profit and net profit margin from ref_mv_net_profit_margin and target attainment from ref_mv_target_attainment, one row. Metric views can't be joined: aggregate each with MEASURE() in its own subquery and cross join the two results. Run the dataset and check it.

**Expected:** one row: revenue 10,744,919; net_profit 6,375,345; margin 0.5933; target_attainment 0.625.
**If stuck:** copy the `kpi_latest` query from the reference dashboard (open it → Data tab).

### Stage 2: Page 1, Executive Summary (10 min)

**Prompt:**
> On a page "Executive Summary", add counters for Revenue 2026-Q2 (EUR, compact), Net profit margin (%), and Target attainment (%) from kpi_latest, and a line chart of net profit by fiscal_quarter colored by region_name from ref_mv_net_profit_margin.

**Expected:** €10.7M · 59.3% · 62.5%; the line chart shows Southeast dropping in 2026-Q2.
**Checkpoint:** the counters match the reference dashboard's Executive Summary.

### Stage 3: Page 2, Regional Performance (12 min)

**Prompt:**
> Add a page "Regional Performance" with a bar chart of net profit by region and a scatter of revenue vs revenue_target by property, both from one dataset on gold_property_quarterly, and a heatmap of quarter-over-quarter net profit growth by market and quarter from ref_mv_qoq_revenue_growth. Add a single-select fiscal_quarter filter defaulting to 2026-Q2 that applies to the bar and scatter.

**Expected:** bar (2026-Q2): Western Europe highest, Southeast **€2,094,950**; heatmap: Miami Beach 2026-Q2 is the darkest negative cell (−44%), Luxembourg City +10%.
**Checkpoint:** if the bar shows ~€24.5M for Southeast, it isn't filtered (all 10 quarters summed): the filter only binds to datasets it was created on. Ask: "Make the Fiscal Quarter filter apply to the bar too, and check the 2026-Q2 Southeast value." Without "from gold_property_quarterly" Genie Code looks only in the metric views, can't find revenue_target, and substitutes net_profit.
**If stuck:** switch the widget type in the widget panel; Genie Code sometimes picks a table first.

### Stage 4: Page 3, Exceptions & Risks (8 min)

**Prompt:**
> Add a page "Exceptions & Risks" with a table of properties from gold_property_quarterly showing net profit, target, variance (net_profit - net_profit_target), qoq_change_pct (already in percent units, -44.05 means -44.05%) and a flag "Sharp decline" when qoq_change_pct < -10, with filters for fiscal_quarter (default 2026-Q2) and met_target.

**Expected:** filtering met_target = false gives 3 rows: Peachtree Center −€71,293, Harbor Tower −€43,235 (Sharp decline, −44%), Zuidas Residences −€41,701.

### Stage 5: Global filters (5 min)

**Prompt:**
> Add global filters for region_name and property_type that apply to all pages. Bind them to every dataset that has those columns, then set Region = Western Europe and verify each page.

**Checkpoint:** Region = Western Europe: the bar shows one bar (€2.69M), the Exceptions table 3 properties, the heatmap 2 markets. The three counters don't change: `kpi_latest` is a one-row portfolio dataset (a good talking point: which KPIs should be filterable?).

### Stage 6: Ask Genie on the dashboard (8 min)

**Publish** the dashboard. In the published view use the **Ask Genie** bar at the bottom (or select a chart, then ask about it):
> Why did Southeast net profit drop in Q2?

**Expected:** Genie drills down by property type, then property: **Harbor Tower** net profit €1.15M → €0.64M (−44%) while revenue fell only 18%, so a cost spike sits on top of the revenue loss. Other Southeast properties were flat or up.
Follow-up for Demo 5: "What made Harbor Tower's operating expense jump?" → repairs & maintenance (the chiller invoice HV-2026-0417).

### Stage 7: Share, schedule, cache (5 min)

- **Share** → add the `revantage_consumers` group as *Can view* (viewers use the publisher's or their own credentials, as you choose).
- **Schedule** → daily 07:00 refresh + email snapshot to yourself.
- Explain caching: published dashboards serve cached results, refreshed on schedule or on demand.
- Talk track: Tableau/Power BI import, custom visuals, and embedding are available; show only if enabled in the workspace (pre-flight).

### Stage 8 (optional, with Demo 14): Forecast page

**Prompt:**
> Add a page "Forecast" with a line chart from ref_d14_revenue_forecast showing actual, forecast, lower and upper interval and target over fiscal_quarter_date for one property, with a property filter defaulting to Harbor Tower.

## Demo 9: Databricks Apps — "Lease Expiry Tracker"

**Session:** Day 1, 3:30–4:15 (45 min) · **You build:** a lease-expiry quick tool as a Databricks App · **Reference:** app `revantage-lease-tracker` (Next.js + TypeScript, `code/app/`)
**Where:** Apps (new Apps UI: **New → App**), the app's source folder in the workspace with Genie Code

### Stage 1: Start from a template (5 min)

**New → App → Install from templates → Hello world → Streamlit**. Name `lease-tracker-<your_name>`, Create. Wait for **Running** (~2–3 min), open it.
The hello-world create flow only asks for compute, so add the warehouse afterwards: app page → **Edit → App resources → Add resource → SQL warehouse** (Can use), resource key **`sql-warehouse`**, Save.
**Checkpoint:** the template renders. Open **Edit in workspace** to see the source folder.

### Stage 2: Query the leases (10 min)

Open the app's main file (e.g. `app.py`) and Genie Code:
> The app has a SQL warehouse resource named sql-warehouse; in app.yaml read it into DATABRICKS_WAREHOUSE_ID with valueFrom: sql-warehouse (no resources block in app.yaml). Change this app to query <catalog>.<schema>.silver_leases joined to silver_tenants and silver_properties through that warehouse, and show property, tenant, lease end, monthly rent, and days remaining (datediff from current_date) for leases ending in the next 90 days, sorted by days remaining.

**Expected:** a table with 6 rows (today), earliest Harbor Tower / Willow Partners (11 days on 9 Oct; the count is from `current_date`).
**If stuck:** open the reference app and compare its query: `code/app/src/app/api/leases/route.ts`.

### Stage 3: Filters and risk (10 min)

> Add filters for expiry window (90 / 180 / 365 days / all including expired), region, and property type, and a risk column: High if within 90 days and not 'Pending Renewal' or the tenant's credit rating is below BB; Medium if within 180 days; otherwise Low.

**Expected:** 180-day window → 14 rows; Southeast filter shows Peachtree Center and Harbor Tower leases.

### Stage 4: Summary cards and export (8 min)

> Add summary cards at the top: number of leases expiring in the window, monthly and annualised rent at risk in EUR, and the average credit rating of the tenants. Add a button that downloads the filtered table as CSV.

**Expected (90 days):** 6 leases · €103k / month · €1.2M / year · average rating BBB (Genie Code's version showed **BBB+**: it rounds the averaged rating scale differently; either is fine, discuss the method).

### Stage 5: Share it like a Google Doc (5 min)

App page → **Permissions** → add `revantage_consumers` (Can use). Send the URL. Viewers sign in with their
Databricks identity; the app reads data as its service principal (or, with on-behalf-of-user auth enabled, as the viewer, so UC row filters and masks apply).

### Stage 6: Talk track (7 min)

- **When an app instead of a dashboard:** workflows (sort, flag, export, write back). Demo 12 adds approve/reject writes on Lakebase.
- **Embedding Genie and agents:** apps can call a Genie Agent (Conversation API) or the Knowledge Assistant endpoint (Demo 5), or use Databricks-managed MCP servers for Genie, UC functions, and vector search.
- **Row Zero / spreadsheet-style analytics:** UNVERIFIED in the Databricks context. Confirm with the account team before mentioning it. Don't present it as a Databricks feature without confirmation.
- **No per-seat cost:** apps bill compute (shown on the create page: Medium ≈ 0.5 DBU/hour), not users.

## Demo 10: Unity Catalog & Governance — "Who can see what, and why?"

**Session:** Day 1, 4:15–4:45 (30 min) · **You build:** business metadata, a certification, and PII masks on the gold layer · **Reference:** `code/reference/d10_governance.sql` (apply) and `d10_reset.sql` (back to the starting state)
**Where:** Catalog Explorer, SQL editor with Genie Code

### Stage 1: Look before you touch (5 min)

Catalog → `<catalog>` → `<schema>` → `gold_property_quarterly`: **Overview** (owner, no description), **Details**, **Permissions**, **Lineage** (upstream silver tables, downstream metric views, the Portfolio Review dashboard, the Genie Agents).

### Stage 2: Describe it for business users (8 min)

In Catalog Explorer use **AI generate** on the description, or in the SQL editor:
**Prompt** (Genie Code):
> Write a description for <catalog>.<schema>.gold_property_quarterly suitable for a non-technical business user, and column comments for net_profit, met_target and qoq_change_pct. Give me the SQL to apply them, run it, and confirm with DESCRIBE TABLE EXTENDED.

**Expected:** `COMMENT ON TABLE … IS '…'` and `ALTER TABLE … ALTER COLUMN net_profit COMMENT '…'` (not TBLPROPERTIES). Net profit must say: revenue minus operating expenses minus management fees; capex and intercompany not deducted.
**Checkpoint:** `DESCRIBE TABLE EXTENDED <catalog>.<schema>.gold_property_quarterly` shows the comment; Genie answers improve because it reads these.

### Stage 3: Certify it (3 min)

```sql
ALTER TABLE <catalog>.<schema>.gold_property_quarterly SET TAGS ('system.certification_status' = 'certified');
```
**Expected:** a **Certified** badge in Catalog Explorer and search. Free-form keys like `data_owner` may be blocked by a governed tag policy ("not an allowed value"); that's governance working.

### Stage 4: Mask PII (8 min)

**Prompt:**
> Create a column mask function that shows the full email only to members of revantage_finance_stewards and otherwise the first letter plus the domain, a similar one for phone numbers showing only the last 3 digits, and apply them to contact_email and contact_phone on <catalog>.<schema>.customer_performance. Put the functions in <my_schema>. Tag the columns with the governed tags class.email_address and class.phone_number. Run it and show me what I see now.

**Expected:** two SQL UDFs with `is_account_group_member(...)`, `ALTER TABLE … ALTER COLUMN contact_email SET MASK …`, tags `class.email_address` / `class.phone_number`.
**Checkpoint:** `SELECT contact_email, contact_phone FROM <catalog>.<schema>.customer_performance LIMIT 1` → `l***@nimbus.example.com | *** *** 597` for you (you're not in the stewards group).

### Stage 5: Permissions and sharing (4 min)

**Permissions** tab: SELECT for `revantage_consumers` inherited from the schema; `SHOW GRANTS ON TABLE …`. The same group has CAN_RUN on the Genie Agents and CAN_READ on the dashboard, so permissions follow the data. Mention the AI Gateway (Demo 13): model access is governed in the same place.

## Demo 11: Lakeflow — "Bronze-Silver-Gold in 20 minutes"

**Session:** Day 2, 9:30–10:30 (60 min) · **You build:** a Lakeflow Spark Declarative Pipeline from the raw CSVs into `<my_schema>` · **Reference:** pipeline "[Revantage workshop] Property Pipeline (Reference)", tables `<catalog>.<schema>.ref_d11_*`, source `code/pipelines/ref_property_pipeline/`
**Where:** Jobs & Pipelines → Create → ETL pipeline (Lakeflow Pipelines Editor), Genie Code in Agent mode

### Stage 0: Show, don't build (5 min)

- **Lakeflow Connect:** Data Ingestion → show the connector tiles (Salesforce, Workday, SQL Server, SharePoint…): authenticate once, pick objects, schedule. Revantage's Yardi/SAP extracts land as files today, so we use Auto Loader.
- **Lakeflow Designer / Visual Data Prep:** left nav *Visual Data Prep*: drag-and-drop for analysts; it generates the same pipeline code.

### Stage 1: Create the pipeline and ask for a design (8 min)

Create an ETL pipeline named `property-pipeline-<your_name>`, default catalog `<catalog>`, schema `<my_schema>`, SQL. Open Genie Code (Agent mode):
> I have raw CSV files in /Volumes/<catalog>/<schema>/raw/ for regions, properties, tenants, leases, gl_accounts, gl_transactions and quarterly_targets. Design a Bronze → Silver → Gold Lakeflow Declarative Pipeline in SQL. Bronze: Auto Loader streaming tables with read_files; more files will arrive for each entity, so match <entity>*.csv (for example gl_transactions*.csv), and read gl_transactions.amount as STRING. Silver: typed and cleaned, latest lease version per lease_id by updated_at, properties without a region removed, market names standardized (Miami Bch → Miami Beach, NYC → New York, Lux-Ville → Luxembourg City). Gold: a materialized view gold_property_quarterly with revenue, operating_expense, mgmt_fee, capex, intercompany by property and fiscal quarter, net_profit = revenue - operating_expense - mgmt_fee, joined to quarterly_targets, with met_target and qoq_change_pct. Dry-run it, run it, and check the gold output.

**Expected:** Genie Code proposes 3 files (bronze / silver / gold) with `CREATE OR REFRESH STREAMING TABLE … FROM STREAM read_files(...)` and `CREATE OR REFRESH MATERIALIZED VIEW`. Accept.
**If stuck:** copy the three files from `code/pipelines/ref_property_pipeline/` and replace `${raw_path}` with your raw path.

### Stage 2: Bronze (5 min)

**Checkpoint:** every bronze table reads `<entity>*.csv` (either `read_files('<raw path>/<entity>*.csv', …)` or the raw folder plus `pathGlobFilter => '<entity>*.csv'`, both work), and `amount` is STRING in `DESCRIBE <my_schema>.bronze_gl_transactions`.

### Stage 3: Expectations (7 min)

**Prompt:**
> Make sure amount is STRING in bronze and try_cast to DECIMAL(18,2) in silver. Add data quality expectations: on silver gl_transactions drop rows whose fiscal_period doesn't match YYYY-Qn and fail the update if amount is NULL after casting; on silver properties drop rows without a region; on gold expect revenue IS NOT NULL and fiscal_quarter in YYYY-Qn format. Run the pipeline with a full refresh and report the expectation metrics.

**Expected:**
```sql
CONSTRAINT valid_fiscal_period EXPECT (fiscal_period RLIKE '^[0-9]{4}-Q[1-4]$') ON VIOLATION DROP ROW,
CONSTRAINT amount_parsed EXPECT (amount IS NOT NULL) ON VIOLATION FAIL UPDATE
```
(the agenda's `MATCHES` isn't SQL; `RLIKE` is), with `try_cast(amount AS DECIMAL(18,2))` in silver.

### Stage 4: Run and inspect (10 min)

Click **Run pipeline**. Open the **graph**: 7 bronze → silver → 1 gold.
**Expected** (data quality tab): `valid_fiscal_period` **3 failed** (a zero-sum manual accrual with period "2026Q2"); `has_region` **2 failed** (Riverside Annex, the duplicate Harbor Tower); gold **80 rows**.
**Checkpoint:**
```sql
SELECT COUNT(*) FROM <my_schema>.gold_property_quarterly g
JOIN <catalog>.<schema>.gold_property_quarterly r USING (property_id, fiscal_quarter)
WHERE abs(g.net_profit - r.net_profit) > 0.01      -- expect 0
```

### Stage 5: A late batch arrives (facilitator, 2 min)

**Expected:** the update **fails**: `EXPECTATION_VIOLATION … Violated expectations: 'amount_parsed' … "amount":"1.850,75" … source_file …/gl_transactions_late_batch_lux.csv`.

### Stage 6: Diagnose and fix with Genie Code (10 min)

**Prompt** (Genie Code, on the failed update):
> Why did this pipeline update fail? Show me the offending rows and propose a fix.

**Expected:** Genie Code points at `amount_parsed` and the European decimal format. A good fix in silver:
```sql
CASE WHEN amount RLIKE ',[0-9]{1,2}$' THEN CAST(replace(replace(amount, '.', ''), ',', '.') AS DECIMAL(18,2))
     ELSE try_cast(amount AS DECIMAL(18,2)) END AS amount
```
(verified: `1.850,75` → 1850.75, `980,40` → 980.40, `258689.5` unchanged).

## Demo 12: Lakebase & Production Operations — "Approval workflow state machine"

**Session:** Day 2, 10:45–11:30 (45 min) · **You build:** an approval table in Lakebase, approvals through an app, and a job that loads only approved invoices to Delta · **Reference:** Lakebase instance `revantage-lux-ops` (db `revantage_ops`, schema `approvals`), app `revantage-invoice-approvals`, job "[Revantage workshop] Approved invoices -> silver (Reference)", Delta `silver_invoices`, synced table `ref_d12_gold_property_quarterly_synced`
**Where:** Compute → Lakebase Postgres; SQL editor connected to Lakebase; the Invoice Approvals app; Jobs & Pipelines

### Stage 1: Why Lakebase (5 min, talk)

A dashboard can show invoices; it can't hold *who approved what, when*, enforce two signatures, or stop unapproved rows reaching the GL.
That's transactional state: row-level updates, constraints, millisecond reads. Lakebase is managed Postgres next to the lakehouse; analytical data stays in Delta.

### Stage 2: Create the database objects (10 min)

Open **SQL Editor → Create new → Query**, then the compute picker → **More… → Lakebase Postgres → Provisioned → revantage-lux-ops → Attach**, and pick the database `revantage_ops` in the database dropdown (the instance page itself only offers psql connection details). Or your own instance: **Create database instance**, CU_1; ~5 min to provision.
**Prompt** (Genie Code / Lakebase SQL editor):
> Create a Postgres schema approvals with a table invoice_approvals (invoice_id primary key, vendor_name, property_name, total_amount, currency, total_eur, status Pending/Approved/Rejected with a check constraint, first_approver, first_approved_at, reviewed_by, reviewed_at, notes, and a generated column requires_two_approvers = total_eur > 50000) and an audit table approval_events. The final approver must differ from the first approver.

**Expected:** DDL like `code/lakebase/d12_invoice_approvals.sql` (generated column + CHECK constraint).
**Checkpoint:** insert the 5 invoices (`code/lakebase/d12_reset.sql`), then
`SELECT invoice_id, total_eur, requires_two_approvers FROM approvals.invoice_approvals ORDER BY total_eur DESC` → HV-2026-0417 and TM-POL-2026-3391 are `true`.

### Stage 3: Approve in the app (10 min)

Open **Invoice Approvals** (the reference app). Everyone signs in with their own identity.
- Approve **PE-2026-06-0088** (€37.7k) with a note → *Invoice approved.*
- Approve **HV-2026-0417** (€312k) → *First approval recorded. Awaiting a second approver.* The panel shows "First approval: <you>".
- Try to approve HV-2026-0417 again yourself → **"The second approval must come from a different person (Expense Approval Policy)."**
- A second participant approves HV-2026-0417 → Approved.
**Checkpoint (Lakebase SQL):** `SELECT * FROM approvals.approval_events ORDER BY at` shows every action with the actor.
How it's wired: the app has a **database resource** (Lakebase) that injects PGHOST/PGUSER/PGDATABASE; its service principal logs in with an OAuth token; `code/app-approvals/src/lib/lakebase.ts` does each decision in a transaction with `SELECT … FOR UPDATE`.

### Stage 4: Only approved invoices reach the lakehouse (10 min)

Run the job **Approved invoices -> silver (Reference)** (Jobs & Pipelines → Run now).
**Expected:** `approved invoices in Lakebase: N`; `SELECT * FROM <catalog>.<schema>.silver_invoices` holds exactly the Approved ones. An invoice with only one signature isn't there.
Show on the job: **retries** (2, 60 s apart), **failure email**, **run history**, and the trigger (periodic 15 min, paused for the workshop).
**Prompt** (Genie Code, on the job's Python file):
> Explain how this job reads from Lakebase and why the MERGE makes re-runs safe.

Talk track on triggers: table-update ("data-readiness") triggers fire on Unity Catalog Delta tables, not on Postgres tables, so this job runs on a schedule or on demand. To trigger downstream work on approval, have the next job use a **table-update trigger on `silver_invoices`**.

### Stage 5: Reverse ETL (5 min)

**Catalog → `ref_d12_gold_property_quarterly_synced`**: a synced table copying certified gold into Postgres (snapshot mode).
**Checkpoint:** in Lakebase SQL, `SELECT count(*), sum(net_profit) FROM revantage_20261008.ref_d12_gold_property_quarterly_synced` → **80 rows, 64,214,088.70**, identical to gold. Apps read it in milliseconds without hitting a warehouse.

### Stage 6: Production health (5 min, show)

Pipeline and job health in one place: Jobs & Pipelines → runs, durations, failures; Demo 11's expectation metrics; Demo 16's data quality monitors and freshness.

## Demo 13: AI Gateway & Monitoring — "Who's using what, and what's it costing us?"

**Session:** Day 2, 11:30–12:15 (45 min) · **You build:** a usage + cost query pack and a SQL alert · **Reference:** `code/reference/d13_ai_gateway_queries.sql`, alert "[Revantage workshop] Daily AI tokens > 1M (Reference)"
**Where:** Serving → endpoint → AI Gateway; SQL editor with Genie Code; Alerts

### Stage 1: Models without deploying (5 min)

**Serving** → show the pay-per-token endpoints already there (Claude, GPT, Llama, Qwen…). Open `databricks-claude-sonnet-4-6` → **AI Gateway**: usage tracking, inference table, rate limits, guardrails, fallbacks. Then call it from SQL:
```sql
SELECT ai_query('databricks-claude-sonnet-4-6', 'In one sentence: why did Harbor Tower miss its Q2 target?')
```

### Stage 2: Tokens by endpoint (7 min)

**Prompt** (Genie Code, SQL editor):
> Using system.ai_gateway.usage, show total requests, total tokens and average latency by endpoint (or service_name when endpoint_name is null) for workspace :workspace_id over the last 30 days.

**Expected:** like Q1 in the reference file. On the FEVM: `system.ai.gpt-5-6-sol` ~1.58M tokens (46 requests), plus ~135–145 calls each to **MCP services** (Gmail, Slack, Google Drive, Atlassian, Microsoft 365, GitHub). Those are Genie One connectors, governed through the same gateway.

**Then (pay-per-token models such as the one `ai_query` calls):**
> Show total requests, total tokens and errors (status_code >= 400) by endpoint for Foundation Model endpoints in workspace :workspace_id over the last 30 days using system.serving.endpoint_usage joined to system.serving.served_entities on served_entity_id.

**Expected:** like Q6: `databricks-claude-sonnet-4-6` with the workshop's `ai_query` traffic. Run in the Genie Code UI 2026-10-09: 4 FM endpoints; sonnet-4-6 37 requests, 10,387 tokens, the 3 deliberate errors.

### Stage 3: Who, and what fails (8 min)

> Show the top 5 users by tokens with their email masked like t***@domain, then the error rate (status_code >= 400) by endpoint.

**Expected:** masked requesters; error rate per endpoint (FEVM: gpt-5-6-sol 2.2%). Point out `routing_information` (fallback attempts) and `mcp_metadata` (which tool was called).

### Stage 4: What it costs (10 min)

> Estimate list-price cost by product and endpoint for the last 30 days by joining system.billing.usage to system.billing.list_prices on sku_name, cloud, usage_unit and the price validity window, for billing_origin_product in MODEL_SERVING, AI_GATEWAY, AI_FUNCTIONS, AGENT_BRICKS, VECTOR_SEARCH.

**Expected:** Q4 in the reference file. On the FEVM the biggest AI line was **VECTOR_SEARCH** for a Knowledge Assistant's index (~200 DBU, ~$14 of ~$19 in 30 days), more than all LLM calls. Lesson: KA indexes cost money while idle; delete the ones you don't use.

### Stage 5: Alert before the bill does (10 min)

> Write a query returning today's total tokens for workspace :workspace_id from system.ai_gateway.usage as a single column tokens_today.

**Alerts → Create alert** on that query: condition `tokens_today > 1000000`, schedule hourly, notify yourself (email).
**Checkpoint:** open the reference alert "Daily AI tokens > 1M (Reference)"; it evaluates OK today. Q5 shows **2026-10-05 at 1.47M tokens**, a day it would have fired.

### Stage 6: Governance tie-in (5 min, talk)

Usage and inference tables are Unity Catalog tables: grant, lineage, and retention like any data. Guardrails (PII, safety) and rate limits per user/group live on the gateway. The same view covers Genie, agents, Genie Code sessions, and MCP connectors.

## Demo 14: Time Series Forecasting — "Where is revenue heading?"

**Session:** Day 2, 12:15–12:30 (15 min) · **You build:** a revenue forecast for 2026-Q3/Q4 vs target · **Reference:** `<catalog>.<schema>.ref_d14_revenue_forecast` (`code/reference/d14_forecast.sql`), dashboard page "Forecast"
**Where:** SQL editor (a SQL warehouse: `ai_forecast` is disabled on serverless job compute)

### Stage 1: One property (4 min)

**Prompt** (Genie Code):
> Forecast Harbor Tower's (property_id 3) quarterly revenue through 2026-12-31 with ai_forecast from <catalog>.<schema>.gold_property_quarterly.

**Expected SQL** (the agenda's `horizon => 2` form doesn't run; `frequency => 'Q'` fails on DATE columns, `'QS'` works):
```sql
SELECT * FROM AI_FORECAST(
  TABLE(SELECT fiscal_quarter_date, revenue FROM <catalog>.<schema>.gold_property_quarterly WHERE property_id = 3),
  horizon => '2026-12-31', time_col => 'fiscal_quarter_date', value_col => 'revenue', frequency => 'QS')
```
**Expected:** 2026-07-01 **≈ €1.71–1.72M** (95% interval ≈ 1.54–1.89M), 2026-10-01 ≈ €1.78–1.79M (values vary slightly run to run).

### Stage 2: Every property at once (3 min)

> Do the same for all properties at once using group_col.

**Expected:** 16 rows (8 properties × 2 quarters), columns `property_id, fiscal_quarter_date, revenue_forecast, revenue_upper, revenue_lower`.

### Stage 3: Who will miss budget? (4 min)

> Join the forecast to silver_quarterly_targets (fiscal_quarter = year-Qn of fiscal_quarter_date) and list properties whose 2026-Q3 forecast is below revenue_target.

**Expected:** exactly **Harbor Tower** (€1.72M vs €1.86M target) and **Zuidas Residences** (€1.32M vs €1.43M).

### Stage 4: Know the limits (4 min, talk)

Harbor Tower's actual Q2 revenue was **€1.51M** after the anchor tenant left on 31 March, yet the forecast says €1.72M for Q3.
`ai_forecast` sees only the revenue history, not the lease roll. When the drivers are known (lease expiries, vacancy), use **Prophet with regressors** or a lease-roll model in a notebook (MLflow-tracked); ARIMA for smooth series; GARCH/AR when the volatility itself matters (rates, FX), not for rent.
**So what for FP&A:** `ai_forecast` is a fast, governed first pass across hundreds of properties in one SQL statement; spend data-science time on the exceptions it flags.
Show the dashboard's **Forecast** page (Demo 8 reference): actual, forecast, 95% interval, target.

## Demo 15: Hands-On Lab — Build Your Own

**Session:** Day 2, 1:30–2:30 (60 min) · Pick one track. Each starts from an asset you've already seen working, so you always have a fallback.
**Where:** your sandbox schema `<my_schema>` (or `<schema>` with `_<your_name>` suffixes), Genie Code throughout

### Track A — Analyst: a Genie Agent for your domain

1. Genie → **New** → name `<your domain> Q&A – <your_name>`; add `gold_property_quarterly`, `silver_leases`, `silver_tenants` (and your own tables if you have dev access).
2. **Instructions:** start from the Reference agent's text (open *Revantage Portfolio Q&A (Reference)* → Configure → Instructions) and adapt the definitions to your domain: latest quarter, net profit definition, what "risk" means.
3. Add 3 **SQL examples** for your hardest questions, synonyms on 3 columns, and join specs.
4. Test 5 questions; for each wrong answer, fix the *context* (instruction, example, synonym), not the question.
   **Benchmark** (should pass after Stage 3): "Which leases expire in the next 90 days and what is the monthly rent at risk?" → 6 leases, €103k (as of 2026-10-08).
- **Fallback:** duplicate the Reference agent and edit it.

### Track B — Dashboard builder: your portfolio company's page

1. New dashboard; datasets on the metric views (`ref_mv_*` or your Demo 7 views) filtered to your region or property type.
2. **Prompt** (Genie Code in the dashboard editor):
   > Build a page for <region> with net profit margin and target attainment counters for 2026-Q2, a net profit trend by property, and a table of leases expiring in 180 days from silver_leases.
3. Add the dashboard's **Ask Genie**; publish; share with a colleague.
- **Fallback:** clone "Revantage Portfolio Review (Reference)" and filter it.

### Track C — Data engineer: a new source, end to end

1. Pick a source: a CSV you bring, or the `documents/invoices` extraction from Demo 4 (`ai_extract` in a pipeline).
2. **Prompt** (Genie Code, pipeline editor, Agent mode):
   > Create a pipeline that ingests <path> with Auto Loader into bronze, cleans it into silver with an expectation that drops rows missing <key> and fails the update when <amount> doesn't parse, and builds a gold summary.
3. **Jobs & Pipelines → Create job**: task 1 = your pipeline, task 2 = a SQL task that checks row counts; schedule daily 06:00; email on failure; 2 retries.
4. Add a SQL alert on a gold metric (copy the pattern from "Daily AI tokens > 1M (Reference)").
- **Fallback:** copy `code/pipelines/ref_property_pipeline/` (Demo 11) and change the paths.

### 4. Closing the lab (5 min)

Each person shows one thing they built. Collect follow-ups for the 4:15 "Next steps" session.

## Demo 16: Data Quality & Observability — "Trust scorecard"

**Session:** Day 2, 3:45–4:15 (30 min) · **You build:** quality monitoring on the gold table, a bad-load detector, and the blast radius · **Reference:** data profiling monitor on `gold_property_quarterly` (bundle target `revantage`), alert "[Revantage workshop] Revenue > 3 sigma from property mean (Reference)", `code/reference/d16_revenue_outliers.sql`, `d16_blast_radius.sql`
**Where:** Catalog Explorer → table → **Quality** tab; SQL editor with Genie Code; Alerts

### Stage 1: Turn on monitoring (5 min)

Catalog → `gold_property_quarterly` → **Quality → Enable data profiling** (Snapshot, slice by `region_name`), and at schema level **anomaly detection** (freshness, completeness).
**Expected:** a profile dashboard and two output tables (`…_profile_metrics`, `…_drift_metrics`) after the first refresh (a few minutes).
**FEVM note:** the FEVM metastore is at its 1,000-monitor limit, so we couldn't create one here. In Revantage's workspace the bundle target creates it; show the profile from the Oct 5 workshop's monitor if needed.

### Stage 2: Read the profile (5 min)

Profile dashboard: per-column null %, distinct counts, min/max/quantiles, per region slice. Freshness = last commit time.
**Prompt** (Genie Code):
> Using <catalog>.<schema>.gold_property_quarterly_profile_metrics, show null rate and max for revenue and net_profit in the latest window.

### Stage 3: A bad load arrives (facilitator, 2 min)

Run `code/sql/d16_seed_bad_row.sql` with `${table}` = `gold_property_quarterly`: inserts **Harbor Tower 2026-Q3** with revenue **10× its average (€17.2M)** and **NULL net_profit**.

### Stage 4: Detect it (8 min)

- **Completeness:** `SELECT COUNT(*) FROM <catalog>.<schema>.gold_property_quarterly WHERE net_profit IS NULL` → 1. Refresh the monitor: net_profit null % > 0, revenue max jumps, drift on revenue flagged.
- **Outlier rule:** run `code/reference/d16_revenue_outliers.sql`.
  **Expected:** exactly one row: Harbor Tower 2026-Q3, **z ≈ 172** vs its other quarters (mean €1.72M).
  **Teach:** a plain "> 3σ" rule on smooth financial series also flags real business moves. Before the seed it flagged Harbor Tower's vacancy and a new Kirchberg suite. The rule therefore uses leave-one-out σ **and** a > 50% materiality guard: **0 rows on clean data, 1 after the seed**.
**Prompt** (Genie Code):
> Write a query on <catalog>.<schema>.gold_property_quarterly that flags property-quarters whose revenue is more than 3 standard deviations from the mean of that property's OTHER quarters (leave-one-out: exclude the quarter being tested from the mean and standard deviation) and more than 50% away from that mean. Run it.

**Expected:** 0 rows before the seed (Genie Code also shows that Harbor Tower 2026-Q2 at z 4.5 and Kirchberg 2026-Q2 at z 3.9 pass 3σ but fail the 50% guard: real business moves); after the seed exactly Harbor Tower 2026-Q3, z ≈ 172.

### Stage 5: Blast radius (5 min)

Catalog Explorer → **Lineage** on the table, or run `code/reference/d16_blast_radius.sql`.
**Expected downstream:** `ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth`, the Portfolio Review dashboard (DASHBOARD_V3), `ref_d14_revenue_forecast`, `ref_d03_property_performance_v`, `ref_d06_property_quality_checks`, `customer_performance`, and the Genie Agents that read them. One bad row reaches every board number.

### Stage 6: Alert (5 min)

Open the reference alert (daily 07:00 Luxembourg, notifies the owner): it counts outliers and fires when > 0. Create your own from the Stage 4 query, wrapped as `SELECT COUNT(*) AS outliers FROM (…)`.

## Demo 17: Genie Accuracy Ladder — "From 0 to 10 out of 10, one layer at a time"

**Session:** Day 2, 2:45–3:20 (35 min) · **You build:** a Genie Agent on the legacy warehouse, made accurate step by step (business names → column comments → table descriptions and keys → metric views → instructions), with a benchmark score after every step · **Reference:** Genie Agent "Revantage Accuracy Lab (Reference)", tables `<catalog>.<schema>.ref_d17_*` (source `code/reference/d17_business_layer.sql`), scorecard `ref_d17_benchmark_results` (`code/genie/d17_ladder.py`)
**Where:** Genie Agents (Configure, Benchmarks); SQL editor with Genie Code

### Stage 1: Clone and take the baseline (5 min)

Genie Agents → **Revantage Accuracy Lab (Start)** → ⋮ → **Clone** → name it `Accuracy Lab – <your_name>`, **Clone to** your home folder → **Clone**. Open the **Benchmark** tab: the 10 questions came with the clone (**Questions (10)**). Set **Mode: Chat** (single-turn SQL, about 3 minutes for 10 questions; Agent mode takes about 8; the mode resets to Agent whenever the page reloads, so check it before every run) → **Run all benchmarks**.

**Expected:** **≈ 2 of 10** (20%). Click a question: Genie's judge shows the assessment (**Bad** · *Extra Rows*, *Filter Issue*), a **Failure analysis** comparing its SQL with the ground truth, and **Attempt fix**. Open one failure, e.g. "How many active leases do we have?": Genie guessed `LSE_STS_CD = 'Active'` and got 0 (the code is `A`). "What was total net profit in 2026-Q2?" sums the wrong thing (no idea which `ACCT_CLS_CD` is revenue).
**Tip:** use a new query tab in the SQL editor for every stage below, so Genie Code doesn't re-run the previous stage's statements.

### Stage 2: Business column names (7 min)

**Prompt** (Genie Code, SQL editor):
> Using <catalog>.<schema>.legacy_data_dictionary, create one table in <my_schema> for each legacy_* table in <catalog>.<schema>: name it after the dictionary's business_name for the table (the row where column_name is NULL) and rename every column to its business_name. Keep the values unchanged and don't add comments yet. Run it and show me the row counts.

**Expected:** 6 tables `properties` 8, `gl_accounts` 15, `gl_transactions` 2,681, `leases` 52, `tenants` 40, `quarterly_targets` 96; values untouched (`account_class` is still `R`/`O`/`M`/`C`/`I`).
Then in your agent: **Configure → Data** → remove the six `legacy_*` tables, add your six → **Benchmarks → Run all**.
**Checkpoint:** **≈ 1 of 10** (10%). Readable names alone don't help: Genie now writes `account_class = 'Revenue'` and `lease_status = 'Active'`, and every filter returns 0.
**If stuck:** run the `@rung R2` section of `code/reference/d17_business_layer.sql` with `ref_d17_` replaced by `<my_schema>.`.

### Stage 3: Column comments (5 min)

**Prompt** (Genie Code, SQL editor):
> Add a column comment to every column of my six tables in <my_schema>, taken from the description in <catalog>.<schema>.legacy_data_dictionary (match on business_name). Run it and confirm with DESCRIBE TABLE on gl_accounts and leases.

**Expected:** `ALTER TABLE … ALTER COLUMN … COMMENT …` for every column; `account_class` reads "R = Revenue, O = Operating expense, M = Management fee, C = CapEx, I = Intercompany recharge".
**Run all benchmarks** again (no need to touch the agent: it reads the comments live).
**Checkpoint:** **≈ 3 of 10** (30%). Genie decodes the codes now (CapEx and office revenue are right), but it still guesses the business rules: net profit subtracts CapEx and intercompany too (€5.59M instead of **€6.38M**), and "active leases" counts old lease versions.

### Stage 4: Table descriptions and keys (6 min)

**Prompt** (Genie Code, SQL editor):
> For each of my six tables in <my_schema>, set the table comment from the legacy_data_dictionary row where column_name is NULL (use my table and column names instead of the legacy ones). Then add the primary keys and foreign keys those descriptions name; make the key columns NOT NULL first. Run it and show me the constraints.

**Expected:** `COMMENT ON TABLE …`; `leases` says "one row per lease VERSION … the current one has the latest updated_at"; PKs on all six, FKs from `gl_transactions`, `leases`, `quarterly_targets`.
**Checkpoint:** **≈ 5 of 10** (50%). The lease questions pass (39 active leases, €1,083,458.87 monthly rent): the grain was the missing fact. Net profit is still wrong: no table can tell Genie the *Finance* definition.

### Stage 5: Metric views and instructions (6 min)

**Configure → Data → Add** the governed metric views `<catalog>.<schema>.ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth` (or your own from Demo 7) → **Run all**.
**Checkpoint:** **9–10 of 10**. Net profit, margin, target misses and attainment now come from the approved definitions (€6.38M, 59.3%, Peachtree Center / Harbor Tower / Zuidas Residences, 62.5%).
Then **Configure → Instructions** → paste:
> Amounts are EUR. The latest complete fiscal quarter is 2026-Q2: "this quarter" means 2026-Q2 and "last quarter" means 2026-Q1; never use the calendar date to pick a quarter. Net profit = revenue (account_class R) - operating expense (O) - management fee (M); CapEx (C) and intercompany (I) are not deducted; prefer the metric views for net profit, margin and target attainment. The leases table keeps every version of a lease: always use only the latest version per lease_id before counting or summing; active means lease_status = 'A'. Property type codes: OFF = Office, MFH = Multifamily, RTL = Retail. Credit ratings best to worst: AAA, AA, A, BBB, BB, B; below investment grade means BB or B.

**Checkpoint:** **10 of 10**, and it stays there when the question is phrased differently (the instructions carry the conventions the data can't).

### Stage 6: Keep it accurate (6 min)

- **Benchmark → Evaluations:** every run is kept with its accuracy; open a run to see each question's SQL next to the ground truth, the failure analysis, and **Attempt fix** (Genie proposes the instruction or example that would fix it). **Analyze with Genie** summarizes the context gaps across a run. Re-run after every schema or instruction change.
- **Monitoring** tab: the questions people actually ask, thumbs up/down, and the answers to review. Turn a good answer into an **SQL example**; turn a recurring question into a new **benchmark** question.
- **SQL examples, synonyms, join relationships** (the Reference agent has 3 examples, synonyms on 7 columns, 5 joins): they make answers stable across phrasings; the score stays at 10/10, the variance drops.

## Demo 18: Domains, Pages & Metrics — "Teach Genie One what your words mean"

**Session:** Day 2, 3:20–3:45 (25 min) · **You build:** a Page (business definition) in the Revantage domain, linked to its governed metric view, and check that Genie One uses it · **Reference:** the four Pages in `code/reference/d18_pages.md` (Net profit, Latest quarter, Active lease, Below investment grade), published by the facilitator in the domain "Revantage Workshop"
**Where:** Discover (Domains, Pages); Genie One (Switch apps → Genie One, or the home page **Ask** box)

### Stage 1: Tour the domain (4 min)

**Discover** → **Browse by domain** → **Revantage Workshop**: the domain's assets, **Featured Metric views** (the `ref_mv_*` views: the domain's *Metrics*), **Pages**, and **Ask Genie** (a Genie scoped to the domain).

### Stage 2: Ask before you define (4 min)

**Prompt** (Genie One, new chat):
> What is our NOI this quarter?

**Expected:** open **Thought process**: Genie One searches the ontology ("Found … ontology results"), picks a metric view and a quarter, and shows its sources. Check *which* definition and *which* quarter it used. Without a Page it has to guess that NOI means net profit and that "this quarter" means the latest complete quarter (2026-Q2), not the calendar quarter.

### Stage 3: Write the Page with Genie Code (8 min)

**Discover → Create → Create page** → in the Genie Code panel click **Help me create a new page** (or type):
> Help me create a page "Net profit (<your_name>)" in the Revantage Workshop domain. Description: Revantage's approved Finance net profit: revenue minus operating expense minus management fee; CapEx and intercompany recharges are not deducted. Definition: per property and fiscal quarter in EUR; in the general ledger account_class R - O - M. "This quarter" means the latest complete fiscal quarter in the workshop data, 2026-Q2. The authoritative source is the metric view <catalog>.<schema>.ref_mv_net_profit_margin over gold_property_quarterly. Synonyms: NOI, net operating income, bottom line. Related assets: <catalog>.<schema>.ref_mv_net_profit_margin and <catalog>.<schema>.gold_property_quarterly. Fill in the page fields but don't publish.

**If stuck:** copy the "Net profit" entry of `code/reference/d18_pages.md` into the form by hand.

### Stage 4: Ask again (4 min)

**Prompt** (Genie One, **new** chat, so it doesn't reuse the previous one):
> What is our NOI this quarter?

**Expected:** **Thought process** shows **Read info for: knowledge_page…** and the answer says NOI is net profit "per the glossary page". With the Page and a single certified metric view, the expected answer is **€6,375,345.36 for 2026-Q2** from `ref_mv_net_profit_margin` (to confirm in the Revantage workspace pre-flight).

### Stage 5: Metrics in the domain, and what Pages don't do (5 min)

- **Domain → Add to domain** (or `ALTER VIEW … SET TAGS ('Revantage Workshop')`): add your Demo 7 metric views; they appear under the domain's metric views. Then try the domain's **Ask Genie**: it answers from the domain's assets only.
- **Pages feed Genie One and Genie Code, not Genie Agents.** A Genie Agent answers from its own data and configuration: the same Demo 17 agent without metric views or instructions scored **50% with and without** the Net profit Page. For an agent, the definition goes into comments, metric views and instructions (Demo 17); for everyone else, into a Page.

## Appendix: the Snowflake view for Demo 3

```sql
-- D3 starting point: a business view as it exists in Snowflake today. Participants paste it into the
-- SQL editor and migrate it with Genie Code. It doesn't run on Databricks as-is, and even once it
-- runs it's wrong: the join is missing its key, so every property is repeated per region.
CREATE OR REPLACE VIEW ${catalog}.${schema}.property_performance_v AS
SELECT
    g.property_id,
    p.property_name,
    p.property_type,
    p.region_name,
    p.market,
    g.fiscal_quarter,
    TO_VARCHAR(g.fiscal_quarter_date, 'YYYY-MM') AS period_start,
    g.revenue::NUMBER(18,2) AS revenue,
    NVL(g.net_profit, 0)::NUMBER(18,2) AS net_profit,
    g.net_profit_target::NUMBER(18,2) AS net_profit_target,
    DIV0(g.net_profit, g.revenue) AS net_profit_margin,
    IFF(g.net_profit >= g.net_profit_target, 'On target', 'Missed') AS target_status,
    DATEADD(quarter, -1, g.fiscal_quarter_date) AS prior_quarter_start,
    SYSDATE() AS refreshed_at
FROM ${catalog}.${schema}.gold_property_quarterly g
JOIN ${catalog}.${schema}.silver_properties p
    ON g.region_name = p.region_name
QUALIFY DENSE_RANK() OVER (ORDER BY g.fiscal_quarter DESC) <= 8;
```
