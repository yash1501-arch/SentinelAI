import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

random.seed(42)

CRIME_TYPES = ["Burglary", "Assault", "Robbery", "Homicide", "Cyber Fraud", "Drug Trafficking", "Vehicle Theft", "Kidnapping"]
DISTRICTS = ["Mysore", "Bengaluru", "Mangalore", "Hubli", "Belgaum", "Shivamogga"]
OFFICERS = ["SI Kumar", "ACP Patil", "Inspector Rao", "SI Deshmukh", "ACP Murthy", "SI Iyer"]

PERSON_NAMES = [
    ("Ravi", "Kumar"), ("Ajay", "Singh"), ("Priya", "Sharma"), ("Vikram", "Patel"),
    ("Sneha", "Reddy"), ("Arjun", "Nair"), ("Deepa", "Joshi"), ("Manoj", "Verma"),
    ("Kavita", "Desai"), ("Sanjay", "Gupta"), ("Anita", "Rao"), ("Vijay", "Naik"),
]

GANG_NAMES = [
    "Mysore Street Crew", "Bandra Boys", "Koramangala Syndicate", "Mangalore Cartel",
    "Old Town Mafia", "Silk Board Ring", "Electronic City Network",
]


def random_date(start_days_ago: int = 365) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=random.randint(0, start_days_ago))).isoformat()


def generate_trends() -> list[dict[str, Any]]:
    trends = []
    for i in range(12):
        d = datetime.now(timezone.utc) - timedelta(days=30 * (11 - i))
        for ct in CRIME_TYPES[:5]:
            trends.append({
                "month": d.replace(day=1).isoformat(),
                "crime_type": ct,
                "count": random.randint(10, 200),
                "district": random.choice(DISTRICTS),
            })
    return trends


def generate_statistics() -> dict[str, Any]:
    return {
        "total_cases": random.randint(500, 2000),
        "solved_cases": random.randint(200, 800),
        "heinous_cases": random.randint(20, 100),
        "avg_loss": round(random.uniform(10000, 500000), 2),
        "active_investigations": random.randint(100, 400),
        "total_arrests": random.randint(150, 600),
        "conviction_rate": round(random.uniform(0.4, 0.8), 2),
        "avg_resolution_days": random.randint(30, 180),
    }


def generate_hotspots(count: int = 15) -> list[dict[str, Any]]:
    centers = [
        (12.3, 76.6), (12.97, 77.6), (12.91, 74.86), (15.36, 75.14),
        (15.85, 74.5), (14.0, 75.67), (12.95, 77.55), (12.35, 76.65),
    ]
    hotspots = []
    cluster_id = 1
    for lat, lng in centers:
        for _ in range(random.randint(1, 3)):
            if len(hotspots) >= count:
                break
            hotspots.append({
                "id": str(uuid.uuid4()),
                "latitude": round(lat + random.uniform(-0.05, 0.05), 6),
                "longitude": round(lng + random.uniform(-0.05, 0.05), 6),
                "cluster_id": cluster_id,
                "risk_score": round(random.uniform(0.1, 0.95), 4),
                "crime_density": round(random.uniform(0.1, 1.0), 4),
                "radius_meters": random.randint(100, 2000),
            })
        cluster_id += 1
    return hotspots[:count]


def generate_forecast(days_ahead: int = 30) -> dict[str, Any]:
    base = random.randint(30, 100)
    data = []
    for d in range(days_ahead):
        ts = (datetime.now(timezone.utc) + timedelta(days=d)).isoformat()
        pred = max(0, base + random.randint(-20, 30) + int(d * 0.5))
        data.append({
            "date": ts,
            "predicted_value": pred,
            "lower_bound": max(0, pred - random.randint(5, 15)),
            "upper_bound": pred + random.randint(5, 15),
        })
    return {
        "forecast_data": data,
        "model_used": random.choice(["Prophet", "ARIMA", "XGBoost"]),
        "confidence_level": round(random.uniform(0.7, 0.95), 2),
        "features_used": ["seasonality", "trend", "day_of_week", "month", "historical_volume"],
    }


def generate_cases(count: int = 25) -> list[dict[str, Any]]:
    cases = []
    for i in range(count):
        reg_date = (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 365)))
        first, last = random.choice(PERSON_NAMES)
        ct = random.choice(CRIME_TYPES)
        solved = random.random() < 0.45
        cases.append({
            "id": str(uuid.uuid4()),
            "fir_id": str(uuid.uuid4()),
            "crime_type_id": str(uuid.uuid4()),
            "incident_date": reg_date.date().isoformat(),
            "incident_time": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
            "description": f"{ct} reported at {random.choice(DISTRICTS)} involving {first} {last}",
            "modus_operandi": random.choice([
                "Forced entry at night", "Social engineering via phone", "Armed robbery in daylight",
                "Break-in during business hours", "Pickpocketing in crowded area",
            ]),
            "is_solved": solved,
            "property_value_loss": round(random.uniform(0, 200000), 2),
            "injury_count": random.randint(0, 3),
            "fatality_count": random.randint(0, 1) if ct == "Homicide" else 0,
            "created_at": reg_date.isoformat(),
            "crime_type": {
                "id": str(uuid.uuid4()),
                "name": ct,
                "category": random.choice(["Violent", "Property", "Financial", "Cyber", "Drug-Related"]),
                "description": f"Cases involving {ct.lower()}",
                "severity_level": random.randint(1, 5),
            },
        })
    return sorted(cases, key=lambda c: c["incident_date"], reverse=True)


def generate_network_analysis(person_id: str | None = None) -> dict[str, Any]:
    nodes = []
    edges = []
    node_ids = [str(uuid.uuid4()) for _ in range(8)]
    for i, nid in enumerate(node_ids):
        nodes.append({
            "id": nid,
            "label": random.choice(PERSON_NAMES)[0] if i < 5 else random.choice(GANG_NAMES),
            "type": "person" if i < 5 else "gang",
            "metadata": None,
        })
    for i in range(7):
        edges.append({
            "source": node_ids[i],
            "target": node_ids[i + 1],
            "relationship": random.choice(["KNOWN", "MEMBER_OF", "CO_CONSPIRATOR", "FAMILY"]),
            "weight": random.randint(1, 10),
        })
    return {
        "nodes": nodes,
        "edges": edges,
        "centrality": {n["label"]: round(random.uniform(0, 1), 4) for n in nodes[:5]},
        "communities": [[n["label"] for n in nodes[:3]], [n["label"] for n in nodes[3:6]]],
    }


def generate_sociological(district: str | None = None) -> dict[str, Any]:
    d = district or random.choice(DISTRICTS)
    return {
        "district": d,
        "unemployment_rate": round(random.uniform(3, 12), 1),
        "literacy_rate": round(random.uniform(65, 95), 1),
        "population_density": round(random.uniform(200, 5000), 0),
        "police_per_capita": round(random.uniform(0.5, 3.0), 2),
        "crime_rate_per_100k": round(random.uniform(100, 800), 0),
        "top_crimes": random.sample(CRIME_TYPES, 3),
        "socioeconomic_score": round(random.uniform(2, 8), 1),
        "year": datetime.now(timezone.utc).year,
    }


def generate_timeline_events(case_id: str) -> list[dict[str, Any]]:
    event_types = [
        ("fir_registered", "FIR Registered", "First Information Report filed at police station"),
        ("incident_reported", "Incident Reported", "Incident reported by victim or witness"),
        ("investigation_started", "Investigation Started", "Preliminary investigation initiated"),
        ("evidence_collected", "Evidence Collected", "Physical and digital evidence collected"),
        ("suspect_identified", "Suspect Identified", "Primary suspect identified through investigation"),
        ("arrest_made", "Arrest Made", "Suspect taken into custody"),
        ("chargesheet_filed", "Chargesheet Filed", "Formal chargesheet submitted to court"),
        ("court_hearing", "Court Hearing", "Case heard in court for proceedings"),
        ("note_added", "Investigation Note", "Officer added detailed investigation notes"),
        ("status_change", "Status Updated", "Case investigation status updated"),
    ]
    officers = ["SI Kumar", "ACP Patil", "Inspector Rao", "SI Deshmukh", "ACP Murthy"]
    now = datetime.now(timezone.utc)
    events = []
    for i, (etype, title, desc) in enumerate(event_types):
        ts = now - timedelta(days=len(event_types) - i, hours=i * 3)
        events.append({
            "id": str(uuid.uuid4()),
            "case_id": case_id,
            "event_type": etype,
            "title": title,
            "description": desc,
            "timestamp": ts.isoformat(),
            "actor": officers[i % len(officers)],
            "metadata": {"source": "synthetic", "index": i},
        })
    return events


def generate_offender_profiles(count: int = 5) -> list[dict[str, Any]]:
    profiles = []
    archetypes = ["Violent Offender", "Financial Fraudster", "Drug Trafficker", "Property Criminal", "Cyber Criminal"]
    for i in range(count):
        profiles.append({
            "person_id": str(uuid.uuid4()),
            "archetype": archetypes[i % len(archetypes)],
            "risk_level": random.choice(["Low", "Medium", "High", "Critical"]),
            "risk_score": round(random.uniform(0.1, 0.95), 4),
            "recidivism_probability": round(random.uniform(0.1, 0.9), 4),
            "escalation_risk": random.choice(["Low", "Moderate", "High"]),
            "behavioral_patterns": random.sample([
                "Night-time activity", "Repeat offenses", "Targets vulnerable victims",
                "Uses violence", "Operates in groups", "Cross-jurisdictional",
            ], 3),
            "profile_summary": f"Subject exhibits {random.choice(archetypes).lower()} patterns with escalation risk.",
        })
    return profiles
