import random
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.crime import CrimeIncidentRead, EvidenceRead, TimelineEventRead
from app.core.synthetic_data import generate_cases, generate_timeline_events

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
    return generate_cases(per_page)


@router.get("/{case_id}", response_model=CrimeIncidentRead)
async def get_case(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cases = generate_cases(1)
    return cases[0] if cases else None


@router.get("/{case_id}/timeline", response_model=list[TimelineEventRead])
async def get_case_timeline(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return generate_timeline_events(case_id)


@router.get("/{case_id}/similar")
async def get_similar_cases(
    case_id: str,
    top_k: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.synthetic_data import generate_cases
    cases = generate_cases(top_k)
    return [
        {
            "case_id": c["id"],
            "fir_number": c["fir_id"][:8],
            "similarity_score": round(0.5 + (i * 0.05) % 0.4, 2),
            "crime_type": c["crime_type"]["name"],
            "incident_date": c["incident_date"],
            "matched_features": {"crime_type": True, "district": True},
        }
        for i, c in enumerate(cases)
    ]


@router.get("/{case_id}/evidence", response_model=list[EvidenceRead])
async def get_case_evidence(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import uuid
    evidence_types = ["Physical", "Digital", "Document", "Forensic", "Witness Statement"]
    return [
        {
            "id": str(uuid.uuid4()),
            "fir_id": case_id,
            "evidence_type": random.choice(evidence_types),
            "name": f"Evidence item {i+1}",
            "description": f"Collected during investigation of case {case_id[:8]}",
            "is_forensically_analyzed": random.random() < 0.6,
            "is_admissible": random.random() < 0.8,
        }
        for i in range(random.randint(3, 8))
    ]



