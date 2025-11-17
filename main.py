"""
Analytics Framework - Main Orchestrator

This script orchestrates the complete analytics workflow for the disassembly simulation DoE analysis.

WORKFLOW:
1. Module 0: Load all input data (indicators, DoE table, experiment configs, simulation outputs)
2. Module 1: Calculate indicators and values for all process steps
3. Module 2: Aggregate to experiment level, apply thresholds, normalize indicators
4. Module 3: Apply AHP weights and rank experiments (feasible + all)
5. Module 4: Calculate group statistics
6. Module 5: Generate trajectory analysis and configuration reports
7. Module 6: Create all visualizations

DATA FLOW:
Module 0 → data['df_process', 'df_product', 'df_resource', 'df_system', 'doe', 'indicators']
         ↓
Module 1 → Adds IND01-IND06, VAL01-04, REVENUE, COSTS, PROFIT to dataframes
         ↓
Module 2 → data['df_experiments'] with aggregated indicators, thresholds, normalized values
         ↓
Module 3 → Adds rank_all, rank, total_weighted_score to df_experiments
         ↓
Module 4 → data['df_groups'] with group-level statistics
         ↓
Module 5 → data['depth_component_analysis', 'depth_cumulative', 'depth_product_cumulative', 'depth_profit_with_baseline']
         ↓
Module 6 → SVG visualizations in output/visualizations/

USAGE:
    python main.py

The pipeline runs all modules sequentially and generates:
- CSV outputs in output/dataframes/
- Trajectory reports in output/trajectories/
- Group statistics in output/groups/
- Visualizations in output/visualizations/
"""

from pathlib import Path

# Import all modules
from modules.module0_data_loader import load_all_data
from modules.module1_step_indicators import calculate_indicators
from modules.module2_experiment_aggregation import run_module2
from modules.module3_ranking import run_module3
from modules.module4_grouping import run_module4
from modules.module5_depth_analysis import run_module5
from modules.module6_visualizations import run_module6


def main():
    """Main orchestrator function."""
    print("=" * 80)
    print("DISASSEMBLY SIMULATION DoE ANALYTICS FRAMEWORK")
    print("=" * 80)

    # ========================================================================
    # MODULE 0: DATA LOADING
    # ========================================================================
    print("\n[MODULE 0] Loading input data...")
    data = load_all_data()
    print(f"  [OK] Loaded data for {len(data['doe'])} experiments")

    # ========================================================================
    # MODULE 1: INDICATOR CALCULATION
    # ========================================================================
    print("\n[MODULE 1] Calculating indicators...")
    data = calculate_indicators(data, save_output=False)
    print(f"  [OK] Calculated indicators for {len(data['df_process'])} process steps")

    # ========================================================================
    # MODULE 2: EXPERIMENT AGGREGATION & NORMALIZATION
    # ========================================================================
    print("\n[MODULE 2] Aggregating to experiment level...")
    data = run_module2(data, save_output=True)
    feasible_count = data['df_experiments']['is_feasible'].sum()
    print(f"  [OK] Aggregated {len(data['df_experiments'])} experiments ({feasible_count} feasible)")

    # ========================================================================
    # MODULE 3: RANKING (AHP)
    # ========================================================================
    print("\n[MODULE 3] Applying AHP weights and ranking...")
    data = run_module3(data, save_output=True)
    print(f"  [OK] Created rankings (all + feasible only)")

    # ========================================================================
    # MODULE 4: GROUP STATISTICS
    # ========================================================================
    print("\n[MODULE 4] Calculating group statistics...")
    data = run_module4(data, save_output=True)
    print(f"  [OK] Calculated statistics for {len(data['df_groups'])} group-indicator combinations")

    # ========================================================================
    # MODULE 5: TRAJECTORY ANALYSIS & REPORTS
    # ========================================================================
    print("\n[MODULE 5] Generating trajectory analysis and reports...")
    data = run_module5(data, save_output=True)
    print(f"  [OK] Generated depth analysis and cumulative trajectories")

    # ========================================================================
    # MODULE 6: VISUALIZATIONS
    # ========================================================================
    print("\n[MODULE 6] Creating visualizations...")
    data = run_module6(data)
    print(f"  [OK] All visualizations complete")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("ANALYTICS COMPLETE")
    print("=" * 80)
    print("\nOutput Locations:")
    print("  - CSV exports: output/dataframes/")
    print("  - Group statistics: output/groups/")
    print("  - Trajectory reports: output/trajectories/")
    print("  - Visualizations: output/visualizations/")
    print("\nKey Results:")
    print(f"  - Total experiments: {len(data['df_experiments'])}")
    print(f"  - Feasible experiments: {feasible_count}")
    print(f"  - Top ranked experiment: {data['df_experiments'][data['df_experiments']['rank'] == 1]['exp_id'].iloc[0] if feasible_count > 0 else 'N/A'}")
    print("=" * 80)


if __name__ == '__main__':
    main()
