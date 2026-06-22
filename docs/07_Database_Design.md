# SENTINEL AI — Database Design

## Technology: Catalyst DataStore (PostgreSQL 16)

## Schema Overview

### 1. Authentication & Authorization

#### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX |
| username | VARCHAR(100) | UNIQUE, NOT NULL, INDEX |
| full_name | VARCHAR(255) | NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| phone | VARCHAR(20) | UNIQUE |
| designation | VARCHAR(255) | |
| badge_number | VARCHAR(50) | UNIQUE |
| department | VARCHAR(255) | |
| jurisdiction | VARCHAR(255) | |
| is_active | BOOLEAN | DEFAULT true |
| is_superuser | BOOLEAN | DEFAULT false |
| last_login | TIMESTAMPTZ | |
| preferred_language | VARCHAR(10) | DEFAULT 'en' |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() |

#### roles
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL, INDEX |
| description | VARCHAR(255) | |
| priority_level | VARCHAR(50) | DEFAULT 'standard' |
| is_active | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

#### permissions
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | UNIQUE, NOT NULL, INDEX |
| description | VARCHAR(255) | |
| resource | VARCHAR(100) | NOT NULL |
| action | VARCHAR(50) | NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

### 2. Crime Data

#### firs
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| fir_number | VARCHAR(50) | UNIQUE, NOT NULL, INDEX |
| police_station | VARCHAR(255) | NOT NULL, INDEX |
| district | VARCHAR(100) | NOT NULL, INDEX |
| state | VARCHAR(100) | NOT NULL |
| registration_date | TIMESTAMPTZ | NOT NULL, INDEX |
| act_sections | TEXT[] | |
| brief_fact | TEXT | NOT NULL |
| is_cognizable | BOOLEAN | DEFAULT true |
| is_bailable | BOOLEAN | DEFAULT true |
| recorded_by | VARCHAR(255) | NOT NULL |
| io_name | VARCHAR(255) | |
| io_badge | VARCHAR(50) | |
| metadata | JSONB | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() |

#### crime_types
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | UNIQUE, NOT NULL |
| category | ENUM | NOT NULL, INDEX |
| description | TEXT | |
| severity_level | INTEGER | |
| is_bailable | BOOLEAN | DEFAULT true |
| is_cognizable | BOOLEAN | DEFAULT true |
| parent_id | UUID | FK → crime_types.id |

#### crime_incidents
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| fir_id | UUID | FK → firs.id, NOT NULL, INDEX |
| crime_type_id | UUID | FK → crime_types.id, NOT NULL, INDEX |
| incident_date | DATE | NOT NULL, INDEX |
| incident_time | TIME | |
| reported_date | TIMESTAMPTZ | NOT NULL |
| description | TEXT | NOT NULL |
| modus_operandi | TEXT | |
| property_value_loss | NUMERIC(15,2) | |
| injury_count | INTEGER | DEFAULT 0 |
| fatality_count | INTEGER | DEFAULT 0 |
| is_solved | BOOLEAN | DEFAULT false |
| is_heinous | BOOLEAN | DEFAULT false |
| day_of_week | VARCHAR(20) | |
| time_period | VARCHAR(50) | |
| metadata | JSONB | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() |

### 3. Person Registry

#### persons
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| first_name | VARCHAR(100) | NOT NULL, INDEX |
| middle_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | NOT NULL, INDEX |
| alias | TEXT[] | |
| date_of_birth | DATE | |
| gender | ENUM | |
| nationality | VARCHAR(100) | |
| occupation | VARCHAR(255) | |
| education_level | VARCHAR(100) | |
| aadhaar_number | VARCHAR(12) | UNIQUE |
| pan_number | VARCHAR(10) | UNIQUE |
| phone | VARCHAR(20) | INDEX |
| email | VARCHAR(255) | |
| is_deceased | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() |

### 4. Financial

#### bank_accounts
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| account_number | VARCHAR(50) | UNIQUE, NOT NULL |
| ifsc_code | VARCHAR(20) | NOT NULL, INDEX |
| bank_name | VARCHAR(255) | NOT NULL |
| account_type | VARCHAR(50) | |
| person_id | UUID | FK → persons.id |
| is_active | BOOLEAN | DEFAULT true |
| current_balance | NUMERIC(15,2) | |

#### transactions
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| from_account_id | UUID | FK → bank_accounts.id, INDEX |
| to_account_id | UUID | FK → bank_accounts.id, INDEX |
| amount | NUMERIC(15,2) | NOT NULL |
| transaction_date | TIMESTAMPTZ | NOT NULL, INDEX |
| transaction_type | VARCHAR(50) | |
| mode | VARCHAR(50) | |
| is_suspicious | BOOLEAN | DEFAULT false |
| suspicion_reason | TEXT | |
| risk_score | FLOAT | |

### 5. Indexes

```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_incidents_date_type ON crime_incidents(incident_date, crime_type_id);
CREATE INDEX idx_incidents_district ON crime_incidents(incident_date) WHERE district IS NOT NULL;
CREATE INDEX idx_transactions_date_amount ON transactions(transaction_date, amount);
CREATE INDEX idx_transactions_chain ON transactions(from_account_id, to_account_id, transaction_date);
CREATE INDEX idx_firs_district_date ON firs(district, registration_date);
CREATE INDEX idx_persons_name_trgm ON persons USING gin (first_name gin_trgm_ops, last_name gin_trgm_ops);
CREATE INDEX idx_locations_coords ON locations(latitude, longitude);
CREATE INDEX idx_conversations_session ON conversation_history(session_id, created_at);
CREATE INDEX idx_audit_time ON audit_logs(created_at DESC);
```
