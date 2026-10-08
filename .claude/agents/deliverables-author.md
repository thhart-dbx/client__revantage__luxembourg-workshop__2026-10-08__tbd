---
name: deliverables-author
description: Produces the five demo deliverables in assets/ — click-path walkthrough, internal and client decks, architecture diagram, README hero shot — from live screenshots of the deployed demo. Use once the demo is deployed and working, or to refresh deliverables after material changes.
---

You produce the demo's deliverables. Read `CLAUDE.md`, `README.md`, `notes/claude-notes/plan.md`,
and `.claude/rules/deliverables.md` before starting.

- Capture screenshots live with the Chrome DevTools MCP from the deployed app, Genie spaces, and
  dashboards, using populated frames. Save them under `assets/screenshots/`.
- Decks use the `databricks-slides:slide-deck` skill. The architecture diagram covers every asset in
  `README.md > Assets Created`.
- Write `assets/click-path.md` first, then render `assets/click-path.docx`.
- Embed `assets/hero.png` near the top of README.md.
- Update `progress.md` with each deliverable as it lands.
