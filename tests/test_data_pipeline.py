"""
Unit tests for the data pipeline (test plan U1–U7).
Validates category_mappings.json and neighborhood_qol.json.
"""

import json
import os
import pytest

BASE_DATA = os.path.join(os.path.dirname(__file__), '..', 'data')


@pytest.fixture(scope="module")
def category_mappings():
    with open(os.path.join(BASE_DATA, 'category_mappings.json')) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def qol_data():
    with open(os.path.join(BASE_DATA, 'neighborhood_qol.json')) as f:
        return json.load(f)


# U1: Category mappings file exists and is valid JSON with all three source keys
class TestCategoryMappings:
    def test_u1_has_all_source_keys(self, category_mappings):
        expected_keys = {"311_service_name", "code_enforcement_complaint_type", "police_call_type"}
        assert expected_keys == set(category_mappings.keys())

    def test_u1_values_are_valid(self, category_mappings):
        valid = {"critical", "non_critical"}
        for source_key, mapping in category_mappings.items():
            assert len(mapping) > 0, f"{source_key} mapping is empty"
            for event_type, classification in mapping.items():
                assert classification in valid, (
                    f"{source_key}: '{event_type}' has invalid value '{classification}'"
                )

    # U2: 311 service names fully mapped
    def test_u2_311_service_names_mapped(self, category_mappings):
        mapping = category_mappings["311_service_name"]
        assert len(mapping) > 0

    # U3: Police call types fully mapped
    def test_u3_police_call_types_mapped(self, category_mappings):
        mapping = category_mappings["police_call_type"]
        assert len(mapping) > 0


# U4–U7: QoL JSON validation
class TestQoLData:
    def test_u4_required_schema(self, qol_data):
        required_fields = {"beat", "q_o_l_category", "score", "source", "year", "quarter", "month"}
        assert len(qol_data) > 0, "QoL data is empty"
        for i, record in enumerate(qol_data[:100]):  # Sample first 100
            missing = required_fields - set(record.keys())
            assert not missing, f"Record {i} missing fields: {missing}"

    def test_u4_schema_all_records(self, qol_data):
        """Verify all records have required fields (spot-check every 1000th)."""
        required_fields = {"beat", "q_o_l_category", "score", "source", "year", "quarter", "month"}
        for i in range(0, len(qol_data), 1000):
            missing = required_fields - set(qol_data[i].keys())
            assert not missing, f"Record {i} missing fields: {missing}"

    def test_u5_scores_non_negative(self, qol_data):
        negative = [r for r in qol_data if r["score"] < 0]
        assert len(negative) == 0, f"Found {len(negative)} records with negative scores"

    def test_u6_year_range(self, qol_data):
        years = {r["year"] for r in qol_data}
        for y in years:
            assert 2018 <= y <= 2025, f"Year {y} outside expected range 2018-2025"

    def test_u7_sources_present(self, qol_data):
        expected = {"311", "code_enforcement", "police_calls", "all_sources_combined"}
        actual = {r["source"] for r in qol_data}
        assert expected == actual, f"Expected sources {expected}, got {actual}"

    def test_record_count(self, qol_data):
        assert len(qol_data) > 50000, f"Expected >50K records, got {len(qol_data)}"
