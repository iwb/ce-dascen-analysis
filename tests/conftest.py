"""
Pytest Configuration and Shared Fixtures

This module provides shared fixtures for testing the analytics framework.
"""

import pytest
import pandas as pd
import numpy as np
import json
from pathlib import Path


@pytest.fixture
def sample_indicators_config():
    """Sample indicators configuration for testing."""
    return {
        'indicators': [
            {
                'indicator_id': 'IND01',
                'indicator_name': 'Test Indicator 01',
                'target_dataframe': 'df_process',
                'aggregation': 'sum',
                'direction': 'minimize',
                'threshold': 1000,
                'weight': 0.3,
                'category': 'economic',
                'formula': 'time * cost_rate',
                'indicator_variables': {
                    'time': {'source': 'dataframe', 'column': 'processing_time'},
                    'cost_rate': {'source': 'dataframe', 'column': 'station_cost'}
                }
            },
            {
                'indicator_id': 'IND02',
                'indicator_name': 'Test Indicator 02',
                'target_dataframe': 'df_process',
                'aggregation': 'sum',
                'direction': 'minimize',
                'threshold': 500,
                'weight': 0.2,
                'category': 'environmental',
                'formula': 'energy * factor',
                'indicator_variables': {
                    'energy': {'source': 'dataframe', 'column': 'energy_used'},
                    'factor': {'source': 'dataframe', 'column': 'emission_factor'}
                }
            },
            {
                'indicator_id': 'IND03',
                'indicator_name': 'Test Indicator 03',
                'target_dataframe': 'df_product',
                'aggregation': 'average',
                'direction': 'maximize',
                'threshold': 0.7,
                'weight': 0.5,
                'category': 'environmental',
                'formula': 'quality * weight',
                'indicator_variables': {
                    'quality': {'source': 'dataframe', 'column': 'component_quality'},
                    'weight': {'source': 'dataframe', 'column': 'component_weight'}
                }
            }
        ]
    }


@pytest.fixture
def sample_values_config():
    """Sample values configuration for testing."""
    return {
        'values': [
            {
                'value_id': 'VAL01',
                'target_dataframe': 'df_process',
                'category': 'cost_factor',
                'formula': 'time * 2',
                'value_variables': {
                    'time': {'source': 'dataframe', 'column': 'processing_time'}
                }
            }
        ],
        'special_values': [
            {
                'value_name': 'REVENUE',
                'target_dataframe': 'df_process',
                'category': 'aggregate',
                'formula': 'value * quantity',
                'value_variables': {
                    'value': {'source': 'dataframe', 'column': 'component_value'},
                    'quantity': {'source': 'dataframe', 'column': 'quantity'}
                }
            }
        ]
    }


@pytest.fixture
def sample_df_process():
    """Sample process dataframe with 3 experiments, 2 components each."""
    return pd.DataFrame({
        'exp_id': ['exp001', 'exp001', 'exp002', 'exp002', 'exp003', 'exp003'],
        'step_name': ['comp_A', 'comp_B', 'comp_A', 'comp_B', 'comp_A', 'comp_B'],
        'processing_time': [10.0, 15.0, 12.0, 18.0, 8.0, 14.0],
        'station_cost': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        'energy_used': [20.0, 30.0, 25.0, 35.0, 15.0, 28.0],
        'emission_factor': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
        'component_value': [100.0, 150.0, 120.0, 140.0, 110.0, 160.0],
        'quantity': [1, 1, 1, 1, 1, 1]
    })


@pytest.fixture
def sample_df_product():
    """Sample product dataframe with 3 experiments, 2 products each."""
    return pd.DataFrame({
        'exp_id': ['exp001', 'exp001', 'exp002', 'exp002', 'exp003', 'exp003'],
        'product_id': ['prod_1', 'prod_2', 'prod_1', 'prod_2', 'prod_1', 'prod_2'],
        'component_quality': [0.9, 0.85, 0.75, 0.8, 0.95, 0.9],
        'component_weight': [2.0, 3.0, 2.0, 3.0, 2.0, 3.0]
    })


@pytest.fixture
def sample_df_resource():
    """Sample resource dataframe with 3 experiments, 2 stations each."""
    return pd.DataFrame({
        'exp_id': ['exp001', 'exp002', 'exp003'],
        'station_count': [2, 3, 2],
        'utilization': [0.8, 0.75, 0.85]
    })


@pytest.fixture
def sample_df_system():
    """Sample system dataframe with 3 experiments."""
    return pd.DataFrame({
        'exp_id': ['exp001', 'exp002', 'exp003'],
        'system_config': ['config_A', 'config_B', 'config_A'],
        'automation_level': [0, 3, 6]
    })


@pytest.fixture
def sample_doe():
    """Sample Design of Experiments table."""
    return pd.DataFrame({
        'exp_id': ['exp001', 'exp002', 'exp003'],
        'system_scenario': [1, 2, 1],
        'product_scenario': [1, 1, 2],
        'automation_level': [0, 3, 6],
        'description': ['Manual system', 'Semi-auto system', 'Full-auto system']
    })


@pytest.fixture
def sample_attributes():
    """Sample attribute tables for lookups."""
    return {
        'process': {
            'process_attributes': [
                {
                    'step_name': 'comp_A',
                    'disassembly_time': 10.0,
                    'cost_rates': {'running': {'power_rating': 2.0}}
                },
                {
                    'step_name': 'comp_B',
                    'disassembly_time': 15.0,
                    'cost_rates': {'running': {'power_rating': 3.0}}
                }
            ]
        },
        'systems': {
            'system_configurations': [
                {
                    'system_config': 'config_A',
                    'fixed_cost': 1000.0,
                    'maintenance_cost': 100.0
                },
                {
                    'system_config': 'config_B',
                    'fixed_cost': 1500.0,
                    'maintenance_cost': 150.0
                }
            ]
        },
        'product': {
            'components': [
                {
                    'component_name': 'comp_A',
                    'fixed_attributes': {'weight': {'value': 2.0}},
                    'quality_dependent_attributes': {
                        'component_value': [
                            {'quality_min': 0.0, 'quality_max': 0.5, 'value': 50.0},
                            {'quality_min': 0.5, 'quality_max': 1.0, 'value': 100.0}
                        ]
                    },
                    'end_of_life_options': {
                        'recycle': {
                            'quality_min': 0.0,
                            'quality_max': 0.6,
                            'circularity_rating': 0.5
                        },
                        'remanufacture': {
                            'quality_min': 0.6,
                            'quality_max': 1.0,
                            'circularity_rating': 0.9
                        }
                    }
                },
                {
                    'component_name': 'comp_B',
                    'fixed_attributes': {'weight': {'value': 3.0}},
                    'quality_dependent_attributes': {
                        'component_value': [
                            {'quality_min': 0.0, 'quality_max': 0.5, 'value': 75.0},
                            {'quality_min': 0.5, 'quality_max': 1.0, 'value': 150.0}
                        ]
                    },
                    'end_of_life_options': {
                        'recycle': {
                            'quality_min': 0.0,
                            'quality_max': 0.7,
                            'circularity_rating': 0.6
                        },
                        'remanufacture': {
                            'quality_min': 0.7,
                            'quality_max': 1.0,
                            'circularity_rating': 0.95
                        }
                    }
                }
            ]
        }
    }


@pytest.fixture
def sample_data_dict(sample_df_process, sample_df_product, sample_df_resource,
                     sample_df_system, sample_doe, sample_indicators_config,
                     sample_values_config, sample_attributes):
    """Complete data dictionary as returned by Module 0."""
    # Load the actual formatting config file
    config_path = Path(__file__).parent.parent / 'data' / 'config' / 'config_formatting.json'
    with open(config_path, 'r') as f:
        formatting_config = json.load(f)

    return {
        'df_process': sample_df_process.copy(),
        'df_product': sample_df_product.copy(),
        'df_resource': sample_df_resource.copy(),
        'df_system': sample_df_system.copy(),
        'doe': sample_doe.copy(),
        'indicators': sample_indicators_config,
        'values': sample_values_config,
        'attributes': sample_attributes,
        'formatting_config': formatting_config
    }


@pytest.fixture
def sample_df_experiments_aggregated():
    """Sample experiments dataframe after aggregation (Module 2 output)."""
    return pd.DataFrame({
        'exp_id': ['exp001', 'exp002', 'exp003'],
        'system_scenario': [1, 2, 1],
        'product_scenario': [1, 1, 2],
        'automation_level': [0, 3, 6],
        'IND01': [125.0, 150.0, 110.0],  # Sum of process level
        'IND02': [100.0, 120.0, 86.0],   # Sum of process level
        'IND03': [5.25, 4.65, 5.55]      # Average of product level
    })


@pytest.fixture
def sample_df_experiments_with_thresholds(sample_df_experiments_aggregated):
    """Sample experiments with threshold checks applied."""
    df = sample_df_experiments_aggregated.copy()
    df['IND01_in_threshold'] = df['IND01'] <= 1000  # minimize, threshold 1000
    df['IND02_in_threshold'] = df['IND02'] <= 500   # minimize, threshold 500
    df['IND03_in_threshold'] = df['IND03'] >= 0.7   # maximize, threshold 0.7
    df['threshold_violations'] = (~df[['IND01_in_threshold', 'IND02_in_threshold', 'IND03_in_threshold']]).sum(axis=1)
    df['is_feasible'] = df['threshold_violations'] == 0
    return df


@pytest.fixture
def sample_df_experiments_normalized(sample_df_experiments_with_thresholds):
    """Sample experiments with normalized values."""
    df = sample_df_experiments_with_thresholds.copy()
    # Simple normalization for testing
    df['IND01_normalized'] = [1.0, 0.0, 1.0]  # Lower is better
    df['IND02_normalized'] = [0.71, 0.0, 1.0]  # Lower is better
    df['IND03_normalized'] = [0.67, 0.0, 1.0]  # Higher is better
    return df


@pytest.fixture
def sample_df_experiments_ranked(sample_df_experiments_normalized, sample_indicators_config):
    """Sample experiments with weights applied and ranked."""
    df = sample_df_experiments_normalized.copy()

    # Apply weights
    df['IND01_weighted'] = df['IND01_normalized'] * 0.3
    df['IND02_weighted'] = df['IND02_normalized'] * 0.2
    df['IND03_weighted'] = df['IND03_normalized'] * 0.5

    # Calculate scores
    df['economic_score'] = df['IND01_weighted']
    df['environmental_score'] = df['IND02_weighted'] + df['IND03_weighted']
    df['total_weighted_score'] = df['IND01_weighted'] + df['IND02_weighted'] + df['IND03_weighted']

    # Add ranks
    df['rank_all'] = df['total_weighted_score'].rank(ascending=False, method='min').astype(int)
    df['rank'] = df.loc[df['is_feasible'], 'total_weighted_score'].rank(ascending=False, method='min')

    return df


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "dataframes").mkdir()
    (output_dir / "groups").mkdir()
    (output_dir / "visualizations").mkdir()
    (output_dir / "trajectories").mkdir()
    return output_dir
