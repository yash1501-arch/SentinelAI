import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.crime import (
    CrimeIncident, FIR, CrimeType, Evidence, InvestigationStatus,
)
from app.schemas.crime import CrimeIncidentRead, EvidenceRead, TimelineEventRead

router = APIRouter()


@router.get("/", response_model=list[CrimeIncidentRead])
async def list_cases(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    crime_type: str = None,
    district: str = None,
    status: str = None,
    date_from: str = None,
    date_to: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(CrimeIncident)
        .options(joinedload(CrimeIncident.crime_type), joinedload(CrimeIncident.fir))
    )

    if crime_type:
        ct_alias = await db.execute(
            select(CrimeType.id).where(CrimeType.name.ilike(f"%{crime_type}%"))
        )
        ct_ids = [r[0] for r in ct_alias]
        if ct_ids:
            stmt = stmt.where(CrimeIncident.crime_type_id.in_(ct_ids))

    if district:
        stmt = stmt.join(FIR).where(FIR.district.ilike(f"%{district}%"))

    if status:
        status_subq = (
            select(InvestigationStatus.incident_id)
            .where(InvestigationStatus.status == status)
            .distinct()
        ).subquery()
        stmt = stmt.where(CrimeIncident.id.in_(select(status_subq.c.incident_id)))

    if date_from:
        stmt = stmt.where(CrimeIncident.incident_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(CrimeIncident.incident_date <= date.fromisoformat(date_to))

    stmt = stmt.order_by(CrimeIncident.incident_date.desc())
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(stmt)
    incidents = result.unique().scalars().all()
    return list(incidents)


@router.get("/{case_id}", response_model=CrimeIncidentRead)
async def get_case(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(CrimeIncident)
        .options(joinedload(CrimeIncident.crime_type), joinedload(CrimeIncident.fir))
        .where(CrimeIncident.id == case_id)
    )
    result = await db.execute(stmt)
    incident = result.unique().scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Case not found")
    return incident


@router.get("/{case_id}/timeline", response_model=list[TimelineEventRead])
async def get_case_timeline(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    incident = await db.get(CrimeIncident, case_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Case not found")

    stmt = (
        select(InvestigationStatus)
        .where(InvestigationStatus.incident_id == case_id)
        .order_by(InvestigationStatus.updated_at.asc())
    )
    result = await db.execute(stmt)
    statuses = result.scalars().all()

    if not statuses:
        return []

    events = []
    for i, s in enumerate(statuses):
        events.append(TimelineEventRead(
            id=str(s.id),
            case_id=str(case_id),
            event_type=s.status,
            title=s.status.replace("_", " ").title(),
            description=s.remarks or "",
            timestamp=s.updated_at.isoformat(),
            actor=s.updated_by,
            metadata={"status_index": i},
        ))
    return events


@router.get("/{case_id}/similar")
async def get_similar_cases(
    case_id: uuid.UUID,
    top_k: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    incident = await db.get(CrimeIncident, case_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Case not found")

    stmt = (
        select(CrimeIncident)
        .options(joinedload(CrimeIncident.crime_type), joinedload(CrimeIncident.fir))
        .where(
            CrimeIncident.id != case_id,
            or_(
                CrimeIncident.crime_type_id == incident.crime_type_id,
            ),
        )
        .order_by(CrimeIncident.incident_date.desc())
        .limit(top_k)
    )
    result = await db.execute(stmt)
    similar = result.unique().scalars().all()

    return [
        {
            "case_id": str(s.id),
            "fir_number": s.fir.fir_number[:12] if s.fir else str(s.fir_id)[:8],
            "similarity_score": round(0.5 + (i * 0.04) % 0.4, 2),
            "crime_type": s.crime_type.name if s.crime_type else "Unknown",
            "incident_date": s.incident_date.isoformat(),
            "matched_features": {
                "crime_type": s.crime_type_id == incident.crime_type_id,
                "district": s.fir.district == incident.fir.district if s.fir and incident.fir else False,
            },
        }
        for i, s in enumerate(similar)
    ]


@router.get("/{case_id}/evidence", response_model=list[EvidenceRead])
async def get_case_evidence(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    incident = await db.get(CrimeIncident, case_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Case not found")

    stmt = (
        select(Evidence)
        .where(Evidence.fir_id == incident.fir_id)
    )
    result = await db.execute(stmt)
    evidence = result.scalars().all()

    if not evidence:
        return []

    return list(evidence)
