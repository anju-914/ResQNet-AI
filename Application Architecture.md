ResQNet AI: Application Architecture

Design basis: your PRD + the stack above. Style: a modular monolith (one API, one worker, one DB), because it is the simplest thing that works. Section 9 marks what to cut for your one-day solo build.

1. System Overview
 Citizens                                         Coordinators
 ┌──────────────┐  ┌──────────────┐              ┌────────────────────┐
 │ Android app  │  │ WhatsApp bot │              │ Next.js dashboard  │
 │ (Kotlin+BLE) │  │ (Cloud API)  │              │ (map, queue, routes)│
 └──────┬───────┘  └──────┬───────┘              └─────────┬──────────┘
        │ HTTPS           │ webhook                        │ HTTPS + SSE
        ▼                 ▼                                ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                    FastAPI (API layer)                           │
 │  public routes │ webhook routes │ coordinator routes (JWT + RBAC)│
 └───────┬──────────────────────────────┬───────────────────────────┘
         │ enqueue                      │ read/write
         ▼                              ▼
 ┌───────────────┐   results    ┌────────────────────────────┐
 │ Redis         │◄────────────►│ PostgreSQL + PostGIS       │
 │ queue+pubsub  │              │ (source of truth)          │
 └───────┬───────┘              └────────────────────────────┘
         ▼
 ┌─────────────────────────────────────────┐
 │ Worker                                  │
 │ NLP extraction │ dedup │ routing │ risk │
 └─────────────────────────────────────────┘

Key idea: the API never does heavy work. It validates, stores, and enqueues. The worker does NLP, dedup, and routing. Redis pub/sub pushes live updates to the dashboard.

2. Project Structure (monorepo)
resqnet/
├── apps/
│   ├── web/                      # Next.js + TypeScript
│   │   ├── app/                  # routes: /login, /dashboard, /queue, /incidents, /resources
│   │   ├── components/           # Map, SosCard, VerifyPanel, RoutePanel
│   │   ├── lib/                  # api client, auth helpers, sse hook
│   │   └── tests/
│   ├── api/                      # FastAPI
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── core/             # config, security (JWT/JWKS), rate limit, logging
│   │   │   ├── routers/          # sos, webhooks, incidents, resources, roads, routes, risk, stream
│   │   │   ├── schemas/          # Pydantic request/response models
│   │   │   ├── models/           # DB models
│   │   │   ├── services/         # sos_service, dedup, routing_service, risk_service
│   │   │   ├── workers/          # extraction job, dedup job, reroute job
│   │   │   └── db/               # session, migrations
│   │   └── tests/
│   └── android/                  # Kotlin: ble/ (advertise, scan, relay), store/ (local queue), sync/, ui/
├── ml/                           # extraction prompts/models, eval set, GNN experiments, notebooks
├── data/                         # synthetic SOS set, road graph snapshot, seed scripts
├── infra/                        # Dockerfiles, docker-compose, CI workflows
└── docs/                         # PRD, architecture, API contract (OpenAPI export)

Rule: routers only handle HTTP, services hold business logic, and workers call services. This keeps the code testable and lets you swap pieces (e.g., LLM → fine-tuned model) without touching routes.

3. Frontend and Backend Flow

Frontend (coordinator dashboard)

/login → managed auth → session with role claim.
/dashboard: full-screen map (verified SOS, resources, blocked roads, risk zones) + live feed.
/queue: unverified SOS list with extracted fields next to the raw text, plus Verify / Reject / Edit actions.
/incidents: merged incidents, status, assigned resources.
/resources: teams and supplies, availability.
One SSE connection (/stream) feeds a client store, which updates the map without refresh.

Backend

Request → auth/rate-limit middleware → Pydantic validation → service → DB write → enqueue job (if needed) → return 202 or 201.
Worker consumes the job → writes results → publishes an event to Redis → API’s SSE endpoint fans it out to connected dashboards.
4. Database Structure (PostgreSQL + PostGIS)
Table	Key columns	Purpose
users	id, email, role (coordinator/admin), created_at	Coordinators only (mirrors the auth provider’s ID)
sos_reports	id, client_uuid (unique), source (app/whatsapp/mesh), raw_text, language, location (geography Point), status (pending/extracted/verified/rejected/resolved), extracted JSON (need_type, people_count, location_text), confidence, spam_score, incident_id (FK), origin_device_id, received_at, hop_count	Every SOS, including raw input
incidents	id, centroid (Point), need_type, people_total, priority, status, created_at	Merged groups of duplicate SOS
resources	id, type (boat/medical/food), capacity, status, location, owner_org	Teams and supplies
assignments	id, resource_id, incident_id, route (LineString), eta, status	Which team goes where
road_edges	id, from_node, to_node, geometry, base_weight, predicted_weight, is_blocked	City graph (nodes can be a small road_nodes table)
road_blocks	id, edge_id, reported_by, active, created_at	History of blockages
risk_zones	id, polygon, score, source, valid_until	Output of the risk map
devices	id, public_key, first_seen, last_sync	Registered mesh/app installs
audit_log	id, actor, action, entity, before/after, at	Who verified/rejected/assigned what

Important design choices:

client_uuid on every SOS makes sync idempotent. The same SOS arriving via mesh and cloud is stored once.
Raw text is stored separately from extracted fields, so you can re-run extraction and measure precision/recall against it.
Spatial indexes (GIST) on all geometry columns.
5. API Structure (/v1)
Group	Endpoint	Auth	Notes
Public	POST /sos	none, rate-limited	Single SOS. Returns 202.
	POST /sos/batch	device-signed	Mesh sync. Idempotent via client_uuid.
	POST /webhooks/whatsapp	HMAC signature	Meta webhook. Verify, then enqueue.
SOS (coordinator)	GET /sos?status=&bbox=	JWT	Filtered, paginated
	PATCH /sos/{id}/verify / reject / edit	JWT, coordinator	Writes audit log
Incidents	GET /incidents, GET /incidents/{id}	JWT	
Resources	GET/POST/PATCH /resources	JWT	
Roads	POST /roads/{edge_id}/block, DELETE ...	JWT	Triggers reroute job
Routing	POST /routes/plan (resource_id, incident_id)	JWT	Returns route + ETA
Risk	GET /risk-zones	JWT	
Live	GET /stream (SSE)	JWT	Events: sos.new, sos.verified, road.blocked, route.updated
Ops	GET /health, GET /metrics	internal	Latency and queue depth

Conventions: versioned path, consistent error shape, cursor pagination, OpenAPI exported to docs/ as the contract.

6. Authentication Flow

Coordinators

Login via the managed provider → receives a JWT with role claim.
Frontend sends Authorization: Bearer <JWT>.
FastAPI verifies signature and expiry against the provider’s JWKS, then checks role per route (dependency-based RBAC).
SSE connects with a short-lived token (not a long-lived one in the URL).

Citizens (anonymous)

No login. Protection comes from per-IP and per-device rate limits, input validation, optional bot-challenge on the web form, and the verification queue, which means no unverified SOS reaches the live map.

WhatsApp

No user auth. The webhook verifies Meta’s signature header before processing.

Mesh/Android

Each install registers once and gets a device ID plus a keypair. Batches are signed by the device so the server can reject forged batches. (This is a design recommendation, not a PRD requirement. Flag it as a decision.)
7. Data Flow

A. Cloud SOS (main path)

Citizen/WhatsApp → API (validate, store raw, status=pending, assign client_uuid)
  → Redis queue → Worker: NLP extract (language, need, count, location) + spam score
  → DB update (status=extracted) → publish event
  → Dashboard queue shows it → Coordinator verifies
  → status=verified → dedup/merge into incident → SSE → map updates

B. Mesh SOS

Phone A (offline) stores SOS locally → BLE advertise → Phone B relays (hop_count+1, TTL limit)
  → any phone with internet → POST /sos/batch (signed)
  → API dedups by client_uuid → continues as flow A

C. Road block → re-route

Coordinator marks road blocked → API sets is_blocked, writes road_blocks
  → reroute job: recompute affected assignments (Dijkstra/A* on updated graph)
  → new route saved → SSE route.updated → map redraws

D. Risk map

Scheduled worker → combines inputs (source TBD per PRD open question) → risk_zones → dashboard layer
8. Risks

Security

Risk	Impact	Mitigation
Public SOS endpoint abused (spam/flood)	Queue overload, coordinator fatigue	Rate limits per IP/device, payload size caps, spam score, bot challenge on web form
Fake or malicious SOS (misleading rescuers)	Real-world harm	Mandatory human verification, audit log, “unverified” never shown as confirmed
Forged mesh batches	Fake incidents injected	Device keypair signing, batch size limits, per-device quotas
Forged WhatsApp webhooks	Fake data	Signature verification, reject unsigned
Prompt injection via SOS text into the LLM extractor	Corrupted fields or leaked prompts	Treat SOS text as data, force JSON-schema output, validate output with Pydantic, never let LLM output trigger actions directly
PII exposure (location, phone numbers)	Privacy breach	Minimize collection, role-gated access, encrypt at rest, retention policy, avoid logging raw text
Broken access control	Citizen or outsider reads data	RBAC on every coordinator route, tests for 401/403 cases
Secrets leakage (LLM key, DB URL)	Account takeover, bills	Env vars only, no secrets in repo, rotate keys
SSE/CORS misconfig	Data leak	Strict CORS origin, short-lived stream tokens

Performance

Risk	Impact	Mitigation
LLM extraction latency and rate limits	Misses the “SOS → map” latency metric	Async worker, retries with backoff, timeout, fallback to rule-based extraction
Disaster-time traffic spike	API slowdown	Queue absorbs bursts, API stays thin, stateless containers
Heavy geo queries	Slow map	GIST indexes, bbox queries, pagination, cluster markers on the client
Re-routing on a large graph	Slow reroute	Keep graph small for MVP, cache graph in worker memory, recompute only affected assignments
Map rendering with many markers	Laggy UI	Clustering, viewport-based loading
Free-tier cold starts (Render sleep)	Slow first request in demo	Warm up before demo
Duplicate storms (many SOS, same incident)	Noisy queue	Dedup by proximity + text similarity, then merge into incidents
9. One-Day Cut Line (solo, free tiers)
Keep	Simplify	Skip
sos_reports, incidents (maybe merge into one table), road_edges, resources	Auth: one protected coordinator login	Redis/queue (run extraction inline or as FastAPI background task)
POST /sos, verify/reject, GET /sos, POST /routes/plan, road block	Live updates: polling instead of SSE	Device signing, /sos/batch (unless doing BLE)
Map + queue + route display	Risk map: static or rule-based layer	WhatsApp webhook, audit log, Playwright/k6

The architecture above is the target. The cut line only changes how much of it you build, not how it is shaped, so adding the queue and SSE later doesn’t require a redesign.