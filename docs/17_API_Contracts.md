# SENTINEL AI — API Contracts

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://{app}.appsail.zoho.com/api/v1`

## Authentication

### POST /auth/login
```
Request: {"username": "investigator1", "password": "Secure@123"}
Response 200: {"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer", "expires_in": 30, "user": {...}}
Response 401: {"detail": "Invalid credentials"}
```

### POST /auth/register
```
Request: {"email": "...", "username": "...", "full_name": "...", "password": "...", "designation": "...", "department": "..."}
Response 201: {User object}
Response 409: {"detail": "User already exists"}
```

### POST /auth/refresh
```
Request: {"refresh_token": "eyJ..."}
Response 200: {"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer"}
```

### GET /auth/me | PUT /auth/me | PUT /auth/change-password
```
GET: Returns current user profile
PUT: Update profile fields
PUT /change-password: {"current_password": "...", "new_password": "..."}
```

## Chat

### POST /chat/converse
```
Request: {"session_id": "uuid", "message": "Show burglary cases in Mysore", "language": "en"}
Response 200: {"session_id": "uuid", "reply": "...", "sources": [...], "confidence_score": 0.95, "processing_time_ms": 452}
```

### GET /chat/history/{session_id} | DELETE /chat/history/{session_id}
```
GET: Returns conversation history for session
DELETE: Clears conversation history
```

## Cases

### GET /cases?page=1&per_page=20&crime_type=&district=&status=&date_from=&date_to=
```
Response 200: {"items": [CrimeIncidentRead], "total": 47, "page": 1, "per_page": 20, "total_pages": 3}
```

### GET /cases/{case_id}
```
Response 200: CrimeIncidentRead with crime_type, fir, locations, accused, victims
Response 404: {"detail": "Case not found"}
```

### GET /cases/{case_id}/similar?top_k=10
```
Response 200: [{"case_id": "uuid", "fir_number": "...", "similarity_score": 0.92, "crime_type": "...", "incident_date": "...", "matched_features": {...}}]
```

### GET /cases/{case_id}/timeline
```
Response 200: [{"case_id": "uuid", "event_type": "filed", "title": "...", "description": "...", "timestamp": "..."}]
```

### GET /cases/{case_id}/evidence
```
Response 200: [EvidenceRead]
```

### GET /cases/{case_id}/recommendations
```
Response 200: {"case_id": "uuid", "crime_type": "...", "resolution_patterns": [...], "avg_resolution_time_days": 45, "recommendations": [{"type": "evidence", "priority": "high", "suggestion": "...", "reason": "..."}], "similar_solved_count": 8}
```

## Network Analysis

### POST /network/analyze
```
Request: {"person_id": "uuid", "case_id": "uuid", "depth": 2}
Response 200: {"nodes": [...], "edges": [...], "centrality": {"label": 0.85}, "communities": [["label1", "label2"]]}
```

### GET /network/centrality/{person_id}
```
Response 200: {"person_id": "uuid", "centrality": {"degree": 0.75, "betweenness": 0.5, "closeness": 0.8, "pagerank": 0.6}, "top_connections": ["Name1", "Name2"]}
```

### GET /network/communities?gang_id=uuid
```
Response 200: [{"community_id": "MysoreGang", "members": ["Name1", "Name2"], "size": 5}]
```

### GET /network/paths/{person_a}/{person_b}?max_depth=4
```
Response 200: {"path": [{"person": "Name A"}, {"person": "Name B", "relationship": "CO_ACCUSED"}], "length": 1, "max_depth": 4}
```

### GET /network/suspicious-patterns
```
Response 200: {"isolated_persons": {"count": 15}, "high_degree_persons": [...], "suspicious_communities": [...]}
```

### GET /network/money-trail/{person_id}?max_depth=5
```
Response 200: {"person_id": "uuid", "trails": [{"path": ["ACC-1", "ACC-2"], "amounts": [10000], "hop_count": 1, "total_amount": 10000}]}
```

### GET /network/circular-transactions?min_cycle=3
```
Response 200: {"circular_transactions": [{"account_cycle": ["A", "B", "A"], "amounts": [50000, 50000], "cycle_length": 2, "total_cycled_amount": 100000}], "total_cycles_found": 1}
```

## Analytics

### GET /analytics/trends?district=&crime_type=&months=12
```
Response 200: [{"month": "2024-01", "crime_type": "burglary", "count": 23}]
```

### GET /analytics/hotspots?days=30&min_count=2
```
Response 200: [{"latitude": 12.34, "longitude": 76.56, "crime_count": 5, "crime_types": "burglary, theft"}]
```

### GET /analytics/sociological?district=&year=
```
Response 200: {"indicators": [{"district": "...", "unemployment_rate": 5.2, "crime_rate_per_100k": 120}], "ml_analysis": {"r2_score": 0.82, "factor_importance": [...], "shap_explanations": {...}}}
```

### GET /analytics/statistics?district=&date_from=&date_to=
```
Response 200: {"total_cases": 1200, "solved_cases": 800, "heinous_cases": 45, "total_injuries": 230, "total_fatalities": 12, "avg_loss": 15000}
```

### GET /analytics/offender-profiles?min_prior_cases=1&limit=20
```
Response 200: [{"person_id": "uuid", "name": "Name", "age": 35, "gender": "male", "prior_cases": 3, "risk_score": 0.72, "risk_level": "High"}]
```

### GET /analytics/financial?min_amount=100000&limit=20
```
Response 200: {"suspicious": [...], "high_value": [...], "stats": {"total": 500, "suspicious_count": 12, "total_volume": 5000000}}
```

### POST /analytics/financial/detect
```
Request: {"amount": 500000, "transaction_type": "transfer", "hour": 14, "day_of_week": 3}
Response 200: {"is_fraudulent": true, "fraud_probability": 0.92, "risk_level": "high"}
```

### POST /analytics/forecast
```
Request: {"forecast_type": "crime_volume", "district": "mysore", "crime_type_id": "uuid", "days_ahead": 30}
Response 200: {"forecast_data": [{"date": "2024-02-15", "predicted": 23.5, "lower_bound": 18.2, "upper_bound": 29.1}], "model_used": "Prophet", "confidence_level": 0.95}
```

## Alerts

### GET /alerts?include_read=false&limit=20
```
Response 200: [{"id": "uuid", "type": "heinous_crime|forecast_anomaly|pattern_match", "severity": "high|medium|low", "title": "...", "message": "...", "created_at": "...", "is_read": false}]
```

### GET /alerts/count
```
Response 200: {"total": 15, "unread": 3}
```

## Export

### POST /export/pdf
```
Request: {"title": "Crime Report", "content": "...", "format": "A4"}
Response: application/pdf binary
```

### POST /export/pdf/case/{case_id}
```
Response: application/pdf binary with case details
```

### POST /export/csv/{resource_type}?crime_type=&district=
```
Response: text/csv binary
resource_type: "cases", "analytics", "persons"
```

## Voice

### POST /voice/transcribe
```
Request: multipart/form-data with audio file
Response 200: {"text": "...", "language": "kn", "confidence": 0.95, "processing_time_ms": 1200}
```

### POST /voice/transcribe-base64
```
Request: {"audio_base64": "...", "format": "wav"}
Response 200: {"text": "...", "language": "kn", "confidence": 0.95}
```

## Admin

### GET /admin/users?skip=0&limit=20 | POST /admin/users | PUT /admin/users/{id} | DELETE /admin/users/{id}
```
GET: [UserAdminRead]
POST: Create user (same body as /auth/register plus is_active, roles)
PUT: Update user fields
DELETE: Soft-delete user
```

### PUT /admin/users/{id}/deactivate | PUT /admin/users/{id}/role
```
PUT /deactivate: {"is_active": false}
PUT /role: {"role_id": "uuid"}
```

### GET /admin/roles | GET /admin/audit-logs?skip=0&limit=50 | GET /admin/system/health
```
GET /roles: [{"id": "uuid", "name": "investigator", "description": "...", "is_active": true}]
GET /audit-logs: [{"id": "uuid", "user_id": "uuid", "action": "LOGIN", "resource_type": "auth", "created_at": "..."}]
GET /system/health: {"status": "healthy", "database": "connected", "cache": "connected", "version": "1.0.0"}
```

## Catalyst

### GET /catalyst/config | GET /catalyst/services/status
```
GET /config: {"project_id": "...", "project_name": "SentinelAI", "environment": "production", "region": "...", "catalyst_functions": ["export-report", "generate-pdf", "process-voice"]}
GET /services/status: {"database": "healthy", "cache": "healthy", "neo4j": "healthy", "qdrant": "healthy", "openai": "healthy"}
```

### POST /catalyst/sync/neo4j | POST /catalyst/sync/embeddings | POST /catalyst/ml/train/{model}
```
POST /sync/neo4j: {"synced_nodes": 150, "synced_relationships": 320, "status": "success"}
POST /sync/embeddings: {"collections_updated": 5, "points_upserted": 1200, "status": "success"}
POST /ml/train/{model}: {"status": "success", "metrics": {...}} where model in ("forecast", "hotspot", "profiling", "financial", "sociological", "similarity")
```

### POST /catalyst/functions/invoke/{fn}
```
Invoke Catalyst function: fn in ("export-report", "generate-pdf", "process-voice")
```

## Common Error Responses
```
400: {"detail": "Validation error"}
401: {"detail": "Invalid or expired token"}
403: {"detail": "Requires one of roles: supervisor, admin"}
404: {"detail": "Resource not found"}
429: {"detail": "Rate limit exceeded"}
500: {"detail": "Internal server error"}
```

## Authentication
All endpoints except /auth/*, /health, /docs, /redoc require:
`Authorization: Bearer {access_token}`
