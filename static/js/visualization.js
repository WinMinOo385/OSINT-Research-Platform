/**
 * OSINT Research Platform - Visualization JavaScript
 * Handles charts, graphs, and data visualization components
 */

// Global charts object to store chart instances
window.dashboardCharts = {};

// Visualization utilities
const VisualizationUtils = {
    // Color schemes
    colorSchemes: {
        primary: ['#1B263B', '#415A77', '#778DA9', '#E0E1DD'],
        confidence: ['#D62828', '#ffc107', '#28a745'],
        sources: ['#1B263B', '#415A77', '#778DA9', '#A3A9C1', '#E0E1DD', '#8B8D8F'],
        timeline: ['#778DA9', '#415A77']
    },

    // Get color by index
    getColor: function(scheme, index) {
        const colors = this.colorSchemes[scheme] || this.colorSchemes.primary;
        return colors[index % colors.length];
    },

    // Generate gradient
    createGradient: function(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },

    // Format chart data
    formatChartData: function(data, type = 'object') {
        if (type === 'array') {
            return Object.entries(data).map(([key, value]) => ({ x: key, y: value }));
        }
        return data;
    },

    // Get responsive chart options
    getResponsiveOptions: function() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#E0E1DD',
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: '#E0E1DD'
                    },
                    grid: {
                        color: '#2d3748'
                    }
                },
                x: {
                    ticks: {
                        color: '#E0E1DD'
                    },
                    grid: {
                        color: '#2d3748'
                    }
                }
            }
        };
    }
};

// Main visualization initialization function
function initializeCharts(data) {
    try {
        // Source distribution pie chart
        if (data.source_distribution && Object.keys(data.source_distribution).length > 0) {
            initializeSourceChart(data.source_distribution);
        }

        // Confidence levels chart
        if (data.confidence_data && data.confidence_data.length > 0) {
            initializeConfidenceChart(data.confidence_data);
        }

        // Timeline chart
        if (data.timeline_data && data.timeline_data.length > 0) {
            initializeTimelineChart(data.timeline_data);
        }

        console.log('Charts initialized successfully');
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

// Source distribution pie chart
function initializeSourceChart(sourceData) {
    const ctx = document.getElementById('sourceChart');
    if (!ctx) return;

    const labels = Object.keys(sourceData);
    const values = Object.values(sourceData);
    const colors = labels.map((_, index) => VisualizationUtils.getColor('sources', index));

    window.dashboardCharts.sourceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(label => label.charAt(0).toUpperCase() + label.slice(1)),
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: '#0D1B2A',
                borderWidth: 2,
                hoverBorderWidth: 3
            }]
        },
        options: {
            ...VisualizationUtils.getResponsiveOptions(),
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#E0E1DD',
                        font: {
                            family: 'Inter',
                            size: 12
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: '#1a2332',
                    titleColor: '#E0E1DD',
                    bodyColor: '#E0E1DD',
                    borderColor: '#415A77',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const percentage = ((context.parsed / values.reduce((a, b) => a + b, 0)) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Confidence levels chart
function initializeConfidenceChart(confidenceData) {
    const ctx = document.getElementById('confidenceChart');
    if (!ctx) return;

    // Group confidence data into ranges
    const ranges = {
        'High (70-100%)': 0,
        'Medium (40-69%)': 0,
        'Low (0-39%)': 0
    };

    confidenceData.forEach(item => {
        const confidence = item.confidence * 100;
        if (confidence >= 70) ranges['High (70-100%)']++;
        else if (confidence >= 40) ranges['Medium (40-69%)']++;
        else ranges['Low (0-39%)']++;
    });

    const labels = Object.keys(ranges);
    const values = Object.values(ranges);
    const colors = VisualizationUtils.colorSchemes.confidence;

    window.dashboardCharts.confidenceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Data Points',
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(color => color + 'CC'),
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            ...VisualizationUtils.getResponsiveOptions(),
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1a2332',
                    titleColor: '#E0E1DD',
                    bodyColor: '#E0E1DD',
                    borderColor: '#415A77',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: '#E0E1DD'
                    },
                    grid: {
                        color: '#2d3748'
                    }
                },
                x: {
                    ticks: {
                        color: '#E0E1DD'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Timeline chart using D3.js
function initializeTimelineChart(timelineData) {
    const container = document.getElementById('timelineChart');
    if (!container) return;

    // Clear previous content
    d3.select(container).selectAll('*').remove();

    // Set dimensions and margins
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Process data
    const parseDate = d3.timeParse('%Y-%m-%d');
    const processedData = d3.rollup(
        timelineData,
        v => v.length,
        d => d.date
    );

    const data = Array.from(processedData, ([date, count]) => ({
        date: parseDate(date),
        count: count
    })).sort((a, b) => a.date - b.date);

    if (data.length === 0) {
        g.append('text')
            .attr('x', width / 2)
            .attr('y', height / 2)
            .attr('text-anchor', 'middle')
            .attr('fill', '#718096')
            .text('No timeline data available');
        return;
    }

    // Set scales
    const xScale = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, width]);

    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count)])
        .nice()
        .range([height, 0]);

    // Create line generator
    const line = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScale(d.count))
        .curve(d3.curveMonotoneX);

    // Add axes
    g.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale)
            .tickFormat(d3.timeFormat('%m/%d')))
        .selectAll('text')
        .style('fill', '#E0E1DD');

    g.append('g')
        .call(d3.axisLeft(yScale).tickFormat(d3.format('d')))
        .selectAll('text')
        .style('fill', '#E0E1DD');

    // Style axis lines
    g.selectAll('.domain, .tick line')
        .style('stroke', '#2d3748');

    // Add area under the line
    const area = d3.area()
        .x(d => xScale(d.date))
        .y0(height)
        .y1(d => yScale(d.count))
        .curve(d3.curveMonotoneX);

    g.append('path')
        .datum(data)
        .attr('fill', 'url(#timelineGradient)')
        .attr('d', area);

    // Add gradient definition
    const defs = svg.append('defs');
    const gradient = defs.append('linearGradient')
        .attr('id', 'timelineGradient')
        .attr('gradientUnits', 'userSpaceOnUse')
        .attr('x1', 0).attr('y1', height)
        .attr('x2', 0).attr('y2', 0);

    gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#778DA9')
        .attr('stop-opacity', 0.1);

    gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#778DA9')
        .attr('stop-opacity', 0.8);

    // Add the line
    g.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#778DA9')
        .attr('stroke-width', 2)
        .attr('d', line);

    // Add dots
    g.selectAll('.dot')
        .data(data)
        .enter().append('circle')
        .attr('class', 'dot')
        .attr('cx', d => xScale(d.date))
        .attr('cy', d => yScale(d.count))
        .attr('r', 4)
        .attr('fill', '#415A77')
        .attr('stroke', '#778DA9')
        .attr('stroke-width', 2)
        .on('mouseover', function(event, d) {
            // Tooltip
            const tooltip = d3.select('body').append('div')
                .attr('class', 'timeline-tooltip')
                .style('position', 'absolute')
                .style('background', '#1a2332')
                .style('color', '#E0E1DD')
                .style('padding', '8px 12px')
                .style('border-radius', '4px')
                .style('border', '1px solid #415A77')
                .style('font-size', '12px')
                .style('pointer-events', 'none')
                .style('opacity', 0);

            tooltip.html(`Date: ${d3.timeFormat('%Y-%m-%d')(d.date)}<br>Collections: ${d.count}`)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .transition()
                .duration(200)
                .style('opacity', 1);

            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', 6);
        })
        .on('mouseout', function() {
            d3.selectAll('.timeline-tooltip').remove();
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', 4);
        });

    // Add labels
    g.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0 - margin.left)
        .attr('x', 0 - (height / 2))
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .style('fill', '#E0E1DD')
        .style('font-size', '12px')
        .text('Data Collections');

    g.append('text')
        .attr('transform', `translate(${width / 2}, ${height + margin.bottom})`)
        .style('text-anchor', 'middle')
        .style('fill', '#E0E1DD')
        .style('font-size', '12px')
        .text('Date');
}

// Network graph visualization (placeholder for advanced network analysis)
function initializeNetworkGraph(networkData) {
    const container = document.getElementById('networkChart');
    if (!container) return;

    // Clear previous content
    d3.select(container).selectAll('*').remove();

    if (!networkData || !networkData.nodes || networkData.nodes.length === 0) {
        d3.select(container)
            .append('div')
            .attr('class', 'text-center py-5')
            .html(`
                <i data-feather="share-2" class="text-muted mb-3" style="width: 48px; height: 48px;"></i>
                <p class="text-muted">Network visualization will be generated after analysis</p>
            `);
        feather.replace();
        return;
    }

    // Set dimensions
    const width = container.clientWidth;
    const height = 400;

    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Create simulation
    const simulation = d3.forceSimulation(networkData.nodes)
        .force('link', d3.forceLink(networkData.links).id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));

    // Add links
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(networkData.links)
        .enter().append('line')
        .attr('stroke', '#415A77')
        .attr('stroke-width', 2);

    // Add nodes
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('circle')
        .data(networkData.nodes)
        .enter().append('circle')
        .attr('r', 8)
        .attr('fill', d => d.type === 'domain' ? '#778DA9' : '#415A77')
        .attr('stroke', '#E0E1DD')
        .attr('stroke-width', 2)
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add labels
    const label = svg.append('g')
        .attr('class', 'labels')
        .selectAll('text')
        .data(networkData.nodes)
        .enter().append('text')
        .text(d => d.label)
        .attr('font-size', '10px')
        .attr('fill', '#E0E1DD')
        .attr('text-anchor', 'middle')
        .attr('dy', -12);

    // Update positions on simulation tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });

    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Dashboard charts for the main dashboard page
function initializeDashboardCharts() {
    // Initialize any dashboard-specific charts
    const activityChart = document.getElementById('activityChart');
    if (activityChart) {
        initializeActivityChart();
    }
}

// Activity chart for dashboard
function initializeActivityChart() {
    const ctx = document.getElementById('activityChart');
    if (!ctx) return;

    // Sample data - in real app this would come from API
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        last7Days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }

    window.dashboardCharts.activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: last7Days,
            datasets: [{
                label: 'Data Collections',
                data: [12, 19, 8, 15, 10, 22, 18], // Sample data
                borderColor: '#778DA9',
                backgroundColor: 'rgba(119, 141, 169, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            ...VisualizationUtils.getResponsiveOptions(),
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5,
                        color: '#E0E1DD'
                    },
                    grid: {
                        color: '#2d3748'
                    }
                },
                x: {
                    ticks: {
                        color: '#E0E1DD'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Resize all charts
function resizeCharts() {
    Object.values(window.dashboardCharts).forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
            chart.resize();
        }
    });

    // Resize D3 charts
    const timelineChart = document.getElementById('timelineChart');
    if (timelineChart && timelineChart.querySelector('svg')) {
        // Re-initialize timeline chart with new dimensions
        const data = window.currentTimelineData;
        if (data) {
            initializeTimelineChart(data);
        }
    }
}

// Export functions for global use
window.initializeCharts = initializeCharts;
window.initializeDashboardCharts = initializeDashboardCharts;
window.resizeCharts = resizeCharts;
window.VisualizationUtils = VisualizationUtils;

// Initialize dashboard charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboardCharts();
});
