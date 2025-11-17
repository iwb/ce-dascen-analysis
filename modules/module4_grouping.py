"""
Module 4: Group Statistics

PURPOSE:
- Calculate group-level statistics using original disaggregated indicator values
- Analyze performance across different factory configurations
- Support single variable and interaction groups
- Provide normalized values for cross-indicator comparison (spider charts)

INPUTS:
- data['df_process']: Component-level data with IND01, IND03, IND06, IND07
- data['df_product']: Product-level data with IND05
- data['df_resource']: Resource-level data with IND02
- data['df_system']: System-level data
- data['doe']: Design of Experiments table with grouping variables
- config_groups.json: Group definitions with indicator_analysis

OUTPUTS:
- data['df_groups']: Group statistics table
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# ====================
# CONSTANTS AND CONFIGURATION
# ====================
# Constants for configuration structure
CONFIG_DIR = Path(__file__).parent.parent / 'data/config'
CONFIG_FILE = 'config_groups.json'
OUTPUT_DIR = Path(__file__).parent.parent / 'output' / 'groups'

# Configuration keys
KEY_GROUPS = 'groups'
KEY_GROUP_ID = 'group_id'
KEY_GROUP_NAME = 'group_name'
KEY_INDICATOR_ANALYSIS = 'indicator_analysis'
KEY_GROUPING_VARIABLES = 'grouping_variables'
KEY_VARIABLE_TYPE = 'variable_type'
KEY_VARIABLE_NAME = 'variable_name'
KEY_COLUMN = 'column'
KEY_SOURCE_COLUMN = 'source_column'
KEY_MAPPING = 'mapping'
KEY_STATISTICS = 'statistics'

# Variable types
VAR_TYPE_DOE = 'doe_table'
VAR_TYPE_DERIVED = 'derived'

# Dataframe keys in data dictionary
DF_PROCESS = 'df_process'
DF_PRODUCT = 'df_product'
DF_RESOURCE = 'df_resource'
DF_SYSTEM = 'df_system'
DF_EXPERIMENTS = 'df_experiments'
DF_DOE = 'doe'

# Indicator lists in config
IND_PROCESS = 'process_indicators'
IND_PRODUCT = 'product_indicators'
IND_RESOURCE = 'resource_indicators'
IND_SYSTEM = 'system_indicators'
EXP_METRICS = 'experiment_metrics'

# Column names
COL_EXP_ID = 'exp_id'
COL_GROUP_ID = 'group_id'
COL_GROUP_NAME = 'group_name'
COL_GROUP_LEVEL = 'group_level'
COL_DATAFRAME = 'dataframe'
COL_INDICATOR_ID = 'indicator_id'
COL_N_EXPERIMENTS = 'n_experiments'
COL_N_OBSERVATIONS = 'n_observations'
COL_MEAN_NORMALIZED = 'mean_normalized'

# Statistics suffixes
STAT_MEAN = 'mean'
STAT_STD = 'std'
STAT_MIN = 'min'
STAT_MAX = 'max'
STAT_COUNT = 'count'
STAT_MEAN_NORMALIZED = 'mean_normalized'

# Default statistics
DEFAULT_STATISTICS = [STAT_MEAN, STAT_STD, STAT_MIN, STAT_MAX]

# Numeric precision
ROUND_PRECISION = 2

# Normalization constants
NORMALIZED_DEFAULT = 0.5  # Default when all values are identical
NORMALIZED_EPSILON = 1e-10  # For numeric stability

# Output file patterns
FILE_ALL_GROUPS = 'M4_01_df_groups_all.csv'
FILE_GROUP_PATTERN = 'M4_{idx:02d}_df_groups_{group_id}.csv'
FILE_START_INDEX = 2  # Per-group files start at M4_02


# ====================
# 1. HELPER FUNCTIONS FOR GROUPING VARIABLES
# ====================

def extract_group_vars(df, group_config):
    """
    Extract list of grouping variable column names that exist in dataframe.

    Args:
        df: DataFrame to check columns against
        group_config: Group configuration dict

    Returns:
        list: Column names for grouping
    """
    group_vars = []
    for var in group_config[KEY_GROUPING_VARIABLES]:
        if var[KEY_VARIABLE_TYPE] == VAR_TYPE_DOE:
            if var[KEY_COLUMN] in df.columns:
                group_vars.append(var[KEY_COLUMN])
            else:
                print(f"  [WARNING] Grouping column '{var[KEY_COLUMN]}' not found in dataframe")
        elif var[KEY_VARIABLE_TYPE] == VAR_TYPE_DERIVED:
            if var[KEY_VARIABLE_NAME] in df.columns:
                group_vars.append(var[KEY_VARIABLE_NAME])
            else:
                print(f"  [WARNING] Derived variable '{var[KEY_VARIABLE_NAME]}' not found in dataframe")
    return group_vars


def create_group_level_string(row, group_vars):
    """
    Create group level identifier string from row values.

    Args:
        row: DataFrame row
        group_vars: List of grouping variable column names

    Returns:
        str: Group level identifier
    """
    if len(group_vars) == 1:
        return str(row[group_vars[0]])
    else:
        return '_'.join([str(row[col]) for col in group_vars])


def create_result_dict(group_id, group_name, group_level, dataframe_name,
                       indicator_id, row, group_vars, n_experiments):
    """
    Create standardized result dictionary from statistics row.

    Args:
        group_id: Group identifier
        group_name: Group name
        group_level: Group level identifier
        dataframe_name: Source dataframe name
        indicator_id: Indicator/metric identifier
        row: Statistics row
        group_vars: List of grouping variable column names
        n_experiments: Number of experiments

    Returns:
        dict: Standardized result dictionary
    """
    result_dict = {
        COL_GROUP_ID: group_id,
        COL_GROUP_NAME: group_name,
        COL_GROUP_LEVEL: group_level,
        COL_DATAFRAME: dataframe_name,
        COL_INDICATOR_ID: indicator_id,
        STAT_MEAN: row.get(f'{indicator_id}_{STAT_MEAN}', np.nan),
        STAT_STD: row.get(f'{indicator_id}_{STAT_STD}', np.nan),
        STAT_MIN: row.get(f'{indicator_id}_{STAT_MIN}', np.nan),
        STAT_MAX: row.get(f'{indicator_id}_{STAT_MAX}', np.nan),
        COL_N_OBSERVATIONS: row.get(f'{indicator_id}_{STAT_COUNT}', 0),
        COL_N_EXPERIMENTS: int(n_experiments) if not pd.isna(n_experiments) else 0
    }

    # Add individual grouping variables
    for gv in group_vars:
        result_dict[gv] = row[gv]

    return result_dict


def add_grouping_variables(df, doe, group_config):
    """
    Join dataframe with DoE to add grouping variables.

    Args:
        df: Process/product/resource/system dataframe with exp_id
        doe: Design of Experiments table
        group_config: Group configuration dict

    Returns:
        pd.DataFrame: df with grouping variables added
    """
    try:
        # Validate inputs
        if df is None or df.empty:
            print("  [WARNING] Empty dataframe provided to add_grouping_variables")
            return df

        if doe is None or doe.empty:
            print("  [WARNING] Empty DoE table, cannot add grouping variables")
            return df

        # Extract column names needed for grouping
        grouping_cols = []
        for var in group_config[KEY_GROUPING_VARIABLES]:
            if var[KEY_VARIABLE_TYPE] == VAR_TYPE_DOE:
                if KEY_COLUMN in var:
                    grouping_cols.append(var[KEY_COLUMN])
            elif var[KEY_VARIABLE_TYPE] == VAR_TYPE_DERIVED:
                # Also add source_column for derived variables
                source_col = var.get(KEY_SOURCE_COLUMN)
                if source_col:
                    grouping_cols.append(source_col)

        # Filter to only columns that don't already exist in df
        cols_to_add = [col for col in grouping_cols if col not in df.columns]

        # Merge with DoE to get grouping variables (only if needed)
        if cols_to_add:
            # Validate exp_id exists in both dataframes
            if COL_EXP_ID not in df.columns:
                print(f"  [ERROR] Column '{COL_EXP_ID}' not found in dataframe")
                return df
            if COL_EXP_ID not in doe.columns:
                print(f"  [ERROR] Column '{COL_EXP_ID}' not found in DoE table")
                return df

            df_with_groups = df.merge(
                doe[[COL_EXP_ID] + cols_to_add],
                on=COL_EXP_ID,
                how='left'
            )

            # Check for merge issues
            if df_with_groups.empty:
                print("  [WARNING] Merge resulted in empty dataframe")
                return df
        else:
            df_with_groups = df.copy()

        return df_with_groups

    except Exception as e:
        print(f"  [ERROR] Failed to add grouping variables: {e}")
        return df


def apply_derived_mappings(df, group_config):
    """
    Apply derived variable mappings (continuous → categorical or categorical → simplified).

    Args:
        df: Dataframe with grouping variables
        group_config: Group configuration dict

    Returns:
        pd.DataFrame: df with derived variable columns added
        list: Names of derived columns created
    """
    derived_cols = []

    try:
        if df is None or df.empty:
            return df, derived_cols

        for var in group_config[KEY_GROUPING_VARIABLES]:
            if var[KEY_VARIABLE_TYPE] == VAR_TYPE_DERIVED:
                var_name = var.get(KEY_VARIABLE_NAME)
                if not var_name:
                    print(f"  [WARNING] Derived variable missing '{KEY_VARIABLE_NAME}' key, skipping")
                    continue

                derived_cols.append(var_name)

                # Get source column from config
                source_col = var.get(KEY_SOURCE_COLUMN)
                if not source_col:
                    print(f"  [WARNING] Derived variable '{var_name}' missing '{KEY_SOURCE_COLUMN}' in config, skipping")
                    continue

                # Check if source column exists
                if source_col not in df.columns:
                    print(f"  [WARNING] Source column '{source_col}' not found for derived variable '{var_name}', skipping")
                    continue

                # Initialize derived column
                df[var_name] = None

                # Apply mapping
                if KEY_MAPPING in var:
                    mapping = var[KEY_MAPPING]

                    # Apply mapping for each level
                    for level, values in mapping.items():
                        if isinstance(values, list):
                            # Values is a list - check if source values are in this list
                            df.loc[df[source_col].isin(values), var_name] = level

                # Check for unmapped values
                unmapped_count = df[var_name].isna().sum()
                if unmapped_count > 0:
                    unique_unmapped = df[df[var_name].isna()][source_col].nunique()
                    print(f"  [WARNING] {unmapped_count} rows have unmapped values for '{var_name}' ({unique_unmapped} unique values)")

    except Exception as e:
        print(f"  [ERROR] Failed to apply derived mappings: {e}")

    return df, derived_cols


# ====================
# 2. STATISTICS CALCULATION
# ====================

def calculate_group_statistics(df, group_vars, indicator_cols):
    """
    Calculate mean, std, min, max for indicators by group.

    Args:
        df: Dataframe with grouping variables and indicators
        group_vars: List of column names to group by
        indicator_cols: List of indicator column names

    Returns:
        pd.DataFrame: Statistics table
    """
    try:
        # Validate inputs
        if df is None or df.empty:
            print("  [WARNING] Empty dataframe for group statistics calculation")
            return pd.DataFrame()

        if not group_vars:
            print("  [WARNING] No grouping variables specified")
            return pd.DataFrame()

        if not indicator_cols:
            print("  [WARNING] No indicator columns specified")
            return pd.DataFrame()

        # Check if grouping variables exist
        missing_vars = [var for var in group_vars if var not in df.columns]
        if missing_vars:
            print(f"  [WARNING] Grouping variables not found: {missing_vars}")
            group_vars = [var for var in group_vars if var in df.columns]
            if not group_vars:
                return pd.DataFrame()

        # Check if indicator columns exist
        missing_indicators = [ind for ind in indicator_cols if ind not in df.columns]
        if missing_indicators:
            print(f"  [WARNING] Indicator columns not found: {missing_indicators}")
            indicator_cols = [ind for ind in indicator_cols if ind in df.columns]
            if not indicator_cols:
                return pd.DataFrame()

        # Group and calculate statistics
        stats = df.groupby(group_vars)[indicator_cols].agg([STAT_MEAN, STAT_STD, STAT_MIN, STAT_MAX, STAT_COUNT])

        # Flatten column names
        stats.columns = ['_'.join(col).strip() for col in stats.columns.values]

        # Reset index to make group vars regular columns
        stats = stats.reset_index()

        # Count unique experiments per group
        if COL_EXP_ID in df.columns:
            exp_counts = df.groupby(group_vars)[COL_EXP_ID].nunique().reset_index()
            exp_counts.columns = group_vars + [COL_N_EXPERIMENTS]

            # Merge experiment counts
            stats = stats.merge(exp_counts, on=group_vars, how='left')
        else:
            print(f"  [WARNING] Column '{COL_EXP_ID}' not found, cannot count experiments per group")
            stats[COL_N_EXPERIMENTS] = 0

        return stats

    except Exception as e:
        print(f"  [ERROR] Failed to calculate group statistics: {e}")
        return pd.DataFrame()


def normalize_group_statistics(df_groups, groups_config):
    """
    Normalize mean values per indicator (0-1 scale) for groups that request it.
    Normalization is PER INDICATOR across ALL group levels globally.

    This enables spider/radar charts where different indicators need to be
    displayed on the same 0-1 scale for visual comparison.

    Args:
        df_groups: Dataframe with group statistics
        groups_config: Full groups configuration dict

    Returns:
        pd.DataFrame: df_groups with mean_normalized column added
    """
    try:
        # Validate inputs
        if df_groups is None or df_groups.empty:
            return df_groups

        if not groups_config or KEY_GROUPS not in groups_config:
            print("  [WARNING] Invalid groups configuration for normalization")
            return df_groups

        # Identify which groups request normalization
        groups_with_normalization = set()
        for group_config in groups_config[KEY_GROUPS]:
            stats = group_config.get(KEY_INDICATOR_ANALYSIS, {}).get(KEY_STATISTICS, DEFAULT_STATISTICS)
            if STAT_MEAN_NORMALIZED in stats:
                groups_with_normalization.add(group_config[KEY_GROUP_ID])

        if not groups_with_normalization:
            # No groups need normalization
            return df_groups

        # Initialize column
        df_groups[COL_MEAN_NORMALIZED] = np.nan

        # Normalize PER INDICATOR across ALL groups globally
        # Example: All IND01 values are normalized together using IND01's global min/max
        for indicator_id in df_groups[COL_INDICATOR_ID].unique():
            mask_indicator = df_groups[COL_INDICATOR_ID] == indicator_id
            values = df_groups.loc[mask_indicator, STAT_MEAN]

            if not values.isna().all():
                # Calculate global min/max for this indicator
                min_val = values.min()
                max_val = values.max()

                if abs(max_val - min_val) > NORMALIZED_EPSILON:
                    # Apply normalization only to groups that requested it
                    for group_id in groups_with_normalization:
                        mask_group = mask_indicator & (df_groups[COL_GROUP_ID] == group_id)
                        if mask_group.any():
                            df_groups.loc[mask_group, COL_MEAN_NORMALIZED] = (
                                (df_groups.loc[mask_group, STAT_MEAN] - min_val) / (max_val - min_val)
                            )
                else:
                    # All values identical, set to default (middle of 0-1 range)
                    print(f"  [INFO] All values for indicator '{indicator_id}' are identical ({min_val:.2f}), setting normalized to {NORMALIZED_DEFAULT}")
                    for group_id in groups_with_normalization:
                        mask_group = mask_indicator & (df_groups[COL_GROUP_ID] == group_id)
                        if mask_group.any():
                            df_groups.loc[mask_group, COL_MEAN_NORMALIZED] = NORMALIZED_DEFAULT

    except Exception as e:
        print(f"  [ERROR] Failed to normalize group statistics: {e}")

    return df_groups


# ====================
# 3. GROUP PROCESSING
# ====================

def process_single_group(data, group_config):
    """
    Process a single group definition and calculate statistics.

    Args:
        data: Data dictionary with all dataframes
        group_config: Single group configuration dict

    Returns:
        list: List of statistics dictionaries
    """
    try:
        # Extract group metadata
        group_id = group_config.get(KEY_GROUP_ID)
        group_name = group_config.get(KEY_GROUP_NAME)
        indicator_analysis = group_config.get(KEY_INDICATOR_ANALYSIS, {})

        if not group_id:
            print("  [ERROR] Group configuration missing 'group_id'")
            return []

        results = []

        # Map dataframe types to indicator lists
        df_indicator_map = {
            DF_PROCESS: indicator_analysis.get(IND_PROCESS, []),
            DF_PRODUCT: indicator_analysis.get(IND_PRODUCT, []),
            DF_RESOURCE: indicator_analysis.get(IND_RESOURCE, []),
            DF_SYSTEM: indicator_analysis.get(IND_SYSTEM, [])
        }

        # Process experiment-level metrics (like rank, total_weighted_score)
        experiment_metrics = indicator_analysis.get(EXP_METRICS, [])
        if experiment_metrics and DF_EXPERIMENTS in data:
            df = data[DF_EXPERIMENTS].copy()

            # Add grouping variables from DoE (if not already present)
            df = add_grouping_variables(df, data[DF_DOE], group_config)

            # Apply derived mappings
            df, derived_cols = apply_derived_mappings(df, group_config)

            # Determine grouping columns using helper function
            group_vars = extract_group_vars(df, group_config)

            if group_vars:
                # Filter to only include metrics present in dataframe
                available_metrics = [metric for metric in experiment_metrics if metric in df.columns]

                if available_metrics:
                    # Calculate statistics
                    stats = calculate_group_statistics(df, group_vars, available_metrics)

                    if not stats.empty:
                        # Reshape to long format
                        for idx, row in stats.iterrows():
                            # Extract group level using helper function
                            group_level = create_group_level_string(row, group_vars)
                            n_experiments = row.get(COL_N_EXPERIMENTS, 0)

                            # Extract statistics for each metric
                            for metric_id in available_metrics:
                                result_dict = create_result_dict(
                                    group_id, group_name, group_level,
                                    DF_EXPERIMENTS, metric_id,
                                    row, group_vars, n_experiments
                                )
                                results.append(result_dict)

        # Process each dataframe type
        for df_name, indicator_list in df_indicator_map.items():
            if not indicator_list:
                continue

            if df_name not in data:
                print(f"  [WARNING] Dataframe '{df_name}' not found in data dictionary")
                continue

            df = data[df_name].copy()

            if df.empty:
                print(f"  [WARNING] Dataframe '{df_name}' is empty, skipping")
                continue

            # Add grouping variables from DoE
            df = add_grouping_variables(df, data[DF_DOE], group_config)

            # Apply derived mappings
            df, derived_cols = apply_derived_mappings(df, group_config)

            # Determine grouping columns using helper function
            group_vars = extract_group_vars(df, group_config)

            if not group_vars:
                continue

            # Filter to only include indicators present in dataframe
            available_indicators = [ind for ind in indicator_list if ind in df.columns]

            if not available_indicators:
                continue

            # Check if all grouping vars have non-null values
            # Skip if derived variables are all null
            has_data = True
            for gv in group_vars:
                if df[gv].isna().all():
                    has_data = False
                    print(f"  [INFO] Grouping variable '{gv}' has all NaN values in {df_name}, skipping")
                    break

            if not has_data:
                continue

            # Check for partial NaN values
            for gv in group_vars:
                nan_count = df[gv].isna().sum()
                if nan_count > 0 and nan_count < len(df):
                    print(f"  [WARNING] Grouping variable '{gv}' has {nan_count} NaN values in {df_name}")

            # Calculate statistics
            stats = calculate_group_statistics(df, group_vars, available_indicators)

            if not stats.empty:
                # Reshape to long format
                for idx, row in stats.iterrows():
                    # Extract group level using helper function
                    group_level = create_group_level_string(row, group_vars)
                    n_experiments = row.get(COL_N_EXPERIMENTS, 0)

                    # Extract statistics for each indicator
                    for ind_id in available_indicators:
                        result_dict = create_result_dict(
                            group_id, group_name, group_level,
                            df_name, ind_id,
                            row, group_vars, n_experiments
                        )
                        results.append(result_dict)

        return results

    except Exception as e:
        print(f"  [ERROR] Failed to process group '{group_id}': {e}")
        return []


# ====================
# 4. MAIN MODULE ORCHESTRATION
# ====================

def run_module4(data, save_output=False):
    """
    Main Module 4 orchestration function.

    Args:
        data: Dictionary with dataframes from previous modules
        save_output: If True, save debug output files

    Returns:
        dict: Updated data dictionary with df_groups added
    """
    print("[Module 4] Calculating group statistics...")

    # ====================
    # Load configuration
    # ====================
    try:
        config_path = CONFIG_DIR / CONFIG_FILE
        if not config_path.exists():
            print(f"  [ERROR] Configuration file not found: {config_path}")
            data['df_groups'] = pd.DataFrame()
            return data

        with open(config_path, 'r') as f:
            groups_config = json.load(f)

        if KEY_GROUPS not in groups_config:
            print(f"  [ERROR] Configuration missing '{KEY_GROUPS}' key")
            data['df_groups'] = pd.DataFrame()
            return data

    except json.JSONDecodeError as e:
        print(f"  [ERROR] Failed to parse configuration file: {e}")
        data['df_groups'] = pd.DataFrame()
        return data
    except Exception as e:
        print(f"  [ERROR] Failed to load configuration: {e}")
        data['df_groups'] = pd.DataFrame()
        return data

    # ====================
    # Process groups
    # ====================
    all_results = []

    for group_config in groups_config[KEY_GROUPS]:
        group_id = group_config.get(KEY_GROUP_ID, 'unknown')
        print(f"  Processing {group_id}...")

        try:
            group_results = process_single_group(data, group_config)
            all_results.extend(group_results)
        except Exception as e:
            print(f"  [ERROR] Failed to process group '{group_id}': {e}")
            continue

    # ====================
    # Create dataframe
    # ====================
    if not all_results:
        print("  [WARNING] No group statistics calculated")
        data['df_groups'] = pd.DataFrame()
        return data

    df_groups = pd.DataFrame(all_results)

    # ====================
    # Normalize and format data
    # ====================
    # Apply normalization for groups that request it
    df_groups = normalize_group_statistics(df_groups, groups_config)

    # Round numeric columns (including mean_normalized if present)
    numeric_cols = [STAT_MEAN, STAT_STD, STAT_MIN, STAT_MAX]
    if COL_MEAN_NORMALIZED in df_groups.columns:
        numeric_cols.append(COL_MEAN_NORMALIZED)

    # Round and convert to float64 (this handles nullable types properly)
    for col in numeric_cols:
        if col in df_groups.columns:
            df_groups[col] = pd.to_numeric(df_groups[col], errors='coerce').round(ROUND_PRECISION)

    # Sort by group_id, group_level, then indicator_id
    # This ensures all indicators for one group_level are together
    df_groups = df_groups.sort_values(
        by=[COL_GROUP_ID, COL_GROUP_LEVEL, COL_INDICATOR_ID],
        ascending=[True, True, True]
    ).reset_index(drop=True)

    # Store in data dictionary
    data['df_groups'] = df_groups

    print(f"  [OK] Calculated statistics for {len(df_groups)} group-indicator combinations")

    # ====================
    # Summary statistics
    # ====================
    print(f"\n  Group Summary:")
    print(f"    Total groups: {df_groups[COL_GROUP_ID].nunique()}")
    print(f"    Total group levels: {df_groups[COL_GROUP_LEVEL].nunique()}")
    print(f"    Total indicators analyzed: {df_groups[COL_INDICATOR_ID].nunique()}")
    print(f"    Total combinations: {len(df_groups)}")

    # ====================
    # Save output files (optional)
    # ====================
    if save_output:
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            # Save complete groups table
            output_file = OUTPUT_DIR / FILE_ALL_GROUPS
            df_groups.to_csv(output_file, index=False)
            print(f"\n  [OK] Saved: {FILE_ALL_GROUPS} ({len(df_groups)} rows)")

            # Save per-group files with sequential numbering
            for idx, group_id in enumerate(sorted(df_groups[COL_GROUP_ID].unique()), start=FILE_START_INDEX):
                df_group = df_groups[df_groups[COL_GROUP_ID] == group_id]
                file_name = FILE_GROUP_PATTERN.format(idx=idx, group_id=group_id)
                df_group.to_csv(OUTPUT_DIR / file_name, index=False)
                print(f"  [OK] Saved: {file_name} ({len(df_group)} rows)")

        except Exception as e:
            print(f"  [ERROR] Failed to save output files: {e}")

    return data


# ====================
# 5. STANDALONE TESTING
# ====================


if __name__ == '__main__':
    # Test Module 4 standalone
    from module0_data_loader import load_all_data
    from module1_step_indicators import calculate_indicators
    from module2_experiment_aggregation import run_module2
    from module3_ranking import run_module3

    data = load_all_data()
    data = calculate_indicators(data, save_output=False)
    data = run_module2(data, save_output=False)
    data = run_module3(data, save_output=False)
    data = run_module4(data, save_output=True)

    print("\nModule 4 test complete!")
