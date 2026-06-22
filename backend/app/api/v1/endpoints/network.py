from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import NetworkQuery, NetworkResponse
from app.core.synthetic_data import generate_network_analysis

router = APIRouter()


@router.post("/analyze", response_model=NetworkResponse)
async def analyze_network(
    query: NetworkQuery,
    current_user: User = Depends(get_current_user),
):
    return generate_network_analysis(query.person_id)


@router.get("/centrality/{person_id}")
async def get_person_centrality(
    person_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {
        "person_id": person_id,
        "centrality": {
            "degree": 0.75,
            "betweenness": 0.42,
            "closeness": 0.61,
            "pagerank": 0.38,
        },
        "top_connections": ["Ravi", "Ajay", "Priya"],
    }


@router.get("/communities")
async def detect_communities(
    gang_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return [
        {"community_id": 1, "members": ["Ravi Kumar", "Ajay Singh", "Priya Sharma"], "size": 3},
        {"community_id": 2, "members": ["Vikram Patel", "Sneha Reddy"], "size": 2},
    ]


@router.get("/paths/{person_a}/{person_b}")
async def find_connection_path(
    person_a: str,
    person_b: str,
    max_depth: int = 4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {
        "path": [
            {"person": person_a, "relationship": None},
            {"person": "Intermediate-1", "relationship": "KNOWN"},
            {"person": "Intermediate-2", "relationship": "CO_CONSPIRATOR"},
            {"person": person_b, "relationship": "MEMBER_OF"},
        ],
        "length": 3,
        "max_depth": max_depth,
    }


@router.get("/suspicious-patterns")
async def detect_suspicious_patterns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {
        "isolated_persons": {"count": 12},
        "high_degree_persons": [
            {"person_id": "P001", "degree": 15},
            {"person_id": "P002", "degree": 12},
            {"person_id": "P003", "degree": 11},
        ],
        "suspicious_communities": [
            {"community_id": 3, "size": 8, "density": 0.9, "flag": "highly_dense"},
        ],
    }
