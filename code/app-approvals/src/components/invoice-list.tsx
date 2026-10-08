import { AlertCircle, CheckCircle, XCircle } from "lucide-react";

interface Invoice {
  invoice_id: string;
  vendor_name: string;
  property_name: string | null;
  total_amount: number;
  currency: string;
  status: string;
  requires_second_approval: boolean;
}

interface InvoiceListProps {
  invoices: Invoice[];
  loading: boolean;
  selectedId?: string;
  onSelect: (invoice: Invoice) => void;
}

export function InvoiceList({ invoices, loading, selectedId, onSelect }: InvoiceListProps) {
  const getStatusIcon = (status: string, requiresSecond: boolean) => {
    if (status === "Pending" && requiresSecond) {
      return <AlertCircle className="h-5 w-5 text-orange-500" />;
    }
    if (status === "Approved") {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    }
    if (status === "Rejected") {
      return <XCircle className="h-5 w-5 text-red-500" />;
    }
    return <AlertCircle className="h-5 w-5 text-blue-500" />;
  };

  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-gray-200 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (invoices.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        <p className="text-lg">No pending invoices</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          Pending Invoices ({invoices.length})
        </h2>
      </div>
      <div className="divide-y divide-gray-200">
        {invoices.map((invoice) => (
          <button
            key={invoice.invoice_id}
            onClick={() => onSelect(invoice)}
            className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
              selectedId === invoice.invoice_id ? "bg-blue-50" : ""
            }`}
          >
            <div className="flex items-start gap-4">
              <div className="mt-1">{getStatusIcon(invoice.status, invoice.requires_second_approval)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-gray-900 truncate">{invoice.invoice_id}</p>
                  {invoice.requires_second_approval && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                      Requires 2 Approvals
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 truncate">{invoice.vendor_name}</p>
                {invoice.property_name && (
                  <p className="text-xs text-gray-500">{invoice.property_name}</p>
                )}
              </div>
              <div className="text-right flex-shrink-0">
                <p className="font-semibold text-gray-900">
                  {formatAmount(invoice.total_amount, invoice.currency)}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
