# SENTINEL AI — Deployment Guide

## Deployment Platform: Zoho Catalyst

### Prerequisites
1. Zoho Catalyst account with AppSail access
2. Neo4j Aura instance (cloud)
3. Qdrant Cloud instance
4. Redis Cloud instance
5. OpenAI API key
6. Mapbox access token

## Deployment Steps

### Step 1: Catalyst Project Setup
```bash
# Install Catalyst CLI
npm install -g zoho-catalyst-cli

# Initialize project
catalyst init

# Login to Catalyst
catalyst login

# Link to project
catalyst project:link --project-id <PROJECT_ID>
```

### Step 2: Deploy Backend (AppSail)
```bash
# Navigate to backend directory
cd backend

# Deploy to AppSail
catalyst appsail:deploy --name sentinelai-backend

# Set environment variables
catalyst appsail:config set \
    --name sentinelai-backend \
    --key OPENAI_API_KEY \
    --value "sk-..."
```

### Step 3: Deploy Frontend (AppSail)
```bash
cd frontend
npm run build
catalyst appsail:deploy --name sentinelai-frontend
```

### Step 4: Deploy Functions
```bash
cd catalyst_functions
catalyst function:deploy --name generate-pdf
catalyst function:deploy --name export-report
catalyst function:deploy --name process-voice
```

### Step 5: Configure Scheduler
```bash
# Schedule daily forecast generation
catalyst scheduler:create \
    --name daily-crime-forecast \
    --cron "0 6 * * *" \
    --function daily_forecast
```

### Step 6: Configure Circuits
```yaml
# catalyst.yml circuits section handles workflow orchestration
# No additional CLI commands needed
```

## Environment Configuration

### Production Environment Variables
```bash
# Core
DEBUG=false
SECRET_KEY=<generated-secure-key>

# Catalyst
CATALYST_PROJECT_ID=<project-id>
CATALYST_CLIENT_ID=<client-id>
CATALYST_CLIENT_SECRET=<client-secret>
CATALYST_REFRESH_TOKEN=<refresh-token>

# Neo4j Aura
NEO4J_URI=neo4j+s://<instance>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<password>

# Qdrant Cloud
QDRANT_HOST=<instance>.cloud.qdrant.io
QDRANT_API_KEY=<api-key>

# Redis
REDIS_HOST=<redis-instance>.cloud.redislabs.com
REDIS_PASSWORD=<password>

# OpenAI
OPENAI_API_KEY=sk-...
```

## CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Catalyst

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy Backend
        run: |
          cd backend
          catalyst appsail:deploy --name sentinelai-backend --auto-approve
      - name: Deploy Frontend
        run: |
          cd frontend
          npm run build
          catalyst appsail:deploy --name sentinelai-frontend --auto-approve
```

## Health Checks

### Endpoints
```bash
# System health
GET /health
Response: {"status": "healthy", "service": "SentinelAI"}

# Service status
GET /api/v1/catalyst/services/status
Response: {
    "appsail": "healthy",
    "datastore": "healthy",
    "neo4j_aura": "healthy",
    "qdrant_cloud": "healthy",
    "redis": "healthy"
}
```

## Monitoring & Logging

- **Catalyst Console**: AppSail dashboard for metrics
- **Neo4j Aura Console**: Graph DB monitoring
- **Qdrant Cloud Console**: Vector DB metrics
- **Custom Logging**: Loguru-based JSON logs shipped to Catalyst

## Rollback Procedure

```bash
# Rollback backend
catalyst appsail:rollback --name sentinelai-backend --version <previous-version>

# Rollback frontend
catalyst appsail:rollback --name sentinelai-frontend --version <previous-version>

# Rollback function
catalyst function:rollback --name generate-pdf --version <previous-version>
```
