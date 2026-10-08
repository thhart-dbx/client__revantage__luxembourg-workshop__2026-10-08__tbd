-- D6 reference: the five Genie One audit questions codified as one recurring check.
-- Each row is a check with the observed value and PASS/FAIL against the agreed expectation, so it
-- can feed an alert or a dashboard tile. Placeholders: ${catalog}, ${schema}.
CREATE OR REPLACE VIEW ${catalog}.${schema}.ref_d06_property_quality_checks
COMMENT 'Recurring data-quality checks on the property master (bronze vs silver vs gold).'
AS
WITH b AS (SELECT * FROM ${catalog}.${schema}.bronze_properties),
s AS (SELECT * FROM ${catalog}.${schema}.silver_properties),
g AS (SELECT DISTINCT property_id FROM ${catalog}.${schema}.gold_property_quarterly)
SELECT 'bronze_vs_gold_property_count' AS check_name,
       concat((SELECT COUNT(*) FROM b), ' bronze vs ', (SELECT COUNT(*) FROM g), ' gold') AS observed,
       (SELECT COUNT(*) FROM b) - (SELECT COUNT(*) FROM g) AS issue_count
UNION ALL
SELECT 'properties_missing_from_gold',
       (SELECT concat_ws(', ', collect_list(concat(property_id, ' ', property_name))) FROM b WHERE property_id NOT IN (SELECT property_id FROM g)),
       (SELECT COUNT(*) FROM b WHERE property_id NOT IN (SELECT property_id FROM g))
UNION ALL
SELECT 'null_region_id',
       concat(ROUND(100 * (SELECT COUNT_IF(region_id IS NULL) FROM b) / (SELECT COUNT(*) FROM b), 1), '% of bronze rows'),
       (SELECT COUNT_IF(region_id IS NULL) FROM b)
UNION ALL
SELECT 'duplicate_property_names',
       (SELECT concat_ws('; ', collect_list(concat(property_name, ' (ids ', ids, ')'))) FROM
          (SELECT property_name, concat_ws(',', transform(sort_array(collect_list(property_id)), x -> CAST(x AS STRING))) AS ids
           FROM b GROUP BY property_name HAVING COUNT(DISTINCT property_id) > 1)),
       (SELECT COUNT(*) FROM (SELECT property_name FROM b GROUP BY property_name HAVING COUNT(DISTINCT property_id) > 1))
UNION ALL
SELECT 'market_name_mismatch_bronze_vs_silver',
       (SELECT concat_ws('; ', collect_list(concat(b.market, ' -> ', s.market))) FROM b JOIN s USING (property_id) WHERE b.market <> s.market),
       (SELECT COUNT(*) FROM b JOIN s USING (property_id) WHERE b.market <> s.market);
