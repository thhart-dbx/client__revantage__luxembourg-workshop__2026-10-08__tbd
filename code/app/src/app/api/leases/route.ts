import { query } from "@/lib/databricks";
import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

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

type RiskLevel = "High" | "Medium" | "Low";

const RATING_TO_NUMERIC: Record<string, number> = {
  AAA: 9,
  AA: 8,
  A: 7,
  BBB: 6,
  BB: 5,
  B: 4,
};

const NUMERIC_TO_RATING = Object.fromEntries(
  Object.entries(RATING_TO_NUMERIC).map(([k, v]) => [v, k])
);

function calculateRiskLevel(
  daysRemaining: number,
  leaseStatus: string,
  creditRating: string
): RiskLevel {
  // High = ≤90 days and not Pending Renewal, OR credit rating < BB
  const ratingNumeric = RATING_TO_NUMERIC[creditRating] || 0;
  if ((daysRemaining <= 90 && leaseStatus !== "Pending Renewal") || ratingNumeric < 5) {
    return "High";
  }
  // Medium = ≤180 days
  if (daysRemaining <= 180) {
    return "Medium";
  }
  // Low otherwise
  return "Low";
}

function getAverageCreditRating(ratings: string[]): string {
  if (ratings.length === 0) return "—";
  const sum = ratings.reduce((acc, r) => acc + (RATING_TO_NUMERIC[r] || 0), 0);
  const avg = sum / ratings.length;
  const rounded = Math.round(avg);
  return NUMERIC_TO_RATING[rounded] || "—";
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const windowDays = parseInt(searchParams.get("window_days") || "90");
    const regionFilter = searchParams.get("region") || "all";
    const propertyTypeFilter = searchParams.get("property_type") || "all";
    const sortBy = searchParams.get("sort_by") || "lease_end";
    const sortAsc = searchParams.get("sort_asc") === "true";

    const catalog = process.env.DATABRICKS_CATALOG;
    const schema = process.env.DATABRICKS_SCHEMA;
    if (!catalog || !schema) throw new Error("DATABRICKS_CATALOG and DATABRICKS_SCHEMA must be set");

    let sql = `
      SELECT
        l.lease_id,
        p.property_name,
        p.property_type,
        p.region_name,
        t.tenant_name,
        t.credit_rating,
        CAST(l.lease_end AS STRING) AS lease_end,
        l.monthly_rent,
        l.lease_status,
        CAST(DATEDIFF(day, current_date(), l.lease_end) AS INT) as days_remaining
      FROM ${catalog}.${schema}.silver_leases l
      JOIN ${catalog}.${schema}.silver_tenants t ON l.tenant_id = t.tenant_id
      JOIN ${catalog}.${schema}.silver_properties p ON l.property_id = p.property_id
      WHERE DATEDIFF(day, current_date(), l.lease_end) <= :window_days
    `;
    // Expiry windows look forward; only "All" (99999) includes leases that have already expired.
    if (windowDays < 99999) sql += " AND l.lease_end >= current_date()";

    const namedParams: Record<string, string | number | boolean | null> = {
      window_days: windowDays,
    };

    if (regionFilter !== "all") {
      sql += " AND p.region_name = :region";
      namedParams.region = regionFilter;
    }

    if (propertyTypeFilter !== "all") {
      sql += " AND p.property_type = :property_type";
      namedParams.property_type = propertyTypeFilter;
    }

    // Order by clause
    const sortColumnMap: Record<string, string> = {
      property_name: "p.property_name",
      tenant_name: "t.tenant_name",
      lease_end: "l.lease_end",
      monthly_rent: "l.monthly_rent",
      days_remaining: "DATEDIFF(day, current_date(), l.lease_end)",
      risk_level: "CASE WHEN (DATEDIFF(day, current_date(), l.lease_end) <= 90 AND l.lease_status != 'Pending Renewal') OR (t.credit_rating NOT IN ('AAA', 'AA', 'A', 'BBB')) THEN 0 WHEN DATEDIFF(day, current_date(), l.lease_end) <= 180 THEN 1 ELSE 2 END",
    };

    const sortColumn = sortColumnMap[sortBy] || sortColumnMap.lease_end;
    const orderDirection = sortAsc ? "ASC" : "DESC";
    sql += ` ORDER BY ${sortColumn} ${orderDirection}`;

    const results = await query<
      Omit<LeaseRecord, "risk_level">
    >(sql, namedParams);

    // Add risk level to each record
    const leases: LeaseRecord[] = results.map((r) => ({
      ...r,
      risk_level: calculateRiskLevel(r.days_remaining, r.lease_status, r.credit_rating),
    }));

    // Calculate summary
    const summary = {
      leases_expiring: leases.length,
      monthly_revenue_at_risk: leases.reduce((sum, l) => sum + l.monthly_rent, 0),
      annual_revenue_at_risk: leases.reduce((sum, l) => sum + l.monthly_rent * 12, 0),
      avg_credit_rating: getAverageCreditRating(leases.map((l) => l.credit_rating)),
    };

    return NextResponse.json({ leases, summary });
  } catch (error) {
    console.error("Failed to fetch leases:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch leases" },
      { status: 500 }
    );
  }
}
