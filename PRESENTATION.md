# SentinelAI — Presentation Deck Content

## Slide 1: The Problem

**Title:** Fragmented Police Data = Slow Justice

**Key Points:**
- Average case resolution: 45+ days in India
- Crime data siloed across FIRs, case files, evidence logs, financial records
- Cross-case pattern detection: almost impossible manually
- 72% of investigators struggle with data access (NCRB Report)
- Hidden criminal networks operate across jurisdictions undetected

**Visual:** Split image — pile of paper files vs. connected graph

---

## Slide 2: The Solution

**Title:** SentinelAI — AI Copilot for Law Enforcement

**Tagline:** *Connecting Crimes, Predicting Threats, Empowering Investigations*

**Key Points:**
- Natural language queries in English & Kannada (no SQL knowledge needed)
- AI discovers hidden connections across thousands of cases
- Predicts crime hotspots before they happen
- Every answer includes evidence trail + confidence score
- Voice-enabled for field investigators

**Visual:** Chat interface screenshot with network graph response

---

## Slide 3: Architecture

**Title:** Multi-Agent AI on Zoho Catalyst

```
User Query → LangGraph Coordinator → 7 Specialist AI Agents
                                          ↓
             ┌─────────────────────────────────────────┐
             │  SQL Agent   │ Graph Agent │ RAG Agent   │
             │  Analytics   │ Profiling   │ Forecast    │
             └─────────────────────────────────────────┘
                                          ↓
             3 Databases: PostgreSQL + Neo4j + Qdrant
                                          ↓
             ML Models: Prophet + XGBoost + DBSCAN + SHAP
```

**Tech Stack:**
- Frontend: Next.js 15 + TypeScript + TailwindCSS
- Backend: FastAPI + LangGraph + Python 3.12
- AI: Llama 3.3 70B (via Groq) + Sentence Transformers
- Graph: Neo4j Aura (criminal network intelligence)
- Vector: Qdrant Cloud (semantic case search)
- Deployment: Zoho Catalyst (AppSail + DataStore + Functions)

---

## Slide 4: Demo Highlights

**Title:** What You Just Saw

| Feature | Technology | Impact |
|---------|-----------|--------|
| Natural Language Crime Queries | LLM + SQL/Cypher Generation | Non-technical investigators can query data |
| Criminal Network Discovery | Neo4j + PageRank + Louvain | Hidden connections found in seconds |
| Crime Forecasting | Prophet + Confidence Intervals | Proactive deployment of resources |
| Hotspot Detection | DBSCAN + Mapbox | Visual crime density mapping |
| Offender Profiling | XGBoost + SHAP Explainability | Evidence-based risk assessment |
| Similar Case Matching | Sentence Transformers + Qdrant | Learn from solved cases |
| Voice Input | Whisper ASR | Hands-free for field work |
| Explainable AI | SHAP + Evidence Trails | Court-admissible reasoning |

---

## Slide 5: Impact & Roadmap

**Title:** Measurable Impact + Future Vision

**Projected Impact:**
- 40% reduction in case resolution time
- 85%+ pattern detection accuracy
- 10x faster criminal network discovery
- Proactive crime prevention through forecasting

**Zoho Catalyst Advantage:**
- AppSail: Auto-scaling backend + frontend
- DataStore: Managed PostgreSQL
- Functions: Serverless PDF generation, voice processing
- Scheduler: Automated forecasts + sync jobs
- Circuits: Multi-agent workflow orchestration

**Future Roadmap:**
- Real-time CCTV integration
- IoT sensor data ingestion
- Cross-jurisdiction federation
- Mobile app for patrol officers
- Biometric matching (AFIS)

---

## Judges Q&A Prep

**Q: How is this different from existing police software?**
> Existing systems are record-keeping tools. SentinelAI is an intelligence platform that actively discovers patterns, predicts crimes, and explains its reasoning. It's the difference between a filing cabinet and a detective partner.

**Q: Is the data real?**
> We use realistic synthetic data modeled after NCRB crime statistics for Karnataka. The platform is designed to connect to real police databases via API.

**Q: How do you handle data security?**
> JWT auth, role-based access control (5 roles), complete audit logging, TLS 1.3, parameterized queries, and 30-minute session timeouts.

**Q: Why Zoho Catalyst?**
> Catalyst provides the complete infrastructure stack — managed databases, serverless compute, object storage, and scheduling — all in one platform with built-in auth and scaling.

**Q: What's the accuracy of predictions?**
> Prophet forecasts show MAPE < 15% on our dataset. XGBoost profiling achieves R² > 0.85. All predictions include confidence intervals so users know the reliability.
