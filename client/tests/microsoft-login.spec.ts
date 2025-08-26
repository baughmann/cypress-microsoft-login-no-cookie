import { test, expect } from "@playwright/test";

const SITE_ONE_URL = "http://localhost:9090";

test.describe("Microsoft Login Test", () => {
  test("Should successfully login with Microsoft", async ({ page }) => {
    // Get environment variables
    const microsoftEmail = process.env.MICROSOFT_LOGIN_EMAIL;
    const microsoftPassword = process.env.MICROSOFT_LOGIN_PASSWORD;

    if (!microsoftEmail || !microsoftPassword) {
      test.skip(
        !microsoftEmail || !microsoftPassword,
        "Microsoft login credentials not provided"
      );
      return;
    }

    // Navigate to the main site
    await page.goto(SITE_ONE_URL);

    // Click the Login button
    await page.getByText("Login").click();

    // We should be redirected to Microsoft login page
    await expect(page).toHaveURL(/login\.microsoftonline\.com/);

    // Fill in the username
    await page.fill('input[name="loginfmt"]', microsoftEmail);
    await page.click('input[type="submit"]');

    // Wait for password field and fill it
    await page.waitForSelector('input[name="passwd"]', { timeout: 10000 });
    await page.fill('input[name="passwd"]', microsoftPassword);
    await page.click('input[type="submit"]');

    // Handle "Stay signed in?" prompt if it appears
    try {
      await page.waitForSelector("input[type='button'][value='No']", {
        timeout: 5000,
      });
      await page.click("input[type='button'][value='No']");
    } catch (error) {
      // If the prompt doesn't appear within 5 seconds, continue
      console.log("Stay signed in prompt did not appear or already handled");
    }

    // Microsoft should redirect back to our site
    await expect(page).toHaveURL(new RegExp(SITE_ONE_URL));
    // after another redirect, we should be back to the client and see the "Login" button
    await expect(page.getByText("Login")).toBeVisible();
  });
});
