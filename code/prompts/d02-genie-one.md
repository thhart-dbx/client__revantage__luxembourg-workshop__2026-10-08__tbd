# Demo 2: Genie One — Property Performance Q&A

**Session:** Day 1, 9:30–10:15 (45 min) · **You build:** five answered, shareable business questions · **Reference:** Genie Agent "Revantage Portfolio Q&A (Reference)"
**Starting state:** Genie Agent "Revantage Portfolio Q&A (Start)" over `gold_property_quarterly`, `silver_properties`, `bronze_properties`, `silver_leases`, `silver_tenants`
**Where:** Genie One (browser), then the desktop/mobile app if installed

Open the Start agent from Genie One (left nav **Genie** → *Revantage Portfolio Q&A (Start)*). Ask each
question, then open **Show thinking** and **Show code** on every answer. That's the habit to build:
read the SQL behind the number.

## Stage 1: Who missed target? (6 min)

**Prompt** (Genie One):
> Which properties missed their quarterly target in 2026-Q2?

**Expected:** 3 properties: Peachtree Center (−€71,293), Harbor Tower (−€43,235), Zuidas Residences (−€41,702).
**Checkpoint:** open *Show code*: `WHERE fiscal_quarter = '2026-Q2' AND met_target = false` on `gold_property_quarterly`.
**If stuck:** ask the same question in the Reference agent; it answers from the metric view `ref_mv_target_attainment`.

## Stage 2: What changed in the Southeast? (8 min)

**Prompt:**
> What changed from Q1 to Q2 for the Southeast region?

**Expected:** revenue down ~€267k (−6.4%), operating expense up ~€221k, net profit €2.58M → €2.09M (−18.6%).
Then follow up in the same thread:
> Which property drove that, and was it revenue or costs?

**Expected:** **Harbor Tower**, net profit −€507k: revenue −€321k (anchor tenant left on 31 March) and costs +€185k.
**Checkpoint:** Harbor Tower is the only Southeast property whose net profit fell.
**If stuck:** in the Reference agent, ask "Why did Southeast net profit drop in Q2?".

## Stage 3: Charts (6 min)

**Prompt:**
> Show me revenue by property type as a bar chart

**Expected:** bar chart: Office €46.7M, Multifamily €37.2M, Retail €19.7M (all quarters). Ask
"Only for 2026-Q2" to refine; use the chart menu to switch type.

## Stage 4: Growth (5 min)

**Prompt:**
> Which market has the highest quarter-over-quarter net profit growth?

**Expected:** **Luxembourg City, +10.0%** (2026-Q2 vs Q1).
**Checkpoint:** *Show code* compares 2026-Q2 with 2026-Q1. The agent's instructions set that default;
without them Genie ranked every quarter in history (Boston 2024-Q4). That's the lesson for Demo 13 (context matters).

## Stage 5: Risks (8 min)

**Prompt:**
> Summarize the top 3 risks across the portfolio this quarter

**Expected (Start agent):** target misses (€156k shortfall across 3 properties), one QoQ decline. Grounded but shallow.
Ask the same in the **Reference** agent: 14 leases expiring within 180 days, 3 missed targets, 1 QoQ decline. Same data, better context.

## Stage 6: Share and take it with you (7 min)

- **Share** the thread with a colleague (share icon, top right): they see the same answers and SQL.
- Show the **desktop** and **mobile** apps, the **Slack / Microsoft 365** connectors, attaching a file
  to a question (e.g. the Q2 board pack PDF from `documents/`), and **scheduling** a question
  ("Every Monday 8:00, which properties are behind target?"). Facilitator demo; check what's enabled
  in the workspace first (pre-flight).

## Wrap-up
- **So what:** a portfolio manager got five board-ready answers in minutes, each with the SQL to prove it.
- **Snowflake equivalent:** Cortex Analyst answers over a semantic model; Genie One adds threads, charts, sharing, and the agent context you'll govern in Demo 7.
- **Verified:** 2026-10-08 via the Genie Conversation API on both agents; transcript in `verification/raw/d02-genie-start-2026-10-08.txt`, summary in `verification/d02-d06-d07-genie.md`. Desktop/mobile, connectors, attachments, schedules: UI verification pending (S9).
