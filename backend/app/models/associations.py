from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("assigned_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

incident_vehicles = Table(
    "incident_vehicles",
    Base.metadata,
    Column("incident_id", UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("vehicle_id", UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(50), nullable=True),
)

incident_weapons = Table(
    "incident_weapons",
    Base.metadata,
    Column("incident_id", UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("weapon_id", UUID(as_uuid=True), ForeignKey("weapons.id", ondelete="CASCADE"), primary_key=True),
)

incident_phone_numbers = Table(
    "incident_phone_numbers",
    Base.metadata,
    Column("incident_id", UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("phone_id", UUID(as_uuid=True), ForeignKey("phone_numbers.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(50), nullable=True),
)

incident_emails = Table(
    "incident_emails",
    Base.metadata,
    Column("incident_id", UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("email_id", UUID(as_uuid=True), ForeignKey("emails.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(50), nullable=True),
)

incident_bank_accounts = Table(
    "incident_bank_accounts",
    Base.metadata,
    Column("incident_id", UUID(as_uuid=True), ForeignKey("crime_incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("account_id", UUID(as_uuid=True), ForeignKey("bank_accounts.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(50), nullable=True),
)

person_addresses = Table(
    "person_addresses",
    Base.metadata,
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
    Column("address_id", UUID(as_uuid=True), ForeignKey("addresses.id", ondelete="CASCADE"), primary_key=True),
    Column("address_type", String(50), default="current"),
)

gang_members = Table(
    "gang_members",
    Base.metadata,
    Column("gang_id", UUID(as_uuid=True), ForeignKey("gangs.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(100), nullable=True),
    Column("joined_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("is_active", Boolean, default=True),
)

organization_members = Table(
    "organization_members",
    Base.metadata,
    Column("organization_id", UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
    Column("role", String(100), nullable=True),
    Column("joined_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)
