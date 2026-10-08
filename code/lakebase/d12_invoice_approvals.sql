-- Demo 12: transactional approval state in Lakebase (database revantage_ops, schema approvals).
-- Over-threshold invoices (> EUR 50,000, Expense Approval Policy) need two different approvers.
CREATE SCHEMA IF NOT EXISTS approvals;

CREATE TABLE IF NOT EXISTS approvals.invoice_approvals (
  invoice_id      TEXT PRIMARY KEY,
  vendor_name     TEXT NOT NULL,
  property_name   TEXT,
  total_amount    NUMERIC(18,2) NOT NULL,
  currency        TEXT NOT NULL,
  total_eur       NUMERIC(18,2) NOT NULL,          -- converted at the ECB rate on the invoice date
  extracted_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  status          TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
  first_approver  TEXT,
  first_approved_at TIMESTAMPTZ,
  reviewed_by     TEXT,
  reviewed_at     TIMESTAMPTZ,
  notes           TEXT,
  requires_two_approvers BOOLEAN GENERATED ALWAYS AS (total_eur > 50000) STORED,
  CHECK (reviewed_by IS NULL OR first_approver IS NULL OR reviewed_by <> first_approver)
);

CREATE TABLE IF NOT EXISTS approvals.approval_events (
  event_id     BIGSERIAL PRIMARY KEY,
  invoice_id   TEXT NOT NULL REFERENCES approvals.invoice_approvals(invoice_id),
  action       TEXT NOT NULL CHECK (action IN ('first_approval', 'approve', 'reject', 'reset')),
  actor        TEXT NOT NULL,
  notes        TEXT,
  at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
