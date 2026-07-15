from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
import uuid


class CrimeTypeRead(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    description: Optional[str] = None
    severity_level: Optional[int] = None

    class Config:
        from_attributes = True


class FIRCreate(BaseModel):
    fir_number: str
    police_station: str
    district: str
    state: str = "Karnataka"
    registration_date: datetime
    act_sections: Optional[List[str]] = None
    brief_fact: str
    recorded_by: str
    io_name: Optional[str] = None
    io_badge: Optional[str] = None


class FIRRead(BaseModel):
    id: uuid.UUID
    fir_number: str
    police_station: str
    district: str
    state: str
    registration_date: datetime
    act_sections: Optional[List[str]] = None
    brief_fact: str
    io_name: Optional[str] = None
    recorded_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class CrimeIncidentCreate(BaseModel):
    fir_id: uuid.UUID
    crime_type_id: uuid.UUID
    incident_date: date
    incident_time: Optional[time] = None
    reported_date: datetime
    description: str
    modus_operandi: Optional[str] = None
    property_value_loss: Optional[float] = None
    injury_count: Optional[int] = 0
    fatality_count: Optional[int] = 0


class CrimeIncidentRead(BaseModel):
    id: uuid.UUID
    fir_id: uuid.UUID
    crime_type_id: uuid.UUID
    incident_date: date
    incident_time: Optional[time] = None
    description: str
    modus_operandi: Optional[str] = None
    is_solved: bool
    property_value_loss: Optional[float] = None
    injury_count: int
    fatality_count: int
    created_at: datetime
    crime_type: Optional[CrimeTypeRead] = None

    class Config:
        from_attributes = True


class PersonCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    alias: Optional[List[str]] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = "Indian"
    occupation: Optional[str] = None
    education_level: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    aadhaar_number: Optional[str] = None


class PersonRead(BaseModel):
    id: uuid.UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    alias: Optional[List[str]] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class LocationData(BaseModel):
    incident_id: uuid.UUID
    name: Optional[str] = None
    location_type: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None


class EvidenceCreate(BaseModel):
    fir_id: uuid.UUID
    evidence_type: str
    name: str
    description: Optional[str] = None
    collection_date: Optional[datetime] = None
    collected_by: Optional[str] = None
    location_found: Optional[str] = None


class EvidenceRead(BaseModel):
    id: uuid.UUID
    fir_id: uuid.UUID
    evidence_type: str
    name: str
    description: Optional[str] = None
    is_forensically_analyzed: bool
    is_admissible: Optional[bool] = None

    class Config:
        from_attributes = True


class TimelineEventRead(BaseModel):
    id: str
    case_id: str
    event_type: str
    title: str
    description: Optional[str] = None
    timestamp: str
    actor: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
