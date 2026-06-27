"""Initial schema migration for SentinelAI.

Revision ID: 001_initial
Revises: None
Create Date: 2026-06-27

This migration creates all tables defined in the SQLAlchemy models.
Since the app uses `Base.metadata.create_all()` at startup, this migration
serves as the canonical schema definition for production deployments.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users & Auth
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), unique=True, nullable=True),
        sa.Column('designation', sa.String(255), nullable=True),
        sa.Column('badge_number', sa.String(50), unique=True, nullable=True),
        sa.Column('department', sa.String(255), nullable=True),
        sa.Column('jurisdiction', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_superuser', sa.Boolean(), default=False, nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('profile_image_url', sa.String(500), nullable=True),
        sa.Column('preferred_language', sa.String(10), default='en', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('priority_level', sa.String(50), default='standard', nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Crime Types
    op.create_table(
        'crime_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('category', sa.String(50), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('section_law', sa.String(255), nullable=True),
        sa.Column('severity_level', sa.Integer(), nullable=True),
        sa.Column('is_bailable', sa.Boolean(), default=True),
        sa.Column('is_cognizable', sa.Boolean(), default=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crime_types.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # FIRs
    op.create_table(
        'firs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('fir_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('police_station', sa.String(255), nullable=False, index=True),
        sa.Column('district', sa.String(100), nullable=False, index=True),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('registration_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('act_sections', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('brief_fact', sa.Text(), nullable=False),
        sa.Column('is_cognizable', sa.Boolean(), default=True),
        sa.Column('is_bailable', sa.Boolean(), default=True),
        sa.Column('recorded_by', sa.String(255), nullable=False),
        sa.Column('io_name', sa.String(255), nullable=True),
        sa.Column('io_badge', sa.String(50), nullable=True),
        sa.Column('case_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Crime Incidents
    op.create_table(
        'crime_incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('fir_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('firs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('crime_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crime_types.id'), nullable=False, index=True),
        sa.Column('incident_date', sa.Date(), nullable=False, index=True),
        sa.Column('incident_time', sa.Time(), nullable=True),
        sa.Column('reported_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('modus_operandi', sa.Text(), nullable=True),
        sa.Column('property_value_loss', sa.Numeric(15, 2), nullable=True),
        sa.Column('injury_count', sa.Integer(), default=0),
        sa.Column('fatality_count', sa.Integer(), default=0),
        sa.Column('is_solved', sa.Boolean(), default=False),
        sa.Column('is_heinous', sa.Boolean(), default=False),
        sa.Column('day_of_week', sa.String(20), nullable=True),
        sa.Column('time_period', sa.String(50), nullable=True),
        sa.Column('case_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Persons
    op.create_table(
        'persons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('first_name', sa.String(100), nullable=False, index=True),
        sa.Column('middle_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=False, index=True),
        sa.Column('alias', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('age_at_incident', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        sa.Column('religion', sa.String(100), nullable=True),
        sa.Column('caste', sa.String(100), nullable=True),
        sa.Column('occupation', sa.String(255), nullable=True),
        sa.Column('education_level', sa.String(100), nullable=True),
        sa.Column('income_level', sa.String(50), nullable=True),
        sa.Column('identification_marks', sa.Text(), nullable=True),
        sa.Column('aadhaar_number', sa.String(12), unique=True, nullable=True),
        sa.Column('pan_number', sa.String(10), unique=True, nullable=True),
        sa.Column('voter_id', sa.String(50), unique=True, nullable=True),
        sa.Column('driving_license', sa.String(50), nullable=True),
        sa.Column('passport_number', sa.String(20), unique=True, nullable=True),
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True, index=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('is_deceased', sa.Boolean(), default=False),
        sa.Column('death_date', sa.Date(), nullable=True),
        sa.Column('death_cause', sa.Text(), nullable=True),
        sa.Column('case_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Locations
    op.create_table(
        'locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crime_incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('location_type', sa.String(100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True, index=True),
        sa.Column('district', sa.String(100), nullable=True, index=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('is_crime_scene', sa.Boolean(), default=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Conversation History
    op.create_table(
        'conversation_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('session_id', sa.String(255), nullable=False, index=True),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, index=True),
    )

    # Performance indexes
    op.create_index('idx_incidents_date_type', 'crime_incidents', ['incident_date', 'crime_type_id'])
    op.create_index('idx_conversations_session', 'conversation_history', ['session_id', 'created_at'])
    op.create_index('idx_audit_time', 'audit_logs', [sa.text('created_at DESC')])


def downgrade() -> None:
    op.drop_index('idx_audit_time')
    op.drop_index('idx_conversations_session')
    op.drop_index('idx_incidents_date_type')
    op.drop_table('audit_logs')
    op.drop_table('conversation_history')
    op.drop_table('locations')
    op.drop_table('persons')
    op.drop_table('crime_incidents')
    op.drop_table('firs')
    op.drop_table('crime_types')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
