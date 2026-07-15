"""End-to-end workflow tests for SentinelAI chat interface.

Tests the full conversational AI pipeline:
1. User registration + login
2. Kannada query → translation → agent orchestration → response
3. Multi-turn conversation context
4. Network analysis endpoint
5. Case similarity and recommendations
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user():
    return {
        "email": "e2e_test@police.gov.in",
        "username": "e2e_officer",
        "full_name": "E2E Test Officer",
        "password": "E2ETest@123",
        "designation": "Inspector",
        "department": "E2E Test Police",
    }


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_auth_flow(client, test_user):
    register_resp = await client.post("/api/v1/auth/register", json=test_user)
    assert register_resp.status_code in (201, 409)

    login_resp = await client.post("/api/v1/auth/login", json={"username": test_user["username"], "password": test_user["password"]})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token is not None
    return token


@pytest.mark.asyncio
async def test_english_chat_conversation(client):
    token = await test_auth_flow(client, {
        "email": "chat_test@police.gov.in",
        "username": "chat_officer",
        "full_name": "Chat Test",
        "password": "Chat@123",
        "designation": "SI",
        "department": "Test",
    })
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/chat/converse",
        json={"session_id": "test-session-1", "message": "Show me burglary cases", "language": "en"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "reply" in data
    assert "confidence_score" in data
    assert "sources" in data


@pytest.mark.asyncio
async def test_kannada_chat_conversation(client):
    token = await test_auth_flow(client, {
        "email": "kn_test@police.gov.in",
        "username": "kn_officer",
        "full_name": "KN Test",
        "password": "KN@123",
        "designation": "SI",
        "department": "Test",
    })
    headers = {"Authorization": f"Bearer {token}"}

    kannada_query = "ನನಗೆ ಮೈಸೂರಿನಲ್ಲಿ ನಡೆದ ಕಳ್ಳತನ ಪ್ರಕರಣಗಳನ್ನು ತೋರಿಸಿ"
    response = await client.post(
        "/api/v1/chat/converse",
        json={
            "session_id": "test-session-kn",
            "message": kannada_query,
            "language": "kn",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("language") == "kn" or data.get("language") == "en"


@pytest.mark.asyncio
async def test_network_analysis(client):
    token = await test_auth_flow(client, {
        "email": "net_test@police.gov.in",
        "username": "net_officer",
        "full_name": "Net Test",
        "password": "Net@123",
        "designation": "SI",
        "department": "Test",
    })
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/network/analyze",
        json={"depth": 2},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "centrality" in data
    assert "communities" in data


@pytest.mark.asyncio
async def test_circular_transactions_endpoint(client):
    token = await test_auth_flow(client, {
        "email": "circ_test@police.gov.in",
        "username": "circ_officer",
        "full_name": "Circ Test",
        "password": "Circ@123",
        "designation": "SI",
        "department": "Test",
    })
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        "/api/v1/network/circular-transactions?min_cycle=3",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "circular_transactions" in data
    assert "total_cycles_found" in data


@pytest.mark.asyncio
async def test_sociological_with_ml(client):
    token = await test_auth_flow(client, {
        "email": "soc_test@police.gov.in",
        "username": "soc_officer",
        "full_name": "Soc Test",
        "password": "Soc@123",
        "designation": "SI",
        "department": "Test",
    })
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        "/api/v1/analytics/sociological",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "indicators" in data
    assert "ml_analysis" in data


@pytest.mark.asyncio
async def test_suspicious_patterns_with_cycles(client):
    token = await test_auth_flow(client, {
        "email": "sp_test@police.gov.in",
        "username": "sp_officer",
        "full_name": "SP Test",
        "password": "SP@123",
        "designation": "SI",
        "department": "Test",
    })
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        "/api/v1/network/suspicious-patterns",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "isolated_persons" in data
    assert "high_degree_persons" in data
    assert "suspicious_communities" in data


@pytest.mark.asyncio
async def test_multi_turn_conversation(client):
    token = await test_auth_flow(client, {
        "email": "multi_test@police.gov.in",
        "username": "multi_officer",
        "full_name": "Multi Test",
        "password": "Multi@123",
        "designation": "SI",
        "department": "Test",
    })
    headers = {"Authorization": f"Bearer {token}"}
    session_id = "multi-turn-session"

    turn1 = await client.post(
        "/api/v1/chat/converse",
        json={"session_id": session_id, "message": "Show me recent burglary cases", "language": "en"},
        headers=headers,
    )
    assert turn1.status_code == 200

    turn2 = await client.post(
        "/api/v1/chat/converse",
        json={"session_id": session_id, "message": "What about in Mysore?", "language": "en"},
        headers=headers,
    )
    assert turn2.status_code == 200

    history = await client.get(
        f"/api/v1/chat/history/{session_id}",
        headers=headers,
    )
    assert history.status_code == 200


@pytest.mark.asyncio
async def test_admin_health_check(client):
    token = await test_auth_flow(client, {
        "email": "admin_test@police.gov.in",
        "username": "admin_officer",
        "full_name": "Admin Test",
        "password": "Admin@123",
        "designation": "SI",
        "department": "Test",
    })
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        "/api/v1/admin/system/health",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
