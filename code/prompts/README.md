# Genie Code prompt library

One file per demo (`d01-platform-overview.md` … `d16-data-quality.md`). Participants copy prompts
from these files during the workshop; facilitators use the expected results and "if stuck" steps to
keep the room moving. The click-path and decks quote these files, so this is the source of truth.

Every prompt in this library was run in the live product during pre-build, and the result recorded.
A prompt that doesn't reliably produce the expected result is rewritten or marked
**Facilitator demo only**.

## Placeholders

| Placeholder | Meaning |
|---|---|
| `<catalog>.<schema>` | Where the starting data lives in your workspace (set by the setup job) |
| `<my_schema>` | Your personal sandbox schema, if the facilitator created one; otherwise `<schema>` |
| `<your_name>` | Short lowercase name, used to suffix the objects you create |

## File format

```markdown
# Demo NN: <title>

**Session:** Day N, HH:MM–HH:MM (NN min) · **You build:** <the asset> · **Reference:** <ref asset name>
**Starting state:** <tables / volumes / files that must already exist>
**Where:** <SQL editor | notebook | Genie One | Agent Bricks | pipeline editor | dashboard | Apps>

## Stage 1: <name> (N min)

**Prompt** (Genie Code, <surface>):
> <exact text to paste>

**Expected:** <what appears, with the planted numbers from notes/agent-notes/data-contract.md>
**Checkpoint:** <one query or click that proves the stage worked>
**If stuck:** <recovery: a smaller prompt, or open/copy the reference asset>

## Stage 2: …

## Wrap-up
- **So what:** <one line for the business audience>
- **Snowflake equivalent:** <where relevant>
- **Verified:** YYYY-MM-DD on <workspace>, Genie Code results recorded in `verification/dNN.md`
```

`verification/` holds the recorded transcript and screenshot reference for each prompt run.
