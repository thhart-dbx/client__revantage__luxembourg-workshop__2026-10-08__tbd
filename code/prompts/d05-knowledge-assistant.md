# Demo 5: Knowledge Assistant — "Ask the Policy Book"

**Session:** Day 1, 11:45–12:15 (30 min) · **You build:** a Knowledge Assistant over the group policies · **Reference:** agent `revantage-policy-assistant` (endpoint `ka-234e391f-endpoint` on the FEVM; a new ID in your workspace)
**Starting state:** 4 policy PDFs in `/Volumes/<catalog>/<schema>/documents/policies/` (Expense Approval, Capital Expenditure Guidelines, Lease Renewal Procedures, Intercompany Transfer); ground truth `code/documents/out/policies_qa_ground_truth.md`
**Where:** Agents → Create Agent → Knowledge Assistant

**Timing reality (measured 2026-10-08):** the form takes ~3 minutes; the endpoint and vector index then take
**~15–25 minutes** before the first answer. Until then questions fail with "Vector index … is not ready".
**Start the build at the beginning of Demo 4** (11:00) so it's ready at 11:45, or use the reference agent while yours indexes.

## Stage 1: Create (3 min, start it early)
**Agents → Create Agent → Knowledge Assistant.**
- **Name:** `policy-assistant-<your_name>` (letters, numbers, dashes; ≤ 64 characters; clear the default name first)
- **Description:**
  > Answers questions about Revantage Europe group policies: expense approval thresholds, capital expenditure vs operating expense classification, lease renewal procedures, and intercompany transfers. Always cite the policy and section.
- **Knowledge source:** Type *Files in a Volume* → Source → *All volumes* → `documents` → expand → **policies** → Select. Name `revantage_group_policies`.
- **Describe the content:**
  > Four Revantage Europe group policy PDFs with numbered sections: Expense Approval Policy (delegation of authority and approval thresholds in EUR), Capital Expenditure Guidelines (CapEx vs OpEx rules, depreciation), Lease Renewal Procedures (180/120/90/30-day steps), Intercompany Transfer Policy (recharges, settlement, reconciliation).

**Create Agent.** **If stuck:** "REQUEST_LIMIT_EXCEEDED" → wait a few seconds and click Create again; if the button spins for minutes, reload, re-enter, and check the agent list first (it may already exist).

## Stage 2: Ask the three business questions (10 min)
In the agent's **Test** panel (or the reference agent while yours indexes):
> What is the approval threshold for expenses over €50,000?

**Expected:** co-signature of the **CFO and the Asset Management Director**, two different people, with supporting documentation. Cites `expense-approval-policy.pdf`.
> If a tenant's lease expires in 90 days, what steps should I take?

**Expected:** Day-90 step: formal written notice by registered letter if there's no response to the renewal proposal, escalate to the Head of Asset Management, start re-letting marketing in parallel; final decision at day 30. Cites `lease-renewal-procedures.pdf`.
> Is a new HVAC system for Harbor Tower classified as CapEx or OpEx?

**Expected:** **CapEx**: replaces a building system, > €25,000, useful life 20 years (> 3); routine servicing would be OpEx. Cites `capital-expenditure-guidelines.pdf`.
**Land it:** Demo 4 showed this exact chiller (HV-2026-0417, €312k) booked to **Repairs & Maintenance (OpEx)**. That's why Harbor Tower "missed" its Q2 target by €43k. The policy says reclassify it.

## Stage 3: Citations and follow-ups (5 min)
Open the citation on each answer: it links to the source PDF passage. Try:
> What credit rating threshold requires Head of Asset Management sign-off for lease renewal?

**Expected:** tenants rated **below BB**.

## Stage 4: Share and use from SQL (7 min)
- **Share:** agent page → Permissions → add the team (Can Query). Anyone with access can use it in the Playground or through the endpoint.
- **From SQL** (the "agents scale to production via SQL" point):
```sql
SELECT ai_query('<your KA endpoint name>',
  'Does invoice HV-2026-0417 (USD 339,600 chiller replacement) need CFO approval? Answer in one sentence.') AS answer
```
**Expected:** "Yes … exceeds the €50,000 threshold that requires co-signature of the CFO and Asset Management Director."
**Prompt** (Genie Code, SQL editor):
> Use ai_query with my Knowledge Assistant endpoint to add a column policy_check to <catalog>.<schema>.ref_invoices_extracted that says, for each invoice, which approvers it needs under the Expense Approval Policy.

## Stage 5: Tour of other agent types (5 min, show)
In **Create Agent** point out: **Information Extraction** (Demo 4), **Document Parsing**, **Text Classification**,
**Supervisor Agent** (combine Genie Agents, Knowledge Assistants, and MCP tools, e.g. "Portfolio Q&A + Policy Assistant"),
**Knowledge Assistant**, **code your own agent** (Apps template), **Genie Agent**.

## Wrap-up
- **So what:** policies answer themselves, with citations, and the same agent works from chat, SQL, and other agents.
- **Snowflake equivalent:** Cortex Search + Cortex Agents. On Databricks the Knowledge Assistant is built from a volume in minutes, governed in Unity Catalog, and callable from SQL with ai_query.
- **Verified:** 2026-10-08 on the FEVM workspace. Agent built in the browser at 15:54 (first create hit a rate limit); index ready in ~25 min. All 6 ground-truth questions answered correctly with the right PDF cited (`verification/raw/d05-ka-2026-10-08.txt`); `ai_query` from SQL verified. Stage 4's Genie Code prompt: UI verification pending (S9).
