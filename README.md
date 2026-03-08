# San Diego Neighborhood Issue Tracker

> Visualize and track quality-of-life issues across San Diego neighborhoods over time

## Team Name

AIVengers

## Team Members

| Name | Role |
|------|------|
| Daman Singh | Development & Orchestration |
| Rajdeep Singh | Data Modeling & Design |
| Kedar Kulkarni | Data Modeling & Design |

## Problem Statement

How do you measure quality of life (QoL) issues in a neighborhood and track it over time?

San Diego residents, city staff, and community organizations lack a unified view of neighborhood-level quality-of-life trends. Data on 311 requests, code enforcement violations, and police calls exists in separate silos, making it difficult to identify patterns, compare neighborhoods, or track whether conditions are improving or declining.

## What It Does

Combines three city datasets — 311/Get It Done requests, code enforcement records, and police calls for service — to produce a Quality of Life score for each San Diego neighborhood (PD beat). Events are classified as critical or non-critical, weighted, and scored relative to the city average. The results are displayed on an interactive ArcGIS map with time-based animation, allowing users to explore QoL trends by neighborhood, data source, and time period from 2018 to 2025.

## Data Sources Used

| Dataset | Records | Source |
|---------|---------|--------|
| 311 / Get It Done Requests | ~2.7M | [data.sandiego.gov](https://data.sandiego.gov/datasets/get-it-done-requests/) |
| Code Enforcement | ~22K | [data.sandiego.gov](https://data.sandiego.gov/datasets/code-enforcement/) |
| Police Calls for Service | ~3.3M | [data.sandiego.gov](https://data.sandiego.gov/datasets/police-calls-for-service/) |
| PD Beats Shapefile | 135 beats | [data.sandiego.gov](https://data.sandiego.gov/datasets/police-beats/) |

## Architecture / Approach

```
Local CSV/Shapefile Data
        │
        ▼
┌─────────────────────┐
│  Preprocessing      │  generate_category_mappings.py (classify events)
│  Scripts (Python)    │  build_qol.py (spatial joins, QoL scoring)
└────────┬────────────┘
         ▼
   neighborhood_qol.json + category_mappings.json
         │
         ▼
┌─────────────────────┐
│  MCP Server /       │  FastMCP tools + Starlette REST API
│  REST API (Python)  │  Serves GeoJSON, filters, ArcGIS OAuth tokens
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Frontend           │  ArcGIS Maps SDK for JavaScript (v4.29)
│  (index.html)       │  Interactive map with filters, time slider, play/pause
└─────────────────────┘
```

## Demo

- **Live App:** N/A
- **Demo Video:** demo/AIVengers Demo Video

## Tech Stack

- **Frontend:** ArcGIS Maps SDK for JavaScript (v4.29)
- **Backend:** Python (Starlette, uvicorn)
- **AI/ML:** Claude API (event classification)
- **Data Processing:** pandas, geopandas, shapely
- **MCP:** FastMCP server with query and ESRI integration tools
- **Deployment:** localhost (API on port 8000, frontend on port 3000)

## Getting Started

### Prerequisites

- Python 3.14+
- ArcGIS Developer account (Client ID & Secret)
- Anthropic API key (optional, for regenerating category mappings)

### Installation

```bash
git clone https://github.com/rdsingh/claude-impact-hackathon.git
cd claude-impact-hackathon
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your ARCGIS_CLIENT_ID and ARCGIS_CLIENT_SECRET
```

### Generate Data (run once)

```bash
source .venv/bin/activate
python3 scripts/generate_category_mappings.py
python3 scripts/build_qol.py
```

### Running Locally

```bash
source .venv/bin/activate
python3 mcp-server/api.py &
python3 -m http.server 3000 --directory frontend &
```

Open http://localhost:3000
