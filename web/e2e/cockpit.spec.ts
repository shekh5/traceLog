import { expect, test } from "@playwright/test";

test("authenticated offline cockpit drives the Patient and self-evaluation", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Replay a labelled supervision example" })).toBeVisible();
  await page
    .getByPlaceholder("Required to drive Patient and run self-evaluation")
    .fill("test-key");

  await page.getByRole("button", { name: "Play offline fixture" }).click();
  await expect(page.getByText("Germany orders have a 45-day return window", { exact: false })).toBeVisible();
  await expect(page.getByText("Prompt remediation planned")).toBeVisible();

  await page.getByRole("button", { name: "Show fixture scorecard" }).click();
  await expect(page.getByText("10/11 traps correct")).toBeVisible();
});
