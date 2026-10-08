import { NextRequest, NextResponse } from "next/server";
import { ApprovalError, decide } from "@/lib/lakebase";

export async function POST(request: NextRequest) {
  const { invoiceId, notes } = (await request.json()) as { invoiceId?: string; notes?: string };
  if (!invoiceId || !notes) return NextResponse.json({ error: "invoiceId and notes are required" }, { status: 400 });
  const actor = request.headers.get("x-forwarded-email");
  if (!actor) return NextResponse.json({ error: "No signed-in user" }, { status: 401 });
  try {
    const r = await decide(invoiceId, "reject", actor, notes);
    return NextResponse.json({ message: "Invoice rejected.", status: r.status });
  } catch (e) {
    if (e instanceof ApprovalError) return NextResponse.json({ error: e.message }, { status: 409 });
    console.error("reject failed", e);
    return NextResponse.json({ error: "Failed to reject invoice" }, { status: 500 });
  }
}
