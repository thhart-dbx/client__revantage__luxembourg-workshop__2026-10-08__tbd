-- Demo 16: simulate a bad 2026-Q3 load for Harbor Tower: revenue 10x its historical average and NULL net_profit.
-- ${table} = gold_property_quarterly in the workshop (last session), or ref_d16_gold_sandbox for rehearsal.
INSERT INTO ${catalog}.${schema}.${table}
SELECT property_id, property_name, property_type, region_name, market, '2026-Q3', DATE'2026-07-01',
       ROUND(AVG(revenue) * 10, 2), ROUND(AVG(operating_expense), 2), ROUND(AVG(mgmt_fee), 2), 0, 0,
       NULL, MAX(net_profit_target), MAX(revenue_target), FALSE, NULL, NULL
FROM ${catalog}.${schema}.${table}
WHERE property_id = 3 AND fiscal_quarter <> '2026-Q3'
GROUP BY ALL;
