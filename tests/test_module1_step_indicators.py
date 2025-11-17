"""
Tests for Module 1: Indicator Calculator

Tests cover:
- Formula evaluation for rows
- Variable value extraction from different sources
- Indicator calculation
- Value calculation
- Edge cases and error handling
"""

import pytest
import pandas as pd
import numpy as np
from modules.module1_step_indicators import (
    evaluate_formula_for_row,
    get_variable_value,
    calculate_indicators
)


class TestEvaluateFormulaForRow:
    """Tests for the evaluate_formula_for_row function."""

    def test_simple_formula_evaluation(self, sample_df_process, sample_data_dict):
        """Test evaluation of a simple formula."""
        row = sample_df_process.iloc[0]
        formula = "time * cost"
        variables = {
            'time': {'source': 'dataframe', 'column': 'processing_time'},
            'cost': {'source': 'dataframe', 'column': 'station_cost'}
        }
        attr_structure = {'process': 'process_attributes', 'systems': 'system_configurations', 'product': 'components'}

        result = evaluate_formula_for_row(row, formula, variables, sample_data_dict, attr_structure)

        assert result == 50.0  # 10.0 * 5.0

    def test_formula_with_addition(self, sample_df_process, sample_data_dict):
        """Test formula with addition operation."""
        row = sample_df_process.iloc[0]
        formula = "time + cost"
        variables = {
            'time': {'source': 'dataframe', 'column': 'processing_time'},
            'cost': {'source': 'dataframe', 'column': 'station_cost'}
        }
        attr_structure = {'process': 'process_attributes', 'systems': 'system_configurations', 'product': 'components'}

        result = evaluate_formula_for_row(row, formula, variables, sample_data_dict, attr_structure)

        assert result == 15.0  # 10.0 + 5.0

    def test_formula_with_division(self, sample_df_process, sample_data_dict):
        """Test formula with division operation."""
        row = sample_df_process.iloc[0]
        formula = "time / cost"
        variables = {
            'time': {'source': 'dataframe', 'column': 'processing_time'},
            'cost': {'source': 'dataframe', 'column': 'station_cost'}
        }
        attr_structure = {'process': 'process_attributes', 'systems': 'system_configurations', 'product': 'components'}

        result = evaluate_formula_for_row(row, formula, variables, sample_data_dict, attr_structure)

        assert result == 2.0  # 10.0 / 5.0

    def test_formula_with_missing_variable(self, sample_df_process, sample_data_dict):
        """Test formula handles missing variable gracefully."""
        row = sample_df_process.iloc[0]
        formula = "time * missing_var"
        variables = {
            'time': {'source': 'dataframe', 'column': 'processing_time'},
            'missing_var': {'source': 'dataframe', 'column': 'nonexistent_column'}
        }
        attr_structure = {'process': 'process_attributes', 'systems': 'system_configurations', 'product': 'components'}

        result = evaluate_formula_for_row(row, formula, variables, sample_data_dict, attr_structure, "TEST_IND")

        # Should return 0 when variable lookup fails
        assert result == 0

    def test_formula_rounding(self, sample_df_process, sample_data_dict):
        """Test that results are rounded to 2 decimal places."""
        row = sample_df_process.iloc[0]
        formula = "time / 3"
        variables = {
            'time': {'source': 'dataframe', 'column': 'processing_time'}
        }
        attr_structure = {'process': 'process_attributes', 'systems': 'system_configurations', 'product': 'components'}

        result = evaluate_formula_for_row(row, formula, variables, sample_data_dict, attr_structure)

        assert result == 3.33  # 10.0 / 3 = 3.333... rounded to 2 decimals


class TestGetVariableValue:
    """Tests for the get_variable_value function."""

    def test_dataframe_source(self, sample_df_process):
        """Test getting value from dataframe column."""
        row = sample_df_process.iloc[0]
        var_config = {'source': 'dataframe', 'column': 'processing_time'}
        attr_structure = {}

        result = get_variable_value(row, 'test_var', var_config, {}, attr_structure)

        assert result == 10.0

    def test_dataframe_source_missing_column(self, sample_df_process):
        """Test error handling for missing dataframe column."""
        row = sample_df_process.iloc[0]
        var_config = {'source': 'dataframe', 'column': 'nonexistent_column'}
        attr_structure = {}

        with pytest.raises(KeyError, match="Column 'nonexistent_column' not found"):
            get_variable_value(row, 'test_var', var_config, {}, attr_structure)

    def test_attribute_file_source_process(self, sample_df_process, sample_data_dict):
        """Test getting value from process attribute file."""
        row = sample_df_process.iloc[0]  # comp_A
        var_config = {
            'source': 'attribute_file',
            'file': 'attributes_process.json',
            'lookup_columns': ['step_name'],
            'value_path': 'disassembly_time'
        }
        attr_structure = {'process': 'process_attributes', 'systems': 'system_configurations', 'product': 'components'}

        result = get_variable_value(row, 'test_var', var_config, sample_data_dict, attr_structure)

        assert result == 10.0

    def test_attribute_file_source_product_fixed(self, sample_df_process, sample_data_dict):
        """Test getting fixed attribute from product file."""
        row = sample_df_process.iloc[0]  # comp_A
        var_config = {
            'source': 'attribute_file',
            'file': 'attributes_product.json',
            'lookup_columns': ['step_name'],
            'value_path': 'fixed_attributes.weight.value'
        }
        attr_structure = {'process': 'process_attributes', 'systems': 'system_configurations', 'product': 'components'}

        result = get_variable_value(row, 'test_var', var_config, sample_data_dict, attr_structure)

        assert result == 2.0

    def test_missing_source_key(self, sample_df_process):
        """Test error when source key is missing."""
        row = sample_df_process.iloc[0]
        var_config = {'column': 'processing_time'}  # Missing 'source'
        attr_structure = {}

        with pytest.raises(KeyError, match="missing required 'source' key"):
            get_variable_value(row, 'test_var', var_config, {}, attr_structure)

    def test_unknown_source_type(self, sample_df_process):
        """Test error for unknown source type."""
        row = sample_df_process.iloc[0]
        var_config = {'source': 'unknown_source_type'}
        attr_structure = {}

        with pytest.raises(ValueError, match="Unknown source type 'unknown_source_type'"):
            get_variable_value(row, 'test_var', var_config, {}, attr_structure)


class TestCalculateIndicators:
    """Tests for the calculate_indicators function."""

    def test_calculate_indicators_basic(self, sample_data_dict):
        """Test basic indicator calculation."""
        result_data = calculate_indicators(sample_data_dict, save_output=False)

        # Check that indicators were added to df_process
        assert 'IND01' in result_data['df_process'].columns
        assert 'IND02' in result_data['df_process'].columns

        # Check that IND03 was added to df_product
        assert 'IND03' in result_data['df_product'].columns

    def test_indicator_values_calculated(self, sample_data_dict):
        """Test that indicator values are calculated correctly."""
        result_data = calculate_indicators(sample_data_dict, save_output=False)

        # IND01 = processing_time * station_cost
        # First row: 10.0 * 5.0 = 50.0
        assert result_data['df_process']['IND01'].iloc[0] == 50.0

        # IND02 = energy_used * emission_factor
        # First row: 20.0 * 2.0 = 40.0
        assert result_data['df_process']['IND02'].iloc[0] == 40.0

        # IND03 = component_quality * component_weight
        # First row: 0.9 * 2.0 = 1.8
        assert result_data['df_product']['IND03'].iloc[0] == 1.8

    def test_calculate_values(self, sample_data_dict):
        """Test that values (VAL01, REVENUE, etc.) are calculated."""
        result_data = calculate_indicators(sample_data_dict, save_output=False)

        # Check that VAL01 was added
        assert 'VAL01' in result_data['df_process'].columns

        # Check that REVENUE was added
        assert 'REVENUE' in result_data['df_process'].columns

    def test_values_calculated_correctly(self, sample_data_dict):
        """Test that value calculations are correct."""
        result_data = calculate_indicators(sample_data_dict, save_output=False)

        # VAL01 = processing_time * 2
        # First row: 10.0 * 2 = 20.0
        assert result_data['df_process']['VAL01'].iloc[0] == 20.0

        # REVENUE = component_value * quantity
        # First row: 100.0 * 1 = 100.0
        assert result_data['df_process']['REVENUE'].iloc[0] == 100.0

    def test_handles_empty_dataframe(self):
        """Test handling of empty dataframes."""
        empty_data = {
            'df_process': pd.DataFrame(),
            'df_product': pd.DataFrame(),
            'df_resource': pd.DataFrame(),
            'df_system': pd.DataFrame(),
            'indicators': {'indicators': []},
            'values': {'values': [], 'special_values': []},
            'attributes': {}
        }

        # Should not raise an error
        result_data = calculate_indicators(empty_data, save_output=False)

        assert result_data is not None

    def test_multiple_experiments(self, sample_data_dict):
        """Test calculation across multiple experiments."""
        result_data = calculate_indicators(sample_data_dict, save_output=False)

        # Check that all rows have indicator values
        assert len(result_data['df_process']) == 6
        assert result_data['df_process']['IND01'].notna().all()
        assert result_data['df_process']['IND02'].notna().all()

    @pytest.mark.unit
    def test_indicator_precision(self, sample_data_dict):
        """Test that indicator values are rounded to 2 decimal places."""
        result_data = calculate_indicators(sample_data_dict, save_output=False)

        # Check that all values have at most 2 decimal places
        for col in ['IND01', 'IND02']:
            values = result_data['df_process'][col]
            for val in values:
                # Check that value has at most 2 decimal places
                assert round(val, 2) == val
