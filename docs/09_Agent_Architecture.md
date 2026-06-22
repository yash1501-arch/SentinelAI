# SENTINEL AI — Agent Architecture (LangGraph)

## Overview

Sentinel AI uses a **LangGraph Multi-Agent Orchestrator** with 8 specialized agents. The Coordinator Agent receives user queries, classifies intent, and routes to appropriate specialist agents. Results flow through the graph state, and the Summarizer Agent generates the final response.

## State Definition

```python
from typing import TypedDict, List, Optional, Dict, Any

class AgentState(TypedDict):
    query: str
    session_id: str
    user_id: str
    language: str               # "en" | "kn"
    context: List[Dict]         # Conversation history
    intent: Optional[str]       # Classified intent
    sql_query: Optional[str]
    sql_result: Optional[List[Dict]]
    cypher_query: Optional[str]
    graph_result: Optional[List[Dict]]
    rag_query: Optional[str]
    rag_result: Optional[List[Dict]]
    analytics_result: Optional[Dict]
    profiling_result: Optional[Dict]
    forecast_result: Optional[Dict]
    response: Optional[str]
    sources: List[Dict]         # Evidence references
    confidence_score: float
    reasoning_chain: List[str]
    visualizations: List[Dict]  # Chart configs
```

## Agent Definitions

### 1. Coordinator Agent
```
Role:       Query classification and routing
Input:      User query + conversation context
Output:     Intent classification + routing to specialist
Logic:      LLM-based intent classification
            Categories: sql | graph | rag | analytics | profile | forecast | general
```

### 2. SQL Agent
```
Role:       Structured data queries
Backend:    Catalyst DataStore (PostgreSQL)
Method:     NL → SQL via LLM, validate, execute
Capable:    FIR lookup, statistics, case filtering, person search
```

### 3. Graph Agent
```
Role:       Relationship and network queries
Backend:    Neo4j Aura
Method:     NL → Cypher via LLM, validate, execute
Capable:    Network analysis, shortest path, community detection
```

### 4. RAG Agent
```
Role:       Semantic search and similar case retrieval
Backend:    Qdrant Cloud + Sentence Transformers
Method:     Embed query → search Qdrant → rank results
Capable:    Similar cases, evidence search, precedent matching
```

### 5. Analytics Agent
```
Role:       Pattern discovery and trend analysis
Backend:    DataStore + ML models
Method:     SQL aggregation + ML analytics
Capable:    Hotspot detection, trend analysis, sociological insights
```

### 6. Profiling Agent
```
Role:       Offender behavioral profiling
Backend:    XGBoost model + SHAP explainer
Method:     Feature extraction → ML inference → SHAP explanation
Capable:    Risk scoring, archetype classification, recidivism prediction
```

### 7. Forecast Agent
```
Role:       Crime prediction and forecasting
Backend:    Prophet model
Method:     Time-series forecasting with confidence intervals
Capable:    Crime count prediction, hotspot forecasting, gang activity
```

### 8. Summarizer Agent
```
Role:       Final response generation
Method:     LLM-based synthesis of all agent results
Output:     Natural language response + evidence + confidence
```

## Graph Flow

```
                   ┌──────────────┐
                   │   USER QUERY │
                   └──────┬───────┘
                          │
                   ┌──────▼───────┐
                   │  COORDINATOR │
                   │   (Classify) │
                   └──────┬───────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼──────┐
    │ SQL Agent   │ │Graph Agent│ │ RAG Agent  │
    │ (DataStore) │ │ (Neo4j)   │ │ (Qdrant)   │
    └──────┬──────┘ └─────┬─────┘ └─────┬──────┘
           │              │              │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼──────┐
    │Analytics    │ │Profiling  │ │ Forecast   │
    │Agent        │ │Agent      │ │ Agent      │
    └──────┬──────┘ └─────┬─────┘ └─────┬──────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
                   ┌──────▼───────┐
                   │  SUMMARIZER  │
                   │  (Generate)  │
                   └──────┬───────┘
                          │
                   ┌──────▼───────┐
                   │   RESPONSE   │
                   │  + Evidence  │
                   │  + Confidence│
                   │  + Reasoning │
                   └──────────────┘
```
