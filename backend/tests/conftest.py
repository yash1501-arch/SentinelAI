import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


@pytest.fixture
def mock_openai():
    with patch("openai.AsyncOpenAI") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_openai_chat(mock_openai):
    async def create_response(content: str):
        mock_msg = MagicMock()
        mock_msg.content = content
        mock_choice = MagicMock()
        mock_choice.message = mock_msg
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]
        return mock_resp

    mock_openai.chat.completions.create = AsyncMock(side_effect=create_response)
    yield mock_openai


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_current_user():
    user = MagicMock()
    user.id = uuid4()
    user.email = "admin@test.gov.in"
    user.username = "admin"
    user.full_name = "Admin User"
    user.is_active = True
    user.is_superuser = True
    user.roles = []
    user.preferred_language = "en"
    return user


@pytest.fixture
def base_state():
    return {
        "query": "",
        "session_id": str(uuid4()),
        "user_id": str(uuid4()),
        "user_role": "investigator",
        "language": "en",
        "context": [],
        "intent": None,
        "intent_confidence": 0.0,
        "intent_reasoning": "",
        "sql_query": None,
        "sql_result": None,
        "sql_error": None,
        "cypher_query": None,
        "graph_result": None,
        "graph_error": None,
        "rag_query": None,
        "rag_result": None,
        "rag_error": None,
        "analytics_result": None,
        "analytics_error": None,
        "profiling_result": None,
        "profiling_error": None,
        "forecast_result": None,
        "forecast_error": None,
        "response": None,
        "sources": [],
        "confidence_score": 0.0,
        "reasoning_chain": [],
        "visualizations": [],
        "processing_time_ms": 0,
    }
