import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.models.user import User, Role, Permission, RolePermission
from app.models.crime import (
    CrimeType, CrimeCategory,
)


SEED_PERMISSIONS = [
    {"name": "cases:read", "resource": "cases", "action": "read", "description": "Read case records"},
    {"name": "cases:write", "resource": "cases", "action": "write", "description": "Create/update case records"},
    {"name": "cases:delete", "resource": "cases", "action": "delete", "description": "Delete case records"},
    {"name": "evidence:read", "resource": "evidence", "action": "read", "description": "Read evidence records"},
    {"name": "evidence:write", "resource": "evidence", "action": "write", "description": "Create/update evidence"},
    {"name": "analytics:read", "resource": "analytics", "action": "read", "description": "View analytics"},
    {"name": "analytics:export", "resource": "analytics", "action": "export", "description": "Export analytics"},
    {"name": "network:read", "resource": "network", "action": "read", "description": "View network analysis"},
    {"name": "forecast:read", "resource": "forecast", "action": "read", "description": "View crime forecasts"},
    {"name": "profiles:read", "resource": "profiles", "action": "read", "description": "View offender profiles"},
    {"name": "users:read", "resource": "users", "action": "read", "description": "View user records"},
    {"name": "users:write", "resource": "users", "action": "write", "description": "Manage users"},
    {"name": "users:delete", "resource": "users", "action": "delete", "description": "Delete users"},
    {"name": "audit:read", "resource": "audit", "action": "read", "description": "View audit logs"},
    {"name": "system:admin", "resource": "system", "action": "admin", "description": "System administration"},
]

SEED_ROLES = [
    {
        "name": "investigator",
        "description": "Front-line investigating officer",
        "priority_level": "standard",
        "permissions": ["cases:read", "cases:write", "evidence:read", "evidence:write"],
    },
    {
        "name": "analyst",
        "description": "Crime data analyst",
        "priority_level": "standard",
        "permissions": ["cases:read", "analytics:read", "analytics:export", "network:read", "forecast:read", "profiles:read"],
    },
    {
        "name": "supervisor",
        "description": "Supervising officer",
        "priority_level": "elevated",
        "permissions": ["cases:read", "cases:write", "evidence:read", "evidence:write", "analytics:read", "network:read", "forecast:read", "profiles:read", "users:read"],
    },
    {
        "name": "policymaker",
        "description": "Policy decision maker",
        "priority_level": "elevated",
        "permissions": ["cases:read", "analytics:read", "analytics:export", "forecast:read"],
    },
    {
        "name": "admin",
        "description": "System administrator",
        "priority_level": "critical",
        "permissions": ["*"],
    },
]

SEED_CRIME_TYPES = [
    {"name": "Murder", "category": CrimeCategory.VIOLENT, "severity_level": 10, "is_cognizable": True, "is_bailable": False},
    {"name": "Attempt to Murder", "category": CrimeCategory.VIOLENT, "severity_level": 9, "is_cognizable": True, "is_bailable": False},
    {"name": "Robbery", "category": CrimeCategory.VIOLENT, "severity_level": 8, "is_cognizable": True, "is_bailable": False},
    {"name": "Burglary", "category": CrimeCategory.PROPERTY, "severity_level": 5, "is_cognizable": True, "is_bailable": True},
    {"name": "Theft", "category": CrimeCategory.PROPERTY, "severity_level": 4, "is_cognizable": True, "is_bailable": True},
    {"name": "Cyber Crime", "category": CrimeCategory.CYBER, "severity_level": 6, "is_cognizable": True, "is_bailable": True},
    {"name": "Fraud", "category": CrimeCategory.FINANCIAL, "severity_level": 6, "is_cognizable": True, "is_bailable": True},
    {"name": "Money Laundering", "category": CrimeCategory.FINANCIAL, "severity_level": 8, "is_cognizable": True, "is_bailable": False},
    {"name": "Drug Trafficking", "category": CrimeCategory.DRUG_RELATED, "severity_level": 9, "is_cognizable": True, "is_bailable": False},
    {"name": "Kidnapping", "category": CrimeCategory.VIOLENT, "severity_level": 9, "is_cognizable": True, "is_bailable": False},
    {"name": "Assault", "category": CrimeCategory.VIOLENT, "severity_level": 5, "is_cognizable": True, "is_bailable": True},
    {"name": "Domestic Violence", "category": CrimeCategory.VIOLENT, "severity_level": 6, "is_cognizable": True, "is_bailable": True},
    {"name": "Human Trafficking", "category": CrimeCategory.TRAFFICKING, "severity_level": 10, "is_cognizable": True, "is_bailable": False},
    {"name": "Organized Crime", "category": CrimeCategory.ORGANIZED, "severity_level": 10, "is_cognizable": True, "is_bailable": False},
    {"name": "Criminal Breach of Trust", "category": CrimeCategory.WHITE_COLLAR, "severity_level": 5, "is_cognizable": True, "is_bailable": True},
    {"name": "Cheating", "category": CrimeCategory.FINANCIAL, "severity_level": 4, "is_cognizable": True, "is_bailable": True},
    {"name": "Rioting", "category": CrimeCategory.VIOLENT, "severity_level": 6, "is_cognizable": True, "is_bailable": True},
    {"name": "Arson", "category": CrimeCategory.PROPERTY, "severity_level": 7, "is_cognizable": True, "is_bailable": False},
    {"name": "Extortion", "category": CrimeCategory.ORGANIZED, "severity_level": 7, "is_cognizable": True, "is_bailable": False},
    {"name": "Hate Crime", "category": CrimeCategory.VIOLENT, "severity_level": 8, "is_cognizable": True, "is_bailable": False},
]


async def seed_database(db: AsyncSession):
    existing_roles = await db.execute(Role.__table__.select().limit(1))
    if existing_roles.first():
        return

    permission_map = {}
    for perm_data in SEED_PERMISSIONS:
        perm = Permission(**perm_data)
        db.add(perm)
        permission_map[perm.name] = perm

    for crime_data in SEED_CRIME_TYPES:
        crime_type = CrimeType(**crime_data)
        db.add(crime_type)

    for role_data in SEED_ROLES:
        role = Role(
            name=role_data["name"],
            description=role_data["description"],
            priority_level=role_data["priority_level"],
        )
        db.add(role)
        await db.flush()

        if role_data["permissions"] == ["*"]:
            for perm in permission_map.values():
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                db.add(rp)
        else:
            for perm_name in role_data["permissions"]:
                if perm_name in permission_map:
                    rp = RolePermission(role_id=role.id, permission_id=permission_map[perm_name].id)
                    db.add(rp)

    admin_role = await db.execute(Role.__table__.select().where(Role.name == "admin"))
    admin_role = admin_role.scalar_one()

    admin_user = User(
        email="admin@sentinelai.gov.in",
        username="admin",
        full_name="System Administrator",
        hashed_password=get_password_hash("Admin@123"),
        designation="System Administrator",
        badge_number="ADM-001",
        department="Administration",
        is_superuser=True,
    )
    db.add(admin_user)
    await db.flush()

    await db.execute(user_roles.insert().values(
        user_id=admin_user.id,
        role_id=admin_role.id,
    ))

    await db.commit()
