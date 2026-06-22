# SENTINEL AI — System Architecture

## Architecture Style

**Hybrid Microservices + Event-Driven Architecture**

The system combines:
- **REST API Gateway** — Synchronous request/response for real-time queries
- **Event-Driven Agents** — Asynchronous LangGraph orchestration
- **CQRS-like Data Access** — Separate read-optimized (Neo4j, Qdrant) and write-optimized (DataStore) paths
- **Batch ML Pipelines** — Scheduled Prophet forecasts, DBSCAN clustering

## Tier Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                   PRESENTATION TIER (AppSail)                     │
│  Next.js 15 · TypeScript · TailwindCSS · Shadcn · Recharts       │
│  React Flow · Mapbox GL · Server Components · Streaming SSR      │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    APPLICATION TIER (AppSail)                      │
│  FastAPI · Python 3.12 · LangGraph · LangChain · Celery Tasks    │
│  JWT Auth · Rate Limiting · Request Validation · Caching         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      ORCHESTRATION TIER                            │
│  LangGraph StateGraph · Multi-Agent Router · Circuit Breaker     │
│  Agent: Coord │ SQL │ Graph │ RAG │ Analytics │ Profile │ Forecast│
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                       DATA TIER                                    │
│  ┌────────────┐ ┌──────────┐ ┌───────────┐ ┌──────┐ ┌────────┐ │
│  │ DataStore  │ │ Neo4j    │ │ Qdrant    │ │Redis │ │Stratus │ │
│  │ (PG)       │ │ (Aura)   │ │ (Cloud)   │ │      │ │(ObjStr)│ │
│  └────────────┘ └──────────┘ └───────────┘ └──────┘ └────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      INTELLIGENCE TIER                             │
│  ML: DBSCAN · XGBoost · Prophet · NetworkX · SHAP                │
│  NLP: Sentence Transformers · Whisper · IndicTrans2              │
│  AI: OpenAI GPT-4 · LangChain                                    │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Sequences

### Query Flow
1. User submits natural language query via Chat UI
2. FastAPI validates JWT, logs to audit trail
3. LangGraph Coordinator classifies intent:
   - Data retrieval → SQL Agent
   - Relationship → Graph Agent
   - Semantic search → RAG Agent
   - Pattern analysis → Analytics Agent
   - Profile → Profiling Agent
   - Prediction → Forecast Agent
4. Specialist agent executes, writes results to state
5. Summarizer Agent generates natural language response
6. Response includes sources, confidence, reasoning chain

### Sync Flow
1. Zoho Scheduler triggers sync_neo4j every 15 minutes
2. Catalyst Function reads new/updated records from DataStore
3. Batch creates/updates Neo4j nodes and relationships
4. Embedding pipeline indexes new text in Qdrant

### Forecast Flow
1. Scheduler triggers daily_forecast at 06:00 daily
2. Prophet model loads historical data from DataStore
3. Generates 30-day crime forecasts with confidence intervals
4. Writes forecast results to DataStore and cache
5. If risk threshold exceeded → alert generation

## Scalability Design

| Component | Strategy |
|-----------|----------|
| FastAPI | Horizontal scaling via AppSail auto-scaling |
| DataStore | Managed PostgreSQL with read replicas |
| Neo4j Aura | Automatic cloud scaling |
| Qdrant Cloud | Horizontal sharding |
| Redis | Cluster mode for cache |
| Functions | Auto-scaled serverless |
| Frontend | CDN + AppSail scaling |

## Availability Design

- AppSail managed hosting with auto-recovery
- Neo4j Aura — 99.95% SLA with multi-region
- Qdrant Cloud — 99.9% SLA
- Redis — 99.99% with replication
- DataStore — 99.95% managed PostgreSQL
