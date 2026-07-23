/**
 * SupportSight - Chart Configurations
 */

// Default chart options
const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                usePointStyle: true,
                padding: 20,
                font: {
                    family: "'Inter', sans-serif",
                    size: 12
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleFont: {
                family: "'Inter', sans-serif",
                size: 13
            },
            bodyFont: {
                family: "'Inter', sans-serif",
                size: 12
            },
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
            boxPadding: 4
        }
    },
    scales: {
        x: {
            grid: {
                display: false
            },
            ticks: {
                font: {
                    family: "'Inter', sans-serif",
                    size: 11
                },
                color: '#6c757d'
            }
        },
        y: {
            grid: {
                color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
                font: {
                    family: "'Inter', sans-serif",
                    size: 11
                },
                color: '#6c757d'
            }
        }
    },
    animation: {
        duration: 500,
        easing: 'easeOutQuart'
    }
};

// Line chart for performance
function createPerformanceChart(ctx, data, options = {}) {
    const colors = getChartColors();

    const config = {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [
                {
                    label: 'CPU',
                    data: data.cpu || [],
                    borderColor: colors.primary,
                    backgroundColor: `${colors.primary}15`,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    borderWidth: 2
                },
                {
                    label: 'Memory',
                    data: data.memory || [],
                    borderColor: colors.success,
                    backgroundColor: `${colors.success}15`,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    borderWidth: 2
                }
            ]
        },
        options: {
            ...defaultChartOptions,
            scales: {
                ...defaultChartOptions.scales,
                y: {
                    ...defaultChartOptions.scales.y,
                    min: 0,
                    max: 100,
                    ticks: {
                        ...defaultChartOptions.scales.y.ticks,
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    };

    return new Chart(ctx, config);
}

// Doughnut chart for disk usage
function createDiskUsageChart(ctx, used, free, options = {}) {
    const colors = getChartColors();

    const config = {
        type: 'doughnut',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [used, free],
                backgroundColor: [
                    colors.warning,
                    `${colors.success}40`
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    }
                },
                tooltip: {
                    ...defaultChartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${formatBytes(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    };

    return new Chart(ctx, config);
}

// Bar chart for component comparison
function createComponentComparisonChart(ctx, labels, values, options = {}) {
    const colors = getChartColors();

    const getColor = (value) => {
        if (value >= 90) return colors.danger;
        if (value >= 70) return colors.warning;
        return colors.success;
    };

    const config = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Usage %',
                data: values,
                backgroundColor: values.map(v => getColor(v)),
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            ...defaultChartOptions,
            indexAxis: 'y',
            scales: {
                x: {
                    ...defaultChartOptions.scales.x,
                    min: 0,
                    max: 100,
                    ticks: {
                        ...defaultChartOptions.scales.x.ticks,
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                y: {
                    ...defaultChartOptions.scales.y,
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...defaultChartOptions.plugins,
                legend: {
                    display: false
                }
            }
        }
    };

    return new Chart(ctx, config);
}

// Radar chart for health overview
function createHealthRadarChart(ctx, scores, options = {}) {
    const colors = getChartColors();

    const config = {
        type: 'radar',
        data: {
            labels: scores.map(s => s.name),
            datasets: [{
                label: 'Health Score',
                data: scores.map(s => s.score),
                backgroundColor: `${colors.primary}30`,
                borderColor: colors.primary,
                borderWidth: 2,
                pointBackgroundColor: colors.primary,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: colors.primary,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    beginAtZero: true,
                    ticks: {
                        stepSize: 20,
                        backdropColor: 'transparent',
                        font: {
                            size: 10
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    pointLabels: {
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12,
                            weight: '500'
                        },
                        color: '#1a1a2e'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    ...defaultChartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.raw}/100`;
                        }
                    }
                }
            }
        }
    };

    return new Chart(ctx, config);
}

// Gauge chart for single value display
function createGaugeChart(ctx, value, options = {}) {
    const colors = getChartColors();
    const maxValue = options.maxValue || 100;
    const label = options.label || '';

    const getColor = (v) => {
        const percentage = (v / maxValue) * 100;
        if (percentage >= 90) return colors.danger;
        if (percentage >= 70) return colors.warning;
        return colors.success;
    };

    const config = {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, maxValue - value],
                backgroundColor: [
                    getColor(value),
                    'rgba(0, 0, 0, 0.05)'
                ],
                borderWidth: 0,
                circumference: 270,
                rotation: 225
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    };

    return new Chart(ctx, config);
}

// Network latency chart
function createLatencyChart(ctx, data, options = {}) {
    const colors = getChartColors();

    const config = {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Latency (ms)',
                data: data.latency || [],
                borderColor: colors.purple,
                backgroundColor: `${colors.purple}15`,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                borderWidth: 2
            }]
        },
        options: {
            ...defaultChartOptions,
            scales: {
                ...defaultChartOptions.scales,
                y: {
                    ...defaultChartOptions.scales.y,
                    beginAtZero: true,
                    ticks: {
                        ...defaultChartOptions.scales.y.ticks,
                        callback: function(value) {
                            return value + 'ms';
                        }
                    }
                }
            }
        }
    };

    return new Chart(ctx, config);
}

// Update existing chart with new data
function updateChartData(chart, newData, newLabels = null) {
    if (newLabels) {
        chart.data.labels = newLabels;
    }

    chart.data.datasets.forEach((dataset, index) => {
        if (newData[index]) {
            dataset.data = newData[index];
        }
    });

    chart.update('none');
}

// Destroy chart instance
function destroyChart(chart) {
    if (chart) {
        chart.destroy();
    }
}

// Export functions
window.SupportSightCharts = {
    createPerformanceChart,
    createDiskUsageChart,
    createComponentComparisonChart,
    createHealthRadarChart,
    createGaugeChart,
    createLatencyChart,
    updateChartData,
    destroyChart,
    defaultChartOptions
};
