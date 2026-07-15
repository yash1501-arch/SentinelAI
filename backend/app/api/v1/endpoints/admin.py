from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, Role
from app.models.analytics import AuditLog
from app.schemas.user import UserRead, RoleRead
from app.schemas.analytics import AuditLogRead

router = APIRouter()


class CreateUserRequest(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    role: str = "investigator"
    department: Optional[str] = None
    designation: Optional[str] = None
    badge_number: Optional[str] = None
    jurisdiction: Optional[str] = None


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    jurisdiction: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


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


@router.post("/users", response_model=UserRead)
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new user (admin only)."""
    # Check if user already exists
    existing = await db.execute(
        select(User).where((User.email == request.email) | (User.username == request.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User with this email or username already exists")

    # Get role
    role_result = await db.execute(select(Role).where(Role.name == request.role))
    role = role_result.scalar_one_or_none()

    new_user = User(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        hashed_password=get_password_hash(request.password),
        department=request.department,
        designation=request.designation,
        badge_number=request.badge_number,
        jurisdiction=request.jurisdiction,
        is_active=True,
    )
    if role:
        new_user.roles = [role]

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Update user details (admin only)."""
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.full_name is not None:
        user.full_name = request.full_name
    if request.department is not None:
        user.department = request.department
    if request.designation is not None:
        user.designation = request.designation
    if request.jurisdiction is not None:
        user.jurisdiction = request.jurisdiction
    if request.is_active is not None:
        user.is_active = request.is_active

    if request.role:
        role_result = await db.execute(select(Role).where(Role.name == request.role))
        role = role_result.scalar_one_or_none()
        if role:
            user.roles = [role]

    await db.commit()
    return {"status": "success", "message": f"User {user_id} updated"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user (admin only). Soft-delete by deactivation."""
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if str(current_user.id) == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    return {"status": "success", "message": f"User {user_id} deactivated"}


@router.put("/users/{user_id}/role")
async def assign_role(
    user_id: str,
    role_name: str,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Assign a role to a user."""
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role_result = await db.execute(select(Role).where(Role.name == role_name))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")

    user.roles = [role]
    await db.commit()
    return {"status": "success", "message": f"Assigned role '{role_name}' to user {user_id}"}


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
