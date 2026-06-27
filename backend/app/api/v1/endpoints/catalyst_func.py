from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.core.config import settings
import httpx
from loguru import logger

router = APIRouter()


@router.get("/config")
async def get_catalyst_config(
    current_user: User = Depends(require_role("admin")),
):
    return {
        "project_id": settings.CATALYST_PROJECT_ID,
        "region": settings.CATALYST_REGION,
        "appsail": True,
        "datastore": True,
        "functions": True,
        "scheduler": True,
        "circuits": True,
        "stratus": True,
    }


@router.get("/services/status")
async def service_status(
    current_user: User = Depends(get_current_user),
):
    services = {
        "appsail": "healthy",
        "datastore": "checking",
        "neo4j_aura": "checking",
        "qdrant_cloud": "checking",
        "redis": "checking",
        "openai": "checking",
    }

    # Check PostgreSQL
    try:
        from app.core.database import async_session_factory
        from sqlalchemy import text
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        services["datastore"] = "healthy"
    except Exception as e:
        services["datastore"] = f"unhealthy: {str(e)[:50]}"

    # Check Neo4j
    try:
        from app.services.neo4j_service import Neo4jService
        driver = await Neo4jService.get_driver()
        if driver:
            services["neo4j_aura"] = "healthy"
        else:
            services["neo4j_aura"] = "not configured"
    except Exception as e:
        services["neo4j_aura"] = f"unhealthy: {str(e)[:50]}"

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, timeout=5)
        client.get_collections()
        services["qdrant_cloud"] = "healthy"
    except Exception as e:
        services["qdrant_cloud"] = f"unhealthy: {str(e)[:50]}"

    # Check Redis
    try:
        from app.services.redis_service import RedisService
        redis_client = await RedisService.get_client()
        if redis_client:
            await redis_client.ping()
            services["redis"] = "healthy"
        else:
            services["redis"] = "not connected"
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)[:50]}"

    # Check OpenAI/Groq
    try:
        from app.services.openai_client import create_openai_client
        client = create_openai_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        services["openai"] = "healthy"
    except Exception as e:
        services["openai"] = f"unhealthy: {str(e)[:50]}"

    return services


@router.post("/sync/neo4j")
async def trigger_neo4j_sync(
    current_user: User = Depends(require_role("admin")),
):
    """Manually trigger Neo4j graph sync."""
    from app.services.sync_service import Neo4jSyncService
    result = await Neo4jSyncService.full_sync()
    return {"status": "success", **result}


@router.post("/sync/embeddings")
async def trigger_embedding_sync(
    current_user: User = Depends(require_role("admin")),
):
    """Manually trigger Qdrant embedding sync."""
    from app.services.sync_service import EmbeddingSyncService
    result = await EmbeddingSyncService.sync_embeddings()
    return {"status": "success", **result}


@router.post("/ml/train/{model_name}")
async def trigger_ml_training(
    model_name: str,
    current_user: User = Depends(require_role("admin")),
):
    """Manually trigger ML model training."""
    if model_name == "forecast":
        from app.ml.forecasting import train_model
        result = await train_model()
    elif model_name == "profiling":
        from app.ml.profiling import train_model
        result = await train_model()
    elif model_name == "financial":
        from app.ml.financial import train_model
        result = await train_model()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model_name}")

    return {"status": "success", "model": model_name, "metrics": result}


@router.post("/functions/invoke/{function_name}")
async def invoke_catalyst_function(
    function_name: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    from app.core.config import settings
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"https://{settings.CATALYST_PROJECT_ID}.functions.catalyst.zoho.com/{function_name}",
                json=payload,
                headers={"Authorization": f"Bearer {current_user.id}"},
            )
            return resp.json()
    except Exception as e:
        logger.error(f"Catalyst function invocation failed: {e}")
        raise HTTPException(status_code=502, detail=f"Function invocation failed: {str(e)[:100]}")
