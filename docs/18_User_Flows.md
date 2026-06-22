# SENTINEL AI — User Flows

## Flow 1: Investigative Query
```
User (Investigator)                    System
  │                                      │
  │  1. Login                            │
  │─────────────────────────────────────▶│
  │◀─────────────────────────────────────│  JWT Token
  │                                      │
  │  2. "Show me all burglary cases      │
  │     in Mysore last 3 months"         │
  │─────────────────────────────────────▶│
  │                                      │  3. Coordinator classifies intent
  │                                      │  4. SQL Agent generates query
  │                                      │  5. DataStore executes
  │                                      │  6. Summarizer formats response
  │◀─────────────────────────────────────│  7. "47 cases found..."
  │                                      │
  │  8. "Who are the repeat offenders?"  │
  │─────────────────────────────────────▶│
  │                                      │  9. Context-aware SQL Agent
  │                                      │  10. Filters by repeat_offender=true
  │                                      │  11. Returns top repeat offenders
  │◀─────────────────────────────────────│
  │                                      │
  │  12. "Show their financial network"  │
  │─────────────────────────────────────▶│
  │                                      │  13. Graph Agent activates
  │                                      │  14. Neo4j network query
  │                                      │  15. React Flow visualization
  │◀─────────────────────────────────────│
```

## Flow 2: Network Analysis
```
User (Analyst)                          System
  │                                      │
  │  1. Navigate to Network page         │
  │─────────────────────────────────────▶│
  │                                      │
  │  2. Search for "Ravi Kumar"          │
  │─────────────────────────────────────▶│  3. Person search
  │◀─────────────────────────────────────│  4. Matching persons
  │                                      │
  │  5. Select person, depth=2           │
  │─────────────────────────────────────▶│  6. Neo4j ego network query
  │                                      │  7. PageRank centrality
  │                                      │  8. Community detection
  │◀─────────────────────────────────────│  9. Interactive graph
```

## Flow 3: Crime Forecasting
```
User (Supervisor)                       System
  │                                      │
  │  1. Open Forecasting Dashboard       │
  │─────────────────────────────────────▶│
  │                                      │  2. Load Prophet model data
  │                                      │  3. Query DataStore for history
  │◀─────────────────────────────────────│  4. 30-day forecast with CI
  │                                      │
  │  5. "What areas will spike?"         │
  │─────────────────────────────────────▶│  6. Extract spike alerts
  │◀─────────────────────────────────────│  7. Map overlay of risk zones
```

## Flow 4: Offender Profiling
```
User (Analyst)                          System
  │                                      │
  │  1. Open Offender Profile page       │
  │─────────────────────────────────────▶│
  │                                      │
  │  2. Enter Person ID                  │
  │─────────────────────────────────────▶│  3. Extract features
  │                                      │  4. XGBoost inference
  │                                      │  5. SHAP explanation
  │◀─────────────────────────────────────│  6. Profile card with risk
```

## Flow 5: Voice Query (Kannada)
```
User                                   System
  │                                      │
  │  1. Click microphone icon            │
  │─────────────────────────────────────▶│  2. Record audio
  │                                      │
  │  3. "ಮೈಸೂರಿನಲ್ಲಿ ಕಳೆದ ತಿಂಗಳು          │
  │     ಆದ ಕಳ್ಳತನ ಪ್ರಕರಣಗಳನ್ನು ತೋರಿಸಿ"   │
  │─────────────────────────────────────▶│  4. Whisper STT (Kannada)
  │                                      │  5. IndicTrans2 → English
  │                                      │  6. Multi-agent processing
  │                                      │  7. IndianTrans2 → Kannada
  │◀─────────────────────────────────────│  8. TTS + Text response
```

## Flow 6: Report Export
```
User (Analyst)                          System
  │                                      │
  │  1. View conversation / case         │
  │─────────────────────────────────────▶│
  │                                      │
  │  2. Click "Export PDF"               │
  │─────────────────────────────────────▶│  3. Catalyst Function triggered
  │                                      │  4. PDF generated with:
  │                                      │     - Conversation text
  │                                      │     - Charts & visualizations
  │                                      │     - Evidence references
  │                                      │  5. Uploaded to Stratus
  │◀─────────────────────────────────────│  6. Download URL returned
```
