# ResQNet AI

> **Emergency SOS Ingestion, Multi-lingual NLP Extraction, Human Verification & Graph-based Routing Engine**  
> Designed for disaster rescue coordinators (NDRF / NGOs / Control Rooms) to turn scattered, unstructured emergency reports into verified triage map pins and dynamic rescue routes that adapt to live road blockages.

---

## 1. Core End-to-End Flow

```
Raw SOS (Hinglish/Hindi/English) ──▶ NLP Extraction (Strict JSON) ──▶ Verification Queue ──▶ Live Incident Map ──▶ Dijkstra + PyG GNN Routing ──▶ Dynamic Road Block Re-routing
```

### Key Capabilities
- **Multi-lingual Entity Extraction:** Accurately extracts `need_type`, `people_count`, and `location_text` from Hinglish (Roman script), Hindi (Devanagari), and English crisis texts while rejecting spam.
- **Human-in-the-Loop Verification Queue:** High-contrast coordinator queue with one-click **Verify**, **Reject** (with undo), and **Edit** controls.
- **Dark & Gold Coordinator Dashboard (Aurum Design):** High-contrast UI (`#0a0a0a` with `#a78b71` gold accents) built with Next.js and MapLibre GL JS.
- **Graph Routing & Dynamic Re-Routing:** NetworkX weighted graph engine with PyTorch Geometric (PyG) GNN risk penalty adjustment. Marking any road as blocked immediately recalculates all active team assignments.
- **Forwarded SOS Simulator:** A built-in console to test preset or custom disaster reports in real time without waiting for external webhooks.

---

## 2. Benchmark & Accuracy Metrics

Run the hand-labelled 30-message evaluation benchmark:
```powershell
.venv\Scripts\python.exe ml\evaluate_extraction.py
```

### Measured Performance
| Metric | Benchmark Result | Target / Standard |
|---|---|---|
| **Average Extraction Latency** | **0.15 ms** | Sub-second real-time |
| **Language Detection Accuracy** | **100.0%** (30/30) | Hinglish / Hindi / English |
| **Spam Filter Precision** | **100.0%** (30/30) | Zero-loss critical triage |
| **Need Type Classification** | **92.0%** (23/25) | Rescue / Medical / Food / Water |
| **People Count Accuracy** | **92.0%** (23/25) | Extracts numbers & word counts |
| **Location Extraction Accuracy** | **96.0%** (24/25) | Landmark & locality extraction |

---

## 3. Project Structure

```
resqnet/
├── .venv/                         # Managed Python 3.11 environment with uv
├── apps/
│   ├── api/                       # FastAPI Modular Monolith Microservice
│   │   ├── app/
│   │   │   ├── main.py            # FastAPI entry point, CORS, startup lifespan
│   │   │   ├── core/              # Config (Pydantic settings), security, tokens
│   │   │   ├── db/                # SQLAlchemy session, engine, ORM models
│   │   │   ├── schemas/           # Pydantic v2 schemas (SOS, incident, routing, road)
│   │   │   ├── services/          # Extraction, SOS lifecycle, Dijkstra routing, PyG GNN
│   │   │   └── routers/           # REST endpoints: /v1/sos, /v1/incidents, /v1/roads, etc.
│   │   └── tests/                 # Integration test suite (pytest)
│   │
│   └── web/                       # Next.js 14 Coordinator Dashboard
│       └── src/
│           ├── app/               # Routes: / (Map), /queue (Review), /incidents, /submit
│           ├── components/        # MapView (MapLibre), SosCard, IncidentPanel, Navbar
│           └── lib/               # Typed API client, design tokens, interfaces
│
├── ml/                            # Machine Learning & Routing
│   ├── extraction/                # 30-message eval dataset & ground truth
│   ├── gnn/                       # PyTorch Geometric GCN/GAT model for edge risk prediction
│   └── evaluate_extraction.py     # Evaluation runner
│
├── data/                          # Synthetic Disaster Datasets
│   ├── road_network_delhi_synthetic.json # City road graph (13 nodes, 25 edges, coords)
│   └── seed.py                    # One-command database populator
│
└── docs/                          # Architecture, PRD, and design specs
```

---

## 4. Quick Start & Execution Guide

### Prerequisites
- Python 3.11+
- Node.js 18+

### Step 1: Seed the Database
Populate the road network graph, initial emergency resources (boats, medical units), predictive flood risk zones, and pending queue items:
```powershell
.venv\Scripts\python.exe data\seed.py
```

### Step 2: Run Backend Tests
Run the automated integration test suite verifying the complete flow (**SOS Submit $\rightarrow$ Queue $\rightarrow$ Verify $\rightarrow$ Incident Creation $\rightarrow$ Routing $\rightarrow$ Road Blockage Re-routing**):
```powershell
.venv\Scripts\pytest.exe apps\api\tests
```

### Step 3: Start the FastAPI Backend Server
```powershell
.venv\Scripts\python.exe -m uvicorn apps.api.app.main:app --reload --port 8000
```
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/v1/health`

### Step 4: Start the Next.js Coordinator Dashboard
In a separate terminal:
```powershell
cd apps\web
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 5. Dashboard Screens

- **Map Dashboard (`/`):** Full-screen MapLibre GL map with verified incident pins (colored by priority: Red/Amber/Blue), team markers (Gold-light squares), live active routes (Gold solid lines), blocked road segments (dashed red with ✕), and translucent flood risk zones. Selecting an incident opens the dispatch panel.
- **Verification Queue (`/queue`):** High-density review list comparing raw incoming messages against model-extracted fields with **Verify ▸**, **Reject**, and **Edit** actions.
- **Incident Dispatch (`/incidents`):** Overview of active and assigned disaster clusters with casualty counts and assigned units.
- **Forwarded SOS Simulator (`/submit`):** Paste any message (or pick one of the preset Hindi/Hinglish/English scenarios) to ingest, extract, and trace through the pipeline.

