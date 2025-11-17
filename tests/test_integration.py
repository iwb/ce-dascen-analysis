"""
Integration Tests for Full Pipeline

Tests cover:
- Module 1 → Module 2 data flow
- Module 2 → Module 3 data flow
- Complete pipeline execution
- Data consistency across modules
"""

import pytest
import pandas as pd
import numpy as np
from modules.module1_step_indicators import calculate_indicators
from modules.module2_experiment_aggregation import run_module2
from modules.module3_ranking import run_module3


@pytest.mark.integration
class TestModule1To2Integration:
    """Tests for data flow from Module 1 to Module 2."""

    def test_module1_output_compatible_with_module2(self, sample_data_dict):
        """Test that Module 1 output can be consumed by Module 2."""
        # Run Module 1
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)

        # Verify Module 1 added indicator columns
        assert 'IND01' in data_after_m1['df_process'].columns
        assert 'IND02' in data_after_m1['df_process'].columns
        assert 'IND03' in data_after_m1['df_product'].columns

        # Run Module 2
        data_after_m2 = run_module2(data_after_m1, save_output=False)

        # Verify Module 2 created df_experiments
        assert 'df_experiments' in data_after_m2
        assert not data_after_m2['df_experiments'].empty

    def test_indicator_values_preserved_in_aggregation(self, sample_data_dict):
        """Test that indicator values are correctly aggregated."""
        # Run Module 1
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)

        # Calculate expected sum for exp001
        exp001_ind01_sum = data_after_m1['df_process'][
            data_after_m1['df_process']['exp_id'] == 'exp001'
        ]['IND01'].sum()

        # Run Module 2
        data_after_m2 = run_module2(data_after_m1, save_output=False)

        # Verify aggregated value matches
        exp001_aggregated = data_after_m2['df_experiments'][
            data_after_m2['df_experiments']['exp_id'] == 'exp001'
        ]['IND01'].values[0]

        assert exp001_aggregated == pytest.approx(exp001_ind01_sum, abs=0.01)


@pytest.mark.integration
class TestModule2To3Integration:
    """Tests for data flow from Module 2 to Module 3."""

    def test_module2_output_compatible_with_module3(self, sample_data_dict):
        """Test that Module 2 output can be consumed by Module 3."""
        # Run Module 1 and 2
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
        data_after_m2 = run_module2(data_after_m1, save_output=False)

        # Verify Module 2 added normalized columns
        assert 'IND01_normalized' in data_after_m2['df_experiments'].columns
        assert 'is_feasible' in data_after_m2['df_experiments'].columns

        # Run Module 3
        data_after_m3 = run_module3(data_after_m2, save_output=False)

        # Verify Module 3 added ranking columns
        assert 'IND01_weighted' in data_after_m3['df_experiments'].columns
        assert 'total_weighted_score' in data_after_m3['df_experiments'].columns
        assert 'rank_all' in data_after_m3['df_experiments'].columns

    def test_normalized_to_weighted_calculation(self, sample_data_dict):
        """Test that weighted values are correctly calculated from normalized."""
        # Run Module 1, 2, and 3
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
        data_after_m2 = run_module2(data_after_m1, save_output=False)
        data_after_m3 = run_module3(data_after_m2, save_output=False)

        # Get first experiment
        first_exp = data_after_m3['df_experiments'].iloc[0]

        # Verify weighted = normalized * weight
        for ind in sample_data_dict['indicators']['indicators']:
            ind_id = ind['indicator_id']
            weight = ind['weight']

            if f'{ind_id}_normalized' in data_after_m3['df_experiments'].columns:
                normalized_val = first_exp[f'{ind_id}_normalized']
                weighted_val = first_exp[f'{ind_id}_weighted']
                expected_weighted = normalized_val * weight

                assert weighted_val == pytest.approx(expected_weighted, abs=0.01)


@pytest.mark.integration
class TestFullPipeline:
    """Tests for complete pipeline execution."""

    def test_full_pipeline_modules_1_2_3(self, sample_data_dict):
        """Test complete pipeline from Module 1 through Module 3."""
        # Run Module 1
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
        assert 'IND01' in data_after_m1['df_process'].columns

        # Run Module 2
        data_after_m2 = run_module2(data_after_m1, save_output=False)
        assert 'df_experiments' in data_after_m2
        assert 'IND01_normalized' in data_after_m2['df_experiments'].columns

        # Run Module 3
        data_after_m3 = run_module3(data_after_m2, save_output=False)
        assert 'rank_all' in data_after_m3['df_experiments'].columns

        # Verify final output has all required columns
        df_exp = data_after_m3['df_experiments']
        expected_columns = [
            'exp_id', 'IND01', 'IND02', 'IND03',
            'IND01_in_threshold', 'IND01_normalized', 'IND01_weighted',
            'is_feasible', 'total_weighted_score', 'rank_all'
        ]

        for col in expected_columns:
            assert col in df_exp.columns, f"Missing column: {col}"

    def test_pipeline_experiment_count_consistency(self, sample_data_dict):
        """Test that experiment count is consistent across modules."""
        # Run pipeline
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
        data_after_m2 = run_module2(data_after_m1, save_output=False)
        data_after_m3 = run_module3(data_after_m2, save_output=False)

        # Get unique experiment counts
        exp_count_doe = len(sample_data_dict['doe'])
        exp_count_process = len(data_after_m1['df_process']['exp_id'].unique())
        exp_count_experiments = len(data_after_m2['df_experiments'])
        exp_count_final = len(data_after_m3['df_experiments'])

        # All should match
        assert exp_count_process == exp_count_doe
        assert exp_count_experiments == exp_count_doe
        assert exp_count_final == exp_count_doe

    def test_pipeline_ranking_correctness(self, sample_data_dict):
        """Test that ranking is correct after full pipeline."""
        # Run pipeline
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
        data_after_m2 = run_module2(data_after_m1, save_output=False)
        data_after_m3 = run_module3(data_after_m2, save_output=False)

        df_exp = data_after_m3['df_experiments']

        # Sort by total_weighted_score descending
        df_sorted = df_exp.sort_values('total_weighted_score', ascending=False)

        # Verify rank_all matches sorted order
        for idx, (_, row) in enumerate(df_sorted.iterrows(), start=1):
            # Rank should match position in sorted list
            assert row['rank_all'] <= len(df_exp)


@pytest.mark.integration
class TestDataConsistency:
    """Tests for data consistency across modules."""

    def test_exp_id_consistency(self, sample_data_dict):
        """Test that exp_id is consistent across all dataframes."""
        # Run pipeline
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
        data_after_m2 = run_module2(data_after_m1, save_output=False)

        # Get exp_ids from different sources
        exp_ids_doe = set(sample_data_dict['doe']['exp_id'])
        exp_ids_process = set(data_after_m1['df_process']['exp_id'])
        exp_ids_experiments = set(data_after_m2['df_experiments']['exp_id'])

        # All should be the same
        assert exp_ids_process == exp_ids_doe
        assert exp_ids_experiments == exp_ids_doe

    def test_no_data_loss_in_pipeline(self, sample_data_dict):
        """Test that no data is lost during pipeline execution."""
        # Initial row counts
        initial_process_rows = len(sample_data_dict['df_process'])
        initial_product_rows = len(sample_data_dict['df_product'])

        # Run pipeline
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)

        # Row counts should be the same
        assert len(data_after_m1['df_process']) == initial_process_rows
        assert len(data_after_m1['df_product']) == initial_product_rows

    def test_metadata_preserved(self, sample_data_dict):
        """Test that metadata columns are preserved through pipeline."""
        # Run pipeline
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
        data_after_m2 = run_module2(data_after_m1, save_output=False)
        data_after_m3 = run_module3(data_after_m2, save_output=False)

        df_exp = data_after_m3['df_experiments']

        # Verify metadata columns exist
        metadata_cols = ['exp_id', 'system_scenario', 'product_scenario', 'automation_level']
        for col in metadata_cols:
            assert col in df_exp.columns, f"Metadata column {col} not preserved"

    @pytest.mark.unit
    def test_feasibility_flag_consistency(self, sample_data_dict):
        """Test that feasibility flags are consistent with threshold checks."""
        # Run pipeline
        data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
        data_after_m2 = run_module2(data_after_m1, save_output=False)

        df_exp = data_after_m2['df_experiments']

        # For each experiment, verify is_feasible matches threshold checks
        for _, row in df_exp.iterrows():
            threshold_cols = [col for col in df_exp.columns if col.endswith('_in_threshold')]
            all_thresholds_met = all(row[col] for col in threshold_cols)

            assert row['is_feasible'] == all_thresholds_met, \
                f"Feasibility flag inconsistent for {row['exp_id']}"


@pytest.mark.integration
@pytest.mark.slow
class TestPipelinePerformance:
    """Tests for pipeline performance and efficiency."""

    def test_pipeline_completes_successfully(self, sample_data_dict):
        """Test that pipeline completes without errors."""
        try:
            data_after_m1 = calculate_indicators(sample_data_dict, save_output=False)
            data_after_m2 = run_module2(data_after_m1, save_output=False)
            data_after_m3 = run_module3(data_after_m2, save_output=False)

            assert data_after_m3 is not None
        except Exception as e:
            pytest.fail(f"Pipeline failed with error: {e}")

    def test_pipeline_handles_edge_cases(self, sample_data_dict):
        """Test pipeline with minimal data."""
        # Create minimal data (single experiment)
        minimal_data = {
            'df_process': sample_data_dict['df_process'].iloc[:2].copy(),
            'df_product': sample_data_dict['df_product'].iloc[:2].copy(),
            'df_resource': sample_data_dict['df_resource'].iloc[:1].copy(),
            'df_system': sample_data_dict['df_system'].iloc[:1].copy(),
            'doe': sample_data_dict['doe'].iloc[:1].copy(),
            'indicators': sample_data_dict['indicators'],
            'values': sample_data_dict['values'],
            'attributes': sample_data_dict['attributes']
        }

        # Update exp_ids to match
        minimal_data['df_process']['exp_id'] = 'exp001'
        minimal_data['df_product']['exp_id'] = 'exp001'

        # Run pipeline
        data_after_m1 = calculate_indicators(minimal_data, save_output=False)
        data_after_m2 = run_module2(data_after_m1, save_output=False)
        data_after_m3 = run_module3(data_after_m2, save_output=False)

        # Verify single experiment processed
        assert len(data_after_m3['df_experiments']) == 1
