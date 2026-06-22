# SENTINEL AI — API Contracts

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://{app}.appsail.zoho.com/api/v1`

## Authentication

### POST /auth/login
```
Request:
{
    "username": "investigator1",
    "password": "Secure@123"
}

Response 200:
{
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 30,
    "user": {
        "id": "uuid",
        "username": "investigator1",
        "full_name": "Inspector Rajesh Kumar",
        "roles": [{"name": "investigator"}]
    }
}

Response 401:
{
    "detail": "Invalid credentials"
}
```

### POST /auth/register
```
Request:
{
    "email": "officer@police.gov.in",
    "username": "officer1",
    "full_name": "Officer Name",
    "password": "Secure@123",
    "designation": "Sub Inspector",
    "badge_number": "SI-2024-001",
    "department": "Mysore Police",
    "jurisdiction": "Mysore North"
}

Response 201: {User object}
Response 409: {"detail": "User already exists"}
```

## Chat

### POST /chat/converse
```
Headers: Authorization: Bearer {token}

Request:
{
    "session_id": "session-uuid",
    "message": "Show me all burglary cases in Mysore last 3 months",
    "language": "en"
}

Response 200:
{
    "session_id": "session-uuid",
    "reply": "Found 47 burglary cases in Mysore from Nov 2024 to Jan 2025...",
    "language": "en",
    "sources": [
        {"type": "database", "table": "crime_incidents", "records": 47}
    ],
    "confidence_score": 1.0,
    "processing_time_ms": 452,
    "reasoning_chain": [
        "Intent classified: sql_query",
        "SQL generated: SELECT ... WHERE crime_type='burglary' AND district='mysore'",
        "Query executed: 47 results",
        "Response generated"
    ],
    "visualizations": [
        {
            "type": "bar_chart",
            "title": "Burglary Cases by Month",
            "data": [...]
        }
    ]
}
```

## Cases

### GET /cases?page=1&per_page=20&crime_type=burglary&district=mysore
```
Response 200:
{
    "items": [CrimeIncidentRead, ...],
    "total": 47,
    "page": 1,
    "per_page": 20,
    "total_pages": 3
}
```

### GET /cases/{case_id}/similar?top_k=10
```
Response 200:
{
    "items": [
        {
            "case_id": "uuid",
            "fir_number": "FIR-2024-003",
            "similarity_score": 0.92,
            "crime_type": "burglary",
            "incident_date": "2024-01-10",
            "matched_features": {
                "modus_operandi": "forced_entry",
                "time_period": "night",
                "location_type": "residential"
            }
        }
    ]
}
```

## Network Analysis

### POST /network/analyze
```
Request:
{
    "person_id": "uuid",
    "depth": 2
}

Response 200:
{
    "nodes": [
        {"id": "uuid-1", "label": "Ravi Kumar", "type": "Person", "metadata": {...}},
        {"id": "uuid-2", "label": "Mysore Street Crew", "type": "Gang", "metadata": {...}}
    ],
    "edges": [
        {"source": "uuid-1", "target": "uuid-2", "relationship": "MEMBER_OF_GANG", "weight": 1.0}
    ],
    "centrality": {"uuid-1": 0.85, "uuid-2": 0.92},
    "communities": [["uuid-1", "uuid-3", "uuid-4"]]
}
```

## Analytics

### POST /analytics/forecast
```
Request:
{
    "forecast_type": "crime_volume",
    "district": "mysore",
    "crime_type_id": "uuid",
    "days_ahead": 30
}

Response 200:
{
    "forecast_data": [
        {"date": "2024-02-15", "predicted": 23.5, "lower_bound": 18.2, "upper_bound": 29.1}
    ],
    "model_used": "prophet",
    "confidence_level": 0.95
}
```

## Common Error Responses

```
400 Bad Request:
{"detail": "Validation error", "errors": [{"field": "email", "message": "Invalid email"}]}

401 Unauthorized:
{"detail": "Invalid or expired token"}

403 Forbidden:
{"detail": "Requires one of roles: supervisor, admin"}

404 Not Found:
{"detail": "Case not found"}

429 Too Many Requests:
{"detail": "Rate limit exceeded"}
```
