-- D4 reference: the SQL that Agent Bricks "Use Agent > Run in SQL" generates for the Invoice Extractor
-- (captured 2026-10-08), wrapped in a CTAS so the result is a governed Delta table.
-- Placeholders: ${catalog}, ${schema}. Runs on a SQL warehouse.
CREATE OR REPLACE TABLE ${catalog}.${schema}.ref_invoices_extracted
COMMENT 'Invoice fields extracted from documents/invoices by ai_parse_document + ai_extract (Demo 4 reference).'
AS
WITH parsed_documents AS (
  SELECT
    path,
    ai_parse_document(content, map('version', '2.0', 'descriptionElementTypes', '*')) AS parsed
  FROM read_files('/Volumes/${catalog}/${schema}/documents/invoices', format => 'binaryFile')
)
SELECT
  path,
  ai_extract(
    parsed,
    '{
      "vendor_name": {"type": "string", "description": "Name of the vendor issuing the invoice"},
      "invoice_number": {"type": "string", "description": "Unique identifier of the invoice"},
      "invoice_date": {"type": "string", "description": "Date the invoice was issued in YYYY-MM-DD format"},
      "due_date": {"type": "string", "description": "Payment due date in YYYY-MM-DD format"},
      "line_items": {
        "type": "array",
        "description": "List of line items on the invoice",
        "items": {
          "type": "object",
          "properties": {
            "description": {"type": "string", "description": "Description of the line item"},
            "quantity": {"type": "number", "description": "Quantity of the item (hours for time-based billing)"},
            "unit_price": {"type": "number", "description": "Unit price of the item without currency symbols"},
            "amount": {"type": "number", "description": "Total amount for the line item (quantity multiplied by unit price) without currency symbols"}
          }
        }
      },
      "subtotal": {"type": "number", "description": "Subtotal amount before tax, without currency symbols"},
      "tax": {"type": "number", "description": "Tax amount applied to the invoice, without currency symbols"},
      "total": {"type": "number", "description": "Total amount due on the invoice, without currency symbols"},
      "currency": {"type": "string", "description": "ISO currency code (e.g., EUR, USD, GBP) used for the amounts"}
    }',
    options => map('version', '2.0')
  ) AS response
FROM parsed_documents
WHERE parsed IS NOT NULL;
