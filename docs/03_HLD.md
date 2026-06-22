# SENTINEL AI — High-Level Design (HLD)

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USERS                                       │
│  Investigator │ Analyst │ Supervisor │ PolicyMaker │ Admin          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS
┌──────────────────────────────▼──────────────────────────────────────┐
│                   NEXT.JS FRONTEND (AppSail)                        │
│  Dashboard │ Chat │ Network │ Map │ Forecast │ Cases │ Admin       │
│  TailwindCSS │ Shadcn │ React Query │ React Flow │ Mapbox          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼──────────────────────────────────────┐
│               FASTAPI BACKEND (AppSail)                             │
│  JWT Auth │ Rate Limit │ Audit │ Caching │ File Upload              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│              LANGGRAPH MULTI-AGENT ORCHESTRATOR                      │
│                                                                     │
│  ┌────────────┐  ┌────────┐  ┌────────┐  ┌──────────┐             │
│  │ Coordinator│  │  SQL   │  │ Graph  │  │   RAG    │             │
│  │   Agent    │─▶│ Agent  │─▶│ Agent  │─▶│  Agent   │             │
│  └────────────┘  └────────┘  └────────┘  └──────────┘             │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Analytics│  │ Profiling│  │ Forecast │  │Summarizer│           │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                         DATA LAYER                                  │
│                                                                     │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────────────┐     │
│  │ Catalyst DataStore│  │  Neo4j Aura   │  │  Qdrant Cloud    │     │
│  │ (PostgreSQL)     │  │  (Graph DB)    │  │  (Vector DB)     │     │
│  └─────────────────┘  └────────────────┘  └──────────────────┘     │
│                                                                     │
│  ┌─────────────────┐  ┌────────────────┐                           │
│  │  Redis          │  │  Stratus       │                           │
│  │  (Cache/Session)│  │  (Object Store)│                           │
│  └─────────────────┘  └────────────────┘                           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                         ML LAYER                                    │
│  DBSCAN │ XGBoost │ Prophet │ NetworkX │ SHAP │ Isolation Forest   │
│  Sentence Transformers │ Whisper │ IndicTrans2                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Technology | Responsibility |
|-----------|-----------|---------------|
| Frontend | Next.js 15 + TypeScript | UI rendering, state, visualization |
| API Gateway | FastAPI | Request routing, auth, validation |
| Orchestrator | LangGraph | Multi-agent workflow coordination |
| SQL Store | Catalyst DataStore | Structured crime data |
| Graph Store | Neo4j Aura | Relationship intelligence |
| Vector Store | Qdrant Cloud | Semantic search |
| Cache | Redis | Session, conversation context |
| Object Store | Catalyst Stratus | Evidence files, PDFs |
| ML Pipeline | Scikit-learn/XGBoost/Prophet | Analytics & forecasting |
| Voice | Whisper + IndicTrans2 | STT & translation |

## Zoho Catalyst Services Used

| Service | Purpose |
|---------|---------|
| AppSail | Host frontend (Node.js) and backend (Python) |
| DataStore | Managed PostgreSQL for structured data |
| Functions | Serverless PDF generation, voice processing |
| Authentication | JWT + built-in RBAC |
| Stratus | Evidence file and PDF storage |
| Scheduler | Cron-based forecast and sync jobs |
| Circuits | Multi-agent workflow orchestration |
| API Gateway | Rate limiting, CORS, API management |

## Data Flow

1. User sends natural language query via Chat interface
2. Frontend authenticates via Catalyst Auth, sends to FastAPI
3. FastAPI validates JWT, logs to Audit, routes to LangGraph
4. Coordinator Agent classifies intent, routes to specialist agents
5. Agents execute queries against respective data stores
6. Results flow back through Summarizer for response generation
7. Response includes evidence trail, confidence scores, and visualizations
8. Frontend renders response with charts, graphs, or network visualizations
