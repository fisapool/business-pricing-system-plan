import pandas as pd
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import base64
from io import BytesIO

class DashboardGenerator:
    def __init__(self, data_dir, output_dir):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_dashboard(self):
        """Generate the complete dashboard"""
        # Create dashboard directory structure
        (self.output_dir / 'js').mkdir(exist_ok=True)
        (self.output_dir / 'css').mkdir(exist_ok=True)
        (self.output_dir / 'data').mkdir(exist_ok=True)
        
        # Generate the data files
        self._generate_price_history_data()
        self._generate_ab_test_data()
        self._generate_model_performance_data()
        self._generate_category_performance_data()
        
        # Create static HTML, CSS, and JS files
        self._create_html_files()
        self._create_css_files()
        self._create_js_files()
        
        print(f"Dashboard generated at {self.output_dir}")
        
    def _generate_price_history_data(self):
        """Create price history JSON data"""
        try:
            # Load price update history
            history_file = self.data_dir / "price_update_history.csv"
            if history_file.exists():
                df = pd.read_csv(history_file)
                df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
                
                # Group by date and card type
                daily_changes = df.groupby(['date', 'gift_card_type']).agg({
                    'change_percentage': ['mean', 'min', 'max', 'count']
                }).reset_index()
                
                # Flatten multi-index columns
                daily_changes.columns = ['date', 'gift_card_type', 'avg_change', 'min_change', 
                                        'max_change', 'num_changes']
                
                # Convert to JSON format suitable for charts
                json_data = daily_changes.to_dict(orient='records')
                
                # Write to output file
                with open(self.output_dir / 'data' / 'price_history.json', 'w') as f:
                    json.dump(json_data, f)
            else:
                print(f"Warning: {history_file} not found")
        except Exception as e:
            print(f"Error generating price history data: {str(e)}")
    
    def _generate_ab_test_data(self):
        """Create A/B test results JSON data"""
        try:
            # Load A/B test results
            ab_file = self.data_dir / "ab_test_results.csv"
            if ab_file.exists():
                df = pd.read_csv(ab_file)
                
                # Convert to json
                json_data = df.to_dict(orient='records')
                
                # Write to output file
                with open(self.output_dir / 'data' / 'ab_test_results.json', 'w') as f:
                    json.dump(json_data, f)
            else:
                print(f"Warning: {ab_file} not found")
        except Exception as e:
            print(f"Error generating A/B test data: {str(e)}")
    
    def _generate_model_performance_data(self):
        """Create model performance metrics JSON data"""
        try:
            # Load model performance data
            perf_file = self.data_dir / "model_performance.csv"
            if perf_file.exists():
                df = pd.read_csv(perf_file)
                
                # Convert to json
                json_data = df.to_dict(orient='records')
                
                # Write to output file
                with open(self.output_dir / 'data' / 'model_performance.json', 'w') as f:
                    json.dump(json_data, f)
            else:
                print(f"Warning: {perf_file} not found")
        except Exception as e:
            print(f"Error generating model performance data: {str(e)}")
    
    def _generate_category_performance_data(self):
        """Create category performance chart image"""
        try:
            # Load inventory data
            inventory_file = self.data_dir / "current_inventory.csv"
            if inventory_file.exists():
                df = pd.read_csv(inventory_file)
                
                # Group by category and calculate profit margin
                category_perf = df.groupby('gift_card_type').agg({
                    'current_price': 'mean',
                    'face_value': 'mean',
                    'profit_margin': 'mean',
                    'gift_card_id': 'count'
                }).reset_index()
                
                category_perf = category_perf.rename(columns={
                    'gift_card_id': 'count'
                })
                
                # Convert to JSON for bubble chart
                json_data = category_perf.to_dict(orient='records')
                
                # Write to output file
                with open(self.output_dir / 'data' / 'category_performance.json', 'w') as f:
                    json.dump(json_data, f)
            else:
                print(f"Warning: {inventory_file} not found")
        except Exception as e:
            print(f"Error generating category performance data: {str(e)}")
    
    def _create_html_files(self):
        """Create HTML files for the dashboard"""
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gift Card Pricing Dashboard</title>
    <link rel="stylesheet" href="css/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/moment@2.29.1/moment.min.js"></script>
</head>
<body>
    <header>
        <h1>Gift Card Pricing Optimization Dashboard</h1>
        <p>Last updated: <span id="last-updated"></span></p>
    </header>

    <nav>
        <ul>
            <li><a href="#" class="active" data-section="overview">Overview</a></li>
            <li><a href="#" data-section="price-history">Price History</a></li>
            <li><a href="#" data-section="ab-testing">A/B Testing</a></li>
            <li><a href="#" data-section="model-performance">Model Performance</a></li>
        </ul>
    </nav>

    <main>
        <section id="overview" class="dashboard-section active">
            <h2>System Overview</h2>
            <div class="cards-container">
                <div class="card">
                    <h3>Total Gift Cards</h3>
                    <p class="big-number" id="total-cards">-</p>
                </div>
                <div class="card">
                    <h3>Avg. Profit Margin</h3>
                    <p class="big-number" id="avg-margin">-</p>
                </div>
                <div class="card">
                    <h3>Price Changes (24h)</h3>
                    <p class="big-number" id="price-changes">-</p>
                </div>
                <div class="card">
                    <h3>ML Price Improvement</h3>
                    <p class="big-number" id="ml-improvement">-</p>
                </div>
            </div>
            
            <div class="charts-container">
                <div class="chart-card">
                    <h3>Category Performance</h3>
                    <div class="chart-container">
                        <canvas id="category-chart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Recent Price Adjustments</h3>
                    <div class="chart-container">
                        <canvas id="adjustments-chart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <section id="price-history" class="dashboard-section">
            <h2>Price History</h2>
            <div class="filter-container">
                <select id="card-type-filter">
                    <option value="all">All Card Types</option>
                </select>
                <select id="time-period-filter">
                    <option value="7">Last 7 days</option>
                    <option value="30">Last 30 days</option>
                    <option value="90">Last 90 days</option>
                </select>
            </div>
            <div class="chart-container full-width">
                <canvas id="price-history-chart"></canvas>
            </div>
            <div class="table-container">
                <h3>Recent Price Changes</h3>
                <table id="price-changes-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Gift Card</th>
                            <th>Old Price</th>
                            <th>New Price</th>
                            <th>Change %</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Will be populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </section>

        <section id="ab-testing" class="dashboard-section">
            <h2>A/B Testing Results</h2>
            <div class="charts-container">
                <div class="chart-card">
                    <h3>Control vs Test Group</h3>
                    <div class="chart-container">
                        <canvas id="ab-comparison-chart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Conversion Rate</h3>
                    <div class="chart-container">
                        <canvas id="conversion-chart"></canvas>
                    </div>
                </div>
            </div>
            <div class="ab-stats-container">
                <div class="ab-stat">
                    <h4>Revenue Lift</h4>
                    <p id="revenue-lift">-</p>
                </div>
                <div class="ab-stat">
                    <h4>Profit Lift</h4>
                    <p id="profit-lift">-</p>
                </div>
                <div class="ab-stat">
                    <h4>Statistical Significance</h4>
                    <p id="significance">-</p>
                </div>
                <div class="ab-stat">
                    <h4>Sample Size</h4>
                    <p id="sample-size">-</p>
                </div>
            </div>
        </section>

        <section id="model-performance" class="dashboard-section">
            <h2>Model Performance</h2>
            <div class="charts-container">
                <div class="chart-card">
                    <h3>Model Error by Card Type</h3>
                    <div class="chart-container">
                        <canvas id="model-error-chart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Feature Importance</h3>
                    <div class="chart-container">
                        <canvas id="feature-importance-chart"></canvas>
                    </div>
                </div>
            </div>
            <div class="table-container">
                <h3>Model Metrics</h3>
                <table id="model-metrics-table">
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>MAE</th>
                            <th>RMSE</th>
                            <th>R²</th>
                            <th>Training Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Will be populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </section>
    </main>

    <footer>
        <p>Gift Card Pricing Optimization System &copy; 2023</p>
    </footer>

    <script src="js/dashboard.js"></script>
</body>
</html>"""

        with open(self.output_dir / 'index.html', 'w') as f:
            f.write(index_html)
    
    def _create_css_files(self):
        """Create CSS files for the dashboard"""
        css = """/* Dashboard Styles */
:root {
    --primary: #3f51b5;
    --primary-light: #757de8;
    --primary-dark: #002984;
    --secondary: #f50057;
    --text-light: #ffffff;
    --text-dark: #212121;
    --background-light: #f5f5f5;
    --card-background: #ffffff;
    --border-color: #e0e0e0;
    --success: #4caf50;
    --warning: #ff9800;
    --error: #f44336;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-dark);
    background-color: var(--background-light);
}

header {
    background: var(--primary);
    color: var(--text-light);
    padding: 1rem 2rem;
    text-align: center;
}

nav {
    background: var(--primary-dark);
    color: var(--text-light);
}

nav ul {
    display: flex;
    list-style: none;
    justify-content: center;
    padding: 0.5rem 1rem;
}

nav a {
    color: var(--text-light);
    text-decoration: none;
    padding: 0.5rem 1rem;
    display: block;
    border-radius: 4px;
}

nav a:hover {
    background: rgba(255, 255, 255, 0.1);
}

nav a.active {
    background: var(--primary-light);
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.dashboard-section {
    display: none;
}

.dashboard-section.active {
    display: block;
}

.cards-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.card {
    background: var(--card-background);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    text-align: center;
}

.big-number {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary);
    margin-top: 0.5rem;
}

.charts-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.chart-card {
    background: var(--card-background);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
}

.chart-container {
    position: relative;
    height: 300px;
    width: 100%;
}

.chart-container.full-width {
    height: 400px;
}

.filter-container {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-bottom: 1rem;
}

select {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.table-container {
    background: var(--card-background);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    margin-bottom: 2rem;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

th {
    background-color: var(--background-light);
    font-weight: bold;
}

tr:hover {
    background-color: rgba(0, 0, 0, 0.02);
}

.ab-stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.ab-stat {
    background: var(--card-background);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    text-align: center;
}

.ab-stat p {
    font-size: 1.75rem;
    font-weight: bold;
    color: var(--primary);
    margin-top: 0.5rem;
}

footer {
    background: var(--primary-dark);
    color: var(--text-light);
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}

h2 {
    margin-bottom: 1.5rem;
    color: var(--primary-dark);
}

h3 {
    margin-bottom: 1rem;
    color: var(--primary);
}

@media (max-width: 768px) {
    .charts-container {
        grid-template-columns: 1fr;
    }
    
    nav ul {
        flex-direction: column;
    }
    
    nav a {
        text-align: center;
    }
}"""

        with open(self.output_dir / 'css' / 'styles.css', 'w') as f:
            f.write(css)
    
    def _create_js_files(self):
        """Create JavaScript files for the dashboard"""
        js = """// Dashboard initialization
document.addEventListener('DOMContentLoaded', function() {
    // Set last updated time
    document.getElementById('last-updated').textContent = new Date().toLocaleString();
    
    // Navigation handling
    const navLinks = document.querySelectorAll('nav a');
    const sections = document.querySelectorAll('.dashboard-section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding section
            const sectionId = this.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Load dashboard data
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        // Load all data files
        const priceHistoryData = await fetchJson('data/price_history.json');
        const abTestData = await fetchJson('data/ab_test_results.json');
        const modelPerformanceData = await fetchJson('data/model_performance.json');
        const categoryPerformanceData = await fetchJson('data/category_performance.json');
        
        // Initialize dashboard components
        initializeOverviewCards(priceHistoryData, abTestData, categoryPerformanceData);
        initializeCategoryChart(categoryPerformanceData);
        initializeAdjustmentsChart(priceHistoryData);
        initializePriceHistoryChart(priceHistoryData);
        initializeAbTestingCharts(abTestData);
        initializeModelPerformanceCharts(modelPerformanceData);
        
        // Populate tables
        populatePriceChangesTable(priceHistoryData);
        populateModelMetricsTable(modelPerformanceData);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

function initializeOverviewCards(priceHistoryData, abTestData, categoryPerformanceData) {
    // Total cards
    const totalCards = categoryPerformanceData.reduce((sum, item) => sum + item.count, 0);
    document.getElementById('total-cards').textContent = totalCards;
    
    // Average profit margin
    const avgMargin = categoryPerformanceData.reduce((sum, item) => sum + (item.profit_margin * item.count), 0) / totalCards;
    document.getElementById('avg-margin').textContent = avgMargin.toFixed(2) + '%';
    
    // Price changes in last 24h
    const today = new Date().toISOString().split('T')[0];
    const recentChanges = priceHistoryData.filter(item => item.date === today);
    const totalChanges = recentChanges.reduce((sum, item) => sum + item.num_changes, 0);
    document.getElementById('price-changes').textContent = totalChanges;
    
    // ML improvement
    if (abTestData && abTestData.length > 0) {
        const latestTest = abTestData[abTestData.length - 1];
        document.getElementById('ml-improvement').textContent = latestTest.lift_percentage.toFixed(2) + '%';
    }
}

function initializeCategoryChart(data) {
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    // Prepare data for bubble chart
    const chartData = {
        datasets: [{
            label: 'Gift Card Categories',
            data: data.map(item => ({
                x: item.face_value,
                y: item.profit_margin,
                r: Math.sqrt(item.count) * 3  // Size based on count
            })),
            backgroundColor: getRandomColors(data.length, 0.7)
        }]
    };
    
    new Chart(ctx, {
        type: 'bubble',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Face Value ($)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Profit Margin (%)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = data[context.dataIndex];
                            return [
                                `Category: ${item.gift_card_type}`,
                                `Face Value: $${item.face_value.toFixed(2)}`,
                                `Profit Margin: ${item.profit_margin.toFixed(2)}%`,
                                `Count: ${item.count}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

function initializeAdjustmentsChart(data) {
    const ctx = document.getElementById('adjustments-chart').getContext('2d');
    
    // Get recent dates (last 7 days)
    const dates = [...new Set(data.map(item => item.date))].sort().slice(-7);
    
    // Aggregate data by date
    const aggregatedData = dates.map(date => {
        const dayData = data.filter(item => item.date === date);
        return {
            date: date,
            avg_change: dayData.reduce((sum, item) => sum + (item.avg_change * item.num_changes), 0) / 
                        dayData.reduce((sum, item) => sum + item.num_changes, 0),
            num_changes: dayData.reduce((sum, item) => sum + item.num_changes, 0)
        };
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: aggregatedData.map(item => formatDate(item.date)),
            datasets: [
                {
                    label: 'Average Change (%)',
                    data: aggregatedData.map(item => item.avg_change),
                    backgroundColor: 'rgba(63, 81, 181, 0.7)',
                    borderColor: 'rgba(63, 81, 181, 1)',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Number of Changes',
                    data: aggregatedData.map(item => item.num_changes),
                    backgroundColor: 'rgba(245, 0, 87, 0.7)',
                    borderColor: 'rgba(245, 0, 87, 1)',
                    borderWidth: 1,
                    type: 'line',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Average Change (%)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Number of Changes'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

function initializePriceHistoryChart(data) {
    const ctx = document.getElementById('price-history-chart').getContext('2d');
    
    // Get all gift card types
    const cardTypes = [...new Set(data.map(item => item.gift_card_type))];
    
    // Populate filter
    const filterSelect = document.getElementById('card-type-filter');
    cardTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        filterSelect.appendChild(option);
    });
    
    // Get recent dates (last 30 days by default)
    const dates = [...new Set(data.map(item => item.date))].sort().slice(-30);
    
    // Create datasets for each card type
    const datasets = cardTypes.map((type, index) => {
        const typeData = data.filter(item => item.gift_card_type === type);
        
        return {
            label: type,
            data: dates.map(date => {
                const dayData = typeData.find(item => item.date === date);
                return dayData ? dayData.avg_change : null;
            }),
            borderColor: getColor(index, 1),
            backgroundColor: getColor(index, 0.1),
            tension: 0.4
        };
    });
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates.map(date => formatDate(date)),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Price Change (%)'
                    }
                }
            }
        }
    });
    
    // Filter handling
    filterSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        
        if (selectedValue === 'all') {
            chart.data.datasets = datasets;
        } else {
            chart.data.datasets = datasets.filter(ds => ds.label === selectedValue);
        }
        
        chart.update();
    });
    
    // Time period filter
    document.getElementById('time-period-filter').addEventListener('change', function() {
        const days = parseInt(this.value);
        const filteredDates = [...new Set(data.map(item => item.date))].sort().slice(-days);
        
        chart.data.labels = filteredDates.map(date => formatDate(date));
        
        chart.data.datasets.forEach(dataset => {
            const type = dataset.label;
            const typeData = data.filter(item => item.gift_card_type === type);
            
            dataset.data = filteredDates.map(date => {
                const dayData = typeData.find(item => item.date === date);
                return dayData ? dayData.avg_change : null;
            });
        });
        
        chart.update();
    });
}

function initializeAbTestingCharts(data) {
    if (!data || data.length === 0) return;
    
    const latestTest = data[data.length - 1];
    
    // Set values in stats cards
    document.getElementById('revenue-lift').textContent = latestTest.revenue_lift.toFixed(2) + '%';
    document.getElementById('profit-lift').textContent = latestTest.profit_lift.toFixed(2) + '%';
    document.getElementById('significance').textContent = latestTest.p_value < 0.05 ? 'Significant' : 'Not significant';
    document.getElementById('sample-size').textContent = latestTest.control_count + latestTest.test_count;
    
    // A/B Comparison chart
    const comparisonCtx = document.getElementById('ab-comparison-chart').getContext('2d');
    new Chart(comparisonCtx, {
        type: 'bar',
        data: {
            labels: ['Revenue', 'Profit', 'Conversion Rate'],
            datasets: [
                {
                    label: 'Control Group',
                    data: [
                        latestTest.control_revenue_per_user,
                        latestTest.control_profit_per_user,
                        latestTest.control_conversion_rate
                    ],
                    backgroundColor: 'rgba(63, 81, 181, 0.7)'
                },
                {
                    label: 'Test Group',
                    data: [
                        latestTest.test_revenue_per_user,
                        latestTest.test_profit_per_user,
                        latestTest.test_conversion_rate
                    ],
                    backgroundColor: 'rgba(245, 0, 87, 0.7)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // Conversion Rate chart
    const conversionCtx = document.getElementById('conversion-chart').getContext('2d');
    
    // Assume we have multiple data points for conversion rate over time
    const dates = data.map(item => item.date);
    new Chart(conversionCtx, {
        type: 'line',
        data: {
            labels: dates.map(date => formatDate(date)),
            datasets: [
                {
                    label: 'Control Group',
                    data: data.map(item => item.control_conversion_rate),
                    borderColor: 'rgba(63, 81, 181, 1)',
                    backgroundColor: 'rgba(63, 81, 181, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Test Group',
                    data: data.map(item => item.test_conversion_rate),
                    borderColor: 'rgba(245, 0, 87, 1)',
                    backgroundColor: 'rgba(245, 0, 87, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function initializeModelPerformanceCharts(data) {
    if (!data || data.length === 0) return;
    
    // Model Error chart
    const errorCtx = document.getElementById('model-error-chart').getContext('2d');
    new Chart(errorCtx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.model_name),
            datasets: [
                {
                    label: 'MAE',
                    data: data.map(item => item.mae),
                    backgroundColor: 'rgba(63, 81, 181, 0.7)'
                },
                {
                    label: 'RMSE',
                    data: data.map(item => item.rmse),
                    backgroundColor: 'rgba(245, 0, 87, 0.7)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // Feature Importance chart
    const featuresCtx = document.getElementById('feature-importance-chart').getContext('2d');
    
    // Assume each model has feature_importance as an object with feature names and values
    const firstModel = data[0];
    if (firstModel.feature_importance) {
        const features = Object.keys(firstModel.feature_importance);
        const importances = Object.values(firstModel.feature_importance);
        
        new Chart(featuresCtx, {
            type: 'horizontalBar',
            data: {
                labels: features,
                datasets: [{
                    label: 'Feature Importance',
                    data: importances,
                    backgroundColor: getRandomColors(features.length, 0.7)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Importance'
                        }
                    }
                }
            }
        });
    }
}

function populatePriceChangesTable(data) {
    // Flatten the data to get individual card changes
    // This assumes you have more detailed data available
    const tableBody = document.getElementById('price-changes-table').querySelector('tbody');
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add sample rows
    for (let i = 0; i < 10; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>2023-04-${10 + i}</td>
            <td>Netflix $50</td>
            <td>$47.99</td>
            <td>$48.99</td>
            <td>+2.08%</td>
        `;
        tableBody.appendChild(row);
    }
}

function populateModelMetricsTable(data) {
    const tableBody = document.getElementById('model-metrics-table').querySelector('tbody');
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add rows for each model
    data.forEach(model => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${model.model_name}</td>
            <td>${model.mae.toFixed(4)}</td>
            <td>${model.rmse.toFixed(4)}</td>
            <td>${model.r_squared.toFixed(4)}</td>
            <td>${model.training_time.toFixed(2)}s</td>
        `;
        tableBody.appendChild(row);
    });
}

// Helper functions
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function getColor(index, alpha) {
    const colors = [
        `rgba(63, 81, 181, ${alpha})`,   // Primary
        `rgba(245, 0, 87, ${alpha})`,    // Secondary
        `rgba(76, 175, 80, ${alpha})`,   // Success
        `rgba(255, 152, 0, ${alpha})`,   // Warning
        `rgba(33, 150, 243, ${alpha})`,  // Info
        `rgba(156, 39, 176, ${alpha})`,  // Purple
        `rgba(0, 188, 212, ${alpha})`,   // Cyan
        `rgba(255, 87, 34, ${alpha})`,   // Deep Orange
        `rgba(121, 85, 72, ${alpha})`,   // Brown
        `rgba(96, 125, 139, ${alpha})`   // Blue Grey
    ];
    
    return colors[index % colors.length];
}

function getRandomColors(count, alpha) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(getColor(i, alpha));
    }
    return colors;
}"""

        with open(self.output_dir / 'js' / 'dashboard.js', 'w') as f:
            f.write(js) 