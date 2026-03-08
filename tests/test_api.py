"""
Unit and integration tests for the REST API (test plan U12–U16, I2).
Uses Starlette TestClient via httpx.
"""

import pytest
from starlette.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-server'))

from api import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# U12: /api/health returns ok
class TestHealthEndpoint:
    def test_u12_health_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# U13: /api/filters returns valid options
class TestFiltersEndpoint:
    def test_u13_filters_returns_arrays(self, client):
        resp = client.get("/api/filters")
        assert resp.status_code == 200
        data = resp.json()
        assert "sources" in data
        assert "categories" in data
        assert "years" in data
        assert "quarters" in data
        assert len(data["sources"]) > 0
        assert len(data["categories"]) > 0
        assert len(data["years"]) > 0
        assert len(data["quarters"]) > 0

    def test_u13_expected_sources(self, client):
        resp = client.get("/api/filters")
        data = resp.json()
        assert "311" in data["sources"]
        assert "police_calls" in data["sources"]
        assert "all_sources_combined" in data["sources"]


# U14: /api/token — skipped if no credentials
class TestTokenEndpoint:
    def test_u14_token_requires_credentials(self, client):
        # If no env vars set, should return 500
        if not os.getenv("ARCGIS_CLIENT_ID"):
            resp = client.get("/api/token")
            assert resp.status_code == 500
            assert "error" in resp.json()
        else:
            resp = client.get("/api/token")
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert "expires_in" in data


# U15–U16: /api/geojson returns FeatureCollection
class TestGeoJSONEndpoint:
    def test_u15_geojson_returns_feature_collection(self, client):
        resp = client.get("/api/geojson?source=all_sources_combined&category=all&year=2024")
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) > 0

    def test_u15_features_have_geometry(self, client):
        resp = client.get("/api/geojson?source=all_sources_combined&category=all&year=2024")
        data = resp.json()
        for feat in data["features"][:5]:
            assert "geometry" in feat
            assert "properties" in feat
            assert feat["geometry"]["type"] in ("Polygon", "MultiPolygon")

    def test_u15_features_have_properties(self, client):
        resp = client.get("/api/geojson?source=all_sources_combined&category=all&year=2024")
        data = resp.json()
        for feat in data["features"][:5]:
            props = feat["properties"]
            assert "beat" in props
            assert "name" in props
            assert "avg_score" in props
            assert "total_records" in props

    def test_u16_geojson_filters_by_year(self, client):
        resp = client.get("/api/geojson?source=all_sources_combined&category=all&year=2024")
        assert resp.status_code == 200
        data = resp.json()
        # All beats should be present (135) since we left-join
        assert len(data["features"]) > 100

    def test_geojson_filters_by_source(self, client):
        resp = client.get("/api/geojson?source=311&category=all&year=2024")
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "FeatureCollection"

    def test_geojson_no_data_returns_zero_scores(self, client):
        resp = client.get("/api/geojson?source=all_sources_combined&category=all&year=1990")
        assert resp.status_code == 200
        data = resp.json()
        for feat in data["features"][:5]:
            assert feat["properties"]["avg_score"] == 0.0
            assert feat["properties"]["total_records"] == 0


# I2: API serves pipeline output — GeoJSON has beat polygons with QoL scores
class TestIntegrationAPIServesData:
    def test_i2_api_serves_pipeline_output(self, client):
        resp = client.get("/api/geojson?source=all_sources_combined&category=all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "FeatureCollection"
        # At least some beats should have non-zero scores
        scores = [f["properties"]["avg_score"] for f in data["features"]]
        non_zero = [s for s in scores if s > 0]
        assert len(non_zero) > 0, "Expected some beats with non-zero QoL scores"


class TestBeatsEndpoint:
    def test_beats_returns_geojson(self, client):
        resp = client.get("/api/beats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 135
