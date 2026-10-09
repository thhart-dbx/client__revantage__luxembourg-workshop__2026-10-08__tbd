"""Build the click-path walkthrough and the participant handout from the 16 verified guides.

The guides in code/prompts/ are the single source of truth (every prompt in them was run in the
Genie Code UI, see code/prompts/verification/s9-genie-code-ui.md). This script compiles them into:
  assets/click-path.md   facilitator walkthrough: every stage, checkpoint, watch-out, screenshot
  assets/participant-handout.md   what participants need: prompts, checkpoints, fallbacks only
and renders both to .docx with pandoc.

Usage (from the project root): python3 code/deliverables/build_docs.py
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "code" / "prompts"
ASSETS = ROOT / "assets"
SHOTS = "../notes/agent-notes/screenshots"  # relative to assets/

# One live screenshot per demo (captured with Chrome DevTools against the deployed objects).
SCREENSHOTS = {
    1: ("architecture.png", "Everything the workshop builds, on one governed dataset."),
    2: (f"{SHOTS}/d02-genie-southeast.png", "Genie One answers the Southeast question: Harbor Tower drives the whole drop."),
    3: (f"{SHOTS}/s9-d03-genie-code.png", "Genie Code explains the Snowflake view and lists what to change for Databricks SQL."),
    4: (f"{SHOTS}/d04-extraction.png", "The Information Extraction agent reads every invoice into typed fields."),
    5: (f"{SHOTS}/d05-ka-building.png", "The Knowledge Assistant indexes the four policy PDFs."),
    7: (f"{SHOTS}/d07-metric-view.png", "The approved net profit margin as a Unity Catalog metric view, with its measures documented."),
    8: (f"{SHOTS}/d08-p1-executive.png", "The Executive Summary page: €10.7M revenue, 59.3% margin, 62.5% target attainment."),
    9: (f"{SHOTS}/d09-app.png", "The lease expiry tracker: windows, risk, rent at risk, CSV export."),
    11: (f"{SHOTS}/d11-pipeline-graph.png", "The reference pipeline graph: 7 Auto Loader sources → bronze → silver → gold."),
    12: (f"{SHOTS}/d12-approvals-app.png", "Invoice approvals on Lakebase: the €312k chiller waits for a second approver."),
    13: (f"{SHOTS}/d13-ai-gateway.png", "AI Gateway on the Claude endpoint: usage tracking and the inference table."),
    14: (f"{SHOTS}/d08-p4-forecast.png", "Forecast page: actuals, ai_forecast with its interval, and the target."),
}

# Lines a participant shouldn't see (facilitator-only).
FACILITATOR = re.compile(r"^\*\*(Watch for|Teach|Verified|Note)\b|seen in pre-build|^- \*\*Verified|"
                         r"^- \*\*Snowflake equivalent|facilitator|pre-build|^\(In the pre-build", re.I)


def parse(path):
    text = path.read_text()
    title = text.splitlines()[0].lstrip("# ").strip()
    num = int(re.match(r"Demo (\d+)", title).group(1))
    header, stages, wrap = [], [], []
    cur = None
    for line in text.splitlines()[1:]:
        if line.startswith("## Wrap"):
            cur = {"title": "Wrap-up", "lines": wrap}
        elif line.startswith("## "):
            cur = {"title": line[3:].strip(), "lines": []}
            stages.append(cur)
        elif cur is None:
            header.append(line)
        else:
            cur["lines"].append(line)
    return num, title, header, stages, wrap


def heading(i, title):
    return title if re.match(r"(Stage|Track) ", title) else f"{i}. {title}"


def demote(lines):
    return "\n".join(lines).strip()


def click_path(guides):
    out = ["# Revantage Luxembourg workshop: build-along click-path", "",
           "Two days, 16 demos, one dataset. Every participant builds each asset in their own schema "
           "(`<my_schema>`), guided by Genie Code; the finished answer key is deployed as `ref_*` objects. "
           "Each demo below is a Critical User Journey: numbered stages with the exact prompt, the expected "
           "result, the checkpoint, and the recovery path. Every prompt was run in the Genie Code UI on "
           "2026-10-08/09 (log: `code/prompts/verification/s9-genie-code-ui.md`).", "",
           "Placeholders: `<catalog>` and `<schema>` are the shared workshop catalog and schema "
           "(`revantage_20261008`); `<my_schema>` is your sandbox schema; `:workspace_id` is the number after "
           "`?o=` in your browser URL.", "",
           "![Architecture](architecture.png)", "", "## Contents", ""]
    for num, title, *_ in guides:
        out.append(f"- [{title}](#demo-{num})")
    for num, title, header, stages, wrap in guides:
        out += ["", f'<a id="demo-{num}"></a>', f"## {title}", "", demote(header), ""]
        if num in SCREENSHOTS:
            img, cap = SCREENSHOTS[num]
            out += [f"![{cap}]({img})", "", f"*{cap}*", ""]
        for i, st in enumerate(stages, 1):
            out += [f"### {heading(i, st['title'])}", "", demote(st["lines"]), ""]
        if wrap:
            out += ["### Wrap-up", "", demote(wrap), ""]
    return "\n".join(out).replace("\n\n\n", "\n\n")


def handout(guides):
    out = ["# Revantage workshop: participant handout", "",
           "You build every asset yourself in **your own schema** (`<my_schema>`). For each step: type the "
           "prompt into Genie Code, compare with the checkpoint, and if you're stuck open the finished "
           "reference (objects named `ref_…` or titled \"(Reference)\").", "",
           "| Placeholder | Means |", "|---|---|",
           "| `<catalog>.<schema>` | the shared workshop data (given by your facilitator) |",
           "| `<my_schema>` | your sandbox schema |",
           "| `:workspace_id` | the number after `?o=` in your browser URL |", "",
           "**Tip:** end every prompt that creates something with *\"run it and check the result\"*.", ""]
    for num, title, header, stages, _ in guides:
        out += [f"## {title}", ""]
        where = [l for l in header if l.startswith("**Where") or l.startswith("**Session")]
        out += [demote(where), ""]
        for i, st in enumerate(stages, 1):
            if re.match(r"(Reset|Stage \d+: Clean up)", st["title"]):
                continue                     # facilitator-only steps
            keep, in_code, skipping = [], False, False
            for l in st["lines"]:
                if l.startswith("```"):
                    in_code = not in_code
                    if not skipping:
                        keep.append(l)
                    continue
                if in_code:
                    if not skipping:
                        keep.append(l)
                    continue
                if FACILITATOR.search(l):
                    skipping = True          # drop the whole facilitator paragraph
                    continue
                if skipping and (not l.strip() or l.startswith("**") or l.startswith(">")):
                    skipping = False
                if not skipping:
                    keep.append(l)
            body = demote(keep)
            if body:
                out += [f"### {heading(i, st['title'])}", "", body, ""]
    out += ["## Appendix: the Snowflake view for Demo 3", "", "```sql",
            (ROOT / "code" / "sql" / "d03_snowflake_property_view.sql").read_text().strip(), "```", ""]
    return "\n".join(out).replace("\n\n\n", "\n\n")


def docx(md):
    subprocess.run(["pandoc", md.name, "-o", md.with_suffix(".docx").name,
                    "--resource-path", ".", "--toc", "--toc-depth=2"], cwd=ASSETS, check=True)


if __name__ == "__main__":
    guides = sorted((parse(p) for p in PROMPTS.glob("d[0-9][0-9]-*.md")), key=lambda g: g[0])
    for name, fn in (("click-path.md", click_path), ("participant-handout.md", handout)):
        p = ASSETS / name
        p.write_text(fn(guides))
        docx(p)
        print("wrote", p, "and", p.with_suffix(".docx"))
