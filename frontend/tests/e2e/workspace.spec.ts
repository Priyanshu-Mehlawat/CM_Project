import { test, expect } from "@playwright/test";
test("real API → episode → replay → correction → research", async ({
  page,
}, testInfo) => {
  await page.goto("/clinical");
  await expect(page.getByText("SYNTHETIC DEMO", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: /Example A/ }).click();
  await expect(
    page.getByRole("heading", { name: "Current creatinine stage 1" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Outcome unknown" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Hour 32", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Current creatinine stage 2" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Observed progression to Stage 2/3" }),
  ).toBeVisible();
  await page.screenshot({
    path: testInfo.outputPath("desktop.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: /Example D/ }).click();
  await page.getByRole("button", { name: "Hour 20", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Current creatinine stage 0" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Research Console" }).click();
  await expect(
    page.getByRole("heading", { name: "Not yet evaluated", exact: true }),
  ).toBeVisible();
});
test("mobile layout keeps navigation and case selection usable", async ({
  page,
}, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/clinical");
  await page.getByRole("button", { name: /Example C/ }).click();
  await expect(
    page.getByRole("heading", { name: "Current creatinine stage 1" }),
  ).toBeVisible();
  await page.screenshot({
    path: testInfo.outputPath("mobile.png"),
    fullPage: true,
  });
  await page.getByRole("link", { name: "Clinical Protocol" }).click();
  await expect(
    page.getByRole("heading", { name: "Clinical protocol", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
});
