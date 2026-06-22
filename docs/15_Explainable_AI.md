# SENTINEL AI — Explainable AI (XAI)

## Design Principle

Every output from Sentinel AI must include:
1. **Evidence** — Source documents and records
2. **Confidence Score** — Quantitative certainty measure
3. **Reasoning Chain** — Step-by-step logic
4. **SHAP Explanations** — Feature importance for ML outputs

The system **never** produces unsupported conclusions or hallucinations.

## XAI Layers

### Layer 1: Data Source Attribution
```
Query: "Show burglary cases in Mysore last 3 months"

Response:
Found 47 burglary cases in Mysore (Nov 2024 - Jan 2025).

Sources:
  └─ FIR-2024-0891 to FIR-2025-0023 (47 records)
  └─ CrimeIncident table, district=mysore, crime_type=burglary
  └─ Date range: 2024-11-01 to 2025-01-31
  └─ Query: SELECT * FROM crime_incidents
            WHERE district = 'mysore'
            AND crime_type_id = '...'
            AND incident_date BETWEEN '2024-11-01' AND '2025-01-31'

Confidence: 1.0 (Exact database match)
```

### Layer 2: ML Prediction Explanation (SHAP)
```
Query: "What is the risk score for offender Ravi Kumar?"

Response:
Risk Score: 0.86 (CRITICAL)

SHAP Explanation:
  Feature                   Impact    Value
  ──────────────────────────────────────────
  prior_convictions        +0.25      4 priors
  crime_type_severity      +0.15      Robbery (severity: 8)
  gang_affiliation         +0.10      Mysore Street Crew
  weapon_used              +0.08      Knife
  education_level          -0.12      Graduate
  age                      -0.05      35 years

  Model: XGBoost (accuracy: 0.89)
  Training data: 12,450 convicted offenders
  Confidence interval: [0.81, 0.91]

Reasoning Chain:
  1. Retrieved offender record for Ravi Kumar (ID: ...)
  2. Extracted 15 features from person + criminal history
  3. XGBoost model predicted risk score = 0.86
  4. SHAP analysis identified top risk factors
  5. Cross-referenced with 124 similar offenders
```

### Layer 3: Network Analysis Explanation
```
Query: "Find connections between Ravi Kumar and Mysore Street Crew"

Response:
Direct connection found: Ravi Kumar → MEMBER_OF_GANG → Mysore Street Crew

Path:
  Ravi Kumar
  └─ KNOWS → Suresh (associate, since 2022)
     └─ MEMBER_OF_GANG → Mysore Street Crew (active)

Confidence: 0.95
  └─ Relationship confirmed by: CDR analysis (phone records)
  └─ Gang membership confirmed by: 3 independent witness statements
  └─ Data freshness: sync 12 minutes ago
```

## Confidence Scoring

| Scenario | Score | Logic |
|----------|-------|-------|
| Exact DB match | 1.0 | Deterministic SQL |
| Aggregation/Stats | 0.95 | SQL with aggregation |
| Graph relationship | 0.85-0.95 | Neo4j query with provenance |
| RAG semantic search | 0.70-0.90 | Vector similarity + reranking |
| ML prediction | Variable | Model confidence + calibration |
| LLM synthesis | 0.50-0.80 | GPT-4 with retrieval context |

## Reasoning Chain Format

```json
{
    "steps": [
        {
            "step": 1,
            "agent": "coordinator",
            "action": "intent_classification",
            "result": "graph_query",
            "tokens_used": 45
        },
        {
            "step": 2,
            "agent": "graph_agent",
            "action": "cypher_generation",
            "result": "MATCH (p:Person)...",
            "tokens_used": 120
        },
        {
            "step": 3,
            "agent": "graph_agent",
            "action": "neo4j_execution",
            "result": "3 nodes, 4 relationships",
            "execution_time_ms": 45
        },
        {
            "step": 4,
            "agent": "summarizer",
            "action": "response_generation",
            "result": "final_answer",
            "tokens_used": 250
        }
    ],
    "total_tokens": 415,
    "total_time_ms": 1230
}
```
