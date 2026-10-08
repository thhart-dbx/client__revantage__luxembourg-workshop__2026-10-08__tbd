# Revantage Synthetic Business Documents

This directory contains a Python script that generates synthetic business documents (invoices, policies, and lease agreements) for the Revantage Luxembourg Databricks workshop. All PDFs are created with realistic layouts, amounts, and properties from the Revantage portfolio.

## Output Structure

```
out/
├── invoices/                      # 8 vendor invoices with distinct layouts
│   ├── HV-2026-0417.pdf          # Coastal Climate Systems (HVAC chiller replacement)
│   ├── PE-2026-06-0088.pdf       # Peachtree Energy Services (utility invoice)
│   ├── TM-POL-2026-3391.pdf      # Thames Mutual Property Insurance
│   ├── ACD-2026-IF-55120.pdf     # Municipal property tax (Luxembourg)
│   ├── NGD-26-1184.pdf           # Nettoyage Grand-Duché (cleaning services)
│   ├── VSB-2026-0612.pdf         # Vigilis Security Benelux
│   ├── ELV-2026-0331.pdf         # Elevatech Lifts (maintenance)
│   └── MK-2026-0278.pdf          # Moreau & Klein Avocats (legal services, timesheet)
├── invoices_ground_truth.json    # Exact invoice data (amounts, dates, line items)
├── policies/                      # 4 group policy documents
│   ├── expense-approval-policy.pdf
│   ├── capital-expenditure-guidelines.pdf
│   ├── lease-renewal-procedures.pdf
│   └── intercompany-transfer-policy.pdf
├── policies_qa_ground_truth.md   # Q&A verification for policy requirements
└── leases/                        # 3 lease agreements
    ├── lease-harbor-tower-anchor.pdf
    ├── lease-kirchberg-plaza-suite-4.pdf
    └── lease-zuidas-residences-commercial.pdf
```

## Invoice Details

| Invoice # | Vendor | Property | Amount | Currency | Tax | Notes |
|-----------|--------|----------|--------|----------|-----|-------|
| HV-2026-0417 | Coastal Climate Systems | Harbor Tower | 339,600.00 | USD | 0% | Chiller replacement (key invoice) |
| PE-2026-06-0088 | Peachtree Energy Services | Peachtree Center | 41,000.00 | USD | 0% | Utility services |
| TM-POL-2026-3391 | Thames Mutual | Portfolio (8 properties) | 49,350.00 | GBP | 12% | Insurance premium |
| ACD-2026-IF-55120 | Ville de Luxembourg | Kirchberg Plaza | 27,826.50 | EUR | 0% | Property tax (bilingual) |
| NGD-26-1184 | Nettoyage Grand-Duché | Kirchberg Plaza | 17,450.00 | EUR | 17% | Cleaning services |
| VSB-2026-0612 | Vigilis Security Benelux | Zuidas Residences | 25,440.00 | EUR | 21% | Security services |
| ELV-2026-0331 | Elevatech Lifts | Cloche d'Or | 11,580.00 | EUR | 17% | Lift maintenance |
| MK-2026-0278 | Moreau & Klein Avocats | Kirchberg Plaza | 10,070.00 | EUR | 17% | Legal services (9 time entries) |

## Layout Diversity

Each invoice uses a distinct vendor template:

1. **HV-2026-0417**: Traditional business invoice (left-aligned vendor, right-aligned metadata, navy table)
2. **PE-2026-06-0088**: Utility invoice with two-column header (grid-based details, monospace table)
3. **TM-POL-2026-3391**: Insurance premium statement (formal serif, maroon header, premium lines)
4. **ACD-2026-IF-55120**: Government tax notice (bilingual French/English, official seal style)
5. **NGD-26-1184**: Minimalist design (clean lines, right-aligned totals, no decorative borders)
6. **VSB-2026-0612**: Sidebar layout (left navy sidebar with company info, main content on right)
7. **ELV-2026-0331**: Two-column header (vendor left, metadata right, navy line separator)
8. **MK-2026-0278**: Legal/timesheet layout (letterhead style, date/hours/rate columns, black total bar)

## Policy Documents

- **expense-approval-policy.pdf**: Delegation-of-authority thresholds (€5k, €25k, €50k with co-signature, €500k with committee)
- **capital-expenditure-guidelines.pdf**: CapEx definition (replacement/improvement, >€25k, >3yr life); worked example with Harbor Tower chiller
- **lease-renewal-procedures.pdf**: 180/120/90/30-day renewal timeline; credit rating requirements (BB minimum)
- **intercompany-transfer-policy.pdf**: Property management fee (3%, account 6000), intercompany shared-services recharge (1.5%, account 8000), loan interest (account 8100)

## Ground Truth Files

### invoices_ground_truth.json
Contains exact amounts for all invoices: line items, quantities, unit prices, subtotals, taxes, and totals. Used for verification and data quality checks.

### policies_qa_ground_truth.md
Six Q&A pairs testing comprehension of key policy thresholds, with source citations (policy file + section number).

## How to Regenerate

### Prerequisites
- Python 3.7+ (stdlib only; no pip required)
- Google Chrome (macOS: `/Applications/Google Chrome.app/`)
- Poppler utilities: `pdftotext`, `pdftoppm`

```bash
# macOS
brew install poppler
```

### Steps

1. Navigate to the documents directory:
   ```bash
   cd code/documents
   ```

2. Run the generation script:
   ```bash
   python3 make_documents.py
   ```

3. Outputs are generated to:
   - PDFs: `out/{invoices,policies,leases}/`
   - Ground truth: `out/invoices_ground_truth.json` and `out/policies_qa_ground_truth.md`
   - Preview PNGs: `build/preview/` (page 1 of each PDF at 60 DPI)

### Customization

Edit `make_documents.py` to:
- Modify invoice amounts, dates, or vendor details in the `INVOICES` list
- Update policy content in the `POLICIES` list
- Change lease terms in the `generate_leases()` function
- Adjust CSS styling in the HTML generation functions

## Verification

All documents are verified:
- **PDF conversion**: Each HTML is converted with headless Chrome (`--headless=new`, no headers/footers)
- **Amount extraction**: `pdftotext` extracts all invoice amounts for spot checks
- **Preview images**: Page 1 of each PDF is rendered to PNG at 60 DPI for visual inspection
- **Ground truth**: Invoice arithmetic is validated (line items sum to subtotal, subtotal + tax = total)

## Currency and Properties

- **Currencies**: USD (Miami/Atlanta/New York), GBP (UK insurance), EUR (Luxembourg/Amsterdam, group standard)
- **Properties**: 8 Revantage portfolio assets (1 Biscayne Point, 2 Peachtree Center, 3 Harbor Tower, 4 Chelsea Lofts, 5 Back Bay Commons, 6 Kirchberg Plaza, 7 Cloche d'Or, 8 Zuidas Residences)
- **Bill-to entities**: Property-owning SPVs or Revantage Europe (e.g., "Harbor Tower Propco LLC c/o Revantage")

## Notes

- All vendor names, addresses, tax IDs, and IBANs are fictitious and invented for demonstration.
- Inline CSS only; no external fonts, images, or API calls.
- A4 page size with 14mm margins (`@page { size: A4; margin: 14mm }`).
- Lease agreement marked "EXPIRED" uses a red header stamp (lease-harbor-tower-anchor.pdf).
