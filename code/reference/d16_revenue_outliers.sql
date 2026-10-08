-- Demo 16 alert query: property-quarters whose revenue is > 3 standard deviations from the same
-- property's OTHER quarters (leave-one-out, so a single bad row can't hide inside its own average)
-- AND more than 50% away from that mean. On smooth financial series sigma is small, so real business
-- moves (Harbor Tower's vacancy, a new Kirchberg suite) exceed 3 sigma too; the materiality guard keeps
-- the alert for data errors.
WITH pairs AS (
  SELECT a.property_name, a.fiscal_quarter, a.revenue, b.revenue AS other_revenue
  FROM ${catalog}.${schema}.${table} a
  JOIN ${catalog}.${schema}.${table} b ON a.property_id = b.property_id AND a.fiscal_quarter <> b.fiscal_quarter
), stats AS (
  SELECT property_name, fiscal_quarter, MAX(revenue) AS revenue, AVG(other_revenue) AS mean_others, STDDEV(other_revenue) AS sd_others
  FROM pairs GROUP BY ALL
)
SELECT property_name, fiscal_quarter, revenue, ROUND(mean_others) AS mean_others,
       ROUND((revenue - mean_others) / sd_others, 1) AS z_score
FROM stats WHERE abs((revenue - mean_others) / sd_others) > 3 AND abs(revenue / mean_others - 1) > 0.5
ORDER BY abs(z_score) DESC;
