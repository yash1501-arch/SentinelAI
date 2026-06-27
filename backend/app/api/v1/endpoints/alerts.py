"""
Smart Alerts endpoint — generates AI-driven alerts from forecasts,
pattern matching, and network anomalies.
"""

import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.crime import CrimeIncident, CrimeType, FIR
from app.models.analytics import CaseForecast, OffenderProfile, CrimeHotspot

router = APIRouter()


@router.get("/")
async def get_alerts(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate smart alerts from multiple intelligence sources:
    - Forecast-based (predicted crime spikes)
    - Pattern-based (similar case matches)
    - Network-based (suspicious connections)
    - Risk-based (high-risk offender activity)
    """
    alerts = []

    # 1. Forecast alerts — predicted spikes
    forecast_alerts = await _get_forecast_alerts(db)
    alerts.extend(forecast_alerts)

    # 2. High-risk offender alerts
    offender_alerts = await _get_offender_alerts(db)
    alerts.extend(offender_alerts)

    # 3. Hotspot alerts — high density crime areas
    hotspot_alerts = await _get_hotspot_alerts(db)
    alerts.extend(hotspot_alerts)

    # 4. Unsolved heinous case alerts
    case_alerts = await _get_unsolved_heinous_alerts(db)
    alerts.extend(case_alerts)

    # Sort by severity then time
    severity_order = {"critical": 0, "high": 1, "warning": 2, "info": 3}
    alerts.sort(key=lambda a: (severity_order.get(a["severity"], 3), a["created_at"]))

    return alerts[:limit]


@router.get("/count")
async def get_alert_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of active alerts by severity."""
    alerts = await get_alerts(limit=50, current_user=current_user, db=db)
    counts = {"critical": 0, "high": 0, "warning": 0, "info": 0, "total": len(alerts)}
    for a in alerts:
        sev = a.get("severity", "info")
        if sev in counts:
            counts[sev] += 1
    return counts


async def _get_forecast_alerts(db: AsyncSession) -> list:
    """Alerts from forecasts predicting high crime volumes."""
    alerts = []
    now = datetime.now(timezone.utc)
    week_ahead = now + timedelta(days=7)

    stmt = (
        select(CaseForecast)
        .where(
            CaseForecast.forecast_date >= now,
            CaseForecast.forecast_date <= week_ahead,
            CaseForecast.predicted_value > 50,
        )
        .order_by(desc(CaseForecast.predicted_value))
        .limit(5)
    )
    result = await db.execute(stmt)
    forecasts = result.scalars().all()

    for f in forecasts:
        confidence_pct = int((f.confidence_level or 0.8) * 100)
        alerts.append({
            "id": str(f.id),
            "type": "forecast",
            "severity": "critical" if f.predicted_value > 75 else "warning",
            "title": f"Crime spike predicted: {f.predicted_value:.0f} incidents forecasted",
            "description": (
                f"Model '{f.model_used}' predicts elevated crime volume "
                f"by {f.forecast_date.strftime('%b %d')} with {confidence_pct}% confidence. "
                f"Range: {f.lower_bound:.0f}–{f.upper_bound:.0f} incidents."
            ),
            "created_at": now.isoformat(),
            "source": "Forecast Agent",
            "actionable": True,
        })

    return alerts


async def _get_offender_alerts(db: AsyncSession) -> list:
    """Alerts for high-risk offenders."""
    alerts = []
    stmt = (
        select(OffenderProfile)
        .where(OffenderProfile.risk_score > 0.75)
        .order_by(desc(OffenderProfile.risk_score))
        .limit(5)
    )
    result = await db.execute(stmt)
    profiles = result.scalars().all()

    now = datetime.now(timezone.utc)
    for p in profiles:
        risk_pct = int((p.risk_score or 0) * 100)
        alerts.append({
            "id": str(p.id),
            "type": "offender",
            "severity": "critical" if p.risk_score > 0.85 else "high",
            "title": f"High-risk offender detected (score: {risk_pct}%)",
            "description": (
                f"Archetype: {p.archetype or 'Unknown'}. "
                f"Escalation risk: {p.escalation_risk or 'Unknown'}. "
                f"Recidivism probability: {int((p.recidivism_probability or 0) * 100)}%."
            ),
            "created_at": now.isoformat(),
            "source": "Profiling Agent",
            "actionable": True,
        })

    return alerts


async def _get_hotspot_alerts(db: AsyncSession) -> list:
    """Alerts for high-density crime hotspots."""
    alerts = []
    stmt = (
        select(CrimeHotspot)
        .where(CrimeHotspot.risk_score > 0.7)
        .order_by(desc(CrimeHotspot.risk_score))
        .limit(3)
    )
    result = await db.execute(stmt)
    hotspots = result.scalars().all()

    now = datetime.now(timezone.utc)
    for h in hotspots:
        risk_pct = int((h.risk_score or 0) * 100)
        alerts.append({
            "id": str(h.id),
            "type": "hotspot",
            "severity": "warning",
            "title": f"Active crime hotspot (risk: {risk_pct}%)",
            "description": (
                f"Location ({h.latitude:.4f}, {h.longitude:.4f}) shows elevated crime density "
                f"({h.crime_density:.2f}) within {h.radius_meters or 500}m radius. "
                f"Cluster #{h.cluster_id}."
            ),
            "created_at": now.isoformat(),
            "source": "Analytics Agent",
            "actionable": True,
        })

    return alerts


async def _get_unsolved_heinous_alerts(db: AsyncSession) -> list:
    """Alerts for unsolved heinous crimes needing attention."""
    alerts = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)

    stmt = (
        select(CrimeIncident, FIR)
        .join(FIR, CrimeIncident.fir_id == FIR.id)
        .where(
            CrimeIncident.is_heinous == True,
            CrimeIncident.is_solved == False,
            CrimeIncident.incident_date >= cutoff.date(),
        )
        .order_by(CrimeIncident.incident_date.desc())
        .limit(3)
    )
    result = await db.execute(stmt)
    cases = result.all()

    now = datetime.now(timezone.utc)
    for incident, fir in cases:
        days_open = (now.date() - incident.incident_date).days if incident.incident_date else 0
        alerts.append({
            "id": str(incident.id),
            "type": "case",
            "severity": "high" if days_open > 30 else "warning",
            "title": f"Unsolved heinous case: FIR {fir.fir_number} ({days_open} days open)",
            "description": (
                f"{fir.district} — {incident.description[:100] if incident.description else 'No description'}. "
                f"Registered: {fir.registration_date.strftime('%b %d, %Y') if fir.registration_date else 'Unknown'}."
            ),
            "created_at": now.isoformat(),
            "source": "Case Monitor",
            "actionable": True,
        })

    return alerts
