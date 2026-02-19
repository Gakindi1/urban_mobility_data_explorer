"""
Data Loading Script for NYC Taxi Database

This script loads cleaned data from the data cleaning pipeline and inserts it
into the SQLite database. It populates all four tables in the correct order:
1. Boroughs (from shapefile)
2. Zones (from shapefile)
3. Payment types (hardcoded reference data)
4. Trips (from cleaned trip data)

The script uses batch inserts for efficiency and prints progress at each stage.
"""

import sqlite3
import pandas as pd
import os
import sys

# Add backend directory to path so we can import clean_data
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clean_data import load_raw_trips, load_zone_lookup, load_shapefile_data, clean_trips


def insert_boroughs(conn, zones_df):
    """
    Insert borough data into the boroughs table.
    
    Extracts unique borough names from the zones DataFrame and inserts them
    into the boroughs table, then returns a mapping of borough names to IDs
    for use when inserting zones.
    
    Args:
        conn: SQLite database connection
        zones_df: DataFrame containing zone data with borough column
    
    Returns:
        Dictionary mapping borough_name to borough_id
    """
    print("\n[INSERT] Loading boroughs...")
    cursor = conn.cursor()
    
    # Get unique borough names
    boroughs = zones_df['borough'].unique()
    print(f"  Found {len(boroughs)} unique boroughs: {', '.join(boroughs)}")
    
    # Insert each borough
    for borough in boroughs:
        try:
            cursor.execute("INSERT INTO boroughs (borough_name) VALUES (?)", (borough,))
        except sqlite3.IntegrityError:
            # Borough may already exist
            pass
    
    conn.commit()
    
    # Get the mapping of borough names to IDs
    cursor.execute("SELECT borough_id, borough_name FROM boroughs")
    borough_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    print(f"  Inserted {len(borough_map)} boroughs")
    return borough_map


def insert_payment_types(conn):
    """
    Insert payment type reference data into the payment_types table.
    
    Inserts the standard NYC taxi payment types: credit card, cash, no charge,
    dispute, and unknown.
    
    Args:
        conn: SQLite database connection
    
    Returns:
        None
    """
    print("\n[INSERT] Loading payment types...")
    cursor = conn.cursor()
    
    payment_types = [
        (1, 'Credit card'),
        (2, 'Cash'),
        (3, 'No charge'),
        (4, 'Dispute'),
        (5, 'Unknown')
    ]
    
    for payment_id, description in payment_types:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO payment_types (payment_type_id, payment_description) VALUES (?, ?)",
                (payment_id, description)
            )
        except sqlite3.Error as e:
            print(f"  Warning: Could not insert payment type {payment_id}: {e}")
    
    conn.commit()
    print(f"  Inserted {len(payment_types)} payment types")


def insert_zones(conn, zones_df, borough_map):
    """
    Insert zone data into the zones table.
    
    Takes the shapefile-derived zone data and inserts it with proper foreign
    key references to the boroughs table.
    
    Args:
        conn: SQLite database connection
        zones_df: DataFrame containing zone data from shapefile
        borough_map: Dictionary mapping borough_name to borough_id
    
    Returns:
        None
    """
    print("\n[INSERT] Loading zones...")
    cursor = conn.cursor()
    
    insert_count = 0
    skip_count = 0
    
    for idx, row in zones_df.iterrows():
        try:
            borough_id = borough_map.get(row['borough'])
            if borough_id is None:
                skip_count += 1
                continue
            
            cursor.execute(
                """INSERT OR IGNORE INTO zones 
                   (location_id, zone_name, borough_id, shape_length, shape_area)
                   VALUES (?, ?, ?, ?, ?)""",
                (row['location_id'], row['zone_name'], borough_id, row['shape_length'], row['shape_area'])
            )
            insert_count += 1
        except sqlite3.Error as e:
            skip_count += 1
            if skip_count < 5:  # Only print first few errors
                print(f"  Warning: Could not insert zone {row['location_id']}: {e}")
    
    conn.commit()
    print(f"  Inserted {insert_count} zones ({skip_count} skipped)")


def insert_trips(conn, trips_df):
    """
    Insert trip data into the trips table in batches.
    
    Inserts cleaned trip records in batches of 10,000 for memory efficiency.
    Prints progress after each batch. Uses direct values conversion to avoid
    memory issues with large DataFrames.
    
    Args:
        conn: SQLite database connection
        trips_df: DataFrame containing cleaned trip data
    
    Returns:
        Total number of trips inserted
    """
    print("\n[INSERT] Loading trips...")
    print(f"  Total trips to insert: {len(trips_df):,}")
    
    cursor = conn.cursor()
    
    # Fill NA values with None for database insertion
    trips_df['payment_type'] = trips_df['payment_type'].fillna(5)  # Default to 'Unknown'
    trips_df['tip_amount'] = trips_df['tip_amount'].fillna(0)
    
    # Select columns in order and convert to tuples
    cols_to_insert = [
        'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'passenger_count',
        'trip_distance', 'PULocationID', 'DOLocationID', 'payment_type',
        'fare_amount', 'tip_amount', 'total_amount', 'trip_duration_minutes',
        'speed_mph', 'fare_per_mile', 'pickup_hour', 'pickup_day_of_week'
    ]
    
    # Convert DataFrame to list of tuples (more efficient than iterrows)
    data_to_insert = [tuple(row) for row in trips_df[cols_to_insert].values]
    
    # Insert in batches
    batch_size = 10000
    total_inserted = 0
    
    for batch_start in range(0, len(data_to_insert), batch_size):
        batch_end = min(batch_start + batch_size, len(data_to_insert))
        batch = data_to_insert[batch_start:batch_end]
        
        try:
            cursor.executemany(
                """INSERT INTO trips
                   (pickup_datetime, dropoff_datetime, passenger_count, trip_distance,
                    pickup_location_id, dropoff_location_id, payment_type_id,
                    fare_amount, tip_amount, total_amount, trip_duration_minutes,
                    speed_mph, fare_per_mile, pickup_hour, pickup_day_of_week)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                batch
            )
            conn.commit()
            total_inserted += len(batch)
            progress_pct = (batch_end / len(data_to_insert)) * 100
            print(f"  Progress: {total_inserted:,} / {len(data_to_insert):,} ({progress_pct:.1f}%)")
        except sqlite3.Error as e:
            print(f"  Error inserting batch {batch_start}-{batch_end}: {e}")
            continue
    
    print(f"  Total trips inserted: {total_inserted:,}")
    return total_inserted


if __name__ == "__main__":
    print("\n" + "="*70)
    print("NYC TAXI DATA LOADING PIPELINE")
    print("="*70)
    
    # Set up file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, 'data')
    
    trips_file = os.path.join(data_dir, 'yellow_tripdata_2019-01.csv')
    zones_file = os.path.join(data_dir, 'taxi_zones.shp')
    lookup_file = os.path.join(data_dir, 'taxi_zone_lookup.csv')
    db_path = os.path.join(script_dir, 'taxi_data.db')
    
    try:
        # STEP 1: Load and clean data
        print("\nSTEP 1: LOADING AND CLEANING DATA")
        print("-" * 70)
        
        raw_trips = load_raw_trips(trips_file, nrows=500000)
        zone_lookup = load_zone_lookup(lookup_file)
        zones_df = load_shapefile_data(zones_file)
        
        print("\nCleaning trips...")
        clean_trips_df, cleaning_log = clean_trips(raw_trips, zone_lookup)
        
        print(f"\nCleaned data ready:")
        print(f"  - Trips: {len(clean_trips_df):,} records")
        print(f"  - Zones: {len(zones_df)} zones")
        print(f"  - Data retention rate: {cleaning_log.get('retention_rate', 'N/A')}%")
        
        # STEP 2: Connect to database
        print("\nSTEP 2: CONNECTING TO DATABASE")
        print("-" * 70)
        
        if not os.path.exists(db_path):
            print(f"  Database not found at {db_path}")
            print("  Please run create_db.py first!")
            sys.exit(1)
        
        conn = sqlite3.connect(db_path)
        print(f"  Connected to: {db_path}")
        
        # STEP 3: Insert data
        print("\nSTEP 3: INSERTING DATA")
        print("-" * 70)
        
        borough_map = insert_boroughs(conn, zones_df)
        insert_payment_types(conn)
        insert_zones(conn, zones_df, borough_map)
        total_trips = insert_trips(conn, clean_trips_df)
        
        # STEP 4: Verify insertion
        print("\nSTEP 4: VERIFYING DATA")
        print("-" * 70)
        
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM boroughs")
        borough_count = cursor.fetchone()[0]
        print(f"  Boroughs: {borough_count}")
        
        cursor.execute("SELECT COUNT(*) FROM zones")
        zone_count = cursor.fetchone()[0]
        print(f"  Zones: {zone_count}")
        
        cursor.execute("SELECT COUNT(*) FROM payment_types")
        payment_count = cursor.fetchone()[0]
        print(f"  Payment types: {payment_count}")
        
        cursor.execute("SELECT COUNT(*) FROM trips")
        trip_count = cursor.fetchone()[0]
        print(f"  Trips: {trip_count:,}")
        
        conn.close()
        
        # Final summary
        print("\n" + "="*70)
        print("DATA LOADING COMPLETE")
        print("="*70)
        print(f"Successfully loaded {trip_count:,} taxi trips into the database.")
        print("Database is ready for API queries!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nERROR: Data loading failed - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
