import uuid
from datetime import datetime, timezone, timedelta, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.crime import CrimeIncident, CrimeType, FIR
from app.models.analytics import CrimeHotspot, SocialIndicator, CaseForecast, OffenderProfile
from app.schemas.analytics import (
    ForecastRequest, ForecastResponse, ForecastDataPoint,
    CrimeHotspotRead,
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
    months = func.date_trunc("month", CrimeIncident.incident_date).label("month")

    stmt = (
        select(
            months,
            CrimeType.name.label("crime_type"),
            FIR.district,
            func.count(CrimeIncident.id).label("count"),
        )
        .join(CrimeType, CrimeIncident.crime_type_id == CrimeType.id)
        .join(FIR, CrimeIncident.fir_id == FIR.id)
    )

    if district:
        stmt = stmt.where(FIR.district.ilike(f"%{district}%"))
    if crime_type:
        stmt = stmt.where(CrimeType.name.ilike(f"%{crime_type}%"))
    if date_from:
        stmt = stmt.where(CrimeIncident.incident_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(CrimeIncident.incident_date <= date.fromisoformat(date_to))

    now = datetime.now(timezone.utc)
    stmt = stmt.where(CrimeIncident.incident_date >= (now - timedelta(days=365)).date())

    stmt = stmt.group_by(months, CrimeType.name, FIR.district).order_by(months)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "month": r.month.isoformat() if hasattr(r.month, "isoformat") else str(r.month),
            "crime_type": r.crime_type,
            "count": r.count,
            "district": r.district,
        }
        for r in rows
    ]


@router.get("/hotspots", response_model=list[CrimeHotspotRead])
async def get_crime_hotspots(
    district: str = None,
    days: int = Query(30, ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CrimeHotspot)

    if district:
        stmt = (
            stmt.join(CrimeIncident, CrimeHotspot.incident_id == CrimeIncident.id)
            .join(FIR, CrimeIncident.fir_id == FIR.id)
            .where(FIR.district.ilike(f"%{district}%"))
        )

    stmt = stmt.order_by(CrimeHotspot.risk_score.desc().nullslast())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/forecast", response_model=ForecastResponse)
async def get_crime_forecast(
    request: ForecastRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(CaseForecast)
        .join(CrimeIncident, CaseForecast.incident_id == CrimeIncident.id)
        .join(FIR, CrimeIncident.fir_id == FIR.id)
    )

    if request.district:
        stmt = stmt.where(FIR.district.ilike(f"%{request.district}%"))
    if request.crime_type_id:
        stmt = stmt.where(CrimeIncident.crime_type_id == request.crime_type_id)

    stmt = stmt.order_by(CaseForecast.forecast_date.desc()).limit(request.days_ahead)
    result = await db.execute(stmt)
    forecasts = result.scalars().all()

    if forecasts:
        data = [
            ForecastDataPoint(
                date=f.forecast_date.isoformat(),
                predicted_value=float(f.predicted_value),
                lower_bound=float(f.lower_bound) if f.lower_bound else None,
                upper_bound=float(f.upper_bound) if f.upper_bound else None,
            )
            for f in forecasts
        ]
        return ForecastResponse(
            forecast_data=data,
            model_used=forecasts[0].model_used or "Prophet",
            confidence_level=float(forecasts[0].confidence_level) if forecasts[0].confidence_level else 0.85,
            features_used=forecasts[0].features_used if forecasts[0].features_used else ["seasonality", "trend"],
        )

    return ForecastResponse(
        forecast_data=[],
        model_used="Prophet",
        confidence_level=0.85,
        features_used=["seasonality", "trend"],
    )


@router.get("/sociological")
async def get_sociological_insights(
    district: str = None,
    year: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SocialIndicator)

    if district:
        stmt = stmt.where(SocialIndicator.district.ilike(f"%{district}%"))
    if year:
        stmt = stmt.where(SocialIndicator.year == year)

    stmt = stmt.order_by(SocialIndicator.year.desc())
    result = await db.execute(stmt)
    indicators = result.scalars().all()

    if not indicators:
        return []

    return [
        {
            "district": ind.district,
            "unemployment_rate": float(ind.unemployment_rate) if ind.unemployment_rate else 0,
            "literacy_rate": float(ind.literacy_rate) if ind.literacy_rate else 0,
            "population_density": float(ind.population_density) if ind.population_density else 0,
            "police_per_capita": float(ind.police_per_capita) if ind.police_per_capita else 0,
            "crime_rate_per_100k": float(ind.crime_rate_per_100k) if ind.crime_rate_per_100k else 0,
            "top_crimes": [],
            "socioeconomic_score": round(float(ind.literacy_rate or 70) / 20, 1),
            "year": ind.year,
        }
        for ind in indicators
    ]


@router.get("/statistics")
async def get_crime_statistics(
    district: str = None,
    date_from: str = None,
    date_to: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Build WHERE conditions
    conditions = []
    if district:
        conditions.append(FIR.district.ilike(f"%{district}%"))
    if date_from:
        conditions.append(CrimeIncident.incident_date >= date.fromisoformat(date_from))
    if date_to:
        conditions.append(CrimeIncident.incident_date <= date.fromisoformat(date_to))

    count_stmt = select(
        func.count(CrimeIncident.id).label("total"),
        func.sum(case((CrimeIncident.is_solved == True, 1), else_=0)).label("solved"),
        func.sum(case((CrimeIncident.is_heinous == True, 1), else_=0)).label("heinous"),
        func.coalesce(func.avg(CrimeIncident.property_value_loss), 0).label("avg_loss"),
        func.coalesce(func.sum(CrimeIncident.injury_count), 0).label("total_injuries"),
        func.coalesce(func.sum(CrimeIncident.fatality_count), 0).label("total_fatalities"),
    ).select_from(CrimeIncident)

    if district:
        count_stmt = count_stmt.join(FIR, CrimeIncident.fir_id == FIR.id)

    for cond in conditions:
        count_stmt = count_stmt.where(cond)

    result = await db.execute(count_stmt)
    row = result.one()

    total = int(row.total) or 0
    solved = int(row.solved) or 0
    heinous = int(row.heinous) or 0

    return {
        "total_cases": total,
        "solved_cases": solved,
        "heinous_cases": heinous,
        "avg_loss": round(float(row.avg_loss or 0), 2),
        "active_investigations": total - solved,
        "total_arrests": solved,
        "conviction_rate": round(float(solved / total), 2) if total > 0 else 0,
        "avg_resolution_days": 45,
    }


@router.get("/offender-profiles")
async def get_offender_profiles(
    archetype: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(OffenderProfile)
    if archetype:
        stmt = stmt.where(OffenderProfile.archetype.ilike(f"%{archetype}%"))
    stmt = stmt.order_by(OffenderProfile.risk_score.desc().nullslast()).limit(20)

    result = await db.execute(stmt)
    profiles = result.scalars().all()

    if not profiles:
        return []

    return [
        {
            "person_id": str(p.person_id),
            "archetype": p.archetype or "Unknown",
            "risk_level": p.risk_level or "Medium",
            "risk_score": float(p.risk_score) if p.risk_score else 0.5,
            "recidivism_probability": float(p.recidivism_probability) if p.recidivism_probability else 0.5,
            "escalation_risk": p.escalation_risk or "Moderate",
            "behavioral_patterns": p.behavioral_pattern or [],
            "profile_summary": p.profile_summary or "",
        }
        for p in profiles
    ]


@router.get("/financial")
async def get_financial_analysis(
    min_amount: float = Query(50000, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Financial crime detection — suspicious transactions and anomalies."""
    from app.models.crime import Transaction, BankAccount

    # Get suspicious transactions
    suspicious_stmt = (
        select(Transaction)
        .where(Transaction.is_suspicious == True)
        .order_by(Transaction.amount.desc())
        .limit(20)
    )
    result = await db.execute(suspicious_stmt)
    suspicious = result.scalars().all()

    # Get high-value transactions
    high_value_stmt = (
        select(Transaction)
        .where(Transaction.amount >= min_amount)
        .order_by(Transaction.transaction_date.desc())
        .limit(20)
    )
    result2 = await db.execute(high_value_stmt)
    high_value = result2.scalars().all()

    # Summary stats
    stats_stmt = select(
        func.count(Transaction.id).label("total"),
        func.sum(case((Transaction.is_suspicious == True, 1), else_=0)).label("suspicious_count"),
        func.coalesce(func.sum(Transaction.amount), 0).label("total_volume"),
    )
    stats_result = await db.execute(stats_stmt)
    stats = stats_result.one()

    return {
        "summary": {
            "total_transactions": int(stats.total or 0),
            "suspicious_count": int(stats.suspicious_count or 0),
            "total_volume": float(stats.total_volume or 0),
            "fraud_rate": round(float(stats.suspicious_count or 0) / max(int(stats.total or 1), 1), 4),
        },
        "suspicious_transactions": [
            {
                "id": str(t.id),
                "amount": float(t.amount),
                "date": t.transaction_date.isoformat() if t.transaction_date else None,
                "type": t.transaction_type,
                "reason": t.suspicion_reason,
                "risk_score": t.risk_score,
            }
            for t in suspicious
        ],
        "high_value_transactions": [
            {
                "id": str(t.id),
                "amount": float(t.amount),
                "date": t.transaction_date.isoformat() if t.transaction_date else None,
                "type": t.transaction_type,
                "is_suspicious": t.is_suspicious,
            }
            for t in high_value
        ],
    }


@router.post("/financial/detect")
async def detect_fraud(
    transaction: dict,
    current_user: User = Depends(get_current_user),
):
    """Run ML fraud detection on a transaction."""
    from app.ml.financial import detect_fraud as ml_detect
    result = await ml_detect(transaction)
    return result
