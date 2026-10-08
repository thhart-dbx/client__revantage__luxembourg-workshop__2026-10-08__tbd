"""Ask a Genie Agent questions through the Conversation API; print answer text, SQL, and result rows.

Usage: python ask_genie.py --profile P --space SPACE_ID "question 1" ["question 2" ...] [--followup]
With --followup, all questions go to one conversation (in order); otherwise each starts fresh.
"""
import argparse
import json
import subprocess
import time

ap = argparse.ArgumentParser()
ap.add_argument("--profile", required=True)
ap.add_argument("--space", required=True)
ap.add_argument("--followup", action="store_true")
ap.add_argument("questions", nargs="+")
args = ap.parse_args()


def api(method, path, body=None):
    cmd = ["databricks", "api", method, path, "-p", args.profile] + (["--json", json.dumps(body)] if body else [])
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout or "{}")


base = f"/api/2.0/genie/spaces/{args.space}"
conv = None
for q in args.questions:
    if conv and args.followup:
        msg = api("post", f"{base}/conversations/{conv}/messages", {"content": q})
    else:
        r = api("post", f"{base}/start-conversation", {"content": q})
        conv, msg = r["conversation_id"], r["message"]
    mid = msg.get("message_id") or msg.get("id")
    for _ in range(90):
        msg = api("get", f"{base}/conversations/{conv}/messages/{mid}")
        if msg["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(4)
    print("=" * 100, f"\nQ: {q}\nstatus: {msg['status']}")
    for att in msg.get("attachments") or []:
        if att.get("text"):
            print("TEXT:", att["text"]["content"].strip())
        if att.get("query"):
            print("SQL:\n" + att["query"]["query"].strip())
            res = api("get", f"{base}/conversations/{conv}/messages/{mid}/query-result/{att['attachment_id']}")
            sr = res.get("statement_response", {})
            cols = [c["name"] for c in sr.get("manifest", {}).get("schema", {}).get("columns", [])]
            rows = sr.get("result", {}).get("data_array", []) or []
            print("ROWS:", cols)
            for row in rows[:12]:
                print("   ", row)
    if msg.get("error"):
        print("ERROR:", msg["error"])
