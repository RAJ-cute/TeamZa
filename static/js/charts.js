/* Chart.js configurations and utilities for HR Platform */

// Chart.js default configurations
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 15;

// HR Platform chart utilities
const HRCharts = {
    colors: {
        primary: '#007bff',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8',
        secondary: '#6c757d',
        light: '#f8f9fa',
        dark: '#343a40'
    },
    
    gradients: {},
    
    // Initialize chart utilities
    init: function() {
        this.setupResponsiveDefaults();
        this.createGradients();
    },
    
    // Setup responsive defaults
    setupResponsiveDefaults: function() {
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.plugins.legend.position = 'bottom';
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        Chart.defaults.plugins.tooltip.titleColor = '#fff';
        Chart.defaults.plugins.tooltip.bodyColor = '#fff';
        Chart.defaults.plugins.tooltip.cornerRadius = 6;
    },
    
    // Create gradient backgrounds
    createGradients: function() {
        // This would be called when creating charts with canvas context
    },
    
    // Get color palette
    getColorPalette: function(count = 6) {
        const baseColors = Object.values(this.colors);
        const colors = [];
        
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        
        return colors;
    },
    
    // Create gradient background
    createGradient: function(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },
    
    // Performance chart configuration
    performanceChart: function(ctx, data) {
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Performance Score',
                    data: data.values,
                    borderColor: this.colors.primary,
                    backgroundColor: this.createGradient(ctx, 
                        this.colors.primary + '40', 
                        this.colors.primary + '10'
                    ),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Performance: ${context.parsed.y}/10`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    },
    
    // Department distribution pie chart
    departmentChart: function(ctx, data) {
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: this.getColorPalette(Object.keys(data).length),
                    borderWidth: 2,
                    borderColor: '#fff',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((context.parsed / total) * 100);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '50%'
            }
        });
    },
    
    // Wellness status bar chart
    wellnessChart: function(ctx, data) {
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Excellent', 'Good', 'Needs Attention'],
                datasets: [{
                    data: [data.green || 0, data.yellow || 0, data.red || 0],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.warning,
                        this.colors.danger
                    ],
                    borderWidth: 1,
                    borderColor: '#fff',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.parsed.y} employees`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    },
    
    // Attrition trends line chart
    attritionChart: function(ctx, data) {
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.month),
                datasets: [{
                    label: 'Attrition Rate',
                    data: data.map(d => d.rate),
                    borderColor: this.colors.danger,
                    backgroundColor: this.colors.danger + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.danger,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Attrition Rate: ${context.parsed.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    },
    
    // Skills radar chart
    skillsRadarChart: function(ctx, data) {
        return new Chart(ctx, {
            type: 'radar',
            data: {
                labels: data.skills,
                datasets: [{
                    label: 'Current Level',
                    data: data.current,
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '40',
                    borderWidth: 2,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }, {
                    label: 'Required Level',
                    data: data.required,
                    borderColor: this.colors.success,
                    backgroundColor: this.colors.success + '20',
                    borderWidth: 2,
                    pointBackgroundColor: this.colors.success,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            stepSize: 2
                        }
                    }
                }
            }
        });
    },
    
    // Learning progress chart
    learningProgressChart: function(ctx, data) {
        return new Chart(ctx, {
            type: 'horizontalBar',
            data: {
                labels: data.modules,
                datasets: [{
                    label: 'Completion %',
                    data: data.progress,
                    backgroundColor: data.progress.map(p => 
                        p >= 80 ? this.colors.success :
                        p >= 60 ? this.colors.info :
                        p >= 40 ? this.colors.warning :
                        this.colors.danger
                    ),
                    borderWidth: 1,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Progress: ${context.parsed.x}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    },
    
    // Sentiment analysis chart
    sentimentChart: function(ctx, data) {
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [data.positive, data.neutral, data.negative],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.warning,
                        this.colors.danger
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((context.parsed / total) * 100);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '40%'
            }
        });
    },
    
    // Create animated counter
    animateCounter: function(element, start, end, duration = 2000) {
        const range = end - start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(duration / range));
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            element.textContent = current;
            
            if (current === end) {
                clearInterval(timer);
            }
        }, stepTime);
    },
    
    // Update chart data
    updateChart: function(chart, newData) {
        chart.data = newData;
        chart.update('active');
    },
    
    // Destroy chart safely
    destroyChart: function(chart) {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    }
};

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    HRCharts.init();
    
    // Initialize any charts present on the page
    initializePageCharts();
});

/**
 * Initialize charts based on current page
 */
function initializePageCharts() {
    const currentPath = window.location.pathname;
    
    // Performance dashboard charts
    if (currentPath === '/appraisal-dashboard') {
        initializeAppraisalCharts();
    }
    
    // HR insights charts
    if (currentPath === '/hr-insights') {
        initializeInsightsCharts();
    }
    
    // Learning module charts
    if (currentPath === '/learning-module') {
        initializeLearningCharts();
    }
    
    // Leadership potential charts
    if (currentPath === '/leadership-potential') {
        initializeLeadershipCharts();
    }
}

/**
 * Initialize appraisal dashboard charts
 */
function initializeAppraisalCharts() {
    // Sentiment chart
    const sentimentCtx = document.getElementById('sentimentChart');
    if (sentimentCtx && window.sentimentData) {
        HRCharts.sentimentChart(sentimentCtx.getContext('2d'), window.sentimentData);
    }
    
    // Performance ratings chart
    const ratingsCtx = document.getElementById('ratingsChart');
    if (ratingsCtx && window.ratingsData) {
        HRCharts.performanceChart(ratingsCtx.getContext('2d'), window.ratingsData);
    }
}

/**
 * Initialize HR insights charts
 */
function initializeInsightsCharts() {
    // Department distribution
    const deptCtx = document.getElementById('departmentChart');
    if (deptCtx && window.departmentData) {
        createDepartmentChart(deptCtx.getContext('2d'), window.departmentData);
    }
    
    // Performance distribution
    const perfCtx = document.getElementById('performanceChart');
    if (perfCtx && window.performanceData) {
        createPerformanceChart(perfCtx.getContext('2d'), window.performanceData);
    }
    
    // Monthly trends
    const trendsCtx = document.getElementById('trendsChart');
    if (trendsCtx && window.monthlyTrends) {
        createTrendsChart(trendsCtx.getContext('2d'), window.monthlyTrends);
    }
    
    // Wellness distribution
    const wellnessCtx = document.getElementById('wellnessChart');
    if (wellnessCtx && window.wellnessData) {
        createWellnessChart(wellnessCtx.getContext('2d'), window.wellnessData);
    }
}

/**
 * Create department distribution pie chart
 */
function createDepartmentChart(ctx, data) {
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#FF6384'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Create performance distribution chart
 */
function createPerformanceChart(ctx, data) {
    const distribution = data.distribution || {};
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Excellent', 'Good', 'Average', 'Needs Improvement'],
            datasets: [{
                label: 'Number of Employees',
                data: [
                    distribution.excellent || 0,
                    distribution.good || 0,
                    distribution.average || 0,
                    distribution.needs_improvement || 0
                ],
                backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

/**
 * Create monthly trends chart
 */
function createTrendsChart(ctx, data) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const incrementData = months.map((_, index) => data.increments ? (data.increments[index + 1] || 0) : 0);
    const joiningData = months.map((_, index) => data.joinings ? (data.joinings[index + 1] || 0) : 0);
    const exitData = months.map((_, index) => data.exits ? (data.exits[index + 1] || 0) : 0);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Increments',
                    data: incrementData,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Joinings',
                    data: joiningData,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Exits',
                    data: exitData,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Create wellness distribution chart
 */
function createWellnessChart(ctx, data) {
    const distribution = data.distribution || {};
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Good', 'Moderate', 'Concerning'],
            datasets: [{
                data: [
                    distribution.green || 0,
                    distribution.yellow || 0,
                    distribution.red || 0
                ],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Initialize learning module charts
 */
function initializeLearningCharts() {
    // Learning progress chart
    const progressCtx = document.getElementById('learningProgressChart');
    if (progressCtx && window.learningData) {
        HRCharts.learningProgressChart(progressCtx.getContext('2d'), window.learningData);
    }
}

/**
 * Initialize leadership potential charts
 */
function initializeLeadershipCharts() {
    // Leadership pipeline chart
    const pipelineCtx = document.getElementById('leadershipChart');
    if (pipelineCtx && window.leadershipData) {
        HRCharts.departmentChart(pipelineCtx.getContext('2d'), window.leadershipData);
    }
}

// Export HRCharts for global use
window.HRCharts = HRCharts;

// Utility functions for chart data processing
window.processChartData = function(rawData, type) {
    switch (type) {
        case 'performance':
            return {
                labels: rawData.map(d => d.period),
                values: rawData.map(d => d.score)
            };
        case 'department':
            return rawData.reduce((acc, item) => {
                acc[item.department] = (acc[item.department] || 0) + 1;
                return acc;
            }, {});
        case 'wellness':
            return {
                green: rawData.filter(d => d.status === 'green').length,
                yellow: rawData.filter(d => d.status === 'yellow').length,
                red: rawData.filter(d => d.status === 'red').length
            };
        default:
            return rawData;
    }
};
