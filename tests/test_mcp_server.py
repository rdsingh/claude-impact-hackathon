"""
Unit tests for MCP server tools (test plan U8–U11).
Tests the tool functions directly (not via MCP protocol).
"""

import json
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-server'))

from server import load_pd_beats, query_311, query_police_calls, aggregate_by_neighborhood


# U8: load_pd_beats returns valid GeoJSON
class TestLoadPDBeats:
    def test_u8_returns_feature_collection(self):
        result = json.loads(load_pd_beats())
        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 135

    def test_u8_features_have_beat_and_name(self):
        result = json.loads(load_pd_beats())
        for feat in result["features"][:5]:
            props = feat["properties"]
            assert "beat" in props
            assert "name" in props
            assert feat["geometry"] is not None


# U9: query_311 filters by year
class TestQuery311:
    def test_u9_filters_by_year(self):
        result = json.loads(query_311(year=2024))
        assert len(result) > 0
        for record in result[:50]:
            assert record["year"] == 2024

    def test_filters_by_category(self):
        result = json.loads(query_311(category="critical"))
        for record in result[:50]:
            assert record["q_o_l_category"] == "critical"


# U10: query_police_calls filters by beat
class TestQueryPoliceCalls:
    def test_u10_filters_by_beat(self):
        result = json.loads(query_police_calls(beat="521"))
        if len(result) > 0:
            for record in result[:50]:
                assert record["beat"] == "521"

    def test_filters_by_year(self):
        result = json.loads(query_police_calls(year=2023))
        assert len(result) > 0
        for record in result[:50]:
            assert record["year"] == 2023


# U11: aggregate_by_neighborhood returns per-beat averages
class TestAggregateByNeighborhood:
    def test_u11_returns_per_beat_averages(self):
        result = json.loads(aggregate_by_neighborhood(source="311", year=2024))
        assert len(result) > 0
        beats_seen = set()
        for record in result:
            assert "beat" in record
            assert "avg_score" in record
            assert "total_records" in record
            beats_seen.add(record["beat"])
        # Each beat should appear only once
        assert len(beats_seen) == len(result)

    def test_aggregate_all_sources(self):
        result = json.loads(aggregate_by_neighborhood(source="all_sources_combined", year=2024))
        assert len(result) > 0
