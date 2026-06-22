from typing import TypedDict, List, Optional, Dict, Any
from enum import Enum


class IntentType(str, Enum):
    SQL_QUERY = "sql_query"
    GRAPH_QUERY = "graph_query"
    RAG_SEARCH = "rag_search"
    ANALYTICS = "analytics"
    PROFILE = "profile"
    FORECAST = "forecast"
    GENERAL = "general"


class AgentState(TypedDict):
    # Input
    query: str
    session_id: str
    user_id: str
    user_role: str
    language: str

    # Context
    context: List[Dict[str, Any]]

    # Coordinator
    intent: Optional[IntentType]
    intent_confidence: float
    intent_reasoning: str

    # SQL Agent
    sql_query: Optional[str]
    sql_result: Optional[List[Dict[str, Any]]]
    sql_error: Optional[str]

    # Graph Agent
    cypher_query: Optional[str]
    graph_result: Optional[List[Dict[str, Any]]]
    graph_error: Optional[str]

    # RAG Agent
    rag_query: Optional[str]
    rag_result: Optional[List[Dict[str, Any]]]
    rag_error: Optional[str]

    # Analytics Agent
    analytics_result: Optional[Dict[str, Any]]
    analytics_error: Optional[str]

    # Profiling Agent
    profiling_result: Optional[Dict[str, Any]]
    profiling_error: Optional[str]

    # Forecast Agent
    forecast_result: Optional[Dict[str, Any]]
    forecast_error: Optional[str]

    # Output
    response: Optional[str]
    sources: List[Dict[str, Any]]
    confidence_score: float
    reasoning_chain: List[str]
    visualizations: List[Dict[str, Any]]
    processing_time_ms: int
