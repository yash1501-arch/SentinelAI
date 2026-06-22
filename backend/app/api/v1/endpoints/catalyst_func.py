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
        "appsail": "checking",
        "datastore": "checking",
        "neo4j_aura": "checking",
        "qdrant_cloud": "checking",
        "redis": "checking",
        "openai": "checking",
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            health = await client.get(f"http://localhost:8000/health")
            if health.status_code == 200:
                services["appsail"] = "healthy"
    except Exception as e:
        services["appsail"] = f"unhealthy: {str(e)[:50]}"
    return services


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
