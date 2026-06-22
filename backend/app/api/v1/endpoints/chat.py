import time
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.analytics import ConversationHistory, ConversationRole
from app.schemas.analytics import ConversationRequest, ConversationResponse, ConversationHistoryRead
from app.llm.graph import agent_graph
from app.llm.state import AgentState
from loguru import logger

router = APIRouter()


@router.post("/converse", response_model=ConversationResponse)
async def converse(
    request: ConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start_time = time.time()

    context = await _get_recent_context(db, current_user.id, request.session_id)

    await _save_message(db, current_user.id, request.session_id,
                        ConversationRole.USER, request.message, request.language)

    user_role = "investigator"
    if current_user.roles:
        user_role = current_user.roles[0].name if current_user.roles else "investigator"

    initial_state: AgentState = {
        "query": request.message,
        "session_id": request.session_id,
        "user_id": str(current_user.id),
        "user_role": user_role,
        "language": request.language or "en",
        "context": context,
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

    try:
        final_state = await agent_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Agent orchestration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

    processing_ms = int((time.time() - start_time) * 1000)

    await _save_message(db, current_user.id, request.session_id,
                        ConversationRole.ASSISTANT, final_state.get("response", "I could not process that request."),
                        request.language)

    visualizations = _build_visualizations(final_state)

    return ConversationResponse(
        session_id=request.session_id,
        reply=final_state.get("response", "No response generated."),
        language=request.language or "en",
        sources=final_state.get("sources", []),
        confidence_score=final_state.get("confidence_score", 0.5),
        processing_time_ms=processing_ms,
        reasoning_chain=final_state.get("reasoning_chain", []),
        visualizations=visualizations,
    )


@router.get("/history/{session_id}", response_model=list[ConversationHistoryRead])
async def get_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConversationHistory)
        .where(
            ConversationHistory.session_id == session_id,
            ConversationHistory.user_id == current_user.id,
        )
        .order_by(ConversationHistory.created_at.asc())
    )
    return result.scalars().all()


@router.delete("/history/{session_id}")
async def clear_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(ConversationHistory).where(
            ConversationHistory.session_id == session_id,
            ConversationHistory.user_id == current_user.id,
        )
    )
    await db.commit()
    return {"message": f"Conversation {session_id} deleted"}


async def _get_recent_context(db: AsyncSession, user_id: uuid.UUID, session_id: str, limit: int = 5) -> list:
    result = await db.execute(
        select(ConversationHistory)
        .where(
            ConversationHistory.session_id == session_id,
            ConversationHistory.user_id == user_id,
        )
        .order_by(ConversationHistory.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [
        {"role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role),
         "content": msg.content}
        for msg in reversed(messages)
    ]


async def _save_message(db: AsyncSession, user_id: uuid.UUID, session_id: str,
                         role: ConversationRole, content: str, language: str):
    msg = ConversationHistory(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
        language=language,
    )
    db.add(msg)
    await db.commit()


def _build_visualizations(state: AgentState) -> list:
    charts = []
    sql_result = state.get("sql_result", [])
    analytics_result = state.get("analytics_result", {})

    if sql_result and len(sql_result) > 1:
        charts.append({
            "type": "table",
            "title": "Query Results",
            "data": sql_result[:20],
        })

    if analytics_result:
        trends = analytics_result.get("trends")
        if trends:
            charts.append({
                "type": "line",
                "title": "Crime Trends by Month",
                "data": trends,
            })

        patterns = analytics_result.get("patterns", {})
        by_day = patterns.get("by_day", [])
        if by_day:
            charts.append({
                "type": "bar",
                "title": "Crimes by Day of Week",
                "data": by_day,
            })

        hotspots = analytics_result.get("hotspots", [])
        if hotspots:
            charts.append({
                "type": "map",
                "title": "Crime Hotspots",
                "data": hotspots,
            })

    profiling = state.get("profiling_result", {})
    if profiling and "risk_score" in profiling:
        charts.append({
            "type": "gauge",
            "title": "Risk Score",
            "data": profiling,
        })

    return charts
