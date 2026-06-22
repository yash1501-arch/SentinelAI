import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def client():
    with patch("app.main.init_db", AsyncMock()):
        from app.main import app
        from fastapi.testclient import TestClient
        app.dependency_overrides = {}
        with TestClient(app) as c:
            yield c


def _mock_auth(override_user=True):
    """Patch get_current_user dependency to return a mock user."""
    from app.core.dependencies import get_current_user
    user = MagicMock()
    user.id = uuid4()
    user.email = "admin@test.gov.in"
    user.username = "admin"
    user.full_name = "Admin User"
    user.is_active = True
    user.is_superuser = True
    user.roles = []
    user.preferred_language = "en"

    def mock_get_current_user():
        return user

    return {get_current_user: mock_get_current_user}


def test_admin_system_health_unauthenticated(client):
    response = client.get("/api/v1/admin/system/health")
    assert response.status_code == 401





def test_export_pdf_unauthenticated(client):
    response = client.post("/api/v1/export/pdf", json={
        "session_id": "test-session",
        "case_ids": [],
        "include_charts": False,
    })
    assert response.status_code == 401


def test_export_pdf_authenticated(client):
    from app.main import app
    overrides = _mock_auth()
    app.dependency_overrides.update(overrides)
    try:
        response = client.post("/api/v1/export/pdf", json={
            "session_id": "test-session",
            "case_ids": [],
            "include_charts": False,
        })
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    finally:
        app.dependency_overrides.clear()


def test_export_csv_cases_authenticated(client):
    from app.main import app
    overrides = _mock_auth()
    app.dependency_overrides.update(overrides)
    try:
        response = client.post("/api/v1/export/csv/cases")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        body = response.text
        assert "Crime Type" in body
    finally:
        app.dependency_overrides.clear()


def test_export_case_pdf_authenticated(client):
    from app.main import app
    overrides = _mock_auth()
    app.dependency_overrides.update(overrides)
    try:
        case_id = str(uuid4())
        response = client.post(f"/api/v1/export/pdf/case/{case_id}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
    finally:
        app.dependency_overrides.clear()


def test_offender_profiles_unauthenticated(client):
    response = client.get("/api/v1/analytics/offender-profiles")
    assert response.status_code == 401


def test_offender_profiles_authenticated(client):
    from app.main import app
    overrides = _mock_auth()
    app.dependency_overrides.update(overrides)
    try:
        response = client.get("/api/v1/analytics/offender-profiles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "archetype" in data[0]
    finally:
        app.dependency_overrides.clear()


def test_analytics_sociological_authenticated(client):
    from app.main import app
    overrides = _mock_auth()
    app.dependency_overrides.update(overrides)
    try:
        response = client.get("/api/v1/analytics/sociological")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    finally:
        app.dependency_overrides.clear()
