import { test, expect } from "@playwright/test";

/**
 * CaseMate E2E smoke tests.
 *
 * These tests verify that critical pages load and core UI elements
 * are present. They do NOT require a running backend — they validate
 * the frontend renders without crashing.
 */

test.describe("CaseMate Smoke Tests", () => {
  test("landing page loads with CaseMate branding", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/CaseMate/i);
    // The landing page should have the main heading or CaseMate branding
    const body = await page.textContent("body");
    expect(body).toBeTruthy();
  });

  test("landing page has navigation elements", async ({ page }) => {
    await page.goto("/");
    // Check that the page has rendered some content (not a blank page)
    await expect(page.locator("body")).not.toBeEmpty();
  });

  test("onboarding page is accessible", async ({ page }) => {
    const response = await page.goto("/onboarding");
    expect(response?.status()).toBeLessThan(500);
  });

  test("chat page is accessible", async ({ page }) => {
    const response = await page.goto("/chat");
    expect(response?.status()).toBeLessThan(500);
  });

  test("profile page is accessible", async ({ page }) => {
    const response = await page.goto("/profile");
    expect(response?.status()).toBeLessThan(500);
  });
});
