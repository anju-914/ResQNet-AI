# ResQNet AI: Build Instructions

Read this file first, then `rules.md`. If something is not written here, ask. Do not invent requirements.

## 1. Goal

ResQNet AI helps rescue coordinators (NDRF / NGOs / control rooms) turn scattered SOS messages into a verified map of needs and a suggested rescue route.

Core demo path (this must work end to end):

**SOS in -> extraction -> human verification -> map -> route**

## 2. Constraints

- One person, one day, free tiers only.
- College fest / hackathon demo. Synthetic data is acceptable and must be labelled as such.
- Primary user: rescue coordinators. Citizens are only a data source.
- SOS languages: Hinglish (Roman script), Hindi, English.
- Disaster scope: generic (not floods only).

## 3. Scope

| Build | Stub (fake it, say so) | Skip |
|---|---|---|
| SOS submit endpoint + web form | GNN: use plain Dijkstra, mention GNN as the planned upgrade | WhatsApp webhook (use a "paste forwarded message" box instead) |
| LLM extraction (need type, people count, location text) | Risk map: static or rule-based layer on synthetic data | Redis / task queue (use FastAPI background tasks) |
| Verification queue (verify / reject / edit) | Auth: one protected coordinator login | Device signing and `/sos/batch` |
| Map with SOS and team markers | | SSE / WebSocket (poll every few seconds) |
| Routing on a small road graph + "block road" re-route | | Playwright, k6, CI |
| Seed script with synthetic data | | iOS, X/Twitter scraping, real feeds |

Stretch goal, only if the core path is done: a minimal Android (Kotlin) BLE demo relaying one SOS between two phones.

## 4. Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js + TypeScript, Tailwind, MapLibre GL JS |
| Backend | Python FastAPI, Pydantic |
| Database | Supabase Postgres + PostGIS |
| Auth | Supabase Auth, or one hardcoded coordinator login |
| Extraction | LLM structured-output prompt returning JSON |
| Routing | NetworkX Dijkstra on a small graph (OSMnx or hand-made) |
| Testing | pytest, plus a 30-message extraction accuracy check |
| Deploy | Vercel (frontend), Render free tier (backend), Supabase |

## 5. Project structure

```
resqnet/
├── apps/
│   ├── web/                 # Next.js dashboard
│   │   ├── app/             # /login, /dashboard, /queue, /incidents
│   │   ├── components/      # Map, SosCard, VerifyPanel, RoutePanel
│   │   └── lib/             # api client, auth helpers
│   └── api/                 # FastAPI
│       └── app/
│           ├── main.py
│           ├── core/        # config, security, rate limit
│           ├── routers/     # sos, incidents, roads, routes
│           ├── schemas/     # Pydantic models
│           ├── services/    # extraction, routing, sos logic
│           └── db/          # session, schema SQL
├── ml/                      # extraction prompt, eval set, eval script
├── data/                    # synthetic SOS set, road graph, seed script
└── docs/                    # PRD, architecture, design doc
```

Routers handle HTTP only. Business logic lives in `services`.

## 6. Data model (kept tables)

| Table | Key columns |
|---|---|
| `sos_reports` | id, client_uuid (unique), source, raw_text, language, location (PostGIS point), status (`pending` / `extracted` / `verified` / `rejected` / `resolved`), extracted (JSON), confidence, spam_score, received_at |
| `incidents` | id, centroid, need_type, people_total, priority, status |
| `resources` | id, type, capacity, status, location |
| `road_edges` | id, from_node, to_node, geometry, weight, is_blocked |
| `assignments` | id, resource_id, incident_id, route, eta, status |

Store raw text separately from extracted fields so extraction can be re-run and measured.

## 7. API (kept endpoints, `/v1`)

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /sos` | none, rate-limited | Submit one SOS; returns 202 |
| `GET /sos?status=&bbox=` | coordinator | List SOS |
| `PATCH /sos/{id}/verify`, `/reject`, `/edit` | coordinator | Verification actions |
| `POST /routes/plan` | coordinator | Route for a resource to an incident |
| `POST /roads/{edge_id}/block` | coordinator | Block a road and re-route |
| `GET /health` | none | Health check |

## 8. Extraction spec

Input: raw SOS text (Hinglish / Hindi / English).

Output (strict JSON, validated with Pydantic):

```json
{
  "need_type": "string",
  "people_count": "integer or null",
  "location_text": "string or null",
  "language": "string",
  "confidence": "number 0 to 1",
  "spam_score": "number 0 to 1"
}
```

- If a field cannot be determined, return `null`. Never guess.
- Evaluate on a hand-labelled set of about 30 synthetic messages. Report precision and recall per field, and end-to-end latency (SOS received to visible in queue).
- Example of the hard case: "paani bhar gaya hai near sector 5".

## 9. Build order

1. Accounts and keys: Supabase, Vercel, Render, LLM API key, repo, `.env.example`.
2. Database schema, FastAPI skeleton, `POST /sos`.
3. Extraction service, synthetic test set, accuracy script.
4. Dashboard: app shell, map, SOS markers, verification queue.
5. Road graph, Dijkstra, route display, block-road re-route.
6. Deploy, seed demo data, smoke test.
7. Only then: rule-based risk layer, then the BLE stretch goal.

## 10. Design

Follow the "ResQNet AI: Dashboard Design Document". Summary:

- Background `#0a0a0a`; gold `#a78b71` accent; gold hover `#e8d5b7`.
- Inter for all readable text; Playfair Display Italic only for the logo and screen titles.
- Minimum text size 12px. Text opacity at least 60% white.
- Status is never colour alone: always add a shape or label.
- Verified and unverified SOS must look clearly different.
- Three screens: map dashboard, verification queue, incident and route panel.

## 11. Open items (ask, do not decide)

- Which free dark basemap MapLibre will use.
- How priority is calculated (currently display-only).
- The final list of need types.
- The confidence threshold that triggers a "Check" flag.
- Whether Verify needs a confirmation step.
- Dashboard language (English only, or also Hindi).
- Whether `sos_reports` and `incidents` stay as two tables for the one-day build.

## 12. Definition of done

- A pasted or submitted SOS appears in the queue with extracted fields.
- Verifying it places it on the map.
- Selecting its incident and a team shows a route.
- Blocking a road changes the route.
- Extraction precision/recall and latency are measured and written down.
- Deployed URL works; README lists what is stubbed.