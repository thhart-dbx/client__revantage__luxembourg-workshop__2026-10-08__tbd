# Demo 18 reference Pages (domain "Revantage Workshop")

Four Pages, one per business rule the Demo 17 benchmark trips over. Each lists the fields of the Pages
editor (Discover → Pages → Create page). Participants write their own with Genie Code ("Help me create a
new page"); these are the answer key. `<catalog>.<schema>` = the workshop schema.
Pages are stored in plain text and replicated globally: no PII, no confidential numbers.

## Net profit
- **Synonyms:** NOI, net operating income, bottom line, profit
- **Description:** Revantage's approved (Finance) net profit: revenue minus operating expense minus management fee. CapEx and intercompany recharges are not deducted.
- **Definition:** Net profit = revenue − operating expense − management fee, per property and fiscal quarter, in EUR. In the general ledger: account_class R − O − M. CapEx (C) and intercompany recharges (I) are excluded. Asset Management also subtracts CapEx; that variant is not approved and must be labelled when shown.
- **Business use:** quarterly property P&L, target attainment, the executive dashboard, investor reporting.
- **Related assets:** `<catalog>.<schema>.ref_mv_net_profit_margin` (metric view), `<catalog>.<schema>.gold_property_quarterly`, `<catalog>.<schema>.ref_d17_gl_accounts`
- **Sources:** Capital Expenditure Guidelines (policy PDF in the `documents` volume)

## Latest quarter
- **Synonyms:** this quarter, current quarter, last quarter, most recent quarter, QTD
- **Description:** "This quarter" is the latest complete fiscal quarter in the data (2026-Q2), not the calendar quarter.
- **Definition:** "This quarter" / "current quarter" means the latest complete fiscal quarter in the data, 2026-Q2; "last quarter" means the one before it, 2026-Q1. Never derive the quarter from today's date.
- **Business use:** every KPI question without an explicit period.
- **Related assets:** `<catalog>.<schema>.gold_property_quarterly` (fiscal_quarter), `<catalog>.<schema>.ref_mv_net_profit_margin`

## Active lease
- **Synonyms:** current lease, rent roll, occupied
- **Description:** A lease that is currently running: the latest version of the lease has status Active.
- **Definition:** Lease tables keep every version of a lease. Take only the latest version per lease_id (highest updated_at), then count it as active when lease_status is Active (code A). Pending Renewal (P) and Expired (X) are not active. Monthly rent is in EUR.
- **Business use:** occupancy, rent at risk, lease-expiry tracking (Demo 9 app).
- **Related assets:** `<catalog>.<schema>.silver_leases`, `<catalog>.<schema>.ref_d17_leases`

## Below investment grade
- **Synonyms:** sub-investment grade, high yield, junk, weak credit
- **Description:** A tenant whose credit rating is BB or B.
- **Definition:** Credit ratings from best to worst: AAA, AA, A, BBB, BB, B. Investment grade is BBB or better; below investment grade is BB or B.
- **Business use:** tenant risk, lease renewal approvals, portfolio risk summaries.
- **Related assets:** `<catalog>.<schema>.silver_tenants`, `<catalog>.<schema>.ref_d17_tenants`
