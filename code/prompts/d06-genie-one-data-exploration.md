# Demo 6: Genie One Data Exploration — "Audit your data before you trust it"

**Session:** Day 1, 12:15–12:30 (15 min) · **You build:** a recurring quality check from Genie's SQL · **Reference:** view `<catalog>.<schema>.ref_d06_property_quality_checks`
**Starting state:** Genie Agent "Revantage Portfolio Q&A (Start)" (includes `bronze_properties`); `silver_properties`, `gold_property_quarterly`
**Where:** Genie One, then SQL editor with Genie Code

Fast-paced: one question per ~2 minutes. After each answer open **Show code**.

## Stage 1: Layer counts (2 min)
**Prompt** (Genie One):
> How many properties are in the bronze layer vs. the gold layer?

**Expected:** bronze **10**, gold **8**.

## Stage 2: What got dropped (2 min)
**Prompt:**
> Which properties exist in bronze but not in gold?

**Expected:** id 9 **Riverside Annex** (Charlotte) and id 10 **Harbor Tower** (Miami Bch), both with no region.

## Stage 3: Completeness (2 min)
**Prompt:**
> Show me the null rate for every column in bronze_properties

**Expected:** `region_id` **20%** (2 of 10). `_rescued_data` 100% NULL: that's Auto Loader's column for
values that didn't fit the schema, and all-NULL is good news.

## Stage 4: Duplicates (2 min)
**Prompt:**
> Are there any duplicate property names with different IDs?

**Expected:** **Harbor Tower**, ids **3** and **10**. Id 10 is the bad record from Stage 2.

## Stage 5: Cross-source consistency (2 min)
**Prompt:**
> Compare market names between bronze and silver for mismatches

**Expected:** 3: Miami Bch → Miami Beach, NYC → New York, Lux-Ville → Luxembourg City.

## Stage 6: Keep the checks (5 min)
Copy the SQL from Stages 1–5 (Show code → copy) into a SQL editor tab, then:

**Prompt** (Genie Code, SQL editor):
> Combine these five checks into one view <my_schema>.property_quality_checks with columns check_name, observed, issue_count, one row per check.

**Expected:** a view returning 5 rows with issue counts **2, 2, 2, 1, 3**.
**Checkpoint:** `SELECT * FROM <my_schema>.property_quality_checks` matches `SELECT * FROM <catalog>.<schema>.ref_d06_property_quality_checks`.
**If stuck:** `SHOW CREATE TABLE <catalog>.<schema>.ref_d06_property_quality_checks` and copy it.
Teaser for Demo 16: schedule this view as an alert so the next bad load is caught automatically.

## Wrap-up
- **So what:** a 15-minute conversation found every planted issue and produced a reusable check, without writing SQL by hand.
- **Verified:** 2026-10-08. Stages 1–5 via the Genie Conversation API (`verification/d02-d06-d07-genie.md`, raw transcript `verification/raw/d06-genie-start-2026-10-08.txt`); reference view returns 2, 2, 2, 1, 3. Stage 6 Genie Code response: UI verification pending (S9).
