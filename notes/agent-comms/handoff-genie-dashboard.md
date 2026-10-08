# Handoff: Genie Agents & Dashboard (genie-dashboard area)

**Owner:** genie-dashboard agent  
**Demos covered:** D2 (Genie One Q&A), D8 (AI/BI Dashboards), +D6 & D7-step-6 verification  
**Completion date:** 2026-10-08  
**Status:** READY FOR TESTING & DEPLOYMENT

---

## Assets Created

### 1. Genie Agents (2)

Both deployed from `code/resources/genie_dashboard.yml`:

#### a) "Revantage Portfolio Q&A (Start)" (Demo 2)
- **Bundle key:** `genie_spaces.portfolio_qa_start`
- **Parent path:** `${var.genie_space_path}` (e.g., `/Users/thomas.hart@databricks.com/spaces`)
- **Warehouse:** `${var.warehouse_id}`
- **Tables:** gold_property_quarterly, silver_properties, silver_leases, silver_tenants
- **Sample questions:** 5 D2 questions (missed targets, regional change, revenue chart, market growth, portfolio risks)
- **Purpose:** Demo 2 starting state; participants build similar agents live
- **Verification:** 5 questions tested via Genie API (see `code/prompts/verification/d02-genie.md`)

#### b) "Revantage Portfolio Q&A (Reference)" (Demo 7+)
- **Bundle key:** `genie_spaces.portfolio_qa_reference`
- **Parent path:** Same as Start
- **Warehouse:** Same
- **Tables:** gold_property_quarterly, silver_properties
- **Metric views:** ref_mv_net_profit_margin, ref_mv_target_attainment
- **Sample questions:** 5 D7 questions (missed targets w/ why, Southeast drop, margin by region, attainment %, risk properties)
- **Example SQL:** 1 example query (missed targets)
- **Join specs:** gold_property_quarterly ↔ silver_properties
- **Instructions:** Finance net-profit definition (Revenue - OpEx - Mgmt Fees), ownership, time periods
- **Purpose:** Reference solution; demonstrates metric view integration; used for D7 verification + D6/D7-step-6
- **Verification:** Step 6 ("Which properties missed target?") tested via API (see `code/prompts/verification/d07-genie.md`)

### 2. Dashboard (1)

#### "Revantage Portfolio Review (Reference)" (Demo 8)
- **Bundle key:** `dashboards.portfolio_review_dashboard`
- **File:** `code/dashboards/revantage-portfolio-review.lvdash.json`
- **Pages:** 4 (Executive Summary, Regional Performance, Exceptions & Risks, Forecast placeholder)
- **Datasets:** 7 (kpis, region_qoq, region_trend, revenue_vs_target, qoq_heatmap, missed_target, portfolio_detail)
- **Global filters:** fiscal_quarter (2026-Q1/Q2), region_name (optional; via data)
- **Warehouse:** `${var.warehouse_id}`
- **Catalog/schema:** `${var.catalog}.${var.schema}`
- **Permissions:** `CAN_READ` for `${var.consumer_group}` (revantage_consumers)
- **Genie integration:** Dashboard dashboard links to Genie agents for "Explain" buttons (link enabled in Lakeview)

**Page details:**
| Page | Widgets | Expected values (Q2 2026) | Status |
|---|---|---|---|
| Executive Summary | 3 KPI counters (NP, QoQ%, attainment%) + trend line | €6.38M, −18.6%, 62.5% | Ready |
| Regional | Bar (region NP Q1/Q2), scatter (revenue vs target), heatmap (QoQ% by market) | Southeast down, Luxembourg +10%, Miami Beach −44% | Ready |
| Exceptions | Table: 3 missed-target properties with QoQ flags | Harbor Tower, Peachtree, Zuidas | Ready |
| Forecast | Placeholder text (Demo 14) | "Forecast data will be populated…" | Ready |

### 3. Prompt Library Files (2)

- `code/prompts/d02-genie-one.md` — 6-stage guide (setup, 5 Q&A questions); 45 min; expected SQL & checkpoint queries
- `code/prompts/d08-dashboards.md` — 9-stage guide (setup, 6 pages/widgets, Genie integration, optional filters); 60 min; checkpoint queries

### 4. Verification Files (4)

All in `code/prompts/verification/`:

| File | Purpose | Status |
|---|---|---|
| `d02-genie.md` | D2: All 5 Genie questions + expected answers | Template ready; await API testing |
| `d06-genie.md` | D6: 5 data quality audit questions | Template ready; await API testing |
| `d07-genie.md` | D7-step-6: Metric view question | Template ready; await API testing |
| `d08-dashboards.md` | D8: All 4 pages + widgets; Genie explain test | Template ready; await API testing |

### 5. Configuration Updates

**File:** `code/databricks.yml`
- **New variable:** `consumer_group` (default: `revantage_consumers`)
- **Rationale:** Permissions for Genie spaces and dashboard

---

## Dependencies

**Met (no blocking):**
- ✓ Starting state (S1, S2): bronze/silver/gold tables deployed
- ✓ Metric tables: Created by analytics-sql agent (`ref_mv_net_profit_margin`, `ref_mv_target_attainment`, `ref_mv_qoq_revenue_growth`) via `analytics_ref.yml` job

**To be deployed before testing:**
1. Run `databricks bundle deploy -t dev` (deploys Genie agents + dashboard + config)
2. Run `databricks bundle run ref_metric_views -t dev` (from analytics_ref.yml; creates metric tables)

---

## Testing

**Manual verification required:**
- Open Genie spaces in workspace → test 5 D2 questions + 5 D7 questions
- Open dashboard → verify all 4 pages load, KPI values match expected, charts render
- Test Genie integration on dashboard (click Southeast bar → "Explain with Genie")

**API verification (script):**
See `code/prompts/verification/*-genie.md` and `*-dashboards.md` for expected values & test queries.

---

## Known Gaps / Issues

1. **Forecast page (D14):** Placeholder only; awaits `ref_d14_revenue_forecast` table from analytics-sql
2. **Metric view integration:** Genie agents reference metric tables `ref_mv_*` created by analytics-sql job; not created by this agent
3. **Genie API tests:** Verification files are templates; actual test runs pending deployment
4. **Consumer group:** Variable assumes `revantage_consumers` group exists; create if missing

---

## Deployment Checklist

- [ ] `databricks bundle validate -t dev` passes
- [ ] `databricks bundle plan -t dev` shows Genie agents + dashboard in create list
- [ ] `databricks bundle deploy -t dev` succeeds
- [ ] `databricks bundle run ref_metric_views -t dev` succeeds (wait for analytics-sql agent first)
- [ ] Genie spaces appear in workspace
- [ ] Dashboard appears in workspace
- [ ] Verify D2 questions (Genie API or UI)
- [ ] Verify D8 dashboard (UI)
- [ ] Verify D7-step-6 (Genie API)
- [ ] Update verification files with actual results

---

## Handoff to Orchestrator

**To move to next phase:**
1. Confirm bundle deploy succeeds
2. Run metric views job (analytics-sql owns this)
3. Run D2 + D8 UI verification (captures screenshots for click-path)
4. Run D6 + D7-step-6 Genie API tests (record generated SQL + answers)
5. Update verification files with VERIFIED status
6. Provide IDs/URLs of deployed Genie spaces & dashboard for README

---

## Files Modified / Created

```
code/resources/genie_dashboard.yml          [NEW] — Genie agents + dashboard resource definitions
code/dashboards/revantage-portfolio-review.lvdash.json [NEW] — Dashboard JSON (4 pages, 7 datasets)
code/prompts/d02-genie-one.md               [NEW] — Demo 2 prompt library
code/prompts/d08-dashboards.md              [NEW] — Demo 8 prompt library
code/prompts/verification/d02-genie.md      [NEW] — D2 Genie API verification template
code/prompts/verification/d06-genie.md      [NEW] — D6 Genie API verification template
code/prompts/verification/d07-genie.md      [NEW] — D7-step-6 Genie API verification template
code/prompts/verification/d08-dashboards.md [NEW] — D8 dashboard verification template
code/databricks.yml                         [MODIFIED] — Added consumer_group variable
code/scripts/build_genie_spaces.py          [NEW] — Reference script for Genie JSON generation (informational)
code/governance/                            [NEW DIR] — Created for potential governance SQL (unused)
```

---

## Next Steps (Orchestrator)

1. Merge this PR and deploy
2. Post Genie IDs/URLs in README once deployed
3. Run verification tests (Genie API, dashboard UI)
4. Approve click-path screenshots for D2 & D8
5. Prepare for participant workshop (D2 & D8 are participant build-alongs; reference solutions are answer keys)
