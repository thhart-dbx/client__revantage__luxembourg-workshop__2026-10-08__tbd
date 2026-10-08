-- Demo 12 reset: 5 invoices back to Pending, audit trail cleared. Amounts match ref_invoices_extracted.
TRUNCATE approvals.approval_events;
DELETE FROM approvals.invoice_approvals;
INSERT INTO approvals.invoice_approvals (invoice_id, vendor_name, property_name, total_amount, currency, total_eur) VALUES
  ('HV-2026-0417',      'Coastal Climate Systems LLC',                     'Harbor Tower',      339600.00, 'USD', 312390.76),
  ('TM-POL-2026-3391',  'Thames Mutual Property Insurance plc',            'Western Europe portfolio', 55272.00, 'GBP', 64730.00),
  ('PE-2026-06-0088',   'Peachtree Energy Services',                       'Peachtree Center',   41000.00, 'USD', 37714.10),
  ('ACD-2026-IF-55120', 'Ville de Luxembourg – Service des Contributions', 'Kirchberg Plaza',    27826.50, 'EUR', 27826.50),
  ('NGD-26-1184',       'Nettoyage Grand-Duché S.à r.l.',                  'Kirchberg Plaza',    20416.50, 'EUR', 20416.50);
