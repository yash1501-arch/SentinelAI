# SENTINEL AI — Demo Script

## Duration: 15 Minutes

## Setup (2 min)
- Ensure test data loaded in DataStore
- Neo4j Aura instance running
- Qdrant collection indexed
- All services healthy (show /health endpoint)

## Demo Flow

### Scene 1: Conversational Intelligence (3 min)
```
Investigator login → Chat interface

Q: "Show me all burglary cases in Mysore last 3 months"

Expected: System shows 47 cases with bar chart by month
Evidence: SQL query shown in reasoning chain
Confidence: 1.0

Q: "Who are the repeat offenders among them?"

Expected: System filters to 12 repeat offenders
Shows names, case counts, last offense date

Q: "Show their financial transactions"

Expected: Graph Agent activates
Neo4j network visualization shows money flows
React Flow renders interactive graph
```

### Scene 2: Network Analysis (3 min)
```
Switch to Network Analysis tab

Search: "Ravi Kumar"

Expected: 
- Ego network graph with depth=2
- Colored by community (Louvain)
- Node size = PageRank centrality
- Click node shows details panel

Click "Mysore Street Crew" node
Expected: Gang details, members, territory, risk level
```

### Scene 3: Crime Map & Hotspots (3 min)
```
Switch to Crime Map

Expected:
- Mapbox map with heatmap overlay
- DBSCAN clusters as circles
- Click cluster shows crime type distribution
- Filter by crime type, date range

Filter: "Show only burglary hotspots in last 7 days"
Expected: Map updates, fewer clusters highlighted
```

### Scene 4: Forecasting Dashboard (2 min)
```
Switch to Forecasting

Expected:
- 30-day Prophet forecast chart
- Upper/lower confidence bands
- Weekly pattern decomposition
- Alert indicators for spike predictions

Hover on peak: "Predicted: 23 cases, CI: [18, 29]"
```

### Scene 5: Offender Profile (2 min)
```
Search: "Ravi Kumar" in Profiling

Expected:
- Risk score: 0.86 (CRITICAL)
- Archetype: Organized Criminal
- SHAP force plot showing top factors
- Recidivism probability: 65%
- MO profile summary
```

### Scene 6: Export (1 min)
```
Click "Export PDF"

Expected:
- PDF generated with conversation
- Charts included
- Evidence references
- Timestamp and officer name
- Download begins automatically
```

## Success Criteria
- All queries return in < 3 seconds
- Evidence trail present on every response
- Visualizations render correctly
- No hallucinations or unsupported claims
