import "server-only";
import { Pool } from "pg";

// Lakebase (Postgres) connection. On Databricks Apps the database resource injects PGHOST, PGPORT,
// PGDATABASE, PGUSER (the app service principal) and PGSSLMODE; the password is a workspace OAuth
// token for that service principal, refreshed before it expires. Locally, set the same PG* vars plus
// LAKEBASE_PASSWORD (from `databricks database generate-database-credential`).

export interface Invoice {
  invoice_id: string;
  vendor_name: string;
  property_name: string | null;
  total_amount: number;
  currency: string;
  total_eur: number;
  extracted_at: string;
  status: "Pending" | "Approved" | "Rejected";
  reviewed_by: string | null;
  reviewed_at: string | null;
  notes: string | null;
  first_approver_email: string | null;
  first_approved_at: string | null;
  requires_second_approval: boolean;
}

let cachedToken: { value: string; expiresAt: number } | null = null;

async function password(): Promise<string> {
  if (process.env.LAKEBASE_PASSWORD) return process.env.LAKEBASE_PASSWORD;
  if (cachedToken && Date.now() < cachedToken.expiresAt - 5 * 60_000) return cachedToken.value;
  const host = process.env.DATABRICKS_HOST!.replace(/^(?!https?:\/\/)/, "https://");
  const res = await fetch(`${host}/oidc/v1/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      Authorization: "Basic " + Buffer.from(`${process.env.DATABRICKS_CLIENT_ID}:${process.env.DATABRICKS_CLIENT_SECRET}`).toString("base64"),
    },
    body: "grant_type=client_credentials&scope=all-apis",
  });
  if (!res.ok) throw new Error(`OAuth token request failed: ${res.status}`);
  const body = (await res.json()) as { access_token: string; expires_in: number };
  cachedToken = { value: body.access_token, expiresAt: Date.now() + body.expires_in * 1000 };
  return cachedToken.value;
}

const pool = new Pool({
  host: process.env.PGHOST,
  port: Number(process.env.PGPORT || 5432),
  database: process.env.PGDATABASE,
  user: process.env.PGUSER,
  password,
  ssl: { rejectUnauthorized: true },
  max: 5,
});

const SELECT = `
  SELECT invoice_id, vendor_name, property_name, total_amount::float8 AS total_amount, currency,
         total_eur::float8 AS total_eur, extracted_at, status, reviewed_by, reviewed_at, notes,
         first_approver AS first_approver_email, first_approved_at,
         requires_two_approvers AS requires_second_approval
  FROM approvals.invoice_approvals`;

export async function getInvoices(status?: string): Promise<Invoice[]> {
  const { rows } = status
    ? await pool.query(`${SELECT} WHERE status = $1 ORDER BY total_eur DESC`, [status])
    : await pool.query(`${SELECT} ORDER BY total_eur DESC`);
  return rows;
}

export async function getInvoiceById(invoiceId: string): Promise<Invoice | null> {
  const { rows } = await pool.query(`${SELECT} WHERE invoice_id = $1`, [invoiceId]);
  return rows[0] ?? null;
}

export class ApprovalError extends Error {}

/**
 * Approve or reject a Pending invoice. Over-threshold invoices need two different approvers:
 * the first approval is recorded and the invoice stays Pending until a second person approves.
 * Returns the resulting state.
 */
export async function decide(
  invoiceId: string,
  decision: "approve" | "reject",
  actor: string,
  notes: string,
): Promise<{ status: Invoice["status"]; awaitingSecondApprover: boolean }> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const { rows } = await client.query(
      `SELECT status, first_approver, requires_two_approvers FROM approvals.invoice_approvals WHERE invoice_id = $1 FOR UPDATE`,
      [invoiceId],
    );
    const inv = rows[0];
    if (!inv) throw new ApprovalError("Invoice not found");
    if (inv.status !== "Pending") throw new ApprovalError(`Invoice is already ${inv.status}`);

    let result: { status: Invoice["status"]; awaitingSecondApprover: boolean };
    if (decision === "reject") {
      await client.query(
        `UPDATE approvals.invoice_approvals SET status = 'Rejected', reviewed_by = $2, reviewed_at = now(), notes = $3 WHERE invoice_id = $1`,
        [invoiceId, actor, notes],
      );
      await client.query(`INSERT INTO approvals.approval_events (invoice_id, action, actor, notes) VALUES ($1, 'reject', $2, $3)`, [invoiceId, actor, notes]);
      result = { status: "Rejected", awaitingSecondApprover: false };
    } else if (inv.requires_two_approvers && !inv.first_approver) {
      await client.query(
        `UPDATE approvals.invoice_approvals SET first_approver = $2, first_approved_at = now(), notes = $3 WHERE invoice_id = $1`,
        [invoiceId, actor, notes],
      );
      await client.query(`INSERT INTO approvals.approval_events (invoice_id, action, actor, notes) VALUES ($1, 'first_approval', $2, $3)`, [invoiceId, actor, notes]);
      result = { status: "Pending", awaitingSecondApprover: true };
    } else {
      if (inv.first_approver && inv.first_approver === actor) {
        throw new ApprovalError("The second approval must come from a different person (Expense Approval Policy).");
      }
      await client.query(
        `UPDATE approvals.invoice_approvals SET status = 'Approved', reviewed_by = $2, reviewed_at = now(),
                notes = concat_ws(' | ', notes, $3::text) WHERE invoice_id = $1`,
        [invoiceId, actor, notes],
      );
      await client.query(`INSERT INTO approvals.approval_events (invoice_id, action, actor, notes) VALUES ($1, 'approve', $2, $3)`, [invoiceId, actor, notes]);
      result = { status: "Approved", awaitingSecondApprover: false };
    }
    await client.query("COMMIT");
    return result;
  } catch (e) {
    await client.query("ROLLBACK");
    throw e;
  } finally {
    client.release();
  }
}
