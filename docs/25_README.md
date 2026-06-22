# SENTINEL AI

**Connecting Crimes, Predicting Threats, Empowering Investigations**

Enterprise-grade AI-powered Crime Intelligence and Investigative Platform for law enforcement agencies.

---

## Overview

Sentinel AI is a production-grade intelligence platform that enables investigators, analysts, supervisors, and policymakers to interact with crime databases using natural language while receiving evidence-backed analytical insights.

Built on **Zoho Catalyst** cloud infrastructure with **LangGraph** multi-agent orchestration, **Neo4j** knowledge graphs, **Qdrant** vector search, and enterprise-grade **RBAC** security.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, TailwindCSS, Shadcn UI, React Query, Mapbox, React Flow, Recharts |
| Backend | FastAPI, Python 3.12, LangGraph, LangChain |
| AI/ML | OpenAI GPT-4, Sentence Transformers, XGBoost, Prophet, DBSCAN, SHAP |
| Graph | Neo4j Aura, NetworkX |
| Vector DB | Qdrant Cloud |
| Cache | Redis |
| Voice | Whisper ASR, IndicTrans2 |
| Infrastructure | Zoho Catalyst (AppSail, DataStore, Functions, Scheduler) |

---

## Key Features

### 1. Conversational AI
- Natural language querying in English and Kannada
- Multi-turn conversation with context memory
- Voice input via Whisper ASR
- IndicTrans2 translation support
- PDF conversation export

### 2. Criminal Network Analysis
- Neo4j knowledge graph with 12 node types, 12 relationship types
- PageRank, Degree/Betweenness Centrality
- Louvain Community Detection
- Interactive React Flow visualization

### 3. Crime Pattern Analytics
- DBSCAN hotspot detection
- Seasonal and temporal analysis
- Mapbox geospatial mapping
- Time-series trend visualization

### 4. Offender Profiling
- Behavioral archetype classification
- Modus operandi pattern matching
- Recidivism risk scoring (XGBoost)
- SHAP-based feature explanations

### 5. Similar Case Retrieval
- Semantic search via Sentence Transformers
- Qdrant vector database
- Top-K similar cases with similarity scores

### 6. Financial Crime Intelligence
- Money trail analysis on Neo4j
- Circular transaction detection
- Isolation Forest anomaly detection

### 7. Crime Forecasting
- Prophet time-series forecasting
- Hotspot and gang activity prediction
- Confidence intervals and early warnings

### 8. Explainable AI
- Every answer includes evidence trail
- Confidence scores and source references
- SHAP reasoning chains

### 9. Security & RBAC
- JWT authentication
- 5 roles: Investigator, Analyst, Supervisor, PolicyMaker, Admin
- Complete audit logging

---

## System Architecture

```
Users → Next.js Frontend (AppSail) → FastAPI Backend (AppSail)
  → LangGraph Multi-Agent Orchestrator
    → Coordinator → SQL | Graph | RAG | Analytics | Profile | Forecast | Summarizer
  → Data Layer: DataStore | Neo4j Aura | Qdrant | Redis
  → ML Layer: DBSCAN | XGBoost | Prophet | NetworkX | SHAP
```

---

## Project Structure

```
├── backend/              # FastAPI application
│   ├── app/api/v1/       # API endpoints & agents
│   ├── app/core/         # Config, security, database
│   ├── app/models/       # SQLAlchemy ORM models
│   ├── app/schemas/      # Pydantic schemas
│   ├── app/services/     # Neo4j, Qdrant, Embedding services
│   └── migrations/       # Alembic migrations
├── frontend/             # Next.js application
├── catalyst_functions/   # Zoho Catalyst Functions
├── graph-services/       # Neo4j schemas & analytics
├── ml-services/          # ML model pipelines
└── docs/                 # 25 documentation files
```

---

## Documentation

| # | Document | Description |
|---|----------|-------------|
| 01 | PRD | Product Requirements Document |
| 02 | Vision & Scope | Product vision and scope |
| 03 | HLD | High-Level Design |
| 04 | LLD | Low-Level Design |
| 05 | System Architecture | Architecture overview |
| 06 | ERD | Entity Relationship Diagram |
| 07 | Database Design | PostgreSQL schema |
| 08 | Neo4j Graph Design | Graph schema & Cypher |
| 09 | Agent Architecture | LangGraph multi-agent |
| 10 | RAG Architecture | Vector search design |
| 11 | ML Architecture | ML pipeline design |
| 12 | Hotspot Analysis | DBSCAN methodology |
| 13 | Offender Profiling | Behavioral analysis |
| 14 | Forecasting | Prophet predictions |
| 15 | Explainable AI | SHAP & confidence |
| 16 | Security & RBAC | Auth & permissions |
| 17 | API Contracts | REST API documentation |
| 18 | User Flows | User interaction flows |
| 19 | Sequence Diagrams | System sequence diagrams |
| 20 | Prompt Engineering | Agent prompts |
| 21 | Testing Strategy | Test plan |
| 22 | Deployment Guide | Catalyst deployment |
| 23 | Demo Script | 15-min demo script |
| 24 | Presentation Content | Slide deck content |
| 25 | README | This document |

---

## Quick Start

```bash
# Clone repository
git clone <repo-url>
cd sentinelai

# Backend setup
cd backend
python -m venv venv
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Run backend
uvicorn app.main:app --reload

# Frontend setup
cd ../frontend
npm install
npm run dev

# Access
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## License

Proprietary — Law Enforcement Use
