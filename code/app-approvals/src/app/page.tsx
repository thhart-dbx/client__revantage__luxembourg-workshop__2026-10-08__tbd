"use client";

import { useEffect, useState } from "react";
import { InvoiceList } from "@/components/invoice-list";
import { InvoiceDetail } from "@/components/invoice-detail";

interface Invoice {
  invoice_id: string;
  vendor_name: string;
  property_name: string | null;
  total_amount: number;
  currency: string;
  total_eur: number;
  status: "Pending" | "Approved" | "Rejected";
  reviewed_by: string | null;
  reviewed_at: string | null;
  notes: string | null;
  requires_second_approval: boolean;
  first_approver_email: string | null;
  first_approved_at: string | null;
}

export default function Home() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/invoices?status=Pending");
      if (!response.ok) throw new Error("Failed to fetch invoices");
      const data = await response.json();
      setInvoices(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleApprove = async (invoiceId: string, notes: string) => {
    try {
      const response = await fetch("/api/invoices/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ invoiceId, notes }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || "Failed to approve invoice");
      setError(null);
      setNotice(body.message);
      setSelectedInvoice(null);
      await fetchInvoices();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to approve invoice");
    }
  };

  const handleReject = async (invoiceId: string, notes: string) => {
    try {
      const response = await fetch("/api/invoices/reject", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ invoiceId, notes }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || "Failed to reject invoice");
      setError(null);
      setNotice(body.message);
      setSelectedInvoice(null);
      await fetchInvoices();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject invoice");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900">Revantage Invoice Approvals</h1>
        <p className="text-sm text-gray-600 mt-1">Review and approve pending invoices</p>
      </header>

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
        {notice && (
          <div role="status" className="mb-4 rounded-md border border-blue-200 bg-blue-50 px-4 py-2 text-sm text-blue-900">
            {notice}
          </div>
        )}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-800">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <InvoiceList
            invoices={invoices}
            loading={loading}
            selectedId={selectedInvoice?.invoice_id}
            onSelect={(inv) => setSelectedInvoice(invoices.find((i) => i.invoice_id === inv.invoice_id) ?? null)}
          />

          {selectedInvoice && (
            <InvoiceDetail
              invoice={selectedInvoice}
              onApprove={handleApprove}
              onReject={handleReject}
              onClose={() => setSelectedInvoice(null)}
            />
          )}
        </div>
      </main>
    </div>
  );
}
