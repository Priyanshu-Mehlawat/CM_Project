import { test, expect } from "@playwright/test";
for (const width of [1440, 390]) {
  test(`upload assessment at width ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/assess");
    await page.getByRole("button", { name: "Load synthetic example" }).click();
    await page.getByRole("button", { name: "Evaluate measurements" }).click();
    await expect(page.getByRole("heading", { name: "Current creatinine stage 1" })).toBeVisible();
    await expect(page.getByText("Hour 3", {exact:true})).toBeVisible();
    await expect(page.getByText(/Install the privately trained/)).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await page.getByRole("button", { name: "Clear session" }).click();
    await expect(page.getByRole("heading", {name: "Assessment results"})).toBeVisible();
  });
}
