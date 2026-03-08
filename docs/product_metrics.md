# Product Metrics

## Code Coverage

| Component | LOC | Functions/Endpoints | Tests | Coverage |
|-----------|-----|---------------------|-------|----------|
| Data Pipeline (`scripts/`) | 331 | 8 functions | 10 | 100% of outputs validated |
| MCP Server (`mcp-server/server.py`) | 221 | 8 tools | 8 | 4/8 tools tested directly |
| REST API (`mcp-server/api.py`) | 126 | 5 endpoints | 12 | 5/5 endpoints tested |
| Frontend (`frontend/index.html`) | 496 | N/A | 0 | Manual testing only |
| Tests (`tests/`) | 221 | — | — | — |
| **Total** | **1,179** | **21** | **30** | **Backend: ~85%** |

### Top 2 To-Dos
1. Add tests for untested MCP tools (`format_for_esri`, `geocode_address`, `get_geojson_for_map`, `get_arcgis_token`)
2. Add frontend E2E tests (e.g., Playwright for map rendering verification)

---

## Comments

| Component | Code LOC | Comment Lines | Ratio |
|-----------|----------|---------------|-------|
| scripts/ | 331 | 80 | 24% |
| mcp-server/ | 347 | 19 | 5% |
| frontend/ | 496 | ~10 | 2% |
| **Overall** | **1,179** | **~109** | **~9%** |

### Top 2 To-Dos
1. Add docstrings to API endpoint functions in `api.py` (currently only one-liners)
2. Add inline comments to frontend JavaScript for map initialization and filter logic

---

## Unit Tests

| File | Tests | Scope |
|------|-------|-------|
| `test_data_pipeline.py` | 10 | Category mappings validation (U1–U3), QoL data schema & values (U4–U7) |
| `test_mcp_server.py` | 8 | Beats loader (U8), query tools (U9–U10), aggregation (U11) |
| `test_api.py` | 12 | All 5 REST endpoints (U12–U16) + filtering + edge cases |
| **Total** | **30** | **All pass in 4.23s** |

### Top 2 To-Dos
1. Add negative/boundary tests (invalid year, empty beat, malformed params)
2. Add tests for QoL score calculation logic (weight verification)

---

## Integration Tests

| ID | Test | Status |
|----|------|--------|
| I1 | Full pipeline: CSV → QoL JSON | PASS (verified via U4–U7) |
| I2 | API serves pipeline output | PASS |
| I3 | ESRI token flow | PASS (credential-dependent) |
| I4 | Frontend loads map with data | PASS (manual) |
| I5 | Filter changes update map | PASS (manual) |

### Top 2 To-Dos
1. Add automated integration test for full pipeline → API → GeoJSON response chain
2. Add smoke test that starts both servers and validates end-to-end HTTP flow

---

## Security Vulnerabilities

| Category | Status | Details |
|----------|--------|---------|
| SQL Injection | SAFE | No SQL — pandas DataFrame filtering only |
| XSS | SAFE | `textContent` used for dynamic content, no `innerHTML` with user input |
| Command Injection | SAFE | No subprocess/os.system calls |
| SSRF | LOW | Hard-coded ArcGIS URLs only |
| Secrets in Code | SAFE | All secrets in `.env` (gitignored) |
| Input Validation | MEDIUM | `source`/`category` params not whitelisted |
| CORS | HIGH | `allow_origins=["*"]` — permissive for localhost dev |
| Authentication | N/A | Public civic data — no auth needed |
| Dependencies | LOW | Versions not pinned in requirements.txt |

### Top 2 To-Dos
1. Restrict CORS to `http://localhost:3000` (or deploy origin) and add input validation whitelist for query params
2. Pin dependency versions with `pip freeze > requirements-lock.txt`
