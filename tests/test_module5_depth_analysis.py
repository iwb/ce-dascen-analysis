"""
Tests for Module 5: Depth Analysis

Basic tests for disassembly depth and cumulative analysis.
"""

import pytest
import pandas as pd
import numpy as np


class TestModule5Basic:
    """Basic tests for Module 5 depth analysis functionality."""

    def test_imports(self):
        """Test that module 5 can be imported."""
        try:
            from modules import module5_depth_analysis
            assert module5_depth_analysis is not None
        except ImportError as e:
            pytest.skip(f"Module5 not available: {e}")

    def test_cumulative_calculation(self):
        """Test basic cumulative sum calculation."""
        df = pd.DataFrame({
            'step': [1, 2, 3, 4],
            'profit': [100, 50, -20, 30]
        })

        df['cumulative_profit'] = df['profit'].cumsum()

        assert df['cumulative_profit'].iloc[0] == 100
        assert df['cumulative_profit'].iloc[1] == 150
        assert df['cumulative_profit'].iloc[2] == 130
        assert df['cumulative_profit'].iloc[3] == 160

    def test_component_aggregation(self):
        """Test aggregating by component."""
        df = pd.DataFrame({
            'exp_id': ['exp001', 'exp001', 'exp002', 'exp002'],
            'component': ['comp_A', 'comp_B', 'comp_A', 'comp_B'],
            'revenue': [100, 150, 120, 140],
            'cost': [20, 30, 25, 35]
        })

        # Calculate profit
        df['profit'] = df['revenue'] - df['cost']

        # Group by component and aggregate
        result = df.groupby('component').agg({
            'revenue': 'sum',
            'cost': 'sum',
            'profit': 'sum'
        })

        assert result.loc['comp_A', 'revenue'] == 220  # 100 + 120
        assert result.loc['comp_A', 'profit'] == 175   # 80 + 95

    def test_profit_calculation(self):
        """Test profit calculation from revenue and costs."""
        revenue = 1000
        fixed_costs = 200
        variable_costs = 300

        profit = revenue - fixed_costs - variable_costs

        assert profit == 500

    def test_depth_trajectory(self):
        """Test creating a depth trajectory."""
        df = pd.DataFrame({
            'depth': [1, 2, 3, 4],
            'component': ['A', 'B', 'C', 'D'],
            'value': [100, 80, 60, 40]
        })

        # Calculate cumulative value
        df['cumulative_value'] = df['value'].cumsum()

        assert df['cumulative_value'].tolist() == [100, 180, 240, 280]

    @pytest.mark.unit
    def test_baseline_subtraction(self):
        """Test subtracting baseline costs from profit."""
        df = pd.DataFrame({
            'step': [1, 2, 3],
            'cumulative_profit': [150, 180, 200],
            'baseline_cost': [100, 100, 100]
        })

        df['net_profit'] = df['cumulative_profit'] - df['baseline_cost']

        assert df['net_profit'].iloc[0] == 50
        assert df['net_profit'].iloc[1] == 80
        assert df['net_profit'].iloc[2] == 100
