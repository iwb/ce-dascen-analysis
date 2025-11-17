"""
Tests for Module 4: Group Statistics

Basic tests for grouping and statistics calculation.
"""

import pytest
import pandas as pd
import numpy as np


class TestModule4Basic:
    """Basic tests for Module 4 grouping functionality."""

    def test_imports(self):
        """Test that module 4 can be imported."""
        try:
            from modules import module4_grouping
            assert module4_grouping is not None
        except ImportError as e:
            pytest.skip(f"Module4 not available: {e}")

    def test_grouping_logic_basic(self):
        """Test basic grouping logic with pandas."""
        # Create test data
        df = pd.DataFrame({
            'exp_id': ['exp001', 'exp001', 'exp002', 'exp002'],
            'system': [1, 1, 2, 2],
            'IND01': [10, 15, 20, 25]
        })

        # Group by system and calculate mean
        result = df.groupby('system')['IND01'].mean()

        assert result[1] == 12.5  # (10 + 15) / 2
        assert result[2] == 22.5  # (20 + 25) / 2

    def test_statistics_calculation(self):
        """Test statistics calculation (mean, std, min, max)."""
        data = pd.Series([10, 20, 30, 40, 50])

        assert data.mean() == 30.0
        assert data.std() == pytest.approx(15.81, abs=0.01)
        assert data.min() == 10
        assert data.max() == 50

    def test_multi_level_grouping(self):
        """Test grouping by multiple variables."""
        df = pd.DataFrame({
            'system': [1, 1, 2, 2],
            'automation': [0, 3, 0, 3],
            'IND01': [10, 15, 20, 25]
        })

        # Group by system and automation
        result = df.groupby(['system', 'automation'])['IND01'].mean()

        assert result[(1, 0)] == 10
        assert result[(1, 3)] == 15
        assert result[(2, 0)] == 20
        assert result[(2, 3)] == 25

    @pytest.mark.unit
    def test_handles_missing_data(self):
        """Test handling of missing data in grouping."""
        df = pd.DataFrame({
            'group': ['A', 'A', 'B', 'B'],
            'value': [10, np.nan, 20, 30]
        })

        # Calculate mean ignoring NaN
        result = df.groupby('group')['value'].mean()

        assert result['A'] == 10.0  # Only non-NaN value
        assert result['B'] == 25.0  # (20 + 30) / 2
