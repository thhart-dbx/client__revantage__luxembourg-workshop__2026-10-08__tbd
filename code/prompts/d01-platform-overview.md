# Demo 1: Welcome & Platform Overview — "Where does my data live?"

**Session:** Day 1, 9:00–9:30 (30 min) · **You build:** your bearings: catalog, SQL editor, Genie Code · **Reference:** none (navigation)
**Starting state:** `<catalog>.<schema>` with `bronze_*` (7), `silver_*` (7), `gold_property_quarterly`, `customer_performance`; volumes `raw` (7 CSVs) and `documents` (`invoices/` 8, `policies/` 4, `leases/` 3 PDFs)
**Where:** Catalog Explorer, SQL editor, Genie Code side panel

## Stage 1: Open platform, 3 minutes of talk
Delta/Iceberg in your own cloud storage (S3/ADLS/GCS); any model (Claude, GPT, open source, behind the AI Gateway); any data type (tables, PDFs, Excel). Unity Catalog governs all of it.

## Stage 2: The three-level namespace (7 min)
**Catalog** → `<catalog>` → `<schema>`: point out tables, views, metric views (later), volumes, functions.
Snowflake mapping: database ≈ catalog, schema = schema, stage ≈ volume, warehouse ≈ SQL warehouse.
**Checkpoint:** open `documents` → `invoices/` → preview `HV-2026-0417.pdf` in the browser.

## Stage 3: First query (5 min)
SQL editor, Serverless warehouse:
```sql
SELECT * FROM <catalog>.<schema>.gold_property_quarterly LIMIT 10;
SELECT COUNT(*) AS rows, COUNT(DISTINCT property_id) AS properties, MIN(fiscal_quarter), MAX(fiscal_quarter)
FROM <catalog>.<schema>.gold_property_quarterly;
```
**Expected:** **80** rows · **8** properties · 2024-Q1 · 2026-Q2.

## Stage 4: Meet Genie Code (10 min)
Open the Genie Code panel (top right):
> What tables are in <catalog>.<schema> and how do the bronze, silver and gold tables relate?

**Expected:** Genie Code explains raw → cleaned → aggregated and names `gold_property_quarterly` as the fact table.
> Write a query showing 2026-Q2 net profit by region from gold_property_quarterly.

**Expected:** Western Europe ≈ €2.69M, Northeast ≈ €1.59M, Southeast ≈ €2.09M.

## Stage 5: Any data type (5 min)
**Prompt:**
> Read the PDFs in /Volumes/<catalog>/<schema>/documents/leases/ with read_files as binaryFile and parse them with ai_parse_document.

**Expected:** 3 rows, ~20 elements each; the first element of `lease-harbor-tower-anchor.pdf` is **"EXPIRED"** (the anchor tenant who left on 31 March; we'll see the impact all day).
```sql
SELECT path, ai_parse_document(content, map('version','2.0')):document.elements[0].content::string AS first_element
FROM read_files('/Volumes/<catalog>/<schema>/documents/leases/', format => 'binaryFile')
```

## Wrap-up
- **So what:** everyone can find the data, run a query, and ask Genie Code before the real work starts.
- **Verified:** 2026-10-08 on the FEVM workspace: counts (80 / 8 / 2024-Q1–2026-Q2), Q2 by region from gold, and the lease parse (3 files, first element "EXPIRED", ~20 elements each) run in SQL. **Stages 4–5 run in the Genie Code UI (S9):** S4 Genie Code listed bronze/silver/gold, named `gold_property_quarterly` as the quarterly P&L fact table (it also sees the `ref_*` answer-key objects and pipeline internals: say so up front), and returned €2.69M / €2.09M / €1.59M; S5 it parsed the 3 lease PDFs (21 / 20 / 21 elements) with Harbor Tower's first element "EXPIRED".
