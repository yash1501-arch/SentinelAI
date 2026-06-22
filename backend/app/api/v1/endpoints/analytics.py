from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.analytics import (
    ForecastRequest, ForecastResponse,
    SimilarCaseRequest, SimilarCaseResult,
    CrimeHotspotRead,
)
from app.core.synthetic_data import (
    generate_trends,
    generate_statistics,
    generate_hotspots,
    generate_forecast,
    generate_sociological,
    generate_offender_profiles,
)

router = APIRouter()


@router.get("/trends")
async def get_crime_trends(
    district: str = None,
    crime_type: str = None,
    period: str = "monthly",
    date_from: str = None,
    date_to: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return generate_trends()


@router.get("/hotspots", response_model=list[CrimeHotspotRead])
async def get_crime_hotspots(
    district: str = None,
    days: int = Query(30, ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return generate_hotspots()


@router.post("/forecast", response_model=ForecastResponse)
async def get_crime_forecast(
    request: ForecastRequest,
    current_user: User = Depends(get_current_user),
):
    return generate_forecast(request.days_ahead)


@router.get("/sociological")
async def get_sociological_insights(
    district: str = None,
    year: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return generate_sociological(district)


@router.get("/statistics")
async def get_crime_statistics(
    district: str = None,
    date_from: str = None,
    date_to: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return generate_statistics()


@router.get("/offender-profiles")
async def get_offender_profiles(
    archetype: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return generate_offender_profiles()
