import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ConversationRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    SEARCH = "search"


class CrimeHotspot(Base):
    __tablename__ = "crime_hotspots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    cluster_id = Column(Integer, nullable=True, index=True)
    hotspot_name = Column(String(255), nullable=True)
    risk_score = Column(Float, nullable=True)
    crime_density = Column(Float, nullable=True)
    time_window_start = Column(DateTime(timezone=True), nullable=True)
    time_window_end = Column(DateTime(timezone=True), nullable=True)
    crime_type_distribution = Column(JSONB, nullable=True)
    radius_meters = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    incident = relationship("CrimeIncident", back_populates="hotspots")

    __table_args__ = (
        {"comment": "Crime hotspot clusters from DBSCAN analysis"},
    )


class SocialIndicator(Base):
    __tablename__ = "social_indicators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    population = Column(Integer, nullable=True)
    population_density = Column(Float, nullable=True)
    urbanization_rate = Column(Float, nullable=True)
    literacy_rate = Column(Float, nullable=True)
    avg_income = Column(Float, nullable=True)
    poverty_rate = Column(Float, nullable=True)
    unemployment_rate = Column(Float, nullable=True)
    migration_rate = Column(Float, nullable=True)
    gender_ratio = Column(Float, nullable=True)
    juvenile_population_pct = Column(Float, nullable=True)
    police_per_capita = Column(Float, nullable=True)
    crime_rate_per_100k = Column(Float, nullable=True)
    case_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        {"comment": "Sociological indicators for crime correlation analysis"},
    )


class SimilarCase(Base):
    __tablename__ = "similar_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    similar_case_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)
    similarity_method = Column(String(50), nullable=True)
    matched_features = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    case = relationship("CrimeIncident", foreign_keys=[case_id], back_populates="cases_similar_from")
    similar_case = relationship("CrimeIncident", foreign_keys=[similar_case_id], back_populates="cases_similar_to")

    __table_args__ = (
        {"comment": "Similar case pairs with similarity scores"},
    )


class CaseForecast(Base):
    __tablename__ = "case_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_date = Column(DateTime(timezone=True), nullable=False, index=True)
    forecast_type = Column(String(50), nullable=False)
    predicted_value = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)
    features_used = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    incident = relationship("CrimeIncident", back_populates="forecasts")

    __table_args__ = (
        {"comment": "Crime forecasting results"},
    )


class OffenderProfile(Base):
    __tablename__ = "offender_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    person_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    archetype = Column(String(100), nullable=True)
    risk_level = Column(String(50), nullable=True)
    risk_score = Column(Float, nullable=True)
    behavioral_pattern = Column(JSONB, nullable=True)
    psychological_indicators = Column(JSONB, nullable=True)
    modus_operandi_profile = Column(JSONB, nullable=True)
    escalation_risk = Column(String(50), nullable=True)
    recidivism_probability = Column(Float, nullable=True)
    shap_explanation = Column(JSONB, nullable=True)
    profile_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    incident = relationship("CrimeIncident", back_populates="profiles")

    __table_args__ = (
        {"comment": "Offender behavioral profiles"},
    )


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(SAEnum(ConversationRole), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    case_metadata = Column(JSONB, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="conversation_history")

    __table_args__ = (
        {"comment": "Conversation history for chat context"},
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(SAEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_payload = Column(JSONB, nullable=True)
    response_status = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        {"comment": "Audit trail for all system actions"},
    )
