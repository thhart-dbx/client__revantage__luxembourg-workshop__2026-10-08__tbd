---
paths:
  - "assets/**"
  - "README.md"
---

# Deliverables (Definition of Done for the demo)

The demo isn't finished until all five deliverables exist in `assets/` and reflect the built demo.
They embed live screenshots, so produce or refresh them after the assets are deployed and working.
Capture screenshots with the Chrome DevTools MCP against the deployed workspace objects, never
mockups, and choose populated, compelling frames rather than empty states. Refresh the deliverables
when the demo changes materially (a new surface, changed UX, new assets on the architecture).

1. **Click-path walkthrough** — `assets/click-path.md` (source, git-diffable) rendered to
   `assets/click-path.docx`. A step-by-step narration of each Critical User Journey: numbered
   steps, each with an annotated screenshot and a sentence on what it shows. This is the walkthrough
   a person reads or presents; the Playwright specs are the automated check of the same paths.

2. **Internal enablement deck** — `assets/<demo>-internal.pptx`, built with the
   `databricks-slides:slide-deck` skill (Databricks template). Audience: Databricks colleagues
   (SA/SSA/AE) who will re-deliver the demo. For each scenario, cover the problem, what the demo
   shows, the key value proposition, and "Why Databricks?" (how the platform uniquely solves it, the
   differentiation and not just the feature). Include live screenshots of the dashboards, Genie
   spaces, and app, plus the architecture diagram.

3. **External client deck** — `assets/<demo>-client.pptx`, same skill. Audience: the customer.
   Narrative: problem / status quo → the Databricks solution → live screenshots as proof → business
   outcomes → next step. Keep the tone customer-appropriate, with no internal competitive positioning.

4. **Architecture diagram** — `assets/architecture.png` plus its source, built with
   `fe-workflows:fe-architecture-diagram` (if that isn't installed, use
   `fe-specialized-agents:drawio-diagram` or `excalidraw-diagram:create-diagram`). It shows and links
   every Databricks object in `README.md > Assets Created`: tables, views, functions, pipelines, jobs,
   dashboards, Genie spaces, the app, Lakebase, endpoints, volumes. Each inventoried asset must appear.
   (`notes/agent-notes/architecture.mmd` is only an internal working sketch.)

5. **README hero screenshot** — `assets/hero.png`, embedded near the top of `README.md`. The
   subject is the first of these the demo has: the app, a Genie space, a dashboard, a notebook.

## README asset inventory

`README.md > Assets Created` lists every Databricks object the demo creates, with its fully
qualified location (`catalog.schema.table`, workspace path, app URL). Tables, views, volumes, and
functions go under **Data Assets**; everything else goes under **Workspace Assets**. Add an entry
when an asset is created and remove it when the asset is deleted. Every entry must be produced by a
step in RUNBOOK.md.
