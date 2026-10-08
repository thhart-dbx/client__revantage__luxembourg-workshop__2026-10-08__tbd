"""Ask a Knowledge Assistant serving endpoint questions; print answer + cited sources."""
import argparse
import json
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("--profile", required=True)
ap.add_argument("--endpoint", required=True)
ap.add_argument("questions", nargs="+")
args = ap.parse_args()
for q in args.questions:
    body = {"input": [{"role": "user", "content": q}]}
    r = subprocess.run(["databricks", "api", "post", f"/serving-endpoints/{args.endpoint}/invocations", "-p", args.profile,
                        "--json", json.dumps(body)], capture_output=True, text=True)
    print("=" * 100, "\nQ:", q)
    if r.returncode:
        print("ERROR", r.stderr[-400:] or r.stdout[-400:])
        continue
    d = json.loads(r.stdout)
    texts, cites = [], set()
    for item in d.get("output", []):
        for c in item.get("content", []) or []:
            if c.get("type") in ("output_text", "text"):
                texts.append(c.get("text", ""))
            for a in c.get("annotations", []) or []:
                cites.add(a.get("title") or a.get("url") or json.dumps(a)[:120])
    print("A:", " ".join(texts).strip()[:1500])
    print("CITES:", sorted(cites))
