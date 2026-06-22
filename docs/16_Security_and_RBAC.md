# SENTINEL AI — Security and RBAC

## Authentication: JWT + Zoho Catalyst Auth

### Token Flow
1. User submits credentials → POST /auth/login
2. Server validates → returns access_token (30min) + refresh_token (7d)
3. Access token included in Authorization: Bearer header
4. Refresh token used to get new access tokens
5. Zoho Catalyst Auth can optionally replace custom JWT

### JWT Payload Structure
```json
{
    "sub": "user-uuid",
    "username": "investigator1",
    "roles": ["investigator"],
    "permissions": ["cases:read", "cases:write"],
    "type": "access",
    "exp": 1700000000,
    "iat": 1699998200
}
```

## Role-Based Access Control

### Role Hierarchy
```
Admin (full access)
  └── Supervisor (elevated access)
       ├── Analyst (analytics access)
       ├── Investigator (case operations)
       └── Policymaker (read-only strategic)
```

### Permission Matrix

| Resource | Investigator | Analyst | Supervisor | PolicyMaker | Admin |
|----------|:---:|:---:|:---:|:---:|:---:|
| Cases: Read | ✓ | ✓ | ✓ | ✓ | ✓ |
| Cases: Write | ✓ | ✗ | ✓ | ✗ | ✓ |
| Cases: Delete | ✗ | ✗ | ✗ | ✗ | ✓ |
| Evidence: Read | ✓ | ✓ | ✓ | ✗ | ✓ |
| Evidence: Write | ✓ | ✗ | ✓ | ✗ | ✓ |
| Analytics: Read | ✗ | ✓ | ✓ | ✓ | ✓ |
| Analytics: Export | ✗ | ✓ | ✓ | ✓ | ✓ |
| Network: Read | ✓ | ✓ | ✓ | ✗ | ✓ |
| Forecast: Read | ✗ | ✓ | ✓ | ✓ | ✓ |
| Profiles: Read | ✓ | ✓ | ✓ | ✗ | ✓ |
| Users: Read | ✗ | ✗ | ✓ | ✗ | ✓ |
| Users: Write | ✗ | ✗ | ✗ | ✗ | ✓ |
| Audit: Read | ✗ | ✗ | ✓ | ✗ | ✓ |
| System: Admin | ✗ | ✗ | ✗ | ✗ | ✓ |

## Audit Logging

### Logged Actions
- All CREATE, UPDATE, DELETE operations on cases, evidence, users
- All EXPORT operations (PDF, CSV)
- All LOGIN attempts (success/failure)
- All SEARCH operations (query text, filters, result count)
- LOGOUT events

### Audit Log Schema
```json
{
    "id": "uuid",
    "user_id": "uuid",
    "action": "create|read|update|delete|login|export|search",
    "resource_type": "case|evidence|user|report",
    "resource_id": "string",
    "description": "User X updated case FIR-2024-001",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "created_at": "2024-01-15T10:30:00Z"
}
```

## Data Security

| Concern | Measure |
|---------|---------|
| Password storage | bcrypt (12 rounds) |
| Transmission | TLS 1.3 |
| Token storage | HttpOnly cookies / Secure storage |
| SQL Injection | Parameterized queries via SQLAlchemy |
| XSS | Input sanitization + CSP headers |
| CSRF | Double-submit cookie pattern |
| Rate limiting | 100 req/min per user (Catalyst Gateway) |
| Session timeout | 30 min inactivity |

## Catalyst Authentication Integration

```python
# Option 1: Custom JWT (default)
from app.core.security import create_access_token

# Option 2: Zoho Catalyst Auth (enterprise)
from zcatalyst.auth import authenticated_user
user = authenticated_user.get_user_details(request)
```
