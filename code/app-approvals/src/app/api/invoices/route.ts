import { NextRequest, NextResponse } from "next/server";
export const dynamic = "force-dynamic";
import { getInvoices } from "@/lib/lakebase";

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const status = url.searchParams.get("status") || undefined;

    const invoices = await getInvoices(status || undefined);

    return NextResponse.json(invoices);
  } catch (error) {
    console.error("Error fetching invoices:", error);
    return NextResponse.json(
      { error: "Failed to fetch invoices" },
      { status: 500 }
    );
  }
}
