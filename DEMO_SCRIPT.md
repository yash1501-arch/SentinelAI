# SentinelAI — Demo Script (3-4 minutes)

## Pre-Demo Checklist
- [ ] Backend running: `cd backend && uvicorn app.main:app --reload --port 8000`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] OpenAI/Groq API key configured in `backend/.env`
- [ ] Browser open at http://localhost:3000
- [ ] Screen resolution 1920x1080, browser at 90% zoom
- [ ] Dark mode enabled for better visibility

---

## Scene 1: Login & Dashboard (30 seconds)

**Action:** Login as `investigator` / `Investigator@123`

**Narration:**
> "SentinelAI is an AI-powered crime intelligence platform built for law enforcement. Each investigator gets a personalized dashboard showing real-time crime statistics and AI-generated alerts."

**What to show:**
- KPI cards (total cases, solved rate, heinous crimes, active alerts)
- Smart alerts section (3 AI-generated alerts with severity badges)
- Quick action grid

---

## Scene 2: Conversational AI + Voice (60 seconds)

**Action:** Navigate to Chat (sidebar or Ctrl+/)

**Query 1 (type):**
> "Show me robbery trends in Bengaluru over the last 6 months"

**What to show:**
- Agent activity indicator (pulsing dot, "Analyzing...")
- Reasoning chain (expand to show Coordinator → Analytics Agent → Summarizer)
- Response with line chart visualization
- Confidence score and processing time

**Query 2 (voice — click mic button):**
> "Who is connected to Rajesh Kumar?"

**What to show:**
- Voice transcription in action
- Graph Agent activated
- Network graph visualization rendered inline
- Sources and evidence references

---

## Scene 3: Network Graph Deep Dive (40 seconds)

**Action:** Navigate to Network tab

**What to show:**
- Search for "Rajesh Kumar" or a person ID
- Set depth to 3 hops
- Interactive graph visualization (drag, zoom)
- Network statistics panel (connections, centrality, community)
- Highlight how cross-case connections are revealed

**Narration:**
> "The platform builds a criminal knowledge graph using Neo4j. It automatically discovers hidden connections across cases — like two suspects linked through a shared vehicle or phone number. These are connections that would take investigators days to find manually."

---

## Scene 4: Forecasting & Predictions (30 seconds)

**Action:** Navigate to Forecasting tab

**What to show:**
- Select crime type: "Theft"
- Forecast period: 30 days
- Prophet model output with confidence bands
- Highlight high-risk predictions
- Early warning alerts

**Narration:**
> "Using Meta's Prophet algorithm, we forecast crime patterns with confidence intervals. This enables proactive policing — deploying resources before crimes happen, not after."

---

## Scene 5: Crime Map (20 seconds)

**Action:** Navigate to Map tab

**What to show:**
- Mapbox heatmap overlay
- Zoom into Bengaluru hotspots
- Click a cluster for details
- Show how hotspots are detected using DBSCAN

---

## Scene 6: Export & Report (20 seconds)

**Action:** Return to a case or chat

**What to show:**
- Click Export → PDF
- Show the generated PDF report (opens in new tab)
- Mention CSV export for analysts

**Narration:**
> "Every analysis can be exported as a professional PDF report with complete audit trail — ready for court proceedings or policy briefings."

---

## Closing (15 seconds)

**Narration:**
> "SentinelAI reduces case resolution time by 40% through AI-powered pattern discovery, predictive intelligence, and natural language access to complex crime data. It supports English and Kannada, works on any browser, and deploys on Zoho Catalyst cloud."

---

## Backup: If Live Demo Fails

1. Have screenshots of each scene pre-captured
2. Show pre-recorded 2-minute video as fallback
3. Fall back to architecture slides + code walkthrough

---

## Demo Queries Cheat Sheet

```
"How many robbery cases were registered this month?"
"Show me crime trends in Bengaluru over the last 6 months"
"Who is Rajesh Kumar connected to?"
"Find cases similar to the Koramangala robbery"
"What's the risk profile of accused in case FIR-2025-001?"
"Predict theft hotspots for next week"
"Show me suspicious transaction chains"
```

---

## Keyboard Shortcuts for Demo

- `Ctrl+K` — Command palette (shows all features)
- `Ctrl+/` — Jump to chat
- `Ctrl+Shift+N` — New chat session
- `Ctrl+Shift+D` — Dashboard
