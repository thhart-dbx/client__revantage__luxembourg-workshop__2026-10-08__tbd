"use client";

import { useState } from "react";
import { X } from "lucide-react";

interface Invoice {
  invoice_id: string;
  vendor_name: string;
  property_name: string | null;
  total_amount: number;
  currency: string;
  total_eur: number;
  status: "Pending" | "Approved" | "Rejected";
  requires_second_approval: boolean;
  first_approver_email: string | null;
  first_approved_at: string | null;
  notes: string | null;
}

interface InvoiceDetailProps {
  invoice: Invoice;
  onApprove: (invoiceId: string, notes: string) => Promise<void>;
  onReject: (invoiceId: string, notes: string) => Promise<void>;
  onClose: () => void;
}

export function InvoiceDetail({ invoice, onApprove, onReject, onClose }: InvoiceDetailProps) {
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const handleApprove = async () => {
    try {
      setLoading(true);
      setError(null);
      await onApprove(invoice.invoice_id, notes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to approve");
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    try {
      setLoading(true);
      setError(null);
      await onReject(invoice.invoice_id, notes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject");
    } finally {
      setLoading(false);
    }
  };

  // Threshold is EUR 50,000 (Expense Approval Policy); total_eur is converted at the ECB rate.
  const isHighValue = invoice.requires_second_approval;
  const needsEuroThreshold = false;

  return (
    <div className="bg-white rounded-lg shadow-lg">
      <div className="sticky top-0 flex items-center justify-between p-6 border-b border-gray-200 bg-gray-50">
        <h3 className="text-lg font-semibold text-gray-900">Invoice Details</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(100vh-200px)]">
        {/* Invoice ID and Basic Info */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">
            Invoice Information
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Invoice ID:</span>
              <span className="font-medium text-gray-900">{invoice.invoice_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Vendor:</span>
              <span className="font-medium text-gray-900">{invoice.vendor_name}</span>
            </div>
            {invoice.property_name && (
              <div className="flex justify-between">
                <span className="text-gray-600">Property:</span>
                <span className="font-medium text-gray-900">{invoice.property_name}</span>
              </div>
            )}
          </div>
        </div>

        {/* Amount - Highlighted */}
        <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
          <p className="text-sm text-gray-600 mb-1">Total Amount</p>
          <p className="text-2xl font-bold text-blue-900">
            {formatAmount(invoice.total_amount, invoice.currency)}
          </p>
        </div>

        {/* Approval Requirements */}
        {(isHighValue || needsEuroThreshold) && (
          <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
            <div className="flex gap-3">
              <div className="text-orange-600 font-bold text-lg">⚠</div>
              <div>
                <p className="font-semibold text-orange-900 text-sm">Approval Required</p>
                <p className="text-xs text-orange-700 mt-1">
                  {isHighValue && `This invoice is €${Math.round(invoice.total_eur).toLocaleString("en-GB")}, above the €50,000 threshold`}
                </p>
                <p className="text-xs text-orange-700 mt-1">
                  Per the Expense Approval Policy, this requires:
                </p>
                <ul className="text-xs text-orange-700 mt-2 ml-4 space-y-1 list-disc">
                  <li>CFO approval</li>
                  <li>Asset Management Director approval</li>
                </ul>
                {invoice.first_approver_email && (
                  <p className="text-xs text-orange-700 mt-2">
                    First approval: {invoice.first_approver_email}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Notes Field */}
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Approval Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Enter your review comments..."
            disabled={loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100"
            rows={4}
          />
          <p className="mt-1 text-xs text-gray-500">Required for approval or rejection</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <button
            onClick={handleReject}
            disabled={loading || !notes.trim()}
            className="flex-1 px-4 py-2 border border-red-300 text-red-700 rounded-md font-medium text-sm hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "..." : "Reject"}
          </button>
          <button
            onClick={handleApprove}
            disabled={loading || !notes.trim()}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md font-medium text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "..." : "Approve"}
          </button>
        </div>
      </div>
    </div>
  );
}
