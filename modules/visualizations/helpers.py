"""
Visualization Helper Functions

Data preparation and utility functions for visualizations.
"""

import json
import pandas as pd
from .constants import (
    CONFIG_DIR, CONFIG_VIZ_FILE, CONFIG_INDICATORS_FILE, CONFIG_MAPPINGS_FILE, DOE_EXPERIMENTS_FILE,
    ATTRIBUTES_DIR, ATTRIBUTES_PATHS_FILE,
    DEFAULT_BOTTOM_MARGIN, TABLE_HEADER_COLOR, TABLE_ROW_LABEL_COLOR,
    TABLE_EVEN_ROW_COLOR, TABLE_ODD_ROW_COLOR, TABLE_FONT_SIZE,
    TABLE_HEADER_FONT_SIZE, TABLE_SCALE_X, TABLE_SCALE_Y, TABLE_CELL_PAD,
    TABLE_HEADER_HEIGHT, TABLE_BBOX_HEIGHT, TABLE_TITLE_Y_POS,
    TABLE_TITLE_FONT_SIZE, TABLE_LEGEND_FONTSIZE, TABLE_LEGEND_LINEWIDTH,
    TABLE_LEGEND_ALPHA, TABLE_LEGEND_BOX_PAD, TABLE_LEGEND_FACECOLOR,
    TABLE_LEGEND_EDGECOLOR, TABLE_LEGEND_FAMILY, TABLE_LEGEND_BOX_STYLE, BRANCH_MARKERS,
    INFO_BOX_X, INFO_BOX_Y, DEFAULT_INFO_FONTSIZE
)


# ====================
# 1. Configuration Loading
# ====================

def load_visualization_config():
    """Load visualization configuration."""
    try:
        config_path = CONFIG_DIR / CONFIG_VIZ_FILE
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"[ERROR] Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in configuration file: {e}")
        raise


def load_product_types():
    """Load product type configuration from config_mappings.json."""
    try:
        config_path = CONFIG_DIR / CONFIG_MAPPINGS_FILE
        with open(config_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)

        if 'product_types' not in mappings:
            print(f"[ERROR] 'product_types' key not found in {CONFIG_MAPPINGS_FILE}")
            return {
                'available': [],
                'reference': None,
                'labels': {},
                'colors': {}
            }
        return mappings['product_types']
    except FileNotFoundError:
        print(f"[ERROR] Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in configuration file: {e}")
        raise


# ====================
# 2. Helper Functions
# ====================

def create_footer_legend(fig, title, content_dict, bottom_margin=DEFAULT_BOTTOM_MARGIN):
    """
    Create a standardized footer legend below the figure with matplotlib legend style.

    Args:
        fig: Matplotlib figure object
        title: Title for the legend (e.g., "Indicator Descriptions")
        content_dict: Dictionary or list of tuples with ID: description pairs
        bottom_margin: Bottom margin to leave for the footer (default from constants)

    Returns:
        bottom_margin value to use in tight_layout
    """
    # Convert dict to list of tuples if needed
    if isinstance(content_dict, dict):
        items = list(content_dict.items())
    else:
        items = content_dict

    # Create text content with left-aligned formatting
    text_lines = [f"{key}: {value}" for key, value in items]
    text_content = '\n'.join(text_lines)

    # Add underline to title for emphasis (since per-line bold isn't supported)
    title_underlined = f"{title}\n{'─' * len(title)}"
    full_text = f"{title_underlined}\n{text_content}"

    # Add text box with matplotlib legend style (white background, gray border)
    fig.text(0.5, 0.01, full_text, ha='center', va='bottom',
            fontsize=TABLE_LEGEND_FONTSIZE, family=TABLE_LEGEND_FAMILY,
            bbox=dict(boxstyle=TABLE_LEGEND_BOX_STYLE,
                     facecolor=TABLE_LEGEND_FACECOLOR,
                     edgecolor=TABLE_LEGEND_EDGECOLOR,
                     linewidth=TABLE_LEGEND_LINEWIDTH,
                     alpha=TABLE_LEGEND_ALPHA))

    return bottom_margin


def create_step_table_legend(fig, axes, paths_data):
    """
    Create a table legend showing step-to-component mapping for all product types.
    Uses hierarchical step_id (e.g., "1", "2", "5", "5.1.1", "5.2.1") as row labels.
    Places the table BELOW the subplots in a dedicated subplot.

    Args:
        fig: Matplotlib figure object
        axes: Array of subplot axes (should have space for table at bottom)
        paths_data: Disassembly paths data from attributes_disassembly_paths.json

    Returns:
        None
    """
    # Load product types from configuration
    product_type_config = load_product_types()
    product_types = product_type_config['available']
    product_labels = [product_type_config['labels'].get(pt, pt.upper()) for pt in product_types]

    # Get all step_ids from reference product (most complex product)
    reference_product = product_type_config['reference']
    if reference_product not in paths_data['products']:
        return

    reference_steps = paths_data['products'][reference_product]['disassembly_steps']

    # Get unique step_ids (in order of first appearance)
    seen = set()
    all_step_ids = []
    for step in reference_steps:
        if step['step_id'] not in seen:
            all_step_ids.append(step['step_id'])
            seen.add(step['step_id'])

    # Build table data: rows = step_ids, columns = product types
    table_data = []
    row_labels = []

    for step_id in all_step_ids:
        row_labels.append(step_id)
        row = []

        for ptype in product_types:
            # Find ALL components for this step_id in this product type
            components_list = []

            if ptype in paths_data['products'] and 'disassembly_steps' in paths_data['products'][ptype]:
                steps = paths_data['products'][ptype]['disassembly_steps']
                # Collect ALL steps with matching step_id
                for step in steps:
                    if step['step_id'] == step_id:
                        components_list.extend(step['components_released'])

            components = ', '.join(components_list) if components_list else "-"
            row.append(components)

        table_data.append(row)

    # Create the table
    col_labels = product_labels

    # Add a new subplot at the bottom for the table
    # The figure should have been created with gridspec (3 rows x 2 cols)
    # We need to access the gridspec used to create the plots
    if len(axes) > 0 and hasattr(axes[0], 'get_gridspec'):
        gs = axes[0].get_gridspec()
        # Use the existing gridspec to span both columns of the third row
        table_ax = fig.add_subplot(gs[2, :])  # Row 2 (0-indexed), all columns
    else:
        # Fallback for figures without gridspec
        table_ax = fig.add_subplot(3, 1, 3)

    table_ax.axis('off')  # Hide axis

    # Create table using plt.table
    table = table_ax.table(
        cellText=table_data,
        rowLabels=row_labels,
        colLabels=col_labels,
        cellLoc='left',
        rowLoc='center',
        colLoc='center',
        loc='center',
        bbox=[0, 0, 1, TABLE_BBOX_HEIGHT]
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(TABLE_FONT_SIZE)
    table.scale(TABLE_SCALE_X, TABLE_SCALE_Y)

    # Style header row and cells
    for (i, j), cell in table.get_celld().items():
        if i == 0:  # Header row
            cell.set_facecolor(TABLE_HEADER_COLOR)
            cell.set_text_props(weight='bold', color='white', fontsize=TABLE_HEADER_FONT_SIZE)
            cell.set_height(TABLE_HEADER_HEIGHT)
        elif j == -1:  # Row labels (step_id column)
            cell.set_facecolor(TABLE_ROW_LABEL_COLOR)
            cell.set_text_props(weight='bold', fontsize=TABLE_FONT_SIZE)
        else:  # Data cells
            cell.set_facecolor(TABLE_EVEN_ROW_COLOR if i % 2 == 0 else TABLE_ODD_ROW_COLOR)

        # Add padding to all cells
        cell.PAD = TABLE_CELL_PAD

    # Add title above the table
    table_ax.text(0.5, TABLE_TITLE_Y_POS, 'Component Mapping by Product Type (Hierarchical Steps)',
                  ha='center', va='top', fontsize=TABLE_TITLE_FONT_SIZE, weight='bold',
                  transform=table_ax.transAxes)


def get_system_info(system):
    """
    Get system details from DOE file.

    Args:
        system: System ID (e.g., 'system_01')

    Returns:
        Dict with system_type, division_type, num_stations
    """
    try:
        doe_path = CONFIG_DIR / DOE_EXPERIMENTS_FILE
        df_doe = pd.read_csv(doe_path)

        # Get first experiment for this system
        row = df_doe[df_doe['system'] == system].iloc[0]

        return {
            'type': row['system_type'].capitalize(),
            'division': row['division_type'].capitalize(),
            'num_stations': int(row['num_stations'])
        }
    except FileNotFoundError:
        print(f"[ERROR] DOE file not found: {doe_path}")
        raise
    except (IndexError, KeyError) as e:
        print(f"[ERROR] System not found or invalid data: {system} - {e}")
        raise


# ====================
# 3. Data Preparation Functions
# ====================

def prepare_data(viz_config, data):
    """Prepare data based on data_source."""
    data_source = viz_config['data_source']

    if data_source == 'experiments':
        df = data['df_experiments'].copy()
    elif data_source == 'groups':
        df = data['df_groups'].copy()
    elif data_source == 'trajectories':
        df = data['depth_component_by_system'].copy()
    elif data_source == 'depth_cumulative':
        df = data['depth_cumulative'].copy()
    elif data_source == 'depth_product_cumulative':
        df = data['depth_product_cumulative'].copy()
    elif data_source == 'depth_step_aggregated':
        df = data['depth_step_aggregated'].copy()
    elif data_source == 'depth_profit_with_baseline':
        df = data['depth_profit_with_baseline'].copy()
    else:
        raise ValueError(f"Unknown data_source: {data_source}")

    # Apply filters
    if 'filters' in viz_config:
        df = apply_filters(df, viz_config['filters'])

    # Apply aggregation if specified
    if 'aggregation' in viz_config:
        df = apply_aggregation(df, viz_config['aggregation'], viz_config)

    return df


def apply_filters(df, filters):
    """Apply filters to dataframe."""
    for key, value in filters.items():
        if isinstance(value, str) and any(op in value for op in ['<=', '>=', '<', '>', '==', '!=']):
            # Parse comparison
            if '<=' in value:
                threshold = float(value.replace('<=', ''))
                df = df[df[key] <= threshold]
            elif '>=' in value:
                threshold = float(value.replace('>=', ''))
                df = df[df[key] >= threshold]
            elif '==' in value:
                val = value.replace('==', '').strip()
                if val.lower() == 'true':
                    df = df[df[key] == True]
                elif val.lower() == 'false':
                    df = df[df[key] == False]
                else:
                    df = df[df[key] == val]
        else:
            df = df[df[key] == value]

    return df


def apply_aggregation(df, agg_config, viz_config=None):
    """Apply aggregation to dataframe."""
    func = agg_config['function']
    metric = agg_config['metric']

    # For heatmaps, only group by row and column variables
    if viz_config and viz_config.get('viz_type') == 'heatmap':
        row_var = viz_config['rows']['variable']
        col_var = viz_config['cols']['variable']
        group_cols = [row_var, col_var]
    else:
        # For other viz types, determine grouping columns (all non-metric columns)
        group_cols = [col for col in df.columns if col != metric and df[col].dtype == 'object']

    if len(group_cols) > 0:
        df = df.groupby(group_cols)[metric].agg(func).reset_index()
        df.columns = list(df.columns[:-1]) + [metric]

        # For std function: convert NaN to 0 (occurs when group has only 1 value)
        if func == 'std':
            df[metric] = df[metric].fillna(0)

    return df


# ====================
# 4. Component Info Box Functions
# ====================

def create_component_info_box(ax, df_product, product_type):
    """
    Create info box showing position→component mapping with branch indicators.

    Args:
        ax: Matplotlib axis
        df_product: Product-specific dataframe
        product_type: Product type name
    """
    # Get unique components sorted by parallel_position
    components = df_product[['component', 'parallel_position', 'branch_path']].drop_duplicates()
    components = components.sort_values(['parallel_position', 'branch_path'])

    # Group components by position to show parallel branches
    position_map = {}
    for _, row in components.iterrows():
        pos = row['parallel_position']
        comp = row['component']
        branch = row['branch_path']

        if pos not in position_map:
            position_map[pos] = []
        position_map[pos].append((comp, branch))

    # Build info text
    info_lines = ["Position → Components:"]
    for pos in sorted(position_map.keys()):
        comps = position_map[pos]
        if len(comps) == 1:
            comp, branch = comps[0]
            marker = '◆' if branch == 'main' else ('○' if branch == 'front_axis' else '□')
            info_lines.append(f"{int(pos)}: {comp} {marker}")
        else:
            # Multiple components at same position (parallel branches)
            comp_strs = []
            for comp, branch in comps:
                marker = '○' if branch == 'front_axis' else '□'
                comp_strs.append(f"{comp} {marker}")
            info_lines.append(f"{int(pos)}: {' | '.join(comp_strs)}")

    info_lines.append("")
    info_lines.append("Legend:")
    info_lines.append("◆ = Main Path")
    info_lines.append("○ = Front Axis")
    info_lines.append("□ = Rear Axis")

    info_text = '\n'.join(info_lines)

    # Add text box in upper left corner
    ax.text(INFO_BOX_X, INFO_BOX_Y, info_text, transform=ax.transAxes,
           fontsize=DEFAULT_INFO_FONTSIZE, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
           family='monospace')


def create_component_info_box_v2(ax, df_product, product_type):
    """
    Create compact info box showing position→component mapping with branch indicators.
    Optimized for multi-subplot layouts.

    Args:
        ax: Matplotlib axis
        df_product: Product-specific dataframe
        product_type: Product type name
    """
    # Get unique components sorted by parallel_position
    components = df_product[['component', 'parallel_position', 'branch_path']].drop_duplicates()
    components = components.sort_values(['parallel_position', 'branch_path'])

    # Group components by position to show parallel branches
    position_map = {}
    for _, row in components.iterrows():
        pos = row['parallel_position']
        comp = row['component']
        branch = row['branch_path']

        if pos not in position_map:
            position_map[pos] = []
        position_map[pos].append((comp, branch))

    # Build compact info text
    info_lines = ["Pos → Comp:"]
    for pos in sorted(position_map.keys()):
        comps = position_map[pos]
        if len(comps) == 1:
            comp, branch = comps[0]
            marker = '◆' if branch == 'main' else ('○' if branch == 'front_axis' else '□')
            info_lines.append(f"{int(pos)}: {comp}{marker}")
        else:
            # Multiple components at same position (parallel branches)
            comp_strs = []
            for comp, branch in comps:
                marker = '○' if branch == 'front_axis' else '□'
                comp_strs.append(f"{comp}{marker}")
            info_lines.append(f"{int(pos)}: {' | '.join(comp_strs)}")

    info_lines.append("")
    info_lines.append("◆=Main ○=Front □=Rear")

    info_text = '\n'.join(info_lines)

    # Add text box in upper left corner with smaller font
    ax.text(INFO_BOX_X, INFO_BOX_Y, info_text, transform=ax.transAxes,
           fontsize=6, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
           family='monospace')


# ====================
# 5. Color and Ordering Utilities
# ====================

def generate_color_shades(base_color, n_shades):
    """
    Generate N shades of a base color, from darker to lighter.

    Args:
        base_color: RGBA tuple from colormap (e.g., plt.cm.tab10(0))
        n_shades: Number of shades to generate

    Returns:
        List of RGBA tuples (darkest first, lightest last)
    """
    import matplotlib.colors as mcolors

    if n_shades == 1:
        return [base_color]

    # Convert to RGB (ignore alpha)
    rgb = base_color[:3]

    # Generate shades by linearly interpolating between darker and lighter versions
    shades = []
    for i in range(n_shades):
        # Progress from 0.7 (dark) to 1.0 (light)
        factor = 0.7 + (0.3 * i / (n_shades - 1)) if n_shades > 1 else 1.0
        shade_rgb = tuple(min(1.0, c * factor + (1 - factor) * 1.0) for c in rgb)
        shades.append(shade_rgb + (0.85,))  # Add alpha=0.85

    return shades


def build_component_ordering_lookup(paths_data):
    """
    Build a lookup dict for component ordering based on JSON paths file.

    Args:
        paths_data: Parsed JSON from attributes_disassembly_paths.json

    Returns:
        Dict mapping (product_type, step_id) -> [list of components in order]
    """
    ordering = {}

    for product_type, product_info in paths_data['products'].items():
        for step in product_info['disassembly_steps']:
            step_id = step['step_id']
            components = step['components_released']

            key = (product_type, step_id)
            if key not in ordering:
                ordering[key] = []

            # Add components in order they appear in JSON
            for comp in components:
                if comp not in ordering[key]:
                    ordering[key].append(comp)

    return ordering


def sort_key_for_step_id(step_id):
    """
    Create a sort key for hierarchical step IDs.
    Handles both underscore and dot notation: "1", "2", "5", "5_1_1", "5_2_1", "5_2_2" or "5.1.1", "5.2.1", "5.2.2"

    Returns tuple of integers for proper sorting.
    """
    if step_id is None or step_id == '':
        return (999,)  # Put None/empty at end

    # Support both underscore and dot notation for compatibility
    if '_' in str(step_id):
        parts = str(step_id).split('_')
    else:
        parts = str(step_id).split('.')

    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (999,)  # Put invalid values at end
