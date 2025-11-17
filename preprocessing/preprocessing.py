"""
Preprocessing Module - Transform Simulation Outputs to Analytics-Ready Format

This module processes event logs from disassembly simulation experiments and creates
a denormalized table with component-level data for analytics calculations.

Usage:
    # Process single experiment
    python preprocessing.py --exp exp001

    # Process all experiments
    python preprocessing.py --all

    # Process range of experiments
    python preprocessing.py --range 1 80

Output:
    analytics/data/processed/summary_process_{exp_id}.csv
    analytics/data/processed/summary_product_{exp_id}.csv
    analytics/data/processed/summary_stations_{exp_id}.csv
"""

import pandas as pd
import numpy as np
import os
import glob
import argparse
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# STANDALONE MODE: Use experiment_data/ for fully portable analytics module
EXPERIMENT_DATA_DIR = os.path.join(BASE_DIR, 'experiment_data')
EXPERIMENT_OUTPUT_DIR = os.path.join(EXPERIMENT_DATA_DIR, 'outputs')
DOE_TABLE_PATH = os.path.join(BASE_DIR, 'data', 'config', 'doe_full_factorial_experiments.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'processed')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_simulation_output_dir(exp_id, base_dir=EXPERIMENT_OUTPUT_DIR):
    """Find simulation output directory for an experiment.

    Updated to work with both old (timestamped) and new (no timestamp) folder names:
    - Old format: 20251021_224227_exp001_s01_hd_a00_run001
    - New format: exp001_s01_hd_a00_run001
    """
    pattern = os.path.join(base_dir, f'*{exp_id}_*_run001')
    matches = glob.glob(pattern)

    if not matches:
        return None

    # Return most recent if multiple matches
    return max(matches, key=os.path.getctime)


def extract_step_from_component(component_name):
    """
    Extract step name from component name while preserving original.

    Examples:
        'comp_001_BOSP_1' -> 'BOSP'
        'comp_001_BOSP_1/2' -> 'BOSP'
        'comp_001_BAT' -> 'BAT'
        'group_001_FRONT_AXIS_GROUP' -> 'FRONT_AXIS_GROUP'
        'comp_001_FAX' -> 'FRONT_AXIS_GROUP'
        'comp_001_RAX_HD' -> 'REAR_AXIS_GROUP'
    """
    if pd.isna(component_name) or component_name == 'none':
        return None

    parts = component_name.split('_')

    # Handle group components (e.g., group_001_FRONT_AXIS_GROUP)
    if parts[0] == 'group':
        return '_'.join(parts[2:])

    # Handle regular components (e.g., comp_001_BOSP_1 or comp_001_BOSP_1/2)
    if parts[0] == 'comp':
        if len(parts) < 3:
            return None

        # Extract everything after comp_XXX_
        step_parts = parts[2:]

        # Remove numeric suffix (last part if it's a number or contains '/')
        if len(step_parts) > 0:
            last_part = step_parts[-1]
            # Remove if it's just a digit or contains '/' (like '1/2')
            if last_part.isdigit() or '/' in last_part:
                step_parts = step_parts[:-1]

        step_name = '_'.join(step_parts)

        # Return the exact component name without transformation
        # This preserves variant information like RAX_HD, RAX_RD, etc.
        return step_name

    return None




# ============================================================================
# MAIN PREPROCESSING LOGIC
# ============================================================================

def calculate_product_throughput(eventlog_file, case_table_file, output_table_file):
    """
    Calculate product-level lead time with completion rate tracking.

    Lead time is calculated only for the components that were actually disassembled.
    Completion rate = (disassembled_components) / (target_components - missing_components)

    Args:
        eventlog_file: Path to raw event log CSV
        case_table_file: Path to raw case table CSV
        output_table_file: Path to raw output table CSV

    Returns:
        pd.DataFrame with columns:
        - caseID
        - product_id
        - product_type
        - created_time (first event timestamp)
        - system_exit_time (last component disassembly timestamp)
        - lead_time (minutes, integer)
        - target_components (count)
        - missing_components (count)
        - disassembled_components (count)
        - completion_rate (%)
        - has_remains (boolean, if product was sent as remains)
        - remains_content (list of components in remains, if applicable)
    """
    import ast

    # ====================
    # 1. Parse case table for target/missing components
    # ====================
    # Read case table to get target and missing components
    case_df = pd.read_csv(case_table_file)

    # Parse JSON strings in target_components and missing_components
    def count_components(json_str):
        """Count total components from JSON string"""
        if pd.isna(json_str) or json_str == '[]':
            return 0
        try:
            # Use ast.literal_eval for safer parsing of Python literal structures
            data = ast.literal_eval(json_str) if isinstance(json_str, str) else json_str
            if isinstance(data, dict):
                return sum(data.values())
            elif isinstance(data, list):
                return len(data)
            return 0
        except:
            return 0

    case_df['target_count'] = case_df['target_components'].apply(count_components)
    case_df['missing_count'] = case_df['missing_components'].apply(count_components)

    # ====================
    # 2. Identify products sent as remains
    # ====================
    # Read output table to identify products sent as remains
    output_df = pd.read_csv(output_table_file)

    # Identify remains: object_type == "product"
    remains_df = output_df[output_df['object_type'] == 'product'].copy()
    remains_df['remains_content'] = remains_df['content']
    remains_df = remains_df[['caseID', 'remains_content', 'output_time']]
    remains_df['has_remains'] = True

    # ====================
    # 3. Count disassembled components
    # ====================
    # Read event log and count disassembled components (object_type == "component" in output table)
    # Count components that were actually disassembled by checking output table
    disassembled_df = output_df[output_df['object_type'] == 'component'].groupby('caseID').agg({
        'objectID': 'count',  # Count of disassembled components
        'output_time': 'max'   # Last component exit time
    }).reset_index()
    disassembled_df.columns = ['caseID', 'disassembled_count', 'system_exit_time']
    disassembled_df['system_exit_time'] = pd.to_datetime(disassembled_df['system_exit_time'])

    # ====================
    # 4. Extract timing information
    # ====================
    # Read event log for created time and shopfloor entry time
    eventlog_df = pd.read_csv(eventlog_file)
    eventlog_df['timestamp'] = pd.to_datetime(eventlog_df['timestamp'])

    # Get first event timestamp per caseID (product arrival / created_time)
    created_time_df = eventlog_df.groupby('caseID').agg({
        'object_id': 'first',  # product_id
        'timestamp': 'min'
    }).reset_index()
    created_time_df.columns = ['caseID', 'product_id', 'created_time']

    # Get shopfloor entry time: when product exits incoming_storage buffer
    # Event pattern: object_type='product', activity='buffer', activity_state='exit', resource_id='incoming_storage'
    shopfloor_entry_df = eventlog_df[
        (eventlog_df['object_type'] == 'product') &
        (eventlog_df['activity'] == 'buffer') &
        (eventlog_df['activity_state'] == 'exit') &
        (eventlog_df['resource_id'] == 'incoming_storage')
    ][['caseID', 'timestamp']].copy()
    shopfloor_entry_df.columns = ['caseID', 'shopfloor_entry_time']

    # Extract product type from product_id
    created_time_df['product_type'] = created_time_df['product_id'].str.split('_').str[-1]

    # ====================
    # 5. Merge all data and calculate metrics
    # ====================
    # Merge all data
    product_summary = case_df[['caseID', 'product_type', 'target_count', 'missing_count']].copy()
    product_summary = product_summary.merge(created_time_df[['caseID', 'product_id', 'created_time']], on='caseID', how='left')
    product_summary = product_summary.merge(shopfloor_entry_df, on='caseID', how='left')
    product_summary = product_summary.merge(disassembled_df, on='caseID', how='left')
    product_summary = product_summary.merge(remains_df, on='caseID', how='left')

    # Fill NaN values
    product_summary['disassembled_count'] = product_summary['disassembled_count'].fillna(0).astype(int)
    product_summary['has_remains'] = product_summary['has_remains'].fillna(False)
    product_summary['remains_content'] = product_summary['remains_content'].fillna('')

    # If product has remains, use remains output_time as system_exit_time
    remains_exit_time = remains_df[['caseID', 'output_time']].copy()
    remains_exit_time['output_time'] = pd.to_datetime(remains_exit_time['output_time'])

    # Merge remains exit time
    product_summary = product_summary.merge(
        remains_exit_time.rename(columns={'output_time': 'remains_exit_time'}),
        on='caseID',
        how='left'
    )

    # Use remains_exit_time if has_remains, otherwise use system_exit_time from components
    product_summary['final_exit_time'] = product_summary.apply(
        lambda row: row['remains_exit_time'] if row['has_remains'] and pd.notna(row['remains_exit_time'])
                   else row['system_exit_time'],
        axis=1
    )

    # Calculate lead time in minutes (rounded to integer)
    product_summary['lead_time'] = (
        (product_summary['final_exit_time'] - product_summary['created_time']).dt.total_seconds() / 60
    ).round(0).astype('Int64')  # Use Int64 to allow NaN values

    # Calculate shopfloor_time: time between shopfloor_entry and system_exit_time (integer minutes)
    product_summary['shopfloor_time'] = (
        (product_summary['final_exit_time'] - product_summary['shopfloor_entry_time']).dt.total_seconds() / 60
    ).round(0).astype('Int64')  # Use Int64 to allow NaN values

    # Calculate completion rate (handle division by zero)
    product_summary['expected_components'] = product_summary['target_count'] - product_summary['missing_count']
    product_summary['completion_rate'] = product_summary.apply(
        lambda row: (row['disassembled_count'] / row['expected_components'] * 100)
                    if row['expected_components'] > 0 else 0.0,
        axis=1
    ).round(1)

    # Drop old system_exit_time from disassembled_df merge before renaming final_exit_time
    if 'system_exit_time' in product_summary.columns:
        product_summary = product_summary.drop(columns=['system_exit_time'])

    # Rename columns for output
    product_summary = product_summary.rename(columns={
        'target_count': 'target_components',
        'missing_count': 'missing_components',
        'disassembled_count': 'disassembled_components',
        'final_exit_time': 'system_exit_time'
    })

    # Drop intermediate columns
    columns_to_drop = [col for col in ['remains_exit_time', 'expected_components'] if col in product_summary.columns]
    if columns_to_drop:
        product_summary = product_summary.drop(columns=columns_to_drop)

    # Select and order final columns
    product_summary = product_summary[[
        'caseID', 'product_id', 'product_type', 'created_time', 'shopfloor_entry_time', 'system_exit_time',
        'lead_time', 'shopfloor_time',
        'target_components', 'missing_components', 'disassembled_components', 'completion_rate',
        'has_remains', 'remains_content'
    ]]

    return product_summary


def calculate_station_utilization(process_df, exp_row):
    """
    Calculate machine utilization rates for each station.

    Utilization is calculated based on three states:
    - Running: Active processing time (sum of process_duration from summary_process)
    - Waiting: Factory open but machine idle (factory_open_time - runtime)
    - Closed: Factory closed (total_simulation_time - factory_open_time)

    Args:
        process_df: DataFrame with component-level process data (from summary_process)
        exp_row: Single row from DoE table with opening_hour, closing_hour, num_weeks

    Returns:
        pd.DataFrame with columns:
        - station_id
        - runtime_minutes (sum of process_duration, integer)
        - waiting_time_minutes (factory_open_time - runtime, integer)
        - closed_time_minutes (total_simulation_time - factory_open_time, integer)
        - total_simulation_time_minutes (integer)
        - factory_open_time_minutes (integer)
        - utilization_rate_running (%)
        - utilization_rate_waiting (%)
        - utilization_rate_closed (%)
    """
    # ====================
    # 1. Extract factory schedule parameters
    # ====================
    # Get DoE parameters
    opening_hour = int(exp_row['opening_hour'])
    closing_hour = int(exp_row['closing_hour'])
    num_weeks = int(exp_row['num_weeks'])

    # ====================
    # 2. Calculate time boundaries
    # ====================
    # Calculate total simulation time: num_weeks * 7 days * 24 hours * 60 minutes
    total_simulation_time_minutes = num_weeks * 7 * 24 * 60

    # Calculate factory open time: (closing_hour - opening_hour) * 60 * 7 days * num_weeks
    factory_open_time_minutes = (closing_hour - opening_hour) * 60 * 7 * num_weeks

    # ====================
    # 3. Aggregate runtime per station
    # ====================
    # Calculate runtime per station (sum of process_duration from summary_process)
    station_runtime = process_df.groupby('station_id').agg({
        'process_duration': 'sum'
    }).reset_index()
    station_runtime.columns = ['station_id', 'runtime_minutes']

    # Round runtime to full minutes (integer)
    station_runtime['runtime_minutes'] = station_runtime['runtime_minutes'].round(0).astype(int)

    # ====================
    # 4. Calculate waiting and closed times
    # ====================
    # Calculate waiting and closed times (integers)
    station_runtime['factory_open_time_minutes'] = factory_open_time_minutes
    station_runtime['total_simulation_time_minutes'] = total_simulation_time_minutes

    # Waiting time = factory open time - runtime (can't be negative)
    station_runtime['waiting_time_minutes'] = (
        station_runtime['factory_open_time_minutes'] - station_runtime['runtime_minutes']
    ).clip(lower=0).astype(int)

    # Closed time = total simulation time - factory open time
    station_runtime['closed_time_minutes'] = (
        station_runtime['total_simulation_time_minutes'] - station_runtime['factory_open_time_minutes']
    ).astype(int)

    # ====================
    # 5. Calculate utilization percentages
    # ====================
    # Calculate utilization rates (as percentage of total simulation time)
    station_runtime['utilization_rate_running'] = (
        station_runtime['runtime_minutes'] / station_runtime['total_simulation_time_minutes'] * 100
    ).round(2)

    station_runtime['utilization_rate_waiting'] = (
        station_runtime['waiting_time_minutes'] / station_runtime['total_simulation_time_minutes'] * 100
    ).round(2)

    station_runtime['utilization_rate_closed'] = (
        station_runtime['closed_time_minutes'] / station_runtime['total_simulation_time_minutes'] * 100
    ).round(2)

    # Reorder columns
    station_runtime = station_runtime[[
        'station_id',
        'runtime_minutes',
        'waiting_time_minutes',
        'closed_time_minutes',
        'total_simulation_time_minutes',
        'factory_open_time_minutes',
        'utilization_rate_running',
        'utilization_rate_waiting',
        'utilization_rate_closed'
    ]]

    return station_runtime


def calculate_closed_time(start_time, end_time, opening_hour=7, closing_hour=17):
    """
    Calculate the total closed time (factory not operating) between start and end times.

    Factory is closed daily from closing_hour to opening_hour next day.
    Factory operates 7 days a week.

    Args:
        start_time: pandas Timestamp for process start
        end_time: pandas Timestamp for process end
        opening_hour: Factory opens at this hour (default 7)
        closing_hour: Factory closes at this hour (default 17)

    Returns:
        float: Total closed time in minutes
    """
    from datetime import timedelta

    # If process completes same day, no closed time
    if start_time.date() == end_time.date():
        # Check if process spans closing time within the same day
        start_hour = start_time.hour + start_time.minute / 60
        end_hour = end_time.hour + end_time.minute / 60

        # If both start and end are within operating hours, no closed time
        if opening_hour <= start_hour < closing_hour and opening_hour <= end_hour <= closing_hour:
            return 0.0

        # If starts before closing and ends after closing (but same date)
        # This shouldn't happen in normal operation but handle it
        if start_hour < closing_hour and end_hour > closing_hour:
            closed_minutes = (end_hour - closing_hour) * 60
            return max(0, closed_minutes)

        return 0.0

    # Calculate total closed time for multi-day processes
    total_closed_minutes = 0.0
    current_time = start_time

    # Hours per day that factory is closed
    closed_hours_per_day = 24 - (closing_hour - opening_hour)

    while current_time.date() < end_time.date():
        # Get closing time for current day
        closing_time = current_time.replace(hour=closing_hour, minute=0, second=0, microsecond=0)

        # Get opening time for next day
        next_day = current_time.date() + timedelta(days=1)
        opening_time = pd.Timestamp(year=next_day.year, month=next_day.month, day=next_day.day,
                                    hour=opening_hour, minute=0, second=0)

        # If current_time is before closing time, count from closing time
        # If current_time is after closing time, it's already in closed period
        if current_time < closing_time:
            # Add closed time from closing_time to opening_time next day
            night_closed_minutes = (opening_time - closing_time).total_seconds() / 60
            total_closed_minutes += night_closed_minutes
        else:
            # Current time is after closing, count from current time to next opening
            if current_time < opening_time:
                partial_closed_minutes = (opening_time - current_time).total_seconds() / 60
                total_closed_minutes += partial_closed_minutes

        # Move to next day
        current_time = opening_time

    # Handle the final day if end_time is before opening hour
    if end_time.hour < opening_hour:
        # Process ended before factory opened, add time from last closing to end_time
        previous_day = end_time.date() - timedelta(days=1)
        previous_closing = pd.Timestamp(year=previous_day.year, month=previous_day.month, day=previous_day.day,
                                        hour=closing_hour, minute=0, second=0)

        if end_time > previous_closing:
            final_closed_minutes = (end_time - previous_closing).total_seconds() / 60
            total_closed_minutes += final_closed_minutes
    elif end_time.hour >= closing_hour:
        # Process ended after closing hour on final day
        final_closing = end_time.replace(hour=closing_hour, minute=0, second=0, microsecond=0)
        if end_time > final_closing:
            final_closed_minutes = (end_time - final_closing).total_seconds() / 60
            total_closed_minutes += final_closed_minutes

    return total_closed_minutes


def parse_event_log(eventlog_file, casetable_file, opening_hour=7, closing_hour=17):
    """
    Parse event log to extract disassembly events with corrected process duration.

    Process duration excludes factory closed time (daily from closing_hour to opening_hour).

    Args:
        eventlog_file: Path to event log CSV
        casetable_file: Path to case table CSV (for case-level product_type)
        opening_hour: Factory opens at this hour (default 7)
        closing_hour: Factory closes at this hour (default 17)

    Returns:
        pd.DataFrame with columns:
        - caseID
        - product_id
        - product_type
        - station_id
        - component_name
        - start_time
        - end_time
        - process_duration (minutes, excluding closed time)
    """
    # Read event log
    df = pd.read_csv(eventlog_file)

    # ====================
    # 1. Filter to disassembly activities
    # ====================
    # Filter to disassembly events
    disassembly_events = df[df['activity'] == 'disassembly'].copy()

    # ====================
    # 2. Separate and extract component names
    # ====================
    # Separate start and complete events
    start_events = disassembly_events[disassembly_events['activity_state'] == 'start'].copy()
    complete_events = disassembly_events[disassembly_events['activity_state'] == 'complete'].copy()

    # Extract component name from related_objects (format: "comp_001_BOSP_1:target")
    # Safely handle cases where ':' delimiter might be missing
    start_events['component_name'] = start_events['related_objects'].apply(
        lambda x: x.split(':')[0] if pd.notna(x) and ':' in x else x
    )
    complete_events['component_name'] = complete_events['related_objects'].apply(
        lambda x: x.split(':')[0] if pd.notna(x) and ':' in x else x
    )

    # ====================
    # 3. Match start and complete events
    # ====================
    # Merge start and complete events
    merged = pd.merge(
        start_events[['caseID', 'object_id', 'resource_id', 'component_name', 'timestamp']],
        complete_events[['caseID', 'component_name', 'timestamp']],
        on=['caseID', 'component_name'],
        suffixes=('_start', '_end'),
        how='inner'
    )

    # ====================
    # 4. Add product type from case table
    # ====================
    # Load case-level product_type from casetable
    case_df = pd.read_csv(casetable_file)
    case_product_type = case_df[['caseID', 'product_type']]

    # Merge case-level product_type into component data
    merged = merged.merge(case_product_type, on='caseID', how='left')

    # Rename columns
    merged = merged.rename(columns={
        'object_id': 'product_id',
        'resource_id': 'station_id',
        'timestamp_start': 'start_time',
        'timestamp_end': 'end_time'
    })

    # ====================
    # 5. Calculate process duration excluding closed time
    # ====================
    # Convert timestamps to datetime
    merged['start_time'] = pd.to_datetime(merged['start_time'])
    merged['end_time'] = pd.to_datetime(merged['end_time'])

    # Calculate raw duration (including closed time)
    merged['raw_duration'] = (merged['end_time'] - merged['start_time']).dt.total_seconds() / 60

    # Calculate closed time for each process
    merged['closed_time'] = merged.apply(
        lambda row: calculate_closed_time(row['start_time'], row['end_time'], opening_hour, closing_hour),
        axis=1
    )

    # Calculate actual process duration (excluding closed time)
    merged['process_duration'] = (merged['raw_duration'] - merged['closed_time']).round(1)

    # Drop intermediate columns
    merged = merged.drop(columns=['raw_duration', 'closed_time'])

    return merged[['caseID', 'product_id', 'product_type', 'station_id', 'component_name',
                   'start_time', 'end_time', 'process_duration']]


def create_analytics_input(exp_id, simulation_output_dir, doe_table):
    """
    Main function: Transform simulation outputs to analytics-ready format.

    Args:
        exp_id: e.g., 'exp001'
        simulation_output_dir: Path to simulation output folder
        doe_table: DataFrame with DoE configuration

    Returns:
        tuple: (component_df, product_summary_df, station_summary_df)
            - component_df: Component-level analytics data (summary_process)
            - product_summary_df: Product-level throughput data (summary_product)
            - station_summary_df: Station-level utilization data (summary_stations)
    """
    print(f"\n{'='*60}")
    print(f"Processing {exp_id}")
    print(f"{'='*60}")

    # ====================
    # 1. Locate required files
    # ====================
    # Find required files
    # Updated patterns to work with or without timestamp prefix
    eventlog_pattern = os.path.join(simulation_output_dir, f'*raw_eventlog_{exp_id}_*.csv')
    eventlog_files = glob.glob(eventlog_pattern)

    casetable_pattern = os.path.join(simulation_output_dir, f'*raw_casetable_{exp_id}_*.csv')
    casetable_files = glob.glob(casetable_pattern)

    outputtable_pattern = os.path.join(simulation_output_dir, f'*raw_outputtable_{exp_id}_*.csv')
    outputtable_files = glob.glob(outputtable_pattern)

    if not eventlog_files:
        raise FileNotFoundError(f"Event log not found for {exp_id} in {simulation_output_dir}")
    if not casetable_files:
        raise FileNotFoundError(f"Case table not found for {exp_id} in {simulation_output_dir}")
    if not outputtable_files:
        raise FileNotFoundError(f"Output table not found for {exp_id} in {simulation_output_dir}")

    eventlog_file = eventlog_files[0]
    casetable_file = casetable_files[0]
    outputtable_file = outputtable_files[0]

    print(f"Reading event log: {os.path.basename(eventlog_file)}")
    print(f"Reading case table: {os.path.basename(casetable_file)}")
    print(f"Reading output table: {os.path.basename(outputtable_file)}")

    # Get experiment row from DoE table (needed for factory hours)
    exp_row = doe_table[doe_table['exp_id'] == exp_id].iloc[0]

    # ====================
    # 2. Calculate product-level metrics
    # ====================
    # Calculate product-level lead time
    product_summary = calculate_product_throughput(eventlog_file, casetable_file, outputtable_file)
    print(f"  Calculated lead time for {len(product_summary)} products")

    # ====================
    # 3. Parse component-level events
    # ====================
    # Parse event log for component-level data with factory hours
    opening_hour = int(exp_row['opening_hour'])
    closing_hour = int(exp_row['closing_hour'])
    df = parse_event_log(eventlog_file, casetable_file, opening_hour=opening_hour, closing_hour=closing_hour)
    print(f"  Extracted {len(df)} component disassembly events")

    # ====================
    # 4. Extract step names and add metadata
    # ====================
    # Extract step names from component names
    df['step_name'] = df['component_name'].apply(extract_step_from_component)

    # Add experiment metadata
    df['exp_id'] = exp_id
    df['system'] = exp_row['system']
    df['product_mix'] = exp_row['product_mix']
    df['automation_level'] = exp_row['automation_level']

    # Add quality column (default to 1.0 if not available from simulation)
    # TODO: Extract from quality output if available in future
    df['quality'] = 1.0

    # Reorder columns (keep component_name original, step_name is parsed)
    output_columns = [
        'exp_id', 'system', 'product_mix', 'automation_level',
        'caseID', 'product_id', 'product_type',
        'station_id', 'component_name', 'step_name', 'quality',
        'start_time', 'end_time', 'process_duration'
    ]

    component_df = df[output_columns]

    # ====================
    # 5. Calculate station utilization
    # ====================
    # Add experiment metadata to product summary
    product_summary['exp_id'] = exp_id
    product_summary['system'] = exp_row['system']
    product_summary['product_mix'] = exp_row['product_mix']
    product_summary['automation_level'] = exp_row['automation_level']

    # Reorder product summary columns
    product_summary = product_summary[[
        'exp_id', 'system', 'product_mix', 'automation_level',
        'caseID', 'product_id', 'product_type',
        'created_time', 'shopfloor_entry_time', 'system_exit_time', 'lead_time', 'shopfloor_time',
        'target_components', 'missing_components', 'disassembled_components', 'completion_rate',
        'has_remains', 'remains_content'
    ]]

    # Calculate station utilization
    station_summary = calculate_station_utilization(component_df, exp_row)
    print(f"  Calculated utilization for {len(station_summary)} stations")

    # Add experiment metadata to station summary
    station_summary['exp_id'] = exp_id
    station_summary['system'] = exp_row['system']
    station_summary['product_mix'] = exp_row['product_mix']
    station_summary['automation_level'] = exp_row['automation_level']

    # Reorder station summary columns
    station_summary = station_summary[[
        'exp_id', 'system', 'product_mix', 'automation_level',
        'station_id',
        'runtime_minutes',
        'waiting_time_minutes',
        'closed_time_minutes',
        'total_simulation_time_minutes',
        'factory_open_time_minutes',
        'utilization_rate_running',
        'utilization_rate_waiting',
        'utilization_rate_closed'
    ]]

    # ====================
    # 6. Format and return dataframes
    # ====================
    # Summary statistics
    print(f"\nSummary:")
    print(f"  Products processed: {component_df['caseID'].nunique()}")
    print(f"  Total components: {len(component_df)}")
    print(f"  Unique step names: {component_df['step_name'].nunique()}")
    print(f"  Avg lead time: {product_summary['lead_time'].mean():.0f} minutes")
    print(f"  Avg completion rate: {product_summary['completion_rate'].mean():.1f}%")
    print(f"  Avg utilization (running): {station_summary['utilization_rate_running'].mean():.1f}%")

    return component_df, product_summary, station_summary


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_single_experiment(exp_id, doe_table):
    """Process a single experiment."""
    # Find simulation output directory
    sim_output_dir = find_simulation_output_dir(exp_id)

    if not sim_output_dir:
        print(f"\nWarning: No simulation output found for {exp_id}")
        return False

    try:
        # Create analytics input
        component_df, product_summary, station_summary = create_analytics_input(exp_id, sim_output_dir, doe_table)

        # Save process-level summary (component disassembly data)
        process_file = os.path.join(OUTPUT_DIR, f'summary_process_{exp_id}.csv')
        component_df.to_csv(process_file, index=False)
        print(f"\nSaved: {process_file}")

        # Save product-level summary
        product_file = os.path.join(OUTPUT_DIR, f'summary_product_{exp_id}.csv')
        product_summary.to_csv(product_file, index=False)
        print(f"Saved: {product_file}")

        # Save station-level summary
        station_file = os.path.join(OUTPUT_DIR, f'summary_stations_{exp_id}.csv')
        station_summary.to_csv(station_file, index=False)
        print(f"Saved: {station_file}")

        print(f"Status: SUCCESS")

        return True

    except Exception as e:
        print(f"\nError processing {exp_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_all_experiments(start=None, end=None):
    """Process all experiments. Auto-detects experiments from outputs folder."""
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load DoE table
    print(f"Loading DoE table from: {DOE_TABLE_PATH}")
    doe_table = pd.read_csv(DOE_TABLE_PATH)
    print(f"  Loaded {len(doe_table)} experiments")

    # Auto-discover experiments from outputs folder
    if start is None and end is None:
        # Scan outputs folder for experiment directories
        exp_folders = glob.glob(os.path.join(EXPERIMENT_OUTPUT_DIR, 'exp*_run001'))
        exp_ids = sorted(set([os.path.basename(f).split('_')[0] for f in exp_folders]))
        print(f"  Found {len(exp_ids)} experiment folders in outputs directory\n")

        # Process each experiment
        results = []
        for exp_id in exp_ids:
            success = process_single_experiment(exp_id, doe_table)
            results.append({'exp_id': exp_id, 'status': 'SUCCESS' if success else 'FAILED'})
    else:
        # Process experiments by range (for backwards compatibility)
        if start is None:
            start = 1
        if end is None:
            # Get max from DOE table
            end = len(doe_table)

        results = []
        for exp_num in range(start, end + 1):
            exp_id = f"exp{exp_num:03d}"
            success = process_single_experiment(exp_id, doe_table)
            results.append({'exp_id': exp_id, 'status': 'SUCCESS' if success else 'FAILED'})

    # Summary
    print(f"\n{'='*60}")
    print("PREPROCESSING SUMMARY")
    print(f"{'='*60}")

    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    print(f"Successfully processed: {success_count}/{len(results)}")

    # Save summary
    summary_df = pd.DataFrame(results)
    summary_file = os.path.join(OUTPUT_DIR, 'preprocessing_summary.csv')
    summary_df.to_csv(summary_file, index=False)
    print(f"\nSummary saved to: {summary_file}")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Preprocess simulation outputs for analytics')
    parser.add_argument('--exp', type=str, help='Process single experiment (e.g., exp001)')
    parser.add_argument('--all', action='store_true', help='Process all experiments (auto-discovers from outputs folder)')
    parser.add_argument('--range', type=int, nargs=2, metavar=('START', 'END'),
                        help='Process range of experiments (e.g., --range 1 10)')

    args = parser.parse_args()

    # Load DoE table
    doe_table = pd.read_csv(DOE_TABLE_PATH)

    if args.exp:
        # Process single experiment
        process_single_experiment(args.exp, doe_table)

    elif args.all:
        # Process all experiments (auto-discover from outputs folder)
        process_all_experiments()

    elif args.range:
        # Process range
        start, end = args.range
        process_all_experiments(start, end)

    else:
        # Default: process all (auto-discover from outputs folder)
        print("No arguments provided. Auto-discovering experiments from outputs folder...")
        process_all_experiments()


if __name__ == '__main__':
    main()
