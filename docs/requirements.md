# Phase 1: Requirements Document

## Project: Neighborhood Issue Tracker
Combine 311 data, code enforcement records, and police call data from San Diego's Open Data Portal to visualize and track quality-of-life issues by neighborhood over time.

---

## Functional Requirements

### FR-1: Data Ingestion (MCP Server)
- Read and parse local CSV files for 311, code enforcement, and police calls
- Parse PD beats shapefile for neighborhood boundary polygons
- Support filtering by: date range, category/call type, neighborhood/beat

### FR-2: Spatial Aggregation
- Spatially join 311 data (lat/lng) against PD beat polygons via point-in-polygon
- Spatially join code enforcement data (lat/lng) against PD beat polygons
- Join police calls data via BEAT field (direct match — no geocoding needed)
- Produce neighborhood-level summary counts per data source

### FR-3: ESRI Integration
- Authenticate via OAuth 2.0 client credentials flow
- Convert aggregated neighborhood data to GeoJSON/FeatureSet format
- Render neighborhood polygons on ArcGIS basemap
- Display popups with incident counts per data source

### FR-4: Map Visualization (MVP Frontend)
- Display San Diego map with PD beat neighborhood polygons
- Color-code polygons by incident density
- Layer toggles: 311 requests, code enforcement, police calls
- Time filtering (date range selector)
- Popup on click: neighborhood name + incident counts by category

### FR-5: Stretch Goal — React GUI
- Filter panel with dropdowns and date pickers
- Charts (bar/line) showing trends over time
- Embedded ArcGIS map
- **Trigger:** Only begin if Phase 3 testing is complete with time remaining

---

## Data Sources

### 311 / Get It Done Requests
- **Source URL:** https://data.sandiego.gov/datasets/get-it-done-requests/
- **Local path:** `data/311/`
- **Files:** 11 yearly CSVs (2016–2026) + open requests
- **Total rows:** ~2.4M
- **Schema:**
  | Field | Type | Notes |
  |-------|------|-------|
  | service_request_id | String | Unique ID |
  | date_requested | Datetime | When request was made |
  | case_record_type | String | High-level group (TSW, etc.) |
  | service_name | String | Service type classification |
  | service_name_detail | String | Further detail |
  | status | String | Current state |
  | lat | Float | Latitude |
  | lng | Float | Longitude |
  | comm_plan_name | String | Community name |
  | council_district | String | Council district |
  | zipcode | String | ZIP code |

### Code Enforcement
- **Source URL:** https://data.sandiego.gov/datasets/code-enforcement/
- **Local path:** `data/code_enforcement/`
- **Main file:** `code_enf_past_2015_to_2018_datasd.csv` (~22K rows)
- **Schema:**
  | Field | Type | Notes |
  |-------|------|-------|
  | case_id | String | Unique case number |
  | description | String | Violation description |
  | complaint_type | String | Type of complaint |
  | date_open | Date | When complaint was filed |
  | date_closed | Date | When case was closed |
  | lat | Float | Latitude |
  | lng | Float | Longitude |
  | workgroup | String | Group that handled it |
- **Lookup tables:** complaint_types_datasd.csv (146 complaint types), code_enf_remedies_datasd.csv

### Police Calls for Service
- **Source URL:** https://data.sandiego.gov/datasets/police-calls-for-service/
- **Local path:** `data/police_calls/`
- **Files:** 12 yearly CSVs (2015–2026)
- **Total rows:** ~6.6M
- **Schema:**
  | Field | Type | Notes |
  |-------|------|-------|
  | INCIDENT_NUM | String | Unique incident ID |
  | DATE_TIME | Datetime | Date/time of call |
  | DAY_OF_WEEK | Integer | 1=Sunday, 2=Monday, etc. |
  | ADDRESS_* | String | Street address components |
  | CALL_TYPE | String | Type code (see lookup) |
  | DISPOSITION | String | Classification code |
  | BEAT | String | PD beat number |
  | PRIORITY | String | Dispatcher priority |
- **No lat/lng** — uses BEAT field for direct join to PD beats shapefile
- **Lookup tables:** pd_cfs_calltypes_datasd.csv (~290 call types), pd_dispo_codes_datasd.csv (19 disposition codes)

### PD Beats Shapefile
- **Source URL:** https://data.sandiego.gov/datasets/police-beats/
- **Local path:** `data/pd_beats_datasd/`
- **Fields:** objectid, beat, div, serv, name
- **Coverage:** ~130 neighborhoods/beats
- **Usage:** Defines neighborhood boundaries for spatial joins; polygons rendered on map

---

## ESRI API Integration

### Authentication
- **Method:** OAuth 2.0 client credentials flow
- **Endpoint:** `https://www.arcgis.com/sharing/rest/oauth2/token`
- **Parameters:**
  - `client_id` = ARCGIS_CLIENT_ID (from .env)
  - `client_secret` = ARCGIS_CLIENT_SECRET (from .env)
  - `grant_type` = client_credentials
- **Response:** Access token (expires in 120 min by default)
- **Server-side:** Token requested by MCP server, passed to frontend

### Data Format for Map Rendering
- **Format:** GeoJSON FeatureCollection or Esri FeatureSet
- **Each feature:**
  - Geometry: Polygon (from PD beats shapefile)
  - Properties: beat, name, 311_count, code_enforcement_count, police_calls_count, time_period
- **Coordinate system:** WGS84 (EPSG:4326)

### ArcGIS Maps SDK (Frontend)
- **SDK:** ArcGIS Maps SDK for JavaScript (v4.x)
- **Basemap:** Streets or Topographic
- **Layers:** FeatureLayer or GeoJSONLayer per data source
- **Widgets:** LayerList (toggles), TimeSlider (filtering), Popup (incident details)

---

## Data Processing Pipeline

### Step 1: Location Mapping
- Map location attributes to common geo/beats
- Use `pd_beats_datasd` shapefile for beat boundaries
- Standardize all sources to beat-level geography

### Step 2: Date Normalization
- Extract `month`, `quarter`, and `year` from date columns
- Standardize across all data sources
- **311 Data:** Use `date_closed` for closed requests, `date_requested` for open requests

### Step 3: Quality of Life Categorization
- Map event type columns (`dispo`, `service_name_detail`, `description`) to `cat_qual_life`
- Categories: **critical** or **non-critical**
- Use Claude API for intelligent categorization

### Step 4: Time Series Aggregation
- Aggregate counts separately for critical and non-critical events
- Group by beat, year, quarter, month

### Step 5: Quality of Life Scoring

| Weight | Category | Default |
|--------|----------|---------|
| `WEIGHT_CRITICAL` | Critical events | 0.7 |
| `WEIGHT_NON_CRITICAL` | Non-critical events | 0.3 |

**Weights are configurable.**

**QoL Score Calculation:**
- Compare neighborhood weighted counts to **city average weighted counts**
- `score = neighborhood_weighted_count / city_avg_weighted_count`

### Step 6: Final Output Schema

**Single JSON file:** `neighborhood_qol.json`

| Column | Type | Values |
|--------|------|--------|
| `beat` | string | Beat ID |
| `q_o_l_category` | string | `critical` / `non_critical` / `all` |
| `score` | float | QoL score vs city avg |
| `source` | string | Data source or `all_sources_combined` |
| `year` | int | 2018-2025 |
| `quarter` | int | 1-4 |
| `month` | int | 1-12 |

### Output Requirements
- **Time range:** Last 7 years only
- **Format:** JSON (for ArcGIS SDK time series)
- **Filters:** By `source`, `q_o_l_category`, `year`, `quarter`, `month`
- **Temporal analysis:** Supports animation/slider via time columns

---

## Testing Strategy

### Unit Tests
- MCP tool functions: query filtering, spatial joins, data aggregation
- ESRI token management
- GeoJSON/FeatureSet formatting

### Integration Tests
- End-to-end: CSV → MCP query → spatial join → GeoJSON output
- ESRI authentication flow
- Map rendering with sample data

### Manual Testing
- Map loads with correct neighborhood polygons
- Layer toggles work correctly
- Popups display accurate counts
- Time filtering updates map data
- Responsive on different screen sizes

---

## Token Estimates by Phase

| Phase | Estimated Tokens | Model | Rationale |
|-------|-----------------|-------|-----------|
| 1: Research & Planning | ~50K | claude-opus-4-6 | Data exploration, schema analysis, requirements docs |
| 2: Engineering | ~200K | claude-sonnet-4-6 | Code generation, MCP server, frontend, API integration |
| 3: Testing | ~80K | claude-sonnet-4-6 | Test writing, debugging, fixing issues |
| 4: Demo & Presentation | ~40K | claude-sonnet-4-6 | Slide deck, narrative, metrics compilation |
| **Total** | **~370K** | | |

---

## Data Provenance

All datasets are sourced from the City of San Diego Open Data Portal (data.sandiego.gov), powered by the Socrata/SODA platform. Data was downloaded for local use — no live API calls at runtime.

| Dataset | Portal URL |
|---------|-----------|
| Get It Done (311) | https://data.sandiego.gov/datasets/get-it-done-requests/ |
| Code Enforcement | https://data.sandiego.gov/datasets/code-enforcement/ |
| Police Calls for Service | https://data.sandiego.gov/datasets/police-calls-for-service/ |
| Police Beats (Shapefile) | https://data.sandiego.gov/datasets/police-beats/ |
