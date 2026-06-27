import { test, expect } from "@playwright/test"

test.describe("Authentication", () => {
  test("login page renders correctly", async ({ page }) => {
    await page.goto("/login")
    await expect(page.getByText(/sign in to continue/i)).toBeVisible()
    await expect(page.getByPlaceholder(/username/i)).toBeVisible()
    await expect(page.getByPlaceholder(/password/i)).toBeVisible()
    await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible()
  })

  test("register page renders correctly", async ({ page }) => {
    await page.goto("/register")
    await expect(page.getByText("Create Account").first()).toBeVisible({ timeout: 5000 })
    await expect(page.getByRole("button", { name: /create account/i })).toBeVisible()
  })

  test("login with empty fields shows validation", async ({ page }) => {
    await page.goto("/login")
    await page.getByRole("button", { name: /sign in/i }).click()
    await expect(page.getByText(/username is required/i)).toBeVisible()
    await expect(page.getByText(/password is required/i)).toBeVisible()
  })

  test("login with mock API succeeds and stores token", async ({ page }) => {
    await page.route("**/api/v1/auth/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "mock-access-token",
          refresh_token: "mock-refresh-token",
          user: {
            id: "u1",
            email: "test@test.gov.in",
            username: "test_officer",
            full_name: "Test Officer",
            is_active: true,
            is_superuser: false,
            preferred_language: "en",
            roles: [{ id: "r1", name: "officer" }],
          },
        }),
      })
    })

    await page.route("**/api/v1/auth/me", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "u1",
          email: "test@test.gov.in",
          username: "test_officer",
          full_name: "Test Officer",
          is_active: true,
          is_superuser: false,
          preferred_language: "en",
          roles: [{ id: "r1", name: "officer" }],
        }),
      })
    })

    await page.goto("/login")
    await page.getByPlaceholder(/enter your username/i).fill("test_officer")
    await page.getByPlaceholder(/enter your password/i).fill("Secure@123")
    await page.getByRole("button", { name: /sign in/i }).click()

    const token = await page.evaluate(() => localStorage.getItem("access_token"))
    expect(token).toBe("mock-access-token")
  })

  test("dashboard redirects to login when unauthenticated", async ({ page }) => {
    await page.goto("/")
    await expect(page).toHaveURL(/.*login.*/, { timeout: 5000 })
  })
})
