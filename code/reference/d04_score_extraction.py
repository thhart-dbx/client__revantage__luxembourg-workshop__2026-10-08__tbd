"""Score ref_invoices_extracted against code/documents/out/invoices_ground_truth.json, field by field.

Usage: python d04_score_extraction.py --profile P --warehouse W --catalog C --schema S
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from sqlclient import query  # noqa: E402

ap = argparse.ArgumentParser()
for a in ("profile", "warehouse", "catalog", "schema"):
    ap.add_argument(f"--{a}", required=True)
args = ap.parse_args()
truth = {t["invoice_number"]: t for t in json.load(open(Path(__file__).resolve().parents[1] / "documents/out/invoices_ground_truth.json"))}
rows = query(f"SELECT path, CAST(response:response AS STRING) r FROM {args.catalog}.{args.schema}.ref_invoices_extracted",
             args.profile, args.warehouse)

HEAD = ["vendor_name", "invoice_number", "invoice_date", "due_date", "subtotal", "tax", "total", "currency"]
ok = tot = 0
for _, row in rows.iterrows():
    got = json.loads(row.r)
    t = truth.get(got.get("invoice_number"))
    if not t:
        print("UNMATCHED", row.path, got.get("invoice_number"))
        continue
    misses = []
    for f in HEAD:
        a, b = got.get(f), t[f]
        same = (abs(float(a or 0) - float(b or 0)) < 0.01) if isinstance(b, (int, float)) else (str(a).strip() == str(b).strip())
        tot += 1
        ok += same
        if not same:
            misses.append(f"{f}: got {a!r} want {b!r}")
    gl, tl = got.get("line_items") or [], t["line_items"]
    tot += 1
    li_ok = len(gl) == len(tl) and all(abs(float(g.get("amount") or 0) - l["amount"]) < 0.01 for g, l in zip(gl, tl))
    ok += li_ok
    if not li_ok:
        misses.append(f"line_items: {len(gl)} vs {len(tl)} or amounts differ")
    print(f"{t['invoice_number']:<20} {'OK' if not misses else 'MISS: ' + '; '.join(misses)}")
print(f"\nfield accuracy: {ok}/{tot} = {ok / tot:.1%} over {len(rows)} invoices")
