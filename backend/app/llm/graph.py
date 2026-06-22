from langgraph.graph import StateGraph, END
from app.llm.state import AgentState, IntentType
from app.api.v1.agents.coordinator import CoordinatorAgent
from app.api.v1.agents.sql_agent import SQLAgent
from app.api.v1.agents.graph_agent import GraphAgent
from app.api.v1.agents.rag_agent import RAGAgent
from app.api.v1.agents.analytics_agent import AnalyticsAgent
from app.api.v1.agents.profiling_agent import ProfilingAgent
from app.api.v1.agents.forecast_agent import ForecastAgent
from app.api.v1.agents.summarizer_agent import SummarizerAgent

coordinator = CoordinatorAgent()
sql_agent = SQLAgent()
graph_agent = GraphAgent()
rag_agent = RAGAgent()
analytics_agent = AnalyticsAgent()
profiling_agent = ProfilingAgent()
forecast_agent = ForecastAgent()
summarizer = SummarizerAgent()


def route_after_coordinator(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == IntentType.SQL_QUERY:
        return "sql_agent"
    elif intent == IntentType.GRAPH_QUERY:
        return "graph_agent"
    elif intent == IntentType.RAG_SEARCH:
        return "rag_agent"
    elif intent == IntentType.ANALYTICS:
        return "analytics_agent"
    elif intent == IntentType.PROFILE:
        return "profiling_agent"
    elif intent == IntentType.FORECAST:
        return "forecast_agent"
    else:
        return "summarizer"


def route_after_specialist(state: AgentState) -> str:
    return "summarizer"


def build_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("coordinator", coordinator.run)
    workflow.add_node("sql_agent", sql_agent.run)
    workflow.add_node("graph_agent", graph_agent.run)
    workflow.add_node("rag_agent", rag_agent.run)
    workflow.add_node("analytics_agent", analytics_agent.run)
    workflow.add_node("profiling_agent", profiling_agent.run)
    workflow.add_node("forecast_agent", forecast_agent.run)
    workflow.add_node("summarizer", summarizer.run)

    workflow.set_entry_point("coordinator")

    workflow.add_conditional_edges(
        "coordinator",
        route_after_coordinator,
        {
            "sql_agent": "sql_agent",
            "graph_agent": "graph_agent",
            "rag_agent": "rag_agent",
            "analytics_agent": "analytics_agent",
            "profiling_agent": "profiling_agent",
            "forecast_agent": "forecast_agent",
            "summarizer": "summarizer",
        },
    )

    for agent in ["sql_agent", "graph_agent", "rag_agent", "analytics_agent", "profiling_agent", "forecast_agent"]:
        workflow.add_conditional_edges(agent, route_after_specialist, {"summarizer": "summarizer"})

    workflow.add_edge("summarizer", END)

    return workflow.compile()


agent_graph = build_agent_graph()
