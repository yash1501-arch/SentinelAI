# SentinelAI Frontend — Implementation Plan

## Goal
Build a production-grade Next.js 15 frontend for the SentinelAI crime intelligence platform, connecting users to the LangGraph multi-agent backend.

## Tech Stack
- Next.js 15 (App Router, TypeScript)
- Tailwind CSS 4 + Shadcn UI
- Recharts (line/bar/pie charts)
- React Flow (network graphs)
- Mapbox GL JS (hotspot maps)
- Zustand (auth state)
- Axios (API client with JWT interceptor)
- react-hook-form + zod (forms)

## Build Order (5 Phases)

### Phase 1: Foundation
- `npx create-next-app@latest` with TypeScript, Tailwind, App Router
- Install & configure Shadcn UI (button, card, dialog, input, select, table, badge, avatar, dropdown, sheet, tabs, toast)
- Define ALL TypeScript types in `src/types/` (mirroring every Pydantic schema)
- Build Axios API client with JWT interceptor in `src/lib/api.ts`
- Build Zustand auth store in `src/store/auth.ts`
- Set up `.env.local` with `NEXT_PUBLIC_API_URL`

### Phase 2: Auth & Layout
- `src/app/(auth)/login/page.tsx` — Login form with validation
- `src/app/(dashboard)/layout.tsx` — Authenticated layout with sidebar, header, user menu
- `src/components/layout/sidebar.tsx` — Responsive sidebar with role-aware nav items
- `src/components/layout/header.tsx` — Top bar with search, notifications, user avatar
- `src/middleware.ts` — Next.js middleware for route protection
- Role-based navigation filtering

### Phase 3: Chat (Core Feature)
- `src/app/(dashboard)/chat/page.tsx` — Chat page with message list and input
- `src/components/chat/message-bubble.tsx` — User/assistant message rendering with markdown
- `src/components/chat/chat-input.tsx` — Text input + voice button + send
- `src/components/chat/visualizations.tsx` — Renders `table|line|bar|map|gauge` from backend
- Conversation session management (new session, history sidebar)
- Loading indicators and streaming simulation

### Phase 4: Data Pages
- `src/app/(dashboard)/analytics/page.tsx` — Trends, statistics, charts via Recharts
- `src/app/(dashboard)/cases/page.tsx` — Case list with filters/pagination
- `src/app/(dashboard)/cases/[id]/page.tsx` — Case detail, timeline, evidence
- `src/app/(dashboard)/network/page.tsx` — React Flow graph visualization
- `src/app/(dashboard)/map/page.tsx` — Mapbox hotspot map
- `src/app/(dashboard)/forecasting/page.tsx` — Prophet forecast charts
- `src/app/(dashboard)/profiles/page.tsx` — Offender profile cards

### Phase 5: Admin & Polish
- `src/app/(dashboard)/admin/page.tsx` — User management, audit logs
- `src/app/(dashboard)/settings/page.tsx` — User profile, password change
- Voice recording with MediaRecorder API → upload to `/voice/transcribe`
- PDF export button → `/export/pdf`
- Error boundaries, loading skeletons, empty states

## Critical Files to Create
| File | Purpose |
|------|---------|
| `src/types/auth.ts` | User, Token, Login/Register types |
| `src/types/chat.ts` | ConversationRequest/Response, Viz types |
| `src/types/cases.ts` | CrimeIncident, Evidence, Person types |
| `src/types/analytics.ts` | Hotspot, Forecast, Trend types |
| `src/types/network.ts` | NetworkNode, NetworkEdge, NetworkResponse |
| `src/lib/api.ts` | Axios instance with JWT interceptor |
| `src/store/auth.ts` | Zustand auth store |
| `src/lib/utils.ts` | cn() utility, formatters |
| `src/middleware.ts` | Route protection |
| `src/app/(dashboard)/layout.tsx` | App shell with sidebar |

## Verification
1. `npm run dev` starts without errors
2. Login page renders, form validates, API call succeeds
3. After login, redirects to chat with valid JWT in header
4. Chat page sends message, receives response with visualizations
5. Sidebar navigation is role-aware
6. All 11 dashboard pages load without 404
7. `npm run build` completes with zero errors
