import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.skip(reason="requires PostgreSQL connection")
@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.gov.in",
            "username": "test_officer",
            "full_name": "Test Officer",
            "password": "Secure@123",
            "designation": "Sub Inspector",
            "department": "Mysore Police",
        },
    )
    assert response.status_code in (201, 409)


@pytest.mark.skip(reason="requires PostgreSQL connection")
@pytest.mark.asyncio
async def test_login_invalid(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    response = await client.get("/api/v1/cases/")
    assert response.status_code == 403 or response.status_code == 401
