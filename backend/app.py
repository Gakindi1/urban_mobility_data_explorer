"""
NYC Taxi Urban Mobility Explorer - Flask Backend API
Provides 9 RESTful API endpoints for analyzing NYC taxi data
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os
import sys
import shapefile
from pyproj import Transformer

# Add parent directory to path for algorithm imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from algorithm.top_k_zones import get_top_k_zones

app = Flask(__name__)
CORS(app)

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'taxi_data.db')
SHAPEFILE_PATH = os.path.join(os.path.dirname(__file__), '../data/taxi_zones.shp')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db_connection():
    """Get database connection with row factory for dict-like access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def shapefile_to_geojson(shapefile_path):
    """Convert shapefile to GeoJSON with EPSG:2263 to EPSG:4326 transformation"""
    try:
        sf = shapefile.Reader(shapefile_path)
        transformer = Transformer.from_epsg_codes(2263, 4326, always_xy=True)
        
        features = []
        for shape_record in sf.shapeRecords():
            shape = shape_record.shape
            record = shape_record.record
            
            # Transform coordinates from EPSG:2263 to EPSG:4326 (lat/lon)
            if shape.shapeType == 5:  # Polygon
                coordinates = []
                for part_idx, part_start in enumerate(shape.parts):
                    part_end = shape.parts[part_idx + 1] if part_idx + 1 < len(shape.parts) else len(shape.points)
                    part_points = shape.points[part_start:part_end]
                    
                    transformed_part = []
                    for point in part_points:
                        lon, lat = transformer.transform(point[0], point[1])
                        transformed_part.append([lon, lat])
                    coordinates.append(transformed_part)
                
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": coordinates
                    },
                    "properties": {
                        "location_id": record[0],
                        "borough": record[1] if len(record) > 1 else "",
                        "zone": record[2] if len(record) > 2 else "",
                        "shape_length": float(record[4]) if len(record) > 4 else 0,
                        "shape_area": float(record[5]) if len(record) > 5 else 0
                    }
                }
                features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    except Exception as e:
        print(f"Error converting shapefile to GeoJSON: {e}")
        return {"type": "FeatureCollection", "features": []}


# ============================================================================
# API ENDPOINT 1: /api/overview
# Returns summary statistics about all taxi trips
# ============================================================================

@app.route('/api/overview', methods=['GET'])
def get_overview():
    """
    GET /api/overview
    Returns summary statistics for all taxi trips
    
    Response:
    {
        "total_trips": 478963,
        "total_fare": 45234567.89,
        "average_fare": 94.50,
        "total_distance": 2345678.50,
        "average_distance": 4.90,
        "unique_zones": 260,
        "total_passengers": 567890,
        "average_passengers": 1.5
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            COUNT(*) as total_trips,
            ROUND(SUM(total_amount), 2) as total_fare,
            ROUND(AVG(total_amount), 2) as average_fare,
            ROUND(SUM(trip_distance), 2) as total_distance,
            ROUND(AVG(trip_distance), 2) as average_distance,
            COUNT(DISTINCT pickup_location_id) as unique_zones,
            SUM(passenger_count) as total_passengers,
            ROUND(AVG(passenger_count), 2) as average_passengers
        FROM trips
        """
        
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                "total_trips": row[0],
                "total_fare": row[1],
                "average_fare": row[2],
                "total_distance": row[3],
                "average_distance": row[4],
                "unique_zones": row[5],
                "total_passengers": row[6],
                "average_passengers": row[7]
            })
        else:
            return jsonify({"error": "No data found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINT 2: /api/trips/by-hour
# Returns trip count and statistics grouped by pickup hour
# ============================================================================

@app.route('/api/trips/by-hour', methods=['GET'])
def get_trips_by_hour():
    """
    GET /api/trips/by-hour
    Returns trip count, average fare, and average distance grouped by pickup hour
    
    Response:
    [
        {
            "hour": 0,
            "trip_count": 5432,
            "average_fare": 12.50,
            "average_distance": 2.1
        },
        ...
    ]
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            pickup_hour as hour,
            COUNT(*) as trip_count,
            ROUND(AVG(total_amount), 2) as average_fare,
            ROUND(AVG(trip_distance), 2) as average_distance
        FROM trips
        GROUP BY pickup_hour
        ORDER BY pickup_hour
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        result = [
            {
                "hour": row[0],
                "trip_count": row[1],
                "average_fare": row[2],
                "average_distance": row[3]
            }
            for row in rows
        ]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINT 3: /api/trips/by-borough
# Returns trip statistics grouped by borough with zone details
# ============================================================================

@app.route('/api/trips/by-borough', methods=['GET'])
def get_trips_by_borough():
    """
    GET /api/trips/by-borough
    Returns trip count and statistics joined with borough and zone information
    
    Response:
    [
        {
            "borough": "Manhattan",
            "trip_count": 234567,
            "average_fare": 15.25,
            "average_distance": 3.2,
            "zones_count": 45
        },
        ...
    ]
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            b.borough_name,
            COUNT(t.trip_id) as trip_count,
            ROUND(AVG(t.total_amount), 2) as average_fare,
            ROUND(AVG(t.trip_distance), 2) as average_distance,
            COUNT(DISTINCT t.pickup_location_id) as zones_count
        FROM trips t
        JOIN zones z ON t.pickup_location_id = z.location_id
        JOIN boroughs b ON z.borough_id = b.borough_id
        GROUP BY b.borough_id, b.borough_name
        ORDER BY trip_count DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        result = [
            {
                "borough": row[0],
                "trip_count": row[1],
                "average_fare": row[2],
                "average_distance": row[3],
                "zones_count": row[4]
            }
            for row in rows
        ]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINT 4: /api/zones/top-pickup
# Returns top K pickup zones using custom MinHeap algorithm
# ============================================================================

@app.route('/api/zones/top-pickup', methods=['GET'])
def get_top_pickup_zones():
    """
    GET /api/zones/top-pickup?k=10
    Returns top K pickup zones by trip frequency using custom MinHeap algorithm
    
    Query Parameters:
        k (int): Number of top zones to return (default 10, max 100)
    
    Response:
    [
        {
            "location_id": 48,
            "zone_name": "Midtown Center",
            "borough": "Manhattan",
            "trip_count": 45678
        },
        ...
    ]
    """
    try:
        k = request.args.get('k', 10, type=int)
        k = min(k, 100)  # Cap at 100 for performance
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all location IDs (this will be used by custom algorithm)
        query = """
        SELECT pickup_location_id FROM trips ORDER BY pickup_location_id
        """
        cursor.execute(query)
        location_ids = [row[0] for row in cursor.fetchall()]
        
        # Use custom MinHeap algorithm to find top K
        top_zones = get_top_k_zones(location_ids, k)
        
        # Build result with zone details
        result = []
        for zone_id, trip_count in top_zones:
            zone_query = """
            SELECT z.location_id, z.zone_name, b.borough_name
            FROM zones z
            JOIN boroughs b ON z.borough_id = b.borough_id
            WHERE z.location_id = ?
            """
            cursor.execute(zone_query, (zone_id,))
            zone_row = cursor.fetchone()
            
            if zone_row:
                result.append({
                    "location_id": zone_row[0],
                    "zone_name": zone_row[1],
                    "borough": zone_row[2],
                    "trip_count": trip_count
                })
        
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINT 5: /api/trips/fare-distribution
# Returns fare amount distribution with SQL CASE bucketing
# ============================================================================

@app.route('/api/trips/fare-distribution', methods=['GET'])
def get_fare_distribution():
    """
    GET /api/trips/fare-distribution
    Returns distribution of trips grouped into fare buckets using SQL CASE statements
    
    Response:
    [
        {
            "fare_bucket": "$0-$5",
            "trip_count": 12345,
            "percentage": 2.57
        },
        ...
    ]
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            CASE 
                WHEN total_amount < 5 THEN '$0-$5'
                WHEN total_amount < 10 THEN '$5-$10'
                WHEN total_amount < 15 THEN '$10-$15'
                WHEN total_amount < 20 THEN '$15-$20'
                WHEN total_amount < 30 THEN '$20-$30'
                WHEN total_amount < 50 THEN '$30-$50'
                ELSE '$50+'
            END as fare_bucket,
            COUNT(*) as trip_count
        FROM trips
        GROUP BY fare_bucket
        ORDER BY 
            CASE 
                WHEN total_amount < 5 THEN 1
                WHEN total_amount < 10 THEN 2
                WHEN total_amount < 15 THEN 3
                WHEN total_amount < 20 THEN 4
                WHEN total_amount < 30 THEN 5
                WHEN total_amount < 50 THEN 6
                ELSE 7
            END
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Calculate total for percentage
        total = sum(row[1] for row in rows)
        
        result = [
            {
                "fare_bucket": row[0],
                "trip_count": row[1],
                "percentage": round((row[1] / total) * 100, 2)
            }
            for row in rows
        ]
        
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINT 6: /api/trips/filter
# Returns filtered trips with pagination and dynamic WHERE clauses
# ============================================================================

@app.route('/api/trips/filter', methods=['GET'])
def filter_trips():
    """
    GET /api/trips/filter?borough=Manhattan&hour=10&page=1&limit=50
    Returns filtered trips with pagination (max 50 rows per page)
    
    Query Parameters:
        borough (str): Filter by borough name (optional)
        hour (int): Filter by pickup hour 0-23 (optional)
        min_fare (float): Minimum fare amount (optional)
        max_fare (float): Maximum fare amount (optional)
        page (int): Page number, default 1
        limit (int): Results per page, max 50, default 50
    
    Response:
    {
        "trips": [
            {
                "trip_id": 1,
                "pickup_datetime": "2019-01-01 12:30:45",
                "dropoff_datetime": "2019-01-01 12:45:20",
                "passenger_count": 1,
                "trip_distance": 2.5,
                "fare_amount": 12.50,
                "total_amount": 15.00,
                "pickup_zone": "Midtown Center",
                "dropoff_zone": "Upper East Side"
            },
            ...
        ],
        "total_count": 5432,
        "page": 1,
        "limit": 50,
        "total_pages": 109
    }
    """
    try:
        # Get filter parameters
        borough = request.args.get('borough', None)
        hour = request.args.get('hour', None, type=int)
        min_fare = request.args.get('min_fare', None, type=float)
        max_fare = request.args.get('max_fare', None, type=float)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        limit = min(limit, 50)  # Cap at 50 per page
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic WHERE clause
        where_conditions = []
        params = []
        
        if borough:
            where_conditions.append("b.borough_name = ?")
            params.append(borough)
        
        if hour is not None:
            where_conditions.append("t.pickup_hour = ?")
            params.append(hour)
        
        if min_fare is not None:
            where_conditions.append("t.total_amount >= ?")
            params.append(min_fare)
        
        if max_fare is not None:
            where_conditions.append("t.total_amount <= ?")
            params.append(max_fare)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        count_query = f"""
        SELECT COUNT(*) FROM trips t
        JOIN zones pz ON t.pickup_location_id = pz.location_id
        JOIN boroughs b ON pz.borough_id = b.borough_id
        WHERE {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get filtered trips
        query = f"""
        SELECT 
            t.trip_id,
            t.pickup_datetime,
            t.dropoff_datetime,
            t.passenger_count,
            t.trip_distance,
            t.fare_amount,
            t.total_amount,
            pz.zone_name as pickup_zone,
            dz.zone_name as dropoff_zone
        FROM trips t
        JOIN zones pz ON t.pickup_location_id = pz.location_id
        JOIN zones dz ON t.dropoff_location_id = dz.location_id
        JOIN boroughs b ON pz.borough_id = b.borough_id
        WHERE {where_clause}
        ORDER BY t.pickup_datetime DESC
        LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        trips = [
            {
                "trip_id": row[0],
                "pickup_datetime": row[1],
                "dropoff_datetime": row[2],
                "passenger_count": row[3],
                "trip_distance": row[4],
                "fare_amount": row[5],
                "total_amount": row[6],
                "pickup_zone": row[7],
                "dropoff_zone": row[8]
            }
            for row in rows
        ]
        
        total_pages = (total_count + limit - 1) // limit
        
        return jsonify({
            "trips": trips,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINT 7: /api/zones/geojson
# Returns GeoJSON with coordinate transformation EPSG:2263 → EPSG:4326
# ============================================================================

@app.route('/api/zones/geojson', methods=['GET'])
def get_zones_geojson():
    """
    GET /api/zones/geojson
    Returns GeoJSON FeatureCollection with geographic boundaries transformed 
    from EPSG:2263 (New York Long Island Feet) to EPSG:4326 (WGS84 lat/lon)
    
    Response:
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-74.0, 40.7], ...]]
                },
                "properties": {
                    "location_id": 48,
                    "zone": "Midtown Center",
                    "borough": "Manhattan",
                    "shape_length": 45678.9,
                    "shape_area": 123456789.0
                }
            },
            ...
        ]
    }
    """
    try:
        geojson = shapefile_to_geojson(SHAPEFILE_PATH)
        return jsonify(geojson)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINT 8: /api/trips/speed-analysis
# Returns average speed by pickup hour with speed_mph derived feature
# ============================================================================

@app.route('/api/trips/speed-analysis', methods=['GET'])
def get_speed_analysis():
    """
    GET /api/trips/speed-analysis
    Returns average speed (mph) grouped by pickup hour
    
    Response:
    [
        {
            "hour": 0,
            "average_speed": 12.5,
            "max_speed": 45.2,
            "min_speed": 0.5,
            "trip_count": 5432
        },
        ...
    ]
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            pickup_hour as hour,
            ROUND(AVG(speed_mph), 2) as average_speed,
            ROUND(MAX(speed_mph), 2) as max_speed,
            ROUND(MIN(speed_mph), 2) as min_speed,
            COUNT(*) as trip_count
        FROM trips
        WHERE speed_mph IS NOT NULL AND speed_mph > 0
        GROUP BY pickup_hour
        ORDER BY pickup_hour
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        result = [
            {
                "hour": row[0],
                "average_speed": row[1],
                "max_speed": row[2],
                "min_speed": row[3],
                "trip_count": row[4]
            }
            for row in rows
        ]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINT 9: /api/trips/payment-types
# Returns trip statistics grouped by payment type
# ============================================================================

@app.route('/api/trips/payment-types', methods=['GET'])
def get_payment_types():
    """
    GET /api/trips/payment-types
    Returns trip count and fare statistics grouped by payment type
    
    Response:
    [
        {
            "payment_type": "Credit card",
            "trip_count": 234567,
            "total_fare": 3456789.50,
            "average_fare": 14.75
        },
        ...
    ]
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            pt.payment_description,
            COUNT(t.trip_id) as trip_count,
            ROUND(SUM(t.total_amount), 2) as total_fare,
            ROUND(AVG(t.total_amount), 2) as average_fare
        FROM trips t
        JOIN payment_types pt ON t.payment_type_id = pt.payment_type_id
        GROUP BY pt.payment_type_id, pt.payment_description
        ORDER BY trip_count DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        result = [
            {
                "payment_type": row[0],
                "trip_count": row[1],
                "total_fare": row[2],
                "average_fare": row[3]
            }
            for row in rows
        ]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trips")
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "trip_count": count
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("NYC TAXI URBAN MOBILITY EXPLORER - FLASK BACKEND API")
    print("=" * 70)
    print(f"Database: {DB_PATH}")
    print(f"Shapefile: {SHAPEFILE_PATH}")
    print("=" * 70)
    print("\nAPI Endpoints:")
    print("  [1] GET /api/overview - Summary statistics")
    print("  [2] GET /api/trips/by-hour - Trips grouped by hour")
    print("  [3] GET /api/trips/by-borough - Trips grouped by borough")
    print("  [4] GET /api/zones/top-pickup - Top K pickup zones (MinHeap)")
    print("  [5] GET /api/trips/fare-distribution - Fare distribution buckets")
    print("  [6] GET /api/trips/filter - Filtered trips with pagination")
    print("  [7] GET /api/zones/geojson - Zone boundaries as GeoJSON")
    print("  [8] GET /api/trips/speed-analysis - Speed analysis by hour")
    print("  [9] GET /api/trips/payment-types - Payment type statistics")
    print("  [+] GET /api/health - Health check")
    print("=" * 70)
    print("\nStarting Flask server on http://127.0.0.1:5000")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
