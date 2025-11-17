"""
Module 5: Depth Analysis

PURPOSE:
- Analyze cost-benefit relationship across disassembly depth levels
- Generate product-specific disassembly trajectories
- Calculate cumulative profit curves with system baseline

OUTPUTS:
- depth_component_analysis.csv: Per-component aggregates
- depth_cumulative.csv: Cumulative values by system and step
- depth_product_cumulative.csv: Product-specific trajectories
- depth_profit_with_baseline.csv: Cumulative profit curves with baseline
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# ====================
# CONSTANTS AND CONFIGURATION
# ====================

# Directory paths
CONFIG_DIR = Path(__file__).parent.parent / 'data' / 'config'
ATTRIBUTES_DIR = Path(__file__).parent.parent / 'data' / 'attributes'
OUTPUT_DIR = Path(__file__).parent.parent / 'output' / 'dataframes'

# Configuration files
CONFIG_MAPPINGS_FILE = 'config_mappings.json'
CONFIG_DEPTH_FILE = 'config_disassembly_depth.json'
ATTR_PATHS_FILE = 'attributes_disassembly_paths.json'
ATTR_PRODUCT_FILE = 'attributes_product.json'

# Output file patterns
OUTPUT_FILES = {
    'component': 'M5_01_depth_component_revenue.csv',
    'step_per_exp': 'M5_02_depth_step_per_experiment.csv',
    'product_cumulative': 'M5_03_depth_product_cumulative.csv',
    'step_aggregated': 'M5_04_depth_step_aggregated.csv',
    'profit_baseline': 'M5_05_depth_profit_with_baseline.csv'
}

# Column names
COL_EXP_ID = 'exp_id'
COL_SYSTEM = 'system'
COL_PRODUCT_MIX = 'product_mix'
COL_AUTOMATION_LEVEL = 'automation_level'
COL_PRODUCT_TYPE = 'product_type'
COL_STEP_NAME = 'step_name'
COL_STEP_ID = 'step_id'
COL_BRANCH_ID = 'branch_id'
COL_COMPONENT_NAME = 'component_name'
COL_IS_FEASIBLE = 'is_feasible'
COL_RANK = 'rank'
COL_TOTAL_SCORE = 'total_weighted_score'
COL_START_TIME = 'start_time'

# Indicator columns
IND_ELECTRICITY = 'IND01'
IND_CIRCULARITY = 'IND06'
VAL_PROFIT = 'PROFIT'
VAL_REVENUE = 'REVENUE'
VAL_COSTS_FIX = 'COSTS_FIX'
VAL_COSTS_VAR = 'COSTS_VAR'
VAL_SYSTEM_BASELINE = 'VAL04'

# Statistical column prefixes
PREFIX_MEAN = 'mean_'
PREFIX_STD = 'std_'
PREFIX_TOTAL = 'total_'
PREFIX_CUMULATIVE = 'cumulative_'
SUFFIX_MEAN = '_mean'
SUFFIX_STD = '_std'

# Default values
DEFAULT_PRODUCT_TYPE = 'unknown'
DEFAULT_BRANCH = 'main'
DEFAULT_BASELINE_COST = 0
SORT_KEY_DEFAULT = 999

# ====================
# 1. CONFIGURATION LOADING FUNCTIONS
# ====================

def load_mappings():
    """Load mappings from config_mappings.json."""
    try:
        config_path = CONFIG_DIR / CONFIG_MAPPINGS_FILE
        if not config_path.exists():
            print(f"  [ERROR] Configuration file not found: {config_path}")
            return {}

        with open(config_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        return mappings
    except json.JSONDecodeError as e:
        print(f"  [ERROR] Failed to parse {CONFIG_MAPPINGS_FILE}: {e}")
        return {}
    except Exception as e:
        print(f"  [ERROR] Failed to load mappings: {e}")
        return {}


def load_product_types():
    """Load product type configuration from config_mappings.json."""
    mappings = load_mappings()
    if 'product_types' not in mappings:
        print(f"  [ERROR] 'product_types' key not found in {CONFIG_MAPPINGS_FILE}")
        return {
            'available': [],
            'reference': None,
            'labels': {},
            'colors': {}
        }
    return mappings['product_types']


def load_aggregation_config():
    """Load aggregation configuration from config_disassembly_depth.json."""
    try:
        config_path = CONFIG_DIR / CONFIG_DEPTH_FILE
        if not config_path.exists():
            print(f"  [ERROR] Configuration file not found: {config_path}")
            return {'count_columns': [], 'sum_columns': []}

        with open(config_path, 'r', encoding='utf-8') as f:
            depth_config = json.load(f)

        if 'component_aggregation' not in depth_config:
            print(f"  [WARNING] 'component_aggregation' key not found in {CONFIG_DEPTH_FILE}")
            return {'count_columns': [], 'sum_columns': []}

        return depth_config['component_aggregation']
    except json.JSONDecodeError as e:
        print(f"  [ERROR] Failed to parse {CONFIG_DEPTH_FILE}: {e}")
        return {'count_columns': [], 'sum_columns': []}
    except Exception as e:
        print(f"  [ERROR] Failed to load aggregation config: {e}")
        return {'count_columns': [], 'sum_columns': []}


# ====================
# 2. COMPONENT AGGREGATION
# ====================

def calculate_component_aggregates(data):
    """
    Calculate per-component aggregates for each experiment.
    Uses actual component names (step_name) from process data.
    Now uses PROFIT, REVENUE, COSTS metrics from Module 1.
    Uses existing product_type column from loaded simulation data.
    """
    try:
        # Validate input data
        if 'df_process' not in data or data['df_process'] is None or data['df_process'].empty:
            print("  [ERROR] df_process is missing or empty")
            return pd.DataFrame()

        df_process = data['df_process'].copy()

        # Load aggregation config from config_disassembly_depth.json
        agg_config = load_aggregation_config()
        if not agg_config:
            print("  [ERROR] Failed to load aggregation configuration")
            return pd.DataFrame()

        # Build aggregation dict from config
        agg_dict = {}
        for col in agg_config.get('count_columns', []):
            if col in df_process.columns:
                agg_dict[col] = 'count'
        for col in agg_config.get('sum_columns', []):
            if col in df_process.columns:
                agg_dict[col] = 'sum'

        if not agg_dict:
            print("  [WARNING] No valid columns to aggregate")
            return pd.DataFrame()

        # Group ALL components without filtering - let config drive what to use
        group_columns = [COL_EXP_ID, COL_SYSTEM, COL_PRODUCT_MIX, COL_AUTOMATION_LEVEL, COL_PRODUCT_TYPE, COL_STEP_NAME]
        missing_cols = [col for col in group_columns if col not in df_process.columns]
        if missing_cols:
            print(f"  [ERROR] Missing required columns: {missing_cols}")
            return pd.DataFrame()

        component_agg = df_process.groupby(group_columns).agg(agg_dict).reset_index()

        # Rename columns directly (since agg returns simple column names)
        rename_map = {
            COL_COMPONENT_NAME: 'n_components',
            IND_ELECTRICITY: 'total_electricity',
            IND_CIRCULARITY: 'total_circularity',
            VAL_PROFIT: 'total_profit',
            VAL_REVENUE: 'total_revenue',
            VAL_COSTS_FIX: 'total_cost_fix',
            VAL_COSTS_VAR: 'total_cost_var'
        }

        # Only rename columns that exist
        rename_map = {k: v for k, v in rename_map.items() if k in component_agg.columns}
        component_agg.rename(columns=rename_map, inplace=True)

        # Calculate total cost as sum of fixed and variable costs
        if 'total_cost_fix' in component_agg.columns and 'total_cost_var' in component_agg.columns:
            component_agg['total_cost'] = component_agg['total_cost_fix'] + component_agg['total_cost_var']
        else:
            component_agg['total_cost'] = 0

        # Calculate mean values (total / n_components) with division by zero handling
        if 'n_components' in component_agg.columns:
            n_comp = component_agg['n_components'].replace(0, 1)  # Avoid division by zero

            if 'total_electricity' in component_agg.columns:
                component_agg[PREFIX_MEAN + 'electricity'] = component_agg['total_electricity'] / n_comp

            if 'total_circularity' in component_agg.columns:
                component_agg[PREFIX_MEAN + 'circularity'] = component_agg['total_circularity'] / n_comp

            if 'total_profit' in component_agg.columns:
                component_agg[PREFIX_MEAN + 'profit'] = component_agg['total_profit'] / n_comp

            if 'total_revenue' in component_agg.columns:
                component_agg[PREFIX_MEAN + 'revenue'] = component_agg['total_revenue'] / n_comp

            if 'total_cost' in component_agg.columns:
                component_agg[PREFIX_MEAN + 'cost'] = component_agg['total_cost'] / n_comp

        # Load disassembly paths to add step_id
        path_config = load_disassembly_paths()

        # Add step_id for each component based on product_type and step_name
        def get_step_id(row):
            product_type = row.get(COL_PRODUCT_TYPE, '')
            step_name = row.get(COL_STEP_NAME, '')

            if product_type in path_config:
                comp_to_step = map_components_to_steps(product_type, path_config)
                if step_name in comp_to_step:
                    return comp_to_step[step_name].get(COL_STEP_ID, '')
            return ''

        component_agg[COL_STEP_ID] = component_agg.apply(get_step_id, axis=1)

        # Reorder columns: step_id and step_name early for easier sorting/viewing
        base_columns = [COL_EXP_ID, COL_SYSTEM, COL_STEP_ID, COL_STEP_NAME, COL_PRODUCT_MIX,
                       COL_AUTOMATION_LEVEL, COL_PRODUCT_TYPE]
        value_columns = ['n_components', 'total_electricity', 'total_circularity',
                        'total_profit', 'total_revenue', 'total_cost']
        mean_columns = [PREFIX_MEAN + 'electricity', PREFIX_MEAN + 'circularity',
                       PREFIX_MEAN + 'profit', PREFIX_MEAN + 'revenue', PREFIX_MEAN + 'cost']

        # Only include columns that exist
        column_order = []
        for col in base_columns + value_columns + mean_columns:
            if col in component_agg.columns:
                column_order.append(col)

        component_agg = component_agg[column_order]

        # Round to specified decimals
        numeric_cols = component_agg.select_dtypes(include=[np.number]).columns
        precision = data['formatting_config']['output_formatting']['precision_decimals']
        component_agg[numeric_cols] = component_agg[numeric_cols].round(precision)

        return component_agg

    except Exception as e:
        print(f"  [ERROR] Failed to calculate component aggregates: {e}")
        return pd.DataFrame()


def aggregate_by_step(df_component_agg):
    """
    Aggregate component-level data to step-level per experiment.

    Sums all components within the same step_id for each experiment.
    This creates one row per (exp_id, system, step_id, product_type) combination.

    Args:
        df_component_agg: Component-level dataframe from calculate_component_aggregates()

    Returns:
        DataFrame with step-level aggregated values per experiment
    """
    df = df_component_agg.copy()

    # Group by experiment and step identifiers
    group_cols = ['exp_id', 'system', 'step_id', 'product_mix', 'automation_level', 'product_type']

    # Aggregate: sum totals, take mean of means (weighted by n_components)
    agg_dict = {
        'n_components': 'sum',
        'total_electricity': 'sum',
        'total_circularity': 'sum',
        'total_profit': 'sum',
        'total_revenue': 'sum',
        'total_cost': 'sum',
        'step_name': lambda x: ', '.join(sorted(x))  # Combine component names
    }

    df_step = df.groupby(group_cols, as_index=False).agg(agg_dict)

    # Rename aggregated column
    df_step = df_step.rename(columns={'step_name': 'components'})

    # Recalculate mean values based on aggregated totals
    df_step['mean_electricity'] = df_step['total_electricity'] / df_step['n_components']
    df_step['mean_circularity'] = df_step['total_circularity'] / df_step['n_components']
    df_step['mean_profit'] = df_step['total_profit'] / df_step['n_components']
    df_step['mean_revenue'] = df_step['total_revenue'] / df_step['n_components']
    df_step['mean_cost'] = df_step['total_cost'] / df_step['n_components']

    # Reorder columns
    column_order = [
        'exp_id', 'system', 'step_id', 'components', 'product_mix', 'automation_level', 'product_type', 'n_components',
        # Total values
        'total_electricity', 'total_circularity',
        'total_profit', 'total_revenue', 'total_cost',
        # Mean values
        'mean_electricity', 'mean_circularity',
        'mean_profit', 'mean_revenue', 'mean_cost'
    ]

    df_step = df_step[column_order]

    # Sort by experiment and step_id hierarchy
    df_step['sort_key'] = df_step['step_id'].apply(sort_key_for_step_id)
    df_step = df_step.sort_values(['exp_id', 'product_type', 'sort_key'])
    df_step = df_step.drop('sort_key', axis=1)

    # Round to 2 decimals
    numeric_cols = df_step.select_dtypes(include=[np.number]).columns
    df_step[numeric_cols] = df_step[numeric_cols].round(2)

    return df_step


def extract_disassembly_sequence(data):
    """
    Extract canonical disassembly sequence order from process data using timestamps.
    Returns ordered list of step_names based on median start_time across all products.
    """
    df_process = data['df_process'].copy()

    # Calculate median start_time for each step across all products
    step_order = df_process.groupby('step_name')['start_time'].apply(
        lambda x: pd.to_datetime(x).median()
    ).sort_values().index.tolist()

    return step_order


def derive_branch_components(path_config):
    """
    Derive branch components from path configuration.

    Args:
        path_config: Disassembly path configuration (from load_disassembly_paths())

    Returns:
        List of component names that create branches
    """
    branch_components = []
    for product_type, config in path_config.items():
        for step in config['disassembly_steps']:
            if 'creates_branches' in step:
                branch_components.append(step['step_name'])
    return list(set(branch_components))  # Remove duplicates


def load_disassembly_paths():
    """Load disassembly path configuration from attributes file."""
    try:
        attrs_path = ATTRIBUTES_DIR / ATTR_PATHS_FILE

        if not attrs_path.exists():
            print(f"  [ERROR] Attributes file not found: {attrs_path}")
            return {}

        with open(attrs_path, 'r', encoding='utf-8') as f:
            path_data = json.load(f)

        if 'products' not in path_data:
            print(f"  [WARNING] 'products' key not found in {ATTR_PATHS_FILE}")
            return {}

        return path_data['products']

    except json.JSONDecodeError as e:
        print(f"  [ERROR] Failed to parse {ATTR_PATHS_FILE}: {e}")
        return {}
    except Exception as e:
        print(f"  [ERROR] Failed to load disassembly paths: {e}")
        return {}


def map_components_to_steps(product_type, path_config):
    """
    Map component names to their parent disassembly step using hierarchical step_id.

    Args:
        product_type: Product type key (e.g., 'car_hd', 'car_rd')
        path_config: Disassembly paths config (from load_disassembly_paths())

    Returns:
        dict: {component_name: step_info_dict}
            step_info includes: step_id, step_name, branch_id, is_passive
    """
    if 'disassembly_steps' not in path_config[product_type]:
        raise ValueError(f"Product '{product_type}' missing 'disassembly_steps' in attributes file")

    steps_config = path_config[product_type]['disassembly_steps']
    component_to_step = {}

    for step in steps_config:
        step_id = step['step_id']
        step_name = step['step_name']
        branch_id = step['branch_id']
        passive_components = step.get('passive_components', [])

        # Map all components released in this step
        for comp in step['components_released']:
            is_passive = comp in passive_components
            component_to_step[comp] = {
                'step_id': step_id,
                'step_name': step_name,
                'branch_id': branch_id,
                'is_passive': is_passive
            }

    return component_to_step


# Removed load_automation_groups() - automation grouping belongs to Module 4 (groups)


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


def load_component_values():
    """Load component value data from attributes_product.json."""
    try:
        attrs_path = ATTRIBUTES_DIR / ATTR_PRODUCT_FILE

        if not attrs_path.exists():
            print(f"  [ERROR] Attributes file not found: {attrs_path}")
            return {}

        with open(attrs_path, 'r', encoding='utf-8') as f:
            product_data = json.load(f)

        if 'components' not in product_data:
            print(f"  [WARNING] 'components' key not found in {ATTR_PRODUCT_FILE}")
            return {}

        # Create dict of component_name -> value dict (quality -> value)
        component_values = {}
        for comp in product_data['components']:
            if 'component_name' not in comp:
                continue

            comp_name = comp['component_name']

            # Get value ranges
            if 'quality_dependent_attributes' in comp and 'component_value' in comp['quality_dependent_attributes']:
                value_ranges = comp['quality_dependent_attributes']['component_value']
                # For simplicity, use the maximum quality value (quality=1.0 if available, else highest)
                if value_ranges:
                    max_value = max(vr.get('value', 0) for vr in value_ranges)
                    component_values[comp_name] = max_value
            else:
                component_values[comp_name] = 0

        return component_values

    except json.JSONDecodeError as e:
        print(f"  [ERROR] Failed to parse {ATTR_PRODUCT_FILE}: {e}")
        return {}
    except Exception as e:
        print(f"  [ERROR] Failed to load component values: {e}")
        return {}


def calculate_cumulative_profit_with_baseline(data):
    """
    Calculate cumulative profit curves with system baseline cost at position 0.

    For VIZ03: Shows how profit accumulates from position 0 (system baseline investment)
    through the disassembly sequence.

    Returns:
        DataFrame with columns: system, automation_level, product_mix, position,
                                cumulative_profit, component_name
    """
    df_process = data['df_process'].copy()
    df_system = data['df_system'].copy()

    # Get system baseline costs (VAL04)
    system_baseline = df_system[['system', 'VAL04']].drop_duplicates()
    system_baseline = system_baseline.rename(columns={'VAL04': 'system_baseline_cost'})

    # Get component aggregates with PROFIT
    df_component_agg = calculate_component_aggregates(data)

    # Load disassembly paths to get sequence order
    path_config = load_disassembly_paths()

    # Load mappings from config
    mappings = load_mappings()
    product_mix_to_type = mappings['product_mix_types']['mapping']

    all_curves = []

    # For each system (aggregate across ALL automation levels)
    for system in df_component_agg['system'].unique():
        df_sys = df_component_agg[df_component_agg['system'] == system].copy()

        # Get system baseline cost
        baseline_row = system_baseline[system_baseline['system'] == system]
        if baseline_row.empty:
            baseline_cost = 0
        else:
            baseline_cost = baseline_row['system_baseline_cost'].iloc[0]

        # For each product_mix and product_type combination in the data
        # (product mixes can contain multiple product types)
        for product_mix in df_sys['product_mix'].unique():
            df_mix = df_sys[df_sys['product_mix'] == product_mix].copy()

            # Get all product types in this product_mix
            for product_type in df_mix['product_type'].unique():
                # Filter to this product_type
                df_type = df_mix[df_mix['product_type'] == product_type].copy()

                # Get step-based sequence
                if product_type not in path_config:
                    print(f"WARNING: '{product_type}' not found in path_config, skipping")
                    continue

                if 'disassembly_steps' not in path_config[product_type]:
                    print(f"WARNING: '{product_type}' missing disassembly_steps, skipping")
                    continue

                steps_config = path_config[product_type]['disassembly_steps']

                # Map components to steps
                comp_to_step = map_components_to_steps(product_type, path_config)

                # Calculate per-component profit (average across ALL experiments and automation levels)
                component_stats = df_type.groupby('step_name').agg({
                    'mean_profit': 'mean',  # Average profit per component
                    'n_components': 'mean'   # Average count
                }).reset_index()

                # Create dict of component -> per-component profit
                component_profits = dict(zip(component_stats['step_name'], component_stats['mean_profit']))

                # Load component values from attributes file (for components not in simulation)
                component_values_from_attrs = load_component_values()

                # Override with attribute values for CAR components (initial cost)
                prefix_car = data['formatting_config']['naming_conventions']['prefix_car_component']
                for comp_name in component_values_from_attrs:
                    if comp_name.startswith(prefix_car):
                        component_profits[comp_name] = component_values_from_attrs[comp_name]

                # Calculate values for virtual components (not in simulation data)
                # Virtual components are identified by having steps that consume them but not being in simulation
                virtual_components = {}
                for step in steps_config:
                    if 'consumes' in step:
                        parent = step['consumes']['component']
                        if parent not in component_profits:  # Not in simulation = virtual component
                            # Find all children that consume this parent
                            children = [s['step_name'] for s in steps_config
                                       if s.get('consumes', {}).get('component') == parent]
                            # Calculate virtual component value as sum of children's actual profits
                            virtual_value = sum(component_profits.get(child, 0) for child in children)
                            virtual_components[parent] = virtual_value

                # Unified lookup function for both real (simulation) and virtual components
                def get_component_value(comp_name):
                    if comp_name in component_profits:
                        return component_profits[comp_name]  # Real component from simulation
                    elif comp_name in virtual_components:
                        return virtual_components[comp_name]  # Virtual component = sum of children
                    else:
                        return 0

                # Step 0: System baseline (negative cost)
                curve_data = [{
                    'system': system,
                    'step_id': '0',
                    'product_mix': product_mix,
                    'product_type': product_type,
                    'branch_id': 'baseline',
                    'component_name': 'SYSTEM_BASELINE',
                    'profit': -baseline_cost,
                    'cumulative_profit': -baseline_cost
                }]

                cumulative = -baseline_cost

                # Add profit for each disassembly step (aggregates all components released)
                for step in steps_config:
                    step_id = step['step_id']
                    step_name = step['step_name']
                    branch_id = step['branch_id']
                    components_released = step['components_released']

                    # Calculate released value (sum profits for ALL components released)
                    released_value = sum(component_profits.get(comp, 0) for comp in components_released)

                    # Calculate consumed value (cost of destroying parent component)
                    consumed_value = 0
                    consumption_label = ""
                    if 'consumes' in step:
                        consumed_comp = step['consumes']['component']
                        consumed_pct = step['consumes']['percentage']
                        # Get the actual value of the consumed component (from simulation or calculated virtual)
                        consumed_comp_value = get_component_value(consumed_comp)
                        consumed_value = consumed_comp_value * consumed_pct
                        consumption_label = f" [-{consumed_comp}({int(consumed_pct*100)}%)]"

                    # Net profit = released value - consumed value
                    step_profit = released_value - consumed_value
                    cumulative += step_profit

                    # Component names for display (show all released + consumption)
                    comp_names = ', '.join(components_released) + consumption_label

                    curve_data.append({
                        'system': system,
                        'step_id': step_id,
                        'product_mix': product_mix,
                        'product_type': product_type,
                        'branch_id': branch_id,
                        'component_name': comp_names,  # All components released + consumption indicator
                        'profit': step_profit,
                        'cumulative_profit': cumulative
                    })

                all_curves.extend(curve_data)

    df_curves = pd.DataFrame(all_curves)

    # Aggregate across product_mixes: average profit/cumulative_profit per (system, product_type, step_id, branch_id, component_name)
    # This gives ONE curve per product_type, preserving each component as a separate row
    group_cols = ['system', 'step_id', 'product_type', 'branch_id', 'component_name']

    agg_dict = {
        'profit': 'mean',
        'cumulative_profit': 'mean'
    }

    df_curves = df_curves.groupby(group_cols, as_index=False).agg(agg_dict)

    # Round numeric columns
    numeric_cols = df_curves.select_dtypes(include=[np.number]).columns
    df_curves[numeric_cols] = df_curves[numeric_cols].round(2)

    return df_curves


def calculate_product_specific_trajectories(df_component_agg, path_config):
    """
    Calculate component values for each system, automation level, and product type.
    Groups by specific_product_type (car_hd, car_tl, car_sa, car_rd) which was classified
    based on component signatures in calculate_component_aggregates().

    Aggregates across all experiments and product_mixes that contain each product type,
    providing average trajectories for each of the 4 vehicle types.

    Args:
        df_component_agg: Component aggregates from calculate_component_aggregates()
                         (must include 'specific_product_type' column)
        path_config: Disassembly path configuration (from load_disassembly_paths())

    Returns:
        DataFrame with system-automation-product type specific trajectories
    """
    all_trajectories = []

    # Load mappings from config
    mappings = load_mappings()
    product_mix_to_type = mappings['product_mix_types']['mapping']

    # Process all data without automation level separation
    df_component_agg = df_component_agg.copy()

    # For each system (aggregate across ALL automation levels)
    for system in df_component_agg['system'].unique():
        df_sys = df_component_agg[df_component_agg['system'] == system].copy()

        # For each specific product type (load from config)
        product_type_config = load_product_types()
        target_product_types = product_type_config['available']

        for product_type in target_product_types:
            # Filter to this product_type
            df_product = df_sys[df_sys['product_type'] == product_type].copy()

            if df_product.empty:
                continue

            # Calculate stats per component for this specific product type (across ALL automation levels)
            component_stats = df_product.groupby('step_name').agg({
                'mean_revenue': ['mean', 'std'],
                'mean_cost': ['mean', 'std'],
                'mean_profit': ['mean', 'std']
            }).reset_index()

            # Flatten columns
            component_stats.columns = ['_'.join(col).strip() if col[1] else col[0] for col in component_stats.columns.values]

            # Create dictionaries for component -> stats lookup
            component_revenue_mean = dict(zip(component_stats['step_name'], component_stats['mean_revenue_mean']))
            component_revenue_std = dict(zip(component_stats['step_name'], component_stats['mean_revenue_std']))
            component_cost_mean = dict(zip(component_stats['step_name'], component_stats['mean_cost_mean']))
            component_cost_std = dict(zip(component_stats['step_name'], component_stats['mean_cost_std']))
            component_profit_mean = dict(zip(component_stats['step_name'], component_stats['mean_profit_mean']))
            component_profit_std = dict(zip(component_stats['step_name'], component_stats['mean_profit_std']))

            # Get step-based sequence from config (config-driven approach)
            if product_type not in path_config or 'disassembly_steps' not in path_config[product_type]:
                print(f"WARNING: '{product_type}' missing disassembly_steps, skipping")
                continue

            steps_config = path_config[product_type]['disassembly_steps']

            # Build stats for each step from config
            step_rows = []
            cumulative_revenue = 0
            cumulative_cost = 0
            cumulative_profit = 0

            for step in steps_config:
                step_id = step['step_id']
                step_name = step['step_name']
                branch_id = step['branch_id']
                components_released = step['components_released']
                passive_components = step.get('passive_components', [])

                # Sum stats for ALL components released in this step
                step_revenue = sum(component_revenue_mean.get(comp, 0) for comp in components_released)
                step_revenue_std = np.sqrt(sum(component_revenue_std.get(comp, 0)**2 for comp in components_released))
                step_cost = sum(component_cost_mean.get(comp, 0) for comp in components_released)
                step_cost_std = np.sqrt(sum(component_cost_std.get(comp, 0)**2 for comp in components_released))
                step_profit = sum(component_profit_mean.get(comp, 0) for comp in components_released)
                step_profit_std = np.sqrt(sum(component_profit_std.get(comp, 0)**2 for comp in components_released))

                # Update cumulative values
                cumulative_revenue += step_revenue
                cumulative_cost += step_cost
                cumulative_profit += step_profit

                # Create row for this step
                step_rows.append({
                    'component': step_name,  # Keep step_name as component for consistency
                    'step_id': step_id,
                    'branch_id': branch_id,
                    'is_passive': len(passive_components) > 0,
                    'mean_revenue': step_revenue,
                    'std_revenue': step_revenue_std,
                    'mean_cost': step_cost,
                    'std_cost': step_cost_std,
                    'mean_profit': step_profit,
                    'std_profit': step_profit_std,
                    'cumulative_revenue': cumulative_revenue,
                    'cumulative_cost': cumulative_cost,
                    'cumulative_profit': cumulative_profit
                })

            # Create dataframe from step rows
            stats = pd.DataFrame(step_rows)

            # Add metadata
            stats['system'] = system
            stats['product_type'] = product_type

            # Rename step_name to component for consistency
            stats = stats.rename(columns={'step_name': 'component'})

            # Select final columns (step_id early for easier filtering/sorting) - NO automation_level
            result_cols = [
                'system', 'step_id', 'product_type',
                'component', 'branch_id', 'is_passive',
                'mean_profit', 'std_profit', 'cumulative_profit',
                'mean_revenue', 'std_revenue', 'cumulative_revenue',
                'mean_cost', 'std_cost', 'cumulative_cost'
            ]

            stats = stats[result_cols]

            all_trajectories.append(stats)

    # Concatenate all trajectories
    if all_trajectories:
        df_result = pd.concat(all_trajectories, ignore_index=True)

        # Round numeric columns
        numeric_cols = df_result.select_dtypes(include=[np.number]).columns
        df_result[numeric_cols] = df_result[numeric_cols].round(2)

        # Fill NaN std with 0 (single experiment case)
        std_cols = [col for col in df_result.columns if col.startswith('std_')]
        df_result[std_cols] = df_result[std_cols].fillna(0)

        return df_result
    else:
        return pd.DataFrame()


# ====================
# 3. COMPONENT STEP AGGREGATION
# ====================

def aggregate_components_by_step(df_product_trajectories):
    """
    Aggregate components by step, summing profit/revenue/cost for all components in the same step.

    This creates a step-level view where multiple components in the same step are combined into
    a single row with summed values. Used for VIZ02 where each step should show as one point.

    Args:
        df_product_trajectories: DataFrame from calculate_product_specific_trajectories()

    Returns:
        DataFrame with one row per (system, product_type, step_id, branch_id)
    """
    df = df_product_trajectories.copy()

    # Group by step-level identifiers (step_id early for easier filtering/sorting) - NO automation_level
    group_cols = ['system', 'step_id', 'product_type', 'branch_id']

    # Aggregate: sum the mean values, drop std and cumulative (not meaningful when aggregating)
    agg_dict = {
        'mean_profit': 'sum',
        'mean_revenue': 'sum',
        'mean_cost': 'sum',
        'component': lambda x: ', '.join(sorted(x)),  # Combine component names
        'is_passive': 'first'  # Keep first value (should be same for all components in step)
    }

    df_step_agg = df.groupby(group_cols, as_index=False).agg(agg_dict)

    # Rename aggregated columns for clarity
    df_step_agg = df_step_agg.rename(columns={
        'mean_profit': 'step_profit',
        'mean_revenue': 'step_revenue',
        'mean_cost': 'step_cost',
        'component': 'components'  # Now contains comma-separated list
    })

    # Sort by system, product_type, then step_id hierarchy
    df_step_agg['sort_key'] = df_step_agg['step_id'].apply(sort_key_for_step_id)
    df_step_agg = df_step_agg.sort_values(['system', 'product_type', 'sort_key'])
    df_step_agg = df_step_agg.drop('sort_key', axis=1)

    return df_step_agg


# ====================
# 5. MAIN MODULE ORCHESTRATION
# ====================

def run_module5(data, save_output=False):
    """
    Main Module 5 orchestration function.
    """
    print("[Module 5] Generating depth analysis and reports...")

    # Phase 1: Component-level depth analysis
    print("  Calculating component aggregates...")
    df_component_agg = calculate_component_aggregates(data)
    data['depth_component_analysis'] = df_component_agg
    print(f"  [OK] Calculated {len(df_component_agg)} component-experiment combinations")

    # Phase 1b: Aggregate to step-level per experiment
    print("  Aggregating components by step per experiment...")
    df_step_agg_per_exp = aggregate_by_step(df_component_agg)
    data['depth_step_per_experiment'] = df_step_agg_per_exp
    print(f"  [OK] Aggregated to {len(df_step_agg_per_exp)} step-experiment combinations")

    # Phase 2: Extract disassembly sequence
    print("  Extracting disassembly sequence...")
    step_order = extract_disassembly_sequence(data)
    data['disassembly_sequence'] = step_order
    print(f"  [OK] Extracted sequence with {len(step_order)} steps")

    # Phase 2b: Load disassembly path configuration
    print("  Loading disassembly path configuration...")
    path_config = load_disassembly_paths()
    print(f"  [OK] Loaded paths for {len(path_config)} product types")

    # Phase 3: Product-specific trajectories
    print("  Calculating product-specific trajectories...")
    df_product_trajectories = calculate_product_specific_trajectories(df_component_agg, path_config)
    data['depth_product_cumulative'] = df_product_trajectories
    print(f"  [OK] Calculated product trajectories for {len(df_product_trajectories)} combinations")

    # Phase 4: Aggregate components by step (for VIZ02)
    print("  Aggregating components by step...")
    df_step_aggregated = aggregate_components_by_step(df_product_trajectories)
    data['depth_step_aggregated'] = df_step_aggregated
    print(f"  [OK] Aggregated to {len(df_step_aggregated)} step-level combinations")

    # Phase 5: Cumulative profit with system baseline (for VIZ03)
    print("  Calculating cumulative profit curves with baseline...")
    df_profit_curves = calculate_cumulative_profit_with_baseline(data)
    data['depth_profit_with_baseline'] = df_profit_curves
    print(f"  [OK] Calculated profit curves for {len(df_profit_curves)} combinations")

    # ====================
    # Save output files (optional)
    # ====================
    if save_output:
        try:
            # Save depth analysis dataframes
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            if not df_component_agg.empty:
                df_component_agg.to_csv(OUTPUT_DIR / OUTPUT_FILES['component'], index=False)
                print(f"\n  [OK] Saved: {OUTPUT_FILES['component']}")

            if not df_step_agg_per_exp.empty:
                df_step_agg_per_exp.to_csv(OUTPUT_DIR / OUTPUT_FILES['step_per_exp'], index=False)
                print(f"  [OK] Saved: {OUTPUT_FILES['step_per_exp']}")

            if not df_product_trajectories.empty:
                df_product_trajectories.to_csv(OUTPUT_DIR / OUTPUT_FILES['product_cumulative'], index=False)
                print(f"  [OK] Saved: {OUTPUT_FILES['product_cumulative']}")

            if not df_step_aggregated.empty:
                df_step_aggregated.to_csv(OUTPUT_DIR / OUTPUT_FILES['step_aggregated'], index=False)
                print(f"  [OK] Saved: {OUTPUT_FILES['step_aggregated']}")

            if not df_profit_curves.empty:
                df_profit_curves.to_csv(OUTPUT_DIR / OUTPUT_FILES['profit_baseline'], index=False)
                print(f"  [OK] Saved: {OUTPUT_FILES['profit_baseline']}")

        except Exception as e:
            print(f"  [ERROR] Failed to save output files: {e}")

    return data


if __name__ == '__main__':
    # Test Module 5 standalone
    from module0_data_loader import load_all_data
    from module1_step_indicators import calculate_indicators
    from module2_experiment_aggregation import run_module2
    from module3_ranking import run_module3

    data = load_all_data()
    data = calculate_indicators(data, save_output=False)
    data = run_module2(data, save_output=False)
    data = run_module3(data, save_output=False)
    data = run_module5(data, save_output=True)

    print("\nModule 5 test complete!")
