import { test, expect } from "@playwright/test";
import { execSync } from "node:child_process";

// CUJ: an approver works the invoice queue. State lives in Lakebase, so these tests run serially on
// one browser project and reset the seed (5 Pending invoices) before and after.
// Locally the "signed-in user" is simulated with the x-forwarded-email header that the Databricks
// Apps proxy sets in production; on the deployed app the proxy sets it from your login.
const LOCAL = !process.env.BASE_URL;
const PROFILE = process.env.DATABRICKS_PROFILE ?? "fevm-thhart-october-2026";

function resetSeed() {
  execSync(
    `uv run -q --index-url https://pypi-proxy.cloud.databricks.com/simple --with "psycopg[binary]" ` +
      `../lakebase/lakebase_sql.py --profile ${PROFILE} --instance revantage-lux-ops --db revantage_ops -f ../lakebase/d12_reset.sql`,
    { stdio: "ignore" },
  );
}

test.describe.configure({ mode: "serial" });

test.describe("Invoice approvals", () => {
  test.beforeAll(() => resetSeed());
  test.afterAll(() => resetSeed());
  test.beforeEach(({}, info) => test.skip(info.project.name !== "desktop", "stateful: desktop project only"));

  const as = (email: string): Record<string, string> => (LOCAL ? { "x-forwarded-email": email } : {});

  test("queue shows the 5 pending invoices, largest first, with two-approver flags", async ({ page, request }) => {
    const res = await request.get("/api/invoices?status=Pending");
    const invoices = await res.json();
    expect(invoices.map((i: { invoice_id: string }) => i.invoice_id)).toEqual([
      "HV-2026-0417", "TM-POL-2026-3391", "PE-2026-06-0088", "ACD-2026-IF-55120", "NGD-26-1184",
    ]);
    expect(invoices.filter((i: { requires_second_approval: boolean }) => i.requires_second_approval).length).toBe(2);
    await page.goto("/");
    await expect(page.getByText("HV-2026-0417")).toBeVisible();
    await expect(page.getByText("Coastal Climate Systems LLC")).toBeVisible();
  });

  test("under-threshold invoice is approved in one step", async ({ request }) => {
    const r = await request.post("/api/invoices/approve", {
      data: { invoiceId: "PE-2026-06-0088", notes: "Utilities in line with budget" }, headers: as("asset.manager@revantage.example"),
    });
    expect(r.ok()).toBeTruthy();
    expect((await r.json()).status).toBe("Approved");
  });

  test("invoice can be rejected with a note", async ({ request }) => {
    const r = await request.post("/api/invoices/reject", {
      data: { invoiceId: "NGD-26-1184", notes: "Duplicate of May invoice" }, headers: as("asset.manager@revantage.example"),
    });
    expect((await r.json()).status).toBe("Rejected");
  });

  test("over-threshold invoice needs two different approvers", async ({ request }) => {
    test.skip(!LOCAL, "needs two identities; on the deployed app only the first approval is tested");
    const first = await request.post("/api/invoices/approve", {
      data: { invoiceId: "HV-2026-0417", notes: "Chiller replacement - CapEx" }, headers: as("cfo@revantage.example"),
    });
    expect((await first.json()).requires_second_approval).toBe(true);
    const same = await request.post("/api/invoices/approve", {
      data: { invoiceId: "HV-2026-0417", notes: "again" }, headers: as("cfo@revantage.example"),
    });
    expect(same.status()).toBe(409);
    const second = await request.post("/api/invoices/approve", {
      data: { invoiceId: "HV-2026-0417", notes: "Agreed" }, headers: as("am.director@revantage.example"),
    });
    expect((await second.json()).status).toBe("Approved");
  });

  test("UI: approve from the detail panel", async ({ page }) => {
    test.skip(LOCAL, "the local dev server has no auth proxy to set the user header for browser requests");
    await page.goto("/");
    await page.getByText("ACD-2026-IF-55120").click();
    await page.getByRole("textbox").last().fill("Annual property tax, as assessed");
    await page.getByRole("button", { name: /approve/i }).click();
    await expect(page.getByRole("status")).toContainText(/approved/i);
  });
});
