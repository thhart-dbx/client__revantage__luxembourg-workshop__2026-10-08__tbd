# Demo 10: Unity Catalog & Governance — "Who can see what, and why?"

**Session:** Day 1, 4:15–4:45 (30 min) · **You build:** business metadata, a certification, and PII masks on the gold layer · **Reference:** `code/reference/d10_governance.sql` (apply) and `d10_reset.sql` (back to the starting state)
**Starting state:** `gold_property_quarterly` ships with **no table description** and **no comments** on `net_profit`, `met_target`, `qoq_change_pct`; `customer_performance` has unmasked tenant emails and phones
**Where:** Catalog Explorer, SQL editor with Genie Code

## Stage 1: Look before you touch (5 min)
Catalog → `<catalog>` → `<schema>` → `gold_property_quarterly`: **Overview** (owner, no description), **Details**, **Permissions**, **Lineage** (upstream silver tables, downstream metric views, the Portfolio Review dashboard, the Genie Agents).

## Stage 2: Describe it for business users (8 min)
In Catalog Explorer use **AI generate** on the description, or in the SQL editor:
**Prompt** (Genie Code):
> Write a description for <catalog>.<schema>.gold_property_quarterly suitable for a non-technical business user, and column comments for net_profit, met_target and qoq_change_pct. Give me the SQL to apply them.

**Expected:** `COMMENT ON TABLE … IS '…'` and `ALTER TABLE … ALTER COLUMN net_profit COMMENT '…'` (not TBLPROPERTIES). Net profit must say: revenue minus operating expenses minus management fees; capex and intercompany not deducted.
**Checkpoint:** `DESCRIBE TABLE EXTENDED <catalog>.<schema>.gold_property_quarterly` shows the comment; Genie answers improve because it reads these.

## Stage 3: Certify it (3 min)
```sql
ALTER TABLE <catalog>.<schema>.gold_property_quarterly SET TAGS ('system.certification_status' = 'certified');
```
**Expected:** a **Certified** badge in Catalog Explorer and search. Free-form keys like `data_owner` may be blocked by a governed tag policy ("not an allowed value"); that's governance working.

## Stage 4: Mask PII (8 min)
**Prompt:**
> Create a column mask function that shows the full email only to members of revantage_finance_stewards and otherwise the first letter plus the domain, a similar one for phone numbers showing only the last 3 digits, and apply them to contact_email and contact_phone on <catalog>.<schema>.customer_performance. Tag both columns with the PII classes.

**Expected:** two SQL UDFs with `is_account_group_member(...)`, `ALTER TABLE … ALTER COLUMN contact_email SET MASK …`, tags `class.email_address` / `class.phone_number`.
**Checkpoint:** `SELECT contact_email, contact_phone FROM <catalog>.<schema>.customer_performance LIMIT 1` → `l***@nimbus.example.com | *** *** 597` for you (you're not in the stewards group).

## Stage 5: Permissions and sharing (4 min)
**Permissions** tab: SELECT for `revantage_consumers` inherited from the schema; `SHOW GRANTS ON TABLE …`. The same group has CAN_RUN on the Genie Agents and CAN_READ on the dashboard, so permissions follow the data. Mention the AI Gateway (Demo 13): model access is governed in the same place.

## Reset (facilitator, after the session)
Run `code/reference/d10_reset.sql`: removes the description, the 3 comments, the tags, and the masks, so the next group starts clean.

## Wrap-up
- **So what:** governance is in the product: descriptions make Genie smarter, certification tells people what to trust, and masks follow the data everywhere it's used.
- **Snowflake equivalent:** object tagging, masking policies, and data classification. UC applies them uniformly across tables, dashboards, Genie, apps, and AI, with lineage.
- **Verified:** 2026-10-08 on the FEVM workspace: reference apply → comments, certified tag, PII class tags, masks (`l***@nimbus.example.com`, `*** *** 597`) confirmed via information_schema and a query; reset → all removed, unmasked values back (`code/tests/check_d10.py`). Genie Code prompts: UI verification pending (S9).
