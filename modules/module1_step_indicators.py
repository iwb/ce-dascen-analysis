"""
Module 1: Indicator Calculator

PURPOSE:
- Calculate indicators for each row in the dataframes
- Add indicator columns to df_process, df_product, and df_resource
- Use config-driven approach: formulas and lookups defined in config_indicators.json

INPUTS (from Module 0):
- data['df_process']: Combined process dataframe
- data['df_product']: Combined product dataframe
- data['df_resource']: Combined resource (stations) dataframe
- data['indicators']: Indicator configuration
- data['attributes']: Attribute tables (product, process, system)

OUTPUTS:
- Enhanced dataframes with new indicator columns
- Saved CSV files for verification
"""

from pathlib import Path
import json

# ====================
# CONSTANTS AND CONFIGURATION
# ====================

# Directory paths
DEFAULT_CONFIG_DIR = 'data/config'
DEFAULT_OUTPUT_DIR = 'output'
DATAFRAMES_SUBDIR = 'dataframes'

# Configuration filenames
CONFIG_MAPPINGS_FILE = 'config_mappings.json'

# Source types for variable lookups
SOURCE_DATAFRAME = 'dataframe'
SOURCE_ATTRIBUTE_FILE = 'attribute_file'
SOURCE_QUALITY_RANGE = 'quality_range'
SOURCE_QUALITY_THRESHOLD = 'quality_threshold'

# Attribute file references
ATTR_FILE_PROCESS = 'attributes_process.json'
ATTR_FILE_SYSTEMS = 'attributes_systems.json'
ATTR_FILE_PRODUCT = 'attributes_product.json'

# Attribute table names (without prefix/suffix)
TABLE_PROCESS = 'process'
TABLE_SYSTEMS = 'systems'
TABLE_PRODUCT = 'product'

# JSON keys
KEY_ATTRIBUTE_STRUCTURE = 'attribute_structure'
KEY_MAPPING = 'mapping'
KEY_INDICATORS = 'indicators'
KEY_VALUES = 'values'
KEY_SPECIAL_VALUES = 'special_values'

# Variable config keys
VAR_SOURCE = 'source'
VAR_COLUMN = 'column'
VAR_FILE = 'file'
VAR_LOOKUP_COLUMNS = 'lookup_columns'
VAR_VALUE_PATH = 'value_path'
VAR_LOOKUP_COLUMN = 'lookup_column'
VAR_QUALITY_COLUMN = 'quality_column'
VAR_VALUE_KEY = 'value_key'

# Indicator config keys
IND_TARGET_DATAFRAME = 'target_dataframe'
IND_INDICATOR_ID = 'indicator_id'
IND_FORMULA = 'formula'
IND_INDICATOR_VARIABLES = 'indicator_variables'

# Value config keys
VAL_TARGET_DATAFRAME = 'target_dataframe'
VAL_VALUE_ID = 'value_id'
VAL_VALUE_NAME = 'value_name'
VAL_FORMULA = 'formula'
VAL_VALUE_VARIABLES = 'value_variables'
VAL_CATEGORY = 'category'

# Categories for values
CATEGORY_COST_FACTOR = 'cost_factor'
CATEGORY_AGGREGATE = 'aggregate'

# Quality range keys
QUALITY_MIN = 'quality_min'
QUALITY_MAX = 'quality_max'

# Component keys
COMPONENT_NAME = 'component_name'

# End of life options path
EOL_OPTIONS = 'end_of_life_options'

# Numeric precision
VALUE_PRECISION = 2

# Default values
DEFAULT_VALUE = 0

# Output filenames (Module 1)
MODULE1_PREFIX = 'M1_'
DF_PROCESS_WITH_IND_OUTPUT = 'M1_01_df_process_with_indicators.csv'
DF_PRODUCT_WITH_IND_OUTPUT = 'M1_02_df_product_with_indicators.csv'
DF_RESOURCE_WITH_IND_OUTPUT = 'M1_03_df_resource_with_indicators.csv'
DF_SYSTEM_WITH_IND_OUTPUT = 'M1_04_df_system_with_indicators.csv'

# Data dictionary keys (to match module 0)
KEY_DF_PROCESS = 'df_process'
KEY_DF_PRODUCT = 'df_product'
KEY_DF_RESOURCE = 'df_resource'
KEY_DF_SYSTEM = 'df_system'

def load_attribute_structure():
    """
    Load attribute structure mapping from config_mappings.json.

    Returns:
        dict: Attribute structure mapping

    Raises:
        FileNotFoundError: If config_mappings.json doesn't exist
        json.JSONDecodeError: If JSON file is malformed
        KeyError: If required keys are missing
    """
    config_path = Path(__file__).parent.parent / DEFAULT_CONFIG_DIR / CONFIG_MAPPINGS_FILE

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config mappings not found at {config_path}\n"
            f"Please ensure {CONFIG_MAPPINGS_FILE} exists in {DEFAULT_CONFIG_DIR}/"
        )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {config_path}: {e.msg}",
            e.doc, e.pos
        )

    if KEY_ATTRIBUTE_STRUCTURE not in mappings:
        raise KeyError(f"Missing '{KEY_ATTRIBUTE_STRUCTURE}' key in {CONFIG_MAPPINGS_FILE}")
    if KEY_MAPPING not in mappings[KEY_ATTRIBUTE_STRUCTURE]:
        raise KeyError(f"Missing '{KEY_MAPPING}' key in {KEY_ATTRIBUTE_STRUCTURE}")

    return mappings[KEY_ATTRIBUTE_STRUCTURE][KEY_MAPPING]


def evaluate_formula_for_row(row, formula, variables, data, attr_structure, context_info=""):
    """
    Shared function to evaluate a formula for a given row.

    This function is used by both indicator and value calculations to avoid code duplication.
    It builds the variable dictionary and evaluates the formula with error handling.

    Args:
        row: DataFrame row being processed
        formula: Formula string to evaluate
        variables: Dictionary of variable configurations
        data: Main data dictionary with attributes and dataframes
        attr_structure: Attribute structure mapping for lookups
        context_info: String for debugging (e.g., "IND01" or "VAL02")

    Returns:
        float: Calculated value rounded to 2 decimal places, or 0 on error
    """
    # ====================
    # 1. Build variable dictionary
    # ====================
    var_values = {}
    for var_name, var_config in variables.items():
        try:
            var_values[var_name] = get_variable_value(row, var_name, var_config, data, attr_structure)
        except Exception as e:
            # Log warning for debugging but continue with default value
            if context_info:
                print(f"      [WARNING] {context_info}: Variable '{var_name}' lookup failed, using {DEFAULT_VALUE}")
            var_values[var_name] = DEFAULT_VALUE

    # ====================
    # 2. Evaluate formula and return result
    # ====================
    try:
        result = eval(formula, {"__builtins__": {}}, var_values)
        if result is not None:
            return round(result, VALUE_PRECISION)
        return DEFAULT_VALUE
    except Exception as e:
        # Log error for debugging
        if context_info:
            print(f"      [WARNING] {context_info}: Formula evaluation failed: {e}")
        return DEFAULT_VALUE


def get_variable_value(row, var_name, var_config, data, attr_structure):
    """
    Get variable value based on simplified config specification.

    Args:
        row: DataFrame row being processed
        var_name: Variable name
        var_config: Variable configuration from indicators config
        data: Full data dictionary from Module 0
        attr_structure: Attribute structure mapping from config_mappings.json

    Returns:
        Value for the variable (numeric)

    Raises:
        KeyError: If required config keys are missing
        ValueError: If source type is unknown
    """

    # Validate required config key
    if VAR_SOURCE not in var_config:
        raise KeyError(f"Variable '{var_name}' missing required '{VAR_SOURCE}' key in config")

    source = var_config[VAR_SOURCE]

    # ====================
    # 1. Column lookup from current row
    # ====================
    if source == SOURCE_DATAFRAME:
        if VAR_COLUMN not in var_config:
            raise KeyError(f"Variable '{var_name}' with source='{SOURCE_DATAFRAME}' missing '{VAR_COLUMN}' key")
        col_name = var_config[VAR_COLUMN]
        if col_name not in row:
            raise KeyError(f"Column '{col_name}' not found in dataframe row for variable '{var_name}'")
        return row[col_name]

    # ====================
    # 2. Attribute file lookup (process/system/product tables)
    # ====================
    elif source == SOURCE_ATTRIBUTE_FILE:
        # Validate required keys
        if VAR_FILE not in var_config:
            raise KeyError(f"Variable '{var_name}' with source='{SOURCE_ATTRIBUTE_FILE}' missing '{VAR_FILE}' key")
        if VAR_LOOKUP_COLUMNS not in var_config:
            raise KeyError(f"Variable '{var_name}' with source='{SOURCE_ATTRIBUTE_FILE}' missing '{VAR_LOOKUP_COLUMNS}' key")
        if VAR_VALUE_PATH not in var_config:
            raise KeyError(f"Variable '{var_name}' with source='{SOURCE_ATTRIBUTE_FILE}' missing '{VAR_VALUE_PATH}' key")

        file = var_config[VAR_FILE]
        lookup_columns = var_config[VAR_LOOKUP_COLUMNS]
        value_path = var_config[VAR_VALUE_PATH]

        # Extract attribute table name from filename (e.g., "attributes_process.json" -> "process")
        table_name = file.replace('attributes_', '').replace('.json', '')

        # Get lookup values from current row
        lookup_values = {}
        for col in lookup_columns:
            if col not in row:
                raise KeyError(f"Lookup column '{col}' not found in row for variable '{var_name}'")
            lookup_values[col] = row[col]

        # Find matching entry in attribute table
        # Handle different table structures using config-driven structure keys
        if table_name == TABLE_PROCESS:
            structure_key = attr_structure[TABLE_PROCESS]
            attr_table = data['attributes'][TABLE_PROCESS][structure_key]
        elif table_name == TABLE_SYSTEMS:
            structure_key = attr_structure[TABLE_SYSTEMS]
            attr_table = data['attributes'][TABLE_SYSTEMS][structure_key]
        elif table_name == TABLE_PRODUCT:
            # For fixed attributes (like weight), navigate to component first
            step_name = row[lookup_columns[0]]  # Assuming first column is step_name
            structure_key = attr_structure[TABLE_PRODUCT]
            attr_table = data['attributes'][TABLE_PRODUCT][structure_key]

            for component in attr_table:
                if component[COMPONENT_NAME] == step_name:
                    # Navigate nested path (e.g., "fixed_attributes.weight.value")
                    value = component
                    for path_part in value_path.split('.'):
                        value = value.get(path_part, DEFAULT_VALUE)
                    return value if value is not None else DEFAULT_VALUE
            return DEFAULT_VALUE
        else:
            return DEFAULT_VALUE  # Unknown table

        # For process and system tables
        for entry in attr_table:
            # Check if all lookup keys match
            if all(entry.get(k) == v for k, v in lookup_values.items()):
                # Navigate nested path (e.g., "cost_rates.running.power_rating")
                value = entry
                for path_part in value_path.split('.'):
                    value = value.get(path_part, DEFAULT_VALUE)
                return value if value is not None else DEFAULT_VALUE

        return DEFAULT_VALUE  # Not found

    # ====================
    # 3. Quality-based value lookup (quality ranges)
    # ====================
    elif source == SOURCE_QUALITY_RANGE:
        # Validate required keys
        for key in [VAR_FILE, VAR_LOOKUP_COLUMN, VAR_QUALITY_COLUMN, VAR_VALUE_PATH, VAR_VALUE_KEY]:
            if key not in var_config:
                raise KeyError(f"Variable '{var_name}' with source='{SOURCE_QUALITY_RANGE}' missing '{key}' key")

        file = var_config[VAR_FILE]
        lookup_column = var_config[VAR_LOOKUP_COLUMN]
        quality_column = var_config[VAR_QUALITY_COLUMN]
        value_path = var_config[VAR_VALUE_PATH]
        value_key = var_config[VAR_VALUE_KEY]

        # Get step_name and quality from current row
        if lookup_column not in row:
            raise KeyError(f"Lookup column '{lookup_column}' not found in row for variable '{var_name}'")
        if quality_column not in row:
            raise KeyError(f"Quality column '{quality_column}' not found in row for variable '{var_name}'")
        step_name = row[lookup_column]
        quality = row[quality_column]

        # Find component in attribute table using config-driven structure key
        structure_key = attr_structure[TABLE_PRODUCT]
        attr_table = data['attributes'][TABLE_PRODUCT][structure_key]

        for component in attr_table:
            if component[COMPONENT_NAME] == step_name:
                # Navigate to quality-dependent attribute array
                attr_data = component
                for path_part in value_path.split('.'):
                    attr_data = attr_data.get(path_part, [])

                # attr_data should now be an array of quality ranges
                if isinstance(attr_data, list):
                    # Find matching quality range
                    for range_entry in attr_data:
                        q_min = range_entry.get(QUALITY_MIN, 0)
                        q_max = range_entry.get(QUALITY_MAX, 1)

                        # Check if quality falls within this range
                        if q_min <= quality <= q_max:
                            return range_entry.get(value_key, DEFAULT_VALUE)

                break  # Component found, no matching quality range

        return DEFAULT_VALUE  # Component not found or quality not matched

    # ====================
    # 4. Quality-based circularity lookup (quality thresholds)
    # ====================
    elif source == SOURCE_QUALITY_THRESHOLD:
        # Validate required keys
        for key in [VAR_FILE, VAR_LOOKUP_COLUMN, VAR_QUALITY_COLUMN, VAR_VALUE_PATH, VAR_VALUE_KEY]:
            if key not in var_config:
                raise KeyError(f"Variable '{var_name}' with source='{SOURCE_QUALITY_THRESHOLD}' missing '{key}' key")

        file = var_config[VAR_FILE]
        lookup_column = var_config[VAR_LOOKUP_COLUMN]
        quality_column = var_config[VAR_QUALITY_COLUMN]
        value_path = var_config[VAR_VALUE_PATH]
        value_key = var_config[VAR_VALUE_KEY]

        # Get step_name and quality from current row
        if lookup_column not in row:
            raise KeyError(f"Lookup column '{lookup_column}' not found in row for variable '{var_name}'")
        if quality_column not in row:
            raise KeyError(f"Quality column '{quality_column}' not found in row for variable '{var_name}'")
        step_name = row[lookup_column]
        quality = row[quality_column]

        # Find component in attribute table using config-driven structure key
        structure_key = attr_structure[TABLE_PRODUCT]
        attr_table = data['attributes'][TABLE_PRODUCT][structure_key]

        for component in attr_table:
            if component[COMPONENT_NAME] == step_name:
                # Navigate to end_of_life_options (should be a dict with recycle/remanufacture/reuse)
                eol_options = component.get(value_path, {})

                # Check which option the quality falls into
                for option_name, option_data in eol_options.items():
                    q_min = option_data.get(QUALITY_MIN, 0)
                    q_max = option_data.get(QUALITY_MAX, 1)

                    if q_min <= quality <= q_max:
                        return option_data.get(value_key, DEFAULT_VALUE)

                break  # Component found, no matching quality range

        return DEFAULT_VALUE  # Component not found or quality not matched

    # Unknown source type
    else:
        raise ValueError(f"Unknown source type '{source}' for variable '{var_name}'")


def calculate_indicators(data, save_output=False):
    """
    Calculate all indicators based on config and add columns to dataframes.

    Args:
        data: Data dictionary from Module 0
        save_output: If True, save enhanced dataframes to output folder (debug only)

    Returns:
        data: Enhanced data dictionary with indicator columns added
    """

    print("[Module 1] Calculating indicators...")

    # ====================
    # 1. Load configuration and setup
    # ====================
    # Load attribute structure mapping from config
    attr_structure = load_attribute_structure()
    indicators_config = data[KEY_INDICATORS][KEY_INDICATORS]

    # ====================
    # 2. Group indicators by target dataframe
    # ====================
    indicators_by_df = {}
    for indicator in indicators_config:
        target_df = indicator[IND_TARGET_DATAFRAME]
        if target_df not in indicators_by_df:
            indicators_by_df[target_df] = []
        indicators_by_df[target_df].append(indicator)

    # ====================
    # 3. Calculate indicators for each dataframe
    # ====================

    for df_name, indicators in indicators_by_df.items():
        print(f"\n  Processing {df_name} ({len(data[df_name])} rows)...")

        for indicator in indicators:
            ind_id = indicator[IND_INDICATOR_ID]
            formula = indicator[IND_FORMULA]
            variables = indicator[IND_INDICATOR_VARIABLES]

            # Use shared function for row calculation with context info for debugging
            calc_row = lambda row: evaluate_formula_for_row(row, formula, variables, data, attr_structure, ind_id)

            # Apply calculation to all rows and add as new column
            data[df_name][ind_id] = data[df_name].apply(calc_row, axis=1)
            print(f"    [OK] {ind_id}")

    print(f"\n  [OK] All indicators calculated")

    # ====================
    # 4. Calculate values (VAL01-VAL04 + special values)
    # ====================
    print(f"\n[Module 1] Calculating values...")

    # Combine both regular values and special values (REVENUE, COSTS_FIX, COSTS_VAR, PROFIT)
    regular_values = data[KEY_VALUES][KEY_VALUES]
    special_values = data[KEY_VALUES][KEY_SPECIAL_VALUES]
    all_values = regular_values + special_values

    # Group values by target dataframe
    values_by_df = {}
    for value in all_values:
        target_df = value[VAL_TARGET_DATAFRAME]
        if target_df not in values_by_df:
            values_by_df[target_df] = []
        values_by_df[target_df].append(value)

    # Calculate values in dependency order (cost factors first, then aggregates)
    for df_name, values in values_by_df.items():
        print(f"\n  Processing {df_name} ({len(data[df_name])} rows)...")

        # Sort values by category to ensure dependencies are met
        # cost_factor values must be calculated before aggregate values
        cost_factors = [v for v in values if v[VAL_CATEGORY] == CATEGORY_COST_FACTOR]
        aggregates = [v for v in values if v[VAL_CATEGORY] == CATEGORY_AGGREGATE]
        ordered_values = cost_factors + aggregates

        for value in ordered_values:
            # Get value identifier (value_id for regular values, value_name for special values)
            value_col = value.get(VAL_VALUE_ID, value.get(VAL_VALUE_NAME))
            formula = value[VAL_FORMULA]
            variables = value[VAL_VALUE_VARIABLES]

            # Use shared function for row calculation with context info for debugging
            calc_row = lambda row: evaluate_formula_for_row(row, formula, variables, data, attr_structure, value_col)

            # Apply calculation to all rows and add as new column
            data[df_name][value_col] = data[df_name].apply(calc_row, axis=1)
            print(f"    [OK] {value_col}")

    print(f"\n  [OK] All values calculated")

    # ====================
    # 5. Save output (optional)
    # ====================
    if save_output:
        output_dir = Path(__file__).parent.parent / DEFAULT_OUTPUT_DIR / DATAFRAMES_SUBDIR
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save df_process with indicators
        if KEY_DF_PROCESS in data:
            output_file = output_dir / DF_PROCESS_WITH_IND_OUTPUT
            data[KEY_DF_PROCESS].to_csv(output_file, index=False)
            print(f"  [OK] Saved: {DF_PROCESS_WITH_IND_OUTPUT}")

        # Save df_product with indicators
        if KEY_DF_PRODUCT in data:
            output_file = output_dir / DF_PRODUCT_WITH_IND_OUTPUT
            data[KEY_DF_PRODUCT].to_csv(output_file, index=False)
            print(f"  [OK] Saved: {DF_PRODUCT_WITH_IND_OUTPUT}")

        # Save df_resource with indicators
        if KEY_DF_RESOURCE in data:
            output_file = output_dir / DF_RESOURCE_WITH_IND_OUTPUT
            data[KEY_DF_RESOURCE].to_csv(output_file, index=False)
            print(f"  [OK] Saved: {DF_RESOURCE_WITH_IND_OUTPUT}")

        # Save df_system with indicators
        if KEY_DF_SYSTEM in data:
            output_file = output_dir / DF_SYSTEM_WITH_IND_OUTPUT
            data[KEY_DF_SYSTEM].to_csv(output_file, index=False)
            print(f"  [OK] Saved: {DF_SYSTEM_WITH_IND_OUTPUT}")

    return data


if __name__ == '__main__':
    # Standalone execution - run modules 0 and 1 only
    from module0_data_loader import load_all_data

    print("Loading data...")
    data = load_all_data()

    print("\nCalculating indicators...")
    data = calculate_indicators(data, save_output=True)

    print("\nDone!")
