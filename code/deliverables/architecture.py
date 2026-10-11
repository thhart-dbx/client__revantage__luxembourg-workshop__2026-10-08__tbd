"""Architecture diagram for the Revantage Luxembourg workshop (draw.io + PNG).

Every asset in README.md > Assets Created appears as a node. Uses the drawio-diagram skill's
DrawioBuilder (fe-specialized-agents). Usage:
    python3 code/deliverables/architecture.py [--skill-dir <drawio-diagram skill dir>]
Writes assets/architecture.drawio and assets/architecture.png.
"""
import argparse
import glob
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
default_skill = sorted(glob.glob(os.path.expanduser(
    "~/.claude/plugins/cache/fe-vibe/fe-specialized-agents/*/skills/drawio-diagram")))
ap.add_argument("--skill-dir", default=default_skill[-1] if default_skill else None)
args = ap.parse_args()
sys.path.insert(0, str(Path(args.skill_dir) / "scripts"))
from generate_drawio import DrawioBuilder, load_icons, export_to_png  # noqa: E402

b = DrawioBuilder(width=2050, height=1180, icons_cache=load_icons())
W, H = 230, 74          # node size (>= 64 so icon and label don't collide)
GAP = 88                # vertical pitch


def column(x, y, w, label, layer, items):
    """A container with stacked nodes; items = [(label, color, icon)]. Returns node ids."""
    h = DrawioBuilder.calc_container_height(len(items), item_height=H, spacing=GAP)
    c = b.add_container(x, y, w, h, label, layer)
    return [b.add_node(15, 45 + i * GAP, w - 30, H, lbl, color, icon_name=icon, parent=c)
            for i, (lbl, color, icon) in enumerate(items)]


b.add_text(30, 8, 1500, 30,
           "Revantage Luxembourg workshop: one dataset, 18 build-along demos  ·  "
           "schema: {catalog}.revantage_20261008 (dev: thhart_october_2026_catalog)", font_size=16, font_color="#1B3139")

# 1. Sources (Unity Catalog volumes)
src = column(30, 50, 260, "Sources (UC volumes)", "sources", [
    ("raw volume: 7 CSV extracts\n(Yardi / SAP: regions … gl_transactions)", "blue", "catalog_store"),
    ("documents volume: 8 invoices,\n4 policies, 3 leases (PDF)", "blue", "catalog_store"),
    ("Snowflake view SQL (D3)\n+ late SAP-LUX batch (D11)", "slate", "snowflake"),
])

# 2. Lakehouse: setup job + medallion tables
setup = column(330, 50, 300, "Starting state (Setup job)", "ingestion", [
    ("Job: Setup starting state\n(generator + SQL, serverless)", "compute_green", "workflows_2"),
    ("Job: Participant sandboxes\n({my_schema} per person)", "compute_green", "workflows_2"),
])
med = column(330, 300, 300, "Medallion (Delta)", "medallion", [
    ("bronze_* (7 tables)\nplanted data issues", "bronze", "delta_table"),
    ("silver_* (7 tables)\ncleaned, standardized", "silver", "delta_table"),
    ("gold_property_quarterly (80)\ncertified quarterly P&L", "gold", "delta_table"),
    ("customer_performance (470)\ntenant level, PII columns", "gold", "delta_table"),
    ("legacy_* (6) + data dictionary\n+ d17_benchmark (10 questions)", "bronze", "delta_table"),
])

# 3. Reference answer keys (built by bundle jobs / pipeline)
ref = column(670, 50, 320, "Reference answer keys (ref_*)", "compute", [
    ("Lakeflow pipeline: Property Pipeline (Ref)\n→ ref_d11_* bronze/silver/gold", "compute_green", "data_pipelines"),
    ("Job: Reference D3/D6/D7/D14", "compute_green", "workflows_2"),
    ("ref_d03_property_performance_v\nref_d06_property_quality_checks", "silver", "delta_table"),
    ("Metric views: ref_mv_net_profit_margin,\nref_mv_target_attainment, ref_mv_qoq_revenue_growth", "gold", "unity_catalog"),
    ("ref_d14_revenue_forecast\n(ai_forecast on a SQL warehouse)", "gold", "delta_table"),
    ("ref_d17_* business layer: names, comments,\ndescriptions, PK/FK · benchmark results", "silver", "delta_table"),
])

# 4. AI
ai = column(1030, 50, 320, "AI: Agent Bricks + AI Gateway", "aiml", [
    ("Agent Bricks: Information Extraction\nextract-invoices → ai_parse_document + ai_extract", "purple", "mlflow"),
    ("ref_invoices_extracted (8)\nVARIANT response, 72/72 fields", "gold", "delta_table"),
    ("Agent Bricks: Knowledge Assistant (reads the\npolicy PDFs) · ka-…-endpoint", "purple", "mlflow"),
    ("AI Gateway on databricks-claude-sonnet-4-6\nusage tracking → ref_d13_payload", "purple", "anthropic"),
    ("system.ai_gateway / system.billing\n(read-only, D13)", "slate", "unity_catalog"),
])

# 5. Operational (Lakebase)
ops = column(1030, 590, 320, "Operational: Lakebase Postgres", "storage", [
    ("revantage-lux-ops (CU_1)\ndb revantage_ops · schema approvals", "teal", "postgresql"),
    ("Job: Approved invoices → silver (Ref)\nMERGE into silver_invoices", "compute_green", "workflows_2"),
    ("silver_invoices (Delta)\napproved invoices only", "silver", "delta_table"),
    ("ref_d12_gold_property_quarterly_synced\nsynced table (reverse ETL)", "teal", "postgresql"),
])
silver_inv = ops[2]

# 6. Consumption
cons = column(1400, 50, 330, "Consumption", "consumption", [
    ("Genie Agent: Portfolio Q&A (Start)\nparticipants teach it", "orange", "databricks"),
    ("Genie Agent: Portfolio Q&A (Reference)\nincl. metric views", "orange", "databricks"),
    ("Genie Agents: Accuracy Lab (Start / Ref)\n10-question benchmark (D17)", "orange", "databricks"),
    ("AI/BI dashboard: Portfolio Review (Ref)\n4 pages + Ask Genie", "orange", "databricks_workspace"),
    ("App: revantage-lease-tracker\n(Next.js, SQL warehouse)", "pink", "apps_services"),
    ("App: revantage-invoice-approvals\n(Next.js, Lakebase, two approvers)", "pink", "apps_services"),
    ("SQL alerts: AI tokens > 1M ·\nrevenue > 3σ outlier (Ref)", "red", "serverless"),
])
users = column(1770, 50, 250, "People", "consumption", [
    ("Finance / FP&A / Asset Mgmt\n(revantage_consumers)", "white", "users"),
    ("Participants (Genie Code\nin every editor)", "white", "users"),
])

# Governance band
gov = b.add_container(30, 1040, 1990, 125, "Unity Catalog governance (applies to every object above)", "governance")
for i, (lbl, icon) in enumerate([
        ("Catalog / schema / volumes\ngrants to groups + app SPs", "unity_catalog"),
        ("Governed tags: system.certification_status,\nclass.email_address / phone_number", "unity_catalog"),
        ("Column masks (is_account_group_member)\non customer_performance", "unity_catalog"),
        ("Lineage + comments\n(gold → metric views → dashboard / Genie)", "unity_catalog"),
        ("Data quality: Lakeflow expectations,\nquality monitor (revantage target)", "unity_catalog"),
        ("Domain + Pages (D18): Revantage Workshop,\nbusiness definitions for Genie One", "unity_catalog")]):
    b.add_node(12 + i * 329, 42, 318, H, lbl, "gov", icon_name=icon, parent=gov)


def e(s, t, label=None, **kw):
    b.add_edge(s, t, label, exit_x=1, exit_y=0.5, entry_x=0, entry_y=0.5, **kw)


def down(s, t):
    b.add_edge(s, t, None, exit_x=0.5, exit_y=1, entry_x=0.5, entry_y=0)


# Short hops carry labels; long cross-column edges stay unlabelled to keep the picture readable.
e(src[0], setup[0], "load")
down(setup[0], setup[1])
b.add_edge(setup[0], med[0], None, exit_x=0.25, exit_y=1, entry_x=0.25, entry_y=0)
down(med[0], med[1]); down(med[1], med[2]); down(med[2], med[3])
e(src[0], ref[0])
e(src[1], ai[0])
e(med[2], ref[2], "views")
e(med[2], ref[3], "metrics")
e(med[2], ref[4], "forecast")
down(ai[0], ai[1])
down(ai[3], ai[4])
down(ops[0], ops[1]); down(ops[1], ops[2])
e(med[2], ops[3])
e(ref[3], cons[1])
e(ref[3], cons[2])
e(ref[4], cons[2])
e(ops[0], cons[4], "OAuth SP")
e(ai[3], cons[5])
e(cons[2], users[0])
e(cons[4], users[0])

out = ROOT / "assets" / "architecture.drawio"
b.save(str(out))
b.print_validation()
export_to_png(str(out), str(ROOT / "assets" / "architecture.png"))
print("wrote", out)
