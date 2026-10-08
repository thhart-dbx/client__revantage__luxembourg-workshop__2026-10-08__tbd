---
paths:
  - "notes/**"
---

# Planning, parallel execution & progress

`notes/claude-notes/plan.md` and `progress.md` let any session, on any machine, pick up exactly where
the last one stopped. Keep them accurate rather than long.

## plan.md

Write it before building, and update it as the plan changes:

- **CUJs**: the Critical User Journeys the demo must show (each gets a Playwright spec and a
  click-path section).
- **Steps**: a dependency table. The owner is a subagent from `.claude/agents/`. Steps in the same
  parallel group run at the same time.

  | Step | Owner | Task | Depends on | Group |
  |------|-------|------|------------|-------|
  | 1 | data-engineer | Schema + synthetic data job | — | A |
  | 2 | data-engineer | SDP pipeline → gold tables | 1 | B |
  | 3 | app-builder | App shell + layout (mock data) | — | A |
  | 4 | deployer | Dashboard + Genie space | 2 | C |
  | 5 | app-builder | Wire app to gold tables | 2, 3 | C |
  | 6 | deployer | Clean deploy + smoke + Playwright | 4, 5 | D |
  | 7 | deliverables-author | Screenshots, decks, click-path, architecture | 6 | E |

- **Expectations** per asset: inputs, outputs, side effects, how it fits the data flow, and what
  success looks like. Testing checks against these.

## Running it

- Launch every step whose dependencies are met in one message (multiple Agent calls). Don't
  serialize independent work, and don't wait for a whole group to finish if a later step is
  already unblocked.
- Give each subagent its task, the relevant config (catalog, schema, profile, warehouse), and the
  files from earlier steps it should read. Subagents start fresh, without this conversation.
- Agents share state through files (`progress.md`, `notes/agent-comms/thread.md`), not by waiting on each other.
- Typical shape: setup → fan out → fan in to deploy + test.

## progress.md

Update it at every step transition, because it is what a new session resumes from.

```markdown
# Progress — <task>
Status: in-progress | complete | blocked · Last updated: YYYY-MM-DD HH:MM · Current group: C

| Group | Steps | Status |
|-------|-------|--------|
| A | 1, 3 | DONE |
| B | 2 | DONE |
| C | 4, 5 | IN PROGRESS (4 done, 5 in progress) |

## Steps
- [x] 4 · deployer · Dashboard + Genie — out: `code/resources/dashboard.yml`, `genie.yml`
- [ ] **>>> 5 · app-builder · Wire app to gold tables — IN PROGRESS <<<** (2 of 3 pages)

## Blockers
| Step | Blocker | Resolution |

## Artifacts
| Artifact | Type | Location | Status |
```

Record each artifact as soon as it exists and each blocker as soon as it's hit, with enough context
for a fresh session to understand it.

## Resuming

Read `progress.md`, then `plan.md`. Relaunch every pending or in-progress step in the current group
(and any later step that's already unblocked) in parallel, without redoing completed steps. Tell the
user: "Resuming at group X. Done: … Launching: …".
