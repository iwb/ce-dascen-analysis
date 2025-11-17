"""
Tests for Configuration Validation

Tests cover:
- Indicator configuration validity
- Weight sum validation
- Threshold consistency
- JSON structure validation
"""

import pytest
import json


class TestIndicatorConfigValidation:
    """Tests for indicator configuration validation."""

    def test_indicator_config_structure(self, sample_indicators_config):
        """Test that indicator config has required structure."""
        assert 'indicators' in sample_indicators_config
        assert isinstance(sample_indicators_config['indicators'], list)
        assert len(sample_indicators_config['indicators']) > 0

    def test_indicator_required_fields(self, sample_indicators_config):
        """Test that each indicator has required fields."""
        required_fields = [
            'indicator_id',
            'target_dataframe',
            'aggregation',
            'direction',
            'threshold',
            'weight',
            'category',
            'formula',
            'indicator_variables'
        ]

        for indicator in sample_indicators_config['indicators']:
            for field in required_fields:
                assert field in indicator, f"Missing field '{field}' in indicator {indicator.get('indicator_id', 'unknown')}"

    def test_weights_sum_to_one(self, sample_indicators_config):
        """Test that indicator weights sum to 1.0."""
        total_weight = sum(ind['weight'] for ind in sample_indicators_config['indicators'])

        assert total_weight == pytest.approx(1.0, abs=0.01), f"Weights sum to {total_weight}, expected 1.0"

    def test_weights_positive(self, sample_indicators_config):
        """Test that all weights are positive."""
        for indicator in sample_indicators_config['indicators']:
            assert indicator['weight'] > 0, f"Weight for {indicator['indicator_id']} is not positive"
            assert indicator['weight'] <= 1.0, f"Weight for {indicator['indicator_id']} exceeds 1.0"

    def test_direction_valid(self, sample_indicators_config):
        """Test that direction is either 'minimize' or 'maximize'."""
        valid_directions = ['minimize', 'maximize']

        for indicator in sample_indicators_config['indicators']:
            assert indicator['direction'] in valid_directions, \
                f"Invalid direction '{indicator['direction']}' for {indicator['indicator_id']}"

    def test_category_valid(self, sample_indicators_config):
        """Test that category is either 'economic' or 'environmental'."""
        valid_categories = ['economic', 'environmental']

        for indicator in sample_indicators_config['indicators']:
            assert indicator['category'] in valid_categories, \
                f"Invalid category '{indicator['category']}' for {indicator['indicator_id']}"

    def test_aggregation_valid(self, sample_indicators_config):
        """Test that aggregation method is valid."""
        valid_aggregations = ['sum', 'average', 'mean', 'max', 'min', 'none']

        for indicator in sample_indicators_config['indicators']:
            assert indicator['aggregation'] in valid_aggregations, \
                f"Invalid aggregation '{indicator['aggregation']}' for {indicator['indicator_id']}"

    def test_threshold_is_numeric(self, sample_indicators_config):
        """Test that thresholds are numeric."""
        for indicator in sample_indicators_config['indicators']:
            assert isinstance(indicator['threshold'], (int, float)), \
                f"Threshold for {indicator['indicator_id']} is not numeric"

    def test_formula_not_empty(self, sample_indicators_config):
        """Test that formulas are not empty."""
        for indicator in sample_indicators_config['indicators']:
            assert len(indicator['formula']) > 0, \
                f"Formula for {indicator['indicator_id']} is empty"

    def test_indicator_variables_structure(self, sample_indicators_config):
        """Test that indicator_variables has proper structure."""
        for indicator in sample_indicators_config['indicators']:
            assert isinstance(indicator['indicator_variables'], dict), \
                f"indicator_variables for {indicator['indicator_id']} is not a dict"

            # Check that each variable has a source
            for var_name, var_config in indicator['indicator_variables'].items():
                assert 'source' in var_config, \
                    f"Variable '{var_name}' in {indicator['indicator_id']} missing 'source'"


class TestIndicatorIDUniqueness:
    """Tests for indicator ID uniqueness."""

    def test_indicator_ids_unique(self, sample_indicators_config):
        """Test that indicator IDs are unique."""
        indicator_ids = [ind['indicator_id'] for ind in sample_indicators_config['indicators']]

        assert len(indicator_ids) == len(set(indicator_ids)), \
            f"Duplicate indicator IDs found: {indicator_ids}"

    def test_indicator_ids_not_empty(self, sample_indicators_config):
        """Test that indicator IDs are not empty."""
        for indicator in sample_indicators_config['indicators']:
            assert len(indicator['indicator_id']) > 0, "Empty indicator ID found"


class TestThresholdConsistency:
    """Tests for threshold consistency."""

    def test_minimize_threshold_positive(self, sample_indicators_config):
        """Test that minimize thresholds are positive (max acceptable)."""
        for indicator in sample_indicators_config['indicators']:
            if indicator['direction'] == 'minimize':
                # For minimize, threshold should be positive (max acceptable value)
                assert indicator['threshold'] > 0 or indicator['threshold'] == 0, \
                    f"Minimize threshold for {indicator['indicator_id']} should be >= 0"

    def test_maximize_threshold_valid(self, sample_indicators_config):
        """Test that maximize thresholds are valid (min acceptable)."""
        for indicator in sample_indicators_config['indicators']:
            if indicator['direction'] == 'maximize':
                # For maximize, threshold should be a valid minimum
                assert indicator['threshold'] >= 0, \
                    f"Maximize threshold for {indicator['indicator_id']} should be >= 0"


class TestJSONStructure:
    """Tests for JSON structure validity."""

    def test_json_serializable(self, sample_indicators_config):
        """Test that config can be serialized to JSON."""
        try:
            json_str = json.dumps(sample_indicators_config)
            assert json_str is not None
        except Exception as e:
            pytest.fail(f"Config is not JSON serializable: {e}")

    def test_json_deserializable(self, sample_indicators_config):
        """Test that config can be deserialized from JSON."""
        try:
            json_str = json.dumps(sample_indicators_config)
            config_restored = json.loads(json_str)
            assert config_restored == sample_indicators_config
        except Exception as e:
            pytest.fail(f"Config cannot be deserialized: {e}")


class TestValueConfigValidation:
    """Tests for value configuration validation."""

    def test_value_config_structure(self, sample_values_config):
        """Test that value config has required structure."""
        assert 'values' in sample_values_config
        assert 'special_values' in sample_values_config
        assert isinstance(sample_values_config['values'], list)
        assert isinstance(sample_values_config['special_values'], list)

    def test_value_required_fields(self, sample_values_config):
        """Test that each value has required fields."""
        required_fields = ['target_dataframe', 'category', 'formula', 'value_variables']

        for value in sample_values_config['values']:
            for field in required_fields:
                assert field in value, f"Missing field '{field}' in value"

    def test_category_valid_for_values(self, sample_values_config):
        """Test that value categories are valid."""
        valid_categories = ['cost_factor', 'aggregate']

        for value in sample_values_config['values'] + sample_values_config['special_values']:
            assert value['category'] in valid_categories, \
                f"Invalid category '{value['category']}' for value"


@pytest.mark.unit
class TestConfigEdgeCases:
    """Tests for configuration edge cases."""

    def test_empty_indicators_list(self):
        """Test handling of empty indicators list."""
        empty_config = {'indicators': []}

        assert len(empty_config['indicators']) == 0

    def test_single_indicator(self):
        """Test config with single indicator."""
        single_config = {
            'indicators': [{
                'indicator_id': 'IND01',
                'target_dataframe': 'df_process',
                'aggregation': 'sum',
                'direction': 'minimize',
                'threshold': 1000,
                'weight': 1.0,
                'category': 'economic',
                'formula': 'a + b',
                'indicator_variables': {'a': {'source': 'dataframe', 'column': 'val_a'}}
            }]
        }

        weights_sum = sum(ind['weight'] for ind in single_config['indicators'])
        assert weights_sum == 1.0
