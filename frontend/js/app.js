/**
 * Main Application Logic
 */

// State management
const state = {
    currentPage: 0,
    pageSize: 50,
    filters: {},
    totalTrips: 0
};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Initializing Urban Mobility Data Explorer...');
    
    try {
        await loadSummary();
        await loadCharts();
        await loadTrips();
        await generateInsights();
        setupEventListeners();
        
        console.log('✅ App initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing app:', error);
        alert('Failed to load data. Please ensure the backend server is running on http://localhost:3000');
    }
});

// Load summary statistics
async function loadSummary() {
    try {
        const data = await api.getSummary();
        const summary = data.summary;

        document.getElementById('total-trips').textContent = Number(summary.total_trips).toLocaleString();
        document.getElementById('total-revenue').textContent = `$${Number(summary.total_revenue).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        document.getElementById('avg-distance').textContent = Number(summary.avg_distance).toFixed(2);
        document.getElementById('avg-duration').textContent = Number(summary.avg_duration).toFixed(1);
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Load all charts
async function loadCharts() {
    try {
        // Hourly demand
        const hourlyData = await api.getHourlyDemand();
        charts.renderHourlyDemand(hourlyData.hourlyDemand);

        // Borough stats
        const boroughData = await api.getBoroughStats();
        charts.renderBoroughChart(boroughData.boroughStats);

        // Payment distribution
        const paymentData = await api.getPaymentDistribution();
        charts.renderPaymentChart(paymentData.paymentDistribution);

        // Speed by hour
        const speedData = await api.getSpeedByHour();
        charts.renderSpeedChart(speedData.speedByHour);

        // Top routes
        const routesData = await api.getTopRoutes(10);
        charts.renderRoutesChart(routesData.topRoutes);
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

// Load trips table
async function loadTrips() {
    try {
        const data = await api.getTrips({
            ...state.filters,
            limit: state.pageSize,
            offset: state.currentPage * state.pageSize
        });

        state.totalTrips = data.pagination.total;
        renderTripsTable(data.trips);
        updatePagination(data.pagination);
    } catch (error) {
        console.error('Error loading trips:', error);
        document.getElementById('trips-tbody').innerHTML = '<tr><td colspan="8" class="loading">Error loading trips</td></tr>';
    }
}


// Render trips table
function renderTripsTable(trips) {
    const tbody = document.getElementById('trips-tbody');
    
    if (trips.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading">No trips found</td></tr>';
        return;
    }

    tbody.innerHTML = trips.map(trip => `
        <tr>
            <td>${new Date(trip.pickupDatetime).toLocaleString()}</td>
            <td>${trip.pickupZone.zone} (${trip.pickupZone.borough})</td>
            <td>${trip.dropoffZone.zone} (${trip.dropoffZone.borough})</td>
            <td>${Number(trip.tripDistance).toFixed(2)}</td>
            <td>${trip.tripDurationMinutes || 'N/A'}</td>
            <td>$${Number(trip.fareAmount).toFixed(2)}</td>
            <td>${trip.tipPercentage ? Number(trip.tipPercentage).toFixed(1) + '%' : 'N/A'}</td>
            <td>$${Number(trip.totalAmount).toFixed(2)}</td>
        </tr>
    `).join('');
}

// Update pagination controls
function updatePagination(pagination) {
    const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
    const totalPages = Math.ceil(pagination.total / pagination.limit);

    document.getElementById('trip-count').textContent = `Showing ${pagination.offset + 1}-${Math.min(pagination.offset + pagination.limit, pagination.total)} of ${pagination.total.toLocaleString()} trips`;
    document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages}`;
    
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = !pagination.hasMore;
}

// Generate insights
async function generateInsights() {
    try {
        // Peak hours insight
        const hourlyData = await api.getHourlyDemand();
        const peakHour = hourlyData.hourlyDemand.reduce((max, curr) => 
            Number(curr.trip_count) > Number(max.trip_count) ? curr : max
        );
        document.getElementById('insight-peak-hours').textContent = 
            `Peak demand occurs at ${peakHour.hour_of_day}:00 with ${Number(peakHour.trip_count).toLocaleString()} trips. Evening rush hour (6-7 PM) shows the highest taxi usage.`;

        // Busiest borough insight
        const boroughData = await api.getBoroughStats();
        const busiestBorough = boroughData.boroughStats[0];
        document.getElementById('insight-busiest-borough').textContent = 
            `${busiestBorough.borough} dominates with ${Number(busiestBorough.trip_count).toLocaleString()} trips (${((Number(busiestBorough.trip_count) / state.totalTrips) * 100).toFixed(1)}% of all trips), generating $${Number(busiestBorough.total_revenue).toLocaleString()} in revenue.`;

        // Tipping behavior insight
        const paymentData = await api.getPaymentDistribution();
        const creditCard = paymentData.paymentDistribution.find(p => p.paymentType === 'Credit Card');
        const cash = paymentData.paymentDistribution.find(p => p.paymentType === 'Cash');
        document.getElementById('insight-tipping').textContent = 
            `Credit card users tip ${Number(creditCard.avgTipPercentage).toFixed(1)}% on average, while cash payments show ${Number(cash.avgTipPercentage).toFixed(1)}% average tip. Digital payments encourage higher tipping rates.`;
    } catch (error) {
        console.error('Error generating insights:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Apply filters
    document.getElementById('apply-filters').addEventListener('click', () => {
        state.filters = {
            borough: document.getElementById('borough-filter').value,
            paymentType: document.getElementById('payment-filter').value,
            minFare: document.getElementById('min-fare').value,
            maxFare: document.getElementById('max-fare').value
        };
        state.currentPage = 0;
        loadTrips();
    });

    // Reset filters
    document.getElementById('reset-filters').addEventListener('click', () => {
        document.getElementById('borough-filter').value = '';
        document.getElementById('payment-filter').value = '';
        document.getElementById('min-fare').value = '';
        document.getElementById('max-fare').value = '';
        state.filters = {};
        state.currentPage = 0;
        loadTrips();
    });

    // Pagination
    document.getElementById('prev-page').addEventListener('click', () => {
        if (state.currentPage > 0) {
            state.currentPage--;
            loadTrips();
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        state.currentPage++;
        loadTrips();
    });
}
