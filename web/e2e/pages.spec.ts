import { expect, test } from "@playwright/test";

test("static Pages fixture completes without a backend or token", async ({ page }) => {
  const failedRequests: string[] = [];
  page.on("requestfailed", (request) => failedRequests.push(request.url()));

  await page.goto("./");
  await expect(page.getByText("offline fixture · no API calls")).toBeVisible();
  await expect(page.getByPlaceholder("Required to drive Patient and run self-evaluation")).toHaveCount(0);

  await page.getByRole("button", { name: "Play offline fixture" }).click();
  await expect(page.getByText("Germany orders have a 45-day return window", { exact: false })).toBeVisible();
  await expect(page.getByText("Candidate survives fixture holdouts")).toBeVisible();

  await page.getByRole("button", { name: "Show fixture scorecard" }).click();
  await expect(page.getByText("10/11 traps correct")).toBeVisible();
  expect(failedRequests).toEqual([]);
});
