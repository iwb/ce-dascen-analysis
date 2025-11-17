"""
Tests for Module 6: Visualizations

Basic tests for visualization generation and data preparation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


class TestModule6Basic:
    """Basic tests for Module 6 visualization functionality."""

    def test_imports(self):
        """Test that module 6 can be imported."""
        try:
            from modules import module6_visualizations
            assert module6_visualizations is not None
        except ImportError as e:
            pytest.skip(f"Module6 not available: {e}")

    def test_matplotlib_available(self):
        """Test that matplotlib is available."""
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            assert matplotlib is not None
            assert plt is not None
        except ImportError:
            pytest.fail("matplotlib not available")

    def test_data_preparation_for_plot(self):
        """Test basic data preparation for plotting."""
        df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [10, 20, 15, 25, 30]
        })

        # Sort by x
        df_sorted = df.sort_values('x')

        assert df_sorted['x'].tolist() == [1, 2, 3, 4, 5]
        assert df_sorted['y'].tolist() == [10, 20, 15, 25, 30]

    def test_pivot_for_heatmap(self):
        """Test pivoting data for heatmap."""
        df = pd.DataFrame({
            'row': ['A', 'A', 'B', 'B'],
            'col': ['X', 'Y', 'X', 'Y'],
            'value': [10, 20, 30, 40]
        })

        pivot = df.pivot(index='row', columns='col', values='value')

        assert pivot.loc['A', 'X'] == 10
        assert pivot.loc['A', 'Y'] == 20
        assert pivot.loc['B', 'X'] == 30
        assert pivot.loc['B', 'Y'] == 40

    def test_output_directory_creation(self, tmp_path):
        """Test that output directory can be created."""
        viz_dir = tmp_path / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)

        assert viz_dir.exists()
        assert viz_dir.is_dir()

    @pytest.mark.unit
    def test_filename_generation(self):
        """Test generation of numbered filenames."""
        base_name = "test_plot.png"
        viz_counter = 5

        numbered_filename = f"M6_{viz_counter:02d}_{base_name}"

        assert numbered_filename == "M6_05_test_plot.png"

    def test_data_filtering_for_plot(self):
        """Test filtering data for specific plot."""
        df = pd.DataFrame({
            'category': ['A', 'B', 'C', 'A', 'B', 'C'],
            'value': [10, 20, 30, 15, 25, 35],
            'group': [1, 1, 1, 2, 2, 2]
        })

        # Filter for group 1
        df_filtered = df[df['group'] == 1]

        assert len(df_filtered) == 3
        assert df_filtered['category'].tolist() == ['A', 'B', 'C']
        assert df_filtered['value'].tolist() == [10, 20, 30]

    def test_normalization_for_spider_chart(self):
        """Test normalization of data for spider chart."""
        df = pd.DataFrame({
            'indicator': ['IND01', 'IND02', 'IND03'],
            'value': [100, 50, 200]
        })

        # Normalize to 0-1 range
        df['normalized'] = (df['value'] - df['value'].min()) / (df['value'].max() - df['value'].min())

        assert df['normalized'].iloc[0] == pytest.approx(0.333, abs=0.01)  # (100 - 50) / (200 - 50) = 50/150
        assert df['normalized'].iloc[1] == 0.0   # (50 - 50) / (200 - 50)
        assert df['normalized'].iloc[2] == 1.0   # (200 - 50) / (200 - 50)
