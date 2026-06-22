from app.models.user import User, Role, Permission
from app.models.crime import (
    FIR, CrimeIncident, CrimeType, Victim, Accused, Offender, Witness,
    Address, Location, Vehicle, Weapon, PhoneNumber, Email,
    BankAccount, Transaction, Organization, Gang,
    InvestigationStatus, CaseNote, Evidence,
)
from app.models.analytics import (
    ConversationHistory, AuditLog, CrimeHotspot, SocialIndicator,
    SimilarCase, CaseForecast, OffenderProfile,
)
from app.models.associations import (
    incident_vehicles, incident_weapons, incident_phone_numbers,
    incident_emails, incident_bank_accounts, person_addresses,
    gang_members, organization_members,
)
