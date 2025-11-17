"""
Module 6: Config-Driven Visualizations (Orchestrator)

PURPOSE:
- Generate publication-quality visualizations based on configuration file
- Support multiple plot types: bar, line, scatter, heatmap, spider, boxplot
- Utilize all group statistics from Module 4

INPUTS:
- config_visualizations.json: Visualization specifications
- Data from previous modules

OUTPUTS:
- PNG files (300 DPI) in analytics/output/visualizations/

ARCHITECTURE:
This module has been refactored for maintainability:
- visualizations/constants.py: All styling constants
- visualizations/helpers.py: Data prep, legends, utilities
- visualizations/plotting.py: All plot functions
- This file: Orchestrates visualization generation
"""

# Import all visualization components from the visualizations package
from .visualizations import (
    # Constants
    VIZ_OUTPUT_DIR,
    VIZ_SUMMARY_FILE,
    # Config loading
    load_visualization_config,
    # Data preparation
    prepare_data,
    # All plot functions
    plot_bar,
    plot_line,
    plot_scatter,
    plot_heatmap,
    plot_spider,
    plot_boxplot,
    plot_product_depth,
    plot_product_depth_by_automation,
    plot_system_type_automation_grid,
    plot_boxplot_by_stations,
    plot_boxplot_by_automation,
    plot_boxplot_by_product_mix,
    plot_line_faceted,
    plot_bar_grouped,
    plot_product_depth_by_automation_bars,
    plot_product_depth_bars_simple,
    plot_cumulative_profit_curve,
    plot_cumulative_profit_curve_bars,
)


def run_module6(data, save_output=False):
    """
    Main Module 6 orchestration function.

    Reads visualization configurations and generates all specified plots.

    Args:
        data: Dictionary containing all dataframes from previous modules
        save_output: If True, saves summary file

    Returns:
        data: Unchanged data dictionary (for pipeline consistency)
    """
    print("[Module 6] Generating visualizations...")

    try:
        # Load visualization config
        viz_config = load_visualization_config()

        # Create output directory
        viz_dir = VIZ_OUTPUT_DIR
        viz_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Failed to initialize module 6: {e}")
        raise

    generated_plots = []
    viz_counter = 1  # Counter for sequential numbering of visualization outputs

    # Generate each visualization
    for viz in viz_config['visualizations']:
        viz_id = viz['viz_id']
        viz_name = viz['viz_name']
        viz_type = viz['viz_type']

        print(f"  Generating {viz_id}: {viz_name}...")

        try:
            # Prepare data
            df = prepare_data(viz, data)

            # Generate plot based on type with module numbering
            base_filename = viz['output_filename']
            numbered_filename = f"M6_{viz_counter:02d}_{base_filename}"
            output_path = viz_dir / numbered_filename

            # Dispatch to appropriate plot function
            if viz_type in ['bar_horizontal', 'bar_vertical']:
                plot_bar(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'bar_vertical_grouped':
                plot_bar_grouped(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'line':
                plot_line(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'line_faceted':
                plot_line_faceted(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'scatter':
                plot_scatter(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'heatmap':
                plot_heatmap(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'spider':
                plot_spider(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'boxplot':
                plot_boxplot(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'boxplot_by_stations':
                plot_boxplot_by_stations(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'boxplot_by_automation':
                plot_boxplot_by_automation(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'boxplot_by_product_mix':
                plot_boxplot_by_product_mix(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'product_depth':
                plot_product_depth(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            elif viz_type == 'product_depth_by_automation':
                # Special case: generates multiple files
                modified_viz = viz.copy()
                modified_viz['output_filename'] = numbered_filename
                generated_files = plot_product_depth_by_automation(df, modified_viz, viz_dir)
                for filename in generated_files:
                    generated_plots.append(f"{viz_id}: {viz_name} → {filename}")

            elif viz_type == 'product_depth_by_automation_bars':
                # Bar chart version (stacked): generates multiple files
                modified_viz = viz.copy()
                modified_viz['output_filename'] = numbered_filename
                generated_files = plot_product_depth_by_automation_bars(df, modified_viz, viz_dir)
                for filename in generated_files:
                    generated_plots.append(f"{viz_id}: {viz_name} → {filename}")

            elif viz_type == 'product_depth_bars_simple':
                # Bar chart version (simple/aggregated): generates one file
                modified_viz = viz.copy()
                modified_viz['output_filename'] = numbered_filename
                generated_files = plot_product_depth_bars_simple(df, modified_viz, viz_dir)
                for filename in generated_files:
                    generated_plots.append(f"{viz_id}: {viz_name} → {filename}")

            elif viz_type == 'cumulative_profit_curve':
                # Scatter plot version: generates one file with 4 subplots
                modified_viz = viz.copy()
                modified_viz['output_filename'] = numbered_filename
                generated_files = plot_cumulative_profit_curve(df, modified_viz, viz_dir)
                for filename in generated_files:
                    generated_plots.append(f"{viz_id}: {viz_name} → {filename}")

            elif viz_type == 'cumulative_profit_curve_bars':
                # Bar chart version: generates multiple files
                modified_viz = viz.copy()
                modified_viz['output_filename'] = numbered_filename
                generated_files = plot_cumulative_profit_curve_bars(df, modified_viz, viz_dir)
                for filename in generated_files:
                    generated_plots.append(f"{viz_id}: {viz_name} → {filename}")

            elif viz_type == 'system_type_automation_grid':
                plot_system_type_automation_grid(df, viz, output_path)
                generated_plots.append(f"{viz_id}: {viz_name} → {numbered_filename}")
                print(f"    [OK] Saved: {numbered_filename}")

            else:
                print(f"    [WARNING] Unknown viz_type: {viz_type}")
                continue

            # Increment counter for next visualization
            viz_counter += 1

        except Exception as e:
            print(f"    [ERROR] Failed to generate {viz_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            # Still increment counter to maintain consistent numbering
            viz_counter += 1
            continue

    # Generate summary
    if save_output:
        summary_path = viz_dir / VIZ_SUMMARY_FILE
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("Generated Visualizations\n")
            f.write("=" * 50 + "\n\n")
            for plot in generated_plots:
                f.write(f"{plot}\n")
        print(f"\n  [OK] Saved: {VIZ_SUMMARY_FILE} ({len(generated_plots)} plots)")

    print(f"\n  [OK] Generated {len(generated_plots)} visualizations")

    return data


if __name__ == '__main__':
    # Test Module 6 standalone
    from module0_data_loader import load_all_data
    from module1_step_indicators import calculate_indicators
    from module2_experiment_aggregation import run_module2
    from module3_ranking import run_module3
    from module4_grouping import run_module4
    from module5_depth_analysis import run_module5

    data = load_all_data()
    data = calculate_indicators(data, save_output=True)
    data = run_module2(data, save_output=False)
    data = run_module3(data, save_output=False)
    data = run_module4(data, save_output=False)
    data = run_module5(data, save_output=True)
    data = run_module6(data, save_output=True)

    print("\nModule 6 test complete!")
