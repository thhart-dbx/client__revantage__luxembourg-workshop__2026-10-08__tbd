-- Demo 16: what reads gold_property_quarterly (tables, views, metric views, dashboards, jobs, pipelines).
SELECT coalesce(target_table_full_name, entity_type) AS downstream, entity_type, COUNT(*) AS events, MAX(event_time) AS last_seen
FROM system.access.table_lineage
WHERE source_table_full_name = '${catalog}.${schema}.gold_property_quarterly'
  AND event_date >= current_date() - INTERVAL 30 DAYS
GROUP BY ALL ORDER BY events DESC;
