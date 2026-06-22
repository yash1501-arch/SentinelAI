import os
import sys
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Ensure OpenAI doesn't fail at import time in agent tests
os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"

# Add ml-services, graph-services, and backend directories to sys.path
# so tests can import profiling.data, graph_analytics, app, etc.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
for child in ("ml-services", "graph-services", "backend"):
    p = str(PROJECT_ROOT / child)
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_current_user():
    user = MagicMock()
    user.id = "550e8400-e29b-41d4-a716-446655440000"
    user.email = "investigator@test.gov"
    user.username = "test_investigator"
    user.full_name = "Test Investigator"
    user.is_active = True
    user.is_superuser = False
    user.roles = []
    return user
