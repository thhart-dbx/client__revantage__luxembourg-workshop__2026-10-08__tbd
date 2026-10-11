# Demo 18: Domains, Pages & Metrics — "Teach Genie One what your words mean"

**Session:** Day 2, 3:20–3:45 (25 min) · **You build:** a Page (business definition) in the Revantage domain, linked to its governed metric view, and check that Genie One uses it · **Reference:** the four Pages in `code/reference/d18_pages.md` (Net profit, Latest quarter, Active lease, Below investment grade), published by the facilitator in the domain "Revantage Workshop"
**Starting state:** domain **Revantage Workshop** (governed tag `Revantage Workshop`, created by `code/scripts/d18_domain.sh`), participants with MANAGE on the domain; the Demo 7 metric views `ref_mv_*` (the domain's *Metrics*); the Demo 17 tables
**Where:** Discover (Domains, Pages); Genie One (Switch apps → Genie One, or the home page **Ask** box)

The story: Demo 17 made one Genie Agent accurate. Genie One answers across *everything* you can see,
so it needs the business meaning to live where all tools find it. **Domains** organize assets by business
area, **Pages** explain a term (definition, synonyms, related assets), **metric views** calculate it, and
**certification** says which asset to trust. Genie One searches them together (the *Genie Ontology*)
and prefers a Page's human-written definition, but only when the trust signals agree.

## Stage 1: Tour the domain (4 min)
**Discover** → **Browse by domain** → **Revantage Workshop**: the domain's assets, **Featured Metric views** (the `ref_mv_*` views: the domain's *Metrics*), **Pages**, and **Ask Genie** (a Genie scoped to the domain).
**Teach:** a domain is backed by a governed tag; tagging a table, metric view, dashboard or Genie Agent with it (or **Add to domain**) puts it in the domain. Pages inherit the domain's permissions.

## Stage 2: Ask before you define (4 min)
**Prompt** (Genie One, new chat):
> What is our NOI this quarter?

**Expected:** open **Thought process**: Genie One searches the ontology ("Found … ontology results"), picks a metric view and a quarter, and shows its sources. Check *which* definition and *which* quarter it used. Without a Page it has to guess that NOI means net profit and that "this quarter" means the latest complete quarter (2026-Q2), not the calendar quarter.

## Stage 3: Write the Page with Genie Code (8 min)
**Discover → Create → Create page** → in the Genie Code panel click **Help me create a new page** (or type):
> Help me create a page "Net profit (<your_name>)" in the Revantage Workshop domain. Description: Revantage's approved Finance net profit: revenue minus operating expense minus management fee; CapEx and intercompany recharges are not deducted. Definition: per property and fiscal quarter in EUR; in the general ledger account_class R - O - M. "This quarter" means the latest complete fiscal quarter in the workshop data, 2026-Q2. The authoritative source is the metric view <catalog>.<schema>.ref_mv_net_profit_margin over gold_property_quarterly. Synonyms: NOI, net operating income, bottom line. Related assets: <catalog>.<schema>.ref_mv_net_profit_margin and <catalog>.<schema>.gold_property_quarterly. Fill in the page fields but don't publish.

**Expected:** Genie Code finds the domain and fills the form: name, domain, 3 synonyms, description, a body with *Definition*, *Authoritative source* and *Business use*, and both **Related assets** (the metric view and the table). Review it → **Save as draft** (a draft is used for you only; the facilitator's published Pages are used for everyone).
**If stuck:** copy the "Net profit" entry of `code/reference/d18_pages.md` into the form by hand.
**Watch for:** Page content is stored in plain text and replicated globally: never put PII or confidential figures in a Page.

## Stage 4: Ask again (4 min)
**Prompt** (Genie One, **new** chat, so it doesn't reuse the previous one):
> What is our NOI this quarter?

**Expected:** **Thought process** shows **Read info for: knowledge_page…** and the answer says NOI is net profit "per the glossary page". With the Page and a single certified metric view, the expected answer is **€6,375,345.36 for 2026-Q2** from `ref_mv_net_profit_margin` (to confirm in the Revantage workspace pre-flight).
**Teach:** if Genie One still prefers another asset, it tells you why in the thought process ("two competing sources of truth"): another *certified* view with a different definition or later data. The fix is trust hygiene, not a better prompt: certify the right metric view (`system.certification_status`, Demo 10), deprecate the other, and list the right one as the Page's related asset.

## Stage 5: Metrics in the domain, and what Pages don't do (5 min)
- **Domain → Add to domain** (or `ALTER VIEW … SET TAGS ('Revantage Workshop')`): add your Demo 7 metric views; they appear under the domain's metric views. Then try the domain's **Ask Genie**: it answers from the domain's assets only.
- **Pages feed Genie One and Genie Code, not Genie Agents.** A Genie Agent answers from its own data and configuration: the same Demo 17 agent without metric views or instructions scored **50% with and without** the Net profit Page. For an agent, the definition goes into comments, metric views and instructions (Demo 17); for everyone else, into a Page.

## Reset (facilitator, after the session)
Delete participants' draft Pages (Discover → Pages → Owned by … → ⋮ → Delete) or leave them: drafts are private to their owner. The reference Pages and the domain stay until teardown (`code/scripts/d18_domain.sh --teardown`).

## Wrap-up
- **So what:** one place for what your words mean. Write the definition once (Page), compute it once (metric view), trust it once (certification), organize it by business area (domain); every Genie surface then answers the same way.
- **Snowflake equivalent:** Horizon catalog tags and semantic views; here the business glossary, the metric layer and the AI assistant share one ontology in Unity Catalog.
- **Verified:** 2026-10-10 on the FEVM workspace (the account is at its governed-tag limit, so no new domain there; the Page was created as a draft in an existing domain): Genie Code filled the Page form from the Stage 3 prompt (domain, 3 synonyms, description, body, 2 related assets) and the draft saved. Genie One then read it ("Read info for: knowledge_page.68801114…", NOI "synonymous with net profit per the glossary page"), but on FEVM kept another project's *certified* `net_profit_metrics` view with later data (2026-Q3, €54.5M) and said so: the conflicting-trust case of Stage 4. Genie Agent check: 10/20 with the Page, 10/20 without (`code/tests/score_genie.py`). **Pending (Revantage workspace):** domain creation by script, Add to domain, the domain's Ask Genie, and Stage 4's clean answer without a competing certified view.
