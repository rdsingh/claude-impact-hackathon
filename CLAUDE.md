# Neighborhood Issue Tracker — Project Context

## Overview
Combine San Diego 311 data, code enforcement records, and police call data to visualize and track quality-of-life issues by neighborhood over time. Data is displayed on an ArcGIS map with neighborhood polygons (PD beats), popups, layer toggles, and time filtering.

## All Phases Complete

- Phase 1 (Research & Planning) — complete.
- Phase 2 (Engineering) — complete.
- Phase 3 (Testing) — complete. 30/30 automated tests passing, 4.23s.
- Phase 4 (Demo, Presentation, wrap-up) — complete. 8-slide deck, product metrics, token tracking.

## Team
- Daman
- Rajdeep
- Kedar Kulkarni

## Architecture

### Data Pipeline (`scripts/`)
Two preprocessing scripts run once to produce the final output:
1. `generate_category_mappings.py` — Classifies ~467 event types across all three sources as critical/non-critical using rule-based logic. Saves to `data/category_mappings.json`.
2. `build_qol.py` — Reads CSVs + shapefile + category mappings. Performs spatial joins (point-in-polygon for 311/code enforcement, direct beat match for police calls), date normalization, aggregation, and QoL scoring. Outputs `data/neighborhood_qol.json` (~100K records, 12.4 MB).

**QoL Score:** `neighborhood_weighted_count / city_avg_weighted_count` where critical events have weight 0.7 and non-critical 0.3. Score of 1.0 = city average.

### MCP Server (`mcp-server/`)
**server.py** — FastMCP server with tools:
- Inbound (local data): `query_311`, `query_code_enforcement`, `query_police_calls`, `load_pd_beats`, `aggregate_by_neighborhood`
- Outbound (ESRI): `get_arcgis_token`, `format_for_esri`, `geocode_address`, `get_geojson_for_map`

**api.py** — Starlette REST API wrapping MCP tools for the frontend:
- `GET /api/geojson?source=&category=&year=&quarter=&month=` — GeoJSON FeatureCollection with beat polygons + QoL scores
- `GET /api/beats` — Raw beat polygons as GeoJSON
- `GET /api/token` — ArcGIS OAuth2 token
- `GET /api/filters` — Available filter values
- `GET /api/health` — Health check

### Frontend (`frontend/`)
Single `index.html` using ArcGIS Maps SDK for JavaScript (v4.29):
- Map centered on San Diego with PD beat polygons
- Color-coded by QoL score: Low (<0.5 green), Medium (0.5-1.5 yellow), High (>1.5 red)
- Filter panel: My Neighborhood (with zoom-to), data source, category (critical/non-critical)
- Time slider with granularity toggle (Monthly / Quarterly / Annually)
- Play/Pause button — animates through time periods at 2-second intervals, supports resume
- Popup on click: neighborhood name, QoL score
- Filters auto-apply on selection change (no Apply button)
- Legend explaining 3-tier color scale

### ESRI Integration
- OAuth 2.0 client credentials flow (ARCGIS_CLIENT_ID / ARCGIS_CLIENT_SECRET in .env)
- Token requested server-side via `/api/token`, used for basemap rendering
- ESRI used for: basemap rendering, geocoding — NOT as a data store

## Data Sources (all local, from data.sandiego.gov)

### 311 / Get It Done Requests
- **Files:** `data/311/get_it_done_requests_closed_{year}_datasd.csv`, `get_it_done_requests_open_datasd.csv`
- **Years:** 2016–2026 + open requests (~2.4M total rows, ~2.7M after date filtering)
- **Key fields:** service_request_id, date_requested, service_name, status, lat, lng, comm_plan_name
- **Source:** https://data.sandiego.gov/datasets/get-it-done-requests/

### Code Enforcement
- **File:** `data/code_enforcement/code_enf_past_2015_to_2018_datasd.csv` (~22K rows, 117 after date filtering)
- **Key fields:** case_id, description, complaint_type, date_open, lat, lng
- **Source:** https://data.sandiego.gov/datasets/code-enforcement/

### Police Calls for Service
- **Files:** `data/police_calls/pd_calls_for_service_{year}_datasd.csv`
- **Years:** 2015–2026 (~6.6M total, ~3.3M after date filtering)
- **Key fields:** INCIDENT_NUM, DATE_TIME, CALL_TYPE, DISPOSITION, BEAT
- **No lat/lng** — uses BEAT field for direct join with PD beats shapefile
- **Source:** https://data.sandiego.gov/datasets/police-calls-for-service/

### PD Beats Shapefile
- **Files:** `data/pd_beats_datasd/pd_beats_datasd.*` (135 beats)
- **Fields:** objectid, beat, div, serv, name
- **Source:** https://data.sandiego.gov/datasets/police-beats/

### Processed Output
- `data/category_mappings.json` — Event type → critical/non_critical mappings
- `data/neighborhood_qol.json` — 100,284 records with beat, q_o_l_category, score, source, year, quarter, month

## Running the Project

### Prerequisites
- Python 3.14+ with venv
- Virtual environment: `.venv/`

### First-time setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Generate data (run once)
```bash
source .venv/bin/activate
python3 scripts/generate_category_mappings.py
python3 scripts/build_qol.py
```

### Start servers
```bash
source .venv/bin/activate
python3 mcp-server/api.py &          # API on port 8000
python3 -m http.server 3000 --directory frontend &  # Frontend on port 3000
```
Open http://localhost:3000

## Project Structure
```
├── CLAUDE.md                           # This context file
├── Hackathon-Playbook.md               # Rules, phases, judging criteria
├── token_tracking.md                   # AI token usage tracking
├── requirements.txt                    # Python dependencies
├── .env                                # Secrets (gitignored)
├── .env.example                        # Credential template
├── .gitignore
├── docs/
│   ├── requirements.md                 # Phase 1 requirements + data pipeline spec
│   └── test_plan.md                    # Test plan for Phase 3
├── scripts/
│   ├── generate_category_mappings.py   # Script 1: classify event types
│   └── build_qol.py                    # Script 2: build neighborhood_qol.json
├── mcp-server/
│   ├── server.py                       # MCP server with tools
│   └── api.py                          # REST API for frontend
├── frontend/
│   └── index.html                      # ArcGIS Maps SDK frontend
├── tests/
│   ├── test_data_pipeline.py           # U1-U7: category mappings + QoL data validation
│   ├── test_mcp_server.py              # U8-U11: MCP server tool tests
│   └── test_api.py                     # U12-U16 + I2: REST API endpoint tests
├── presentation/
│   └── slides.html                     # 8-slide HTML presentation
└── data/
    ├── 311/                            # Get It Done CSVs (gitignored)
    ├── code_enforcement/               # Code enforcement CSVs (gitignored)
    ├── police_calls/                   # Police calls CSVs (gitignored)
    ├── pd_beats_datasd/                # PD beats shapefile (tracked)
    ├── category_mappings.json          # Generated mappings (tracked)
    └── neighborhood_qol.json           # Generated QoL data (tracked)
```

## Key Design Decisions
- All data is local — no live API calls to city data portal at runtime
- Python MCP server (geopandas for spatial joins)
- Clean separation between data layer (MCP/API) and presentation layer (frontend)
- Police calls join to neighborhoods via BEAT field (direct match)
- 311 and code enforcement join via lat/lng point-in-polygon
- QoL score is relative to city average, not absolute counts
- Stretch goal: React/Vite app — only if Phase 3 complete with time remaining

## Model Usage
- Phase 1: claude-opus-4-6 (data exploration, requirements)
- Phases 2, 3, 4: claude-sonnet-4-6 preferred (cost-efficient)
- Opus only for genuinely hard architectural problems
