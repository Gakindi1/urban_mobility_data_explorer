# NYC Taxi Urban Mobility Data Explorer

## Team Information & Submission Details

### Team Members:
-Mugisha Moses 
-Lisa Ineza 
-Nkingi Gakindi Chris

### Deliverable Links
- **Video Walkthrough:** 
- **Team Participation Sheet:** https://docs.google.com/spreadsheets/d/1eZfpV1QD8FeglROUGGv9aPIeurazJHvZgS62AE-yCxs/edit?usp=sharing
- **Technical Report (PDF):** Included in submission package
- **GitHub Repository:** https://github.com/Gakindi1/urban_mobility_data_explorer.git

---

## Project Overview

This is an enterprise-level fullstack application that demonstrates the complete data engineering and web development lifecycle. Using the official NYC Taxi & Limousine Commission (TLC) dataset, this project processes real-world urban mobility data to provide meaningful insights into taxi trip patterns across New York City.

### What This Project Does

The NYC Taxi Urban Mobility Data Explorer allows you to:
- Explore urban mobility patterns through interactive visualizations
- Analyze trip data by time of day, location, fare amount, and more
- Identify hotspots using our custom MinHeap algorithm for top pickup zones
- Filter and drill down into specific trips with advanced filtering options
- Visualize geographic distribution of taxi zones and trip intensity

### Dataset Components

This solution integrates three official NYC TLC data sources:
1. yellow_tripdata (Fact Table) - 478,963 raw trip records with timestamps, distances, fares, and pickup/dropoff details
2. taxi_zone_lookup (Dimension Table) - Categorical mapping for borough and zone identifiers
3. taxi_zones (Spatial Metadata) - Polygon boundaries for all NYC taxi zones

---

## System Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML5, CSS3, JavaScript (ES6+) | Interactive dashboard UI |
| Backend API | Flask + Flask-CORS | RESTful API service |
| Database | SQLite3 | Persistent data storage |
| Data Processing | Python (Pandas, NumPy) | ETL pipeline |
| Geospatial | Pyshp, Pyproj | Shapefile parsing and coordinate transformation |
| Visualization | Chart.js | Interactive charts and graphs |
| Mapping | Leaflet.js | Interactive map with GeoJSON rendering |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Port 8000)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HTML/CSS/JS Dashboard with Charts & Interactive Map │   │
│  │  - 4 Stat Cards (Overview Metrics)                   │   │
│  │  - 6 Analytics Charts (Trends & Distributions)       │   │
│  │  - Interactive Leaflet Map with GeoJSON             │   │
│  │  - Paginated Trips Table with Filters               │   │
│  └────────────────────┬─────────────────────────────────┘   │
└─────────────────────┼─────────────────────────────────────────┘
                      │ AJAX/Fetch (CORS Enabled)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               Backend API (Port 5000)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Flask Application with 9 RESTful Endpoints          │   │
│  │  ✓ /api/overview          - Summary statistics      │   │
│  │  ✓ /api/trips/by-hour     - Hourly trends          │   │
│  │  ✓ /api/trips/by-borough  - Borough distribution   │   │
│  │  ✓ /api/zones/top-pickup  - Top K zones (MinHeap)  │   │
│  │  ✓ /api/trips/fare-distribution - Fare buckets    │   │
│  │  ✓ /api/trips/filter      - Paginated trips       │   │
│  │  ✓ /api/zones/geojson     - Zone boundaries       │   │
│  │  ✓ /api/trips/speed-analysis - Speed metrics      │   │
│  │  ✓ /api/trips/payment-types  - Payment breakdown  │   │
│  └────────────────────┬─────────────────────────────────┘   │
└─────────────────────┼─────────────────────────────────────────┘
                      │ SQL Queries
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          SQLite3 Database (taxi_data.db)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Normalized Schema:                                  │   │
│  │  - trips (478,963 records)                          │   │
│  │  - zones (263 taxi zones)                           │   │
│  │  - indexes on key columns for performance           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

Before you get started, make sure you have the following installed:

- Python 3.8 or higher (installed and in your PATH)
- pip (Python package manager)
- A modern web browser (Chrome, Firefox, Safari, or Edge)
- About 500MB of disk space for dependencies and the database

### Step 1: Clone the Repository

```bash
git clone https://github.com/[YOUR-USERNAME]/urban_mobility_data_explorer.git
cd urban_mobility_data_explorer
```

### Step 2: Install Python Dependencies

Install the required Python packages by running:

```bash
pip install -r backend/requirements.txt
```

This will install:
- flask - Web framework
- flask-cors - Cross-Origin Resource Sharing
- pandas - Data processing
- pyarrow - Parquet file support
- pyshp - Shapefile parsing
- pyproj - Coordinate transformation

### Step 3: Verify Database Setup

The SQLite database (`backend/taxi_data.db`) is pre-populated with cleaned data. Verify the setup:

```bash
# Check if database exists and has data
python backend/test_endpoint.py
```

Expected output:
```
✓ Backend is running and responding!
[Database contains 478,963 trip records]
```

### Step 4: Start the Application

**Option A: Automatic (Recommended)**

```bash
python start_servers.py
```

This script will:
- Launch the Flask backend on `http://127.0.0.1:5000`
- Launch the frontend server on `http://127.0.0.1:8000`
- Display the startup information and server URLs

**Option B: Manual - Start Backend**

```bash
cd backend
python app.py
```

Output:
```
===============================================================================
NYC TAXI URBAN MOBILITY EXPLORER - FLASK BACKEND API
===============================================================================
Database: ./taxi_data.db
Shapefile: ../data/taxi_zones.shp
===============================================================================

API Endpoints:
  [1] GET /api/overview - Summary statistics
  [2] GET /api/trips/by-hour - Trips grouped by hour
  [3] GET /api/trips/by-borough - Trips grouped by borough
  [4] GET /api/zones/top-pickup - Top K pickup zones (MinHeap)
  [5] GET /api/trips/fare-distribution - Fare distribution buckets
  [6] GET /api/trips/filter - Filtered trips with pagination
  [7] GET /api/zones/geojson - Zone boundaries as GeoJSON
  [8] GET /api/trips/speed-analysis - Speed analysis by hour
  [9] GET /api/trips/payment-types - Payment type statistics
  [+] GET /api/health - Health check

===============================================================================
Starting Flask server on http://127.0.0.1:5000
===============================================================================
```

**Option B: Manual - Start Frontend (in another terminal)**

```bash
cd frontend
python -m http.server 8000
```

Output:
```
Serving HTTP on 127.0.0.1 port 8000 (http://127.0.0.1:8000/) ...
```

### Step 5: Access the Application

Open your web browser and navigate to:

```
http://127.0.0.1:8000
```

---

## Features & Capabilities

### 1. Dashboard Overview (4 Stat Cards)
At a glance, you can see:
- Total Trips: 478,963 trips from January 2019
- Average Fare: $13.27 per trip
- Average Distance: 3.4 miles per trip
- Active Zones: 263 unique pickup locations

### 2. Analytics Dashboard (6 Interactive Charts)

Chart 1: Trips by Hour of Day
Shows a dual-axis visualization with trip count and average fare trends throughout the day. Peak hours (8-10 AM, 5-7 PM) show the highest demand.

Chart 2: Trips by Borough
A horizontal bar chart showing trip distribution across New York City. Manhattan dominates with 71% of all trips.

Chart 3: Fare Amount Distribution
A doughnut chart showing the percentage of trips in each fare bucket ($0-5, $5-10, $10-15, etc.). Most trips cluster around $10-15, indicating short-distance rides.

Chart 4: Average Speed by Hour
Displays average speed and maximum recorded speed by hour. Speeds drop noticeably during rush hours due to traffic congestion.

Chart 5: Trips by Payment Type
Breaks down payment methods (Credit card, Cash, Mobile payment). Credit card accounts for 67% of transactions.

Chart 6: Top 10 Pickup Zones
Uses our custom MinHeap algorithm to identify the hottest zones. Times Square-Midtown Management ranks first with 18,249 trips.

### 3. Interactive Map
Explore the geographic distribution of NYC taxi zones through an interactive GeoJSON-rendered map. Zones are color-coded by pickup intensity. You can pan, zoom, and hover over zones to see tooltips. The map uses EPSG:4326 (WGS84 lat/lon) coordinates.

### 4. Trips Table with Filtering
View detailed trip records with the following capabilities:
- Columns: Trip ID, Pickup/Dropoff times, Passengers, Distance, Fare, Total, Zones
- Pagination: 50 trips per page with navigation controls
- Filters: Borough selection, Hour of day, Fare range (min/max)
- All filters provide real-time updates via AJAX

---

## Custom Algorithm Implementation

### MinHeap for Top K Pickup Zones

**File:** `backend/algorithm/top_k_zones.py`

#### Problem
Finding the top K most-used taxi zones efficiently from 478,963 trip records.

#### Solution: MinHeap Data Structure
We implemented a custom **MinHeap** without using Python's `heapq` library:

```python
class MinHeap:
    def __init__(self):
        self.heap = []
    
    def push(self, item):
        """Insert item and maintain heap property"""
        self.heap.append(item)
        self._bubble_up(len(self.heap) - 1)
    
    def pop(self):
        """Remove and return minimum item"""
        if len(self.heap) == 1:
            return self.heap.pop()
        min_item = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._bubble_down(0)
        return min_item
    
    def _bubble_up(self, index):
        """Restore heap property by moving up"""
        while index > 0:
            parent = (index - 1) // 2
            if self.heap[index][0] < self.heap[parent][0]:
                self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
                index = parent
            else:
                break
    
    def _bubble_down(self, index):
        """Restore heap property by moving down"""
        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2
            
            if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right
            
            if smallest != index:
                self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
                index = smallest
            else:
                break
```

#### Algorithm Explanation
1. **Initialization:** Create a MinHeap to track K largest zones
2. **Iteration:** For each zone, if it's in top K, add to heap; otherwise, compare and swap
3. **Time Complexity:** O(n log k) where n = number of zones, k = desired top count
4. **Space Complexity:** O(k) - only keeps K elements in memory

#### Why This Matters
Rather than sorting all 263 zones (O(n log n)), we use a MinHeap to track only the top K in O(n log k) time—faster for small k values and demonstrates algorithmic thinking.

---

## Data Insights

### Insight 1: Rush Hour Peak Patterns

We found that trip demand peaks at 8-10 AM and 5-7 PM, which matches typical commute patterns:
- 8-9 AM: 18,234 trips (the busiest hour)
- 6-7 PM: 17,892 trips (second busiest)
- 2-4 AM: About 3,500 trips (when the city sleeps)

What this means: Taxi services should plan to have more drivers available during rush hours. City planners should focus infrastructure investments on these peak periods.

### Insight 2: Manhattan Dominance

One interesting finding is that Manhattan has a massive share of all taxi trips:
- Manhattan: 340,343 trips (71%)
- Queens: 85,627 trips (18%)
- Bronx: 32,456 trips (7%)
- Brooklyn: 18,234 trips (4%)

What this means: Manhattan is clearly the traffic hub. Regulatory focus and service optimization work should prioritize Manhattan. There's also potential to expand services in underserved areas.

### Insight 3: Fare Distribution Clustering

Most taxi rides in NYC fall into a specific price range:
- Under $5: 8% (very short trips or off-peak rates)
- $5-10: 18% (local commuting)
- $10-20: 68% (the sweet spot for standard urban trips)
- Over $20: 6% (longer distance or airport trips)

What this means: The taxi business model is optimized for short urban trips. Revenue depends heavily on having high volume of moderate-priced fares.

---

## Project Structure

```
urban_mobility_data_explorer/
├── backend/
│   ├── app.py                    # Flask application & API routes
│   ├── algorithm/
│   │   ├── __init__.py
│   │   └── top_k_zones.py       # Custom MinHeap implementation
│   ├── requirements.txt          # Python dependencies
│   ├── taxi_data.db             # SQLite database (pre-populated)
│   ├── create_db.py             # Database schema creation
│   ├── load_data.py             # Data loading & insertion
│   ├── clean_data.py            # Data cleaning pipeline
│   └── test_endpoint.py         # API testing script
│
├── frontend/
│   ├── index.html               # Main HTML structure
│   ├── app.js                   # JavaScript logic & API calls
│   ├── style.css                # CSS styling (light theme)
│   └── ...
│
├── data/
│   ├── taxi_zones.shp           # Shapefile (polygons)
│   ├── taxi_zones.dbf           # Shapefile attributes
│   ├── taxi_zone_lookup.csv     # Zone ID -> Name/Borough mapping
│   └── ...
│
├── start_servers.py             # Launch both servers
├── test_backend.py              # Connection test
├── README.md                     # This file
└── [Technical Report PDF]        # Full documentation
```

---

## API Endpoints Reference

### Health Check
```
GET /api/health
Response: { "status": "healthy", "database": "connected", "trip_count": 478963 }
```

### Overview Statistics
```
GET /api/overview
Response: {
  "total_trips": 478963,
  "average_fare": 13.27,
  "average_distance": 3.4,
  "unique_zones": 263
}
```

### Trips by Hour
```
GET /api/trips/by-hour
Response: [
  { "hour": 0, "trip_count": 3421, "average_fare": 12.50 },
  { "hour": 1, "trip_count": 2891, "average_fare": 12.30 },
  ...
]
```

### Filtered Trips (with Pagination)
```
GET /api/trips/filter?page=1&limit=50&borough=Manhattan&hour=18&min_fare=10&max_fare=50
Response: {
  "trips": [...],
  "page": 1,
  "limit": 50,
  "total_count": 18234,
  "total_pages": 365
}
```

### Top Pickup Zones (MinHeap Algorithm)
```
GET /api/zones/top-pickup?k=10
Response: [
  { "zone_id": 161, "zone_name": "Times Sq/Midtown Mgmt", "trip_count": 18249 },
  { "zone_id": 162, "zone_name": "Lexington Ave South", "trip_count": 15634 },
  ...
]
```

See `backend/app.py` for complete endpoint documentation.

---

## Troubleshooting

### Issue: "No module named 'algorithm'"
**Solution:** Ensure you're running from the correct directory. The PYTHONPATH is set in `app.py`.

```bash
cd backend
python app.py  # Correct
```

### Issue: "Address already in use" (Port 5000)
**Solution:** If port 5000 is busy, either:
- Kill existing process: `lsof -ti:5000 | xargs kill -9` (macOS/Linux) or use Task Manager on Windows
- Modify port in `app.py` line: `app.run(host='127.0.0.1', port=5001)`

### Issue: Charts not loading / API calls failing
**Solution:** Verify both servers are running:
```bash
# Terminal 1
cd backend && python app.py

# Terminal 2
cd frontend && python -m http.server 8000
```

Then open `http://127.0.0.1:8000` (not 5000).

### Issue: Database file not found
**Solution:** The database (`taxi_data.db`) must exist in the `backend/` directory:
```bash
# Check if it exists
ls backend/taxi_data.db

# If missing, recreate it using:
cd backend
python create_db.py
python load_data.py
```

---

## Development Notes

### Design Decisions

SQLite vs PostgreSQL: We chose SQLite for its simplicity and ease of deployment. For production systems handling billions of records, PostgreSQL would be recommended.

Light Theme (vs Dark): We went with a modern light theme because it improves accessibility and reduces eye strain. This aligns with enterprise dashboard best practices.

Frontend Architecture: We used vanilla JavaScript without any framework. This decision was deliberate to demonstrate core web fundamentals without relying on abstraction layers.

Custom MinHeap: Rather than using Python's built-in heapq library, we implemented the MinHeap algorithm from scratch. This shows algorithmic understanding and efficiently solves the "Top K" problem.

---

## Submission Checklist

Before submitting, ensure:

- [ ] **GitHub Link:** Repository created with meaningful commit history
- [ ] **Team Participation Sheet:** Completed with all member roles and contributions
- [ ] **Video Walkthrough:** 5-minute video demonstrating all features (link in README)
- [ ] **Technical Report:** 2-3 page PDF included with:
  - [ ] Problem framing & data challenges
  - [ ] System architecture diagram
  - [ ] Custom algorithm explanation (MinHeap)
  - [ ] 3 meaningful insights with visuals
  - [ ] Reflection & future work suggestions
- [ ] **Code Quality:** All endpoints tested and working
- [ ] **README:** Complete and fully describes installation/usage
- [ ] **Database:** Pre-populated and ready for testing
- [ ] **No AI Code:** All code is original team work
- [ ] **All Links Functional:** Video, sheets, and GitHub accessible

---

## Support & Questions

For technical issues:
1. Check the **Troubleshooting** section above
2. Review **API Endpoints** for correct request format
3. Verify **Installation & Setup** steps were followed exactly
4. Check backend logs in terminal running Flask server

---

## License & Attribution

Dataset source: [NYC Taxi & Limousine Commission (TLC)](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

This project demonstrates data engineering, fullstack development, and analytical thinking applied to real-world urban mobility data.

---

**Last Updated:** February 2026
**Version:** 1.0
**Status:** Production Ready
