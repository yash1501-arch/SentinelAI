import pytest
from datetime import datetime, timezone, date
from app.models.user import User, Role, Permission
from app.models.crime import (
    FIR, CrimeIncident, CrimeType, CrimeCategory,
    Person, Victim, Accused, Address, Location,
    Vehicle, Weapon, PhoneNumber, BankAccount, Transaction,
    Organization, Gang,
)


class TestUserModel:
    def test_user_creation(self):
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed_pwd",
        )
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.preferred_language == "en"

    def test_user_str(self):
        user = User(email="a@b.com", username="test", full_name="Test", hashed_password="h")
        assert str(user) == "<User test (a@b.com)>"


class TestFIRModel:
    def test_fir_creation(self):
        fir = FIR(
            fir_number="FIR-2024-001",
            police_station="Mysore North",
            district="Mysore",
            state="Karnataka",
            registration_date=datetime.now(timezone.utc),
            brief_fact="Burglary reported at residential premises",
            recorded_by="SI Kumar",
        )
        assert fir.fir_number == "FIR-2024-001"
        assert fir.is_cognizable is True


class TestCrimeIncident:
    def test_incident_creation(self):
        incident = CrimeIncident(
            fir_id="00000000-0000-0000-0000-000000000001",
            crime_type_id="00000000-0000-0000-0000-000000000002",
            incident_date=date(2024, 1, 15),
            reported_date=datetime.now(timezone.utc),
            description="Residential burglary at night",
        )
        assert incident.incident_date == date(2024, 1, 15)
        assert incident.is_solved is False
        assert incident.injury_count == 0


class TestNetworkModel:
    def test_person_creation(self):
        person = Person(
            first_name="Ravi",
            last_name="Kumar",
            date_of_birth=date(1990, 5, 15),
            occupation="Driver",
        )
        assert person.first_name == "Ravi"
        assert person.is_deceased is False

    def test_gang_creation(self):
        gang = Gang(
            name="Mysore Street Crew",
            type="Organized Theft",
            territory="Mysore City",
            estimated_strength=15,
            risk_level="high",
        )
        assert gang.is_active is True
        assert gang.name == "Mysore Street Crew"

    def test_transaction_creation(self):
        tx = Transaction(
            from_account_id="00000000-0000-0000-0000-000000000001",
            to_account_id="00000000-0000-0000-0000-000000000002",
            amount=500000.00,
            transaction_date=datetime.now(timezone.utc),
            is_suspicious=True,
            suspicion_reason="High value transfer between known associates",
        )
        assert tx.amount == 500000.00
        assert tx.is_suspicious is True
