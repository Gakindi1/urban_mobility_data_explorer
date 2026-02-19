"""
Database Creation Script for NYC Taxi Trip Data

This script creates a normalized SQLite database schema with four tables:
- boroughs: Stores NYC boroughs
- zones: Stores taxi zone information with geographic data
- payment_types: Stores payment type lookup values
- trips: Stores cleaned taxi trip records

The script creates appropriate indexes for efficient querying and enforces
foreign key constraints for data integrity.
"""

import sqlite3
import os


def create_database(db_path):
    """
    Create the SQLite database with normalized schema and indexes.
    
    Args:
        db_path: Path where the database file will be created
    
    Returns:
        None
    """
    print(f"Creating database at: {db_path}")
    
    try:
        # Connect to database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\nDropping existing tables if they exist...")
        
        # Drop existing tables to allow clean creation
        cursor.execute("DROP TABLE IF EXISTS trips")
        cursor.execute("DROP TABLE IF EXISTS payment_types")
        cursor.execute("DROP TABLE IF EXISTS zones")
        cursor.execute("DROP TABLE IF EXISTS boroughs")
        
        print("Creating table: boroughs")
        
        # TABLE 1: Boroughs (dimension table)
        # Stores the five NYC boroughs
        cursor.execute("""
        CREATE TABLE boroughs (
            borough_id INTEGER PRIMARY KEY AUTOINCREMENT,
            borough_name TEXT NOT NULL UNIQUE
        )
        """)
        
        print("Creating table: zones")
        
        # TABLE 2: Zones (dimension table)
        # Stores taxi zone information with geographic boundaries
        cursor.execute("""
        CREATE TABLE zones (
            location_id INTEGER PRIMARY KEY,
            zone_name TEXT NOT NULL,
            borough_id INTEGER NOT NULL,
            shape_length REAL,
            shape_area REAL,
            FOREIGN KEY (borough_id) REFERENCES boroughs(borough_id)
        )
        """)
        
        print("Creating table: payment_types")
        
        # TABLE 3: Payment Types (dimension table)
        # Stores payment type lookup values
        cursor.execute("""
        CREATE TABLE payment_types (
            payment_type_id INTEGER PRIMARY KEY,
            payment_description TEXT NOT NULL
        )
        """)
        
        print("Creating table: trips")
        
        # TABLE 4: Trips (fact table)
        # Stores the actual taxi trip records with derived features
        cursor.execute("""
        CREATE TABLE trips (
            trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pickup_datetime TEXT NOT NULL,
            dropoff_datetime TEXT NOT NULL,
            passenger_count INTEGER,
            trip_distance REAL,
            pickup_location_id INTEGER NOT NULL,
            dropoff_location_id INTEGER NOT NULL,
            payment_type_id INTEGER,
            fare_amount REAL,
            tip_amount REAL,
            total_amount REAL,
            trip_duration_minutes REAL,
            speed_mph REAL,
            fare_per_mile REAL,
            pickup_hour INTEGER,
            pickup_day_of_week INTEGER,
            FOREIGN KEY (pickup_location_id) REFERENCES zones(location_id),
            FOREIGN KEY (dropoff_location_id) REFERENCES zones(location_id),
            FOREIGN KEY (payment_type_id) REFERENCES payment_types(payment_type_id)
        )
        """)
        
        print("Creating indexes for efficient querying...")
        
        # Create indexes on frequently queried columns
        cursor.execute("CREATE INDEX idx_trips_pickup_location ON trips(pickup_location_id)")
        cursor.execute("CREATE INDEX idx_trips_dropoff_location ON trips(dropoff_location_id)")
        cursor.execute("CREATE INDEX idx_trips_pickup_hour ON trips(pickup_hour)")
        cursor.execute("CREATE INDEX idx_trips_pickup_datetime ON trips(pickup_datetime)")
        cursor.execute("CREATE INDEX idx_trips_pickup_day_of_week ON trips(pickup_day_of_week)")
        
        print("Enabling foreign key constraints...")
        
        # Enable foreign key enforcement
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "="*70)
        print("DATABASE CREATION SUCCESSFUL")
        print("="*70)
        print(f"Database: {db_path}")
        print("\nTables created:")
        print("  1. boroughs - NYC borough dimension")
        print("  2. zones - Taxi zone dimension with geographic data")
        print("  3. payment_types - Payment type lookup")
        print("  4. trips - Main fact table with trip records")
        print("\nIndexes created:")
        print("  - idx_trips_pickup_location")
        print("  - idx_trips_dropoff_location")
        print("  - idx_trips_pickup_hour")
        print("  - idx_trips_pickup_datetime")
        print("  - idx_trips_pickup_day_of_week")
        print("\nForeign keys: ENABLED")
        print("="*70)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"ERROR: Database creation failed - {e}")
        raise
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        raise


def verify_database(db_path):
    """
    Verify the database was created correctly by checking tables and indexes.
    
    Args:
        db_path: Path to the database file
    
    Returns:
        None
    """
    print("\nVerifying database structure...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query sqlite_master to get all tables and indexes
        print("\nTables in database:")
        cursor.execute("SELECT name, type FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        for table_name, table_type in tables:
            print(f"  - {table_name} ({table_type})")
        
        print("\nIndexes in database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name")
        indexes = cursor.fetchall()
        for (index_name,) in indexes:
            print(f"  - {index_name}")
        
        # Verify table schemas
        print("\nTable schemas:")
        for table_name, _ in tables:
            print(f"\n  {table_name}:")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col_id, col_name, col_type, notnull, default, pk in columns:
                pk_indicator = " [PRIMARY KEY]" if pk else ""
                nn_indicator = " [NOT NULL]" if notnull else ""
                print(f"    - {col_name} ({col_type}){pk_indicator}{nn_indicator}")
        
        conn.close()
        print("\nDatabase verification complete!")
        
    except Exception as e:
        print(f"ERROR during verification: {e}")
        raise


if __name__ == "__main__":
    # Set up database path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'taxi_data.db')
    
    print("\n" + "="*70)
    print("NYC TAXI DATABASE CREATION")
    print("="*70)
    
    # Create the database
    create_database(db_path)
    
    # Verify the database
    verify_database(db_path)
    
    print("\nReady for data insertion!")
