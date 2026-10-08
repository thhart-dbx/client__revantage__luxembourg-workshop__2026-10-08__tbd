"""Tiny SQL Statement API client over the databricks CLI (uses the CLI profile's auth)."""
import json
import subprocess

import pandas as pd


def query(sql, profile, warehouse_id):
    body = {"warehouse_id": warehouse_id, "statement": sql, "wait_timeout": "50s",
            "disposition": "INLINE", "format": "JSON_ARRAY"}
    out = subprocess.run(["databricks", "api", "post", "/api/2.0/sql/statements", "-p", profile,
                          "--json", json.dumps(body)], capture_output=True, text=True, check=True).stdout
    res = json.loads(out)
    while res["status"]["state"] in ("PENDING", "RUNNING"):
        out = subprocess.run(["databricks", "api", "get", f"/api/2.0/sql/statements/{res['statement_id']}",
                              "-p", profile], capture_output=True, text=True, check=True).stdout
        res = json.loads(out)
    if res["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(f"{res['status']}\n{sql}")
    cols = [c["name"] for c in res["manifest"]["schema"]["columns"]]
    return pd.DataFrame(res.get("result", {}).get("data_array", []) or [], columns=cols)
