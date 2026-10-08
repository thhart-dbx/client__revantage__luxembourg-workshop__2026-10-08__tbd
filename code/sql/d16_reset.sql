-- Demo 16 reset: remove the simulated bad load.
DELETE FROM ${catalog}.${schema}.${table} WHERE fiscal_quarter = '2026-Q3';
