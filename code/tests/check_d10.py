"""Print the D10 governance state of gold_property_quarterly and customer_performance."""
import sys
from sqlclient import query
P, W, C, S = sys.argv[1:5]
q = lambda s: query(s, P, W)
print("table comment:", (q(f"SELECT comment FROM {C}.information_schema.tables WHERE table_schema='{S}' AND table_name='gold_property_quarterly'").comment[0] or "")[:70])
print("col comments:", q(f"SELECT column_name, left(comment, 40) c FROM {C}.information_schema.columns WHERE table_schema='{S}' AND table_name='gold_property_quarterly' AND column_name IN ('net_profit','met_target','qoq_change_pct')").values.tolist())
print("table tags:", q(f"SELECT tag_name, tag_value FROM {C}.information_schema.table_tags WHERE schema_name='{S}' AND table_name='gold_property_quarterly'").values.tolist())
print("column tags:", q(f"SELECT column_name, tag_name FROM {C}.information_schema.column_tags WHERE schema_name='{S}' AND table_name='customer_performance'").values.tolist())
print("masked sample:", q(f"SELECT contact_email, contact_phone FROM {C}.{S}.customer_performance LIMIT 1").values.tolist())
