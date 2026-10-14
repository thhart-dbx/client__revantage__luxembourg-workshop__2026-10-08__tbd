# Databricks notebook source
# MAGIC %md
# MAGIC # Module 0 · Build your own copy of the workshop data
# MAGIC
# MAGIC Run this notebook from your Git folder (Run all, serverless). In about 3 minutes it builds the full
# MAGIC starting state in **your** schema: the 7 raw CSVs and 15 PDFs in volumes, then the bronze, silver and
# MAGIC gold tables every module uses. Same data as the shared workshop schema, value for value, so the
# MAGIC expected results in every module hold for your copy too.
# MAGIC
# MAGIC Fill in the two widgets at the top with the names your facilitator gives you, then **Run all**.
# MAGIC Safe to re-run: it rebuilds your copy from scratch.

# COMMAND ----------

import re

dbutils.widgets.text("catalog", "", "1. Workshop catalog")
dbutils.widgets.text("shared_schema", "", "2. Shared workshop schema")
dbutils.widgets.text("my_schema", "", "3. My schema (blank = <shared_schema>_<your name>)")
dbutils.widgets.text("as_of", "2026-10-13", "4. Workshop day 1 (leave as is)")

catalog = dbutils.widgets.get("catalog").strip()
shared = dbutils.widgets.get("shared_schema").strip()
assert catalog and shared, "Fill in the catalog and shared schema widgets (your facilitator has the names)."
me = spark.sql("SELECT current_user()").first()[0]
name = re.sub(r"[^a-z0-9]+", "_", me.split("@")[0].lower()).strip("_")
my_schema = dbutils.widgets.get("my_schema").strip() or f"{shared}_{name}"  # same rule as the sandbox job
print(f"{me} -> {catalog}.{my_schema}")

# COMMAND ----------

# MAGIC %md ## 1. Your schema and its two volumes

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{my_schema}` COMMENT 'Revantage workshop copy for {me}'")
for vol in ("raw", "documents"):
    spark.sql(f"CREATE VOLUME IF NOT EXISTS `{catalog}`.`{my_schema}`.`{vol}`")
display(spark.sql(f"SHOW VOLUMES IN `{catalog}`.`{my_schema}`"))

# COMMAND ----------

# MAGIC %md ## 2. Generate the data, copy the documents, build bronze → silver → gold
# MAGIC The same script the facilitator's setup job runs, pointed at your schema.

# COMMAND ----------

import os
import runpy
import sys
from pathlib import Path

code_dir = Path(os.getcwd()).parent  # this notebook lives in <Git folder>/code/setup
sys.argv = ["setup_starting_state.py", "--catalog", catalog, "--schema", my_schema,
            "--as-of", dbutils.widgets.get("as_of"), "--bundle-root", str(code_dir)]
runpy.run_path(str(code_dir / "setup" / "setup_starting_state.py"), run_name="__main__")

# COMMAND ----------

# MAGIC %md ## 3. Check your copy
# MAGIC Every line should say PASS. The numbers are the ones Module 1 starts from.

# COMMAND ----------

T = f"`{catalog}`.`{my_schema}`"
V = f"/Volumes/{catalog}/{my_schema}"
one = lambda sql: spark.sql(sql).first()
g = one(f"SELECT COUNT(*) n, COUNT(DISTINCT property_id) p, MIN(fiscal_quarter) lo, MAX(fiscal_quarter) hi "
        f"FROM {T}.gold_property_quarterly")
se = one(f"SELECT ROUND(SUM(net_profit) / 1e6, 2) m FROM {T}.gold_property_quarterly "
         f"WHERE fiscal_quarter = '2026-Q2' AND region_name = 'Southeast'").m
checks = [
    ("gold_property_quarterly: 80 rows, 8 properties, 2024-Q1..2026-Q2",
     (g.n, g.p, g.lo, g.hi) == (80, 8, "2024-Q1", "2026-Q2")),
    ("Southeast 2026-Q2 net profit ≈ €2.09M", float(se) == 2.09),
    ("16 starting tables (bronze 7, silver 7, gold, customer_performance)",
     spark.sql(f"SHOW TABLES IN {T}").filter("tableName RLIKE '^(bronze|silver)_|^gold_property_quarterly$|"
                                            "^customer_performance$'").count() == 16),
    ("Module 17 legacy warehouse: 7 legacy_* tables + d17_benchmark",
     spark.sql(f"SHOW TABLES IN {T}").filter("tableName RLIKE '^legacy_|^d17_benchmark$'").count() == 8),
    ("raw volume: 7 CSVs", len(dbutils.fs.ls(f"{V}/raw")) == 7),
] + [(f"documents/{d}: {n} PDFs", len(dbutils.fs.ls(f"{V}/documents/{d}")) == n)
     for d, n in (("invoices", 8), ("policies", 4), ("leases", 3))]
for label, ok in checks:
    print("PASS" if ok else "FAIL", " ", label)
assert all(ok for _, ok in checks), "Some checks failed: re-run the notebook, then ask your facilitator."
print(f"\nDone. In the module prompts, <my_schema> is {catalog}.{my_schema}.")
