"""Build the module-by-module build-along deck (one module per demo).

Per demo:  section slide → "What we'll build" (overview + finished asset) → "How we'll get there"
(the steps) → one slide per step / per prompt: the prompt to type (or the click-path instruction for
steps without one), the expected result, the fallback, and a screenshot of the expected output.

Text comes from the verified guides in code/prompts/ (facilitator-only notes are dropped); the
screenshots come from code/deliverables/module_manifest.py. Usage (from the project root):
    uv run --with python-pptx --with pillow python code/deliverables/build_modules_deck.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build_decks as bd  # noqa: E402  (Deck class, template, slide kit)
from build_docs import FACILITATOR, parse  # noqa: E402
from module_manifest import OVERVIEW, STEPS, fname  # noqa: E402

g = bd.g
from pptx.util import Inches, Pt  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR  # noqa: E402

SHOTS = ROOT / "notes" / "agent-notes" / "screenshots"
for t in ("module-step", "module-overview", "module-steps"):
    g.VALID_SLIDE_TYPES.add(t)
    g.LAYOUT_MAPPINGS[t] = ["CUSTOM"]


def find_image(name):
    for d in (SHOTS / "modules", SHOTS, ROOT / "assets"):
        if (d / name).exists():
            return d / name
    raise FileNotFoundError(name)


def clean(s):
    s = re.sub(r"\s*\([^)]*FEVM[^)]*\)", "", s)
    s = re.split(r"\*?\*?FEVM note|On the FEVM", s)[0]  # workspace-specific numbers stay out of the participant deck
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = s.replace("`", "").replace("\\", "")
    s = re.sub(r"\[(.+?)\]\([^)]*\)", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def clip(s, n):
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + " …"


def stage_key(title):
    m = re.match(r"(Stage \d+|Track [A-Z]|Closing)", title)
    return m.group(1) if m else title.split(":")[0]


def short(title):
    t = re.sub(r"^(Stage \d+( \([^)]*\))?|Track [A-Z])\s*[:—-]\s*", "", title)
    return re.sub(r"\s*\((\d+ min[^)]*|facilitator[^)]*|optional[^)]*)\)\s*$", "", t).strip()


def steps_of(stage):
    """Split a stage into steps: one per prompt, or one 'do' step if there is no prompt."""
    lines = [l for l in stage["lines"] if not FACILITATOR.search(l)]
    prompts, cur, intro, stuck, code, in_code, want_code = [], None, [], [], [], False, None
    for l in lines:
        if l.startswith("```"):
            in_code = not in_code
            if not in_code and want_code is not None:
                want_code.append(" ".join(c.strip() for c in code[:3]))
                want_code, code = None, []
            elif not in_code:
                if cur is None:
                    intro.append(("CODE", " ".join(c.strip() for c in code[:4])))
                code = []
            continue
        if in_code:
            code.append(l)
            continue
        if l.startswith(">"):
            if cur is None or cur["expected"]:
                cur = {"prompt": clean(l.lstrip("> ")), "expected": []}
                prompts.append(cur)
            else:
                cur["prompt"] += " " + clean(l.lstrip("> "))
        elif re.match(r"\*\*(Expected|Checkpoint)", l):
            body = clean(re.sub(r"^\*\*[^*]+\*\*:?\s*", "", l))
            if cur is None:
                intro.append(("EXP", body))
            elif body:
                cur["expected"].append(body)
            if not body or body.endswith(":"):
                want_code = cur["expected"] if cur else None
        elif l.startswith("**If stuck"):
            stuck.append(clean(re.sub(r"^\*\*[^*]+\*\*:?\s*", "", l)))
        elif l.startswith("**Prompt"):
            continue
        elif l.strip() and not l.startswith("|") and cur is None:
            intro.append(("TXT", clean(l.lstrip("-* "))))
    if not prompts:
        txt = [t for k, t in intro if k == "TXT" and t]
        sql = [t for k, t in intro if k == "CODE" and t]
        exp = [t for k, t in intro if k == "EXP" and t]
        return [{"prompt": None, "do": clip(" ".join(txt[:3]), 420), "sql": clip(sql[0], 420) if sql else None,
                 "expected": " ".join(exp), "stuck": " ".join(stuck)}]
    return [{"prompt": p["prompt"], "expected": " ".join(p["expected"]), "stuck": " ".join(stuck),
             "do": None, "sql": None} for p in prompts]


class ModuleDeck(bd.Deck):
    def add_module_overview_slide(self, d):
        s = self._create_slide("module-overview", d)
        self._title(s, d["title"], d.get("subtitle"))
        y = 1.55
        for label, text in d["blocks"]:
            n = 1 + len(text) // 58
            self._block(s, label, text, 0.6, y, 4.3, 0.45 + 0.22 * n, size=12)
            y += 0.6 + 0.22 * n
        self._image(s, find_image(d["image"]), 5.1, 1.5, 7.7, 5.5)

    def add_module_steps_slide(self, d):
        s = self._create_slide("module-steps", d)
        self._title(s, d["title"], d.get("subtitle"))
        items = d["items"]
        per_col = (len(items) + 1) // 2 if len(items) > 5 else len(items)
        for i, (name, kind) in enumerate(items):
            col, row = divmod(i, per_col)
            x, y = 0.6 + col * 6.2, 1.6 + row * 0.95
            badge = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.55), Inches(0.55))
            badge.fill.solid()
            badge.fill.fore_color.rgb = g.hex_to_rgb(bd.ACCENT)
            badge.line.fill.background()
            tf = badge.text_frame
            tf.paragraphs[0].text = str(i + 1)
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            tf.paragraphs[0].font.size, tf.paragraphs[0].font.bold = Pt(16), True
            tf.paragraphs[0].font.color.rgb = g.hex_to_rgb("#FFFFFF")
            self.add_textbox(s, name, x + 0.75, y + 0.02, 5.2, 0.4, font_size=16, bold=True, color=bd.DARK)
            self.add_textbox(s, kind, x + 0.75, y + 0.4, 5.2, 0.35, font_size=11, color=bd.MUTED)

    def add_module_step_slide(self, d):
        s = self._create_slide("module-step", d)
        self._title(s, d["title"], d.get("subtitle"))
        img = d.get("image")
        w = 4.75 if img else 12.1
        text = d.get("prompt") or d.get("sql") or d.get("do") or ""
        label = ("YOU TYPE (Genie Code / Genie)" if d.get("prompt") else "YOU RUN (SQL editor)" if d.get("sql")
                 else "TALK TRACK" if d.get("talk") else "YOU DO")
        size = 13 if len(text) < 180 else 11 if len(text) < 330 else 10
        box_h = min(3.1, 0.55 + len(text) / (52 if img else 120) * 0.24 * (13 / size))
        self.add_textbox(s, label, 0.6, 1.45, w, 0.3, font_size=10, bold=True, color=bd.ACCENT)
        box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.8), Inches(w), Inches(box_h))
        box.fill.solid()
        box.fill.fore_color.rgb = g.hex_to_rgb("#EEF2F3")
        box.line.color.rgb = g.hex_to_rgb("#C9D2D6")
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = Inches(0.15)
        p = tf.paragraphs[0]
        p.text, p.alignment = text, PP_ALIGN.LEFT
        p.font.size = Pt(size)
        p.font.name = "Courier New" if (d.get("prompt") or d.get("sql")) else g.FONT_FAMILY
        p.font.color.rgb = g.hex_to_rgb(bd.DARK)
        y = 1.95 + box_h
        if d.get("expected"):
            n = 1 + len(d["expected"]) // (60 if img else 140)
            self._block(s, "Expected result", d["expected"], 0.6, y, w, 0.45 + 0.21 * n, size=12)
            y += 0.6 + 0.21 * n
        if d.get("stuck"):
            self._block(s, "If you're stuck", d["stuck"], 0.6, min(y, 6.3), w, 0.8, size=10, label_color=bd.MUTED)
        if img:
            self._image(s, find_image(img), 5.55, 1.45, 7.25, 5.6)
        self.add_textbox(s, d.get("footer", ""), 0.6, 7.0, 12.0, 0.3, font_size=9, color=bd.MUTED)

    def generate(self, content):
        extra = {"module-step": self.add_module_step_slide, "module-overview": self.add_module_overview_slide,
                 "module-steps": self.add_module_steps_slide}
        for sd in content["slides"]:
            if sd.get("type") in extra:
                extra[sd["type"]](sd)
            else:
                bd.Deck.generate(self, {"slides": [sd]})


def header_field(header, name):
    for line in header:
        for part in line.split(" · "):
            m = re.match(r"\*\*(.+?):\*\*\s*(.*)", part.strip())
            if m and m.group(1).strip() == name:
                return clean(m.group(2))
    return ""


def build():
    guides = sorted((parse(p) for p in (ROOT / "code" / "prompts").glob("d[0-9][0-9]-*.md")), key=lambda x: x[0])
    slides = [
        {"type": "title", "title": "Build it yourself: module by module",
         "subtitle": "Revantage workshop · every step, the prompt, the expected result", "date": "October 2026"},
        {"type": "timeline", "title": "How every module works", "steps": [
            {"title": "What we'll build", "description": "The finished asset you'll have at the end"},
            {"title": "How we'll get there", "description": "The steps, in order"},
            {"title": "Each step", "description": "Type the prompt, compare with the expected result"},
            {"title": "If stuck", "description": "Open the reference (ref_… / \"(Reference)\")"}]},
        {"type": "content", "title": "Placeholders in the prompts", "bullets": [
            "<catalog>.<schema>: the shared workshop data (your facilitator gives you the names)",
            "<my_schema>: your own sandbox schema; everything you build goes here",
            ":workspace_id: the number after ?o= in your browser URL",
            "End every prompt that builds something with \"run it and check the result\""]},
    ]
    unmatched = []
    for num, title, header, stages, _ in guides:
        name = re.sub(r"^Demo \d+:\s*", "", title)
        session = header_field(header, "Session")
        slides.append({"type": "section", "title": f"Module {num}: {name.split(' — ')[0]}",
                       "subtitle": name.split(" — ")[1].strip('"“”') if " — " in name else session})
        real = [st for st in stages if not re.match(r"(Reset|Stage \d+: Clean up)", st["title"])]
        plan = []
        for st in real:
            key = stage_key(st["title"])
            for i, step in enumerate(steps_of(st), 1):
                pidx = i if step["prompt"] else 0
                mkey = next((k for k in ((num, key, pidx), (num, key, 0), (num, key, 1)) if k in STEPS), None)
                if mkey is None:
                    unmatched.append((num, key, pidx))
                plan.append((st, step, STEPS.get(mkey), mkey))
        blocks = [("You build", header_field(header, "You build")), ("Session", session),
                  ("Where", header_field(header, "Where")), ("Reference (answer key)", header_field(header, "Reference"))]
        slides.append({"type": "module-overview", "title": f"What we'll build · {name.split(' — ')[0]}",
                       "blocks": [(l, clip(t, 230)) for l, t in blocks if t], "image": OVERVIEW[num]})
        items, seen = [], set()
        for st, step, media, _ in plan:
            if st["title"] in seen:
                continue
            seen.add(st["title"])
            kind = ("talk" if media and media[0] == "talk" else
                    "prompt" if step["prompt"] else "do")
            items.append((short(st["title"]), {"prompt": "Genie Code / Genie prompt", "do": "Click-path step",
                                               "talk": "Talk track"}[kind]))
        slides.append({"type": "module-steps", "title": f"How we'll get there · {len(items)} steps", "items": items[:10]})
        step_no = {}
        for st, step, media, key in plan:
            idx = list(dict.fromkeys(s["title"] for s, *_ in plan)).index(st["title"]) + 1
            step_no[idx] = step_no.get(idx, 0) + 1
            sub = f"{step_no[idx]}" if sum(1 for s, *_ in plan if s["title"] == st["title"]) > 1 else ""
            img = None
            if media and media[0] == "file":
                img = media[1]
            elif media and media[0] != "talk":
                img = fname(key)
            slides.append({"type": "module-step",
                           "title": f"Step {idx}{('.' + sub) if sub else ''} · {short(st['title'])}",
                           "subtitle": f"Module {num}: {name.split(' — ')[0]}",
                           "prompt": clip(step["prompt"], 520) if step["prompt"] else None,
                           "do": None if step["prompt"] else step["do"],
                           "sql": step.get("sql") if not step["prompt"] else None,
                           "talk": bool(media and media[0] == "talk") and not step["prompt"],
                           "expected": clip(step["expected"] or ("Runs once the profiling monitor exists (created by the bundle in the Revantage workspace)." if media and media[0] == "talk" and step["prompt"] else ""), 380), "stuck": clip(step["stuck"], 200),
                           "image": img})
    slides.append({"type": "closing", "title": "Thank you"})
    if unmatched:
        print("WARNING: steps without a manifest entry:", unmatched)
    out = ROOT / "assets" / f"{bd.NAME}-modules.pptx"
    d = ModuleDeck(g.TEMPLATE_PATH)
    d.generate({"slides": slides})
    d.save(str(out))
    print("wrote", out, len(slides), "slides")


if __name__ == "__main__":
    build()
