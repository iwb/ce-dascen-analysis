"""
Visualizations Package

Modular visualization components for the analytics framework.
"""

from .constants import *
from .helpers import (
    load_visualization_config,
    prepare_data,
    apply_filters,
    apply_aggregation,
    create_footer_legend,
    create_step_table_legend,
    get_system_info,
    create_component_info_box,
    create_component_info_box_v2,
    generate_color_shades,
    build_component_ordering_lookup,
    sort_key_for_step_id
)
from .plotting import (
    # Batch 1: Core plot functions
    plot_bar,
    plot_line,
    plot_scatter,
    plot_heatmap,
    plot_spider,
    # Batch 2: Boxplot functions
    plot_boxplot,
    plot_boxplot_by_stations,
    plot_boxplot_by_automation,
    plot_boxplot_by_product_mix,
    # Batch 3: Product depth functions
    plot_product_depth,
    plot_product_depth_by_automation,
    plot_product_depth_by_automation_bars,
    plot_product_depth_bars_simple,
    # Batch 4: Line and bar variants
    plot_line_faceted,
    plot_bar_grouped,
    # Batch 5: Cumulative profit and system grid
    plot_cumulative_profit_curve,
    plot_cumulative_profit_curve_bars,
    plot_system_type_automation_grid
)

__all__ = [
    # Config loading
    'load_visualization_config',
    # Data preparation
    'prepare_data',
    'apply_filters',
    'apply_aggregation',
    # Legends and helpers
    'create_footer_legend',
    'create_step_table_legend',
    'get_system_info',
    'create_component_info_box',
    'create_component_info_box_v2',
    'generate_color_shades',
    'build_component_ordering_lookup',
    'sort_key_for_step_id',
    # Plot functions - Batch 1
    'plot_bar',
    'plot_line',
    'plot_scatter',
    'plot_heatmap',
    'plot_spider',
    # Plot functions - Batch 2
    'plot_boxplot',
    'plot_boxplot_by_stations',
    'plot_boxplot_by_automation',
    'plot_boxplot_by_product_mix',
    # Plot functions - Batch 3
    'plot_product_depth',
    'plot_product_depth_by_automation',
    'plot_product_depth_by_automation_bars',
    'plot_product_depth_bars_simple',
    # Plot functions - Batch 4
    'plot_line_faceted',
    'plot_bar_grouped',
    # Plot functions - Batch 5
    'plot_cumulative_profit_curve',
    'plot_cumulative_profit_curve_bars',
    'plot_system_type_automation_grid'
]
