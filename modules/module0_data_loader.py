"""
Module 0: Data Loader

PURPOSE:
- Load all configuration files and preprocessed experiment data
- Combine individual experiment files into consolidated DataFrames
- Provide structured data for downstream analytics modules

INPUTS:
- data/config/config_indicators.json     # KPI definitions with formulas and weights
- data/config/config_groups.json         # Group definitions for statistics
- data/config/config_values.json         # Non-KPI supporting calculations
- data/config/doe_full_factorial_experiments.csv  # Design of experiments table
- data/attributes/attributes_*.json      # Product, process, system attributes
- data/processed/summary_process_*.csv   # Component-level process data
- data/processed/summary_product_*.csv   # Product-level throughput data
- data/processed/summary_stations_*.csv  # Station-level utilization data

OUTPUTS:
- Dictionary with loaded data:
  {
    'indicators': dict,       # KPI configurations from JSON
    'values': dict,          # Supporting value calculations
    'groups': dict,          # Group definitions
    'doe': pd.DataFrame,     # Design of experiments table
    'attributes': dict,      # Attribute lookup tables
    'df_process': pd.DataFrame,   # Combined process data (all experiments)
    'df_product': pd.DataFrame,   # Combined product data (all experiments)
    'df_resource': pd.DataFrame,  # Combined resource/station data (all experiments)
    'df_system': pd.DataFrame,    # System-level data (one row per experiment)
    'summary_process': dict,      # Original per-experiment process DataFrames
    'summary_product': dict,      # Original per-experiment product DataFrames
    'summary_stations': dict      # Original per-experiment station DataFrames
  }
"""

import pandas as pd
import json
from pathlib import Path

# ====================
# CONSTANTS AND CONFIGURATION
# ====================

# Directory paths
DEFAULT_CONFIG_DIR = 'data/config'
DEFAULT_DATA_DIR = 'data/processed'
DEFAULT_ATTR_DIR = 'data/attributes'
OUTPUT_DIR = 'output'
DATAFRAMES_SUBDIR = 'dataframes'

# Configuration filenames
CONFIG_INDICATORS_FILE = 'config_indicators.json'
CONFIG_GROUPS_FILE = 'config_groups.json'
CONFIG_VALUES_FILE = 'config_values.json'
DOE_FILE = 'doe_full_factorial_experiments.csv'
CONFIG_MAPPINGS_FILE = 'config_mappings.json'
CONFIG_FORMATTING_FILE = 'config_formatting.json'

# File patterns and prefixes
ATTRIBUTES_PREFIX = 'attributes_'
ATTRIBUTES_PATTERN = 'attributes_*.json'
SUMMARY_PROCESS_PREFIX = 'summary_process_'
SUMMARY_PRODUCT_PREFIX = 'summary_product_'
SUMMARY_STATIONS_PREFIX = 'summary_stations_'
FILE_EXTENSION_CSV = '.csv'
FILE_EXTENSION_JSON = '.json'

# Column names
EXP_ID_COLUMN = 'exp_id'

# Output filenames (Module 0)
MODULE0_PREFIX = 'M0_'
DF_PROCESS_OUTPUT = 'M0_01_df_process.csv'
DF_PRODUCT_OUTPUT = 'M0_02_df_product.csv'
DF_RESOURCE_OUTPUT = 'M0_03_df_resource.csv'
DF_SYSTEM_OUTPUT = 'M0_04_df_system.csv'

# Display settings
MAX_MISSING_FILES_DISPLAY = 5  # Number of missing files to show before truncating

# Data dictionary keys
KEY_INDICATORS = 'indicators'
KEY_VALUES = 'values'
KEY_GROUPS = 'groups'
KEY_DOE = 'doe'
KEY_ATTRIBUTES = 'attributes'
KEY_SUMMARY_PROCESS = 'summary_process'
KEY_SUMMARY_PRODUCT = 'summary_product'
KEY_SUMMARY_STATIONS = 'summary_stations'
KEY_DF_PROCESS = 'df_process'
KEY_DF_PRODUCT = 'df_product'
KEY_DF_RESOURCE = 'df_resource'
KEY_DF_SYSTEM = 'df_system'

def load_indicator_tables(config_dir=DEFAULT_CONFIG_DIR):
    """
    Load indicators from JSON config file.

    Returns:
        dict: Indicators configuration

    Raises:
        FileNotFoundError: If config_indicators.json doesn't exist
        json.JSONDecodeError: If JSON file is malformed
    """
    config_path = Path(__file__).parent.parent / config_dir / CONFIG_INDICATORS_FILE

    if not config_path.exists():
        raise FileNotFoundError(
            f"Indicators config not found at {config_path}\n"
            f"Please ensure {CONFIG_INDICATORS_FILE} exists in {config_dir}/"
        )

    try:
        with open(config_path, 'r') as f:
            indicators = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {config_path}: {e.msg}",
            e.doc, e.pos
        )

    return indicators


def load_doe_table(config_dir=DEFAULT_CONFIG_DIR):
    """
    Load the Design of Experiments master table.

    The DoE table contains the experimental design with all factors
    (system, product_mix, automation_level, etc.) for each experiment.

    Returns:
        pd.DataFrame: DoE table with all experiments

    Raises:
        FileNotFoundError: If DoE table doesn't exist at expected location
    """
    doe_path = Path(__file__).parent.parent / config_dir / DOE_FILE

    if not doe_path.exists():
        raise FileNotFoundError(
            f"DOE table not found at {doe_path}\n"
            f"Please run: python scripts/copy_experiment_data.py"
        )

    return pd.read_csv(doe_path)


def load_groups_config(config_dir=DEFAULT_CONFIG_DIR):
    """
    Load groups configuration from JSON.

    Returns:
        dict: Groups configuration

    Raises:
        FileNotFoundError: If config_groups.json doesn't exist
        json.JSONDecodeError: If JSON file is malformed
    """
    config_path = Path(__file__).parent.parent / config_dir / CONFIG_GROUPS_FILE

    if not config_path.exists():
        raise FileNotFoundError(
            f"Groups config not found at {config_path}\n"
            f"Please ensure {CONFIG_GROUPS_FILE} exists in {config_dir}/"
        )

    try:
        with open(config_path, 'r') as f:
            groups = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {config_path}: {e.msg}",
            e.doc, e.pos
        )

    return groups


def load_values_config(config_dir=DEFAULT_CONFIG_DIR):
    """
    Load values configuration from JSON.

    Values are descriptive calculations (VAL01-VAL07: labor_cost, fixed_cost, etc.)
    that are NOT used for ranking/AHP. They provide additional analytical value
    without thresholds or weights. Values use VAL prefix instead of IND.

    Returns:
        dict: Values configuration

    Raises:
        FileNotFoundError: If config_values.json doesn't exist
        json.JSONDecodeError: If JSON file is malformed
    """
    config_path = Path(__file__).parent.parent / config_dir / CONFIG_VALUES_FILE

    if not config_path.exists():
        raise FileNotFoundError(
            f"Values config not found at {config_path}\n"
            f"Please ensure {CONFIG_VALUES_FILE} exists in {config_dir}/"
        )

    try:
        with open(config_path, 'r') as f:
            values = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {config_path}: {e.msg}",
            e.doc, e.pos
        )

    return values


def load_formatting_config(config_dir=DEFAULT_CONFIG_DIR):
    """
    Load formatting configuration for display and output settings.

    Contains cross-module formatting parameters including decimal precision,
    console output settings, and naming conventions to achieve 100% config-driven
    architecture with no hardcoded display logic.

    Returns:
        dict: Formatting configuration with keys:
            - output_formatting: Precision settings (precision_decimals, score_precision)
            - console_output: Display parameters (separator_width, top_n_display)
            - naming_conventions: Standard labels and prefixes

    Raises:
        FileNotFoundError: If config_formatting.json doesn't exist
        ValueError: If required sections are missing
        json.JSONDecodeError: If JSON file is malformed
    """
    config_path = Path(__file__).parent.parent / config_dir / CONFIG_FORMATTING_FILE

    if not config_path.exists():
        raise FileNotFoundError(
            f"Formatting config not found at {config_path}\n"
            f"Please ensure {CONFIG_FORMATTING_FILE} exists in {config_dir}/"
        )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {config_path}: {e.msg}",
            e.doc, e.pos
        )

    # Validate required sections
    required_sections = ['output_formatting', 'console_output', 'naming_conventions']
    missing_sections = [section for section in required_sections if section not in config]

    if missing_sections:
        raise ValueError(
            f"Missing required sections in {config_path}: {', '.join(missing_sections)}\n"
            f"Required sections: {', '.join(required_sections)}"
        )

    return config


def load_attributes(attr_dir=DEFAULT_ATTR_DIR):
    """
    Load attribute JSON files.

    Returns:
        dict: {attr_type: attribute_data}

    Raises:
        FileNotFoundError: If attributes directory doesn't exist
        json.JSONDecodeError: If any JSON file is malformed
    """
    attr_path = Path(__file__).parent.parent / attr_dir

    if not attr_path.exists():
        raise FileNotFoundError(
            f"Attributes directory not found at {attr_path}\n"
            f"Please ensure {attr_dir}/ exists with {ATTRIBUTES_PATTERN} files"
        )

    attributes = {}
    attr_files = list(attr_path.glob(ATTRIBUTES_PATTERN))

    if not attr_files:
        raise FileNotFoundError(
            f"No attribute files found in {attr_path}\n"
            f"Expected files matching pattern: {ATTRIBUTES_PATTERN}"
        )

    for attr_file in attr_files:
        attr_type = attr_file.stem.replace(ATTRIBUTES_PREFIX, '')
        try:
            with open(attr_file, 'r') as f:
                attributes[attr_type] = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in {attr_file}: {e.msg}",
                e.doc, e.pos
            )

    return attributes

def load_preprocessed_data(exp_ids=None, data_dir=DEFAULT_DATA_DIR):
    """
    Load preprocessed summary files for specified experiments.

    Note: Missing files are logged as warnings but do not raise errors.
    This allows partial data loading if some summaries are unavailable.

    Args:
        exp_ids: List of experiment IDs or None to auto-detect

    Returns:
        dict: {
            'summary_process': {exp_id: DataFrame},
            'summary_product': {exp_id: DataFrame},
            'summary_stations': {exp_id: DataFrame}
        }
    """
    data_path = Path(__file__).parent.parent / data_dir

    # ====================
    # 1. Auto-detect experiments if needed
    # ====================
    if exp_ids is None:
        # Note: Only checking process files for auto-detection
        # Assumes process files are always present if experiment exists
        process_files = list(data_path.glob(f'{SUMMARY_PROCESS_PREFIX}*{FILE_EXTENSION_CSV}'))
        exp_ids = [f.stem.split('_')[-1] for f in process_files]

        if not exp_ids:
            print(f"[WARNING] No experiments found in {data_path}")
            print(f"          Expected files: {SUMMARY_PROCESS_PREFIX}*{FILE_EXTENSION_CSV}")

    preprocessed = {
        KEY_SUMMARY_PROCESS: {},
        KEY_SUMMARY_PRODUCT: {},
        KEY_SUMMARY_STATIONS: {}
    }

    # ====================
    # 2. Load each summary type for each experiment
    # ====================
    missing_files = []

    for exp_id in exp_ids:
        process_file = data_path / f'{SUMMARY_PROCESS_PREFIX}{exp_id}{FILE_EXTENSION_CSV}'
        product_file = data_path / f'{SUMMARY_PRODUCT_PREFIX}{exp_id}{FILE_EXTENSION_CSV}'
        stations_file = data_path / f'{SUMMARY_STATIONS_PREFIX}{exp_id}{FILE_EXTENSION_CSV}'

        # Check and load process file
        if process_file.exists():
            preprocessed[KEY_SUMMARY_PROCESS][exp_id] = pd.read_csv(process_file)
        else:
            missing_files.append(f'{SUMMARY_PROCESS_PREFIX}{exp_id}{FILE_EXTENSION_CSV}')

        # Check and load product file
        if product_file.exists():
            preprocessed[KEY_SUMMARY_PRODUCT][exp_id] = pd.read_csv(product_file)
        else:
            missing_files.append(f'{SUMMARY_PRODUCT_PREFIX}{exp_id}{FILE_EXTENSION_CSV}')

        # Check and load stations file
        if stations_file.exists():
            preprocessed[KEY_SUMMARY_STATIONS][exp_id] = pd.read_csv(stations_file)
        else:
            missing_files.append(f'{SUMMARY_STATIONS_PREFIX}{exp_id}{FILE_EXTENSION_CSV}')

    # Report any missing files
    if missing_files:
        print(f"[WARNING] {len(missing_files)} files not found in {data_path}:")
        for f in missing_files[:MAX_MISSING_FILES_DISPLAY]:  # Show first 5 missing files
            print(f"          - {f}")
        if len(missing_files) > MAX_MISSING_FILES_DISPLAY:
            print(f"          ... and {len(missing_files) - MAX_MISSING_FILES_DISPLAY} more")

    return preprocessed


def load_all_data(exp_ids=None, save_summary=True):
    """
    Master loader function that loads all required data.

    Args:
        exp_ids: List of experiment IDs to load (None = auto-detect all)
        save_summary: If True, save a summary file to output/ folder

    Returns:
        dict: Complete data dictionary with all inputs loaded
    """
    print(f"Loading data...")

    data = {}

    # ====================
    # 1. Load configuration files
    # ====================
    # Load KPI definitions, groups, values, and DoE table
    data[KEY_INDICATORS] = load_indicator_tables()
    data[KEY_VALUES] = load_values_config()
    data[KEY_GROUPS] = load_groups_config()
    data[KEY_DOE] = load_doe_table()
    data['formatting_config'] = load_formatting_config()

    # ====================
    # 2. Load attribute data
    # ====================
    # Load product, process, system attributes from JSON files
    data[KEY_ATTRIBUTES] = load_attributes()

    # ====================
    # 3. Load preprocessed experiment data
    # ====================
    # Load summary CSV files from preprocessing step
    preprocessed = load_preprocessed_data(exp_ids)
    data[KEY_SUMMARY_PROCESS] = preprocessed[KEY_SUMMARY_PROCESS]
    data[KEY_SUMMARY_PRODUCT] = preprocessed[KEY_SUMMARY_PRODUCT]
    data[KEY_SUMMARY_STATIONS] = preprocessed[KEY_SUMMARY_STATIONS]

    exp_count = len(data[KEY_SUMMARY_PROCESS])
    print(f"[OK] Loaded data for {exp_count} experiments")

    # ====================
    # 4. Combine into consolidated dataframes
    # ====================
    # Merge individual experiment dataframes into three large dataframes
    # This allows vectorized operations and simpler calculations downstream
    print(f"Combining data into consolidated dataframes...")

    # Combine all process dataframes (add exp_id column to track source)
    all_process_dfs = []
    for exp_id, df in data[KEY_SUMMARY_PROCESS].items():
        df_copy = df.copy()
        df_copy[EXP_ID_COLUMN] = exp_id
        all_process_dfs.append(df_copy)

    if all_process_dfs:
        data[KEY_DF_PROCESS] = pd.concat(all_process_dfs, ignore_index=True)
    else:
        data[KEY_DF_PROCESS] = pd.DataFrame()
        print("[WARNING] No process data found - df_process is empty")

    # Combine all product dataframes
    all_product_dfs = []
    for exp_id, df in data[KEY_SUMMARY_PRODUCT].items():
        df_copy = df.copy()
        df_copy[EXP_ID_COLUMN] = exp_id
        all_product_dfs.append(df_copy)

    if all_product_dfs:
        data[KEY_DF_PRODUCT] = pd.concat(all_product_dfs, ignore_index=True)
    else:
        data[KEY_DF_PRODUCT] = pd.DataFrame()
        print("[WARNING] No product data found - df_product is empty")

    # Combine all resource (stations) dataframes
    all_resource_dfs = []
    for exp_id, df in data[KEY_SUMMARY_STATIONS].items():
        df_copy = df.copy()
        df_copy[EXP_ID_COLUMN] = exp_id
        all_resource_dfs.append(df_copy)

    if all_resource_dfs:
        data[KEY_DF_RESOURCE] = pd.concat(all_resource_dfs, ignore_index=True)
    else:
        data[KEY_DF_RESOURCE] = pd.DataFrame()
        print("[WARNING] No resource data found - df_resource is empty")

    # ====================
    # 5. Create system-level dataframe
    # ====================
    # Filter DoE table to only include loaded experiments (one row per experiment)
    exp_ids = list(data[KEY_SUMMARY_PROCESS].keys())
    data[KEY_DF_SYSTEM] = data[KEY_DOE][data[KEY_DOE][EXP_ID_COLUMN].isin(exp_ids)].copy().reset_index(drop=True)

    print(f"[OK] Combined dataframes:")
    print(f"  - df_process: {len(data[KEY_DF_PROCESS])} rows")
    print(f"  - df_product: {len(data[KEY_DF_PRODUCT])} rows")
    print(f"  - df_resource: {len(data[KEY_DF_RESOURCE])} rows")
    print(f"  - df_system: {len(data[KEY_DF_SYSTEM])} rows")

    # ====================
    # 6. Save output files (optional)
    # ====================
    # Save combined dataframes with module numbering for traceability
    # Can be disabled by setting save_summary=False
    if save_summary:
        output_dir = Path(__file__).parent.parent / OUTPUT_DIR / DATAFRAMES_SUBDIR
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save the three big dataframes with module numbering
        data[KEY_DF_PROCESS].to_csv(output_dir / DF_PROCESS_OUTPUT, index=False)
        print(f"[OK] Saved: {DF_PROCESS_OUTPUT} ({len(data[KEY_DF_PROCESS])} rows)")

        data[KEY_DF_PRODUCT].to_csv(output_dir / DF_PRODUCT_OUTPUT, index=False)
        print(f"[OK] Saved: {DF_PRODUCT_OUTPUT} ({len(data[KEY_DF_PRODUCT])} rows)")

        data[KEY_DF_RESOURCE].to_csv(output_dir / DF_RESOURCE_OUTPUT, index=False)
        print(f"[OK] Saved: {DF_RESOURCE_OUTPUT} ({len(data[KEY_DF_RESOURCE])} rows)")

        data[KEY_DF_SYSTEM].to_csv(output_dir / DF_SYSTEM_OUTPUT, index=False)
        print(f"[OK] Saved: {DF_SYSTEM_OUTPUT} ({len(data[KEY_DF_SYSTEM])} rows)")

    return data


if __name__ == '__main__':
    # Test the data loader
    data = load_all_data()
    print("Data loaded successfully:")
    for key in data.keys():
        print(f"  - {key}")
