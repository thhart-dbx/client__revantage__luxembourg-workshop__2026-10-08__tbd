# Demo 3: Genie Code — migrate and fix a Snowflake view

**Session:** Day 1, 10:15–10:45 (30 min) · **You build:** `<my_schema>.property_performance_v` · **Reference:** `<catalog>.<schema>.ref_d03_property_performance_v`
**Starting state:** `gold_property_quarterly`, `silver_properties`; the Snowflake view in `code/sql/d03_snowflake_property_view.sql` (also in the participant handout)
**Where:** SQL editor, Genie Code side panel

The point to land: most Snowflake SQL runs on Databricks unchanged (`NVL`, `IFF`, `DATEADD`, `QUALIFY`,
`::` casts all work). Genie Code finds the few things that don't, and a logic bug that was already
there in Snowflake.

## Stage 1: Paste and run (3 min)

Paste the Snowflake view into a new SQL editor tab. Replace the table prefixes with `<catalog>.<schema>`
and the view name with `<my_schema>.property_performance_v`. Run it.

**Expected:** `[UNSUPPORTED_DATATYPE] Unsupported data type "NUMBER(18,2)"`.
**Checkpoint:** the error appears in the results panel.
**If stuck:** check the three-part names. The error must be about `NUMBER`, not "table not found".

## Stage 2: Explain and find the issues (5 min)

**Prompt** (Genie Code, SQL editor, with the query selected):
> Explain this query and identify any issues for Databricks SQL. It was written for Snowflake.

**Expected:** Genie Code flags `NUMBER(18,2)` (use `DECIMAL`), `TO_VARCHAR(date, 'YYYY-MM')` (use
`date_format(date, 'yyyy-MM')`), `DIV0` (use `try_divide`), and `SYSDATE()` (use `current_timestamp()`).
It may also note that `NVL`, `IFF`, `DATEADD`, and `QUALIFY` work as-is.
**Checkpoint:** all four incompatibilities are listed.
**If stuck:** ask the follow-up "Which functions in this query don't exist in Databricks SQL?"

## Stage 3: Fix the syntax (5 min)

**Prompt:**
> Fix the syntax errors and adapt this for Databricks SQL. Keep the logic the same.

**Expected:** the view is created. Then run:
`SELECT COUNT(*) FROM <my_schema>.property_performance_v` → **176**.
**Checkpoint:** 176 rows. That's suspicious: 8 properties × 8 quarters should be 64.
**If stuck:** copy the syntax lines from the reference view (`SHOW CREATE TABLE <catalog>.<schema>.ref_d03_property_performance_v`), but keep your join as it is.

## Stage 4: Why are there duplicate rows? (5 min)

**Prompt:**
> Why does this view return 176 rows when there are 8 properties and 8 quarters? Are there duplicate rows?

**Expected:** Genie Code spots the join `ON g.region_name = p.region_name`: each property row matches
every property in its region (3 in Southeast, 2 in Northeast, 3 in Western Europe), and `property_name`
comes from the wrong side of the join. Fix: `ON g.property_id = p.property_id`.
**Checkpoint:** after the fix, `COUNT(*)` = **64** and `COUNT(DISTINCT property_id, fiscal_quarter)` = 64.
**If stuck:** "Compare row counts with and without the join to silver_properties."

## Stage 5: Add YoY (7 min)

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

## Stage 6: Verify (5 min)

**Prompt:**
> Write a query that checks my view against <catalog>.<schema>.ref_d03_property_performance_v row by row and returns any differences.

**Expected:** an `EXCEPT` or full-outer-join check returning 0 rows (ignore `refreshed_at`).

## Wrap-up
- **So what:** the migration is a conversation. Genie Code found the 4 incompatible functions and a join bug that was already wrong in Snowflake.
- **Snowflake equivalent:** Snowflake Copilot explains and drafts SQL. Genie Code also fixes, runs, and checks against governed tables in the same editor.
- **Verified:** 2026-10-08 on the FEVM workspace: broken view fails on `NUMBER`; syntax-fixed/join-unfixed = 176 rows; reference = 64 rows; Harbor Tower 2026-Q2 YoY −478,309.66. Genie Code prompt responses: UI verification pending (S9).
