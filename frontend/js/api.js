/**
 * API Client for Urban Mobility Data Explorer
 */

const API_BASE_URL = 'http://localhost:3000/api';

const api = {
    // Get trips with filters
    async getTrips(filters = {}) {
        try {
            const params = new URLSearchParams();
            
            if (filters.borough) params.append('borough', filters.borough);
            if (filters.paymentType) params.append('paymentType', filters.paymentType);
            if (filters.minFare) params.append('minFare', filters.minFare);
            if (filters.maxFare) params.append('maxFare', filters.maxFare);
            if (filters.limit) params.append('limit', filters.limit);
            if (filters.offset) params.append('offset', filters.offset);

            const response = await axios.get(`${API_BASE_URL}/trips?${params}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching trips:', error);
            throw error;
        }
    },

    // Get all zones
    async getZones() {
        try {
            const response = await axios.get(`${API_BASE_URL}/zones`);
            return response.data;
        } catch (error) {
            console.error('Error fetching zones:', error);
            throw error;
        }
    },

    // Get hourly demand pattern
    async getHourlyDemand() {
        try {
            const response = await axios.get(`${API_BASE_URL}/insights/hourly-demand`);
            return response.data;
        } catch (error) {
            console.error('Error fetching hourly demand:', error);
            throw error;
        }
    },

    // Get borough statistics
    async getBoroughStats() {
        try {
            const response = await axios.get(`${API_BASE_URL}/insights/borough-stats`);
            return response.data;
        } catch (error) {
            console.error('Error fetching borough stats:', error);
            throw error;
        }
    },

    // Get payment distribution
    async getPaymentDistribution() {
        try {
            const response = await axios.get(`${API_BASE_URL}/insights/payment-distribution`);
            return response.data;
        } catch (error) {
            console.error('Error fetching payment distribution:', error);
            throw error;
        }
    },

    // Get speed by hour
    async getSpeedByHour() {
        try {
            const response = await axios.get(`${API_BASE_URL}/insights/speed-by-hour`);
            return response.data;
        } catch (error) {
            console.error('Error fetching speed by hour:', error);
            throw error;
        }
    },

    // Get top routes
    async getTopRoutes(limit = 10) {
        try {
            const response = await axios.get(`${API_BASE_URL}/insights/top-routes?limit=${limit}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching top routes:', error);
            throw error;
        }
    },

    // Get summary statistics
    async getSummary() {
        try {
            const response = await axios.get(`${API_BASE_URL}/insights/summary`);
            return response.data;
        } catch (error) {
            console.error('Error fetching summary:', error);
            throw error;
        }
    },

    // Get weekend vs weekday comparison
    async getWeekendVsWeekday() {
        try {
            const response = await axios.get(`${API_BASE_URL}/insights/weekend-vs-weekday`);
            return response.data;
        } catch (error) {
            console.error('Error fetching weekend vs weekday:', error);
            throw error;
        }
    }
};
