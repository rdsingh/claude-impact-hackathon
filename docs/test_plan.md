# Test Plan

## Unit Tests

### Data Pipeline (`scripts/`)
| ID | Test | Input | Expected |
|----|------|-------|----------|
| U1 | Category mappings file exists and is valid JSON | `category_mappings.json` | All three source keys present, values are "critical" or "non_critical" |
| U2 | 311 service names fully mapped | All unique service_name values | Every value has a mapping entry |
| U3 | Police call types fully mapped | All unique CALL_TYPE values | Every value has a mapping entry |
| U4 | QoL JSON has required schema | `neighborhood_qol.json` | Every record has: beat, q_o_l_category, score, source, year, quarter, month |
| U5 | QoL scores are non-negative | All score values | score >= 0 |
| U6 | Year range is 2018-2025 | All year values | No years outside range |
| U7 | Sources include all expected values | Unique source values | 311, code_enforcement, police_calls, all_sources_combined |

### MCP Server (`mcp-server/server.py`)
| ID | Test | Input | Expected |
|----|------|-------|----------|
| U8 | load_pd_beats returns valid GeoJSON | No params | FeatureCollection with 135 features, each with beat, name, geometry |
| U9 | query_311 filters by year | year=2024 | All returned records have year=2024 |
| U10 | query_police_calls filters by beat | beat=521 | All returned records have beat=521 |
| U11 | aggregate_by_neighborhood returns per-beat averages | source=311, year=2024 | Each beat appears once with avg_score and total_records |

### API Server (`mcp-server/api.py`)
| ID | Test | Input | Expected |
|----|------|-------|----------|
| U12 | /api/health returns ok | GET | {"status": "ok"} |
| U13 | /api/filters returns valid options | GET | sources, categories, years, quarters arrays non-empty |
| U14 | /api/token returns access_token | GET | Response has access_token and expires_in |
| U15 | /api/geojson returns FeatureCollection | GET with source, category, year | type=FeatureCollection, features array with geometry and properties |
| U16 | /api/geojson filters correctly | year=2024 | Returned data reflects 2024 only |

## Integration Tests

| ID | Test | Flow | Expected |
|----|------|------|----------|
| I1 | Full pipeline: CSV → QoL JSON | Run build_qol.py | neighborhood_qol.json created with >0 records |
| I2 | API serves pipeline output | Start API → GET /api/geojson | GeoJSON has beat polygons with QoL scores |
| I3 | ESRI token flow | GET /api/token → use in ArcGIS SDK | Token is valid, map basemap loads |
| I4 | Frontend loads map with data | Open localhost:3000 | Map renders with colored polygons |
| I5 | Filter changes update map | Change source/year → Apply | Polygon colors change to reflect new data |

## Manual Testing Checklist

- [ ] Map loads centered on San Diego
- [ ] All 135 PD beat polygons visible
- [ ] Polygons colored by QoL score (green to red)
- [ ] Clicking a polygon shows popup with name, beat, score, record count
- [ ] Source filter works (311, code enforcement, police calls, all)
- [ ] Category filter works (all, critical, non-critical)
- [ ] Year filter works (2018-2025)
- [ ] Quarter filter works (Q1-Q4)
- [ ] Apply button refreshes map data
- [ ] Legend matches polygon colors
- [ ] No console errors in browser

## Pass/Fail Criteria

- **Pass:** All unit tests pass, all integration tests pass, manual checklist >90% checked
- **Fail:** Any unit test fails, or integration tests I1-I3 fail, or map does not render
