from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ConversationRequest(BaseModel):
    session_id: str
    message: str
    language: Optional[str] = "en"


class ConversationResponse(BaseModel):
    session_id: str
    reply: str
    language: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    reasoning_chain: Optional[List[str]] = None
    visualizations: Optional[List[Dict[str, Any]]] = None


class ConversationHistoryRead(BaseModel):
    id: uuid.UUID
    session_id: str
    role: str
    content: str
    language: str
    created_at: datetime

    class Config:
        from_attributes = True


class CrimeHotspotRead(BaseModel):
    id: uuid.UUID
    latitude: float
    longitude: float
    cluster_id: Optional[int] = None
    risk_score: Optional[float] = None
    crime_density: Optional[float] = None
    radius_meters: Optional[float] = None

    class Config:
        from_attributes = True


class ForecastRequest(BaseModel):
    forecast_type: str
    district: Optional[str] = None
    crime_type_id: Optional[uuid.UUID] = None
    days_ahead: int = 30


class ForecastDataPoint(BaseModel):
    date: str
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class ForecastResponse(BaseModel):
    forecast_data: List[ForecastDataPoint]
    model_used: str
    confidence_level: float
    features_used: Optional[List[str]] = None


class SimilarCaseRequest(BaseModel):
    case_id: uuid.UUID
    top_k: int = 10


class SimilarCaseResult(BaseModel):
    case_id: uuid.UUID
    fir_number: str
    similarity_score: float
    crime_type: str
    incident_date: str
    matched_features: Optional[Dict[str, Any]] = None


class NetworkQuery(BaseModel):
    person_id: Optional[uuid.UUID] = None
    case_id: Optional[uuid.UUID] = None
    depth: int = 2


class NetworkNode(BaseModel):
    id: str
    label: str
    type: str
    metadata: Optional[Dict[str, Any]] = None


class NetworkEdge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: Optional[float] = None


class NetworkResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    centrality: Optional[Dict[str, float]] = None
    communities: Optional[List[List[str]]] = None


class ExportPDFRequest(BaseModel):
    session_id: str
    case_ids: Optional[List[uuid.UUID]] = None
    include_charts: bool = True


class AuditLogRead(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
