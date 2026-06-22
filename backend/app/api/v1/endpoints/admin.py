from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.config import settings
from app.models.user import User, Role, Permission
from app.models.analytics import AuditLog
from app.schemas.user import UserRead, RoleRead
from app.schemas.analytics import AuditLogRead

router = APIRouter()


@router.get("/users", response_model=list[UserRead])
async def list_users(
    current_user: User = Depends(require_role("admin", "supervisor")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
    )
    return result.scalars().all()


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    await db.commit()
    return {
        "status": "success",
        "user_id": user_id,
        "is_active": user.is_active,
        "message": f"User {'deactivated' if not user.is_active else 'activated'} successfully",
    }


@router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Role).order_by(Role.name))
    return result.scalars().all()


@router.get("/audit-logs", response_model=list[AuditLogRead])
async def get_audit_logs(
    page: int = 1,
    per_page: int = 50,
    current_user: User = Depends(require_role("admin", "supervisor")),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page
    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    return result.scalars().all()


@router.get("/system/health")
async def system_health(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    services = {
        "postgresql": "unhealthy",
        "neo4j": "unhealthy",
        "qdrant": "unhealthy",
        "redis": "unhealthy",
    }

    try:
        await db.execute(select(func.now()))
        services["postgresql"] = "healthy"
    except Exception:
        pass

    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        driver.verify_connectivity()
        services["neo4j"] = "healthy"
        driver.close()
    except Exception:
        pass

    qdrant_host = settings.QDRANT_HOST
    qdrant_port = settings.QDRANT_PORT
    qdrant_key = settings.QDRANT_API_KEY
    try:
        from qdrant_client import QdrantClient
        if qdrant_key:
            qdrant = QdrantClient(url=f"https://{qdrant_host}:{qdrant_port}", api_key=qdrant_key)
        else:
            qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
        qdrant.get_collections()
        services["qdrant"] = "healthy"
    except Exception:
        pass

    try:
        import redis as redis_lib
        r = redis_lib.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            socket_connect_timeout=2,
        )
        r.ping()
        services["redis"] = "healthy"
        r.close()
    except Exception:
        pass

    overall = "healthy" if all(s == "healthy" for s in services.values()) else "degraded"
    return {"status": overall, "services": services}
