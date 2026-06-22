# SENTINEL AI — Product Requirements Document (PRD)

## 1. Executive Summary

Sentinel AI is an enterprise-grade AI-powered Crime Intelligence and Investigative Platform designed for law enforcement agencies. It enables investigators, analysts, supervisors, and policymakers to interact with crime databases using natural language while receiving evidence-backed analytical insights.

**Tagline:** *Connecting Crimes, Predicting Threats, Empowering Investigations*

## 2. Problem Statement

Law enforcement agencies face critical challenges:
- Siloed data spread across FIRs, case files, evidence logs, and financial records
- Inability to detect cross-case patterns and hidden criminal networks
- Manual, time-consuming investigative processes
- Lack of predictive intelligence for crime prevention
- Limited accessibility for non-technical investigators

## 3. Product Vision

Build an intelligent platform that unifies crime data, applies AI and graph analytics to discover hidden relationships, forecasts criminal activity, and empowers every investigation with explainable, evidence-backed insights.

## 4. Target Users

| Role | Primary Need |
|------|-------------|
| Investigator | Case insights, evidence linking, suspect identification |
| Analyst | Pattern discovery, trend analysis, reporting |
| Supervisor | Case oversight, resource allocation, performance tracking |
| Policymaker | Strategic intelligence, crime statistics, policy support |
| Admin | System configuration, user management, audit |

## 5. Core Features

### 5.1 Conversational AI
- Natural language querying in English and Kannada
- Multi-turn conversation with context memory
- Voice input via Whisper ASR
- Translated output via IndicTrans2
- PDF export of conversations

### 5.2 Criminal Network Analysis
- Neo4j knowledge graph with 12 node types and 12 relationship types
- PageRank, Degree/Betweenness Centrality
- Louvain Community Detection for gang structures
- Interactive React Flow visualization

### 5.3 Crime Pattern Analytics
- DBSCAN-based hotspot detection
- Seasonal and temporal pattern analysis
- Geospatial mapping via Mapbox
- Time-series trend visualization

### 5.4 Sociological Crime Intelligence
- Multi-factor correlation (age, gender, income, education, urbanization)
- XGBoost-based importance analysis
- SHAP explainability reports

### 5.5 Offender Profiling
- Behavioral archetype classification
- Modus operandi pattern matching
- Recidivism risk scoring
- SHAP-based feature explanations

### 5.6 Similar Case Retrieval
- Semantic search via Sentence Transformers + Qdrant
- Top-K similar cases with similarity scores
- Outcome-based recommendations

### 5.7 Financial Crime Intelligence
- Money trail analysis on Neo4j
- Circular transaction detection
- Isolation Forest for anomaly detection

### 5.8 Crime Forecasting
- Prophet-based time-series forecasting
- Hotspot and gang activity prediction
- Early warning alert system
- Confidence intervals on all predictions

### 5.9 Explainable AI
- Every answer includes evidence trail
- Confidence scores
- Source document references
- SHAP-based reasoning chains

### 5.10 Security & RBAC
- JWT authentication
- Role-based access (Investigator, Analyst, Supervisor, Policymaker, Admin)
- Complete audit logging
- Data traceability

## 6. Success Metrics

| Metric | Target |
|--------|--------|
| Case resolution time reduction | 40% |
| Pattern detection accuracy | >85% |
| User satisfaction score | >4.5/5 |
| System uptime | 99.9% |
| Query response time | <3 seconds |
