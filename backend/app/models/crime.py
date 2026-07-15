import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, DateTime, Date, Time, Text, Numeric,
    Float, Integer, ForeignKey, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base
from app.models.associations import (
    incident_vehicles, incident_weapons, incident_phone_numbers,
    incident_emails, incident_bank_accounts, person_addresses,
    gang_members, organization_members,
)


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    TRANSGENDER = "transgender"
    UNKNOWN = "unknown"


class PersonType(str, enum.Enum):
    VICTIM = "victim"
    ACCUSED = "accused"
    OFFENDER = "offender"
    WITNESS = "witness"
    INFORMANT = "informant"
    OTHER = "other"


class CrimeCategory(str, enum.Enum):
    VIOLENT = "violent"
    PROPERTY = "property"
    FINANCIAL = "financial"
    CYBER = "cyber"
    DRUG_RELATED = "drug_related"
    ORGANIZED = "organized"
    TRAFFICKING = "trafficking"
    WHITE_COLLAR = "white_collar"
    JUVENILE = "juvenile"
    OTHER = "other"


class InvestigationStatusEnum(str, enum.Enum):
    REGISTERED = "registered"
    UNDER_INVESTIGATION = "under_investigation"
    EVIDENCE_COLLECTION = "evidence_collection"
    SUSPECT_IDENTIFIED = "suspect_identified"
    ARREST_MADE = "arrest_made"
    CHARGESHEET_FILED = "chargesheet_filed"
    UNDER_TRIAL = "under_trial"
    CONVICTED = "convicted"
    ACQUITTED = "acquitted"
    CLOSED = "closed"
    COLD_CASE = "cold_case"
    TRANSFERRED = "transferred"


class EvidenceType(str, enum.Enum):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    DOCUMENT = "document"
    FORENSIC = "forensic"
    TESTIMONY = "testimony"
    CCTV = "cctv"
    FINANCIAL = "financial"
    OTHER = "other"


class FIR(Base):
    __tablename__ = "firs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fir_number = Column(String(50), unique=True, nullable=False, index=True)
    police_station = Column(String(255), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    registration_date = Column(DateTime(timezone=True), nullable=False, index=True)
    act_sections = Column(ARRAY(String), nullable=True)
    brief_fact = Column(Text, nullable=False)
    is_cognizable = Column(Boolean, default=True)
    is_bailable = Column(Boolean, default=True)
    recorded_by = Column(String(255), nullable=False)
    io_name = Column(String(255), nullable=True)
    io_badge = Column(String(50), nullable=True)
    case_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    incidents = relationship("CrimeIncident", back_populates="fir")
    evidence_items = relationship("Evidence", back_populates="fir")

    __table_args__ = (
        {"comment": "First Information Reports"}
    )


class CrimeType(Base):
    __tablename__ = "crime_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(SAEnum(CrimeCategory), nullable=False, index=True)
    description = Column(Text, nullable=True)
    section_law = Column(String(255), nullable=True)
    severity_level = Column(Integer, nullable=True)
    is_bailable = Column(Boolean, default=True)
    is_cognizable = Column(Boolean, default=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("crime_types.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    parent = relationship("CrimeType", remote_side=[id], backref="subtypes")
    incidents = relationship("CrimeIncident", back_populates="crime_type")

    __table_args__ = (
        {"comment": "Crime type classifications"}
    )


class CrimeIncident(Base):
    __tablename__ = "crime_incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fir_id = Column(UUID(as_uuid=True), ForeignKey("firs.id", ondelete="CASCADE"), nullable=False, index=True)
    crime_type_id = Column(UUID(as_uuid=True), ForeignKey("crime_types.id"), nullable=False, index=True)
    incident_date = Column(Date, nullable=False, index=True)
    incident_time = Column(Time, nullable=True)
    reported_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=False)
    modus_operandi = Column(Text, nullable=True)
    property_value_loss = Column(Numeric(15, 2), nullable=True)
    injury_count = Column(Integer, default=0)
    fatality_count = Column(Integer, default=0)
    is_solved = Column(Boolean, default=False)
    is_heinous = Column(Boolean, default=False)
    day_of_week = Column(String(20), nullable=True)
    time_period = Column(String(50), nullable=True)
    case_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    fir = relationship("FIR", back_populates="incidents")
    crime_type = relationship("CrimeType", back_populates="incidents")
    victims = relationship("Victim", back_populates="incident")
    accused = relationship("Accused", back_populates="incident")
    witnesses = relationship("Witness", back_populates="incident")
    locations = relationship("Location", back_populates="incident")
    vehicles = relationship("Vehicle", secondary=incident_vehicles, back_populates="incidents")
    weapons = relationship("Weapon", secondary=incident_weapons, back_populates="incidents")
    phone_numbers_used = relationship("PhoneNumber", secondary=incident_phone_numbers, back_populates="incidents")
    emails_used = relationship("Email", secondary=incident_emails, back_populates="incidents")
    bank_accounts_used = relationship("BankAccount", secondary=incident_bank_accounts, back_populates="incidents")
    case_notes = relationship("CaseNote", back_populates="incident")
    statuses = relationship("InvestigationStatus", back_populates="incident")
    hotspots = relationship("CrimeHotspot", back_populates="incident")
    profiles = relationship("OffenderProfile", back_populates="incident")
    cases_similar_from = relationship(
        "SimilarCase",
        foreign_keys="SimilarCase.case_id",
        back_populates="case",
    )
    cases_similar_to = relationship(
        "SimilarCase",
        foreign_keys="SimilarCase.similar_case_id",
        back_populates="similar_case",
    )
    forecasts = relationship("CaseForecast", back_populates="incident")

    __table_args__ = (
        {"comment": "Crime incident records"}
    )


class Person(Base):
    __tablename__ = "persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False, index=True)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False, index=True)
    alias = Column(ARRAY(String), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    age_at_incident = Column(Integer, nullable=True)
    gender = Column(SAEnum(GenderEnum), nullable=True)
    nationality = Column(String(100), nullable=True)
    religion = Column(String(100), nullable=True)
    caste = Column(String(100), nullable=True)
    occupation = Column(String(255), nullable=True)
    education_level = Column(String(100), nullable=True)
    income_level = Column(String(50), nullable=True)
    identification_marks = Column(Text, nullable=True)
    aadhaar_number = Column(String(12), unique=True, nullable=True)
    pan_number = Column(String(10), unique=True, nullable=True)
    voter_id = Column(String(50), unique=True, nullable=True)
    driving_license = Column(String(50), nullable=True)
    passport_number = Column(String(20), unique=True, nullable=True)
    photo_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True)
    is_deceased = Column(Boolean, default=False)
    death_date = Column(Date, nullable=True)
    death_cause = Column(Text, nullable=True)
    case_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    addresses = relationship("Address", secondary=person_addresses, back_populates="persons")
    vehicles_owned = relationship("Vehicle", back_populates="owner")
    phone_numbers = relationship("PhoneNumber", back_populates="person")
    emails_rel = relationship("Email", back_populates="person")
    bank_accounts = relationship("BankAccount", back_populates="person")
    organizations = relationship("Organization", secondary=organization_members, back_populates="members")
    gangs = relationship("Gang", secondary=gang_members, back_populates="members")
    victim_records = relationship("Victim", back_populates="person")
    accused_records = relationship("Accused", back_populates="person")
    offender_records = relationship("Offender", back_populates="person")
    witness_records = relationship("Witness", back_populates="person")

    __table_args__ = (
        {"comment": "Unified person registry"}
    )


class Victim(Base):
    __tablename__ = "victims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    injury_description = Column(Text, nullable=True)
    injury_severity = Column(String(50), nullable=True)
    property_loss = Column(Numeric(15, 2), nullable=True)
    compensation_amount = Column(Numeric(15, 2), nullable=True)
    relationship_to_accused = Column(String(100), nullable=True)
    testimony = Column(Text, nullable=True)
    is_minor = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    person = relationship("Person", back_populates="victim_records")
    incident = relationship("CrimeIncident", back_populates="victims")

    __table_args__ = (
        {"comment": "Victim records linked to incidents"},
    )


class Accused(Base):
    __tablename__ = "accused"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    arrest_date = Column(DateTime(timezone=True), nullable=True)
    arrest_location = Column(String(255), nullable=True)
    arresting_officer = Column(String(255), nullable=True)
    charge_sections = Column(ARRAY(String), nullable=True)
    bail_status = Column(String(50), nullable=True)
    bail_amount = Column(Numeric(15, 2), nullable=True)
    custody_type = Column(String(50), nullable=True)
    is_juvenile = Column(Boolean, default=False)
    is_repeat_offender = Column(Boolean, default=False)
    criminal_history_id = Column(String(100), nullable=True)
    risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    person = relationship("Person", back_populates="accused_records")
    incident = relationship("CrimeIncident", back_populates="accused")

    __table_args__ = (
        {"comment": "Accused persons linked to incidents"},
    )


class Offender(Base):
    __tablename__ = "offenders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    conviction_date = Column(Date, nullable=True)
    sentencing_date = Column(Date, nullable=True)
    sentence_duration_years = Column(Integer, nullable=True)
    sentence_type = Column(String(100), nullable=True)
    prison_id = Column(String(100), nullable=True)
    parole_date = Column(Date, nullable=True)
    probation_end_date = Column(Date, nullable=True)
    recidivism_risk_score = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    person = relationship("Person", back_populates="offender_records")

    __table_args__ = (
        {"comment": "Convicted offender records"},
    )


class Witness(Base):
    __tablename__ = "witnesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    witness_type = Column(String(50), nullable=True)
    statement = Column(Text, nullable=True)
    statement_recorded_date = Column(DateTime(timezone=True), nullable=True)
    statement_recorded_by = Column(String(255), nullable=True)
    is_eye_witness = Column(Boolean, default=False)
    is_hostile = Column(Boolean, default=False)
    protection_required = Column(Boolean, default=False)
    credibility_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    person = relationship("Person", back_populates="witness_records")
    incident = relationship("CrimeIncident", back_populates="witnesses")

    __table_args__ = (
        {"comment": "Witness records"},
    )


class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    line1 = Column(String(255), nullable=False)
    line2 = Column(String(255), nullable=True)
    area = Column(String(255), nullable=True)
    landmark = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=True, index=True)
    country = Column(String(100), default="India")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    persons = relationship("Person", secondary=person_addresses, back_populates="addresses")

    __table_args__ = (
        {"comment": "Address registry"},
    )


class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    location_type = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True, index=True)
    district = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    is_crime_scene = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    incident = relationship("CrimeIncident", back_populates="locations")

    __table_args__ = (
        {"comment": "Geographic locations linked to incidents"},
    )


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    chassis_number = Column(String(50), nullable=True)
    engine_number = Column(String(50), nullable=True)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    color = Column(String(50), nullable=True)
    vehicle_type = Column(String(100), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    is_stolen = Column(Boolean, default=False)
    stolen_date = Column(Date, nullable=True)
    recovered_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    owner = relationship("Person", back_populates="vehicles_owned")
    incidents = relationship("CrimeIncident", secondary=incident_vehicles, back_populates="vehicles")

    __table_args__ = (
        {"comment": "Vehicle registry"},
    )


class Weapon(Base):
    __tablename__ = "weapons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    weapon_type = Column(String(100), nullable=False, index=True)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    caliber = Column(String(50), nullable=True)
    serial_number = Column(String(100), nullable=True)
    license_number = Column(String(100), nullable=True)
    owner_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_illegal = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    incidents = relationship("CrimeIncident", secondary=incident_weapons, back_populates="weapons")

    __table_args__ = (
        {"comment": "Weapon registry"},
    )


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number = Column(String(20), unique=True, nullable=False, index=True)
    imei = Column(String(50), nullable=True)
    operator = Column(String(100), nullable=True)
    sim_card_provider = Column(String(100), nullable=True)
    subscriber_name = Column(String(255), nullable=True)
    is_prepaid = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    registration_date = Column(Date, nullable=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    person = relationship("Person", back_populates="phone_numbers")
    incidents = relationship("CrimeIncident", secondary=incident_phone_numbers, back_populates="phone_numbers_used")

    __table_args__ = (
        {"comment": "Phone number registry"},
    )


class Email(Base):
    __tablename__ = "emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_address = Column(String(255), unique=True, nullable=False, index=True)
    provider = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    person = relationship("Person", back_populates="emails_rel")
    incidents = relationship("CrimeIncident", secondary=incident_emails, back_populates="emails_used")

    __table_args__ = (
        {"comment": "Email registry"},
    )


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    ifsc_code = Column(String(20), nullable=False, index=True)
    bank_name = Column(String(255), nullable=False)
    branch = Column(String(255), nullable=True)
    account_type = Column(String(50), nullable=True)
    account_holder_name = Column(String(255), nullable=False)
    is_joint_account = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    opening_date = Column(Date, nullable=True)
    closing_date = Column(Date, nullable=True)
    current_balance = Column(Numeric(15, 2), nullable=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    person = relationship("Person", back_populates="bank_accounts")
    incidents = relationship("CrimeIncident", secondary=incident_bank_accounts, back_populates="bank_accounts_used")
    outgoing_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.from_account_id",
        back_populates="from_account",
    )
    incoming_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.to_account_id",
        back_populates="to_account",
    )

    __table_args__ = (
        {"comment": "Bank account registry"},
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(100), unique=True, nullable=True)
    from_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False, index=True)
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default="INR")
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=True)
    mode = Column(String(50), nullable=True)
    reference = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_suspicious = Column(Boolean, default=False)
    suspicion_reason = Column(Text, nullable=True)
    risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    from_account = relationship("BankAccount", foreign_keys=[from_account_id], back_populates="outgoing_transactions")
    to_account = relationship("BankAccount", foreign_keys=[to_account_id], back_populates="incoming_transactions")

    __table_args__ = (
        {"comment": "Financial transaction records"},
    )


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(100), nullable=True)
    registration_number = Column(String(100), unique=True, nullable=True)
    gst_number = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    is_legitimate = Column(Boolean, default=True)
    is_under_investigation = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    members = relationship("Person", secondary=organization_members, back_populates="organizations")

    __table_args__ = (
        {"comment": "Organization registry"},
    )


class Gang(Base):
    __tablename__ = "gangs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    alias = Column(ARRAY(String), nullable=True)
    type = Column(String(100), nullable=True)
    territory = Column(String(255), nullable=True)
    area_of_operation = Column(String(255), nullable=True)
    primary_crime_type = Column(String(100), nullable=True)
    hierarchy_level = Column(String(50), nullable=True)
    estimated_strength = Column(Integer, nullable=True)
    leader_name = Column(String(255), nullable=True)
    rival_gangs = Column(ARRAY(String), nullable=True)
    is_active = Column(Boolean, default=True)
    risk_level = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    members = relationship("Person", secondary=gang_members, back_populates="gangs")

    __table_args__ = (
        {"comment": "Criminal gang registry"},
    )


class InvestigationStatus(Base):
    __tablename__ = "investigation_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SAEnum(InvestigationStatusEnum), nullable=False, index=True)
    remarks = Column(Text, nullable=True)
    updated_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    incident = relationship("CrimeIncident", back_populates="statuses")

    __table_args__ = (
        {"comment": "Investigation status tracking"},
    )


class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), nullable=True)
    is_confidential = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    incident = relationship("CrimeIncident", back_populates="case_notes")
    created_by_user = relationship("User", back_populates="case_notes")

    __table_args__ = (
        {"comment": "Investigation case notes"},
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fir_id = Column(UUID(as_uuid=True), ForeignKey("firs.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(SAEnum(EvidenceType), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    collection_date = Column(DateTime(timezone=True), nullable=True)
    collected_by = Column(String(255), nullable=True)
    location_found = Column(String(255), nullable=True)
    chain_of_custody = Column(JSONB, nullable=True)
    storage_location = Column(String(255), nullable=True)
    is_forensically_analyzed = Column(Boolean, default=False)
    forensic_report_url = Column(String(500), nullable=True)
    is_admissible = Column(Boolean, nullable=True)
    file_url = Column(String(500), nullable=True)
    case_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    fir = relationship("FIR", back_populates="evidence_items")

    __table_args__ = (
        {"comment": "Evidence records"},
    )
