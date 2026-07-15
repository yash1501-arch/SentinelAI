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
    from app.services.qdrant_service import QdrantService
    from app.services.embedding_service import EmbeddingService

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

    similarity_scores = {}
    try:
        query_text = f"{incident.description or ''} {incident.modus_operandi or ''}"
        query_vector = await EmbeddingService.get_embedding(query_text)
        qdrant_results = await QdrantService.search_similar(
            collection="crime_descriptions",
            query_vector=query_vector,
            top_k=top_k,
            score_threshold=0.3,
            filter_params={"crime_type_id": str(incident.crime_type_id)} if incident.crime_type_id else None,
        )
        for r in qdrant_results:
            payload_case_id = r["payload"].get("case_id") or r["payload"].get("incident_id")
            if payload_case_id:
                similarity_scores[payload_case_id] = r["score"]
    except Exception:
        pass

    results = []
    for i, s in enumerate(similar):
        sid = str(s.id)
        score = similarity_scores.get(sid, 0.5 if s.crime_type_id == incident.crime_type_id else 0.3)
        score = round(score, 2)
        results.append({
            "case_id": sid,
            "fir_number": s.fir.fir_number[:12] if s.fir else str(s.fir_id)[:8],
            "similarity_score": score,
            "crime_type": s.crime_type.name if s.crime_type else "Unknown",
            "incident_date": s.incident_date.isoformat(),
            "matched_features": {
                "crime_type": s.crime_type_id == incident.crime_type_id,
                "district": s.fir.district == incident.fir.district if s.fir and incident.fir else False,
            },
        })
    return results


@router.get("/{case_id}/recommendations")
async def get_case_recommendations(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    incident = await db.get(CrimeIncident, case_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Case not found")

    same_type = await db.execute(
        select(CrimeIncident).options(
            joinedload(CrimeIncident.crime_type),
            joinedload(CrimeIncident.fir),
        ).where(
            CrimeIncident.crime_type_id == incident.crime_type_id,
            CrimeIncident.id != case_id,
            CrimeIncident.is_solved,
        ).limit(10)
    )
    solved_similar = same_type.unique().scalars().all()

    resolution_patterns = []
    avg_resolution_time_days = None
    if solved_similar:
        resolution_times = []
        for s in solved_similar:
            if s.fir and s.fir.registration_date:
                delta = (s.incident_date - s.fir.registration_date.date()).days if hasattr(s.incident_date, 'date') else 0
                if delta > 0:
                    resolution_times.append(delta)
                    outcome_note = getattr(s, 'modus_operandi', None) or s.description[:100] if s.description else None
                    if outcome_note:
                        resolution_patterns.append({
                            "case_id": str(s.id),
                            "resolution_time_days": delta,
                            "modus_operandi": s.modus_operandi[:200] if s.modus_operandi else None,
                            "district": s.fir.district if s.fir else None,
                        })
        if resolution_times:
            avg_resolution_time_days = round(sum(resolution_times) / len(resolution_times))

    recommendations = []
    if incident.description:
        keywords = ["cctv", "fingerprint", "forensic", "witness", "phone", "bank"]
        missing = [k for k in keywords if k not in (incident.description or "").lower()]
        if missing:
            recommendations.append({
                "type": "evidence",
                "priority": "high",
                "suggestion": f"Consider collecting: {', '.join(missing)} evidence",
                "reason": "Similar solved cases typically had these evidence types",
            })

    if avg_resolution_time_days and avg_resolution_time_days > 30:
        recommendations.append({
            "type": "timeline",
            "priority": "medium",
            "suggestion": f"Similar cases resolved in ~{avg_resolution_time_days} days on average",
            "reason": "Case is taking longer than similar solved cases",
        })

    if resolution_patterns:
        modus_list = list(set(p["modus_operandi"] for p in resolution_patterns if p.get("modus_operandi")))
        for mo in modus_list[:3]:
            recommendations.append({
                "type": "modus_operandi",
                "priority": "medium",
                "suggestion": f"Investigate MO pattern: {mo[:150]}",
                "reason": "Matches resolution pattern from similar cases",
            })

    district_recommendations = [p.get("district") for p in resolution_patterns if p.get("district")]
    if district_recommendations:
        from collections import Counter
        common_district = Counter(district_recommendations).most_common(1)[0][0]
        recommendations.append({
            "type": "jurisdiction",
            "priority": "low",
            "suggestion": f"Coordinate with {common_district} police for cross-jurisdictional leads",
            "reason": "Similar crimes occurred across jurisdictions",
        })

    return {
        "case_id": str(case_id),
        "crime_type": incident.crime_type.name if incident.crime_type else "Unknown",
        "resolution_patterns": resolution_patterns[:5],
        "avg_resolution_time_days": avg_resolution_time_days,
        "recommendations": recommendations,
        "similar_solved_count": len(solved_similar),
    }


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
