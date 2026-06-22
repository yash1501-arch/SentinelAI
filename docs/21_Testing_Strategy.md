# SENTINEL AI — Testing Strategy

## Test Pyramid

```
        ╱╲
       ╱  ╲         E2E Tests (5%)
      ╱    ╲     ── Playwright, API integration
     ╱      ╲
    ╱────────╲
   ╱          ╲    Integration Tests (25%)
  ╱            ╲ ── API tests, DB queries, Neo4j queries
 ╱──────────────╲
╱                  ╲  Unit Tests (70%)
╱   Models, Security,  ╲
╱   Schemas, Helpers    ╲
╱────────────────────────╲
```

## Test Configuration

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    asyncio: async tests
    integration: integration tests
    slow: tests that take > 5s
```

## Unit Tests

### Coverage Targets: 80%+

| Module | Tests | Focus |
|--------|-------|-------|
| Core Security | test_security.py | JWT, password hashing, token validation |
| Models | test_models.py | ORM creation, relationships, constraints |
| Schemas | test_schemas.py | Pydantic validation, serialization |
| Helpers | test_helpers.py | Date parsing, chunking, PII masking |
| Services | test_services.py | Neo4j, Qdrant, Embedding |

### Example: Security Tests
```python
class TestSecurity:
    def test_password_hashing(self):
        hashed = get_password_hash("Secure@123")
        assert verify_password("Secure@123", hashed)
        assert not verify_password("wrong", hashed)

    def test_access_token(self):
        token = create_access_token({"sub": "user123"})
        decoded = decode_token(token)
        assert decoded["sub"] == "user123"
        assert decoded["type"] == "access"
```

## Integration Tests

| Test File | What It Tests |
|-----------|---------------|
| test_api_auth.py | Registration, login, refresh, protected endpoints |
| test_api_cases.py | CRUD operations, filtering, pagination |
| test_api_chat.py | Conversation flow, context, multi-turn |
| test_api_network.py | Graph queries, community detection |
| test_api_analytics.py | Trends, hotspots, forecasts |

### Example: API Auth Tests
```python
@pytest.mark.asyncio
async def test_login_valid_credentials(client):
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_protected_endpoint(client):
    response = await client.get("/api/v1/cases/")
    assert response.status_code == 401
```

## E2E Tests (Playwright)

```typescript
// Frontend E2E
test('investigator can search cases', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="username"]', 'investigator1');
    await page.fill('[name="password"]', 'Secure@123');
    await page.click('button[type="submit"]');
    await page.goto('/chat');
    await page.fill('[placeholder="Ask a question..."]', 'Show burglaries in Mysore');
    await page.click('button[aria-label="Send"]');
    await expect(page.locator('.message-response')).toContainText('burglary');
});
```

## Test Data

```python
# conftest.py provides mock fixtures
@pytest.fixture
def sample_fir():
    return {
        "fir_number": "FIR-TEST-001",
        "police_station": "Test Station",
        "district": "Mysore",
        "brief_fact": "Test FIR for unit testing"
    }
```

## CI Integration

```yaml
# GitHub Actions workflow
steps:
  - name: Run tests
    run: |
      pytest tests/unit -v --cov=app --cov-report=term-missing
      pytest tests/integration -v --cov=app --cov-append
```
