"""Agent graph integration tests — coordinator routing + specialist agent execution."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


from app.api.v1.agents import coordinator as _coordinator
from app.api.v1.agents import sql_agent as _sql_agent
from app.api.v1.agents import graph_agent as _graph_agent
from app.api.v1.agents import rag_agent as _rag_agent
from app.api.v1.agents import summarizer_agent as _summarizer_agent
from app.llm.graph import route_after_coordinator, route_after_specialist, agent_graph
from app.llm.state import IntentType


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


class TestCoordinatorRouting:
    def test_route_sql_query(self, base_state):
        state = {**base_state, "intent": IntentType.SQL_QUERY}
        assert route_after_coordinator(state) == "sql_agent"

    def test_route_graph_query(self, base_state):
        state = {**base_state, "intent": IntentType.GRAPH_QUERY}
        assert route_after_coordinator(state) == "graph_agent"

    def test_route_rag_search(self, base_state):
        state = {**base_state, "intent": IntentType.RAG_SEARCH}
        assert route_after_coordinator(state) == "rag_agent"

    def test_route_analytics(self, base_state):
        state = {**base_state, "intent": IntentType.ANALYTICS}
        assert route_after_coordinator(state) == "analytics_agent"

    def test_route_profile(self, base_state):
        state = {**base_state, "intent": IntentType.PROFILE}
        assert route_after_coordinator(state) == "profiling_agent"

    def test_route_forecast(self, base_state):
        state = {**base_state, "intent": IntentType.FORECAST}
        assert route_after_coordinator(state) == "forecast_agent"

    def test_route_general(self, base_state):
        state = {**base_state, "intent": IntentType.GENERAL}
        assert route_after_coordinator(state) == "summarizer"

    def test_route_none(self, base_state):
        state = {**base_state, "intent": None}
        assert route_after_coordinator(state) == "summarizer"

    def test_specialist_reroutes_to_summarizer(self, base_state):
        state = {**base_state, "sql_result": [{"id": 1, "count": 42}]}
        assert route_after_specialist(state) == "summarizer"


class TestAgentExecution:
    pytestmark = pytest.mark.asyncio
    @patch.object(_coordinator, "client", new_callable=MagicMock)
    async def test_coordinator_intent_classification(self, mock_client, base_state):
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "sql_query", "confidence": 0.95, "reasoning": "User asking for counts"}'
            ))]
        ))
        state = {**base_state, "query": "how many cases last month?"}
        agent = _coordinator.CoordinatorAgent()
        result = await agent.run(state)
        assert result["intent"] == IntentType.SQL_QUERY
        assert result["intent_confidence"] >= 0.9
        assert len(result["reasoning_chain"]) > 0

    @patch.object(_coordinator, "client", new_callable=MagicMock)
    async def test_coordinator_fallback(self, mock_client, base_state):
        mock_client.chat.completions.create.side_effect = Exception("API unavailable")
        state = {**base_state, "query": "hello"}
        agent = _coordinator.CoordinatorAgent()
        result = await agent.run(state)
        assert result["intent"] == IntentType.GENERAL
        assert result["intent_confidence"] == 0.5
        assert "Fallback" in result["intent_reasoning"]

    @patch.object(_sql_agent, "client", new_callable=MagicMock)
    @patch("app.api.v1.agents.sql_agent.async_session_factory")
    async def test_sql_agent_execution(self, mock_session, mock_client, base_state):
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="SELECT count(*) FROM crime_incidents"))]
        ))
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        state = {**base_state, "query": "how many cases?"}
        agent = _sql_agent.SQLAgent()
        result = await agent.run(state)
        assert result["sql_query"] is not None or result["sql_error"] is not None

    @patch.object(_graph_agent, "client", new_callable=MagicMock)
    async def test_graph_agent_execution(self, mock_client, base_state):
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="MATCH (p:Person) RETURN p LIMIT 10"))]
        ))
        state = {**base_state, "query": "find all persons"}
        agent = _graph_agent.GraphAgent()
        result = await agent.run(state)
        assert result["cypher_query"] is not None or result["graph_error"] is not None

    @patch.object(_rag_agent, "EmbeddingService")
    @patch.object(_rag_agent, "QdrantService")
    async def test_rag_agent_execution(self, mock_qdrant, mock_embedding, base_state):
        mock_embedding.return_value = MagicMock()
        mock_embedding.return_value.embed_query = AsyncMock(return_value=[0.1] * 384)
        mock_qdrant.return_value = MagicMock()
        mock_qdrant.return_value.search = AsyncMock(return_value=[{"id": "case-1", "score": 0.95}])
        state = {**base_state, "query": "find similar cases"}
        agent = _rag_agent.RAGAgent()
        result = await agent.run(state)
        assert result["rag_query"] is not None or result["rag_error"] is not None

    @patch.object(_summarizer_agent, "client", new_callable=MagicMock)
    async def test_summarizer_response(self, mock_client, base_state):
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content=(
                '{"response": "Found 42 cases.", "sources": [{"type": "sql", "detail": "cases table"}],'
                '"confidence_score": 0.9, "suggested_questions": ["Show details"]}'
            )))]
        ))
        state = {
            **base_state,
            "query": "how many cases?",
            "intent": IntentType.SQL_QUERY,
            "intent_confidence": 0.95,
            "sql_result": [{"count": 42}],
            "reasoning_chain": ["SQL Agent executed"],
        }
        agent = _summarizer_agent.SummarizerAgent()
        result = await agent.run(state)
        assert result["response"] is not None
        assert result["confidence_score"] > 0


class TestFullGraph:
    pytestmark = pytest.mark.asyncio
    @patch.object(_coordinator, "client", new_callable=MagicMock)
    @patch.object(_sql_agent, "client", new_callable=MagicMock)
    @patch.object(_summarizer_agent, "client", new_callable=MagicMock)
    async def test_full_graph_sql_flow(self, mock_summarizer, mock_sql, mock_coord, base_state):
        mock_coord.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "sql_query", "confidence": 0.95, "reasoning": "Count query"}'
            ))]
        ))
        mock_sql.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="SELECT count(*) FROM crime_incidents"))]
        ))
        mock_summarizer.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content=(
                '{"response": "Found 42 cases.", "sources": [], "confidence_score": 0.9, '
                '"suggested_questions": []}'
            )))]
        ))

        with patch("app.api.v1.agents.sql_agent.async_session_factory") as mock_sesh:
            mock_sesh.return_value.__aenter__.return_value = AsyncMock()
            state = {**base_state, "query": "how many cases?"}
            result = await agent_graph.ainvoke(state)

        assert result["intent"] is not None
        assert result["response"] is not None
        assert len(result["reasoning_chain"]) >= 2

    @patch.object(_coordinator, "client", new_callable=MagicMock)
    @patch.object(_summarizer_agent, "client", new_callable=MagicMock)
    async def test_full_graph_general_flow(self, mock_summarizer, mock_coord, base_state):
        mock_coord.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "general", "confidence": 0.99, "reasoning": "Greeting"}'
            ))]
        ))
        mock_summarizer.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content=(
                '{"response": "Hello! How can I help?", "sources": [], "confidence_score": 1.0, '
                '"suggested_questions": []}'
            )))]
        ))

        state = {**base_state, "query": "hello"}
        result = await agent_graph.ainvoke(state)
        assert result["intent"] is not None
        assert result["response"] is not None
