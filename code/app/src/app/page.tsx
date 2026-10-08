"use client";

import { useEffect, useState } from "react";
import { Download } from "lucide-react";

type LeaseRecord = {
  lease_id: string;
  property_name: string;
  property_type: string;
  region_name: string;
  tenant_name: string;
  credit_rating: string;
  lease_end: string;
  monthly_rent: number;
  lease_status: string;
  days_remaining: number;
  risk_level: string;
};

type SummaryData = {
  leases_expiring: number;
  monthly_revenue_at_risk: number;
  annual_revenue_at_risk: number;
  avg_credit_rating: string;
};

export default function Home() {
  const [leases, setLeases] = useState<LeaseRecord[]>([]);
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [windowDays, setWindowDays] = useState<number>(90);
  const [region, setRegion] = useState<string>("all");
  const [propertyType, setPropertyType] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("lease_end");
  const [sortAsc, setSortAsc] = useState(false);

  // Derived values
  const [regions, setRegions] = useState<string[]>([]);
  const [propertyTypes, setPropertyTypes] = useState<string[]>([]);

  useEffect(() => {
    fetchData();
  }, [windowDays, region, propertyType, sortBy, sortAsc]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        window_days: windowDays.toString(),
        region: region || "all",
        property_type: propertyType || "all",
        sort_by: sortBy,
        sort_asc: sortAsc.toString(),
      });

      const response = await fetch(`/api/leases?${params}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch leases: ${response.statusText}`);
      }

      const data = await response.json();
      setLeases(data.leases);
      setSummary(data.summary);

      // Extract unique values for filters
      if (data.leases.length > 0) {
        const uniqueRegions = Array.from(
          new Set(data.leases.map((l: LeaseRecord) => l.region_name))
        ).sort() as string[];
        const uniqueTypes = Array.from(
          new Set(data.leases.map((l: LeaseRecord) => l.property_type))
        ).sort() as string[];
        setRegions(uniqueRegions);
        setPropertyTypes(uniqueTypes);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(column);
      setSortAsc(false);
    }
  };

  const exportCSV = () => {
    if (leases.length === 0) {
      alert("No data to export");
      return;
    }

    const headers = [
      "Lease ID",
      "Property Name",
      "Property Type",
      "Region",
      "Tenant Name",
      "Credit Rating",
      "Lease End",
      "Monthly Rent (EUR)",
      "Days Remaining",
      "Risk Level",
      "Status",
    ];

    const rows = leases.map((lease) => [
      lease.lease_id,
      lease.property_name,
      lease.property_type,
      lease.region_name,
      lease.tenant_name,
      lease.credit_rating,
      lease.lease_end,
      lease.monthly_rent.toFixed(2),
      lease.days_remaining,
      lease.risk_level,
      lease.lease_status,
    ]);

    const csv = [headers, ...rows].map((row) => row.map((v) => `"${v}"`).join(",")).join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lease-expiry-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "high":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100";
      case "medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100";
      case "low":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Lease Expiry Tracker
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Monitor upcoming lease expirations and manage portfolio risk
          </p>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                Leases Expiring
              </p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {summary.leases_expiring}
              </p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                Monthly Revenue at Risk
              </p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                €{(summary.monthly_revenue_at_risk / 1000).toFixed(0)}k
              </p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                Annual Revenue at Risk
              </p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                €{(summary.annual_revenue_at_risk / 1000000).toFixed(1)}M
              </p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                Avg Credit Rating
              </p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {summary.avg_credit_rating}
              </p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Expiry Window
              </label>
              <select
                value={windowDays}
                onChange={(e) => setWindowDays(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
              >
                <option value={90}>90 Days</option>
                <option value={180}>180 Days</option>
                <option value={365}>365 Days</option>
                <option value={99999}>All (including expired)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Region
              </label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Regions</option>
                {regions.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Property Type
              </label>
              <select
                value={propertyType}
                onChange={(e) => setPropertyType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Types</option>
                {propertyTypes.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={exportCSV}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-500">{error}</div>
          ) : leases.length === 0 ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              No leases found matching the selected filters
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-slate-700 border-b border-gray-200 dark:border-slate-600">
                  <tr>
                    {[
                      { key: "property_name", label: "Property" },
                      { key: "tenant_name", label: "Tenant" },
                      { key: "lease_end", label: "Lease End" },
                      { key: "monthly_rent", label: "Monthly Rent" },
                      { key: "days_remaining", label: "Days Remaining" },
                      { key: "risk_level", label: "Risk" },
                    ].map(({ key, label }) => (
                      <th
                        key={key}
                        onClick={() => handleSort(key)}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-slate-600"
                      >
                        {label}
                        {sortBy === key && (sortAsc ? " ↑" : " ↓")}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
                  {leases.map((lease) => (
                    <tr
                      key={lease.lease_id}
                      className="hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                        {lease.property_name}
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {lease.property_type} • {lease.region_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                        {lease.tenant_name}
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {lease.credit_rating}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                        {lease.lease_end}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-gray-100">
                        €{lease.monthly_rent.toLocaleString("de-DE", { maximumFractionDigits: 0 })}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-gray-100">
                        {lease.days_remaining < 0 ? `${Math.abs(lease.days_remaining)}d ago` : `${lease.days_remaining}d`}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getRiskColor(
                            lease.risk_level
                          )}`}
                          title={getRiskTooltip(lease.risk_level, lease.lease_status, lease.credit_rating)}
                        >
                          {lease.risk_level}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function getRiskTooltip(risk: string, status: string, rating: string): string {
  const rules = [
    `High = ≤90 days and not "Pending Renewal", OR credit rating < BB`,
    `Medium = ≤180 days`,
    `Low = otherwise`,
  ];
  return rules.join("\n");
}
