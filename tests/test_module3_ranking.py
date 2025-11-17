"""
Tests for Module 3: Weighting & Ranking

Tests cover:
- Applying weights to normalized indicators
- Calculating total weighted scores
- Ranking experiments (all and feasible only)
- Category-specific scores
- Edge cases and error handling
"""

import pytest
import pandas as pd
import numpy as np
from modules.module3_ranking import (
    apply_weights,
    calculate_total_score,
    rank_experiments,
    generate_summary_statistics,
    run_module3
)


class TestApplyWeights:
    """Tests for the apply_weights function."""

    def test_basic_weight_application(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that weights are applied correctly."""
        result_df = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)

        # Check that weighted columns were created
        assert 'IND01_weighted' in result_df.columns
        assert 'IND02_weighted' in result_df.columns
        assert 'IND03_weighted' in result_df.columns

    def test_weight_calculation(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test weight calculation values."""
        result_df = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)

        # IND01_normalized = 1.0, weight = 0.3 → weighted = 0.3
        assert result_df['IND01_weighted'].iloc[0] == pytest.approx(0.3, abs=0.01)

        # IND02_normalized = 0.71, weight = 0.2 → weighted = 0.142 → 0.14
        assert result_df['IND02_weighted'].iloc[0] == pytest.approx(0.14, abs=0.01)

        # IND03_normalized = 0.67, weight = 0.5 → weighted = 0.335 → 0.34
        assert result_df['IND03_weighted'].iloc[0] == pytest.approx(0.34, abs=0.01)

    def test_weight_precision(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that weighted values are rounded to specified precision."""
        result_df = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)

        # All weighted values should have at most 2 decimal places
        for col in ['IND01_weighted', 'IND02_weighted', 'IND03_weighted']:
            for val in result_df[col]:
                assert round(val, 2) == val

    def test_handles_missing_normalized_column(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test handling when normalized column is missing."""
        # Remove one normalized column
        df_copy = sample_df_experiments_normalized.copy()
        df_copy = df_copy.drop(columns=['IND02_normalized'])

        result_df = apply_weights(df_copy, sample_indicators_config, score_precision=2)

        # Should have IND01 and IND03 weighted, but not IND02
        assert 'IND01_weighted' in result_df.columns
        assert 'IND02_weighted' not in result_df.columns
        assert 'IND03_weighted' in result_df.columns

    def test_handles_nan_values(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that NaN values are handled correctly."""
        # Introduce NaN
        sample_df_experiments_normalized.loc[0, 'IND01_normalized'] = np.nan

        result_df = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)

        # NaN should be filled with 0
        assert result_df['IND01_weighted'].iloc[0] == 0.0

    def test_empty_dataframe(self, sample_indicators_config):
        """Test handling of empty dataframe."""
        empty_df = pd.DataFrame()

        result_df = apply_weights(empty_df, sample_indicators_config, score_precision=2)

        assert result_df.empty


class TestCalculateTotalScore:
    """Tests for the calculate_total_score function."""

    def test_total_score_calculation(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that total score is calculated correctly."""
        # First apply weights
        df_with_weights = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)

        # Then calculate total score
        result_df = calculate_total_score(df_with_weights, sample_indicators_config, score_precision=2)

        # Check that score columns exist
        assert 'economic_score' in result_df.columns
        assert 'environmental_score' in result_df.columns
        assert 'total_weighted_score' in result_df.columns

    def test_total_score_values(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test total score calculation values."""
        # Apply weights
        df_with_weights = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)

        # Calculate total score
        result_df = calculate_total_score(df_with_weights, sample_indicators_config, score_precision=2)

        # First row: IND01_weighted (~0.3) + IND02_weighted (~0.14) + IND03_weighted (~0.34) ≈ 0.78
        expected_total = (
            df_with_weights['IND01_weighted'].iloc[0] +
            df_with_weights['IND02_weighted'].iloc[0] +
            df_with_weights['IND03_weighted'].iloc[0]
        )
        assert result_df['total_weighted_score'].iloc[0] == pytest.approx(expected_total, abs=0.01)

    def test_category_scores(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that category scores are calculated correctly."""
        # Apply weights
        df_with_weights = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)

        # Calculate total score
        result_df = calculate_total_score(df_with_weights, sample_indicators_config, score_precision=2)

        # Economic score should be IND01_weighted (IND01 is economic)
        assert result_df['economic_score'].iloc[0] == pytest.approx(df_with_weights['IND01_weighted'].iloc[0], abs=0.01)

        # Environmental score should be IND02_weighted + IND03_weighted (both environmental)
        expected_env = df_with_weights['IND02_weighted'].iloc[0] + df_with_weights['IND03_weighted'].iloc[0]
        assert result_df['environmental_score'].iloc[0] == pytest.approx(expected_env, abs=0.01)

    def test_score_precision(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that scores are rounded to specified precision."""
        df_with_weights = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)
        result_df = calculate_total_score(df_with_weights, sample_indicators_config, score_precision=2)

        # All scores should have at most 2 decimal places
        for col in ['economic_score', 'environmental_score', 'total_weighted_score']:
            for val in result_df[col]:
                assert round(val, 2) == val


class TestCreateRankings:
    """Tests for the rank_experiments function."""

    def test_ranking_all_experiments(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test ranking of all experiments."""
        # Apply weights and calculate scores
        df_with_weights = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)
        df_with_scores = calculate_total_score(df_with_weights, sample_indicators_config, score_precision=2)

        # Create rankings
        result_df = rank_experiments(df_with_scores)

        # Check that rank columns exist
        assert 'rank_all' in result_df.columns
        assert 'rank' in result_df.columns

    def test_rank_all_correct(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that rank_all is correct."""
        # Apply weights and calculate scores
        df_with_weights = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)
        df_with_scores = calculate_total_score(df_with_weights, sample_indicators_config, score_precision=2)

        # Create rankings
        result_df = rank_experiments(df_with_scores)

        # Highest score should have rank 1
        highest_score_idx = result_df['total_weighted_score'].idxmax()
        assert result_df.loc[highest_score_idx, 'rank_all'] == 1

    def test_rank_feasible_only(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that rank column only ranks feasible experiments."""
        # Apply weights and calculate scores
        df_with_weights = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)
        df_with_scores = calculate_total_score(df_with_weights, sample_indicators_config, score_precision=2)

        # Create rankings
        result_df = rank_experiments(df_with_scores)

        # Infeasible experiments should have NaN for rank
        infeasible_mask = ~result_df['is_feasible']
        if infeasible_mask.any():
            assert result_df.loc[infeasible_mask, 'rank'].isna().all()

    def test_rank_order(self, sample_df_experiments_normalized, sample_indicators_config):
        """Test that ranks are in descending order of score."""
        # Apply weights and calculate scores
        df_with_weights = apply_weights(sample_df_experiments_normalized, sample_indicators_config, score_precision=2)
        df_with_scores = calculate_total_score(df_with_weights, sample_indicators_config, score_precision=2)

        # Create rankings
        result_df = rank_experiments(df_with_scores)

        # Sort by rank_all and check that scores are descending
        sorted_df = result_df.sort_values('rank_all')
        scores = sorted_df['total_weighted_score'].values

        # Scores should be in descending order
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]


class TestGenerateSummary:
    """Tests for the generate_summary_statistics function."""

    def test_summary_generation(self, sample_df_experiments_ranked, sample_indicators_config):
        """Test that summary is generated."""
        summary = generate_summary_statistics(
            sample_df_experiments_ranked,
            sample_indicators_config,
            score_precision=4,
            separator_width=70,
            top_n_display=3
        )

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_summary_contains_key_info(self, sample_df_experiments_ranked, sample_indicators_config):
        """Test that summary contains key information."""
        summary = generate_summary_statistics(
            sample_df_experiments_ranked,
            sample_indicators_config,
            score_precision=4,
            separator_width=70,
            top_n_display=3
        )

        # Should contain experiment count
        assert "experiments" in summary.lower() or "Experiments" in summary

    def test_summary_empty_dataframe(self, sample_indicators_config):
        """Test summary with empty dataframe."""
        empty_df = pd.DataFrame()

        summary = generate_summary_statistics(
            empty_df,
            sample_indicators_config,
            score_precision=4,
            separator_width=70,
            top_n_display=3
        )

        assert summary is not None


class TestRunModule3:
    """Integration tests for run_module3 function."""

    def test_run_module3_complete_pipeline(self, sample_data_dict, sample_df_experiments_normalized):
        """Test complete module 3 pipeline."""
        # Add df_experiments to data
        sample_data_dict['df_experiments'] = sample_df_experiments_normalized.copy()

        result_data = run_module3(sample_data_dict, save_output=False)

        # Check that all columns were added
        df_exp = result_data['df_experiments']
        assert 'IND01_weighted' in df_exp.columns
        assert 'IND02_weighted' in df_exp.columns
        assert 'IND03_weighted' in df_exp.columns
        assert 'economic_score' in df_exp.columns
        assert 'environmental_score' in df_exp.columns
        assert 'total_weighted_score' in df_exp.columns
        assert 'rank_all' in df_exp.columns
        assert 'rank' in df_exp.columns

    def test_run_module3_ranking_logic(self, sample_data_dict, sample_df_experiments_normalized):
        """Test that ranking logic works correctly."""
        # Modify scores to have clear ranking
        sample_df_experiments_normalized.loc[0, 'IND01_normalized'] = 1.0
        sample_df_experiments_normalized.loc[1, 'IND01_normalized'] = 0.5
        sample_df_experiments_normalized.loc[2, 'IND01_normalized'] = 0.0

        sample_data_dict['df_experiments'] = sample_df_experiments_normalized.copy()

        result_data = run_module3(sample_data_dict, save_output=False)

        df_exp = result_data['df_experiments']

        # First experiment should have highest score (assuming all feasible)
        # Check that rank_all is assigned
        assert df_exp['rank_all'].min() == 1
        assert df_exp['rank_all'].max() <= 3

    def test_run_module3_handles_empty_data(self, sample_data_dict):
        """Test module 3 with empty experiments dataframe."""
        sample_data_dict['df_experiments'] = pd.DataFrame()

        result_data = run_module3(sample_data_dict, save_output=False)

        # Should handle gracefully
        assert 'df_experiments' in result_data

    @pytest.mark.unit
    def test_run_module3_weights_sum_to_one(self, sample_data_dict, sample_df_experiments_normalized):
        """Test that indicator weights sum to 1.0."""
        sample_data_dict['df_experiments'] = sample_df_experiments_normalized.copy()

        # Check that weights in config sum to 1.0
        weights_sum = sum(ind['weight'] for ind in sample_data_dict['indicators']['indicators'])
        assert weights_sum == pytest.approx(1.0, abs=0.01)

    @pytest.mark.unit
    def test_run_module3_score_range(self, sample_data_dict, sample_df_experiments_normalized):
        """Test that total weighted scores are in expected range."""
        sample_data_dict['df_experiments'] = sample_df_experiments_normalized.copy()

        result_data = run_module3(sample_data_dict, save_output=False)

        df_exp = result_data['df_experiments']

        # Scores should typically be between 0 and 1 (can be negative for violations)
        assert df_exp['total_weighted_score'].max() <= 1.0
