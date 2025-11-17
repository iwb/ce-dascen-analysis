"""
Visualization Plotting Functions

All plot generation functions for different visualization types.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .constants import (
    CONFIG_DIR, CONFIG_INDICATORS_FILE,
    DEFAULT_DPI, DEFAULT_FIGSIZE, LARGE_FIGSIZE, SPIDER_FIGSIZE,
    DEFAULT_PALETTE, DEFAULT_COLORMAP, DEFAULT_ALPHA,
    HEATMAP_LINEWIDTH, HEATMAP_LINECOLOR,
    ERROR_BAR_CAPSIZE, ERROR_BAR_LINEWIDTH, ERROR_BAR_MARKERSIZE, DEFAULT_LINE_MARKER,
    SPIDER_R_MIN, SPIDER_R_MAX, SPIDER_TICK_VALUES, SPIDER_MARKER_SIZE,
    MARKER_STYLES, DEFAULT_GRID_ALPHA, DEFAULT_PAD,
    DEFAULT_TITLE_FONTSIZE, DEFAULT_LABEL_FONTSIZE, DEFAULT_LEGEND_FONTSIZE,
    DEFAULT_ANNOTATION_FONTSIZE, DEFAULT_FONTWEIGHT_BOLD, DEFAULT_FONT_SIZE,
    DEFAULT_TICK_FONTSIZE,
    HEATMAP_FIGSIZE_BASE, HEATMAP_SIZE_MULTIPLIER,
    DEFAULT_SCATTER_MIN_SIZE, DEFAULT_SCATTER_MAX_SIZE,
    DEFAULT_MARKER_SIZE,
    ATTRIBUTES_DIR, ATTRIBUTES_PATHS_FILE
)
from .helpers import create_footer_legend, get_system_info, build_component_ordering_lookup, sort_key_for_step_id, generate_color_shades, create_step_table_legend, load_product_types


# ====================
# Helper Functions
# ====================

def get_product_type_colors():
    """Generate product type color mapping from configuration."""
    product_type_config = load_product_types()
    color_mapping = {}

    for product_type, color_spec in product_type_config['colors'].items():
        colormap_name = color_spec['colormap']
        color_index = color_spec['index']
        colormap = getattr(plt.cm, colormap_name)
        color_mapping[product_type] = colormap(color_index)

    return color_mapping


# ====================
# BATCH 1: Core Plot Types
# ====================

def plot_bar(df, config, output_path):
    """Generate bar chart."""
    try:
        fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

        x_var = config['x_axis']['variable']
        y_var = config['y_axis']['variable']
        horizontal = config['viz_type'] == 'bar_horizontal'

        if 'color' in config:
            color_var = config['color']['variable']
            palette = config['color'].get('palette', DEFAULT_PALETTE)

            if horizontal:
                sns.barplot(data=df, y=y_var, x=x_var, hue=color_var, palette=palette, ax=ax)
            else:
                sns.barplot(data=df, x=x_var, y=y_var, hue=color_var, palette=palette, ax=ax)
        else:
            if horizontal:
                sns.barplot(data=df, y=y_var, x=x_var, ax=ax)
            else:
                sns.barplot(data=df, x=x_var, y=y_var, ax=ax)

        ax.set_xlabel(config['x_axis'].get('label', x_var))
        ax.set_ylabel(config['y_axis'].get('label', y_var))
        ax.set_title(config['title'])

        plt.tight_layout()
        plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"[ERROR] Failed to generate bar plot: {e}")
        plt.close()
        raise


def plot_line(df, config, output_path):
    """Generate line chart."""
    x_var = config['x_axis']['variable']
    y_var = config['y_axis']['variable']

    # Check if faceting is needed
    if 'facet' in config:
        facet_var = config['facet']['variable']
        ncols = config['facet'].get('ncols', 2)

        unique_vals = df[facet_var].unique()
        nrows = int(np.ceil(len(unique_vals) / ncols))

        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*5, nrows*4))
        axes = axes.flatten() if nrows * ncols > 1 else [axes]

        for idx, val in enumerate(unique_vals):
            if idx < len(axes):
                df_subset = df[df[facet_var] == val]
                ax = axes[idx]

                if 'series' in config:
                    series_var = config['series']['variable']
                    for series_val in df_subset[series_var].unique():
                        df_series = df_subset[df_subset[series_var] == series_val]
                        ax.plot(df_series[x_var], df_series[y_var], marker=DEFAULT_LINE_MARKER, label=series_val)
                else:
                    ax.plot(df_subset[x_var], df_subset[y_var], marker=DEFAULT_LINE_MARKER)

                ax.set_title(f"{facet_var}: {val}")
                ax.set_xlabel(config['x_axis'].get('label', x_var))
                ax.set_ylabel(config['y_axis'].get('label', y_var))
                if 'series' in config:
                    ax.legend()

        # Hide unused subplots
        for idx in range(len(unique_vals), len(axes)):
            axes[idx].set_visible(False)
    else:
        fig, ax = plt.subplots(figsize=LARGE_FIGSIZE)

        if 'series' in config:
            series_var = config['series']['variable']
            series_vals = sorted(df[series_var].unique())

            # Use tab10 colormap for consistency
            colors = plt.cm.tab10(np.linspace(0, 0.9, len(series_vals)))

            for idx, series_val in enumerate(series_vals):
                df_series = df[df[series_var] == series_val]
                color = colors[idx]

                if 'error_bars' in config:
                    err_var = config['error_bars']['variable']
                    ax.errorbar(df_series[x_var], df_series[y_var],
                              yerr=df_series[err_var], marker=DEFAULT_LINE_MARKER, label=series_val,
                              capsize=ERROR_BAR_CAPSIZE, color=color, linewidth=ERROR_BAR_LINEWIDTH,
                              markersize=ERROR_BAR_MARKERSIZE)
                else:
                    ax.plot(df_series[x_var], df_series[y_var], marker=DEFAULT_LINE_MARKER,
                           label=series_val, color=color, linewidth=ERROR_BAR_LINEWIDTH,
                           markersize=ERROR_BAR_MARKERSIZE)
            ax.legend(loc='best', fontsize=DEFAULT_LEGEND_FONTSIZE, frameon=True, fancybox=True, shadow=True)
        else:
            if 'error_bars' in config:
                err_var = config['error_bars']['variable']
                ax.errorbar(df[x_var], df[y_var], yerr=df[err_var], marker=DEFAULT_LINE_MARKER,
                           capsize=ERROR_BAR_CAPSIZE)
            else:
                ax.plot(df[x_var], df[y_var], marker=DEFAULT_LINE_MARKER)

        ax.set_xlabel(config['x_axis'].get('label', x_var), fontsize=DEFAULT_LABEL_FONTSIZE,
                     fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(config['y_axis'].get('label', y_var), fontsize=DEFAULT_LABEL_FONTSIZE,
                     fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_title(config['title'], fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD,
                    pad=DEFAULT_PAD)
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA)

    plt.tight_layout()
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_scatter(df, config, output_path):
    """Generate scatter plot."""
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

    x_var = config['x_axis']['variable']
    y_var = config['y_axis']['variable']

    scatter_kwargs = {}
    if 'color' in config:
        scatter_kwargs['hue'] = config['color']['variable']
        scatter_kwargs['palette'] = config['color'].get('palette', DEFAULT_PALETTE)
    if 'size' in config:
        scatter_kwargs['size'] = config['size']['variable']
        scatter_kwargs['sizes'] = (config['size'].get('min', DEFAULT_SCATTER_MIN_SIZE),
                                   config['size'].get('max', DEFAULT_SCATTER_MAX_SIZE))

    sns.scatterplot(data=df, x=x_var, y=y_var, **scatter_kwargs, ax=ax, alpha=DEFAULT_ALPHA)

    if config.get('trend_line', False):
        z = np.polyfit(df[x_var].dropna(), df[y_var].dropna(), 1)
        p = np.poly1d(z)
        ax.plot(df[x_var], p(df[x_var]), "r--", alpha=0.5, label='Trend')

    ax.set_xlabel(config['x_axis'].get('label', x_var))
    ax.set_ylabel(config['y_axis'].get('label', y_var))
    ax.set_title(config['title'])
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_heatmap(df, config, output_path):
    """
    Generate heatmap using pre-aggregated group statistics from Module 4.

    IMPORTANT: Expects df_groups filtered by group_id (e.g., 'G11').
    For interaction groups, uses individual grouping variable columns (product_mix, system).
    Config specifies metric (e.g., 'rank') and statistic ('mean' or 'std').

    Config option 'transpose' (default: false): if true, swaps rows and columns for axis rotation.
    """
    row_var = config['rows']['variable']
    col_var = config['cols']['variable']
    row_label = config['rows'].get('label', row_var)
    col_label = config['cols'].get('label', col_var)

    metric = config.get('metric', 'rank')  # Which metric to plot
    statistic = config.get('statistic', 'mean')  # Which statistic (mean/std/min/max)

    # Filter to specific metric
    df_metric = df[df['indicator_id'] == metric].copy()

    if df_metric.empty:
        print(f"[WARNING] No data for metric: {metric}")
        return

    # Check if individual grouping variables exist in dataframe
    if row_var not in df_metric.columns or col_var not in df_metric.columns:
        print(f"[ERROR] Grouping variables {row_var} or {col_var} not found in df_groups")
        print(f"Available columns: {df_metric.columns.tolist()}")
        return

    # Extract the statistic column as value
    if statistic not in df_metric.columns:
        print(f"[ERROR] Statistic '{statistic}' not found. Available: {df_metric.columns.tolist()}")
        return

    df_metric['value'] = df_metric[statistic]

    # Pivot data for heatmap
    pivot_df = df_metric.pivot_table(index=row_var, columns=col_var, values='value', aggfunc='first')

    # Ensure full grid by reindexing with all possible values
    all_row_values = sorted(df_metric[row_var].unique())
    all_col_values = sorted(df_metric[col_var].unique())

    # Reindex to ensure all combinations are present
    pivot_df = pivot_df.reindex(index=all_row_values, columns=all_col_values)

    # Transpose if requested (swaps rows and columns)
    if config.get('transpose', False):
        pivot_df = pivot_df.T
        row_label, col_label = col_label, row_label

    # Get dimensions
    n_rows, n_cols = pivot_df.shape

    # Create figure with proper sizing
    fig, ax = plt.subplots(figsize=(max(HEATMAP_FIGSIZE_BASE[0], n_cols * HEATMAP_SIZE_MULTIPLIER),
                                     max(HEATMAP_FIGSIZE_BASE[1], n_rows * 1.2)))

    # Create a mask for NaN values
    mask = pivot_df.isna()

    # Create custom colormap
    cmap = sns.color_palette(config.get('colormap', DEFAULT_COLORMAP), as_cmap=True)

    # Get colorbar label
    colorbar_label = config.get('colorbar_label', f"{metric} ({statistic})")

    # Plot heatmap
    sns.heatmap(pivot_df,
                annot=True,
                fmt='.1f',
                cmap=cmap,
                ax=ax,
                cbar_kws={'label': colorbar_label},
                linewidths=HEATMAP_LINEWIDTH,
                linecolor=HEATMAP_LINECOLOR,
                square=True,
                vmin=pivot_df.min().min(),
                vmax=pivot_df.max().max(),
                cbar=True)

    # Manually add "N/A" text to NaN cells
    for i in range(n_rows):
        for j in range(n_cols):
            if mask.iloc[i, j]:
                # Add gray background rectangle
                rect = plt.Rectangle((j, i), 1, 1, fill=True,
                                    facecolor='lightgray', edgecolor='black', linewidth=HEATMAP_LINEWIDTH)
                ax.add_patch(rect)
                # Add "N/A" text
                ax.text(j + 0.5, i + 0.5, 'N/A',
                       ha='center', va='center', fontsize=DEFAULT_ANNOTATION_FONTSIZE,
                       fontweight=DEFAULT_FONTWEIGHT_BOLD)

    ax.set_xlabel(config['cols'].get('label', col_var), fontsize=DEFAULT_LABEL_FONTSIZE,
                 fontweight=DEFAULT_FONTWEIGHT_BOLD)
    ax.set_ylabel(config['rows'].get('label', row_var), fontsize=DEFAULT_LABEL_FONTSIZE,
                 fontweight=DEFAULT_FONTWEIGHT_BOLD)
    ax.set_title(config['title'], fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD,
                pad=DEFAULT_PAD)

    # Ensure all ticks are shown
    ax.set_xticks(np.arange(n_cols) + 0.5)
    ax.set_yticks(np.arange(n_rows) + 0.5)
    ax.set_xticklabels(pivot_df.columns, rotation=0, ha='center')
    ax.set_yticklabels(pivot_df.index, rotation=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_spider(df, config, output_path):
    """
    Generate spider/radar chart using pre-aggregated group statistics from Module 4.

    IMPORTANT: Expects df_groups filtered by group_id = 'G01'.
    Data format: group_level, indicator_id, mean (normalized values 0-1)

    DYNAMIC INDICATOR DETECTION: If config['axes'] is missing or set to 'auto',
    automatically pulls all indicators from config_indicators.json.
    """
    # Load indicator config for names
    try:
        indicators_path = CONFIG_DIR / CONFIG_INDICATORS_FILE
        with open(indicators_path, 'r') as f:
            indicators_config = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Indicators config file not found: {indicators_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in indicators config: {e}")
        raise

    # Create mapping of indicator_id to indicator_name
    ind_names = {ind['indicator_id']: ind['indicator_name']
                 for ind in indicators_config['indicators']}

    fig, ax = plt.subplots(figsize=SPIDER_FIGSIZE, subplot_kw=dict(projection='polar'))

    # DYNAMIC: Determine axes - either from config or auto-detect from indicator config
    if 'axes' not in config or config['axes'] == 'auto':
        # Automatically use ALL indicators from config
        axes_vars = [ind['indicator_id'] for ind in indicators_config['indicators']]
        print(f"    [INFO] Spider chart auto-detected {len(axes_vars)} indicators: {axes_vars}")
    else:
        # Use manually specified axes (for backward compatibility)
        axes_vars = config['axes']

    series_var = config['series']['variable']  # 'group_level' for G01 (contains system names)

    # Get unique group levels (system names)
    systems = sorted(df[series_var].unique())

    N = len(axes_vars)

    # Compute angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Collect all values first to find min/max
    all_values = []
    system_values = {}

    # Pivot data: group_level × indicator_id → mean values
    for system in systems:
        df_system = df[df[series_var] == system]

        values = []
        for ind_id in axes_vars:
            df_ind = df_system[df_system['indicator_id'] == ind_id]

            if not df_ind.empty:
                # Use normalized values if available, otherwise raw mean
                if 'mean_normalized' in df_ind.columns and pd.notna(df_ind['mean_normalized'].iloc[0]):
                    mean_value = df_ind['mean_normalized'].iloc[0]
                else:
                    mean_value = df_ind['mean'].iloc[0]
                values.append(mean_value)
                all_values.append(mean_value)
            else:
                values.append(0.0)
                all_values.append(0.0)

        system_values[system] = values

    # Use tab10 colormap which provides 10 distinct colors
    colors = plt.cm.tab10(np.linspace(0, 0.9, len(systems)))

    # Plot each system with different markers
    for idx, system in enumerate(systems):
        values = system_values[system]

        # Close the polygon
        values_closed = values + values[:1]

        # Plot line with unique marker style
        marker = MARKER_STYLES[idx % len(MARKER_STYLES)]
        color = colors[idx]

        ax.plot(angles, values_closed, marker=marker, linestyle='-', linewidth=ERROR_BAR_LINEWIDTH,
                label=system, markersize=SPIDER_MARKER_SIZE, color=color, markeredgewidth=1.5,
                markeredgecolor='white')

    # Set axis labels (short IDs only)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_vars, size=DEFAULT_ANNOTATION_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)

    # Set radial limits with fixed round numbers
    ax.set_ylim(SPIDER_R_MIN, SPIDER_R_MAX)

    # Create tick marks with nice round numbers
    ax.set_yticks(SPIDER_TICK_VALUES)
    ax.set_yticklabels([f'{v:.1f}' for v in SPIDER_TICK_VALUES], size=9)

    # Title and legend
    ax.set_title(config['title'], size=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=1.1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=DEFAULT_LEGEND_FONTSIZE,
              frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=DEFAULT_GRID_ALPHA)

    # Add indicator descriptions in a footer using standardized style
    indicator_items = [(ind_id, ind_names.get(ind_id, ind_id)) for ind_id in axes_vars]
    bottom_margin = create_footer_legend(fig, "Indicator Descriptions", indicator_items)

    plt.tight_layout(rect=[0, bottom_margin, 1, 1])
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


# ====================
# BATCH 2: Boxplot Functions
# ====================

def plot_boxplot(df, config, output_path):
    """Generate boxplot."""
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

    variable = config['variable']
    groups = config['groups']
    orientation = config.get('orientation', 'vertical')

    if orientation == 'vertical':
        sns.boxplot(data=df, x=groups, y=variable, ax=ax)
        ax.set_xlabel(groups)
        ax.set_ylabel(variable)
    else:
        sns.boxplot(data=df, y=groups, x=variable, ax=ax)
        ax.set_ylabel(groups)
        ax.set_xlabel(variable)

    ax.set_title(config['title'])

    plt.tight_layout()
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_boxplot_by_stations(df, config, output_path):
    """
    Generate boxplot visualization showing indicator distributions by number of stations.
    Creates 3 subplots (one for n=3, n=4, n=5 stations) with 6 boxplots each (IND01-IND06).
    Uses ALL 12 experiments (including infeasible ones).

    Args:
        df: Experiment dataframe (df_experiments_aggregated) with normalized indicator columns
        config: Visualization config
        output_path: Output file path
    """
    # Load indicator config for names
    try:
        indicators_path = CONFIG_DIR / CONFIG_INDICATORS_FILE
        with open(indicators_path, 'r') as f:
            indicators_config = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Indicators config file not found: {indicators_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in indicators config: {e}")
        raise

    ind_names = {ind['indicator_id']: ind['indicator_name']
                 for ind in indicators_config['indicators']}

    # Get indicators from config
    indicators = config['indicators']

    # Get unique station counts from data
    station_counts = sorted(df['num_stations'].unique())
    n_stations = len(station_counts)

    print(f"    [DEBUG] Station counts: {station_counts}")
    print(f"    [DEBUG] Total experiments: {len(df)}")

    # Create 1×3 subplot grid (horizontal layout)
    fig, axes = plt.subplots(1, n_stations, figsize=(18, 6))

    # Handle case where we have only 1 station count
    if n_stations == 1:
        axes = [axes]

    # Get y-axis limits from config
    y_min = config['y_axis'].get('min', -0.6)
    y_max = config['y_axis'].get('max', 1.4)
    y_label = config['y_axis'].get('label', 'Normalized Value')

    # Group name from config
    group_id = config.get('group_id', '')

    # For each station count
    for idx, n_stat in enumerate(station_counts):
        ax = axes[idx]

        # Filter experiments for this station count
        df_subset = df[df['num_stations'] == n_stat]
        n_experiments = len(df_subset)

        print(f"    [DEBUG] n={int(n_stat)} stations: {n_experiments} experiments")

        # Prepare data for boxplot: collect normalized values for each indicator
        boxplot_data = []
        boxplot_labels = []

        for ind_id in indicators:
            ind_col = f"{ind_id}_normalized"
            if ind_col in df_subset.columns:
                values = df_subset[ind_col].dropna().tolist()
                boxplot_data.append(values)
                boxplot_labels.append(ind_id)
            else:
                print(f"    [WARNING] Column {ind_col} not found in data")

        # Create boxplot
        bp = ax.boxplot(boxplot_data,
                       labels=boxplot_labels,
                       patch_artist=True,
                       widths=0.6,
                       showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red',
                                     markeredgecolor='black', markersize=6))

        # Color the boxes
        colors = plt.cm.Set3(range(len(boxplot_data)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(DEFAULT_ALPHA)

        # Formatting
        ax.set_xlabel('Indicators', fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(y_label, fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylim(y_min, y_max)
        ax.set_title(f"n={int(n_stat)} Stations ({n_experiments} experiments)",
                    fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, axis='y', linestyle='--', linewidth=0.5)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)
        ax.axhline(y=1, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)

        # Bold x-axis labels
        ax.tick_params(axis='x', labelsize=10)
        for label in ax.get_xticklabels():
            label.set_fontweight(DEFAULT_FONTWEIGHT_BOLD)

    # Overall title
    fig.suptitle(config['title'], fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.98)

    # Add indicator names as footer using standardized style
    indicator_items = [(ind_id, ind_names[ind_id]) for ind_id in indicators]
    bottom_margin = create_footer_legend(fig, "Indicator Descriptions", indicator_items, bottom_margin=0.18)

    plt.tight_layout(rect=[0, bottom_margin, 1, 0.96])
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_boxplot_by_automation(df, config, output_path):
    """
    Generate boxplot visualization showing indicator distributions by automation level.
    Creates dynamic subplots (one per automation level) with 6 boxplots each (IND01-IND06).
    Uses ALL 12 experiments (including infeasible ones).

    Args:
        df: Experiment dataframe (df_experiments_aggregated) with normalized indicator columns
        config: Visualization config with automation_mapping
        output_path: Output file path
    """
    # Load indicator config for names
    try:
        indicators_path = CONFIG_DIR / CONFIG_INDICATORS_FILE
        with open(indicators_path, 'r') as f:
            indicators_config = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Indicators config file not found: {indicators_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in indicators config: {e}")
        raise

    ind_names = {ind['indicator_id']: ind['indicator_name']
                 for ind in indicators_config['indicators']}

    # Get indicators from config
    indicators = config['indicators']

    # Get automation mapping from config
    automation_mapping = config['automation_mapping']

    # Map automation_degree to labels
    def map_automation_level(degree):
        for label, range_def in automation_mapping.items():
            if range_def['min'] <= degree <= range_def['max']:
                return label
        return 'unknown'

    df = df.copy()
    df['automation_label'] = df['automation_degree'].apply(map_automation_level)

    # Get unique automation labels from data (in defined order)
    defined_order = ['manual', 'low', 'medium', 'high']
    automation_labels = [label for label in defined_order if label in df['automation_label'].unique()]
    n_automation = len(automation_labels)

    print(f"    [DEBUG] Automation labels: {automation_labels}")
    print(f"    [DEBUG] Total experiments: {len(df)}")

    # Create 1×n subplot grid (horizontal layout)
    fig, axes = plt.subplots(1, n_automation, figsize=(6*n_automation, 6))

    # Handle case where we have only 1 automation level
    if n_automation == 1:
        axes = [axes]

    # Get y-axis limits from config
    y_min = config['y_axis'].get('min', -0.6)
    y_max = config['y_axis'].get('max', 1.4)
    y_label = config['y_axis'].get('label', 'Normalized Value')

    # Group name from config
    group_id = config.get('group_id', '')

    # For each automation level
    for idx, auto_label in enumerate(automation_labels):
        ax = axes[idx]

        # Filter experiments for this automation level
        df_subset = df[df['automation_label'] == auto_label]
        n_experiments = len(df_subset)

        print(f"    [DEBUG] {auto_label}: {n_experiments} experiments")

        # Prepare data for boxplot: collect normalized values for each indicator
        boxplot_data = []
        boxplot_labels = []

        for ind_id in indicators:
            ind_col = f"{ind_id}_normalized"
            if ind_col in df_subset.columns:
                values = df_subset[ind_col].dropna().tolist()
                boxplot_data.append(values)
                boxplot_labels.append(ind_id)
            else:
                print(f"    [WARNING] Column {ind_col} not found in data")

        # Create boxplot
        bp = ax.boxplot(boxplot_data,
                       labels=boxplot_labels,
                       patch_artist=True,
                       widths=0.6,
                       showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red',
                                     markeredgecolor='black', markersize=6))

        # Color the boxes
        colors = plt.cm.Set3(range(len(boxplot_data)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(DEFAULT_ALPHA)

        # Formatting
        ax.set_xlabel('Indicators', fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(y_label, fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylim(y_min, y_max)
        ax.set_title(f"{auto_label.capitalize()} Automation ({n_experiments} experiments)",
                    fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, axis='y', linestyle='--', linewidth=0.5)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)
        ax.axhline(y=1, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)

        # Bold x-axis labels
        ax.tick_params(axis='x', labelsize=10)
        for label in ax.get_xticklabels():
            label.set_fontweight(DEFAULT_FONTWEIGHT_BOLD)

    # Overall title
    fig.suptitle(config['title'], fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.98)

    # Add indicator names as footer using standardized style
    indicator_items = [(ind_id, ind_names[ind_id]) for ind_id in indicators]
    bottom_margin = create_footer_legend(fig, "Indicator Descriptions", indicator_items, bottom_margin=0.18)

    plt.tight_layout(rect=[0, bottom_margin, 1, 0.96])
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_boxplot_by_product_mix(df, config, output_path):
    """
    Generate boxplot visualization showing indicator distributions by product mix.
    Creates dynamic subplots (one per product mix) with 6 boxplots each (IND01-IND06).
    Uses ALL 12 experiments (including infeasible ones).

    Args:
        df: Experiment dataframe (df_experiments_aggregated) with normalized indicator columns
        config: Visualization config with product_mix_order
        output_path: Output file path
    """
    # Load indicator config for names
    try:
        indicators_path = CONFIG_DIR / CONFIG_INDICATORS_FILE
        with open(indicators_path, 'r') as f:
            indicators_config = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Indicators config file not found: {indicators_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in indicators config: {e}")
        raise

    ind_names = {ind['indicator_id']: ind['indicator_name']
                 for ind in indicators_config['indicators']}

    # Get indicators from config
    indicators = config['indicators']

    # Get product mix order from config (or detect from data)
    if 'product_mix_order' in config:
        defined_order = config['product_mix_order']
        product_mixes = [mix for mix in defined_order if mix in df['product_mix'].unique()]
    else:
        product_mixes = sorted(df['product_mix'].unique())

    n_mixes = len(product_mixes)

    print(f"    [DEBUG] Product mixes: {product_mixes}")
    print(f"    [DEBUG] Total experiments: {len(df)}")

    # Create 1×n subplot grid (horizontal layout)
    fig, axes = plt.subplots(1, n_mixes, figsize=(6*n_mixes, 6))

    # Handle case where we have only 1 product mix
    if n_mixes == 1:
        axes = [axes]

    # Get y-axis limits from config
    y_min = config['y_axis'].get('min', -0.6)
    y_max = config['y_axis'].get('max', 1.4)
    y_label = config['y_axis'].get('label', 'Normalized Value')

    # Group name from config
    group_id = config.get('group_id', '')

    # For each product mix
    for idx, mix in enumerate(product_mixes):
        ax = axes[idx]

        # Filter experiments for this product mix
        df_subset = df[df['product_mix'] == mix]
        n_experiments = len(df_subset)

        print(f"    [DEBUG] {mix}: {n_experiments} experiments")

        # Prepare data for boxplot: collect normalized values for each indicator
        boxplot_data = []
        boxplot_labels = []

        for ind_id in indicators:
            ind_col = f"{ind_id}_normalized"
            if ind_col in df_subset.columns:
                values = df_subset[ind_col].dropna().tolist()
                boxplot_data.append(values)
                boxplot_labels.append(ind_id)
            else:
                print(f"    [WARNING] Column {ind_col} not found in data")

        # Create boxplot
        bp = ax.boxplot(boxplot_data,
                       labels=boxplot_labels,
                       patch_artist=True,
                       widths=0.6,
                       showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red',
                                     markeredgecolor='black', markersize=6))

        # Color the boxes
        colors = plt.cm.Set3(range(len(boxplot_data)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(DEFAULT_ALPHA)

        # Formatting
        ax.set_xlabel('Indicators', fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(y_label, fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylim(y_min, y_max)

        # Clean up mix name for title (remove 'mix_' prefix)
        mix_label = mix.replace('mix_', '').upper()
        ax.set_title(f"{mix_label} Mix ({n_experiments} experiments)",
                    fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, axis='y', linestyle='--', linewidth=0.5)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)
        ax.axhline(y=1, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=1)

        # Bold x-axis labels
        ax.tick_params(axis='x', labelsize=10)
        for label in ax.get_xticklabels():
            label.set_fontweight(DEFAULT_FONTWEIGHT_BOLD)

    # Overall title
    fig.suptitle(config['title'], fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.98)

    # Add indicator names as footer using standardized style
    indicator_items = [(ind_id, ind_names[ind_id]) for ind_id in indicators]
    bottom_margin = create_footer_legend(fig, "Indicator Descriptions", indicator_items, bottom_margin=0.18)

    plt.tight_layout(rect=[0, bottom_margin, 1, 0.96])
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


# ====================
# BATCH 3: Product Depth Functions
# ====================

def plot_product_depth(df, config, output_path):
    """
    Generate product-specific disassembly depth scatter plots.
    Creates a 2×2 subplot layout with one plot per product type.
    Uses scatter plots with branch-specific markers (no line connections).
    """
    # Get unique product types
    product_types = sorted(df['product_type'].unique())

    # Create 2×2 subplot layout
    fig, axes = plt.subplots(2, 2, figsize=XLARGE_FIGSIZE)
    axes = axes.flatten()

    # Use tab10 colormap for systems
    systems = sorted(df['system'].unique())
    colors = plt.cm.tab10(np.linspace(0, 0.9, len(systems)))

    # Define marker styles for branches
    branch_markers = BRANCH_MARKERS

    for idx, product_type in enumerate(product_types):
        if idx >= 4:  # Safety check
            break

        ax = axes[idx]
        df_product = df[df['product_type'] == product_type]

        x_var = config['x_axis']['variable']
        y_var = config['y_axis']['variable']

        # Track which system-branch combinations have been labeled
        labeled_combinations = set()

        # Plot each system within this product
        for sys_idx, system in enumerate(systems):
            df_sys = df_product[df_product['system'] == system]

            if df_sys.empty:
                continue

            color = colors[sys_idx]

            # Group by branch_path to apply different markers
            for branch in df_sys['branch_path'].unique():
                df_branch = df_sys[df_sys['branch_path'] == branch]

                if df_branch.empty:
                    continue

                # Sort by parallel_position
                df_branch = df_branch.sort_values('parallel_position')

                marker = branch_markers.get(branch, 'o')

                # Create label only once per system
                label = system if (system, branch) not in labeled_combinations and branch == 'main' else ""
                if label:
                    labeled_combinations.add((system, branch))

                # Scatter plot with branch-specific marker
                ax.scatter(
                    df_branch[x_var],
                    df_branch[y_var],
                    marker=marker,
                    color=color,
                    s=DEFAULT_MARKER_SIZE,
                    label=label,
                    alpha=0.8,
                    edgecolors='black',
                    linewidths=1.0,
                    zorder=3
                )

                # Add error bars if available
                if 'error_bars' in config and config['error_bars']['variable'] in df_branch.columns:
                    err_var = config['error_bars']['variable']
                    ax.errorbar(
                        df_branch[x_var],
                        df_branch[y_var],
                        yerr=df_branch[err_var],
                        fmt='none',  # No line, only error bars
                        color=color,
                        alpha=0.4,
                        capsize=3,
                        capthick=1,
                        zorder=2
                    )

        # Formatting
        ax.set_xlabel(config['x_axis'].get('label', x_var), fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(config['y_axis'].get('label', y_var), fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_title(f"{product_type.upper().replace('CAR_', '')}", fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)

        # Legend for systems
        if ax.get_legend_handles_labels()[0]:  # Check if there are any labels
            ax.legend(loc='upper right', fontsize=8, frameon=True, fancybox=True, shadow=True,
                     title='Systems', title_fontsize=9)

        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, linestyle='--', linewidth=0.5)
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5, zorder=1)  # Zero line

        # Add component info box
        create_component_info_box(ax, df_product, product_type)

        # Set x-axis to show integer step numbers
        if x_var == 'step_number' or x_var == 'parallel_position':
            x_min = df_product['parallel_position'].min()
            x_max = df_product['parallel_position'].max()
            ax.set_xlim(x_min - 0.5, x_max + 0.5)
            ax.set_xticks(range(int(x_min), int(x_max) + 1))

    # Hide unused subplots
    for idx in range(len(product_types), 4):
        axes[idx].set_visible(False)

    # Overall title
    fig.suptitle(config['title'], fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.995)

    plt.tight_layout()
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_product_depth_by_automation(df, config, output_dir):
    """
    Generate product-specific disassembly depth scatter plots.
    Creates 1 SVG file containing 4 subplots (one per system).
    Each subplot shows product lines based on config specification.
    Data is averaged across all automation levels.

    Args:
        df: Dataframe with trajectory data
        config: Visualization config
        output_dir: Directory to save output files

    Returns:
        List of generated file paths
    """
    # Filter by product_types if specified in config, otherwise load from mappings
    if 'product_types' in config:
        df = df[df['product_type'].isin(config['product_types'])].copy()
        product_types = config['product_types']
    else:
        product_type_config = load_product_types()
        product_types = product_type_config['available']

    # Get unique systems
    systems = sorted([s for s in df['system'].unique() if pd.notna(s)])

    # Define colors for product types (use tab10 colormap)
    product_type_colors = get_product_type_colors()

    # Define marker styles for branches
    branch_markers = BRANCH_MARKERS

    x_var = config['x_axis']['variable']
    y_var = config['y_axis']['variable']
    err_var = config.get('error_bars', {}).get('variable', None)

    # Calculate dodge offset for separating overlapping points
    # Each product type gets a small horizontal offset proportional to its index
    n_product_types = len(product_types)
    dodge_width = 0.25  # Total spread width (adjustable)
    product_type_offsets = {}
    for idx, ptype in enumerate(product_types):
        # Center the offsets around 0
        offset = (idx - (n_product_types - 1) / 2) * (dodge_width / (n_product_types - 1)) if n_product_types > 1 else 0
        product_type_offsets[ptype] = offset

    generated_files = []

    # Create figure with gridspec layout (2 rows for plots + 1 row for table)
    fig = plt.figure(figsize=XXLARGE_FIGSIZE)  # Increased height for table
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.6], hspace=0.25, wspace=0.25)

    # Create subplots for the 2x2 grid (top two rows)
    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1])
    ]

    for sys_idx, system in enumerate(systems):
        if sys_idx >= 4:  # Safety check
            break

        ax = axes[sys_idx]
        df_sys = df[df['system'] == system]

        if df_sys.empty:
            ax.set_visible(False)
            continue

        # Get system information
        system_info = get_system_info(system)

        # Create step_id → numeric position mapping for this system
        # Use all unique step_ids across all products to ensure consistency
        all_step_ids = df_sys[x_var].unique().tolist()
        all_step_ids_sorted = sorted(all_step_ids, key=sort_key_for_step_id)
        step_to_pos = {step: idx for idx, step in enumerate(all_step_ids_sorted)}

        # Track which product types have been labeled for legend
        labeled_product_types = set()

        # Plot each product type within this system
        for product_type in product_types:
            df_type = df_sys[df_sys['product_type'] == product_type]

            if df_type.empty:
                continue

            color = product_type_colors[product_type]

            # Create label for legend (e.g., car_hd → HD)
            label = product_type.replace('car_', '').upper() if product_type not in labeled_product_types else ""
            if label:
                labeled_product_types.add(product_type)

            # Map step_id to numeric position
            numeric_positions = df_type[x_var].map(step_to_pos)

            # Get offset for this product type to avoid overlapping
            x_offset = product_type_offsets[product_type]
            x_positions = numeric_positions + x_offset

            # Scatter plot
            ax.scatter(
                x_positions,
                df_type[y_var],
                marker='o',
                color=color,
                s=DEFAULT_MARKER_SIZE,
                label=label,
                alpha=0.8,
                edgecolors='black',
                linewidths=1.0,
                zorder=3
            )

            # Add error bars if available
            if err_var and err_var in df_type.columns:
                ax.errorbar(
                    x_positions,
                    df_type[y_var],
                    yerr=df_type[err_var],
                    fmt='none',
                    color=color,
                    alpha=0.4,
                    capsize=3,
                    capthick=1,
                    zorder=2
                )

        # Formatting
        ax.set_xlabel(config['x_axis'].get('label', x_var), fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(config['y_axis'].get('label', y_var), fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)

        # Title with system info
        system_title = f"{system.upper()}\n({system_info['type']}, {system_info['division']}, {system_info['num_stations']} stations)"
        ax.set_title(system_title, fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)

        # Legend for product types
        if ax.get_legend_handles_labels()[0]:  # Check if there are any labels
            ax.legend(loc='upper right', fontsize=9, frameon=True, fancybox=True, shadow=True,
                     title='Product Type', title_fontsize=10)

        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, linestyle='--', linewidth=0.5)
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5, zorder=1)  # Zero line

        # Set x-axis to show step_ids
        ax.set_xlim(-0.5, len(all_step_ids_sorted) - 0.5)
        ax.set_xticks(range(len(all_step_ids_sorted)))
        ax.set_xticklabels(all_step_ids_sorted, fontsize=10, fontweight=DEFAULT_FONTWEIGHT_BOLD)

    # Hide unused subplots
    for idx in range(len(systems), 4):
        axes[idx].set_visible(False)

    # Overall title
    title_text = config['title']
    fig.suptitle(title_text, fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.98)

    # Add component mapping table footer showing all product types
    try:
        paths_file = ATTRIBUTES_DIR / ATTRIBUTES_PATHS_FILE
        with open(paths_file, 'r') as f:
            paths_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Paths file not found: {paths_file}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in paths file: {e}")
        raise

    # Create table legend in the bottom row (gridspec row 2, spanning both columns)
    create_step_table_legend(fig, axes, paths_data)

    # Save figure (gridspec handles layout, no tight_layout needed)
    output_filename = config['output_filename']
    output_path = output_dir / output_filename

    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()

    generated_files.append(output_filename)
    print(f"    [OK] Saved: {output_filename}")

    return generated_files


def plot_product_depth_by_automation_bars(df, config, output_dir):
    """
    Generate product-specific disassembly depth bar charts.
    Creates 1 SVG file containing 4 subplots (one per system).
    Each subplot shows grouped bars per step based on config specification.
    Data is averaged across all automation levels.

    Args:
        df: Dataframe with trajectory data
        config: Visualization config
        output_dir: Directory to save output files

    Returns:
        List of generated file paths
    """
    # Filter by product_types if specified in config, otherwise load from mappings
    if 'product_types' in config:
        df = df[df['product_type'].isin(config['product_types'])].copy()
        product_types = config['product_types']
    else:
        product_type_config = load_product_types()
        product_types = product_type_config['available']

    # Get unique systems
    systems = sorted([s for s in df['system'].unique() if pd.notna(s)])

    # Define colors for product types
    product_type_colors = get_product_type_colors()

    # Load disassembly paths and build component ordering lookup
    try:
        paths_file = ATTRIBUTES_DIR / ATTRIBUTES_PATHS_FILE
        with open(paths_file, 'r') as f:
            paths_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Paths file not found: {paths_file}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in paths file: {e}")
        raise
    component_ordering = build_component_ordering_lookup(paths_data)

    x_var = config['x_axis']['variable']
    y_var = config['y_axis']['variable']

    generated_files = []

    # Calculate global y-axis limits
    global_y_min = df[y_var].min()
    global_y_max = df[y_var].max()

    # Add some padding (10% on each side)
    y_range = global_y_max - global_y_min
    global_y_min = global_y_min - 0.1 * y_range
    global_y_max = global_y_max + 0.1 * y_range

    # Create figure with gridspec layout (2 rows for plots + 1 row for table)
    fig = plt.figure(figsize=(20, 20))  # Increased height for table
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.6], hspace=0.25, wspace=0.25)

    # Create subplots for the 2x2 grid (top two rows)
    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1])
    ]

    for sys_idx, system in enumerate(systems):
        if sys_idx >= 4:
            break

        ax = axes[sys_idx]
        df_sys = df[df['system'] == system]

        if df_sys.empty:
            ax.set_visible(False)
            continue

        # Get system information
        system_info = get_system_info(system)

        # Create step_id → numeric position mapping for this system
        all_step_ids = df_sys[x_var].unique().tolist()
        all_step_ids_sorted = sorted(all_step_ids, key=sort_key_for_step_id)
        step_to_pos = {step: idx for idx, step in enumerate(all_step_ids_sorted)}

        # Set up bar positions
        n_types = len(product_types)
        bar_width = 0.15
        position_indices = np.arange(len(all_step_ids_sorted))

        # Track which product types have data for legend
        has_data = {ptype: False for ptype in product_types}

        # Plot bars for each product type
        for type_idx, product_type in enumerate(product_types):
            df_type = df_sys[df_sys['product_type'] == product_type]

            if df_type.empty:
                continue

            has_data[product_type] = True
            base_color = product_type_colors[product_type]

            # Plot each step_id with stacked components
            for pos_idx, step_id in enumerate(all_step_ids_sorted):
                df_step = df_type[df_type[x_var] == step_id]

                if df_step.empty:
                    continue

                # Get components for this step
                components_in_step = df_step['component'].unique().tolist()

                # Order components according to JSON (fallback to alphabetical if not found)
                key = (product_type, step_id)
                ordered_components = component_ordering.get(key, sorted(components_in_step))

                # Filter to only components present in data
                ordered_components = [c for c in ordered_components if c in components_in_step]

                # Generate color shades for stacking
                n_components = len(ordered_components)
                color_shades = generate_color_shades(base_color, n_components)

                # Calculate x position for this bar
                x_pos = position_indices[pos_idx] + (type_idx - n_types/2 + 0.5) * bar_width

                # Stack bars by component
                bottom = 0
                for comp_idx, component in enumerate(ordered_components):
                    comp_row = df_step[df_step['component'] == component]

                    if comp_row.empty:
                        continue

                    y_val = comp_row[y_var].iloc[0]

                    ax.bar(x_pos, y_val, bar_width,
                          bottom=bottom,
                          color=color_shades[comp_idx],
                          edgecolor='black',
                          linewidth=1.5)

                    bottom += y_val

        # Formatting
        ax.set_xticks(position_indices)
        ax.set_xticklabels(all_step_ids_sorted, fontsize=DEFAULT_TICK_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_xlabel(config['x_axis']['label'], fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(config['y_axis']['label'], fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylim(global_y_min, global_y_max)  # Use global y-axis limits
        ax.set_title(f"{system.upper()}\n({system_info['type']}, {system_info['division']}, "
                    f"{system_info['num_stations']} stations)",
                    fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, axis='y', linestyle='--', linewidth=0.5)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.7)

        # Create legend with only product types that have data
        legend_handles = []
        legend_labels = []
        for ptype in product_types:
            if has_data[ptype]:
                legend_handles.append(plt.Rectangle((0,0),1,1,
                                                   facecolor=product_type_colors[ptype],
                                                   edgecolor='black', alpha=DEFAULT_ALPHA))
                legend_labels.append(ptype.replace('car_', '').upper())

        if legend_handles:
            ax.legend(legend_handles, legend_labels,
                     loc='upper left', fontsize=10, frameon=True,
                     fancybox=True, shadow=True, title='Product Type')

    # Overall title
    fig.suptitle(f"{config['title']}",
                fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.985)

    # Create table legend in the bottom row (gridspec row 2, spanning both columns)
    # (paths_data already loaded earlier for component ordering)
    create_step_table_legend(fig, axes, paths_data)

    # Save figure (gridspec handles layout, no tight_layout needed)
    output_filename = config['output_filename']
    output_path = output_dir / output_filename

    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()

    generated_files.append(output_filename)
    print(f"    [OK] Saved: {output_filename}")

    return generated_files


def plot_product_depth_bars_simple(df, config, output_dir):
    """
    Generate simple (non-stacked) bar charts for product-specific disassembly depth.
    Creates 1 SVG file containing 4 subplots (one per system).
    Each subplot shows grouped bars per step (one bar per product type).
    Data shows aggregated total profit per step (not component-level detail).

    Args:
        df: Dataframe with step-aggregated data (depth_step_aggregated)
        config: Visualization config
        output_dir: Directory to save output files

    Returns:
        List of generated file paths
    """
    # Filter by product_types if specified in config, otherwise load from mappings
    if 'product_types' in config:
        df = df[df['product_type'].isin(config['product_types'])].copy()
        product_types = config['product_types']
    else:
        product_type_config = load_product_types()
        product_types = product_type_config['available']

    # Get unique systems
    systems = sorted([s for s in df['system'].unique() if pd.notna(s)])

    # Define colors for product types
    product_type_colors = get_product_type_colors()

    # Load disassembly paths and build component ordering lookup
    try:
        paths_file = ATTRIBUTES_DIR / ATTRIBUTES_PATHS_FILE
        with open(paths_file, 'r') as f:
            paths_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Paths file not found: {paths_file}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in paths file: {e}")
        raise

    x_var = config['x_axis']['variable']
    y_var = config['y_axis']['variable']

    generated_files = []

    # Calculate global y-axis limits
    global_y_min = df[y_var].min()
    global_y_max = df[y_var].max()

    # Add some padding (10% on each side)
    y_range = global_y_max - global_y_min
    global_y_min = global_y_min - 0.1 * y_range
    global_y_max = global_y_max + 0.1 * y_range

    # Create figure with gridspec layout (2 rows for plots + 1 row for table)
    fig = plt.figure(figsize=(20, 20))
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.6], hspace=0.25, wspace=0.25)

    # Create subplots for the 2x2 grid (top two rows)
    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1])
    ]

    for sys_idx, system in enumerate(systems):
        if sys_idx >= 4:
            break

        ax = axes[sys_idx]
        df_sys = df[df['system'] == system]

        if df_sys.empty:
            ax.set_visible(False)
            continue

        # Get system information
        system_info = get_system_info(system)

        # Create step_id → numeric position mapping for this system
        all_step_ids = df_sys[x_var].unique().tolist()
        all_step_ids_sorted = sorted(all_step_ids, key=sort_key_for_step_id)
        step_to_pos = {step: idx for idx, step in enumerate(all_step_ids_sorted)}

        # Set up bar positions
        n_types = len(product_types)
        bar_width = 0.15
        position_indices = np.arange(len(all_step_ids_sorted))

        # Track which product types have data for legend
        has_data = {ptype: False for ptype in product_types}

        # Plot bars for each product type (simple grouped bars, no stacking)
        for type_idx, product_type in enumerate(product_types):
            df_type = df_sys[df_sys['product_type'] == product_type]

            if df_type.empty:
                continue

            has_data[product_type] = True
            color = product_type_colors[product_type]

            # Plot each step_id
            for pos_idx, step_id in enumerate(all_step_ids_sorted):
                df_pos = df_type[df_type[x_var] == step_id]

                if df_pos.empty:
                    continue

                # Get aggregated value for this step (total across all components)
                y_val = df_pos[y_var].iloc[0]

                # Calculate x position for this bar
                x_pos = position_indices[pos_idx] + (type_idx - n_types/2 + 0.5) * bar_width

                # Plot simple bar
                ax.bar(x_pos, y_val, bar_width,
                      color=color, alpha=DEFAULT_ALPHA,
                      edgecolor='black', linewidth=1.5)

        # Formatting
        ax.set_xticks(position_indices)
        ax.set_xticklabels(all_step_ids_sorted, fontsize=DEFAULT_TICK_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_xlabel(config['x_axis']['label'], fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(config['y_axis']['label'], fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylim(global_y_min, global_y_max)
        ax.set_title(f"{system.upper()}\n({system_info['type']}, {system_info['division']}, "
                    f"{system_info['num_stations']} stations)",
                    fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, axis='y', linestyle='--', linewidth=0.5)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.7)

        # Create legend with only product types that have data
        legend_handles = []
        legend_labels = []
        for ptype in product_types:
            if has_data[ptype]:
                legend_handles.append(plt.Rectangle((0,0),1,1,
                                                   facecolor=product_type_colors[ptype],
                                                   edgecolor='black', alpha=DEFAULT_ALPHA))
                legend_labels.append(ptype.replace('car_', '').upper())

        if legend_handles:
            ax.legend(legend_handles, legend_labels,
                     loc='upper left', fontsize=10, frameon=True,
                     fancybox=True, shadow=True, title='Product Type')

    # Overall title
    fig.suptitle(f"{config['title']}",
                fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.985)

    # Create table legend in the bottom row
    create_step_table_legend(fig, axes, paths_data)

    # Save figure
    output_filename = config['output_filename']
    output_path = output_dir / output_filename

    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()

    generated_files.append(output_filename)
    print(f"    [OK] Saved: {output_filename}")

    return generated_files


# ====================
# BATCH 4: Line and Bar Variants
# ====================

def plot_line_faceted(df, config, output_path):
    """
    Generate faceted line chart - one subplot per indicator.
    Used for VIZ16 (Automation Impact on All Indicators).
    """
    x_var = config['x_axis']['variable']
    y_var = config['y_axis']['variable']
    facet_var = config['facet']['variable']
    ncols = config['facet'].get('ncols', 3)

    # Get unique facet values (indicators)
    facet_values = sorted(df[facet_var].unique())
    n_facets = len(facet_values)
    nrows = (n_facets + ncols - 1) // ncols  # Ceiling division

    # Load indicator config for names
    try:
        indicators_path = CONFIG_DIR / CONFIG_INDICATORS_FILE
        with open(indicators_path, 'r') as f:
            indicators_config = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Indicators config file not found: {indicators_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in indicators config: {e}")
        raise

    ind_names = {ind['indicator_id']: ind['indicator_name']
                 for ind in indicators_config['indicators']}
    ind_units = {ind['indicator_id']: ind.get('unit', '')
                 for ind in indicators_config['indicators']}

    # Create figure with subplots
    fig, axes = plt.subplots(nrows, ncols, figsize=(6*ncols, 5*nrows))
    if n_facets == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    # Define automation level ordering
    automation_order = ['manual', 'low', 'medium', 'high']

    # Plot each indicator in its own subplot
    for idx, indicator_id in enumerate(facet_values):
        ax = axes[idx]
        df_facet = df[df[facet_var] == indicator_id].copy()

        if df_facet.empty:
            ax.set_visible(False)
            continue

        # Ensure proper ordering by automation level
        df_facet['automation_order'] = df_facet[x_var].map(
            {level: i for i, level in enumerate(automation_order)}
        )
        df_facet = df_facet.sort_values('automation_order')

        # Plot line with markers
        ax.plot(
            df_facet[x_var],
            df_facet[y_var],
            marker='o',
            color=plt.cm.viridis(idx / max(1, n_facets - 1)),
            linewidth=2.5,
            markersize=8,
            alpha=0.8
        )

        # Add error bars if configured
        if 'error_bars' in config and config['error_bars']['variable'] in df_facet.columns:
            error_var = config['error_bars']['variable']
            ax.errorbar(
                df_facet[x_var],
                df_facet[y_var],
                yerr=df_facet[error_var],
                fmt='none',
                ecolor=plt.cm.viridis(idx / max(1, n_facets - 1)),
                alpha=0.3,
                capsize=ERROR_BAR_CAPSIZE
            )

        # Formatting
        indicator_name = ind_names.get(indicator_id, indicator_id)
        unit = ind_units.get(indicator_id, '')
        unit_str = f" ({unit})" if unit else ""

        ax.set_title(f"{indicator_name}{unit_str}", fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_xlabel(config['x_axis'].get('label', x_var), fontsize=DEFAULT_FONT_SIZE)
        ax.set_ylabel(config['y_axis'].get('label', y_var) + unit_str, fontsize=DEFAULT_FONT_SIZE)
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, linestyle='--', linewidth=0.5)

        # Rotate x-axis labels if they're text
        ax.tick_params(axis='x', rotation=45)

    # Hide unused subplots
    for idx in range(n_facets, len(axes)):
        axes[idx].set_visible(False)

    # Overall title
    fig.suptitle(config['title'], fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.995)

    plt.tight_layout()
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


def plot_bar_grouped(df, config, output_path):
    """Generate grouped vertical bar chart with multiple series."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Set white background
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    x_var = config['x_axis']['variable']
    x_label = config['x_axis'].get('label', x_var)
    y_label = config['y_axis'].get('label', 'Value')
    series_configs = config['series']

    # Get unique x values
    x_values = df[x_var].tolist()
    x_pos = np.arange(len(x_values))

    # Bar width and spacing
    n_series = len(series_configs)
    width = 0.8 / n_series

    # Support custom color palette (default: tab10)
    color_palette = config.get('color_palette', 'tab10')
    if color_palette == 'Set2':
        colors = plt.cm.Set2(np.linspace(0, 0.9, n_series))
    elif color_palette == 'RdYlGn':
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, n_series))
    elif color_palette == 'YlGnBu':
        colors = plt.cm.YlGnBu(np.linspace(0.3, 0.9, n_series))
    elif color_palette == 'YlGnBu_r':
        colors = plt.cm.YlGnBu_r(np.linspace(0.3, 0.9, n_series))
    else:
        colors = plt.cm.tab10(np.linspace(0, 0.9, n_series))

    # Plot each series
    for idx, series_config in enumerate(series_configs):
        series_var = series_config['variable']
        series_label = series_config.get('label', series_var)
        series_color = colors[idx]

        values = df[series_var].tolist()
        offset = (idx - n_series/2 + 0.5) * width

        ax.bar(x_pos + offset, values, width, label=series_label, color=series_color)

    # Set labels and formatting
    ax.set_xlabel(x_label, fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
    ax.set_ylabel(y_label, fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
    ax.set_title(config['title'], fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=DEFAULT_PAD)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_values, rotation=45, ha='right')

    # Show legend only if not disabled
    if not config.get('hide_legend', False):
        ax.legend(loc='upper left', fontsize=DEFAULT_LEGEND_FONTSIZE)

    # Show grid only if not disabled
    if not config.get('hide_grid', False):
        ax.grid(axis='y', alpha=DEFAULT_GRID_ALPHA)
    else:
        # Explicitly turn off all gridlines
        ax.grid(False)

    # Add secondary legend if requested
    if 'legend' in config:
        legend_config = config['legend']
        if legend_config.get('show_system') or legend_config.get('show_product_mix'):
            # Create experiment details text for legend box
            experiment_lines = []
            for idx, row in df.iterrows():
                parts = []
                if legend_config.get('show_system'):
                    parts.append(f"System: {row.get('system', 'N/A')}")
                if legend_config.get('show_product_mix'):
                    parts.append(f"Mix: {row.get('product_mix', 'N/A').replace('mix_', '')}")
                experiment_lines.append(f"{row[x_var]}: {', '.join(parts)}")

            legend_text = "Experiment Details\n" + '\n'.join(experiment_lines)

            # Add as text box to the right of the plot
            fig.text(1.02, 0.5, legend_text, ha='left', va='center',
                    transform=ax.transAxes,
                    fontsize=9, family='sans-serif',
                    bbox=dict(boxstyle='round,pad=0.6',
                             facecolor='white',
                             edgecolor='gray',
                             linewidth=1.0,
                             alpha=1.0))

    plt.tight_layout()
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight', facecolor='white')
    plt.close()


# ====================
# BATCH 5: Cumulative Profit and System Grid Functions
# ====================

def plot_cumulative_profit_curve(df, config, output_dir):
    """
    Generate cumulative profit scatter plots with system baseline.
    Creates 1 SVG file containing subplots (one per system).
    Each subplot shows scatter points for each product type.
    Data is averaged across all automation levels.

    Config options:
    - 'systems': List of systems to display (default: all systems)
    - 'show_table': Whether to show component mapping table (default: true)

    Args:
        df: Dataframe with trajectory profit data
        config: Visualization config
        output_dir: Directory to save output files

    Returns:
        List of generated file paths
    """
    # Filter by product_types if specified in config, otherwise load from mappings
    if 'product_types' in config:
        df = df[df['product_type'].isin(config['product_types'])].copy()
        product_types = config['product_types']
    else:
        product_type_config = load_product_types()
        product_types = product_type_config['available']

    # Filter by systems if specified in config (for publication figures)
    if 'systems' in config:
        df = df[df['system'].isin(config['systems'])].copy()
        systems = config['systems']
    else:
        systems = sorted([s for s in df['system'].unique() if pd.notna(s)])

    # Check if table should be shown (default: true for backward compatibility)
    show_table = config.get('show_table', True)

    # Support custom color palette (default: tab10)
    color_palette = config.get('color_palette', 'tab10')
    product_type_config = load_product_types()

    # Generate colors dynamically based on product types
    product_type_colors = {}
    if color_palette == 'Set2':
        for pt, color_spec in product_type_config['colors'].items():
            product_type_colors[pt] = plt.cm.Set2(color_spec['index'])
    elif color_palette == 'RdYlGn':
        color_values = [0.2, 0.4, 0.6, 0.8]
        for i, pt in enumerate(product_type_config['available']):
            product_type_colors[pt] = plt.cm.RdYlGn(color_values[i % len(color_values)])
    elif color_palette == 'YlGnBu':
        color_values = [0.3, 0.5, 0.7, 0.9]
        for i, pt in enumerate(product_type_config['available']):
            product_type_colors[pt] = plt.cm.YlGnBu(color_values[i % len(color_values)])
    else:
        # Default: use colormap from config
        product_type_colors = get_product_type_colors()

    x_var = config['x_axis']['variable']
    y_var = config['y_axis']['variable']

    generated_files = []

    # Calculate global y-axis limits
    global_y_min = df[y_var].min()
    global_y_max = df[y_var].max()

    # Add some padding (15% on each side for better visual spacing)
    y_range = global_y_max - global_y_min
    global_y_min = global_y_min - 0.15 * y_range
    global_y_max = global_y_max + 0.15 * y_range

    # Determine layout based on number of systems and table display
    n_systems = len(systems)

    if n_systems == 1 and not show_table:
        # Single system without table: simple single plot
        fig, ax = plt.subplots(figsize=(10, 8))
        axes = [ax]
    elif n_systems == 1 and show_table:
        # Single system with table: 2 rows (1 plot + 1 table)
        fig = plt.figure(figsize=(10, 12))
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 0.4], hspace=0.25)
        axes = [fig.add_subplot(gs[0, 0])]
    elif show_table:
        # Multiple systems with table: original layout
        fig = plt.figure(figsize=(20, 20))
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.6], hspace=0.25, wspace=0.25)
        axes = [
            fig.add_subplot(gs[0, 0]),
            fig.add_subplot(gs[0, 1]),
            fig.add_subplot(gs[1, 0]),
            fig.add_subplot(gs[1, 1])
        ]
    else:
        # Multiple systems without table: 2x2 grid only
        fig, axes_grid = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes_grid.flatten()

    for sys_idx, system in enumerate(systems):
        if sys_idx >= 4:
            break

        ax = axes[sys_idx]
        df_sys = df[df['system'] == system]

        if df_sys.empty:
            ax.set_visible(False)
            continue

        # Get system information
        system_info = get_system_info(system)

        # Create step_id → numeric position mapping for this system
        all_step_ids = df_sys[x_var].unique().tolist()
        all_step_ids_sorted = sorted(all_step_ids, key=sort_key_for_step_id)
        step_to_pos = {step: idx for idx, step in enumerate(all_step_ids_sorted)}

        # Track which product types have data for legend
        has_data = {ptype: False for ptype in product_types}

        # Calculate horizontal offset for each product type
        n_types = len(product_types)
        offset_scale = config.get('offset_scale', 0.08)  # Horizontal offset to separate points

        # Load disassembly paths for connecting lines
        try:
            paths_file = ATTRIBUTES_DIR / ATTRIBUTES_PATHS_FILE
            with open(paths_file, 'r') as f:
                paths_data = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Paths file not found: {paths_file}")
            raise
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in paths file: {e}")
            raise

        # Plot scatter points and connecting lines for each product type
        for type_idx, product_type in enumerate(product_types):
            df_type = df_sys[df_sys['product_type'] == product_type]

            # Exclude baseline branch - only plot main disassembly path
            df_type = df_type[df_type['branch_id'] != 'baseline']

            if df_type.empty:
                continue

            has_data[product_type] = True
            color = product_type_colors[product_type]

            # Calculate horizontal offset for this product type
            offset = (type_idx - n_types/2 + 0.5) * offset_scale

            # Collect x,y values for each step with step_id mapping
            step_positions = {}  # step_id -> (x_pos, y_val)

            for step_id in all_step_ids_sorted:
                df_pos = df_type[df_type[x_var] == step_id]

                if not df_pos.empty:
                    x_pos = step_to_pos[step_id] + offset
                    y_val = df_pos[y_var].iloc[0]
                    step_positions[step_id] = (x_pos, y_val)

            # Get disassembly sequence for this product type
            if product_type in paths_data['products']:
                steps = paths_data['products'][product_type]['disassembly_steps']

                # Group steps by branch_id
                branches = {}
                for step in steps:
                    branch_id = step.get('branch_id', 'main')
                    if branch_id not in branches:
                        branches[branch_id] = []
                    branches[branch_id].append(step)

                # Draw main branch path (sequential steps in order of appearance)
                if 'main' in branches:
                    main_steps = branches['main']
                    prev_step_id = None
                    for step in main_steps:
                        current_step_id = step['step_id']
                        if prev_step_id and prev_step_id in step_positions and current_step_id in step_positions:
                            x1, y1 = step_positions[prev_step_id]
                            x2, y2 = step_positions[current_step_id]
                            ax.plot([x1, x2], [y1, y2], color=color, linestyle='--',
                                   linewidth=2, alpha=0.5, zorder=1)
                        prev_step_id = current_step_id

                # Draw front_axis branch: 5 -> 5_1_1
                if 'front_axis' in branches:
                    if '5' in step_positions and '5_1_1' in step_positions:
                        x1, y1 = step_positions['5']
                        x2, y2 = step_positions['5_1_1']
                        ax.plot([x1, x2], [y1, y2], color=color, linestyle='--',
                               linewidth=2, alpha=0.5, zorder=1)

                # Draw rear_axis branch: 5 -> 5_2_1 -> 5_2_2
                if 'rear_axis' in branches:
                    if '5' in step_positions and '5_2_1' in step_positions:
                        x1, y1 = step_positions['5']
                        x2, y2 = step_positions['5_2_1']
                        ax.plot([x1, x2], [y1, y2], color=color, linestyle='--',
                               linewidth=2, alpha=0.5, zorder=1)
                    if '5_2_1' in step_positions and '5_2_2' in step_positions:
                        x1, y1 = step_positions['5_2_1']
                        x2, y2 = step_positions['5_2_2']
                        ax.plot([x1, x2], [y1, y2], color=color, linestyle='--',
                               linewidth=2, alpha=0.5, zorder=1)

            # Plot scatter points on top of lines
            if step_positions:
                x_positions = [pos[0] for pos in step_positions.values()]
                y_values = [pos[1] for pos in step_positions.values()]
                ax.scatter(x_positions, y_values, s=200, color=color,
                          alpha=0.8, edgecolors='black', linewidth=1.5,
                          label=product_type.replace('car_', '').upper(), zorder=2)

        # Add baseline cost as horizontal line
        baseline_rows = df_sys[df_sys['branch_id'] == 'baseline']
        if not baseline_rows.empty:
            baseline = baseline_rows[y_var].iloc[0]
            ax.axhline(y=baseline, color='#666666', linestyle=':',
                      linewidth=2, alpha=0.7, label='System Baseline Cost')

        # Formatting
        ax.set_xticks(range(len(all_step_ids_sorted)))
        ax.set_xticklabels(all_step_ids_sorted, fontsize=DEFAULT_TICK_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_xlabel(config['x_axis']['label'], fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(config['y_axis']['label'], fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylim(global_y_min, global_y_max)
        ax.set_title(f"{system.upper()}\n({system_info['type']}, {system_info['division']}, "
                    f"{system_info['num_stations']} stations)",
                    fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)

        # Show grid only if not disabled
        if not config.get('hide_grid', False):
            ax.grid(True, alpha=DEFAULT_GRID_ALPHA, linestyle='--', linewidth=0.5)
        else:
            # Explicitly turn off all gridlines
            ax.grid(False)

        # Create legend
        if any(has_data.values()) or not baseline_rows.empty:
            ax.legend(loc='upper left', fontsize=DEFAULT_LEGEND_FONTSIZE, frameon=True,
                     fancybox=True, shadow=True, title='Product Type')

    # Overall title
    fig.suptitle(f"{config['title']}",
                fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.985)

    # Add component mapping table footer (if enabled)
    if show_table:
        try:
            paths_file = ATTRIBUTES_DIR / ATTRIBUTES_PATHS_FILE
            with open(paths_file, 'r') as f:
                paths_data = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Paths file not found: {paths_file}")
            raise
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in paths file: {e}")
            raise

        # Create table legend in the bottom row
        create_step_table_legend(fig, axes, paths_data)

    # Save figure
    output_filename = config['output_filename']
    output_path = output_dir / output_filename

    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()

    generated_files.append(output_filename)
    print(f"    [OK] Saved: {output_filename}")

    return generated_files


def plot_cumulative_profit_curve_bars(df, config, output_dir):
    """
    Generate cumulative profit bar charts with system baseline.
    Creates 1 SVG file containing 4 subplots (one per system).
    Each subplot shows grouped bars per step based on config specification.
    Data is averaged across all automation levels.

    Args:
        df: Dataframe with trajectory profit data
        config: Visualization config
        output_dir: Directory to save output files

    Returns:
        List of generated file paths
    """
    # Filter by product_types if specified in config, otherwise load from mappings
    if 'product_types' in config:
        df = df[df['product_type'].isin(config['product_types'])].copy()
        product_types = config['product_types']
    else:
        product_type_config = load_product_types()
        product_types = product_type_config['available']

    # Get unique systems
    systems = sorted([s for s in df['system'].unique() if pd.notna(s)])

    # Define colors for product types
    product_type_colors = get_product_type_colors()

    x_var = config['x_axis']['variable']
    y_var = config['y_axis']['variable']

    generated_files = []

    # Calculate global y-axis limits
    global_y_min = df[y_var].min()
    global_y_max = df[y_var].max()

    # Add some padding (10% on each side)
    y_range = global_y_max - global_y_min
    global_y_min = global_y_min - 0.1 * y_range
    global_y_max = global_y_max + 0.1 * y_range

    # Create figure with gridspec layout (2 rows for plots + 1 row for table)
    fig = plt.figure(figsize=(20, 20))  # Increased height for table
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.6], hspace=0.25, wspace=0.25)

    # Create subplots for the 2x2 grid (top two rows)
    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1])
    ]

    for sys_idx, system in enumerate(systems):
        if sys_idx >= 4:
            break

        ax = axes[sys_idx]
        df_sys = df[df['system'] == system]

        if df_sys.empty:
            ax.set_visible(False)
            continue

        # Get system information
        system_info = get_system_info(system)

        # Create step_id → numeric position mapping for this system
        all_step_ids = df_sys[x_var].unique().tolist()
        all_step_ids_sorted = sorted(all_step_ids, key=sort_key_for_step_id)
        step_to_pos = {step: idx for idx, step in enumerate(all_step_ids_sorted)}

        # Set up bar positions
        n_types = len(product_types)
        bar_width = 0.15
        position_indices = np.arange(len(all_step_ids_sorted))

        # Track which product types have data for legend
        has_data = {ptype: False for ptype in product_types}

        # Plot bars for each product type
        for type_idx, product_type in enumerate(product_types):
            df_type = df_sys[df_sys['product_type'] == product_type]

            if df_type.empty:
                continue

            has_data[product_type] = True
            color = product_type_colors[product_type]

            # Plot each step_id
            for pos_idx, step_id in enumerate(all_step_ids_sorted):
                df_pos = df_type[df_type[x_var] == step_id]

                if df_pos.empty:
                    continue

                # Get value for this step (aggregated across all components)
                y_val = df_pos[y_var].iloc[0]

                # Calculate x position for this bar
                x_pos = position_indices[pos_idx] + (type_idx - n_types/2 + 0.5) * bar_width

                # Plot bar
                ax.bar(x_pos, y_val, bar_width,
                      color=color, alpha=DEFAULT_ALPHA,
                      edgecolor='black', linewidth=1.5)

        # Add baseline cost as horizontal line
        if 'baseline_cost' in df_sys.columns:
            baseline = df_sys['baseline_cost'].iloc[0]
            ax.axhline(y=baseline, color='red', linestyle='--',
                      linewidth=2, alpha=0.7, label='System Baseline Cost')

        # Formatting
        ax.set_xticks(position_indices)
        ax.set_xticklabels(all_step_ids_sorted, fontsize=DEFAULT_TICK_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_xlabel(config['x_axis']['label'], fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylabel(config['y_axis']['label'], fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
        ax.set_ylim(global_y_min, global_y_max)  # Use global y-axis limits
        ax.set_title(f"{system.UPPER()}\n({system_info['type']}, {system_info['division']}, "
                    f"{system_info['num_stations']} stations)",
                    fontsize=DEFAULT_TITLE_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA, axis='y', linestyle='--', linewidth=0.5)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.7)

        # Create legend
        legend_handles = []
        legend_labels = []
        for ptype in product_types:
            if has_data[ptype]:
                legend_handles.append(plt.Rectangle((0,0),1,1,
                                                   facecolor=product_type_colors[ptype],
                                                   edgecolor='black', alpha=DEFAULT_ALPHA))
                legend_labels.append(ptype.replace('car_', '').upper())

        # Add baseline to legend if it exists
        if 'baseline_cost' in df_sys.columns:
            legend_handles.append(plt.Line2D([0], [0], color='red', linestyle='--',
                                            linewidth=2, alpha=0.7))
            legend_labels.append('Baseline Cost')

        if legend_handles:
            ax.legend(legend_handles, legend_labels,
                     loc='upper left', fontsize=DEFAULT_LEGEND_FONTSIZE, frameon=True,
                     fancybox=True, shadow=True, title='Product Type')

    # Overall title
    fig.suptitle(f"{config['title']}",
                fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.985)

    # Add component mapping table footer showing all product types
    try:
        paths_file = ATTRIBUTES_DIR / ATTRIBUTES_PATHS_FILE
        with open(paths_file, 'r') as f:
            paths_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Paths file not found: {paths_file}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in paths file: {e}")
        raise

    # Create table legend in the bottom row (gridspec row 2, spanning both columns)
    create_step_table_legend(fig, axes, paths_data)

    # Save figure (gridspec handles layout, no tight_layout needed)
    output_filename = config['output_filename']
    output_path = output_dir / output_filename

    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()

    generated_files.append(output_filename)
    print(f"    [OK] Saved: {output_filename}")

    return generated_files


def plot_system_type_automation_grid(df, config, output_path):
    """
    Generate dynamic grid of scatter plots for VIZ14.

    Layout:
    - 2 columns: Line systems (left) vs. Workshop systems (right)
    - Dynamic rows: Based on actual automation levels in data
    - X-axis: 6 indicators (IND01-IND06)
    - Y-axis: Normalized mean values
    - 3 scatter points per plot: 3, 4, 5 stations (where data exists)
    """
    # Load indicator config for names
    try:
        indicators_path = CONFIG_DIR / CONFIG_INDICATORS_FILE
        with open(indicators_path, 'r') as f:
            indicators_config = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Indicators config file not found: {indicators_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in indicators config: {e}")
        raise

    ind_names = {ind['indicator_id']: ind['indicator_name']
                 for ind in indicators_config['indicators']}

    # Get all 6 indicators
    all_indicators = sorted([ind['indicator_id'] for ind in indicators_config['indicators']])

    # Define system types
    system_types = ['line', 'workshop']

    # Create automation level mapping (raw DOE values → display labels)
    automation_mapping = {
        'a00': 'manual',
        'a02': 'low',
        'a04': 'medium',
        'a06': 'high'
    }

    # DYNAMIC: Detect actual automation levels in data
    raw_auto_levels = sorted(df['automation_level'].unique())
    automation_levels = [(raw, automation_mapping.get(raw, raw)) for raw in raw_auto_levels]
    n_auto_levels = len(automation_levels)

    print(f"    [DEBUG] Detected {n_auto_levels} automation levels: {raw_auto_levels}")

    # Convert num_stations to int for proper comparison
    df = df.copy()
    df['num_stations'] = df['num_stations'].astype(int)

    # DYNAMIC: Detect actual station counts in data
    station_counts = sorted(df['num_stations'].unique())
    print(f"    [DEBUG] Detected station counts: {station_counts}")

    # Create dynamic grid (n_auto_levels rows × 2 cols for system types)
    fig, axes = plt.subplots(n_auto_levels, 2, figsize=(16, 6*n_auto_levels))

    # Handle case where we have only 1 row
    if n_auto_levels == 1:
        axes = axes.reshape(1, -1)

    # Color map for station counts (dynamic based on data)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    markers = MARKER_STYLES[:5]  # Use first 5 markers from constants
    station_colors = {count: colors[i] for i, count in enumerate(station_counts)}
    station_markers = {count: markers[i] for i, count in enumerate(station_counts)}

    # For each automation level (rows)
    for auto_idx, (raw_auto, auto_label) in enumerate(automation_levels):

        # For each system type (columns)
        for sys_idx, sys_type in enumerate(system_types):
            ax = axes[auto_idx, sys_idx]

            # Filter data for this subplot using RAW automation value
            df_subset = df[
                (df['system_type'] == sys_type) &
                (df['automation_level'] == raw_auto)  # Use raw value for filtering
            ].copy()

            if df_subset.empty:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                       transform=ax.transAxes, fontsize=DEFAULT_TITLE_FONTSIZE, color='gray')
                ax.set_xticks([])
                ax.set_yticks([])
                continue

            # For each station count, plot all indicators
            for station_count in station_counts:
                df_stations = df_subset[df_subset['num_stations'] == station_count]

                if df_stations.empty:
                    continue

                # Collect y-values for all indicators
                x_positions = []
                y_values = []

                for indicator_id in all_indicators:
                    df_ind = df_stations[df_stations['indicator_id'] == indicator_id]

                    if not df_ind.empty:
                        x_positions.append(indicator_id)
                        y_values.append(df_ind['mean_normalized'].iloc[0])

                # Plot scatter points
                x_numeric = list(range(len(x_positions)))
                ax.scatter(
                    x_numeric,
                    y_values,
                    color=station_colors[station_count],
                    marker=station_markers[station_count],
                    s=DEFAULT_MARKER_SIZE,
                    label=f'{station_count} stations',
                    alpha=DEFAULT_ALPHA,
                    edgecolors='black',
                    linewidths=1.5,
                    zorder=3
                )

            # Formatting
            ax.set_xticks(range(len(all_indicators)))
            # Use indicator IDs (IND01, IND02, etc.) as x-axis labels
            ax.set_xticklabels(all_indicators, fontsize=DEFAULT_FONT_SIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
            # Get x-axis label from config or use default
            x_label = config.get('x_axis', {}).get('label', 'Indicators')
            ax.set_xlabel(x_label, fontsize=DEFAULT_FONT_SIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
            # Get y-axis label from config or use default
            y_label = config.get('y_axis', {}).get('label', 'Normalized Mean Value')
            ax.set_ylabel(y_label, fontsize=DEFAULT_FONT_SIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD)
            ax.set_ylim(-0.1, 1.1)
            ax.grid(True, alpha=DEFAULT_GRID_ALPHA, linestyle='--', linewidth=0.5, zorder=1)
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=2)
            ax.axhline(y=1, color='black', linestyle='-', linewidth=0.8, alpha=0.5, zorder=2)

            # Title for each subplot using DISPLAY LABEL
            title = f"{sys_type.capitalize()} - {auto_label.capitalize()}"
            ax.set_title(title, fontsize=DEFAULT_LABEL_FONTSIZE, fontweight=DEFAULT_FONTWEIGHT_BOLD, pad=10)

            # Legend in each subplot
            ax.legend(loc='upper right', fontsize=9, frameon=True,
                     fancybox=True, shadow=True)

    # Overall title
    fig.suptitle(config['title'], fontsize=16, fontweight=DEFAULT_FONTWEIGHT_BOLD, y=0.995)

    # Add indicator names as footer using standardized style
    indicator_items = [(ind_id, ind_names[ind_id]) for ind_id in all_indicators]
    bottom_margin = create_footer_legend(fig, "Indicator Descriptions", indicator_items, bottom_margin=0.12)

    plt.tight_layout(rect=[0, bottom_margin, 1, 0.99])
    plt.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.close()


# ====================
# ALL FUNCTIONS EXTRACTED
# ====================
# Module 6 refactoring complete!
# 18 plot functions successfully extracted from original 3,336-line file
