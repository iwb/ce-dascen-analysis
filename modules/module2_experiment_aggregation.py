"""
Module 2: Experiment Aggregation, Filtering, and Normalization

PURPOSE:
- Aggregate component/product/resource indicators to experiment level
- Apply threshold filtering to identify feasible experiments
- Normalize indicators for downstream ranking

INPUTS:
- data['df_process']: Component-level data with IND01, IND03, IND06, IND07
- data['df_product']: Product-level data with IND05
- data['df_resource']: Station-level data with IND02
- data['df_system']: System-level data
- data['doe']: Design of Experiments table with metadata
- data['indicators']: Config with aggregation rules and thresholds

OUTPUTS:
- data['df_experiments']: Master experiment table with:
  * Experiment metadata
  * Aggregated indicator values
  * Threshold compliance flags
  * Normalized indicator values
"""

import pandas as pd
import numpy as np
from pathlib import Path
# ====================
# CONSTANTS AND CONFIGURATION
# ====================

# Directory paths
DEFAULT_OUTPUT_DIR = 'output'
DATAFRAMES_SUBDIR = 'dataframes'

# Column names
EXP_ID_COLUMN = 'exp_id'
IS_FEASIBLE_COLUMN = 'is_feasible'

# Column suffixes
THRESHOLD_SUFFIX = '_in_threshold'
NORMALIZED_SUFFIX = '_normalized'

# Aggregation methods
AGG_SUM = 'sum'
AGG_AVERAGE = 'average'
AGG_MAX = 'max'
AGG_MIN = 'min'

# Indicator config keys
IND_INDICATOR_ID = 'indicator_id'
IND_TARGET_DATAFRAME = 'target_dataframe'
IND_AGGREGATION = 'aggregation'
IND_THRESHOLD = 'threshold'
IND_THRESHOLD_MIN = 'threshold_min'
IND_THRESHOLD_MAX = 'threshold_max'
IND_NORMALIZATION = 'normalization'
IND_IS_FEASIBILITY_CHECK = 'is_feasibility_check'

# Normalization methods
NORM_HIGHER_BETTER = 'higher_better'
NORM_LOWER_BETTER = 'lower_better'
NORM_RANGE = 'range'

# Data dictionary keys
KEY_DOE = 'doe'
KEY_INDICATORS = 'indicators'
KEY_DF_PROCESS = 'df_process'
KEY_DF_PRODUCT = 'df_product'
KEY_DF_RESOURCE = 'df_resource'
KEY_DF_SYSTEM = 'df_system'
KEY_DF_EXPERIMENTS = 'df_experiments'

# Numeric precision
AGGREGATION_PRECISION = 2

# Default values
DEFAULT_NORMALIZED_VALUE = 0

# Output filenames (Module 2)
MODULE2_PREFIX = 'M2_'
DF_EXPERIMENTS_AGGREGATED_OUTPUT = 'M2_01_df_experiments_aggregated.csv'
DF_EXPERIMENTS_FEASIBLE_OUTPUT = 'M2_02_df_experiments_feasible.csv'

# Messages
MSG_WARNING_PREFIX = "[WARNING]"
MSG_ERROR_PREFIX = "[ERROR]"
MSG_OK_PREFIX = "[OK]"

def aggregate_to_experiment_level(data):
    """
    Aggregate indicators from component/product/resource level to experiment level.

    Args:
        data: Dictionary with dataframes from Modules 0 and 1

    Returns:
        pd.DataFrame: df_experiments with metadata + aggregated indicators
    """
    # ====================
    # 1. Initialize experiment table and filter to available data
    # ====================
    try:
        # Validate required keys exist in data
        if KEY_DOE not in data or data[KEY_DOE] is None or data[KEY_DOE].empty:
            raise ValueError("Design of Experiments (DoE) table is missing or empty")

        if KEY_DF_PROCESS not in data or data[KEY_DF_PROCESS] is None or data[KEY_DF_PROCESS].empty:
            raise ValueError("df_process is missing or empty - cannot determine available experiments")

        if KEY_INDICATORS not in data or KEY_INDICATORS not in data[KEY_INDICATORS]:
            raise ValueError("Indicators configuration is missing or malformed")

        # Start with DoE table to get all experiment metadata
        df_experiments = data[KEY_DOE].copy()

        # Get list of experiment IDs that have data
        available_exp_ids = data[KEY_DF_PROCESS][EXP_ID_COLUMN].unique()
        if len(available_exp_ids) == 0:
            print(f"  {MSG_WARNING_PREFIX} No experiments found in df_process, returning empty dataframe")
            return pd.DataFrame()

        df_experiments = df_experiments[df_experiments[EXP_ID_COLUMN].isin(available_exp_ids)]

        if df_experiments.empty:
            print(f"  {MSG_WARNING_PREFIX} No matching experiments between DoE and processed data")
            return pd.DataFrame()

    except KeyError as e:
        raise KeyError(f"Missing required data key: {e}")
    except Exception as e:
        raise RuntimeError(f"Error initializing experiment table: {e}")

    # ====================
    # 2. Aggregate each indicator based on configuration
    # ====================
    indicators = data[KEY_INDICATORS][KEY_INDICATORS]
    missing_indicators = []

    for indicator in indicators:
        try:
            ind_id = indicator[IND_INDICATOR_ID]
            target_df_name = indicator[IND_TARGET_DATAFRAME]
            agg_method = indicator[IND_AGGREGATION]

            # Validate target dataframe exists
            if target_df_name not in data:
                print(f"  {MSG_WARNING_PREFIX} Target dataframe '{target_df_name}' not found for {ind_id}, skipping")
                missing_indicators.append(ind_id)
                continue

            target_df = data[target_df_name]

            # Validate indicator column exists in target dataframe
            if ind_id not in target_df.columns:
                print(f"  {MSG_WARNING_PREFIX} Indicator '{ind_id}' not found in {target_df_name}, skipping")
                missing_indicators.append(ind_id)
                continue

            # Perform aggregation based on method
            if agg_method == AGG_SUM:
                aggregated = target_df.groupby(EXP_ID_COLUMN)[ind_id].sum()
            elif agg_method == AGG_AVERAGE or agg_method == 'mean':  # Handle both 'average' and 'mean'
                aggregated = target_df.groupby(EXP_ID_COLUMN)[ind_id].mean()
            else:  # no aggregation needed - already at experiment level
                aggregated = target_df.set_index(EXP_ID_COLUMN)[ind_id]

            # Merge into df_experiments
            df_experiments = df_experiments.merge(
                aggregated.rename(ind_id).to_frame(),
                left_on=EXP_ID_COLUMN,
                right_index=True,
                how='left'
            )

            # Fill NaN values from merge with 0 and warn
            if df_experiments[ind_id].isna().any():
                nan_count = df_experiments[ind_id].isna().sum()
                print(f"  {MSG_WARNING_PREFIX} {nan_count} experiments have no data for {ind_id}, filling with 0")
                df_experiments[ind_id] = df_experiments[ind_id].fillna(0)

        except KeyError as e:
            print(f"  {MSG_ERROR_PREFIX} Missing required config key for indicator: {e}")
            missing_indicators.append(indicator.get(IND_INDICATOR_ID, 'unknown'))
        except Exception as e:
            print(f"  {MSG_ERROR_PREFIX} Failed to aggregate {indicator.get(IND_INDICATOR_ID, 'unknown')}: {e}")
            missing_indicators.append(indicator.get(IND_INDICATOR_ID, 'unknown'))

    # ====================
    # 3. Round aggregated values for readability
    # ====================
    # Only round columns that were successfully aggregated
    indicator_cols = [ind[IND_INDICATOR_ID] for ind in indicators if ind[IND_INDICATOR_ID] not in missing_indicators]
    if indicator_cols:
        df_experiments[indicator_cols] = df_experiments[indicator_cols].round(AGGREGATION_PRECISION)
    else:
        print(f"  {MSG_WARNING_PREFIX} No indicators were successfully aggregated")

    return df_experiments


def apply_threshold_filters(df_experiments, indicators_config):
    """
    Check each indicator against single threshold value and flag violations.

    For minimize: threshold = max acceptable value (should be <=)
    For maximize: threshold = min acceptable value (should be >=)

    Args:
        df_experiments: DataFrame with aggregated indicators
        indicators_config: Config dictionary with indicator definitions

    Returns:
        pd.DataFrame: df_experiments with threshold check columns added
    """
    # ====================
    # 1. Evaluate threshold compliance for each indicator
    # ====================
    try:
        # Validate inputs
        if df_experiments is None or df_experiments.empty:
            print(f"  {MSG_WARNING_PREFIX} Empty experiments dataframe, skipping threshold filtering")
            return df_experiments

        if KEY_INDICATORS not in indicators_config:
            raise ValueError(f"Indicators configuration missing '{KEY_INDICATORS}' key")

        indicators = indicators_config[KEY_INDICATORS]
        threshold_cols = []
        skipped_indicators = []

        for indicator in indicators:
            try:
                # Extract required fields
                ind_id = indicator[IND_INDICATOR_ID]
                threshold = indicator[IND_THRESHOLD]
                direction = indicator['direction']

                # Validate indicator column exists
                if ind_id not in df_experiments.columns:
                    print(f"  {MSG_WARNING_PREFIX} Indicator '{ind_id}' not found in dataframe, skipping threshold check")
                    skipped_indicators.append(ind_id)
                    continue

                col_name = f'{ind_id}{THRESHOLD_SUFFIX}'

                # Apply threshold based on direction
                if direction == 'minimize':
                    # For minimize: value should be <= threshold (max acceptable)
                    df_experiments[col_name] = df_experiments[ind_id] <= threshold
                elif direction == 'maximize':
                    # For maximize: value should be >= threshold (min acceptable)
                    df_experiments[col_name] = df_experiments[ind_id] >= threshold
                else:
                    print(f"  [WARNING] Unknown direction '{direction}' for {ind_id}, defaulting to minimize")
                    df_experiments[col_name] = df_experiments[ind_id] <= threshold

                threshold_cols.append(col_name)

            except KeyError as e:
                print(f"  [ERROR] Missing required key for indicator {indicator.get('indicator_id', 'unknown')}: {e}")
                skipped_indicators.append(indicator.get('indicator_id', 'unknown'))
            except Exception as e:
                print(f"  [ERROR] Failed to apply threshold for {indicator.get('indicator_id', 'unknown')}: {e}")
                skipped_indicators.append(indicator.get('indicator_id', 'unknown'))

    except Exception as e:
        raise RuntimeError(f"Error in threshold filtering setup: {e}")

    # ====================
    # 2. Calculate overall feasibility metrics
    # ====================
    if threshold_cols:
        # Count violations (number of False values)
        df_experiments['threshold_violations'] = (~df_experiments[threshold_cols]).sum(axis=1)

        # Mark feasibility
        df_experiments['is_feasible'] = df_experiments['threshold_violations'] == 0
    else:
        print("  [WARNING] No threshold checks were applied, marking all experiments as feasible")
        df_experiments['threshold_violations'] = 0
        df_experiments['is_feasible'] = True

    return df_experiments


def normalize_indicators(df_experiments, indicators_config):
    """
    Normalize all indicators based on ALL experiments (not just feasible).

    Uses ALL experiments to determine bounds. Worst value is capped at threshold
    to allow negative normalized values for threshold violations.

    Args:
        df_experiments: DataFrame with indicators and feasibility flags
        indicators_config: Config dictionary with indicator definitions

    Returns:
        pd.DataFrame: df_experiments with normalized columns added
    """
    # ====================
    # 1. Determine normalization bounds from all experiments
    # ====================
    try:
        # Validate inputs
        if df_experiments is None or df_experiments.empty:
            print("  [WARNING] Empty experiments dataframe, skipping normalization")
            return df_experiments

        if 'indicators' not in indicators_config:
            raise ValueError("Indicators configuration missing 'indicators' key")

        indicators = indicators_config['indicators']
        skipped_indicators = []

        # Normalize each indicator using ALL experiments
        for indicator in indicators:
            try:
                ind_id = indicator['indicator_id']
                direction = indicator['direction']
                threshold = indicator['threshold']

                # Validate indicator column exists
                if ind_id not in df_experiments.columns:
                    print(f"  [WARNING] Indicator '{ind_id}' not found in dataframe, skipping normalization")
                    skipped_indicators.append(ind_id)
                    continue

                # Get best and worst values from ALL experiments
                best_value = df_experiments[ind_id].max() if direction == 'maximize' else df_experiments[ind_id].min()
                worst_value_raw = df_experiments[ind_id].min() if direction == 'maximize' else df_experiments[ind_id].max()

                # Adjust worst value based on threshold
                # This allows negative normalized values for threshold violations
                if direction == 'minimize':
                    # For minimize: worst should not exceed threshold
                    worst_value = min(worst_value_raw, threshold)
                else:  # maximize
                    # For maximize: worst should not fall below threshold
                    worst_value = max(worst_value_raw, threshold)

                # ====================
                # 2. Normalize values with direction-aware scaling
                # ====================
                # Handle edge case: all values are identical
                if abs(best_value - worst_value) < 1e-10:  # Using epsilon for numeric stability
                    print(f"  [WARNING] All values for {ind_id} are identical ({best_value}), setting normalized to 1.0")
                    df_experiments[f'{ind_id}_normalized'] = 1.0
                    continue

                # Normalize based on direction
                if direction == 'minimize':
                    # Lower values are better → higher normalized scores
                    # Formula: (worst - value) / (worst - best)
                    df_experiments[f'{ind_id}_normalized'] = (
                        (worst_value - df_experiments[ind_id]) / (worst_value - best_value)
                    )
                elif direction == 'maximize':
                    # Higher values are better → higher normalized scores
                    # Formula: (value - worst) / (best - worst)
                    df_experiments[f'{ind_id}_normalized'] = (
                        (df_experiments[ind_id] - worst_value) / (best_value - worst_value)
                    )
                else:
                    print(f"  [WARNING] Unknown direction '{direction}' for {ind_id}, defaulting to minimize")
                    df_experiments[f'{ind_id}_normalized'] = (
                        (worst_value - df_experiments[ind_id]) / (worst_value - best_value)
                    )

                # Round to 2 decimal places
                df_experiments[f'{ind_id}_normalized'] = df_experiments[f'{ind_id}_normalized'].round(2)

                # Check for any inf or -inf values
                if df_experiments[f'{ind_id}_normalized'].isin([np.inf, -np.inf]).any():
                    print(f"  [WARNING] Infinite values detected in {ind_id}_normalized, replacing with 0")
                    df_experiments[f'{ind_id}_normalized'] = df_experiments[f'{ind_id}_normalized'].replace([np.inf, -np.inf], 0)

            except KeyError as e:
                print(f"  [ERROR] Missing required key for indicator {indicator.get('indicator_id', 'unknown')}: {e}")
                skipped_indicators.append(indicator.get('indicator_id', 'unknown'))
            except Exception as e:
                print(f"  [ERROR] Failed to normalize {indicator.get('indicator_id', 'unknown')}: {e}")
                skipped_indicators.append(indicator.get('indicator_id', 'unknown'))

    except Exception as e:
        raise RuntimeError(f"Error in normalization: {e}")

    return df_experiments


def generate_summary_statistics(df_experiments):
    """
    Generate summary statistics about feasibility and thresholds.

    Args:
        df_experiments: DataFrame with all experiment data

    Returns:
        str: Summary text
    """
    # ====================
    # 1. Calculate overall feasibility statistics
    # ====================
    try:
        # Validate input
        if df_experiments is None or df_experiments.empty:
            return "No experiments data available for summary"

        total_exp = len(df_experiments)

        # Handle missing feasibility column
        if 'is_feasible' not in df_experiments.columns:
            print("  [WARNING] 'is_feasible' column not found, assuming all experiments are feasible")
            feasible_exp = total_exp
            infeasible_exp = 0
        else:
            feasible_exp = df_experiments['is_feasible'].sum()
            infeasible_exp = total_exp - feasible_exp

        summary = []
        summary.append("="*70)
        summary.append("  MODULE 2: EXPERIMENT AGGREGATION SUMMARY")
        summary.append("="*70)
        summary.append(f"\nTotal Experiments: {total_exp}")

        # Fix division by zero
        if total_exp > 0:
            summary.append(f"Feasible Experiments: {feasible_exp} ({100*feasible_exp/total_exp:.1f}%)")
            summary.append(f"Infeasible Experiments: {infeasible_exp} ({100*infeasible_exp/total_exp:.1f}%)")
        else:
            summary.append(f"Feasible Experiments: {feasible_exp} (N/A%)")
            summary.append(f"Infeasible Experiments: {infeasible_exp} (N/A%)")

        # ====================
        # 2. Calculate per-indicator violation counts
        # ====================
        summary.append(f"\nThreshold Violations by Indicator:")

        # Count violations per indicator
        indicator_cols = [col for col in df_experiments.columns if col.endswith('_in_threshold')]

        if indicator_cols:
            for col in indicator_cols:
                ind_id = col.replace('_in_threshold', '')
                violations = (~df_experiments[col]).sum()
                if total_exp > 0:
                    summary.append(f"  {ind_id}: {violations} violations ({100*violations/total_exp:.1f}%)")
                else:
                    summary.append(f"  {ind_id}: {violations} violations (N/A%)")
        else:
            summary.append("  No threshold checks were applied")

        summary.append("\n" + "="*70)

        return "\n".join(summary)

    except Exception as e:
        return f"Error generating summary: {e}"


def run_module2(data, save_output=False):
    """
    Main Module 2 orchestration function.

    Args:
        data: Dictionary with dataframes from previous modules
        save_output: If True, save debug output files

    Returns:
        dict: Updated data dictionary with df_experiments added
    """
    print("[Module 2] Aggregating indicators to experiment level...")

    # ====================
    # 1. Aggregate indicators
    # ====================
    try:
        df_experiments = aggregate_to_experiment_level(data)
        if df_experiments is not None and not df_experiments.empty:
            print(f"  [OK] Aggregated {len(df_experiments)} experiments")
        else:
            print("  [WARNING] No experiments were aggregated")
            data['df_experiments'] = pd.DataFrame()
            return data
    except Exception as e:
        print(f"  [ERROR] Aggregation failed: {e}")
        data['df_experiments'] = pd.DataFrame()
        return data

    # ====================
    # 2. Apply threshold filters
    # ====================
    try:
        df_experiments = apply_threshold_filters(df_experiments, data['indicators'])
        if 'is_feasible' in df_experiments.columns:
            feasible_count = df_experiments['is_feasible'].sum()
            print(f"  [OK] Threshold filtering complete: {feasible_count}/{len(df_experiments)} feasible")
        else:
            print("  [WARNING] Threshold filtering did not produce feasibility flags")
    except Exception as e:
        print(f"  [ERROR] Threshold filtering failed: {e}")

    # ====================
    # 3. Normalize indicators
    # ====================
    try:
        df_experiments = normalize_indicators(df_experiments, data['indicators'])
        print(f"  [OK] Normalization complete")
    except Exception as e:
        print(f"  [ERROR] Normalization failed: {e}")

    # ====================
    # 4. Store results and generate summary
    # ====================
    # Store in data dictionary
    data['df_experiments'] = df_experiments

    # Generate summary
    summary = generate_summary_statistics(df_experiments)
    print(summary)

    # ====================
    # 5. Save output (optional)
    # ====================
    if save_output:
        try:
            # Save dataframes
            df_dir = Path(__file__).parent.parent / 'output' / 'dataframes'
            df_dir.mkdir(parents=True, exist_ok=True)

            df_experiments.to_csv(df_dir / 'M2_01_df_experiments_aggregated.csv', index=False)
            print(f"\n  [OK] Saved: M2_01_df_experiments_aggregated.csv ({len(df_experiments)} experiments)")

            # Fix: Remove redundant == True comparison
            if 'is_feasible' in df_experiments.columns:
                df_feasible = df_experiments[df_experiments['is_feasible']]
                df_feasible.to_csv(df_dir / 'M2_02_df_experiments_feasible.csv', index=False)
                print(f"  [OK] Saved: M2_02_df_experiments_feasible.csv ({len(df_feasible)} experiments)")

            # Save reports
            reports_dir = Path(__file__).parent.parent / 'output' / 'reports'
            reports_dir.mkdir(parents=True, exist_ok=True)

            with open(reports_dir / 'module2_summary.txt', 'w') as f:
                f.write(summary)
            print(f"  [OK] Saved: module2_summary.txt")

        except Exception as e:
            print(f"  [ERROR] Failed to save output files: {e}")

    return data


if __name__ == '__main__':
    # Test Module 2 standalone
    from module0_data_loader import load_all_data
    from module1_step_indicators import calculate_indicators

    data = load_all_data()
    data = calculate_indicators(data, save_output=False)
    data = run_module2(data, save_output=True)

    print("\nModule 2 test complete!")
