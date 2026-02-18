/**
 * Chart Rendering Functions
 */

const charts = {
    instances: {},

    // Destroy existing chart if it exists
    destroyChart(chartId) {
        if (this.instances[chartId]) {
            this.instances[chartId].destroy();
        }
    },

    // Render hourly demand chart
    renderHourlyDemand(data) {
        this.destroyChart('hourlyDemand');
        
        const ctx = document.getElementById('hourly-demand-chart').getContext('2d');
        const hours = data.map(d => `${d.hour_of_day}:00`);
        const tripCounts = data.map(d => Number(d.trip_count));

        this.instances.hourlyDemand = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours,
                datasets: [{
                    label: 'Number of Trips',
                    data: tripCounts,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Trips: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    },

    // Render borough chart
    renderBoroughChart(data) {
        this.destroyChart('borough');
        
        const ctx = document.getElementById('borough-chart').getContext('2d');
        const boroughs = data.map(d => d.borough);
        const tripCounts = data.map(d => Number(d.trip_count));

        this.instances.borough = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: boroughs,
                datasets: [{
                    label: 'Number of Trips',
                    data: tripCounts,
                    backgroundColor: [
                        '#2563eb',
                        '#7c3aed',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    },


    // Render payment distribution chart
    renderPaymentChart(data) {
        this.destroyChart('payment');
        
        const ctx = document.getElementById('payment-chart').getContext('2d');
        const paymentTypes = data.map(d => d.paymentType);
        const counts = data.map(d => d.count);

        this.instances.payment = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: paymentTypes,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        '#2563eb',
                        '#7c3aed',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#6b7280'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    },

    // Render speed by hour chart
    renderSpeedChart(data) {
        this.destroyChart('speed');
        
        const ctx = document.getElementById('speed-chart').getContext('2d');
        const hours = data.map(d => `${d.hour_of_day}:00`);
        const speeds = data.map(d => Number(d.avg_speed));

        this.instances.speed = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours,
                datasets: [{
                    label: 'Average Speed (mph)',
                    data: speeds,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Speed (mph)'
                        }
                    }
                }
            }
        });
    },

    // Render top routes chart
    renderRoutesChart(data) {
        this.destroyChart('routes');
        
        const ctx = document.getElementById('routes-chart').getContext('2d');
        const routes = data.map(d => `${d.pickup_zone} → ${d.dropoff_zone}`);
        const tripCounts = data.map(d => Number(d.trip_count));

        this.instances.routes = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: routes,
                datasets: [{
                    label: 'Number of Trips',
                    data: tripCounts,
                    backgroundColor: '#7c3aed'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
};
