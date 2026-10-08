import { expect, test } from "@playwright/test";

// Placeholder: replace with one spec per CUJ from notes/claude-notes/plan.md.
test("home page loads", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/.+/);
});
