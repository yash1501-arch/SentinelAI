import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4


pytestmark = pytest.mark.asyncio


class TestCoordinatorAgent:
    """Tests for the Coordinator Agent - intent classification and routing."""

    @patch("app.api.v1.agents.coordinator.client")
    async def test_sql_query_intent(self, mock_client, base_state):
        from app.api.v1.agents.coordinator import CoordinatorAgent
        from app.llm.state import IntentType

        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "sql_query", "confidence": 0.95, "reasoning": "User asking for case count"}'
            ))]
        ))

        state = {**base_state, "query": "how many cases were registered last month?"}
        agent = CoordinatorAgent()
        result = await agent.run(state)

        assert result["intent"] == IntentType.SQL_QUERY
        assert result["intent_confidence"] >= 0.9
        assert result["processing_time_ms"] >= 0

    @patch("app.api.v1.agents.coordinator.client")
    async def test_graph_query_intent(self, mock_client, base_state):
        from app.api.v1.agents.coordinator import CoordinatorAgent
        from app.llm.state import IntentType

        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "graph_query", "confidence": 0.92, "reasoning": "User asking about connections"}'
            ))]
        ))

        state = {**base_state, "query": "show me the gang network connections"}
        agent = CoordinatorAgent()
        result = await agent.run(state)

        assert result["intent"] == IntentType.GRAPH_QUERY

    @patch("app.api.v1.agents.coordinator.client")
    async def test_rag_search_intent(self, mock_client, base_state):
        from app.api.v1.agents.coordinator import CoordinatorAgent
        from app.llm.state import IntentType

        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "rag_search", "confidence": 0.88, "reasoning": "Similar case search"}'
            ))]
        ))

        state = {**base_state, "query": "find similar cases to FIR-2024-123"}
        agent = CoordinatorAgent()
        result = await agent.run(state)

        assert result["intent"] == IntentType.RAG_SEARCH

    @patch("app.api.v1.agents.coordinator.client")
    async def test_analytics_intent(self, mock_client, base_state):
        from app.api.v1.agents.coordinator import CoordinatorAgent
        from app.llm.state import IntentType

        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "analytics", "confidence": 0.93, "reasoning": "Trend analysis requested"}'
            ))]
        ))

        state = {**base_state, "query": "what are the crime trends this quarter?"}
        agent = CoordinatorAgent()
        result = await agent.run(state)

        assert result["intent"] == IntentType.ANALYTICS

    @patch("app.api.v1.agents.coordinator.client")
    async def test_profile_intent(self, mock_client, base_state):
        from app.api.v1.agents.coordinator import CoordinatorAgent
        from app.llm.state import IntentType

        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "profile", "confidence": 0.91, "reasoning": "Offender profiling"}'
            ))]
        ))

        state = {**base_state, "query": "profile suspect Rajesh Kumar"}
        agent = CoordinatorAgent()
        result = await agent.run(state)

        assert result["intent"] == IntentType.PROFILE

    @patch("app.api.v1.agents.coordinator.client")
    async def test_forecast_intent(self, mock_client, base_state):
        from app.api.v1.agents.coordinator import CoordinatorAgent
        from app.llm.state import IntentType

        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "forecast", "confidence": 0.90, "reasoning": "Predictive analysis"}'
            ))]
        ))

        state = {**base_state, "query": "predict crime trends for next month"}
        agent = CoordinatorAgent()
        result = await agent.run(state)

        assert result["intent"] == IntentType.FORECAST

    @patch("app.api.v1.agents.coordinator.client")
    async def test_general_intent(self, mock_client, base_state):
        from app.api.v1.agents.coordinator import CoordinatorAgent
        from app.llm.state import IntentType

        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='{"intent": "general", "confidence": 0.99, "reasoning": "Greeting"}'
            ))]
        ))

        state = {**base_state, "query": "hello"}
        agent = CoordinatorAgent()
        result = await agent.run(state)

        assert result["intent"] == IntentType.GENERAL

    @patch("app.api.v1.agents.coordinator.client")
    async def test_fallback_on_error(self, mock_client, base_state):
        from app.api.v1.agents.coordinator import CoordinatorAgent
        from app.llm.state import IntentType

        mock_client.chat.completions.create.side_effect = Exception("API error")

        state = {**base_state, "query": "test query"}
        agent = CoordinatorAgent()
        result = await agent.run(state)

        assert result["intent"] == IntentType.GENERAL
        assert result["intent_confidence"] == 0.5
        assert "Fallback" in result["intent_reasoning"]
