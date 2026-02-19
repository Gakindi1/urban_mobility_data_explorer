"""
Data Cleaning Script for NYC Taxi Trip Data

This script loads raw taxi trip data from a Parquet file and applies comprehensive
cleaning and feature engineering. It produces a cleaned DataFrame and logs all
cleaning operations for transparency and documentation.
"""

import pandas as pd
import os
from datetime import datetime
import json


def load_raw_trips(file_path, nrows=500000):
    """
    Load raw taxi trip data from a Parquet file.
    
    Args:
        file_path: Path to the yellow_tripdata.parquet file
        nrows: Number of rows to load for development (default 500,000)
    
    Returns:
        pandas DataFrame containing raw trip data
    """
    print(f"Loading raw trips from {file_path}...")
    # For CSV files, we load from CSV instead of parquet
    df = pd.read_csv(file_path, nrows=nrows)
    print(f"Loaded {len(df)} rows of trip data")
    return df


def load_zone_lookup(file_path):
    """
    Load the taxi zone lookup table that maps LocationID to zone names and boroughs.
    
    Args:
        file_path: Path to the taxi_zone_lookup.csv file
    
    Returns:
        pandas DataFrame containing zone lookup data
    """
    print(f"Loading zone lookup from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} zones")
    return df


def load_shapefile_data(file_path):
    """
    Load taxi zone geographic data from a shapefile.
    
    Args:
        file_path: Path to the taxi_zones.shp file
    
    Returns:
        pandas DataFrame with columns: location_id, zone_name, borough, shape_length, shape_area
    """
    import shapefile
    
    print(f"Loading shapefile from {file_path}...")
    
    # Open the shapefile
    sf = shapefile.Reader(file_path)
    
    records = []
    for shape_record in sf.shapeRecords():
        record = shape_record.record
        # Map the DBF fields to our column names
        location_data = {
            'location_id': record[4],  # LocationID
            'zone_name': record[3],    # zone
            'borough': record[5],      # borough
            'shape_length': record[1], # Shape_Leng
            'shape_area': record[2]    # Shape_Area
        }
        records.append(location_data)
    
    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} zones from shapefile")
    return df


def clean_trips(raw_trips_df, zone_lookup_df):
    """
    Clean raw trip data by removing invalid records and adding derived features.
    
    Args:
        raw_trips_df: DataFrame containing raw trip data
        zone_lookup_df: DataFrame containing zone lookup information
    
    Returns:
        tuple: (cleaned DataFrame, cleaning_log dictionary)
    """
    
    # Initialize the cleaning log
    cleaning_log = {}
    
    # STEP 1: Record starting row count
    starting_rows = len(raw_trips_df)
    cleaning_log['starting_row_count'] = starting_rows
    print(f"\nStarting with {starting_rows} rows")
    
    # Create a working copy
    df = raw_trips_df.copy()
    
    # STEP 2: Remove rows with null values in critical columns
    critical_columns = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 
                       'PULocationID', 'DOLocationID', 'fare_amount', 
                       'total_amount', 'trip_distance']
    null_rows_before = len(df)
    df = df.dropna(subset=critical_columns)
    null_rows_removed = null_rows_before - len(df)
    cleaning_log['null_values_removed'] = null_rows_removed
    print(f"Step 2 - Null values: Removed {null_rows_removed} rows")
    
    # STEP 3: Remove rows with trip_distance <= 0
    distance_rows_before = len(df)
    df = df[df['trip_distance'] > 0]
    distance_rows_removed = distance_rows_before - len(df)
    cleaning_log['invalid_distance_removed'] = distance_rows_removed
    print(f"Step 3 - Invalid distance: Removed {distance_rows_removed} rows")
    
    # STEP 4: Remove rows with fare_amount < 0
    fare_negative_before = len(df)
    df = df[df['fare_amount'] >= 0]
    fare_negative_removed = fare_negative_before - len(df)
    cleaning_log['negative_fare_removed'] = fare_negative_removed
    print(f"Step 4 - Negative fare: Removed {fare_negative_removed} rows")
    
    # STEP 5: Remove rows with total_amount <= 0
    total_invalid_before = len(df)
    df = df[df['total_amount'] > 0]
    total_invalid_removed = total_invalid_before - len(df)
    cleaning_log['invalid_total_amount_removed'] = total_invalid_removed
    print(f"Step 5 - Invalid total amount: Removed {total_invalid_removed} rows")
    
    # STEP 6: Remove rows with invalid passenger_count
    passenger_before = len(df)
    df = df[(df['passenger_count'] >= 1) & (df['passenger_count'] <= 6)]
    passenger_removed = passenger_before - len(df)
    cleaning_log['invalid_passenger_count_removed'] = passenger_removed
    print(f"Step 6 - Invalid passenger count: Removed {passenger_removed} rows")
    
    # STEP 7: Convert datetime columns and remove conversion errors
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce')
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'], errors='coerce')
    
    datetime_before = len(df)
    df = df.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
    datetime_removed = datetime_before - len(df)
    cleaning_log['datetime_conversion_failed_removed'] = datetime_removed
    print(f"Step 7 - Datetime conversion: Removed {datetime_removed} rows")
    
    # STEP 8: Remove rows where pickup_datetime >= dropoff_datetime
    time_logic_before = len(df)
    df = df[df['tpep_pickup_datetime'] < df['tpep_dropoff_datetime']]
    time_logic_removed = time_logic_before - len(df)
    cleaning_log['invalid_time_logic_removed'] = time_logic_removed
    print(f"Step 8 - Invalid trip time logic: Removed {time_logic_removed} rows")
    
    # STEP 9: Validate location IDs
    valid_location_ids = set(zone_lookup_df['LocationID'].unique())
    location_before = len(df)
    df = df[(df['PULocationID'].isin(valid_location_ids)) & 
            (df['DOLocationID'].isin(valid_location_ids))]
    location_removed = location_before - len(df)
    cleaning_log['invalid_location_ids_removed'] = location_removed
    print(f"Step 9 - Invalid location IDs: Removed {location_removed} rows")
    
    # STEP 10: Remove exact duplicate rows
    duplicates_before = len(df)
    df = df.drop_duplicates()
    duplicates_removed = duplicates_before - len(df)
    cleaning_log['exact_duplicates_removed'] = duplicates_removed
    print(f"Step 10 - Exact duplicates: Removed {duplicates_removed} rows")
    
    # STEP 11: Remove rows with total_amount > 500
    outlier_before = len(df)
    df = df[df['total_amount'] <= 500]
    outlier_removed = outlier_before - len(df)
    cleaning_log['extreme_outlier_fare_removed'] = outlier_removed
    print(f"Step 11 - Extreme outlier fares (>$500): Removed {outlier_removed} rows")
    
    # FEATURE ENGINEERING
    print("\nAdding derived features...")
    
    # Feature 1: trip_duration_minutes
    duration_delta = df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    df['trip_duration_minutes'] = (duration_delta.dt.total_seconds() / 60).round(2)
    
    # Feature 2: speed_mph
    df['speed_mph'] = 0.0  # Initialize
    non_zero_duration = df['trip_duration_minutes'] > 0
    df.loc[non_zero_duration, 'speed_mph'] = (
        (df.loc[non_zero_duration, 'trip_distance'] / 
         (df.loc[non_zero_duration, 'trip_duration_minutes'] / 60)).round(2)
    )
    
    # Feature 3: fare_per_mile
    df['fare_per_mile'] = 0.0  # Initialize
    non_zero_distance = df['trip_distance'] > 0
    df.loc[non_zero_distance, 'fare_per_mile'] = (
        (df.loc[non_zero_distance, 'fare_amount'] / 
         df.loc[non_zero_distance, 'trip_distance']).round(2)
    )
    
    # Feature 4: pickup_hour
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    
    # Feature 5: pickup_day_of_week (0=Monday, 6=Sunday)
    df['pickup_day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek
    
    print("Features added: trip_duration_minutes, speed_mph, fare_per_mile, pickup_hour, pickup_day_of_week")
    
    # Remove impossible speeds (>100 mph)
    speed_before = len(df)
    df = df[df['speed_mph'] <= 100]
    speed_removed = speed_before - len(df)
    cleaning_log['impossible_speed_removed'] = speed_removed
    print(f"Post-feature engineering - Impossible speeds (>100 mph): Removed {speed_removed} rows")
    
    # Convert datetime columns to ISO format strings for SQLite storage
    df['tpep_pickup_datetime'] = df['tpep_pickup_datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    df['tpep_dropoff_datetime'] = df['tpep_dropoff_datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Record final row count
    final_rows = len(df)
    cleaning_log['final_row_count'] = final_rows
    cleaning_log['total_rows_removed'] = starting_rows - final_rows
    cleaning_log['retention_rate'] = round(100 * final_rows / starting_rows, 2)
    
    print(f"\nCleaning complete:")
    print(f"  Starting rows: {starting_rows}")
    print(f"  Final rows: {final_rows}")
    print(f"  Total removed: {cleaning_log['total_rows_removed']}")
    print(f"  Retention rate: {cleaning_log['retention_rate']}%")
    
    return df, cleaning_log


def write_cleaning_log(cleaning_log, log_file_path):
    """
    Write the cleaning log to a human-readable text file.
    
    Args:
        cleaning_log: Dictionary containing cleaning statistics
        log_file_path: Path where to write the log file
    """
    with open(log_file_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("NYC TAXI DATA CLEANING LOG\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Starting row count:           {cleaning_log.get('starting_row_count', 'N/A')}\n")
        f.write(f"Final row count:              {cleaning_log.get('final_row_count', 'N/A')}\n")
        f.write(f"Total rows removed:           {cleaning_log.get('total_rows_removed', 'N/A')}\n")
        f.write(f"Data retention rate:          {cleaning_log.get('retention_rate', 'N/A')}%\n\n")
        
        f.write("CLEANING STEPS DETAILED\n")
        f.write("-" * 70 + "\n")
        f.write(f"1. Null values removed:                    {cleaning_log.get('null_values_removed', 0)}\n")
        f.write(f"2. Invalid trip distance removed:          {cleaning_log.get('invalid_distance_removed', 0)}\n")
        f.write(f"3. Negative fare removed:                  {cleaning_log.get('negative_fare_removed', 0)}\n")
        f.write(f"4. Invalid total amount removed:           {cleaning_log.get('invalid_total_amount_removed', 0)}\n")
        f.write(f"5. Invalid passenger count removed:        {cleaning_log.get('invalid_passenger_count_removed', 0)}\n")
        f.write(f"6. Datetime conversion failures removed:   {cleaning_log.get('datetime_conversion_failed_removed', 0)}\n")
        f.write(f"7. Invalid time logic removed:             {cleaning_log.get('invalid_time_logic_removed', 0)}\n")
        f.write(f"8. Invalid location IDs removed:           {cleaning_log.get('invalid_location_ids_removed', 0)}\n")
        f.write(f"9. Exact duplicates removed:               {cleaning_log.get('exact_duplicates_removed', 0)}\n")
        f.write(f"10. Extreme outlier fares removed:         {cleaning_log.get('extreme_outlier_fare_removed', 0)}\n")
        f.write(f"11. Impossible speeds removed:             {cleaning_log.get('impossible_speed_removed', 0)}\n\n")
        
        f.write("DERIVED FEATURES ADDED\n")
        f.write("-" * 70 + "\n")
        f.write("1. trip_duration_minutes: Duration of trip in minutes\n")
        f.write("2. speed_mph: Average speed in miles per hour\n")
        f.write("3. fare_per_mile: Fare amount divided by trip distance\n")
        f.write("4. pickup_hour: Hour of day (0-23) when trip started\n")
        f.write("5. pickup_day_of_week: Day of week (0=Monday, 6=Sunday)\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("END OF LOG\n")
        f.write("=" * 70 + "\n")


if __name__ == "__main__":
    # Set up file paths (relative to this script's location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, 'data')
    
    # File paths
    trips_file = os.path.join(data_dir, 'yellow_tripdata_2019-01.csv')
    zones_file = os.path.join(data_dir, 'taxi_zones.shp')
    lookup_file = os.path.join(data_dir, 'taxi_zone_lookup.csv')
    log_file = os.path.join(data_dir, 'cleaning_log.txt')
    
    print("\n" + "=" * 70)
    print("NYC TAXI DATA CLEANING PIPELINE")
    print("=" * 70 + "\n")
    
    # Load data
    print("STEP 1: LOADING DATA")
    print("-" * 70)
    raw_trips = load_raw_trips(trips_file)
    zone_lookup = load_zone_lookup(lookup_file)
    shapefile_data = load_shapefile_data(zones_file)
    
    # Clean data
    print("\n\nSTEP 2: CLEANING AND FEATURE ENGINEERING")
    print("-" * 70)
    clean_trips_df, cleaning_log = clean_trips(raw_trips, zone_lookup)
    
    # Write log
    print("\n\nSTEP 3: WRITING CLEANING LOG")
    print("-" * 70)
    write_cleaning_log(cleaning_log, log_file)
    print(f"Cleaning log written to: {log_file}")
    
    # Final summary
    print("\n\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\nFinal dataset: {len(clean_trips_df)} clean trip records")
    print(f"Columns in cleaned dataset: {list(clean_trips_df.columns)}")
    print(f"\nCleaned data is ready for database insertion.")
