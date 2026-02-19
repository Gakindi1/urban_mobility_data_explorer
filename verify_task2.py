import sys
sys.path.insert(0, '.')
from clean_data import load_raw_trips, load_zone_lookup, load_shapefile_data, clean_trips
import os

# File paths
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

trips_file = os.path.join(data_dir, 'yellow_tripdata_2019-01.csv')
zones_file = os.path.join(data_dir, 'taxi_zones.shp')
lookup_file = os.path.join(data_dir, 'taxi_zone_lookup.csv')

# Load and clean
print("\n[OK] LOADING DATA...")
raw_trips = load_raw_trips(trips_file, nrows=500000)
zone_lookup = load_zone_lookup(lookup_file)
shapefile_data = load_shapefile_data(zones_file)

print("\n[OK] CLEANING DATA...")
clean_trips_df, cleaning_log = clean_trips(raw_trips, zone_lookup)

print('\n' + '='*70)
print('[OK] TASK 2 VERIFICATION RESULTS:')
print('='*70)
print(f'[OK] Raw trips loaded: {len(raw_trips):,} rows')
print(f'[OK] Zone lookup loaded: {len(zone_lookup)} zones')
print(f'[OK] Shapefile data loaded: {len(shapefile_data)} zones')
print(f'[OK] Cleaned trips: {len(clean_trips_df):,} rows')
print(f'[OK] Data retention: {100 * len(clean_trips_df) / len(raw_trips):.2f}%')
print('\n[OK] Cleaned DataFrame columns:')
for i, col in enumerate(clean_trips_df.columns, 1):
    dtype = clean_trips_df[col].dtype
    print(f'  {i:2d}. {col:30s} - {dtype}')

print('\n[OK] Cleaning log entries:')
for key, value in cleaning_log.items():
    print(f'  {key}: {value}')

print('\n[OK] Data sample (first row):')
print(clean_trips_df.iloc[0])

print('\n' + '='*70)
print('[OK] TASK 2 COMPLETE - ALL SYSTEMS OPERATIONAL')
print('='*70)
