/**
 * NYC Taxi Urban Mobility Explorer - Frontend Application
 * Handles API data fetching, chart rendering, map visualization, and user interactions
 */

// ========================================================================
// GLOBAL STATE & CONFIGURATION
// ========================================================================

const API_BASE_URL = 'http://127.0.0.1:5000/api';
const MAP_CENTER = [40.7128, -74.0060];  // NYC coordinates
const MAP_ZOOM = 10;

// Global chart instances (to prevent memory leaks)
const charts = {};

// Current filter state
const filterState = {
    borough: '',
    hour: '',
    minFare: '',
    maxFare: '',
    currentPage: 1
};

// ========================================================================
// INITIALIZATION
// ========================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('[APP] Initializing NYC Taxi Urban Mobility Explorer...');
    
    // Load all data on page load
    initializeApp();
    
    // Attach event listeners
    attachEventListeners();
});

/**
 * Initialize the application by fetching all data
 */
async function initializeApp() {
    try {
        // Fetch data in parallel
        const [overviewData, hourData, boroughData, fareData, speedData, paymentData, tripsData, geojsonData] = await Promise.all([
            fetchData('/overview'),
            fetchData('/trips/by-hour'),
            fetchData('/trips/by-borough'),
            fetchData('/trips/fare-distribution'),
            fetchData('/trips/speed-analysis'),
            fetchData('/trips/payment-types'),
            fetchData('/trips/filter'),
            fetchData('/zones/geojson')
        ]);

        // Update status
        updateDataStatus('ready');

        // Render all components
        renderOverview(overviewData);
        renderChartsHour(hourData);
        renderChartBorough(boroughData);
        renderChartFareDistribution(fareData);
        renderChartSpeed(speedData);
        renderChartPaymentTypes(paymentData);
        renderTripsTable(tripsData);
        renderMap(geojsonData);

        console.log('[APP] Initialization complete');
    } catch (error) {
        console.error('[APP] Error initializing app:', error);
        updateDataStatus('error');
    }
}

/**
 * Attach event listeners to filter buttons and table controls
 */
function attachEventListeners() {
    // Filter buttons
    document.getElementById('filter-apply').addEventListener('click', applyFilters);
    document.getElementById('filter-reset').addEventListener('click', resetFilters);

    // Pagination
    document.getElementById('trips-prev-page').addEventListener('click', () => prevPage());
    document.getElementById('trips-next-page').addEventListener('click', () => nextPage());

    // Real-time filter updates
    document.getElementById('filter-borough').addEventListener('change', (e) => {
        filterState.borough = e.target.value;
    });

    document.getElementById('filter-hour').addEventListener('change', (e) => {
        filterState.hour = e.target.value;
    });

    document.getElementById('filter-min-fare').addEventListener('change', (e) => {
        filterState.minFare = e.target.value;
    });

    document.getElementById('filter-max-fare').addEventListener('change', (e) => {
        filterState.maxFare = e.target.value;
    });
}

// ========================================================================
// API FETCHING FUNCTIONS
// ========================================================================

/**
 * Generic fetch function for API calls with error handling
 */
async function fetchData(endpoint, params = {}) {
    try {
        const queryParams = new URLSearchParams(params);
        const url = `${API_BASE_URL}${endpoint}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`[API] Error fetching ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Fetch filtered trips with current filter state
 */
async function fetchFilteredTrips(page = 1) {
    const params = {
        page: page,
        limit: 50
    };

    if (filterState.borough) params.borough = filterState.borough;
    if (filterState.hour) params.hour = filterState.hour;
    if (filterState.minFare) params.min_fare = filterState.minFare;
    if (filterState.maxFare) params.max_fare = filterState.maxFare;

    return await fetchData('/trips/filter', params);
}

/**
 * Fetch top K pickup zones
 */
async function fetchTopPickupZones(k = 10) {
    return await fetchData('/zones/top-pickup', { k: k });
}

// ========================================================================
// DATA STATUS UPDATE
// ========================================================================

/**
 * Update data status badge
 */
function updateDataStatus(status) {
    const statusBadge = document.getElementById('data-status');
    
    const statusMap = {
        loading: 'Loading...',
        ready: 'Database Ready',
        error: 'Connection Error'
    };

    statusBadge.textContent = statusMap[status] || status;
    statusBadge.className = `status-badge ${status === 'ready' ? 'ready' : ''}`;
}

// ========================================================================
// OVERVIEW RENDERING
// ========================================================================

/**
 * Render overview statistics (4 stat cards)
 */
function renderOverview(data) {
    if (!data || data.error) {
        console.error('[OVERVIEW] No data received');
        return;
    }

    document.getElementById('stat-total-trips').textContent = 
        formatNumber(data.total_trips);
    
    document.getElementById('stat-avg-fare').textContent = 
        $${parseFloat(data.average_fare).toFixed(2)};
    
    document.getElementById('stat-avg-distance').textContent = 
        `${parseFloat(data.average_distance).toFixed(1)} mi`;
    
    document.getElementById('stat-unique-zones').textContent = 
        data.unique_zones;

    console.log('[OVERVIEW] Statistics rendered');
}

// ========================================================================
// CHART RENDERING FUNCTIONS
// ========================================================================

/**
 * Render trips by hour line chart
 */
function renderChartsHour(data) {
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('chart-by-hour')?.getContext('2d');
    if (!ctx) return;

    // Destroy previous chart if exists
    if (charts.hourChart) charts.hourChart.destroy();

    const labels = data.map(item => `${item.hour}:00`);
    const tripCounts = data.map(item => item.trip_count);
    const avgFares = data.map(item => item.average_fare);

    charts.hourChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Trip Count',
                    data: tripCounts,
                    borderColor: '#FFD700',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Average Fare ($)',
                    data: avgFares,
                    borderColor: '#79c0ff',
                    backgroundColor: 'rgba(121, 192, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: {
                    labels: { color: '#e6edf3', padding: 15 }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(48, 54, 61, 0.5)' },
                    ticks: { color: '#8b949e' }
                },
                y: {
                    position: 'left',
                    grid: { color: 'rgba(48, 54, 61, 0.5)' },
                    ticks: { color: '#8b949e' },
                    title: { display: true, text: 'Trip Count', color: '#e6edf3' }
                },
                y1: {
                    position: 'right',
                    grid: { display: false },
                    ticks: { color: '#79c0ff' },
                    title: { display: true, text: 'Avg Fare ($)', color: '#79c0ff' }
                }
            }
        }
    });

    console.log('[CHART] Trips by hour rendered');
}

/**
 * Render trips by borough bar chart
 */
function renderChartBorough(data) {
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('chart-by-borough')?.getContext('2d');
    if (!ctx) return;

    if (charts.boroughChart) charts.boroughChart.destroy();

    const labels = data.map(item => item.borough);
    const tripCounts = data.map(item => item.trip_count);

    const colors = ['#FFD700', '#79c0ff', '#3fb950', '#f85149', '#d29922', '#a371f7'];

    charts.boroughChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Trips',
                data: tripCounts,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: '#FFD700',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e6edf3' }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(48, 54, 61, 0.5)' },
                    ticks: { color: '#8b949e' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#8b949e' }
                }
            }
        }
    });

    console.log('[CHART] Trips by borough rendered');
}

/**
 * Render fare distribution pie chart
 */
function renderChartFareDistribution(data) {
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('chart-fare-dist')?.getContext('2d');
    if (!ctx) return;

    if (charts.fareChart) charts.fareChart.destroy();

    const labels = data.map(item => item.fare_bucket);
    const counts = data.map(item => item.trip_count);

    const colors = ['#FFD700', '#FFF44F', '#79c0ff', '#3fb950', '#f85149', '#d29922', '#a371f7'];

    charts.fareChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: '#0d1117',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e6edf3', padding: 15 }
                }
            }
        }
    });

    console.log('[CHART] Fare distribution rendered');
}

/**
 * Render average speed by hour line chart
 */
function renderChartSpeed(data) {
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('chart-speed')?.getContext('2d');
    if (!ctx) return;

    if (charts.speedChart) charts.speedChart.destroy();

    const labels = data.map(item => `${item.hour}:00`);
    const avgSpeeds = data.map(item => item.average_speed);
    const maxSpeeds = data.map(item => item.max_speed);

    charts.speedChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Average Speed (mph)',
                    data: avgSpeeds,
                    borderColor: '#FFD700',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Max Speed (mph)',
                    data: maxSpeeds,
                    borderColor: '#f85149',
                    backgroundColor: 'rgba(248, 81, 73, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e6edf3' }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(48, 54, 61, 0.5)' },
                    ticks: { color: '#8b949e' }
                },
                y: {
                    grid: { color: 'rgba(48, 54, 61, 0.5)' },
                    ticks: { color: '#8b949e' },
                    title: { display: true, text: 'Speed (mph)', color: '#e6edf3' }
                }
            }
        }
    });

    console.log('[CHART] Speed analysis rendered');
}

/**
 * Render payment types pie chart
 */
function renderChartPaymentTypes(data) {
    if (!data || data.length === 0) return;

    const ctx = document.getElementById('chart-payment')?.getContext('2d');
    if (!ctx) return;

    if (charts.paymentChart) charts.paymentChart.destroy();

    const labels = data.map(item => item.payment_type);
    const counts = data.map(item => item.trip_count);

    const colors = ['#3fb950', '#79c0ff', '#d29922', '#f85149', '#a371f7'];

    charts.paymentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Trips',
                data: counts,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: '#FFD700',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'x',
            plugins: {
                legend: {
                    labels: { color: '#e6edf3' }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#8b949e' }
                },
                y: {
                    grid: { color: 'rgba(48, 54, 61, 0.5)' },
                    ticks: { color: '#8b949e' }
                }
            }
        }
    });

    console.log('[CHART] Payment types rendered');
}

/**
 * Render top pickup zones horizontal bar chart using custom MinHeap algorithm data
 */
async function renderChartTopZones() {
    try {
        const topZones = await fetchTopPickupZones(10);
        
        if (!topZones || topZones.length === 0) return;

        const ctx = document.getElementById('chart-top-zones')?.getContext('2d');
        if (!ctx) return;

        if (charts.topZonesChart) charts.topZonesChart.destroy();

        const labels = topZones.map(item => item.zone_name);
        const counts = topZones.map(item => item.trip_count);

        charts.topZonesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Trip Count (MinHeap Algorithm)',
                    data: counts,
                    backgroundColor: '#FFD700',
                    borderColor: '#FFF44F',
                    borderWidth: 2
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#e6edf3', font: { size: 11 } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(48, 54, 61, 0.5)' },
                        ticks: { color: '#8b949e' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#8b949e' }
                    }
                }
            }
        });

        console.log('[CHART] Top zones (MinHeap) rendered');
    } catch (error) {
        console.error('[CHART] Error rendering top zones:', error);
    }
}

// ========================================================================
// MAP RENDERING
// ========================================================================

let leafletMap = null;

/**
 * Render interactive Leaflet map with GeoJSON zones
 */
function renderMap(geojsonData) {
    if (!geojsonData || geojsonData.error) {
        console.error('[MAP] No GeoJSON data received');
        return;
    }

    // Initialize map if not already done
    if (!leafletMap) {
        leafletMap = L.map('map').setView(MAP_CENTER, MAP_ZOOM);

        // Add tile layer
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(leafletMap);
    }

    // Add GeoJSON layer with styling
    if (geojsonData.features && geojsonData.features.length > 0) {
        L.geoJSON(geojsonData, {
            style: function(feature) {
                return {
                    fillColor: '#FFD700',
                    weight: 2,
                    opacity: 0.8,
                    color: '#FFF44F',
                    fillOpacity: 0.2
                };
            },
            onEachFeature: function(feature, layer) {
                const props = feature.properties;
                const popup = `<strong>${props.zone}</strong><br/>
                               Location ID: ${props.location_id}<br/>
                               Borough: ${props.borough}`;
                layer.bindPopup(popup);
                
                // Highlight on hover
                layer.on('mouseover', function() {
                    this.setStyle({ fillOpacity: 0.4, weight: 3 });
                });
                layer.on('mouseout', function() {
                    this.setStyle({ fillOpacity: 0.2, weight: 2 });
                });
            }
        }).addTo(leafletMap);
    }

    console.log('[MAP] GeoJSON map rendered with', geojsonData.features?.length || 0, 'zones');
}

// ========================================================================
// TRIPS TABLE RENDERING
// ========================================================================

/**
 * Render trips table with pagination
 */
function renderTripsTable(data) {
    if (!data || data.error) {
        console.error('[TABLE] No data received');
        return;
    }

    const tbody = document.getElementById('trips-tbody');
    tbody.innerHTML = '';

    if (!data.trips || data.trips.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="loading-cell">No trips found</td></tr>';
        return;
    }

    // Create table rows
    data.trips.forEach(trip => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${trip.trip_id}</td>
            <td>${formatDateTime(trip.pickup_datetime)}</td>
            <td>${formatDateTime(trip.dropoff_datetime)}</td>
            <td>${trip.passenger_count}</td>
            <td>${parseFloat(trip.trip_distance).toFixed(2)}</td>
            <td>$${parseFloat(trip.fare_amount).toFixed(2)}</td>
            <td>$${parseFloat(trip.total_amount).toFixed(2)}</td>
            <td>${trip.pickup_zone}</td>
            <td>${trip.dropoff_zone}</td>
        `;
        tbody.appendChild(row);
    });

    // Update pagination info
    const start = (data.page - 1) * data.limit + 1;
    const end = Math.min(data.page * data.limit, data.total_count);
    document.getElementById('trips-showing').textContent = 
        `Showing ${start}-${end} of ${data.total_count} trips`;
    
    document.getElementById('trips-page').textContent = data.page;
    document.getElementById('trips-total-pages').textContent = data.total_pages;

    // Update button states
    document.getElementById('trips-prev-page').disabled = data.page === 1;
    document.getElementById('trips-next-page').disabled = data.page === data.total_pages;

    console.log('[TABLE] Trips table rendered, page', data.page, 'of', data.total_pages);
}

// ========================================================================
// FILTER FUNCTIONS
// ========================================================================

/**
 * Apply current filters and reload data
 */
async function applyFilters() {
    console.log('[FILTER] Applying filters:', filterState);
    filterState.currentPage = 1;
    
    try {
        const data = await fetchFilteredTrips(1);
        renderTripsTable(data);
    } catch (error) {
        console.error('[FILTER] Error applying filters:', error);
    }
}

/**
 * Reset all filters to default
 */
function resetFilters() {
    console.log('[FILTER] Resetting all filters');
    
    filterState.borough = '';
    filterState.hour = '';
    filterState.minFare = '';
    filterState.maxFare = '';
    filterState.currentPage = 1;

    document.getElementById('filter-borough').value = '';
    document.getElementById('filter-hour').value = '';
    document.getElementById('filter-min-fare').value = '';
    document.getElementById('filter-max-fare').value = '';

    applyFilters();
}

/**
 * Go to previous page of results
 */
async function prevPage() {
    if (filterState.currentPage > 1) {
        filterState.currentPage--;
        const data = await fetchFilteredTrips(filterState.currentPage);
        renderTripsTable(data);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Go to next page of results
 */
async function nextPage() {
    const totalPages = document.getElementById('trips-total-pages').textContent;
    if (filterState.currentPage < parseInt(totalPages)) {
        filterState.currentPage++;
        const data = await fetchFilteredTrips(filterState.currentPage);
        renderTripsTable(data);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// ========================================================================
// UTILITY FUNCTIONS
// ========================================================================

/**
 * Format large numbers with comma separators
 */
function formatNumber(num) {
    return num?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') || '0';
}

/**
 * Format datetime string to readable format
 */
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Log messages to console with prefix
 */
function logMessage(context, message) {
    console.log(`[${context}] ${message}`);
}

// ========================================================================
// RENDER TOP ZONES CHART ON LOAD
// ========================================================================

// Call this after initial data load
setTimeout(() => {
    renderChartTopZones();
}, 1000);