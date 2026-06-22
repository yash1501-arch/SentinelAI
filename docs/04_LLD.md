# SENTINEL AI — Low-Level Design (LLD)

## 1. Module Structure

```
sentinelai/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   │   ├── endpoints/     # Route handlers
│   │   │   └── agents/        # LangGraph agents
│   │   ├── core/              # Config, security, database
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response
│   │   ├── services/          # Business logic services
│   │   ├── llm/               # LangChain/LangGraph setup
│   │   ├── ml/                # ML model wrappers
│   │   └── utils/             # Helpers
│   └── migrations/            # Alembic DB migrations
├── frontend/                   # Next.js Frontend
│   └── src/
│       ├── app/               # Pages (auth, dashboard, etc.)
│       ├── components/        # UI components
│       ├── lib/               # Utilities
│       ├── hooks/             # React hooks
│       ├── services/          # API service layer
│       ├── store/             # State management
│       └── types/             # TypeScript types
├── catalyst_functions/        # Zoho Catalyst Functions
├── graph-services/            # Neo4j schemas & analytics
│   ├── cypher/                # Cypher queries
│   ├── analytics/             # Graph algorithms
│   └── ingestion/             # Data sync scripts
├── ml-services/               # ML model pipelines
│   ├── forecasting/           # Prophet models
│   ├── profiling/             # XGBoost profiling
│   ├── hotspot/               # DBSCAN clustering
│   ├── financial/             # Isolation Forest
│   ├── network/               # NetworkX algorithms
│   ├── similarity/            # Embedding search
│   └── sociological/          # Correlation analysis
└── docs/                      # Documentation
```

## 2. API Endpoint Design

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /auth/login | User login | No |
| POST | /auth/register | User registration | No |
| POST | /auth/refresh | Refresh token | Yes |
| GET | /auth/me | Current user profile | Yes |
| POST | /chat/converse | Send message | Yes |
| GET | /chat/history/{session} | Get conversation history | Yes |
| GET | /cases/ | List cases with filters | Yes |
| GET | /cases/{id} | Case detail | Yes |
| GET | /cases/{id}/timeline | Case timeline | Yes |
| GET | /cases/{id}/similar | Similar cases | Yes |
| GET | /cases/{id}/evidence | Case evidence | Yes |
| GET | /analytics/trends | Crime trends | Yes |
| GET | /analytics/hotspots | Crime hotspots | Yes |
| POST | /analytics/forecast | Get forecasts | Yes |
| GET | /analytics/sociological | Sociological insights | Yes |
| GET | /analytics/statistics | Crime statistics | Yes |
| POST | /network/analyze | Network analysis | Yes |
| GET | /network/centrality/{id} | Person centrality | Yes |
| GET | /network/communities | Detect communities | Yes |
| GET | /network/paths/{a}/{b} | Find connection path | Yes |
| POST | /export/pdf | Export to PDF | Yes |
| POST | /export/csv/{type} | Export to CSV | Yes |
| GET | /admin/users | List users | Admin |
| GET | /admin/audit-logs | Audit logs | Admin |

## 3. Key Service Interfaces

### Neo4jService (neo4j_service.py)
- `create_person_node(data)` — Create/merge person in graph
- `create_crime_node(data)` — Create/merge crime node
- `link_person_to_crime(person_id, crime_id, role)` — Link person to incident
- `get_person_network(person_id, depth)` — Get ego network
- `find_shortest_path(p1, p2, max_depth)` — Shortest path
- `detect_suspicious_transactions(amount, chain)` — Money trail
- `run_query(query, params)` — Raw Cypher execution

### QdrantService (qdrant_service.py)
- `initialize_collections()` — Create vector collections
- `upsert_points(collection, points)` — Index vectors
- `search_similar(collection, vector, top_k, filter)` — Semantic search

### EmbeddingService (embedding_service.py)
- `embed_texts(texts)` — Batch embedding
- `embed_query(query)` — Single query embedding

## 4. LangGraph Agent Design

```python
class AgentState(TypedDict):
    query: str
    session_id: str
    user_id: str
    language: str
    context: List[Dict]
    sql_result: Optional[List[Dict]]
    graph_result: Optional[List[Dict]]
    rag_result: Optional[List[Dict]]
    analytics_result: Optional[Dict]
    profiling_result: Optional[Dict]
    forecast_result: Optional[Dict]
    response: Optional[str]
    sources: List[Dict]
    confidence_score: float
    reasoning_chain: List[str]
```

Each agent is a LangGraph node that reads from and writes to AgentState.

## 5. Security Implementation

- JWT with access (30min) and refresh (7d) tokens
- Password hashing via bcrypt (passlib)
- Role-based permission matrix checked at endpoint level
- Audit logging for all CREATE, UPDATE, DELETE, EXPORT actions
- Input validation via Pydantic schemas
- Rate limiting via Catalyst API Gateway
