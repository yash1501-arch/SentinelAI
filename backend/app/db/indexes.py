from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


ADDITIONAL_INDEXES = [
    # Crime Incidents
    "CREATE INDEX IF NOT EXISTS idx_incidents_date_type ON crime_incidents(incident_date, crime_type_id)",
    "CREATE INDEX IF NOT EXISTS idx_incidents_solved ON crime_incidents(is_solved) WHERE is_solved = FALSE",
    "CREATE INDEX IF NOT EXISTS idx_incidents_heinous ON crime_incidents(is_heinous) WHERE is_heinous = TRUE",
    "CREATE INDEX IF NOT EXISTS idx_incidents_day_period ON crime_incidents(day_of_week, time_period)",

    # Persons
    "CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(last_name, first_name)",
    "CREATE INDEX IF NOT EXISTS idx_persons_dob ON persons(date_of_birth)",
    "CREATE INDEX IF NOT EXISTS idx_persons_aadhaar ON persons(aadhaar_number) WHERE aadhaar_number IS NOT NULL",

    # FIRs
    "CREATE INDEX IF NOT EXISTS idx_firs_district_date ON firs(district, registration_date)",
    "CREATE INDEX IF NOT EXISTS idx_firs_station ON firs(police_station, registration_date)",

    # Transactions
    "CREATE INDEX IF NOT EXISTS idx_transactions_from ON transactions(from_account_id, transaction_date)",
    "CREATE INDEX IF NOT EXISTS idx_transactions_to ON transactions(to_account_id, transaction_date)",
    "CREATE INDEX IF NOT EXISTS idx_transactions_suspicious ON transactions(is_suspicious) WHERE is_suspicious = TRUE",

    # Locations
    "CREATE INDEX IF NOT EXISTS idx_locations_city ON locations(city)",
    "CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(location_type)",

    # Case Notes
    "CREATE INDEX IF NOT EXISTS idx_case_notes_incident ON case_notes(incident_id, created_at DESC)",

    # Investigation Status
    "CREATE INDEX IF NOT EXISTS idx_inv_status_current ON investigation_status(incident_id, status, updated_at DESC)",

    # Evidence
    "CREATE INDEX IF NOT EXISTS idx_evidence_fir ON evidence(fir_id, evidence_type)",

    # Conversations
    "CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversation_history(session_id, created_at)",
    "CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversation_history(user_id, created_at DESC)",

    # Audit
    "CREATE INDEX IF NOT EXISTS idx_audit_user_action ON audit_logs(user_id, action, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id)",

    # Similar Cases
    "CREATE INDEX IF NOT EXISTS idx_similar_cases_score ON similar_cases(similarity_score DESC)",
]


async def create_additional_indexes(db: AsyncSession):
    for index_sql in ADDITIONAL_INDEXES:
        try:
            await db.execute(text(index_sql))
        except Exception:
            pass
    await db.commit()
