"""
Tests for Module 2: Experiment Aggregation, Filtering, and Normalization

Tests cover:
- Indicator aggregation to experiment level
- Threshold filtering and feasibility checks
- Indicator normalization
- Edge cases and error handling
"""

import pytest
import pandas as pd
import numpy as np
from modules.module2_experiment_aggregation import (
    aggregate_to_experiment_level,
    apply_threshold_filters,
    normalize_indicators,
    generate_summary_statistics,
    run_module2
)


class TestAggregateToExperimentLevel:
    """Tests for the aggregate_to_experiment_level function."""

    def test_basic_aggregation_sum(self, sample_data_dict):
        """Test sum aggregation works correctly."""
        # Add indicators to df_process for testing
        sample_data_dict['df_process']['IND01'] = [50.0, 75.0, 60.0, 90.0, 40.0, 70.0]

        result_df = aggregate_to_experiment_level(sample_data_dict)

        # exp001: 50 + 75 = 125
        # exp002: 60 + 90 = 150
        # exp003: 40 + 70 = 110
        assert result_df[result_df['exp_id'] == 'exp001']['IND01'].values[0] == 125.0
        assert result_df[result_df['exp_id'] == 'exp002']['IND01'].values[0] == 150.0
        assert result_df[result_df['exp_id'] == 'exp003']['IND01'].values[0] == 110.0

    def test_basic_aggregation_average(self, sample_data_dict):
        """Test average aggregation works correctly."""
        # Add IND03 to df_product for testing
        sample_data_dict['df_product']['IND03'] = [1.8, 2.55, 1.5, 2.4, 1.9, 2.7]

        result_df = aggregate_to_experiment_level(sample_data_dict)

        # exp001: (1.8 + 2.55) / 2 = 2.175 → 2.18
        # exp002: (1.5 + 2.4) / 2 = 1.95
        # exp003: (1.9 + 2.7) / 2 = 2.3
        assert result_df[result_df['exp_id'] == 'exp001']['IND03'].values[0] == pytest.approx(2.18, abs=0.05)
        assert result_df[result_df['exp_id'] == 'exp002']['IND03'].values[0] == pytest.approx(1.95, abs=0.05)
        assert result_df[result_df['exp_id'] == 'exp003']['IND03'].values[0] == pytest.approx(2.30, abs=0.05)

    def test_aggregation_preserves_metadata(self, sample_data_dict):
        """Test that DoE metadata is preserved."""
        sample_data_dict['df_process']['IND01'] = [50.0, 75.0, 60.0, 90.0, 40.0, 70.0]

        result_df = aggregate_to_experiment_level(sample_data_dict)

        # Check that metadata columns are present
        assert 'exp_id' in result_df.columns
        assert 'system_scenario' in result_df.columns
        assert 'product_scenario' in result_df.columns
        assert 'automation_level' in result_df.columns

        # Check values
        assert len(result_df) == 3

    def test_handles_missing_indicators(self, sample_data_dict):
        """Test handling of missing indicator columns."""
        # Don't add IND01 to df_process
        result_df = aggregate_to_experiment_level(sample_data_dict)

        # Should still return a dataframe with metadata
        assert len(result_df) == 3
        assert 'exp_id' in result_df.columns

    def test_filters_to_available_experiments(self, sample_data_dict):
        """Test that only experiments with data are included."""
        # Remove one experiment from df_process
        sample_data_dict['df_process'] = sample_data_dict['df_process'][
            sample_data_dict['df_process']['exp_id'] != 'exp003'
        ]
        sample_data_dict['df_process']['IND01'] = [50.0, 75.0, 60.0, 90.0]

        result_df = aggregate_to_experiment_level(sample_data_dict)

        # Should only have 2 experiments
        assert len(result_df) == 2
        assert 'exp001' in result_df['exp_id'].values
        assert 'exp002' in result_df['exp_id'].values
        assert 'exp003' not in result_df['exp_id'].values


class TestApplyThresholdFilters:
    """Tests for the apply_threshold_filters function."""

    def test_threshold_minimize_pass(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test threshold check for minimize indicators (passing)."""
        result_df = apply_threshold_filters(sample_df_experiments_aggregated, sample_indicators_config)

        # IND01 minimize, threshold 1000 - all should pass
        assert result_df['IND01_in_threshold'].all()

    def test_threshold_minimize_fail(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test threshold check for minimize indicators (failing)."""
        # Make one value exceed threshold
        sample_df_experiments_aggregated.loc[1, 'IND01'] = 1500  # exp002

        result_df = apply_threshold_filters(sample_df_experiments_aggregated, sample_indicators_config)

        # exp001 and exp003 should pass, exp002 should fail
        assert result_df.iloc[0]['IND01_in_threshold'] == True
        assert result_df.iloc[1]['IND01_in_threshold'] == False
        assert result_df.iloc[2]['IND01_in_threshold'] == True

    def test_threshold_maximize_pass(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test threshold check for maximize indicators (passing)."""
        result_df = apply_threshold_filters(sample_df_experiments_aggregated, sample_indicators_config)

        # IND03 maximize, threshold 0.7 - all should pass (values are 5.25, 4.65, 5.55)
        assert result_df['IND03_in_threshold'].all()

    def test_threshold_maximize_fail(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test threshold check for maximize indicators (failing)."""
        # Make one value fall below threshold
        sample_df_experiments_aggregated.loc[1, 'IND03'] = 0.5  # exp002

        result_df = apply_threshold_filters(sample_df_experiments_aggregated, sample_indicators_config)

        # exp001 and exp003 should pass, exp002 should fail
        assert result_df.iloc[0]['IND03_in_threshold'] == True
        assert result_df.iloc[1]['IND03_in_threshold'] == False
        assert result_df.iloc[2]['IND03_in_threshold'] == True

    def test_feasibility_flag(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test that feasibility flag is set correctly."""
        # Make exp002 fail on IND01
        sample_df_experiments_aggregated.loc[1, 'IND01'] = 1500

        result_df = apply_threshold_filters(sample_df_experiments_aggregated, sample_indicators_config)

        # exp001 and exp003 should be feasible
        assert result_df.iloc[0]['is_feasible'] == True
        assert result_df.iloc[1]['is_feasible'] == False
        assert result_df.iloc[2]['is_feasible'] == True

    def test_violation_count(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test that violation counts are calculated correctly."""
        # Make exp002 fail on both IND01 and IND03
        sample_df_experiments_aggregated.loc[1, 'IND01'] = 1500
        sample_df_experiments_aggregated.loc[1, 'IND03'] = 0.5

        result_df = apply_threshold_filters(sample_df_experiments_aggregated, sample_indicators_config)

        # exp002 should have 2 violations
        assert result_df.iloc[1]['threshold_violations'] == 2

    def test_empty_dataframe(self, sample_indicators_config):
        """Test handling of empty dataframe."""
        empty_df = pd.DataFrame()

        result_df = apply_threshold_filters(empty_df, sample_indicators_config)

        # Should return empty dataframe
        assert result_df.empty


class TestNormalizeIndicators:
    """Tests for the normalize_indicators function."""

    def test_normalize_minimize_indicator(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test normalization of minimize indicator."""
        result_df = normalize_indicators(sample_df_experiments_aggregated, sample_indicators_config)

        # IND01 (minimize): best = 110, worst = 150
        # exp001 (125): (150 - 125) / (150 - 110) = 25/40 = 0.62
        # exp002 (150): (150 - 150) / (150 - 110) = 0/40 = 0.0
        # exp003 (110): (150 - 110) / (150 - 110) = 40/40 = 1.0
        assert result_df['IND01_normalized'].iloc[0] == pytest.approx(0.62, abs=0.01)
        assert result_df['IND01_normalized'].iloc[1] == pytest.approx(0.0, abs=0.01)
        assert result_df['IND01_normalized'].iloc[2] == pytest.approx(1.0, abs=0.01)

    def test_normalize_maximize_indicator(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test normalization of maximize indicator."""
        result_df = normalize_indicators(sample_df_experiments_aggregated, sample_indicators_config)

        # IND03 (maximize): best = 5.55, worst = 4.65
        # exp001 (5.25): (5.25 - 4.65) / (5.55 - 4.65) = 0.6 / 0.9 = 0.67
        # exp002 (4.65): (4.65 - 4.65) / (5.55 - 4.65) = 0 / 0.9 = 0.0
        # exp003 (5.55): (5.55 - 4.65) / (5.55 - 4.65) = 0.9 / 0.9 = 1.0
        assert result_df['IND03_normalized'].iloc[0] == pytest.approx(0.67, abs=0.01)
        assert result_df['IND03_normalized'].iloc[1] == pytest.approx(0.0, abs=0.01)
        assert result_df['IND03_normalized'].iloc[2] == pytest.approx(1.0, abs=0.01)

    def test_normalize_all_same_values(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test normalization when all values are identical."""
        # Make all IND01 values the same
        sample_df_experiments_aggregated['IND01'] = 125.0

        result_df = normalize_indicators(sample_df_experiments_aggregated, sample_indicators_config)

        # All should be normalized to 1.0
        assert (result_df['IND01_normalized'] == 1.0).all()

    def test_normalize_handles_inf(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test that infinite values are handled."""
        # This shouldn't happen normally, but test the safety check
        result_df = normalize_indicators(sample_df_experiments_aggregated, sample_indicators_config)

        # No inf values should be present
        assert not result_df['IND01_normalized'].isin([np.inf, -np.inf]).any()
        assert not result_df['IND02_normalized'].isin([np.inf, -np.inf]).any()
        assert not result_df['IND03_normalized'].isin([np.inf, -np.inf]).any()

    def test_normalized_range(self, sample_df_experiments_aggregated, sample_indicators_config):
        """Test that normalized values are in expected range."""
        result_df = normalize_indicators(sample_df_experiments_aggregated, sample_indicators_config)

        # Normalized values should typically be between 0 and 1 for feasible experiments
        # (can be negative for threshold violations)
        for col in ['IND01_normalized', 'IND02_normalized', 'IND03_normalized']:
            assert result_df[col].max() <= 1.0
            # Min could be negative if threshold is violated


class TestGenerateSummaryStatistics:
    """Tests for the generate_summary_statistics function."""

    def test_summary_with_data(self, sample_df_experiments_with_thresholds):
        """Test summary generation with valid data."""
        summary = generate_summary_statistics(sample_df_experiments_with_thresholds)

        assert "Total Experiments: 3" in summary
        assert "Feasible Experiments" in summary
        assert "Threshold Violations by Indicator" in summary

    def test_summary_empty_dataframe(self):
        """Test summary with empty dataframe."""
        empty_df = pd.DataFrame()

        summary = generate_summary_statistics(empty_df)

        assert "No experiments data available" in summary

    def test_summary_all_feasible(self, sample_df_experiments_with_thresholds):
        """Test summary when all experiments are feasible."""
        # Make all feasible
        sample_df_experiments_with_thresholds['is_feasible'] = True
        sample_df_experiments_with_thresholds['threshold_violations'] = 0

        summary = generate_summary_statistics(sample_df_experiments_with_thresholds)

        assert "Total Experiments: 3" in summary
        assert "Feasible Experiments: 3 (100.0%)" in summary


class TestRunModule2:
    """Integration tests for run_module2 function."""

    def test_run_module2_complete_pipeline(self, sample_data_dict):
        """Test complete module 2 pipeline."""
        # Add indicator columns
        sample_data_dict['df_process']['IND01'] = [50.0, 75.0, 60.0, 90.0, 40.0, 70.0]
        sample_data_dict['df_process']['IND02'] = [40.0, 60.0, 50.0, 70.0, 30.0, 56.0]
        sample_data_dict['df_product']['IND03'] = [1.8, 2.55, 1.5, 2.4, 1.9, 2.7]

        result_data = run_module2(sample_data_dict, save_output=False)

        # Check that df_experiments was created
        assert 'df_experiments' in result_data
        assert len(result_data['df_experiments']) == 3

        # Check that all required columns are present
        df_exp = result_data['df_experiments']
        assert 'IND01' in df_exp.columns
        assert 'IND02' in df_exp.columns
        assert 'IND03' in df_exp.columns
        assert 'IND01_in_threshold' in df_exp.columns
        assert 'IND01_normalized' in df_exp.columns
        assert 'is_feasible' in df_exp.columns
        assert 'threshold_violations' in df_exp.columns

    def test_run_module2_handles_empty_data(self):
        """Test module 2 with empty data."""
        empty_data = {
            'doe': pd.DataFrame(),
            'df_process': pd.DataFrame(),
            'df_product': pd.DataFrame(),
            'df_resource': pd.DataFrame(),
            'df_system': pd.DataFrame(),
            'indicators': {'indicators': []},
            'attributes': {}
        }

        result_data = run_module2(empty_data, save_output=False)

        # Should handle gracefully
        assert 'df_experiments' in result_data

    @pytest.mark.unit
    def test_run_module2_feasibility_calculation(self, sample_data_dict):
        """Test that feasibility is calculated correctly."""
        # Add indicators with one experiment violating threshold
        sample_data_dict['df_process']['IND01'] = [50.0, 75.0, 1200.0, 90.0, 40.0, 70.0]  # exp002 violates
        sample_data_dict['df_process']['IND02'] = [40.0, 60.0, 50.0, 70.0, 30.0, 56.0]
        sample_data_dict['df_product']['IND03'] = [1.8, 2.55, 1.5, 2.4, 1.9, 2.7]

        result_data = run_module2(sample_data_dict, save_output=False)

        df_exp = result_data['df_experiments']

        # exp001 and exp003 should be feasible, exp002 should not
        assert df_exp[df_exp['exp_id'] == 'exp001']['is_feasible'].values[0] == True
        assert df_exp[df_exp['exp_id'] == 'exp002']['is_feasible'].values[0] == False
        assert df_exp[df_exp['exp_id'] == 'exp003']['is_feasible'].values[0] == True
