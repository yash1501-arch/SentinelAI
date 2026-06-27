# SentinelAI

**Connecting Crimes, Predicting Threats, Empowering Investigations**

SentinelAI is an AI-powered crime intelligence platform that enables law enforcement personnel to query, analyze, and predict crime patterns through natural language. It combines a multi-agent LLM system with graph databases, vector search, and predictive ML to provide actionable intelligence in seconds.

## Key Features

- **Conversational AI** — Natural language queries processed by 7 specialized agents
- **Crime Network Analysis** — Interactive graph visualization of criminal connections (Neo4j)
- **Predictive Forecasting** — Crime volume and hotspot predictions (Prophet, XGBoost)
- **Semantic Case Matching** — Find similar cases via vector embeddings (Qdrant)
- **Offender Profiling** — Risk scoring with behavioral pattern analysis and SHAP explainability
- **Crime Hotspot Mapping** — Geospatial visualization of crime density (Mapbox)
- **Smart Alerts** — AI-generated alerts from forecasts, patterns, and anomalies
- **Voice Input** — Speak queries using OpenAI Whisper transcription
- **Multi-language** — Supports English and Kannada
- **PDF/CSV Export** — Generate investigation reports on demand

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js 15)                   │
│  Dashboard │ Chat │ Cases │ Map │ Network │ Forecasting │ ...│
└──────────────────────────┬───────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼───────────────────────────────────┐
│                   Backend (FastAPI + Python)                    │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              LangGraph Multi-Agent Orchestrator           │  │
│  │                                                           │  │
│  │  Coordinator → [SQL│Graph│RAG│Analytics│Profile│Forecast] │  │
│  │                          ↓                                │  │
│  │                     Summarizer                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ PostgreSQL │  │  Neo4j   │  │  Qdrant  │  │   Redis   │  │
│  │  (Cases)   │  │ (Graphs) │  │  (RAG)   │  │  (Cache)  │  │
│  └────────────┘  └──────────┘  └──────────┘  └───────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## The 7-Agent System

| Agent | Purpose | Data Source |
|-------|---------|-------------|
| Coordinator | Intent classification & routing | OpenAI GPT-4 |
| SQL Agent | Structured data queries | PostgreSQL |
| Graph Agent | Relationship/network analysis | Neo4j (Cypher) |
| RAG Agent | Semantic document search | Qdrant (Vector) |
| Analytics Agent | Trends, hotspots, patterns | PostgreSQL |
| Profiling Agent | Offender risk assessment | XGBoost + SHAP |
| Forecast Agent | Crime prediction | Prophet + XGBoost |
| Summarizer | Response synthesis | OpenAI GPT-4 |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui |
| Charts | Recharts |
| Maps | Mapbox GL |
| Graphs | React Flow (@xyflow/react) |
| Backend | FastAPI, Python 3.13, SQLAlchemy (async) |
| AI/LLM | LangGraph, OpenAI GPT-4, LangChain |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| ML | scikit-learn, XGBoost, Prophet, HDBSCAN, SHAP |
| Primary DB | PostgreSQL |
| Graph DB | Neo4j |
| Vector DB | Qdrant |
| Cache | Redis |
| Voice | OpenAI Whisper |
| Auth | JWT (python-jose + passlib) |
| CI/CD | GitHub Actions, Docker |

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL 15+
- Redis (optional, for caching)
- OpenAI API key

### Backend

```bash
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and OpenAI key

# Run server (auto-creates tables and seeds demo data)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin@123 |
| Investigator | investigator | Investigator@123 |
| Analyst | analyst | Analyst@123 |

## API Documentation

With the backend running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
SentinelAI/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── agents/        # 7 LangGraph agents
│   │   │   └── endpoints/     # REST API routes
│   │   ├── core/              # Config, DB, security
│   │   ├── llm/               # LangGraph state machine
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Neo4j, Qdrant, OpenAI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js pages
│   │   ├── components/        # UI components
│   │   ├── services/          # API service layer
│   │   └── store/             # Zustand state
│   └── package.json
├── tests/                     # pytest suite
└── .github/workflows/         # CI pipeline
```

## License

Private — Hackathon Project
