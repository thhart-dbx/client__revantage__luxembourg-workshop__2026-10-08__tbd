import { NextRequest, NextResponse } from "next/server";
import { ApprovalError, decide } from "@/lib/lakebase";

// The signed-in user comes from the Databricks Apps proxy header.
export async function POST(request: NextRequest) {
  const { invoiceId, notes } = (await request.json()) as { invoiceId?: string; notes?: string };
  if (!invoiceId || !notes) return NextResponse.json({ error: "invoiceId and notes are required" }, { status: 400 });
  const actor = request.headers.get("x-forwarded-email");
  if (!actor) return NextResponse.json({ error: "No signed-in user" }, { status: 401 });
  try {
    const r = await decide(invoiceId, "approve", actor, notes);
    return NextResponse.json({
      message: r.awaitingSecondApprover ? "First approval recorded. Awaiting a second approver." : "Invoice approved.",
      requires_second_approval: r.awaitingSecondApprover,
      status: r.status,
    });
  } catch (e) {
    if (e instanceof ApprovalError) return NextResponse.json({ error: e.message }, { status: 409 });
    console.error("approve failed", e);
    return NextResponse.json({ error: "Failed to approve invoice" }, { status: 500 });
  }
}
