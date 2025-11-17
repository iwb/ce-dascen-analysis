"""
Module 3: Weighting & Ranking

PURPOSE:
- Apply weights to normalized indicators (AHP methodology)
- Calculate total weighted score per experiment
- Rank feasible experiments (TOPSIS-inspired ranking)

INPUTS:
- data['df_experiments']: Experiment table from Module 2 with normalized indicators
- data['indicators']: Config with indicator weights

OUTPUTS:
- data['df_experiments']: Enhanced with weighted indicators, total score, and rank
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ====================
# CONSTANTS AND CONFIGURATION
# ====================
# Column naming patterns
NORMALIZED_SUFFIX = '_normalized'
WEIGHTED_SUFFIX = '_weighted'
RANK_ALL_COLUMN = 'rank_all'
RANK_FEASIBLE_COLUMN = 'rank'
ECONOMIC_SCORE_COLUMN = 'economic_score'
ENVIRONMENTAL_SCORE_COLUMN = 'environmental_score'
TOTAL_SCORE_COLUMN = 'total_weighted_score'
FEASIBILITY_COLUMN = 'is_feasible'

# Category identifiers
ECONOMIC_CATEGORY = 'economic'
ENVIRONMENTAL_CATEGORY = 'environmental'

# Output paths and filenames
OUTPUT_DIR = Path(__file__).parent.parent / 'output'
DATAFRAMES_DIR = OUTPUT_DIR / 'dataframes'
REPORTS_DIR = OUTPUT_DIR / 'reports'
RANKED_ALL_FILENAME = 'M3_01_df_experiments_ranked_all.csv'
RANKED_FEASIBLE_FILENAME = 'M3_02_df_experiments_ranked_feasible.csv'
SUMMARY_FILENAME = 'module3_summary.txt'


def apply_weights(df_experiments, indicators_config, score_precision):
    """
    Apply weights to normalized indicators.

    Args:
        df_experiments: DataFrame with normalized indicator columns
        indicators_config: Config dictionary with indicator definitions
        score_precision: Decimal places for weighted values and scores

    Returns:
        pd.DataFrame: df_experiments with weighted indicator columns added
    """
    # ====================
    # 1. Validate inputs and extract indicator config
    # ====================
    try:
        # Validate inputs
        if df_experiments is None or df_experiments.empty:
            print("  [WARNING] Empty experiments dataframe, skipping weight application")
            return df_experiments

        if 'indicators' not in indicators_config:
            raise ValueError("Indicators configuration missing 'indicators' key")

        indicators = indicators_config['indicators']
        skipped_indicators = []

    except Exception as e:
        raise RuntimeError(f"Error validating inputs for weight application: {e}")

    # ====================
    # 2. Apply weights to normalized indicators
    # ====================
    for indicator in indicators:
        try:
            ind_id = indicator['indicator_id']
            weight = indicator['weight']

            # Check if normalized column exists
            normalized_col = f'{ind_id}{NORMALIZED_SUFFIX}'
            if normalized_col not in df_experiments.columns:
                print(f"  [WARNING] Normalized column '{normalized_col}' not found, skipping weight for {ind_id}")
                skipped_indicators.append(ind_id)
                continue

            # Create weighted column name
            weighted_col = f'{ind_id}{WEIGHTED_SUFFIX}'

            # Multiply normalized value by weight
            df_experiments[weighted_col] = df_experiments[normalized_col] * weight

            # Round to specified decimal places
            df_experiments[weighted_col] = df_experiments[weighted_col].round(score_precision)

            # Check for inf/NaN values
            if df_experiments[weighted_col].isin([np.inf, -np.inf]).any():
                print(f"  [WARNING] Infinite values detected in {weighted_col}, replacing with 0")
                df_experiments[weighted_col] = df_experiments[weighted_col].replace([np.inf, -np.inf], 0)

            if df_experiments[weighted_col].isna().any():
                nan_count = df_experiments[weighted_col].isna().sum()
                print(f"  [WARNING] {nan_count} NaN values in {weighted_col}, filling with 0")
                df_experiments[weighted_col] = df_experiments[weighted_col].fillna(0)

        except KeyError as e:
            print(f"  [ERROR] Missing required key for indicator {indicator.get('indicator_id', 'unknown')}: {e}")
            skipped_indicators.append(indicator.get('indicator_id', 'unknown'))
        except Exception as e:
            print(f"  [ERROR] Failed to apply weight for {indicator.get('indicator_id', 'unknown')}: {e}")
            skipped_indicators.append(indicator.get('indicator_id', 'unknown'))

    if len(skipped_indicators) > 0:
        print(f"  [WARNING] Weights not applied for {len(skipped_indicators)} indicators: {skipped_indicators}")

    return df_experiments


def calculate_total_score(df_experiments, indicators_config, score_precision):
    """
    Calculate total weighted score and category-specific scores.

    Args:
        df_experiments: DataFrame with weighted indicator columns
        indicators_config: Config dictionary with indicator definitions
        score_precision: Decimal places for weighted values and scores

    Returns:
        pd.DataFrame: df_experiments with economic_score, environmental_score, and total_weighted_score columns
    """
    # ====================
    # 1. Separate indicators by category
    # ====================
    try:
        # Validate inputs
        if df_experiments is None or df_experiments.empty:
            print("  [WARNING] Empty experiments dataframe, skipping score calculation")
            return df_experiments

        if 'indicators' not in indicators_config:
            raise ValueError("Indicators configuration missing 'indicators' key")

        indicators = indicators_config['indicators']

        # Separate indicators by category
        economic_indicators = [ind for ind in indicators if ind.get('category') == ECONOMIC_CATEGORY]
        environmental_indicators = [ind for ind in indicators if ind.get('category') == ENVIRONMENTAL_CATEGORY]

        # Warn if categories are empty
        if not economic_indicators:
            print(f"  [WARNING] No indicators found with category '{ECONOMIC_CATEGORY}'")
        if not environmental_indicators:
            print(f"  [WARNING] No indicators found with category '{ENVIRONMENTAL_CATEGORY}'")

    except Exception as e:
        raise RuntimeError(f"Error processing indicator categories: {e}")

    # ====================
    # 2. Calculate category-specific scores
    # ====================
    try:
        # Calculate economic score
        economic_cols = []
        for ind in economic_indicators:
            weighted_col = f"{ind['indicator_id']}{WEIGHTED_SUFFIX}"
            if weighted_col in df_experiments.columns:
                economic_cols.append(weighted_col)
            else:
                print(f"  [WARNING] Weighted column '{weighted_col}' not found for economic score")

        if economic_cols:
            df_experiments[ECONOMIC_SCORE_COLUMN] = df_experiments[economic_cols].sum(axis=1).round(score_precision)
        else:
            print(f"  [WARNING] No economic columns found, setting {ECONOMIC_SCORE_COLUMN} to 0")
            df_experiments[ECONOMIC_SCORE_COLUMN] = 0

        # Calculate environmental score
        environmental_cols = []
        for ind in environmental_indicators:
            weighted_col = f"{ind['indicator_id']}{WEIGHTED_SUFFIX}"
            if weighted_col in df_experiments.columns:
                environmental_cols.append(weighted_col)
            else:
                print(f"  [WARNING] Weighted column '{weighted_col}' not found for environmental score")

        if environmental_cols:
            df_experiments[ENVIRONMENTAL_SCORE_COLUMN] = df_experiments[environmental_cols].sum(axis=1).round(score_precision)
        else:
            print(f"  [WARNING] No environmental columns found, setting {ENVIRONMENTAL_SCORE_COLUMN} to 0")
            df_experiments[ENVIRONMENTAL_SCORE_COLUMN] = 0

    except Exception as e:
        print(f"  [ERROR] Failed to calculate category scores: {e}")
        df_experiments[ECONOMIC_SCORE_COLUMN] = 0
        df_experiments[ENVIRONMENTAL_SCORE_COLUMN] = 0

    # ====================
    # 3. Calculate total weighted score
    # ====================
    try:
        # Get all weighted columns that actually exist
        all_weighted_cols = []
        for ind in indicators:
            weighted_col = f"{ind['indicator_id']}{WEIGHTED_SUFFIX}"
            if weighted_col in df_experiments.columns:
                all_weighted_cols.append(weighted_col)

        if all_weighted_cols:
            df_experiments[TOTAL_SCORE_COLUMN] = df_experiments[all_weighted_cols].sum(axis=1).round(score_precision)

            # Check for inf/NaN in total score
            if df_experiments[TOTAL_SCORE_COLUMN].isin([np.inf, -np.inf]).any():
                print(f"  [WARNING] Infinite values detected in {TOTAL_SCORE_COLUMN}, replacing with 0")
                df_experiments[TOTAL_SCORE_COLUMN] = df_experiments[TOTAL_SCORE_COLUMN].replace([np.inf, -np.inf], 0)

            if df_experiments[TOTAL_SCORE_COLUMN].isna().any():
                nan_count = df_experiments[TOTAL_SCORE_COLUMN].isna().sum()
                print(f"  [WARNING] {nan_count} NaN values in {TOTAL_SCORE_COLUMN}, filling with 0")
                df_experiments[TOTAL_SCORE_COLUMN] = df_experiments[TOTAL_SCORE_COLUMN].fillna(0)
        else:
            print(f"  [ERROR] No weighted columns found, setting {TOTAL_SCORE_COLUMN} to 0")
            df_experiments[TOTAL_SCORE_COLUMN] = 0

    except Exception as e:
        print(f"  [ERROR] Failed to calculate total weighted score: {e}")
        df_experiments[TOTAL_SCORE_COLUMN] = 0

    return df_experiments


def rank_experiments(df_experiments):
    """
    Rank ALL experiments based on total weighted score.

    NEW LOGIC (per user requirements):
    - Creates TWO ranking columns:
      1. 'rank_all': Ranks ALL experiments (feasible + infeasible) by score
      2. 'rank': Ranks ONLY feasible experiments (for backward compatibility)

    - Infeasible experiments get rank_all (can still be compared)
    - Infeasible experiments get rank = NaN (excluded from feasible ranking)
    - This enables AHP to rank all experiments while keeping feasible subset separate

    Args:
        df_experiments: DataFrame with total_weighted_score and is_feasible columns

    Returns:
        pd.DataFrame: df_experiments with rank_all and rank columns added
    """
    # ====================
    # 1. Rank ALL experiments (feasible + infeasible)
    # ====================
    try:
        # Validate inputs
        if df_experiments is None or df_experiments.empty:
            print("  [WARNING] Empty experiments dataframe, skipping ranking")
            return df_experiments

        # Check required columns exist
        if TOTAL_SCORE_COLUMN not in df_experiments.columns:
            print(f"  [ERROR] Column '{TOTAL_SCORE_COLUMN}' not found, cannot rank experiments")
            df_experiments[RANK_ALL_COLUMN] = pd.NA
            df_experiments[RANK_FEASIBLE_COLUMN] = pd.NA
            return df_experiments

        if FEASIBILITY_COLUMN not in df_experiments.columns:
            print(f"  [WARNING] Column '{FEASIBILITY_COLUMN}' not found, assuming all experiments are feasible")
            df_experiments[FEASIBILITY_COLUMN] = True

        # Rank ALL experiments by score
        # Higher score = better = lower rank number
        df_experiments[RANK_ALL_COLUMN] = (
            df_experiments[TOTAL_SCORE_COLUMN]
            .rank(ascending=False, method='min')
            .astype(int)
        )

    except Exception as e:
        print(f"  [ERROR] Failed to rank all experiments: {e}")
        df_experiments[RANK_ALL_COLUMN] = pd.NA

    # ====================
    # 2. Rank ONLY feasible experiments
    # ====================
    try:
        # Fix: Remove redundant == True comparison
        feasible_mask = df_experiments[FEASIBILITY_COLUMN]

        # Initialize rank column as nullable integer type (allows NaN while keeping integers)
        df_experiments[RANK_FEASIBLE_COLUMN] = pd.Series(dtype='Int64')

        if feasible_mask.sum() > 0:
            # Rank only feasible experiments
            df_experiments.loc[feasible_mask, RANK_FEASIBLE_COLUMN] = (
                df_experiments.loc[feasible_mask, TOTAL_SCORE_COLUMN]
                .rank(ascending=False, method='min')
                .astype('Int64')
            )
            print(f"  [OK] Ranked {feasible_mask.sum()} feasible experiments")
        else:
            print("  [WARNING] No feasible experiments to rank")

        # Infeasible experiments automatically have NaN (pd.NA) due to dtype='Int64'
        # No need to explicitly assign NaN to infeasible rows

    except Exception as e:
        print(f"  [ERROR] Failed to rank feasible experiments: {e}")
        df_experiments[RANK_FEASIBLE_COLUMN] = pd.NA

    return df_experiments


def generate_summary_statistics(df_experiments, indicators_config, score_precision, separator_width, top_n_display):
    """
    Generate summary statistics about ranking.

    Args:
        df_experiments: DataFrame with all experiment data
        indicators_config: Config dictionary with indicator definitions
        score_precision: Decimal places for score formatting
        separator_width: Width of separator lines in summary
        top_n_display: Number of top/bottom experiments to display

    Returns:
        str: Summary text
    """
    # ====================
    # 1. Display weight distribution
    # ====================
    try:
        if 'indicators' not in indicators_config:
            return "Error: Indicators configuration missing"

        indicators = indicators_config['indicators']

        summary = []
        summary.append("=" * separator_width)
        summary.append("  MODULE 3: RANKING & WEIGHTING SUMMARY")
        summary.append("=" * separator_width)

        # Weight distribution
        summary.append("\nIndicator Weights:")
        total_weight = 0
        for indicator in indicators:
            ind_id = indicator['indicator_id']
            ind_name = indicator['indicator_name']
            weight = indicator['weight']
            total_weight += weight
            summary.append(f"  {ind_id} ({ind_name}): {weight:.2f} ({100*weight:.0f}%)")
        summary.append(f"  Total: {total_weight:.2f} ({100*total_weight:.0f}%)")

    except Exception as e:
        return f"Error generating weight summary: {e}"

    # ====================
    # 2. Display all experiments ranking
    # ====================
    try:
        if df_experiments is None or df_experiments.empty:
            summary.append("\nNo experiments data available")
            return "\n".join(summary)

        # Check if ranking columns exist
        if RANK_ALL_COLUMN in df_experiments.columns:
            df_all = df_experiments.copy().sort_values(RANK_ALL_COLUMN)
            summary.append(f"\nALL Experiments Ranked: {len(df_all)}")
            summary.append(f"\nTop {top_n_display} Experiments (All):")
            for idx, row in df_all.head(top_n_display).iterrows():
                if FEASIBILITY_COLUMN in df_experiments.columns:
                    feasible_flag = "OK" if row[FEASIBILITY_COLUMN] else "INFEASIBLE"
                else:
                    feasible_flag = "UNKNOWN"
                summary.append(
                    f"  Rank {int(row[RANK_ALL_COLUMN])}: {row['exp_id']} [{feasible_flag}] "
                    f"(score: {row[TOTAL_SCORE_COLUMN]:.{score_precision}f}, "
                    f"system: {row.get('system', 'N/A')}, mix: {row.get('product_mix', 'N/A')})"
                )
        else:
            summary.append("\nAll experiments ranking not available")

    except Exception as e:
        summary.append(f"\nError displaying all experiments ranking: {e}")

    # ====================
    # 3. Display feasible experiments ranking
    # ====================
    try:
        if FEASIBILITY_COLUMN in df_experiments.columns:
            # Fix: Remove == True comparison
            df_feasible = df_experiments[df_experiments[FEASIBILITY_COLUMN]].copy()
            if RANK_FEASIBLE_COLUMN in df_feasible.columns:
                df_feasible = df_feasible.sort_values(RANK_FEASIBLE_COLUMN)

                summary.append(f"\nFeasible Experiments ONLY: {len(df_feasible)}/{len(df_experiments)}")

                if len(df_feasible) > 0:
                    summary.append(f"\nTop {top_n_display} Feasible Experiments:")
                    for idx, row in df_feasible.head(top_n_display).iterrows():
                        summary.append(
                            f"  Rank {int(row[RANK_FEASIBLE_COLUMN])}: {row['exp_id']} "
                            f"(score: {row[TOTAL_SCORE_COLUMN]:.{score_precision}f}, "
                            f"rank_all: {int(row[RANK_ALL_COLUMN]) if RANK_ALL_COLUMN in row else 'N/A'}, "
                            f"system: {row.get('system', 'N/A')}, mix: {row.get('product_mix', 'N/A')})"
                        )

                    if len(df_feasible) >= top_n_display:
                        summary.append(f"\nBottom {top_n_display} Feasible Experiments:")
                        for idx, row in df_feasible.tail(top_n_display).iterrows():
                            summary.append(
                                f"  Rank {int(row[RANK_FEASIBLE_COLUMN])}: {row['exp_id']} "
                                f"(score: {row[TOTAL_SCORE_COLUMN]:.{score_precision}f}, "
                                f"rank_all: {int(row[RANK_ALL_COLUMN]) if RANK_ALL_COLUMN in row else 'N/A'})"
                            )

                    if TOTAL_SCORE_COLUMN in df_feasible.columns:
                        summary.append(f"\nScore Statistics (Feasible):")
                        summary.append(f"  Mean: {df_feasible[TOTAL_SCORE_COLUMN].mean():.{score_precision}f}")
                        summary.append(f"  Std: {df_feasible[TOTAL_SCORE_COLUMN].std():.{score_precision}f}")
                        summary.append(f"  Min: {df_feasible[TOTAL_SCORE_COLUMN].min():.{score_precision}f}")
                        summary.append(f"  Max: {df_feasible[TOTAL_SCORE_COLUMN].max():.{score_precision}f}")
                else:
                    summary.append("\nNo feasible experiments found")
            else:
                summary.append("\nFeasible experiments ranking not available")
        else:
            summary.append("\nFeasibility information not available")

    except Exception as e:
        summary.append(f"\nError displaying feasible experiments ranking: {e}")

    # ====================
    # 4. Display infeasible experiments
    # ====================
    try:
        if FEASIBILITY_COLUMN in df_experiments.columns:
            # Fix: Use ~ for negation instead of == False
            df_infeasible = df_experiments[~df_experiments[FEASIBILITY_COLUMN]]
            if len(df_infeasible) > 0 and RANK_ALL_COLUMN in df_infeasible.columns:
                df_infeasible = df_infeasible.sort_values(RANK_ALL_COLUMN)
                summary.append(f"\nInfeasible Experiments: {len(df_infeasible)}")
                for idx, row in df_infeasible.iterrows():
                    summary.append(
                        f"  Rank_all {int(row[RANK_ALL_COLUMN])}: {row['exp_id']} "
                        f"(score: {row[TOTAL_SCORE_COLUMN]:.{score_precision}f})"
                    )
            elif len(df_infeasible) > 0:
                summary.append(f"\nInfeasible Experiments: {len(df_infeasible)} (not ranked)")

    except Exception as e:
        summary.append(f"\nError displaying infeasible experiments: {e}")

    summary.append("\n" + "=" * separator_width)

    return "\n".join(summary)


def run_module3(data, save_output=False):
    """
    Main Module 3 orchestration function.

    Args:
        data: Dictionary with dataframes from previous modules
        save_output: If True, save debug output files

    Returns:
        dict: Updated data dictionary with enhanced df_experiments
    """
    print("[Module 3] Applying weights and ranking experiments...")

    # ====================
    # 1. Initialize and copy input data
    # ====================
    try:
        # Validate required data keys exist
        if 'df_experiments' not in data:
            print("  [ERROR] 'df_experiments' not found in data dictionary")
            print("  [ERROR] Module 2 must be run before Module 3")
            return data

        if 'indicators' not in data:
            print("  [ERROR] 'indicators' configuration not found in data dictionary")
            return data

        if 'formatting_config' not in data:
            print("  [ERROR] 'formatting_config' not found in data dictionary")
            return data

        df_experiments = data['df_experiments'].copy()

        if df_experiments.empty:
            print("  [WARNING] Empty experiments dataframe, nothing to rank")
            return data

        # Extract formatting configuration
        fmt_config = data['formatting_config']
        score_precision = fmt_config['output_formatting']['score_precision']
        separator_width = fmt_config['console_output']['separator_width']
        top_n_display = fmt_config['console_output']['top_n_display']

    except Exception as e:
        print(f"  [ERROR] Failed to initialize Module 3: {e}")
        return data

    # ====================
    # 2. Apply weights to normalized indicators
    # ====================
    try:
        df_experiments = apply_weights(df_experiments, data['indicators'], score_precision)
        if 'indicators' in data['indicators']:
            num_indicators = len(data['indicators']['indicators'])
            print(f"  [OK] Applied weights to {num_indicators} indicators")
    except Exception as e:
        print(f"  [ERROR] Failed to apply weights: {e}")

    # ====================
    # 3. Calculate total weighted scores
    # ====================
    try:
        df_experiments = calculate_total_score(df_experiments, data['indicators'], score_precision)
        print(f"  [OK] Calculated total weighted scores")
    except Exception as e:
        print(f"  [ERROR] Failed to calculate scores: {e}")

    # ====================
    # 4. Rank experiments
    # ====================
    try:
        df_experiments = rank_experiments(df_experiments)
        if FEASIBILITY_COLUMN in df_experiments.columns:
            feasible_count = df_experiments[FEASIBILITY_COLUMN].sum()
            print(f"  [OK] Ranked {feasible_count} feasible experiments")
    except Exception as e:
        print(f"  [ERROR] Failed to rank experiments: {e}")

    # Update data dictionary
    data['df_experiments'] = df_experiments

    # ====================
    # 5. Generate and display summary
    # ====================
    try:
        summary = generate_summary_statistics(df_experiments, data['indicators'],
                                              score_precision, separator_width, top_n_display)
        print(summary)
    except Exception as e:
        print(f"  [ERROR] Failed to generate summary: {e}")
        summary = "Summary generation failed"

    # ====================
    # 6. Save output files (optional)
    # ====================
    if save_output:
        try:
            # Save dataframes
            DATAFRAMES_DIR.mkdir(parents=True, exist_ok=True)

            # OUTPUT 1: ALL experiments ranked (includes infeasible with rank_all)
            if RANK_ALL_COLUMN in df_experiments.columns:
                df_all = df_experiments.copy().sort_values(RANK_ALL_COLUMN)

                # Convert Int64 rank column to string representation for CSV (removes .0 decimals)
                # Keep NaN as empty string for infeasible experiments
                df_all_export = df_all.copy()
                if RANK_FEASIBLE_COLUMN in df_all_export.columns:
                    df_all_export[RANK_FEASIBLE_COLUMN] = df_all_export[RANK_FEASIBLE_COLUMN].apply(
                        lambda x: '' if pd.isna(x) else str(int(x))
                    )

                df_all_export.to_csv(DATAFRAMES_DIR / RANKED_ALL_FILENAME, index=False)
                print(f"\n  [OK] Saved: {RANKED_ALL_FILENAME} ({len(df_all)} experiments)")

            # OUTPUT 2: ONLY feasible experiments ranked (excludes infeasible)
            if FEASIBILITY_COLUMN in df_experiments.columns and RANK_FEASIBLE_COLUMN in df_experiments.columns:
                # Fix: Remove == True comparison
                df_feasible = df_experiments[df_experiments[FEASIBILITY_COLUMN]].copy()
                if not df_feasible.empty:
                    df_feasible = df_feasible.sort_values(RANK_FEASIBLE_COLUMN)

                    # Convert Int64 rank to regular int (no NaN in feasible set)
                    df_feasible[RANK_FEASIBLE_COLUMN] = df_feasible[RANK_FEASIBLE_COLUMN].astype(int)

                    df_feasible.to_csv(DATAFRAMES_DIR / RANKED_FEASIBLE_FILENAME, index=False)
                    print(f"  [OK] Saved: {RANKED_FEASIBLE_FILENAME} ({len(df_feasible)} experiments)")

            # Save reports
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)

            with open(REPORTS_DIR / SUMMARY_FILENAME, 'w') as f:
                f.write(summary)
            print(f"  [OK] Saved: {SUMMARY_FILENAME}")

        except Exception as e:
            print(f"  [ERROR] Failed to save output files: {e}")

    return data


if __name__ == '__main__':
    # Test Module 3 standalone
    from module0_data_loader import load_all_data
    from module1_step_indicators import calculate_indicators
    from module2_experiment_aggregation import run_module2

    data = load_all_data()
    data = calculate_indicators(data, save_output=False)
    data = run_module2(data, save_output=False)
    data = run_module3(data, save_output=True)

    print("\nModule 3 test complete!")
