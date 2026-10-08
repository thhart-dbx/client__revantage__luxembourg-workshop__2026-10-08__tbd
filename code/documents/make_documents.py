#!/usr/bin/env python3
"""
Generate synthetic business documents (invoices, policies, leases) for Databricks workshop.
Uses only stdlib; converts HTML to PDF with headless Chrome.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
BUILD_HTML_DIR = BASE_DIR / "build" / "html"
BUILD_PREVIEW_DIR = BASE_DIR / "build" / "preview"
OUT_DIR = BASE_DIR / "out"
OUT_INVOICES = OUT_DIR / "invoices"
OUT_POLICIES = OUT_DIR / "policies"
OUT_LEASES = OUT_DIR / "leases"

# Chrome path (macOS)
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Portfolio properties
PROPERTIES = {
    "harbor_tower": {"name": "Harbor Tower Propco LLC", "address": "Miami Beach, FL", "location": "Miami Beach"},
    "peachtree_center": {"name": "Peachtree Center Propco LLC", "address": "Atlanta, GA", "location": "Atlanta"},
    "biscayne_point": {"name": "Biscayne Point Propco LLC", "address": "Miami, FL", "location": "Miami"},
    "chelsea_lofts": {"name": "Chelsea Lofts Propco LLC", "address": "New York, NY", "location": "New York"},
    "back_bay": {"name": "Back Bay Commons Propco LLC", "address": "Boston, MA", "location": "Boston"},
    "kirchberg": {"name": "Kirchberg Plaza S.à r.l.", "address": "2 rue Eugène Ruppert, L-2453 Luxembourg", "location": "Luxembourg"},
    "cloche_dor": {"name": "Cloche d'Or Propco S.à r.l.", "address": "L-1219 Luxembourg", "location": "Luxembourg"},
    "zuidas": {"name": "Zuidas Residences B.V.", "address": "Amsterdam, Netherlands", "location": "Amsterdam"},
}

# Invoice data
INVOICES = [
    {
        "invoice_number": "HV-2026-0417",
        "vendor_name": "Coastal Climate Systems LLC",
        "vendor_address": "2847 Biscayne Blvd, Miami, FL 33137",
        "vendor_tax_id": "12-3456789",
        "bill_to_name": "Harbor Tower Propco LLC",
        "bill_to_address": "c/o Revantage, Miami Beach, FL",
        "invoice_date": "2026-05-12",
        "due_date": "2026-06-11",
        "currency": "USD",
        "lines": [
            {"description": "Carrier 30XA 400-ton air-cooled chiller (replacement unit)", "quantity": 1, "unit_price": 214500.00},
            {"description": "Crane lift, rigging and removal of failed chiller", "quantity": 1, "unit_price": 38900.00},
            {"description": "Installation, piping and controls integration", "quantity": 1, "unit_price": 61200.00},
            {"description": "Commissioning and 5-year parts warranty", "quantity": 1, "unit_price": 25000.00},
        ],
        "tax_rate": 0.0,
        "note": "Replacement of end-of-life rooftop chiller; expected useful life 20 years.\nExempt as commercial capital improvement.",
        "layout": "traditional",
    },
    {
        "invoice_number": "PE-2026-06-0088",
        "vendor_name": "Peachtree Energy Services",
        "vendor_address": "445 Peachtree St NE, Atlanta, GA 30308",
        "vendor_tax_id": "58-9876543",
        "bill_to_name": "Peachtree Center Propco LLC",
        "bill_to_address": "c/o Revantage, Atlanta, GA",
        "invoice_date": "2026-06-05",
        "due_date": "2026-07-05",
        "currency": "USD",
        "lines": [
            {"description": "Electricity consumption – May 2026 (125,400 kWh @ $0.1245/kWh)", "quantity": 1, "unit_price": 15617.48},
            {"description": "Chilled water service – May 2026", "quantity": 1, "unit_price": 19430.00},
            {"description": "Water & sewer usage – May 2026", "quantity": 1, "unit_price": 5952.52},
        ],
        "tax_rate": 0.0,
        "note": "Utility invoice for calendar month of May 2026.",
        "layout": "table_heavy",
    },
    {
        "invoice_number": "TM-POL-2026-3391",
        "vendor_name": "Thames Mutual Property Insurance plc",
        "vendor_address": "Leadenhall Street, London EC3V 1PP, UK",
        "vendor_tax_id": "GB123456789",
        "bill_to_name": "Revantage Europe",
        "bill_to_address": "Luxembourg City, Luxembourg",
        "invoice_date": "2026-06-20",
        "due_date": "2026-07-20",
        "currency": "GBP",
        "lines": [
            {"description": "Q3 2026 all-risks property premium (Western Europe schedule, 8 properties)", "quantity": 1, "unit_price": 42000.00},
            {"description": "Terrorism cover – optional extension", "quantity": 1, "unit_price": 6500.00},
            {"description": "Administration fee", "quantity": 1, "unit_price": 850.00},
        ],
        "tax_rate": 0.12,
        "tax_label": "Insurance Premium Tax (12%)",
        "note": "Premium due by 20 July 2026. Coverage effective 01 July – 30 September 2026.",
        "layout": "insurance",
    },
    {
        "invoice_number": "ACD-2026-IF-55120",
        "vendor_name": "Ville de Luxembourg – Service des Contributions",
        "vendor_address": "4 rue de la Congrégation, L-1352 Luxembourg",
        "vendor_tax_id": "N/A",
        "bill_to_name": "Kirchberg Plaza S.à r.l.",
        "bill_to_address": "L-1919 Luxembourg",
        "invoice_date": "2026-04-15",
        "due_date": "2026-05-31",
        "currency": "EUR",
        "lines": [
            {"description": "Impôt foncier 2026 – Kirchberg Plaza (cadastral value €1,950,000 × 1.427%)", "quantity": 1, "unit_price": 27826.50},
        ],
        "tax_rate": 0.0,
        "note": "Official municipal property tax assessment. Bilingual notice (French/English).",
        "layout": "government",
    },
    {
        "invoice_number": "NGD-26-1184",
        "vendor_name": "Nettoyage Grand-Duché S.à r.l.",
        "vendor_address": "15 avenue de la Liberté, L-1930 Luxembourg",
        "vendor_tax_id": "LU12345678",
        "bill_to_name": "Kirchberg Plaza S.à r.l.",
        "bill_to_address": "L-1919 Luxembourg",
        "invoice_date": "2026-06-30",
        "due_date": "2026-07-30",
        "currency": "EUR",
        "lines": [
            {"description": "Office cleaning June 2026 (16 days @ €480/day)", "quantity": 1, "unit_price": 7680.00},
            {"description": "Window cleaning – quarterly deep clean", "quantity": 1, "unit_price": 2400.00},
            {"description": "Carpet deep-clean – lobby and 3 floor areas", "quantity": 1, "unit_price": 4200.00},
            {"description": "Consumables (detergents, supplies, waste disposal)", "quantity": 1, "unit_price": 1820.00},
            {"description": "Waste removal and recycling management", "quantity": 1, "unit_price": 1350.00},
        ],
        "tax_rate": 0.17,
        "tax_label": "VAT (17%)",
        "note": "Invoice for services rendered June 2026.",
        "layout": "minimalist",
    },
    {
        "invoice_number": "VSB-2026-0612",
        "vendor_name": "Vigilis Security Benelux B.V.",
        "vendor_address": "Europaplein 402, 1079 PC Amsterdam, Netherlands",
        "vendor_tax_id": "NL987654321",
        "bill_to_name": "Zuidas Residences B.V.",
        "bill_to_address": "Amsterdam, Netherlands",
        "invoice_date": "2026-06-12",
        "due_date": "2026-07-12",
        "currency": "EUR",
        "lines": [
            {"description": "On-site guard services (224 hours @ €35/hour)", "quantity": 1, "unit_price": 7840.00},
            {"description": "Mobile patrol visits (8 visits/month, 3 months)", "quantity": 1, "unit_price": 2400.00},
            {"description": "CCTV system maintenance and monitoring", "quantity": 1, "unit_price": 3600.00},
            {"description": "Access-card batch production and issuance (120 cards)", "quantity": 1, "unit_price": 1800.00},
            {"description": "Alarm response call-out fees (2 incidents)", "quantity": 1, "unit_price": 600.00},
            {"description": "24/7 monitoring service charge", "quantity": 1, "unit_price": 9200.00},
        ],
        "tax_rate": 0.21,
        "tax_label": "VAT (21%)",
        "note": "Services provided June 2026; contract term: ongoing.",
        "layout": "sidebar",
    },
    {
        "invoice_number": "ELV-2026-0331",
        "vendor_name": "Elevatech Lifts S.A.",
        "vendor_address": "Rue de Gasperich 18, L-5251 Sandweiler, Luxembourg",
        "vendor_tax_id": "LU98765432",
        "bill_to_name": "Cloche d'Or Retail Park S.à r.l.",
        "bill_to_address": "L-1219 Luxembourg",
        "invoice_date": "2026-03-31",
        "due_date": "2026-04-30",
        "currency": "EUR",
        "lines": [
            {"description": "Q1 2026 escalator & lift maintenance contract (3-month service)", "quantity": 1, "unit_price": 9600.00},
            {"description": "Emergency call-out service – 1 incident (hydraulic system repair)", "quantity": 1, "unit_price": 1980.00},
        ],
        "tax_rate": 0.17,
        "tax_label": "VAT (17%)",
        "note": "Quarterly maintenance for 6 escalators and 4 passenger lifts. Contract includes preventive maintenance.",
        "layout": "twocolumn",
    },
    {
        "invoice_number": "MK-2026-0278",
        "vendor_name": "Moreau & Klein Avocats",
        "vendor_address": "51 avenue de la Faïencerie, L-1511 Luxembourg",
        "vendor_tax_id": "LU55555555",
        "bill_to_name": "Kirchberg Plaza S.à r.l.",
        "bill_to_address": "L-1919 Luxembourg",
        "invoice_date": "2026-06-28",
        "due_date": "2026-07-28",
        "currency": "EUR",
        "lines": [
            {"description": "2026-06-03, Legal research & drafting – MK, Lease renewal negotiation prep", "quantity": 4.5, "unit_price": 350.00},
            {"description": "2026-06-05, Tenant meeting & negotiation – PJ", "quantity": 3.0, "unit_price": 380.00},
            {"description": "2026-06-07, Lease amendment drafting – MK", "quantity": 6.0, "unit_price": 350.00},
            {"description": "2026-06-10, Review of tenant proposal – PJ", "quantity": 2.5, "unit_price": 380.00},
            {"description": "2026-06-12, Financial review with client – MK & PJ", "quantity": 2.0, "unit_price": 365.00},
            {"description": "2026-06-15, Drafting final lease agreement – MK", "quantity": 7.0, "unit_price": 350.00},
            {"description": "2026-06-18, Execution coordination & closing logistics – PJ", "quantity": 1.5, "unit_price": 380.00},
            {"description": "2026-06-22, Post-execution administration – MK", "quantity": 0.5, "unit_price": 350.00},
            {"description": "2026-06-25, Client communication & follow-up – PJ", "quantity": 1.0, "unit_price": 380.00},
        ],
        "tax_rate": 0.17,
        "tax_label": "VAT (17%)",
        "note": "Professional services for Lease renewal negotiation – anchor tenant, Kirchberg Plaza.",
        "layout": "timesheet",
    },
]

# Policies
POLICIES = [
    {
        "filename": "expense-approval-policy.pdf",
        "title": "Expense Approval Policy",
        "version": "1.2",
        "effective_date": "2026-01-01",
        "approved_by": "Investment Committee",
        "content": """
1. PURPOSE AND SCOPE
This policy establishes delegation-of-authority limits and approval workflows for operating expenses and capital expenditures across all Revantage Europe properties.

1.1 Scope
This policy applies to all employees, contractors, and external service providers billing to property-owning SPVs.

2. APPROVAL AUTHORITY
Approval authority for expenses is delegated based on amount (converted to EUR at ECB reference rate on invoice date) and expense type:

2.1 Delegation Table
- €0.01 to €5,000: Property Manager approval
- €5,000.01 to €25,000: Asset Manager approval
- €25,000.01 to €50,000: Head of Asset Management approval
- €50,000.01+: Co-signature of CFO and Asset Management Director (two signatories, never the same person)
- >€500,000: Additional approval required from Investment Committee

2.2 Multi-Currency Conversion
For invoices in foreign currencies (USD, GBP, etc.), amounts must be converted to EUR using the ECB reference rate on the invoice date. Approval threshold is determined by the EUR-converted amount.

2.3 Prohibition on Invoice Splitting
Deliberately splitting a single obligation into multiple invoices to avoid approval thresholds is strictly prohibited. Finance will flag and reject suspicious split invoices.

2.4 Capital Expenditure Classification
Capital expenditure must also follow the Capital Expenditure Guidelines; an item approved under this policy is not thereby classified as OpEx. Classification is determined per the CapEx criteria (replacement/improvement, >€25,000, useful life >3 years).

3. AUTHORIZATION REQUIREMENTS
- Two signatories for expenses >€50,000 must be independent (different roles, different individuals).
- All digital signatures must follow Revantage's document control procedures.
- Supporting documentation (quotes, scope of work, business rationale) must accompany all approvals.

4. FINANCE OVERSIGHT
Finance (Group Finance) retains the right to audit, challenge, and reject any approval where procedures were not followed.
""",
    },
    {
        "filename": "capital-expenditure-guidelines.pdf",
        "title": "Capital Expenditure Guidelines",
        "version": "2.0",
        "effective_date": "2026-01-01",
        "approved_by": "CFO & Head of Finance",
        "content": """
1. DEFINITION OF CAPEX VS. OPEX
1.1 Capital Expenditure (CapEx) Definition
An expenditure is classified as CapEx when ALL three criteria are met:
- It replaces or improves a building system or component
- Cost exceeds €25,000 (or currency equivalent, converted at ECB reference rate on invoice date)
- Useful life of the asset is greater than 3 years

1.2 Operating Expense (OpEx) Definition
All other building-related expenses are classified as OpEx (repairs, maintenance, routine servicing).

1.3 Worked Example: Harbor Tower Chiller
CAPEX: Replacement of a central HVAC chiller (invoice HV-2026-0417, $339,600 ≈ €312,000) is CapEx because:
- It replaces the failed building system (chiller)
- Cost is $339,600 (well above €25,000 threshold)
- Useful life is 20 years (exceeds 3-year threshold)

OPEX: Routine HVAC servicing (e.g., seasonal filter replacement, refrigerant top-up, minor repairs) is OpEx because:
- It does not replace or substantially improve the system
- Useful life is under 1 year

2. DEPRECIATION SCHEDULE
Straight-line depreciation is applied based on asset type and useful life:
- HVAC and mechanical systems: 15–20 years
- Roofs and waterproofing: 20 years
- Tenant improvements: over lease term (typically 3–10 years)
- IT and security systems: 3 years
- Other building components: determined by Finance on case-by-case basis

3. CLASSIFICATION REQUIREMENTS
3.1 Review Timeline
All expenditures >€25,000 (in any currency) must be classified (CapEx or OpEx) by the requesting asset manager before invoice approval.

3.2 Reclassification Process
Misclassified items must be reclassified by Group Finance before quarter close. Upon reclassification:
- A correcting journal entry is posted to account 7000 (Building Improvements)
- The quarterly financial close is adjusted accordingly
- Finance reports the adjustment in the month-end variance analysis

3.3 Finance Sign-Off
All reclassifications are recorded and tracked by Group Finance for audit and tax compliance purposes.

4. APPROVAL ROUTING
CapEx expenditures >€50,000 require co-approval by CFO and Asset Management Director (per Expense Approval Policy).
""",
    },
    {
        "filename": "lease-renewal-procedures.pdf",
        "title": "Lease Renewal Procedures",
        "version": "1.1",
        "effective_date": "2026-01-01",
        "approved_by": "Head of Asset Management",
        "content": """
1. LEASE RENEWAL TIMELINE
A structured renewal process, starting 180 days before lease expiry, ensures we retain quality tenants, secure market rent, and avoid unexpected vacancies.

1.1 Day 180 Before Expiry: Tenant Review
- Asset Manager conducts credit rating review (payment history, financial stability)
- Assess tenant performance (rental history, maintenance issues, lease compliance)
- Decision: Renew, re-let, or non-renew
- Tenants with credit rating below BB are escalated to Head of Asset Management for renewal sign-off

1.2 Day 120 Before Expiry: Issue Renewal Proposal
- Asset Manager drafts renewal proposal with recommended rent (market rent check completed)
- Proposal is sent to tenant via formal notice (Luxembourg leases require bilingual French/English)

1.3 Day 90 Before Expiry: Follow-Up and Re-Letting
- If no tenant response received, issue formal written notice (registered letter, Luxembourg requirement)
- Escalate to Head of Asset Management
- In parallel: begin re-letting marketing and vacancy planning

1.4 Day 30 Before Expiry: Final Decision
- Final decision on renewal or vacancy plan must be made
- If renewing: engage external legal counsel to prepare renewal lease agreement
- If vacating: finalize vacancy readiness (tenant coordination, make-good scope, marketing)

2. CREDIT RATING AND RENEWAL
2.1 Below-BB Tenants
Any tenant with credit rating below BB requires written sign-off from Head of Asset Management before lease renewal is approved.

2.2 Payment History
Tenants with >2 late payments in the preceding 24 months are flagged for alternative consideration (non-renewal, rent increase, additional security).

3. NOTICE REQUIREMENTS
3.1 Luxembourg Leases (Bilingual)
All formal notices to Luxembourg tenants must be provided in both French and English, sent via registered mail (courrier recommandé).

3.2 Other Jurisdictions
Notice requirements follow local law for the property's jurisdiction.

4. EXTERNAL COUNSEL ENGAGEMENT
Once final renewal decision is made (Day 30), external legal counsel (such as Moreau & Klein Avocats) is engaged to:
- Draft or amend lease renewal agreement
- Coordinate with tenant legal representatives
- Prepare final execution package

5. DOCUMENTATION AND APPROVAL
All lease renewals must have written approval from Head of Asset Management or CFO before execution.
""",
    },
    {
        "filename": "intercompany-transfer-policy.pdf",
        "title": "Intercompany Transfer Policy",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "approved_by": "Group Finance",
        "content": """
1. PURPOSE
This policy governs transfers of funds and services between Revantage Europe (parent company) and property-owning Propcos (subsidiaries), ensuring arm's-length transfer pricing, proper documentation, and accurate financial reporting. This policy covers intercompany shared-services recharges; the third-party property management fee is covered separately.

2. PROPERTY MANAGEMENT FEE (Third-Party)
2.1 Charged to Propcos
Property management services (leasing, maintenance coordination, tenant relations) are contracted to third-party property managers (account 6000 Management Fees). The fee is 3% of gross revenue, charged monthly by the contractor.

2.2 Included in Net Profit Calculation
The property management fee IS deducted from each Propco's property net profit (for KPIs, bonus calculations, internal reporting). It is treated as a normal operating expense.

2.3 Documentation
Invoices and contracts with third-party property managers are maintained by Finance.

3. INTERCOMPANY SHARED-SERVICES RECHARGES
3.1 Recharge Mechanism
Revantage Europe provides group shared services (IT, finance, human resources, treasury) to each property-owning Propco. These costs are recharged quarterly as intercompany charges (account 8000 Intercompany Charges).

3.2 Recharge Rate
Intercompany shared-services recharge equals 1.5% of gross rental revenue (and other property operating revenue) per quarter.

3.3 Billing Quarterly
- Each Propco receives a quarterly invoice from Revantage Europe
- Invoice is dated on the last day of the quarter (31 Mar, 30 Jun, 30 Sep, 31 Dec)
- Amount is 1.5% × (gross revenue collected from tenants in that quarter)

3.4 Examples
- Harbor Tower Propco LLC: quarterly rent = $472,000 → intercompany recharge = $7,080
- Kirchberg Plaza S.à r.l.: quarterly rent = €600,000 → intercompany recharge = €9,000

4. INTERCOMPANY LOAN INTEREST
4.1 Intercompany Loans
Where Revantage Europe finances Propco operations via intercompany loans, interest accrues at a rate determined annually by the Board (arm's-length rate, comparable to market debt rates for similar risk).

4.2 Interest Charged
Interest on intercompany loans is charged monthly and billed quarterly (account 8100 Intercompany Loan Interest). The rate and principal amount are documented in a formal intercompany loan agreement.

4.3 Settlement
Interest payments are subject to the same 30-day settlement terms as other intercompany charges.

5. ARM'S-LENGTH TRANSFER PRICING
5.1 Fair Market Rate
All intercompany charges (shared-services recharge and loan interest) are reviewed annually by Finance and approved by the Board to ensure they reflect arm's-length rates (comparable to market prices for similar services and debt rates in each jurisdiction).

5.2 Documentation
Transfer pricing documentation must be maintained by Group Finance for tax compliance in each jurisdiction (EU transfer pricing regulations).

6. EXCLUSION FROM NET PROFIT REPORTING
6.1 Reporting to Finance
When calculating property net profit (for KPIs, bonus calculations, or internal reporting), intercompany shared-services charges (account 8000) and intercompany loan interest (account 8100) are excluded from the property's "cost of operations."

6.2 Separate Disclosure
Intercompany charges are tracked separately by Finance and reported in a dedicated schedule (not netted into operating profit). Property net profit is shown before intercompany charges.

6.3 Example
- Kirchberg Plaza gross revenue: €600,000
- Operating costs (utilities, cleaning, maintenance): €210,000
- Third-party management fee (account 6000): €18,000 (3% of revenue) — INCLUDED in net profit
- Net profit reported to executive management: €372,000 (includes the €18,000 fee as operating cost)
- Separate disclosure: Intercompany shared-services recharge: €9,000 (1.5%); Intercompany loan interest: €2,400
- Finance reports: "Property net profit before intercompany charges: €372,000"

7. SETTLEMENT AND RECONCILIATION
7.1 Settlement Terms
All intercompany invoices must be paid within 30 days of invoice date.

7.2 Variance Reconciliation
At each quarter close, Finance reconciles the Propco's payment with the invoice raised by Revantage Europe.
- Discrepancies >€1,000 (absolute amount) must be investigated and resolved before quarter close
- Prepayments or underpayments >€1,000 must be documented and carry-forwarded to the next quarter

7.3 Year-End True-Up
At year-end (31 December), Finance performs a full true-up: reconciles actual revenue received by each Propco to the intercompany charges billed, and adjusts any over/under-charges in a Year-End Adjustment invoice (January).

8. PROHIBITED ACTIVITIES
- Transfer pricing that deviates significantly from the arm's-length rates without Board approval
- Intercompany debt arrangements that are not documented
- Split invoicing or timing manipulations to avoid consolidated reporting

9. EXCEPTIONS
Any exceptions to this policy (non-standard intercompany charges, one-time transfers) require written approval from the CFO and Group Finance.
""",
    },
]

# Helper functions
def calculate_line_amounts(lines):
    """Calculate line amounts and totals. Returns modified lines + subtotal, tax, total."""
    for line in lines:
        line["amount"] = round(line["quantity"] * line["unit_price"], 2)
    subtotal = round(sum(line["amount"] for line in lines), 2)
    return lines, subtotal


def generate_invoice_html(inv):
    """Generate HTML for invoice based on layout type."""
    lines, subtotal = calculate_line_amounts(inv["lines"][:])
    tax = round(subtotal * inv["tax_rate"], 2)
    total = round(subtotal + tax, 2)

    # Store amounts for ground truth
    inv["_subtotal"] = subtotal
    inv["_tax"] = tax
    inv["_total"] = total
    inv["_lines"] = lines

    layout = inv.get("layout", "traditional")

    if layout == "traditional":
        return html_traditional(inv, lines, subtotal, tax, total)
    elif layout == "table_heavy":
        return html_table_heavy(inv, lines, subtotal, tax, total)
    elif layout == "insurance":
        return html_insurance(inv, lines, subtotal, tax, total)
    elif layout == "government":
        return html_government(inv, lines, subtotal, tax, total)
    elif layout == "minimalist":
        return html_minimalist(inv, lines, subtotal, tax, total)
    elif layout == "sidebar":
        return html_sidebar(inv, lines, subtotal, tax, total)
    elif layout == "twocolumn":
        return html_twocolumn(inv, lines, subtotal, tax, total)
    elif layout == "timesheet":
        return html_timesheet(inv, lines, subtotal, tax, total)
    else:
        return html_traditional(inv, lines, subtotal, tax, total)


def html_traditional(inv, lines, subtotal, tax, total):
    """Traditional business invoice layout."""
    tax_rate_pct = f"{inv['tax_rate']*100:.0f}%"
    tax_label = inv.get("tax_label", f"Tax ({tax_rate_pct})")
    currency_symbol = "€" if inv["currency"] == "EUR" else ("$" if inv["currency"] == "USD" else "£")
    tax_line = f'<tr><td colspan="3" style="text-align: right; padding: 8px; font-weight: bold;">{tax_label}:</td><td style="text-align: right; padding: 8px; border-top: 1px solid #000; font-weight: bold;">{currency_symbol}{tax:,.2f}</td></tr>' if tax > 0 else ''

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{inv['invoice_number']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333 }}
.header {{ display: flex; justify-content: space-between; margin-bottom: 40px; border-bottom: 3px solid #1a5490; padding-bottom: 20px }}
.company-info h1 {{ margin: 0; color: #1a5490; font-size: 28px }}
.company-info p {{ margin: 4px 0; font-size: 11px; color: #666 }}
.invoice-meta {{ text-align: right; font-size: 12px }}
.invoice-meta div {{ margin: 4px 0 }}
.label {{ font-weight: bold; color: #1a5490 }}
.bill-to {{ margin: 30px 0; font-size: 12px }}
.bill-to-label {{ font-weight: bold; margin-bottom: 8px; text-transform: uppercase; font-size: 11px; color: #666 }}
.bill-to-content {{ background: #f5f5f5; padding: 12px; border-left: 4px solid #1a5490 }}
table {{ width: 100%; border-collapse: collapse; margin: 30px 0 }}
table th {{ background: #1a5490; color: white; padding: 12px; text-align: left; font-weight: bold; font-size: 12px }}
table td {{ padding: 10px 8px; border-bottom: 1px solid #ddd; font-size: 12px }}
table tr:nth-child(even) {{ background: #f9f9f9 }}
.totals {{ margin: 30px 0; text-align: right; font-size: 13px }}
.totals-row {{ display: flex; justify-content: flex-end; margin: 8px 0 }}
.totals-row .label {{ width: 150px; text-align: right; padding-right: 20px }}
.totals-row .amount {{ width: 100px; text-align: right; font-weight: bold }}
.total-amount {{ background: #1a5490; color: white; padding: 12px; border-radius: 4px; font-size: 16px; font-weight: bold; margin-top: 12px }}
.note {{ margin-top: 30px; padding: 12px; background: #fffacd; border-left: 3px solid #f0a000; font-size: 11px; line-height: 1.5 }}
</style>
</head>
<body>
<div class="header">
  <div class="company-info">
    <h1>{inv['vendor_name']}</h1>
    <p>{inv['vendor_address']}</p>
    <p>Tax ID: {inv['vendor_tax_id']}</p>
  </div>
  <div class="invoice-meta">
    <div><span class="label">Invoice #:</span> {inv['invoice_number']}</div>
    <div><span class="label">Date:</span> {inv['invoice_date']}</div>
    <div><span class="label">Due:</span> {inv['due_date']}</div>
    <div style="font-weight: bold; color: #1a5490; margin-top: 8px">{inv['currency']}</div>
  </div>
</div>

<div class="bill-to">
  <div class="bill-to-label">Bill To:</div>
  <div class="bill-to-content">
    <strong>{inv['bill_to_name']}</strong><br/>
    {inv['bill_to_address']}
  </div>
</div>

<table>
  <thead>
    <tr>
      <th style="width: 50%">Description</th>
      <th style="width: 15%; text-align: right">Qty</th>
      <th style="width: 15%; text-align: right">Unit Price</th>
      <th style="width: 20%; text-align: right">Amount</th>
    </tr>
  </thead>
  <tbody>
    {''.join(f'<tr><td>{line["description"]}</td><td style="text-align: right">{line["quantity"]}</td><td style="text-align: right">{inv["currency"]} {line["unit_price"]:,.2f}</td><td style="text-align: right">{inv["currency"]} {line["amount"]:,.2f}</td></tr>' for line in lines)}
  </tbody>
</table>

<div class="totals">
  <div class="totals-row">
    <div class="label">Subtotal:</div>
    <div class="amount">{inv['currency']} {subtotal:,.2f}</div>
  </div>
  {tax_line}
  <div class="total-amount">
    Total: {inv['currency']} {total:,.2f}
  </div>
</div>

{'<div class="note">' + inv.get('note', '') + '</div>' if inv.get('note') else ''}

</body>
</html>"""


def html_table_heavy(inv, lines, subtotal, tax, total):
    """Utility invoice with data table focus."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{inv['invoice_number']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: 'Courier New', monospace; margin: 0; padding: 20px; color: #222; background: #fff }}
.header {{ background: linear-gradient(90deg, #2c5aa0, #1a3d6d); color: white; padding: 20px; margin: -20px -20px 30px -20px }}
.header h1 {{ margin: 0; font-size: 24px }}
.header p {{ margin: 4px 0; font-size: 11px; opacity: 0.9 }}
.invoice-details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; font-size: 12px }}
.detail-block {{ border: 1px solid #ddd; padding: 12px }}
.detail-block strong {{ display: block; color: #2c5aa0; margin-bottom: 6px }}
table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 12px }}
table th {{ background: #e8e8e8; padding: 10px; text-align: left; border-bottom: 2px solid #2c5aa0; font-weight: bold }}
table td {{ padding: 10px; border-bottom: 1px solid #f0f0f0 }}
table tr:hover {{ background: #fafafa }}
.amount-column {{ text-align: right; font-weight: bold }}
.summary {{ margin: 30px 0; padding: 20px; background: #f8f8f8; border-top: 2px solid #2c5aa0; border-bottom: 2px solid #2c5aa0 }}
.summary-line {{ display: flex; justify-content: space-between; margin: 8px 0; font-size: 13px }}
.summary-line.total {{ font-weight: bold; font-size: 16px; color: #2c5aa0; border-top: 1px solid #ddd; padding-top: 8px }}
</style>
</head>
<body>
<div class="header">
  <h1>{inv['vendor_name']}</h1>
  <p>{inv['vendor_address']}</p>
</div>

<div class="invoice-details">
  <div class="detail-block">
    <strong>Invoice Details:</strong>
    Invoice #: {inv['invoice_number']}<br/>
    Date: {inv['invoice_date']}<br/>
    Due: {inv['due_date']}<br/>
    Currency: {inv['currency']}
  </div>
  <div class="detail-block">
    <strong>Bill To:</strong>
    {inv['bill_to_name']}<br/>
    {inv['bill_to_address']}
  </div>
</div>

<table>
  <thead>
    <tr>
      <th style="width: 50%">Service / Description</th>
      <th style="width: 15%; text-align: right">Qty / Units</th>
      <th style="width: 15%; text-align: right">Rate</th>
      <th style="width: 20%; text-align: right">Total</th>
    </tr>
  </thead>
  <tbody>
    {''.join(f'<tr><td>{line["description"]}</td><td style="text-align: right">{line["quantity"]}</td><td style="text-align: right">{inv["currency"]} {line["unit_price"]:,.2f}</td><td class="amount-column">{inv["currency"]} {line["amount"]:,.2f}</td></tr>' for line in lines)}
  </tbody>
</table>

<div class="summary">
  <div class="summary-line">
    <span>Subtotal:</span>
    <span>{inv['currency']} {subtotal:,.2f}</span>
  </div>
  {'<div class="summary-line"><span>' + inv.get("tax_label", "Tax") + ':</span><span>' + inv["currency"] + ' ' + f'{tax:,.2f}' + '</span></div>' if tax > 0 else ''}
  <div class="summary-line total">
    <span>TOTAL AMOUNT DUE:</span>
    <span>{inv['currency']} {total:,.2f}</span>
  </div>
</div>

{'<p style="margin-top: 20px; font-size: 11px; line-height: 1.5"><strong>Notes:</strong> ' + inv.get('note', '') + '</p>' if inv.get('note') else ''}

</body>
</html>"""


def html_insurance(inv, lines, subtotal, tax, total):
    """Insurance policy invoice with premium breakdown."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{inv['invoice_number']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: Georgia, serif; margin: 0; padding: 20px; color: #1a1a1a }}
.masthead {{ text-align: center; border-bottom: 3px solid #8b0000; padding-bottom: 15px; margin-bottom: 25px }}
.masthead h1 {{ margin: 0; color: #8b0000; font-size: 26px; letter-spacing: 1px }}
.masthead p {{ margin: 4px 0; font-size: 12px; color: #555 }}
.policy-ref {{ display: flex; justify-content: space-between; margin: 20px 0; font-size: 12px; background: #f5f5f5; padding: 12px }}
.policy-ref-item {{ flex: 1 }}
.policy-ref-item strong {{ display: block; color: #8b0000; font-size: 11px; text-transform: uppercase }}
.bill-to {{ margin: 25px 0; font-size: 12px }}
.bill-to h3 {{ color: #8b0000; margin: 0 0 8px 0; font-size: 12px; text-transform: uppercase }}
.bill-to p {{ margin: 2px 0; line-height: 1.5 }}
table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 12px }}
table th {{ background: #8b0000; color: white; padding: 10px 8px; text-align: left; font-weight: bold }}
table td {{ padding: 10px 8px; border-bottom: 1px solid #ddd }}
.description {{ width: 55% }}
.amount {{ width: 20%; text-align: right }}
.premium-row {{ background: #f9f9f9 }}
.subtotal-row {{ border-top: 2px solid #8b0000; font-weight: bold; background: #fff }}
.tax-row {{ background: #fff; border-bottom: 2px solid #8b0000 }}
.total-row {{ font-weight: bold; font-size: 14px; background: #8b0000; color: white }}
.footer-note {{ margin-top: 20px; font-size: 10px; color: #666; line-height: 1.6 }}
</style>
</head>
<body>
<div class="masthead">
  <h1>INSURANCE PREMIUM STATEMENT</h1>
  <p>{inv['vendor_name']}</p>
  <p>{inv['vendor_address']}</p>
</div>

<div class="policy-ref">
  <div class="policy-ref-item">
    <strong>Statement #</strong>
    {inv['invoice_number']}
  </div>
  <div class="policy-ref-item">
    <strong>Statement Date</strong>
    {inv['invoice_date']}
  </div>
  <div class="policy-ref-item">
    <strong>Due Date</strong>
    {inv['due_date']}
  </div>
  <div class="policy-ref-item">
    <strong>Currency</strong>
    {inv['currency']}
  </div>
</div>

<div class="bill-to">
  <h3>Policyholder / Bill To</h3>
  <p><strong>{inv['bill_to_name']}</strong></p>
  <p>{inv['bill_to_address']}</p>
</div>

<table>
  <thead>
    <tr>
      <th class="description">Coverage / Item</th>
      <th class="amount">Amount ({inv['currency']})</th>
    </tr>
  </thead>
  <tbody>
    {''.join(f'<tr class="premium-row"><td>{line["description"]}</td><td class="amount">{line["unit_price"]:,.2f}</td></tr>' for line in lines)}
    <tr class="subtotal-row">
      <td>Total Premium:</td>
      <td class="amount">{subtotal:,.2f}</td>
    </tr>
    {'<tr class="tax-row"><td>' + inv.get("tax_label", "Tax") + ':</td><td class="amount">' + f'{tax:,.2f}' + '</td></tr>' if tax > 0 else ''}
    <tr class="total-row">
      <td><strong>TOTAL AMOUNT DUE</strong></td>
      <td class="amount"><strong>{total:,.2f}</strong></td>
    </tr>
  </tbody>
</table>

<div class="footer-note">
  <strong>Payment Terms:</strong> Net due by {inv['due_date']}<br/>
  {'<strong>Notes:</strong> ' + inv.get('note', '') if inv.get('note') else ''}
</div>

</body>
</html>"""


def html_government(inv, lines, subtotal, tax, total):
    """Government tax notice layout (bilingual)."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{inv['invoice_number']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #000 }}
.official-header {{ background: #003d82; color: white; padding: 20px; text-align: center; margin: -20px -20px 20px -20px }}
.official-header h1 {{ margin: 0; font-size: 20px; letter-spacing: 1px }}
.official-header p {{ margin: 4px 0; font-size: 11px }}
.notice-type {{ font-weight: bold; text-transform: uppercase; color: #8b0000; font-size: 14px; margin: 15px 0 }}
.bilingual {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; font-size: 11px }}
.lang-col h3 {{ margin: 0 0 8px 0; color: #003d82; font-size: 12px }}
.lang-col p {{ margin: 4px 0; line-height: 1.4 }}
.info-box {{ background: #f0f0f0; padding: 15px; margin: 15px 0; border-left: 4px solid #003d82 }}
.info-box-label {{ font-weight: bold; color: #003d82; font-size: 11px; text-transform: uppercase }}
.info-box-value {{ font-size: 13px; margin-top: 4px }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 12px }}
table th {{ background: #e8e8e8; padding: 10px; border: 1px solid #999; text-align: left; font-weight: bold }}
table td {{ padding: 10px; border: 1px solid #ddd; }}
.description {{ width: 60% }}
.amount {{ width: 40%; text-align: right; font-weight: bold }}
.total-section {{ background: #003d82; color: white; padding: 15px; text-align: right; margin-top: 20px }}
.total-label {{ font-size: 12px; text-transform: uppercase }}
.total-amount {{ font-size: 20px; font-weight: bold; margin-top: 5px }}
</style>
</head>
<body>
<div class="official-header">
  <h1>{inv['vendor_name']}</h1>
  <p>{inv['vendor_address']}</p>
</div>

<div class="notice-type">AVIS D'IMPOSITION / TAX ASSESSMENT NOTICE</div>

<div class="bilingual">
  <div class="lang-col">
    <h3>Français</h3>
    <p><strong>Réference:</strong> {inv['invoice_number']}</p>
    <p><strong>Date d'émission:</strong> {inv['invoice_date']}</p>
    <p><strong>Date d'échéance:</strong> {inv['due_date']}</p>
    <p><strong>Propriété imposée:</strong> {inv['bill_to_name']}</p>
  </div>
  <div class="lang-col">
    <h3>English</h3>
    <p><strong>Reference:</strong> {inv['invoice_number']}</p>
    <p><strong>Issue Date:</strong> {inv['invoice_date']}</p>
    <p><strong>Due Date:</strong> {inv['due_date']}</p>
    <p><strong>Subject Property:</strong> {inv['bill_to_name']}</p>
  </div>
</div>

<div class="info-box">
  <div class="info-box-label">Adresse / Address</div>
  <div class="info-box-value">{inv['bill_to_address']}</div>
</div>

<table>
  <thead>
    <tr>
      <th class="description">Libellé de l'imposition / Assessment Item</th>
      <th class="amount">Montant / Amount ({inv['currency']})</th>
    </tr>
  </thead>
  <tbody>
    {''.join(f'<tr><td>{line["description"]}</td><td class="amount">{line["unit_price"]:,.2f}</td></tr>' for line in lines)}
  </tbody>
</table>

<div class="total-section">
  <div class="total-label">Montant total dû / Total Amount Due</div>
  <div class="total-amount">{total:,.2f} {inv['currency']}</div>
</div>

{'<p style="margin-top: 20px; font-size: 10px; line-height: 1.5"><strong>Remarques / Notes:</strong> ' + inv.get('note', '') + '</p>' if inv.get('note') else ''}

</body>
</html>"""


def html_minimalist(inv, lines, subtotal, tax, total):
    """Minimalist, clean design."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{inv['invoice_number']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; color: #333 }}
.header {{ margin-bottom: 40px }}
.header-row {{ display: flex; justify-content: space-between; align-items: flex-start }}
.company {{ font-size: 14px }}
.company h1 {{ margin: 0 0 6px 0; font-size: 18px; font-weight: 600 }}
.company p {{ margin: 2px 0; font-size: 11px; color: #666 }}
.invoice-ref {{ text-align: right; font-size: 12px }}
.invoice-ref-line {{ margin: 4px 0 }}
.bill-to-section {{ margin: 30px 0 }}
.bill-to-section h3 {{ margin: 0 0 6px 0; font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; letter-spacing: 1px }}
.bill-to-section p {{ margin: 2px 0; font-size: 12px }}
.bill-to-section strong {{ display: block; font-size: 12px; margin-bottom: 4px }}
table {{ width: 100%; border-collapse: collapse; margin: 30px 0 }}
table th {{ border-top: 1px solid #333; border-bottom: 1px solid #333; padding: 12px 0; text-align: left; font-weight: 600; font-size: 12px }}
table td {{ padding: 10px 0; border-bottom: 1px solid #f0f0f0; font-size: 12px }}
table tr:last-child td {{ border-bottom: 1px solid #333 }}
.amount {{ text-align: right }}
.totals {{ margin: 30px 0; text-align: right; font-size: 12px }}
.totals-item {{ display: flex; justify-content: flex-end; margin: 8px 0 }}
.totals-item-label {{ width: 200px; text-align: right; padding-right: 20px }}
.totals-item-value {{ width: 80px; text-align: right; font-weight: 600 }}
.total-final {{ margin-top: 15px; padding-top: 15px; border-top: 2px solid #333; display: flex; justify-content: flex-end }}
.total-final-label {{ width: 200px; text-align: right; padding-right: 20px; font-weight: 600 }}
.total-final-value {{ width: 80px; text-align: right; font-weight: 600; font-size: 14px }}
</style>
</head>
<body>

<div class="header">
  <div class="header-row">
    <div class="company">
      <h1>{inv['vendor_name']}</h1>
      <p>{inv['vendor_address']}</p>
      <p>Tax ID: {inv['vendor_tax_id']}</p>
    </div>
    <div class="invoice-ref">
      <div class="invoice-ref-line"><strong>{inv['invoice_number']}</strong></div>
      <div class="invoice-ref-line">{inv['invoice_date']}</div>
      <div class="invoice-ref-line">Due: {inv['due_date']}</div>
    </div>
  </div>
</div>

<div class="bill-to-section">
  <h3>Bill To</h3>
  <strong>{inv['bill_to_name']}</strong>
  <p>{inv['bill_to_address']}</p>
</div>

<table>
  <thead>
    <tr>
      <th style="width: 50%">Description</th>
      <th style="width: 15%; text-align: right">Qty</th>
      <th style="width: 17%; text-align: right">Unit Price</th>
      <th style="width: 18%; text-align: right">Amount</th>
    </tr>
  </thead>
  <tbody>
    {''.join(f'<tr><td>{line["description"]}</td><td class="amount">{line["quantity"]}</td><td class="amount">{inv["currency"]} {line["unit_price"]:,.2f}</td><td class="amount">{inv["currency"]} {line["amount"]:,.2f}</td></tr>' for line in lines)}
  </tbody>
</table>

<div class="totals">
  <div class="totals-item">
    <div class="totals-item-label">Subtotal</div>
    <div class="totals-item-value">{inv['currency']} {subtotal:,.2f}</div>
  </div>
  {'<div class="totals-item"><div class="totals-item-label">' + inv.get("tax_label", "Tax") + '</div><div class="totals-item-value">' + inv["currency"] + ' ' + f'{tax:,.2f}' + '</div></div>' if tax > 0 else ''}
  <div class="total-final">
    <div class="total-final-label">Total</div>
    <div class="total-final-value">{inv['currency']} {total:,.2f}</div>
  </div>
</div>

{'<p style="margin-top: 30px; font-size: 11px; color: #666; line-height: 1.5">' + inv.get('note', '') + '</p>' if inv.get('note') else ''}

</body>
</html>"""


def html_sidebar(inv, lines, subtotal, tax, total):
    """Layout with sidebar for company info."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{inv['invoice_number']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 0; color: #333 }}
.container {{ display: flex; min-height: 297mm }}
.sidebar {{ width: 30%; background: linear-gradient(135deg, #2a5a7a 0%, #1a3a5a 100%); color: white; padding: 20px; box-sizing: border-box }}
.sidebar-section {{ margin-bottom: 25px }}
.sidebar-section h3 {{ margin: 0 0 8px 0; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8 }}
.sidebar-section p {{ margin: 2px 0; font-size: 11px; line-height: 1.5 }}
.sidebar-section strong {{ display: block }}
.main {{ flex: 1; padding: 20px }}
.invoice-title {{ font-size: 16px; font-weight: bold; color: #1a3a5a; margin-bottom: 15px }}
.invoice-number {{ font-size: 13px; color: #666; margin-bottom: 5px }}
.bill-to {{ margin: 30px 0 }}
.bill-to h3 {{ margin: 0 0 8px 0; font-size: 11px; font-weight: bold; color: #1a3a5a; text-transform: uppercase }}
.bill-to p {{ margin: 2px 0; font-size: 12px }}
table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 11px }}
table th {{ background: #f0f0f0; padding: 8px; text-align: left; border-bottom: 2px solid #1a3a5a; font-weight: bold }}
table td {{ padding: 8px; border-bottom: 1px solid #ddd }}
.amount-col {{ text-align: right }}
.summary {{ margin: 20px 0; text-align: right; font-size: 12px }}
.summary-line {{ display: flex; justify-content: flex-end; margin: 4px 0 }}
.summary-line-label {{ width: 140px; text-align: right; padding-right: 15px }}
.summary-line-amount {{ width: 80px; text-align: right; font-weight: bold }}
.total-box {{ background: #1a3a5a; color: white; padding: 12px; border-radius: 3px; margin-top: 10px; display: flex; justify-content: space-between }}
.total-box-label {{ font-weight: bold }}
.total-box-amount {{ font-size: 14px; font-weight: bold }}
</style>
</head>
<body>
<div class="container">
  <div class="sidebar">
    <div class="sidebar-section">
      <h3>From</h3>
      <strong>{inv['vendor_name']}</strong>
      <p>{inv['vendor_address']}</p>
      <p>Tax ID: {inv['vendor_tax_id']}</p>
    </div>
    <div class="sidebar-section">
      <h3>Invoice #</h3>
      <p><strong>{inv['invoice_number']}</strong></p>
    </div>
    <div class="sidebar-section">
      <h3>Date</h3>
      <p>{inv['invoice_date']}</p>
    </div>
    <div class="sidebar-section">
      <h3>Due Date</h3>
      <p>{inv['due_date']}</p>
    </div>
    <div class="sidebar-section">
      <h3>Currency</h3>
      <p>{inv['currency']}</p>
    </div>
  </div>

  <div class="main">
    <div class="invoice-title">INVOICE</div>
    <div class="invoice-number">{inv['invoice_number']}</div>

    <div class="bill-to">
      <h3>Bill To</h3>
      <strong>{inv['bill_to_name']}</strong>
      <p>{inv['bill_to_address']}</p>
    </div>

    <table>
      <thead>
        <tr>
          <th style="width: 50%">Description</th>
          <th style="width: 15%; text-align: right">Qty</th>
          <th style="width: 17%; text-align: right">Rate</th>
          <th style="width: 18%; text-align: right">Total</th>
        </tr>
      </thead>
      <tbody>
        {''.join(f'<tr><td>{line["description"]}</td><td class="amount-col">{line["quantity"]}</td><td class="amount-col">{inv["currency"]} {line["unit_price"]:,.2f}</td><td class="amount-col">{inv["currency"]} {line["amount"]:,.2f}</td></tr>' for line in lines)}
      </tbody>
    </table>

    <div class="summary">
      <div class="summary-line">
        <div class="summary-line-label">Subtotal:</div>
        <div class="summary-line-amount">{inv['currency']} {subtotal:,.2f}</div>
      </div>
      {'<div class="summary-line"><div class="summary-line-label">' + inv.get("tax_label", "Tax") + ':</div><div class="summary-line-amount">' + inv["currency"] + ' ' + f'{tax:,.2f}' + '</div></div>' if tax > 0 else ''}
      <div class="total-box">
        <div class="total-box-label">TOTAL DUE</div>
        <div class="total-box-amount">{inv['currency']} {total:,.2f}</div>
      </div>
    </div>

    {'<p style="margin-top: 15px; font-size: 10px; color: #666; line-height: 1.4">' + inv.get('note', '') + '</p>' if inv.get('note') else ''}
  </div>
</div>
</body>
</html>"""


def html_twocolumn(inv, lines, subtotal, tax, total):
    """Two-column header layout."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{inv['invoice_number']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: Verdana, sans-serif; margin: 0; padding: 20px; color: #333 }}
.header {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px; border-bottom: 3px double #2a5a7a; padding-bottom: 20px }}
.header-left h1 {{ margin: 0 0 6px 0; font-size: 22px; color: #2a5a7a }}
.header-left p {{ margin: 2px 0; font-size: 11px; color: #666 }}
.header-right {{ text-align: right; font-size: 12px }}
.header-right .label {{ font-weight: bold; color: #2a5a7a; display: block; margin-top: 8px }}
.bill-to {{ margin: 25px 0; padding: 12px; background: #f9f9f9; border-left: 4px solid #2a5a7a; font-size: 12px }}
.bill-to h3 {{ margin: 0 0 6px 0; font-size: 11px; font-weight: bold; text-transform: uppercase; color: #2a5a7a }}
.bill-to p {{ margin: 2px 0 }}
table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 12px }}
table th {{ background: #2a5a7a; color: white; padding: 10px; text-align: left; font-weight: bold }}
table td {{ padding: 9px; border-bottom: 1px solid #ddd }}
table tr:nth-child(even) {{ background: #f9f9f9 }}
.amount {{ text-align: right }}
.summary {{ margin: 25px 0; display: grid; grid-template-columns: 1fr 200px; gap: 20px }}
.summary-text {{ font-size: 12px }}
.summary-numbers {{ text-align: right; font-size: 12px }}
.summary-numbers-line {{ display: flex; justify-content: space-between; margin: 6px 0; padding: 4px 0 }}
.summary-numbers-label {{ }}
.summary-numbers-value {{ font-weight: bold; width: 80px; text-align: right }}
.total-line {{ border-top: 2px solid #2a5a7a; border-bottom: 2px solid #2a5a7a; padding: 8px 0; font-size: 13px }}
.total-line .summary-numbers-value {{ font-weight: bold; font-size: 14px }}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <h1>{inv['vendor_name']}</h1>
    <p>{inv['vendor_address']}</p>
    <p>Tax ID: {inv['vendor_tax_id']}</p>
  </div>
  <div class="header-right">
    <div><span class="label">Invoice #</span>{inv['invoice_number']}</div>
    <div><span class="label">Date</span>{inv['invoice_date']}</div>
    <div><span class="label">Due</span>{inv['due_date']}</div>
    <div><span class="label">Currency</span>{inv['currency']}</div>
  </div>
</div>

<div class="bill-to">
  <h3>Bill To</h3>
  <strong>{inv['bill_to_name']}</strong>
  <p>{inv['bill_to_address']}</p>
</div>

<table>
  <thead>
    <tr>
      <th style="width: 50%">Description</th>
      <th style="width: 15%; text-align: right">Qty</th>
      <th style="width: 17%; text-align: right">Unit Price</th>
      <th style="width: 18%; text-align: right">Amount</th>
    </tr>
  </thead>
  <tbody>
    {''.join(f'<tr><td>{line["description"]}</td><td class="amount">{line["quantity"]}</td><td class="amount">{inv["currency"]} {line["unit_price"]:,.2f}</td><td class="amount">{inv["currency"]} {line["amount"]:,.2f}</td></tr>' for line in lines)}
  </tbody>
</table>

<div class="summary">
  <div class="summary-text"></div>
  <div class="summary-numbers">
    <div class="summary-numbers-line">
      <span class="summary-numbers-label">Subtotal:</span>
      <span class="summary-numbers-value">{inv['currency']} {subtotal:,.2f}</span>
    </div>
    {'<div class="summary-numbers-line"><span class="summary-numbers-label">' + inv.get("tax_label", "Tax") + ':</span><span class="summary-numbers-value">' + inv["currency"] + ' ' + f'{tax:,.2f}' + '</span></div>' if tax > 0 else ''}
    <div class="summary-numbers-line total-line">
      <span class="summary-numbers-label">TOTAL:</span>
      <span class="summary-numbers-value">{inv['currency']} {total:,.2f}</span>
    </div>
  </div>
</div>

{'<p style="margin-top: 20px; font-size: 11px; color: #666; line-height: 1.5">' + inv.get('note', '') + '</p>' if inv.get('note') else ''}

</body>
</html>"""


def html_timesheet(inv, lines, subtotal, tax, total):
    """Legal/timesheet invoice layout."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{inv['invoice_number']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: 'Times New Roman', serif; margin: 0; padding: 20px; color: #1a1a1a }}
.letterhead {{ margin-bottom: 30px; padding-bottom: 15px; border-bottom: 2px solid #333 }}
.letterhead h1 {{ margin: 0; font-size: 18px; color: #333 }}
.letterhead p {{ margin: 4px 0; font-size: 11px; color: #555 }}
.invoice-header {{ display: flex; justify-content: space-between; margin: 30px 0; font-size: 12px }}
.invoice-header-item {{ }}
.invoice-header-label {{ font-weight: bold; color: #333; font-size: 11px }}
.bill-to {{ margin: 25px 0; font-size: 12px }}
.bill-to-label {{ font-weight: bold; color: #333; font-size: 11px; text-transform: uppercase }}
.bill-to-content {{ margin-top: 6px }}
table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 11px }}
table th {{ background: #e8e8e8; padding: 10px 6px; text-align: left; border: 1px solid #999; font-weight: bold }}
table td {{ padding: 8px 6px; border: 1px solid #ccc }}
table tr:nth-child(odd) {{ background: #fafafa }}
.desc {{ width: 40% }}
.date-col {{ width: 12%; text-align: center }}
.hours-col {{ width: 10%; text-align: right }}
.rate-col {{ width: 15%; text-align: right }}
.amount-col {{ width: 18%; text-align: right; font-weight: bold }}
.summary-line {{ display: flex; justify-content: flex-end; margin: 8px 0; font-size: 12px }}
.summary-line-label {{ width: 120px; text-align: right; padding-right: 15px }}
.summary-line-amount {{ width: 80px; text-align: right; font-weight: bold }}
.total-final {{ background: #333; color: white; padding: 10px; text-align: right; font-size: 13px; font-weight: bold; margin-top: 15px }}
.note-box {{ margin-top: 20px; padding: 12px; background: #f5f5f5; border-left: 3px solid #333; font-size: 11px; line-height: 1.5 }}
</style>
</head>
<body>

<div class="letterhead">
  <h1>{inv['vendor_name']}</h1>
  <p>{inv['vendor_address']}</p>
</div>

<div class="invoice-header">
  <div class="invoice-header-item">
    <div class="invoice-header-label">Invoice #</div>
    <div>{inv['invoice_number']}</div>
  </div>
  <div class="invoice-header-item">
    <div class="invoice-header-label">Invoice Date</div>
    <div>{inv['invoice_date']}</div>
  </div>
  <div class="invoice-header-item">
    <div class="invoice-header-label">Due Date</div>
    <div>{inv['due_date']}</div>
  </div>
</div>

<div class="bill-to">
  <div class="bill-to-label">Billed To:</div>
  <div class="bill-to-content">
    <strong>{inv['bill_to_name']}</strong><br/>
    {inv['bill_to_address']}
  </div>
</div>

<table>
  <thead>
    <tr>
      <th class="desc">Description of Services</th>
      <th class="date-col">Date</th>
      <th class="hours-col">Hours</th>
      <th class="rate-col">Rate</th>
      <th class="amount-col">Amount</th>
    </tr>
  </thead>
  <tbody>
    {''.join(f'<tr><td class="desc">{line["description"]}</td><td class="date-col">-</td><td class="hours-col">{line["quantity"]}</td><td class="rate-col">{inv["currency"]} {line["unit_price"]:,.2f}</td><td class="amount-col">{inv["currency"]} {line["amount"]:,.2f}</td></tr>' for line in lines)}
  </tbody>
</table>

<div class="summary-line">
  <span class="summary-line-label">Subtotal:</span>
  <span class="summary-line-amount">{inv['currency']} {subtotal:,.2f}</span>
</div>

{'<div class="summary-line"><span class="summary-line-label">' + inv.get("tax_label", "Tax") + ':</span><span class="summary-line-amount">' + inv["currency"] + ' ' + f'{tax:,.2f}' + '</span></div>' if tax > 0 else ''}

<div class="total-final">
  TOTAL DUE: {inv['currency']} {total:,.2f}
</div>

{'<div class="note-box"><strong>Re:</strong> ' + inv.get('note', '') + '</div>' if inv.get('note') else ''}

</body>
</html>"""


def generate_policy_html(policy):
    """Generate HTML for policy document."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{policy['title']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; line-height: 1.6 }}
.header {{ background: #003d82; color: white; padding: 20px; margin: -20px -20px 20px -20px }}
.header h1 {{ margin: 0; font-size: 24px }}
.header p {{ margin: 4px 0; font-size: 12px; opacity: 0.9 }}
.doc-info {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; margin: 20px 0; font-size: 11px }}
.info-box {{ background: #f0f0f0; padding: 10px; border-left: 3px solid #003d82 }}
.info-box strong {{ display: block; color: #003d82; margin-bottom: 4px }}
h2 {{ color: #003d82; font-size: 14px; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #ddd; padding-bottom: 5px }}
h3 {{ color: #003d82; font-size: 12px; margin-top: 15px; margin-bottom: 8px }}
p {{ font-size: 12px; margin: 8px 0 }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 11px }}
table th {{ background: #e8e8e8; padding: 8px; text-align: left; border: 1px solid #ccc; font-weight: bold }}
table td {{ padding: 8px; border: 1px solid #ddd }}
.highlight {{ background: #ffffcc; padding: 2px 4px }}
ul {{ margin: 8px 0; padding-left: 20px }}
ul li {{ margin: 4px 0; font-size: 12px }}
.page-break {{ page-break-after: always }}
</style>
</head>
<body>
<div class="header">
  <h1>{policy['title']}</h1>
  <p>Revantage Europe – Group Policy</p>
</div>

<div class="doc-info">
  <div class="info-box">
    <strong>Policy Owner</strong>
    {policy['approved_by']}
  </div>
  <div class="info-box">
    <strong>Version</strong>
    {policy['version']}
  </div>
  <div class="info-box">
    <strong>Effective Date</strong>
    {policy['effective_date']}
  </div>
  <div class="info-box">
    <strong>Last Updated</strong>
    {datetime.now().strftime('%Y-%m-%d')}
  </div>
</div>

<div style="white-space: pre-wrap; font-size: 12px; line-height: 1.5">
{policy['content']}
</div>

</body>
</html>"""


def generate_lease_html(lease):
    """Generate HTML for lease agreement."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{lease['title']}</title>
<style>
@page {{ size: A4; margin: 14mm }}
body {{ font-family: 'Times New Roman', serif; margin: 0; padding: 20px; color: #333; line-height: 1.5 }}
.header {{ text-align: center; margin-bottom: 30px }}
.expired-stamp {{ color: red; font-weight: bold; font-size: 14px; text-transform: uppercase; margin-bottom: 10px }}
.header h1 {{ margin: 0; font-size: 18px; font-weight: bold }}
.header p {{ margin: 4px 0; font-size: 12px }}
.party-section {{ margin: 20px 0; font-size: 12px }}
.party-section h3 {{ margin: 0 0 8px 0; font-weight: bold; font-size: 12px }}
.party-section p {{ margin: 2px 0 }}
.terms {{ margin: 20px 0; font-size: 12px }}
.terms-row {{ display: flex; margin: 8px 0 }}
.terms-label {{ width: 150px; font-weight: bold }}
.terms-value {{ flex: 1 }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 11px }}
table th {{ background: #e8e8e8; padding: 8px; text-align: left; border: 1px solid #ccc; font-weight: bold }}
table td {{ padding: 8px; border: 1px solid #ddd }}
.signature-block {{ margin-top: 30px; font-size: 11px }}
.signature-line {{ margin-top: 20px; display: flex; justify-content: space-between }}
.sig {{ width: 45%; }}
.sig-line {{ border-top: 1px solid #000; margin-top: 8px; text-align: center; font-size: 10px }}
</style>
</head>
<body>

<div class="header">
  {'<div class="expired-stamp">EXPIRED</div>' if lease.get('expired') else ''}
  <h1>{lease['title']}</h1>
  <p>LEASE AGREEMENT</p>
</div>

<div class="party-section">
  <h3>LANDLORD / LESSOR:</h3>
  <p><strong>{lease['landlord_name']}</strong></p>
  <p>{lease['landlord_address']}</p>
</div>

<div class="party-section">
  <h3>TENANT / LESSEE:</h3>
  <p><strong>{lease['tenant_name']}</strong></p>
  <p>{lease['tenant_address']}</p>
</div>

<div class="terms">
  <div class="terms-row">
    <div class="terms-label"><strong>Property:</strong></div>
    <div class="terms-value">{lease['property']}</div>
  </div>
  <div class="terms-row">
    <div class="terms-label"><strong>Lease Commencement:</strong></div>
    <div class="terms-value">{lease['commencement_date']}</div>
  </div>
  <div class="terms-row">
    <div class="terms-label"><strong>Lease Expiration:</strong></div>
    <div class="terms-value">{lease['expiration_date']}</div>
  </div>
  <div class="terms-row">
    <div class="terms-label"><strong>Term Length:</strong></div>
    <div class="terms-value">{lease['term_length']}</div>
  </div>
  <div class="terms-row">
    <div class="terms-label"><strong>Monthly Rent:</strong></div>
    <div class="terms-value">{lease['monthly_rent']}</div>
  </div>
  <div class="terms-row">
    <div class="terms-label"><strong>Rent Currency:</strong></div>
    <div class="terms-value">{lease['currency']}</div>
  </div>
</div>

<h3 style="margin-top: 25px">1. LEASE TERM</h3>
<p>The Landlord hereby leases to the Tenant, and the Tenant hereby leases from the Landlord, the property described above for a term of {lease['term_length']}, commencing on {lease['commencement_date']} and expiring at 11:59 p.m. on {lease['expiration_date']}, unless sooner terminated as provided herein.</p>

<h3>2. RENT</h3>
<p>The Tenant agrees to pay the Landlord the monthly rent of {lease['currency']} {lease['monthly_rent_numeric']:,.2f}, payable on the 1st day of each month in advance, without demand. Rent for any partial month shall be prorated daily at the rate of {lease['monthly_rent_numeric'] / 30:,.2f} per day.</p>

<h3>3. PAYMENT TERMS</h3>
<p>All rent payments shall be made to: {lease['payment_address']}</p>

<h3>4. USE OF PREMISES</h3>
<p>The Tenant agrees to use the premises only for {lease['permitted_use']}. No other use is permitted without prior written consent from the Landlord.</p>

<h3>5. MAINTENANCE</h3>
<p>The Tenant shall maintain the premises in good condition and shall be responsible for routine repairs and maintenance. The Landlord remains responsible for structural repairs and major systems.</p>

<div class="signature-block">
  <div class="signature-line">
    <div class="sig">
      <strong>Landlord / Authorized Representative</strong>
      <div class="sig-line"></div>
      <div style="font-size: 10px; margin-top: 4px">Date: _______________</div>
    </div>
    <div class="sig">
      <strong>Tenant / Authorized Representative</strong>
      <div class="sig-line"></div>
      <div style="font-size: 10px; margin-top: 4px">Date: _______________</div>
    </div>
  </div>
</div>

</body>
</html>"""


def html_to_pdf(html_path, pdf_path):
    """Convert HTML to PDF using Chrome headless."""
    try:
        cmd = [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            f"file://{html_path}",
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error converting {html_path} to PDF: {e}")
        return False


def pdf_to_png(pdf_path, png_path):
    """Convert PDF page 1 to PNG."""
    try:
        cmd = [
            "pdftoppm",
            "-png",
            "-r", "60",
            "-f", "1",
            "-l", "1",
            pdf_path,
            png_path.replace(".png", ""),  # pdftoppm adds suffix
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error converting {pdf_path} to PNG: {e}")
        return False


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF for verification."""
    try:
        cmd = ["pdftotext", pdf_path, "-"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def generate_invoices():
    """Generate all invoices."""
    ground_truth = []

    for inv in INVOICES:
        # Generate HTML
        html_content = generate_invoice_html(inv)
        html_path = BUILD_HTML_DIR / f"{inv['invoice_number']}.html"
        with open(html_path, "w") as f:
            f.write(html_content)

        # Convert to PDF
        pdf_path = OUT_INVOICES / f"{inv['invoice_number']}.pdf"
        if html_to_pdf(str(html_path), str(pdf_path)):
            print(f"✓ Invoice {inv['invoice_number']} generated")
        else:
            print(f"✗ Failed to generate {inv['invoice_number']}")

        # Generate preview PNG
        png_path = BUILD_PREVIEW_DIR / f"{inv['invoice_number']}.png"
        if pdf_to_png(str(pdf_path), str(png_path)):
            print(f"  Preview PNG created")

        # Add to ground truth
        gt_entry = {
            "file": f"{inv['invoice_number']}.pdf",
            "vendor_name": inv["vendor_name"],
            "invoice_number": inv["invoice_number"],
            "invoice_date": inv["invoice_date"],
            "due_date": inv["due_date"],
            "line_items": [
                {
                    "description": line["description"],
                    "quantity": line["quantity"],
                    "unit_price": line["unit_price"],
                    "amount": line["amount"],
                }
                for line in inv["_lines"]
            ],
            "subtotal": inv["_subtotal"],
            "tax": inv["_tax"],
            "total": inv["_total"],
            "currency": inv["currency"],
        }
        ground_truth.append(gt_entry)

    # Write ground truth JSON
    gt_path = OUT_DIR / "invoices_ground_truth.json"
    with open(gt_path, "w") as f:
        json.dump(ground_truth, f, indent=2)
    print(f"✓ Ground truth JSON written to {gt_path}")

    return ground_truth


def generate_policies():
    """Generate all policies."""
    for policy in POLICIES:
        html_content = generate_policy_html(policy)
        html_filename = policy["filename"].replace(".pdf", ".html")
        html_path = BUILD_HTML_DIR / html_filename
        with open(html_path, "w") as f:
            f.write(html_content)

        pdf_path = OUT_POLICIES / policy["filename"]
        if html_to_pdf(str(html_path), str(pdf_path)):
            print(f"✓ Policy {policy['filename']} generated")
        else:
            print(f"✗ Failed to generate {policy['filename']}")

        # Generate preview PNG
        png_name = policy["filename"].replace(".pdf", ".png")
        png_path = BUILD_PREVIEW_DIR / png_name
        if pdf_to_png(str(pdf_path), str(png_path)):
            print(f"  Preview PNG created")


def generate_leases():
    """Generate all leases."""
    leases = [
        {
            "title": "LEASE AGREEMENT – HARBOR TOWER",
            "filename": "lease-harbor-tower-anchor.pdf",
            "landlord_name": "Harbor Tower Propco LLC",
            "landlord_address": "Miami Beach, FL",
            "tenant_name": "Meridian Health Partners",
            "tenant_address": "Miami, FL",
            "property": "Harbor Tower, Miami Beach – Suite 1500",
            "commencement_date": "April 1, 2021",
            "expiration_date": "March 31, 2026",
            "term_length": "5 years",
            "monthly_rent": "USD 118,000.00",
            "monthly_rent_numeric": 118000.00,
            "currency": "USD",
            "payment_address": "c/o Revantage, Miami Beach, FL",
            "permitted_use": "Healthcare services and medical office",
            "expired": True,
        },
        {
            "title": "LEASE AGREEMENT – KIRCHBERG PLAZA",
            "filename": "lease-kirchberg-plaza-suite-4.pdf",
            "landlord_name": "Kirchberg Plaza S.à r.l.",
            "landlord_address": "L-1919 Luxembourg",
            "tenant_name": "Nordlicht Asset Advisory S.A.",
            "tenant_address": "Luxembourg City, Luxembourg",
            "property": "Kirchberg Plaza, Luxembourg City – Suite 400",
            "commencement_date": "January 1, 2022",
            "expiration_date": "January 15, 2027",
            "term_length": "5 years",
            "monthly_rent": "EUR 46,500.00",
            "monthly_rent_numeric": 46500.00,
            "currency": "EUR",
            "payment_address": "c/o Revantage Europe, Luxembourg",
            "permitted_use": "Asset management and financial advisory",
            "expired": False,
        },
        {
            "title": "LEASE AGREEMENT – ZUIDAS RESIDENCES",
            "filename": "lease-zuidas-residences-commercial.pdf",
            "landlord_name": "Zuidas Residences B.V.",
            "landlord_address": "Amsterdam, Netherlands",
            "tenant_name": "Grachten Coffee B.V.",
            "tenant_address": "Amsterdam, Netherlands",
            "property": "Zuidas Residences, Amsterdam – Commercial Unit 01",
            "commencement_date": "July 1, 2023",
            "expiration_date": "December 31, 2026",
            "term_length": "3 years 6 months",
            "monthly_rent": "EUR 9,800.00",
            "monthly_rent_numeric": 9800.00,
            "currency": "EUR",
            "payment_address": "c/o Revantage Europe, Amsterdam",
            "permitted_use": "Retail café and food service",
            "expired": False,
        },
    ]

    for lease in leases:
        html_content = generate_lease_html(lease)
        html_filename = lease["filename"].replace(".pdf", ".html")
        html_path = BUILD_HTML_DIR / html_filename
        with open(html_path, "w") as f:
            f.write(html_content)

        pdf_path = OUT_LEASES / lease["filename"]
        if html_to_pdf(str(html_path), str(pdf_path)):
            print(f"✓ Lease {lease['filename']} generated")
        else:
            print(f"✗ Failed to generate {lease['filename']}")

        # Generate preview PNG
        png_name = lease["filename"].replace(".pdf", ".png")
        png_path = BUILD_PREVIEW_DIR / png_name
        if pdf_to_png(str(pdf_path), str(png_path)):
            print(f"  Preview PNG created")


def generate_policies_qa():
    """Generate QA ground truth for policies."""
    qa_content = """# Policies QA Ground Truth

## Questions and Answers

1. **What is the approval threshold for expenses over €50,000?**
   - **Answer:** Expenses over €50,000 require co-signature of the CFO and the Asset Management Director (two signatories, never the same person). Additional approval from the Investment Committee is required for expenses over €500,000.
   - **Source:** expense-approval-policy.pdf, Section 2.1 (Delegation Table)

2. **If a tenant's lease expires in 90 days, what steps should I take?**
   - **Answer:** At the 90-day mark, issue a formal written notice (registered letter) if the tenant has not responded to the earlier renewal proposal (sent at 120 days). Escalate to Head of Asset Management and begin re-letting marketing in parallel.
   - **Source:** lease-renewal-procedures.pdf, Section 1.3 (Day 90 Before Expiry: Follow-Up and Re-Letting)

3. **Is a new HVAC system for Harbor Tower classified as CapEx or OpEx?**
   - **Answer:** A replacement HVAC chiller (e.g., Harbor Tower) is classified as CapEx because it replaces the building system, costs exceed €25,000, and the useful life is 20 years (exceeds 3-year threshold). Depreciation is applied over 15–20 years per the HVAC depreciation schedule.
   - **Source:** capital-expenditure-guidelines.pdf, Section 1.3 (Worked Example: Harbor Tower Chiller)

4. **What is the intercompany shared-services recharge percentage billed quarterly by Revantage Europe to each property-owning Propco?**
   - **Answer:** Revantage Europe bills each Propco an intercompany shared-services recharge equal to 1.5% of gross rental revenue (and other property operating revenue) per quarter (account 8000). This excludes the third-party property management fee (3%, account 6000), which is a normal operating expense.
   - **Source:** intercompany-transfer-policy.pdf, Section 3.2 (Recharge Rate)

5. **What must be done if an intercompany charge variance exceeds €1,000 at quarter close?**
   - **Answer:** Discrepancies greater than €1,000 (absolute amount) must be investigated and resolved before quarter close. Finance reconciles the Propco's payment with the invoice and carries forward any prepayments or underpayments to the next quarter, with a year-end true-up adjustment in January.
   - **Source:** intercompany-transfer-policy.pdf, Section 7.2 (Variance Reconciliation)

6. **What credit rating threshold requires Head of Asset Management sign-off for lease renewal?**
   - **Answer:** Any tenant with a credit rating below BB requires written sign-off from the Head of Asset Management before lease renewal is approved. Tenants with >2 late payments in the preceding 24 months are flagged for alternative consideration (non-renewal, rent increase, additional security).
   - **Source:** lease-renewal-procedures.pdf, Section 2 (Credit Rating and Renewal)
"""
    qa_path = OUT_DIR / "policies_qa_ground_truth.md"
    with open(qa_path, "w") as f:
        f.write(qa_content)
    print(f"✓ Policies QA ground truth written to {qa_path}")


def main():
    """Main execution."""
    print("Generating synthetic business documents for Databricks workshop...\n")

    # Ensure output directories exist
    BUILD_HTML_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_INVOICES.mkdir(parents=True, exist_ok=True)
    OUT_POLICIES.mkdir(parents=True, exist_ok=True)
    OUT_LEASES.mkdir(parents=True, exist_ok=True)

    # Generate invoices
    print("Generating invoices...")
    ground_truth = generate_invoices()
    print(f"Generated {len(ground_truth)} invoices\n")

    # Generate policies
    print("Generating policies...")
    generate_policies()
    print(f"Generated {len(POLICIES)} policies\n")

    # Generate leases
    print("Generating leases...")
    generate_leases()
    print("Generated 3 leases\n")

    # Generate QA
    print("Generating policies QA...")
    generate_policies_qa()
    print()

    print("All documents generated successfully!")
    print(f"Output directory: {OUT_DIR}")


if __name__ == "__main__":
    main()
