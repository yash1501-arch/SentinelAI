import { test, expect } from "@playwright/test"

const mockUser = {
  id: "u1",
  email: "test@test.gov.in",
  username: "test_officer",
  full_name: "Test Officer",
  is_active: true,
  is_superuser: false,
  preferred_language: "en",
  roles: [{ id: "r1", name: "officer", description: "Police Officer", priority_level: "standard", is_active: true }],
}

test.beforeEach(async ({ page, context }) => {
  await context.addCookies([
    { name: "access_token", value: "mock-token", domain: "localhost", path: "/" },
  ])

  await page.addInitScript(() => {
    localStorage.setItem("access_token", "mock-token")
    localStorage.setItem("refresh_token", "mock-refresh")
    localStorage.setItem("user", JSON.stringify({
      id: "u1",
      email: "test@test.gov.in",
      username: "test_officer",
      full_name: "Test Officer",
      is_active: true,
      is_superuser: false,
      preferred_language: "en",
      roles: [{ id: "r1", name: "officer" }],
    }))
  })

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(mockUser) })
  })
})

test.describe("Dashboard pages", () => {
  test("chat page loads", async ({ page }) => {
    await page.goto("/chat")
    await expect(page.getByRole("heading", { name: /AI Chat/i })).toBeVisible({ timeout: 10000 })
    await expect(page.getByPlaceholder(/type your question/i)).toBeVisible()
  })

  test("cases page loads with mock data", async ({ page }) => {
    await page.route("**/api/v1/cases*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(Array.from({ length: 5 }, (_, i) => ({
          id: `c${i}`,
          fir_id: `f${i}`,
          crime_type_id: `ct${i}`,
          incident_date: "2026-01-15",
          incident_time: null,
          description: `Test case ${i}`,
          modus_operandi: null,
          is_solved: i % 2 === 0,
          property_value_loss: 0,
          injury_count: i,
          fatality_count: 0,
          created_at: "2026-01-16T00:00:00Z",
          crime_type: { id: `ct${i}`, name: "Burglary", category: "Property", description: "", severity_level: 3 },
        }))),
      })
    })
    await page.goto("/cases")
    await expect(page.getByRole("heading", { name: /cases/i })).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("Burglary").first()).toBeVisible({ timeout: 10000 })
  })

  test("analytics page loads", async ({ page }) => {
    await page.route("**/api/v1/analytics/trends*", async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify([]) })
    })
    await page.route("**/api/v1/analytics/statistics*", async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify({ total_cases: 100, solved_cases: 40 }) })
    })
    await page.goto("/analytics")
    await expect(page.getByRole("heading", { name: /analytics/i })).toBeVisible({ timeout: 10000 })
  })

  test("forecasting page loads", async ({ page }) => {
    await page.route("**/api/v1/analytics/forecast", async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify({
        forecast_data: [], model_used: "Prophet", confidence_level: 0.85, features_used: [],
      }) })
    })
    await page.goto("/forecasting")
    await expect(page.getByRole("heading", { name: /forecast/i })).toBeVisible({ timeout: 10000 })
  })

  test("admin page loads", async ({ page }) => {
    await page.route("**/api/v1/admin/users", async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify([mockUser]) })
    })
    await page.route("**/api/v1/admin/audit-logs", async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify([]) })
    })
    await page.goto("/admin")
    await expect(page.getByRole("heading", { name: /admin/i })).toBeVisible({ timeout: 10000 })
  })

  test("network page loads", async ({ page }) => {
    await page.goto("/network")
    await expect(page.getByRole("heading", { name: /network/i })).toBeVisible({ timeout: 10000 })
  })

  test("settings page loads", async ({ page }) => {
    await page.goto("/settings")
    await expect(page.getByRole("heading", { name: /settings/i })).toBeVisible({ timeout: 10000 })
  })

  test("map page loads", async ({ page }) => {
    await page.goto("/map")
    await expect(page.getByRole("heading", { name: /crime map/i })).toBeVisible({ timeout: 10000 })
  })

  test("timeline page loads", async ({ page }) => {
    await page.goto("/timeline")
    await expect(page.getByRole("heading", { name: /case timeline/i })).toBeVisible({ timeout: 10000 })
  })

  test("profiles page loads", async ({ page }) => {
    await page.goto("/profiles")
    await expect(page.getByRole("heading", { name: /offender profiles/i })).toBeVisible({ timeout: 10000 })
  })

  test("case detail page loads with mock data", async ({ page }) => {
    const mockCaseId = "c0000000-0000-4000-8000-000000000001"

    await page.route(`**/api/v1/cases/${mockCaseId}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: mockCaseId,
          fir_id: "FIR-2024-001",
          crime_type_id: "ct1",
          incident_date: "2026-01-15",
          incident_time: "14:30",
          description: "Armed robbery at City Mall involving three suspects",
          modus_operandi: "Armed robbery in daylight",
          is_solved: false,
          property_value_loss: 150000,
          injury_count: 2,
          fatality_count: 0,
          created_at: "2026-01-16T00:00:00Z",
          crime_type: {
            id: "ct1",
            name: "Robbery",
            category: "Violent",
            description: "Armed robbery cases",
            severity_level: 4,
          },
        }),
      })
    })

    await page.route(`**/api/v1/cases/${mockCaseId}/timeline`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: "t1",
            case_id: mockCaseId,
            event_type: "incident_reported",
            title: "Incident Reported",
            description: "Robbery reported at City Mall",
            timestamp: "2026-01-15T14:35:00Z",
            actor: "SI Kumar",
            metadata: null,
          },
          {
            id: "t2",
            case_id: mockCaseId,
            event_type: "investigation_started",
            title: "Investigation Started",
            description: "Case assigned to investigation team",
            timestamp: "2026-01-15T16:00:00Z",
            actor: "ACP Patil",
            metadata: null,
          },
        ]),
      })
    })

    await page.route(`**/api/v1/cases/${mockCaseId}/evidence`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: "e1",
            fir_id: mockCaseId,
            evidence_type: "Physical",
            name: "CCTV footage",
            description: "Security camera recording from City Mall",
            is_forensically_analyzed: true,
            is_admissible: true,
          },
        ]),
      })
    })

    await page.goto(`/cases/${mockCaseId}`)
    await expect(page.getByRole("heading", { name: /robbery detail/i })).toBeVisible({ timeout: 10000 })
    await expect(page.getByText(/Incident Reported/i)).toBeVisible()
    await expect(page.getByText(/CCTV footage/i)).toBeVisible()
  })
})
