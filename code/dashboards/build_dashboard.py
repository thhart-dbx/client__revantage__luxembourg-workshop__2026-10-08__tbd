"""Generate code/dashboards/revantage-portfolio-review.lvdash.json (Demo 8 reference dashboard).

Run after editing:  code/data-gen/.venv/bin/python code/dashboards/build_dashboard.py
Datasets reference `${catalog}.${schema}` through the bundle's dataset_catalog / dataset_schema, so
queries use unqualified table names.
Pages: Executive Summary (metric views), Regional Performance, Exceptions & Risks, Forecast (D14),
plus global filters (region, property type).
"""
import json
from pathlib import Path

EUR = {"type": "number-currency", "currencyCode": "EUR", "abbreviation": "compact", "decimalPlaces": {"type": "max", "places": 1}}
EUR0 = {"type": "number-currency", "currencyCode": "EUR", "abbreviation": "none", "decimalPlaces": {"type": "exact", "places": 0}}
PCT = {"type": "number-percent", "decimalPlaces": {"type": "max", "places": 1}}

DATASETS = {
    "kpi_latest": ("Portfolio KPIs, 2026-Q2 (metric views)", """
SELECT m.revenue, m.net_profit, m.net_profit_margin, t.target_attainment, t.properties_met_target, t.properties, g.qoq_net_profit_growth
FROM (SELECT MEASURE(revenue) AS revenue, MEASURE(net_profit) AS net_profit, MEASURE(net_profit_margin) AS net_profit_margin
      FROM ref_mv_net_profit_margin WHERE fiscal_quarter = '2026-Q2') m
CROSS JOIN (SELECT MEASURE(target_attainment) AS target_attainment, MEASURE(properties_met_target) AS properties_met_target,
                   MEASURE(properties) AS properties FROM ref_mv_target_attainment WHERE fiscal_quarter = '2026-Q2') t
CROSS JOIN (SELECT MEASURE(qoq_net_profit_growth) AS qoq_net_profit_growth FROM ref_mv_qoq_revenue_growth WHERE fiscal_quarter = '2026-Q2') g"""),
    "trend_region": ("Net profit and margin by quarter and region (metric view)", """
SELECT fiscal_quarter, region_name, property_type, MEASURE(revenue) AS revenue, MEASURE(net_profit) AS net_profit
FROM ref_mv_net_profit_margin
GROUP BY ALL"""),
    "property_quarter": ("Property x quarter (certified gold)", """
SELECT property_name, property_type, region_name, market, fiscal_quarter, revenue, revenue_target, net_profit,
       net_profit_target, net_profit - net_profit_target AS variance_to_target, met_target, qoq_change_pct,
       CASE WHEN qoq_change_pct < -10 THEN 'Sharp decline' WHEN qoq_change_pct < 0 THEN 'Decline' ELSE 'OK' END AS qoq_flag
FROM gold_property_quarterly"""),
    "market_qoq": ("QoQ net profit growth by market (metric view)", """
SELECT market, fiscal_quarter, region_name, MEASURE(qoq_net_profit_growth) AS qoq_net_profit_growth
FROM ref_mv_qoq_revenue_growth
WHERE fiscal_quarter >= '2024-Q2'
GROUP BY ALL"""),
    "forecast": ("Revenue actuals + ai_forecast with 95% interval (Demo 14)", """
SELECT property_name, region_name, property_type, fiscal_quarter_date, series, value FROM (
  SELECT property_name, region_name, property_type, fiscal_quarter_date,
         stack(5, 'Actual', revenue_actual, 'Forecast', revenue_forecast, 'Lower 95%', revenue_lower,
                  'Upper 95%', revenue_upper, 'Target', revenue_target) AS (series, value)
  FROM ref_d14_revenue_forecast)
WHERE value IS NOT NULL
UNION ALL
-- anchor the forecast and interval lines on the last actual so they connect
SELECT property_name, region_name, property_type, fiscal_quarter_date, s.series, revenue_actual
FROM ref_d14_revenue_forecast
CROSS JOIN (SELECT explode(array('Forecast', 'Lower 95%', 'Upper 95%')) AS series) s
WHERE fiscal_quarter = '2026-Q2'"""),
}

_n = 0


def wid(prefix):
    global _n
    _n += 1
    return f"{prefix}{_n:03d}"


def q(ds, fields, disaggregated=True, name="main_query"):
    return [{"name": name, "query": {"datasetName": ds, "fields": [{"name": f, "expression": e} for f, e in fields],
                                     "disaggregated": disaggregated}}]


def text(md):
    return {"name": wid("txt"), "multilineTextboxSpec": {"lines": [md]}}


def counter(ds, field, title, fmt):
    return {"name": wid("ctr"), "queries": q(ds, [(field, f"`{field}`")]),
            "spec": {"version": 2, "widgetType": "counter",
                     "encodings": {"value": {"fieldName": field, "displayName": title, "format": fmt}},
                     "frame": {"showTitle": True, "title": title}}}


def chart(kind, ds, x, y, title, color=None, agg=None, xscale="categorical", yfmt=EUR, extra=None):
    yexpr = f"{agg}(`{y[0]}`)" if agg else f"`{y[0]}`"
    yname = f"{agg.lower()}({y[0]})" if agg else y[0]
    fields = [(x[0], f"`{x[0]}`"), (yname, yexpr)] + ([(color[0], f"`{color[0]}`")] if color else [])
    enc = {"x": {"fieldName": x[0], "scale": {"type": xscale}, "displayName": x[1]},
           "y": {"fieldName": yname, "scale": {"type": "quantitative"}, "displayName": y[1], "format": yfmt}}
    if color:
        enc["color"] = {"fieldName": color[0], "scale": {"type": "categorical"}, "displayName": color[1]}
    spec = {"version": 3, "widgetType": kind, "encodings": enc, "frame": {"showTitle": True, "title": title}}
    spec.update(extra or {})
    return {"name": wid("chr"), "queries": q(ds, fields, disaggregated=not agg), "spec": spec}


def scatter(ds, title):
    fields = [("revenue_target", "`revenue_target`"), ("revenue", "`revenue`"), ("property_name", "`property_name`")]
    return {"name": wid("chr"), "queries": q(ds, fields),
            "spec": {"version": 3, "widgetType": "scatter",
                     "encodings": {"x": {"fieldName": "revenue_target", "scale": {"type": "quantitative"}, "displayName": "Revenue target", "format": EUR},
                                   "y": {"fieldName": "revenue", "scale": {"type": "quantitative"}, "displayName": "Revenue", "format": EUR},
                                   "color": {"fieldName": "property_name", "scale": {"type": "categorical"}, "displayName": "Property"}},
                     "frame": {"showTitle": True, "title": title}}}


def heatmap(ds, title):
    fields = [("fiscal_quarter", "`fiscal_quarter`"), ("market", "`market`"), ("qoq", "`qoq_net_profit_growth`")]
    return {"name": wid("chr"), "queries": q(ds, fields),
            "spec": {"version": 3, "widgetType": "heatmap",
                     "encodings": {"x": {"fieldName": "fiscal_quarter", "scale": {"type": "categorical"}, "displayName": "Quarter"},
                                   "y": {"fieldName": "market", "scale": {"type": "categorical"}, "displayName": "Market"},
                                   "color": {"fieldName": "qoq", "scale": {"type": "quantitative"}, "displayName": "QoQ net profit growth", "format": PCT}},
                     "frame": {"showTitle": True, "title": title}}}


def table(ds, cols, title):
    fields = [(c, f"`{c}`") for c, _, _ in cols]
    columns = [dict({"fieldName": c, "displayName": n}, **({"format": f} if f else {})) for c, n, f in cols]
    return {"name": wid("tbl"), "queries": q(ds, fields),
            "spec": {"version": 2, "widgetType": "table", "encodings": {"columns": columns},
                     "frame": {"showTitle": True, "title": title}}}


def filt(kind, field, title, datasets, default=None):
    queries = [{"name": f"f_{ds}_{field}", "query": {"datasetName": ds, "fields": [{"name": field, "expression": f"`{field}`"}],
                                                      "disaggregated": False}} for ds in datasets]
    spec = {"version": 2, "widgetType": kind,
            "encodings": {"fields": [{"fieldName": field, "displayName": title, "queryName": qq["name"]} for qq in queries]},
            "frame": {"showTitle": True, "title": title}}
    if default:
        spec["selection"] = {"defaultSelection": {"values": {"dataType": "STRING", "values": [{"value": default}]}}}
    return {"name": wid("flt"), "queries": queries, "spec": spec}


def page(name, title, items):
    return {"name": name, "displayName": title, "pageType": "PAGE_TYPE_CANVAS",
            "layout": [{"widget": w, "position": dict(zip("xywh", p)) | {"width": p[2], "height": p[3]}} for w, p in items]}


def fix(pos):
    return {"x": pos["x"], "y": pos["y"], "width": pos["width"], "height": pos["height"]}


GLOBAL_DS = ["trend_region", "property_quarter", "market_qoq", "forecast"]
pages = [
    page("exec", "Executive Summary", [
        (text("# Revantage Portfolio Review\n\nCertified view of **2026-Q2** (latest complete quarter). KPIs come from the governed metric views "
              "(`ref_mv_*`): net profit = revenue − operating expense − management fees (Finance definition)."), (0, 0, 6, 2, 0)),
        (counter("kpi_latest", "revenue", "Revenue 2026-Q2", EUR), (0, 2, 2, 3, 0)),
        (counter("kpi_latest", "net_profit_margin", "Net profit margin", PCT), (2, 2, 1, 3, 0)),
        (counter("kpi_latest", "target_attainment", "Target attainment", PCT), (3, 2, 1, 3, 0)),
        (counter("kpi_latest", "qoq_net_profit_growth", "Net profit QoQ", PCT), (4, 2, 2, 3, 0)),
        (chart("line", "trend_region", ("fiscal_quarter", "Fiscal quarter"), ("net_profit", "Net profit"),
               "Net profit trend by region", color=("region_name", "Region"), agg="SUM"), (0, 5, 6, 7, 0)),
    ]),
    page("regional", "Regional Performance", [
        (filt("filter-single-select", "fiscal_quarter", "Fiscal quarter", ["property_quarter"], default="2026-Q2"), (0, 0, 2, 2, 0)),
        (chart("bar", "property_quarter", ("region_name", "Region"), ("net_profit", "Net profit"), "Net profit by region",
               agg="SUM"), (0, 2, 3, 7, 0)),
        (scatter("property_quarter", "Revenue vs target by property"), (3, 2, 3, 7, 0)),
        (heatmap("market_qoq", "QoQ net profit growth by market"), (0, 9, 6, 7, 0)),
    ]),
    page("exceptions", "Exceptions & Risks", [
        (filt("filter-single-select", "fiscal_quarter", "Fiscal quarter", ["property_quarter"], default="2026-Q2"), (0, 0, 2, 2, 0)),
        (filt("filter-multi-select", "met_target", "Met target", ["property_quarter"]), (2, 0, 2, 2, 0)),
        (table("property_quarter", [("property_name", "Property", None), ("region_name", "Region", None),
                                    ("property_type", "Type", None), ("net_profit", "Net profit", EUR0),
                                    ("net_profit_target", "Target", EUR0), ("variance_to_target", "Variance", EUR0),
                                    ("qoq_change_pct", "QoQ %", None), ("qoq_flag", "QoQ flag", None),
                                    ("met_target", "Met target", None)], "Properties vs target"), (0, 2, 6, 8, 0)),
    ]),
    page("forecast_page", "Forecast", [
        (filt("filter-single-select", "property_name", "Property", ["forecast"], default="Harbor Tower"), (0, 0, 2, 2, 0)),
        (text("Revenue actuals to 2026-Q2 and `ai_forecast` for 2026-Q3/Q4 with the 95% interval, against target. "
              "The forecast can't see that Harbor Tower's anchor tenant left on 31 March."), (2, 0, 4, 2, 0)),
        (chart("line", "forecast", ("fiscal_quarter_date", "Quarter"), ("value", "Revenue"), "Revenue: actual, forecast, interval, target",
               color=("series", "Series"), agg="SUM", xscale="temporal"), (0, 2, 6, 8, 0)),
    ]),
    {"name": "global_filters", "displayName": "Global filters", "pageType": "PAGE_TYPE_GLOBAL_FILTERS", "layout": [
        {"widget": filt("filter-multi-select", "region_name", "Region", GLOBAL_DS), "position": {"x": 0, "y": 0, "width": 1, "height": 2}},
        {"widget": filt("filter-multi-select", "property_type", "Property type", ["trend_region", "property_quarter", "forecast"]), "position": {"x": 1, "y": 0, "width": 1, "height": 2}},
    ]},
]
for p in pages:
    for item in p["layout"]:
        item["position"] = fix(item["position"])

dash = {"datasets": [{"name": k, "displayName": v[0], "queryLines": [l + "\n" for l in v[1].strip().splitlines()]}
                     for k, v in DATASETS.items()], "pages": pages, "uiSettings": {"theme": {"widgetHeaderAlignment": "LEFT"}}}
out = Path(__file__).with_name("revantage-portfolio-review.lvdash.json")
out.write_text(json.dumps(dash, indent=2))
print(f"wrote {out}")
