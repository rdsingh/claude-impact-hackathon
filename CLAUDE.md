# Neighborhood Issue Tracker — Project Context

## Overview
Combine San Diego 311 data, code enforcement records, and police call data to visualize and track quality-of-life issues by neighborhood over time. Data is displayed on an ArcGIS map with neighborhood polygons (PD beats), popups, layer toggles, and time filtering.

## Current Phase: Phase 1 — Research & Planning

## Team
- Daman
- Rajdeep
- Kedar Kulkarni

## Architecture

### MCP Server (Python — geopandas/shapely for spatial ops)
**Inbound tools (local data):**
- `query_311` — read/filter local 311 CSV by category, date range, neighborhood
- `query_code_enforcement` — filter local code enforcement CSV
- `query_police_calls` — filter local police calls CSV
- `load_pd_beats` — parse shapefile to get neighborhood boundary polygons
- `aggregate_by_neighborhood` — spatially join CSV point data against PD beats boundaries

**Outbound tools (ESRI):**
- `get_arcgis_token` — OAuth 2.0 client credentials flow (ARCGIS_CLIENT_ID / ARCGIS_CLIENT_SECRET in .env)
- `format_for_esri` — convert aggregated results to GeoJSON/FeatureSet for ArcGIS Maps SDK
- `geocode_address` — optional, for search UX

### Frontend
- **MVP:** ArcGIS Maps SDK only — neighborhood polygons, popups with incident counts, layer toggles (311/code enforcement/police calls), time filtering via SDK controls
- **Stretch goal:** React/Vite app with filter panel + charts + embedded map (only if Phase 3 complete with time remaining)

### ESRI Integration
- OAuth 2.0 app authentication (client credentials flow)
- Token requested server-side, passed to frontend
- ESRI used for: basemap rendering, geocoding, map display — NOT as a data store

## Data Sources (all local, from data.sandiego.gov)

### 311 / Get It Done Requests
- **Files:** `data/311/get_it_done_requests_closed_{year}_datasd.csv`, `get_it_done_requests_open_datasd.csv`
- **Years:** 2016–2026 + open requests
- **Total rows:** ~2.4M
- **Key fields:** service_request_id, date_requested, case_record_type, service_name, service_name_detail, status, lat, lng, comm_plan_name, council_district
- **Source:** https://data.sandiego.gov/datasets/get-it-done-requests/

### Code Enforcement
- **File:** `data/code_enforcement/code_enf_past_2015_to_2018_datasd.csv`
- **Rows:** ~22K
- **Key fields:** case_id, description, complaint_type, date_open, date_closed, lat, lng, workgroup
- **Lookup tables:** complaint_types_datasd.csv, code_enf_remedies_datasd.csv
- **Source:** https://data.sandiego.gov/datasets/code-enforcement/

### Police Calls for Service
- **Files:** `data/police_calls/pd_calls_for_service_{year}_datasd.csv`
- **Years:** 2015–2026
- **Total rows:** ~6.6M
- **Key fields:** INCIDENT_NUM, DATE_TIME, CALL_TYPE, DISPOSITION, BEAT, PRIORITY, address fields
- **Lookup tables:** pd_cfs_calltypes_datasd.csv, pd_dispo_codes_datasd.csv
- **Note:** No lat/lng — uses BEAT field for spatial join with PD beats shapefile
- **Source:** https://data.sandiego.gov/datasets/police-calls-for-service/

### PD Beats Shapefile (Neighborhood Boundaries)
- **Files:** `data/pd_beats_datasd/pd_beats_datasd.*` (.shp, .dbf, .shx, .prj, .cpg)
- **Fields:** objectid, beat, div, serv, name
- **Coverage:** ~130 neighborhoods/beats across San Diego
- **Source:** https://data.sandiego.gov/datasets/police-beats/

## Key Design Decisions
- All data is local — no live API calls to city data portal at runtime
- Python MCP server (geopandas for spatial joins)
- Clean separation between data layer and presentation layer (enables React stretch goal)
- Police calls join to neighborhoods via BEAT field (direct match to shapefile)
- 311 and code enforcement join via lat/lng point-in-polygon against PD beat boundaries

## Project Structure
```
├── CLAUDE.md                    # This file — project context
├── Hackathon-Playbook.md        # Rules, phases, judging criteria
├── token_tracking.md            # AI token usage tracking
├── .env                         # ARCGIS_CLIENT_ID, ARCGIS_CLIENT_SECRET
├── .env.example                 # Template for .env
├── data/
│   ├── 311/                     # Get It Done request CSVs
│   ├── code_enforcement/        # Code enforcement CSVs
│   ├── police_calls/            # Police calls for service CSVs
│   └── pd_beats_datasd/         # PD beats shapefile set
├── docs/
│   └── requirements.md          # Phase 1 requirements document
├── mcp-server/                  # Python MCP server (Phase 2)
└── frontend/                    # ArcGIS Maps SDK frontend (Phase 2)
```

## Model Usage
- Phases 1, 2, 3: claude-sonnet-4-6 (cost-efficient)
- Phase 4 (narrative): claude-sonnet-4-6
- Opus only for genuinely hard architectural problems

## Rules
- Use city data responsibly — public APIs and open data only
- Code in public GitHub repo
- Checkpoint at end of each phase — team must confirm before proceeding
