// GeoH2 Frontend Application - India Focus
// Simplified version with India data and working visualizations

class GeoH2Frontend {
    constructor() {
        this.backendUrl = 'http://localhost:8000';
        this.currentData = null;
        this.map = null;
        this.hexagonLayer = null;
        this.selectedLocation = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.initMap();
        this.loadIndiaData();
        this.createVisualizations();
    }

    bindEvents() {
        // Map control event listeners
        document.getElementById('transport-type').addEventListener('change', () => {
            this.updateMapDisplay();
            this.updateAnalysisDisplay();
        });

        document.getElementById('cost-threshold').addEventListener('input', (e) => {
            document.getElementById('threshold-value').textContent = `${e.target.value} ₹/kg`;
            this.updateMapDisplay();
            this.updateAnalysisDisplay();
        });
    }

    initMap() {
        // Initialize Leaflet map centered on India
        this.map = L.map('factory-map').setView([23.5937, 78.9629], 5); // India center

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add India boundary highlight
        this.addIndiaBoundary();

        // Initialize hexagon layer
        this.hexagonLayer = L.geoJSON(null, {
            style: this.getHexagonStyle.bind(this),
            onEachFeature: this.onHexagonFeature.bind(this)
        }).addTo(this.map);

        // Add major cities as demand centers
        this.addDemandCenters();
    }

    addIndiaBoundary() {
        // Add a simple rectangle to highlight India
        const indiaBounds = [
            [6.0, 68.0],   // Southwest
            [37.0, 97.0]   // Northeast
        ];
        
        L.rectangle(indiaBounds, {
            color: "#6f42c1",
            weight: 2,
            fillOpacity: 0.1,
            fillColor: "#6f42c1"
        }).addTo(this.map).bindPopup("India - Analysis Region");
    }

    addDemandCenters() {
        // Major Indian cities as demand centers
        const demandCenters = [
            { name: "Mumbai", coords: [19.0760, 72.8777], type: "Port City" },
            { name: "Delhi", coords: [28.7041, 77.1025], type: "Capital" },
            { name: "Bangalore", coords: [12.9716, 77.5946], type: "Tech Hub" },
            { name: "Chennai", coords: [13.0827, 80.2707], type: "Port City" },
            { name: "Kolkata", coords: [22.5726, 88.3639], type: "Industrial" }
        ];

        demandCenters.forEach(center => {
            L.marker(center.coords, {
                icon: L.divIcon({
                    className: 'demand-center-marker',
                    html: '<i class="fas fa-building fa-2x" style="color: #6f42c1;"></i>',
                    iconSize: [40, 40],
                    iconAnchor: [20, 20]
                })
            }).addTo(this.map).bindPopup(`
                <div class="map-popup">
                    <h6>${center.name}</h6>
                    <p>${center.type} - Hydrogen Demand Center</p>
                    <div class="cost-info">
                        <strong>Target LCOH:</strong> < 300 ₹/kg
                    </div>
                </div>
            `);
        });
    }

    async loadIndiaData() {
        try {
            console.log('🔄 Loading real India data from API...');
            
            // Load real India data from our API
            const response = await fetch(`${this.backendUrl}/api/india/hexagons`);
            
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success') {
                    // Load real India data
                    const data = result.data.preview_hexagons;
                    this.currentData = data;
                    this.hexagonData = data;
                    this.updateMapDisplay();
                    this.updateAnalysisDisplay();
                    console.log('✅ Loaded real India data:', data.features.length, 'locations');
                    console.log('📊 LCOH range:', result.statistics['Mumbai pipeline LCOH'].min, '-', result.statistics['Mumbai pipeline LCOH'].max, '₹/kg');
                } else {
                    console.error('❌ Failed to load India data:', result.error);
                    this.loadSampleData();
                }
            } else {
                console.error('❌ Failed to load India data from API');
                this.loadSampleData();
            }
        } catch (error) {
            console.error('❌ Error loading India data:', error);
            // Fallback to sample data
            this.loadSampleData();
        }
    }

    async generateIndiaData() {
        try {
            console.log('Generating India data...');
            const response = await fetch(`${this.backendUrl}/api/generate-india`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success') {
                    // Reload the data
                    await this.loadIndiaData();
                } else {
                    console.error('Failed to generate India data:', result.errors);
                    this.loadSampleData();
                }
            } else {
                console.error('Failed to generate India data');
                this.loadSampleData();
            }
        } catch (error) {
            console.error('Error generating India data:', error);
            this.loadSampleData();
        }
    }

    loadSampleData() {
        // Fallback to sample data if real data is not available
        this.createSampleHexagons();
        this.updateMapDisplay();
        this.updateAnalysisDisplay();
    }

    createSampleHexagons() {
        // Create sample hexagon data covering India
        const hexagons = [];
        const indiaBounds = [
            [6.0, 68.0],   // Southwest
            [37.0, 97.0]   // Northeast
        ];

        // Create a grid of hexagons
        const latStep = 2;
        const lngStep = 2;

        for (let lat = indiaBounds[0][0]; lat <= indiaBounds[1][0]; lat += latStep) {
            for (let lng = indiaBounds[0][1]; lng <= indiaBounds[1][1]; lng += lngStep) {
                // Create hexagon geometry (simplified)
                const hexagon = {
                    type: "Feature",
                    geometry: {
                        type: "Polygon",
                        coordinates: [[
                            [lng, lat],
                            [lng + 0.5, lat + 0.3],
                            [lng + 0.5, lat + 0.7],
                            [lng, lat + 1],
                            [lng - 0.5, lat + 0.7],
                            [lng - 0.5, lat + 0.3],
                            [lng, lat]
                        ]]
                    },
                    properties: {
                        id: `hex_${lat}_${lng}`,
                        lat: lat,
                        lng: lng,
                        "Mumbai pipeline LCOH": this.generateSampleLCOH(lat, lng, "pipeline"),
                        "Mumbai trucking LCOH": this.generateSampleLCOH(lat, lng, "trucking"),
                        "Delhi pipeline LCOH": this.generateSampleLCOH(lat, lng, "pipeline"),
                        "Delhi trucking LCOH": this.generateSampleLCOH(lat, lng, "trucking"),
                        "Bangalore pipeline LCOH": this.generateSampleLCOH(lat, lng, "pipeline"),
                        "Bangalore trucking LCOH": this.generateSampleLCOH(lat, lng, "trucking")
                    }
                };
                hexagons.push(hexagon);
            }
        }

        this.hexagonData = {
            type: "FeatureCollection",
            features: hexagons
        };
    }

    generateSampleLCOH(lat, lng, transportType) {
        // Generate realistic LCOH values based on location and transport
        const baseCost = transportType === "pipeline" ? 200 : 350; // Pipeline cheaper
        const distanceFactor = Math.sqrt((lat - 20) ** 2 + (lng - 80) ** 2) * 10; // Distance from center
        const renewableFactor = Math.sin(lat * 0.1) * Math.cos(lng * 0.1) * 50; // Renewable potential
        const randomFactor = (Math.random() - 0.5) * 100; // Random variation
        
        return Math.max(100, Math.min(500, baseCost + distanceFactor + renewableFactor + randomFactor));
    }

    getHexagonStyle(feature) {
        if (!this.hexagonData) return {};

        const costThreshold = parseFloat(document.getElementById('cost-threshold').value);
        const transportType = document.getElementById('transport-type').value;
        
        // Get LCOH value for this hexagon from real India data
        let lcoh = 300; // Default value
        
        // Try to get LCOH from Mumbai (as default city) for the selected transport type
        const lcohColumn = `Mumbai ${transportType} LCOH`;
        if (feature.properties[lcohColumn]) {
            lcoh = feature.properties[lcohColumn];
        } else {
            // Fallback: try to find any LCOH value
            const lcohColumns = Object.keys(feature.properties).filter(key => key.includes('LCOH'));
            if (lcohColumns.length > 0) {
                lcoh = feature.properties[lcohColumns[0]];
            }
        }

        // Better color distribution based on LCOH values from real data
        let color = '#dc3545'; // Red - Unsuitable (high cost)
        
        // Green: Very low cost (≤ 200 ₹/kg) - Most Suitable
        if (lcoh <= 200) {
            color = '#28a745'; // Green - Most Suitable
        } 
        // Orange: Low to moderate cost (200-300 ₹/kg) - Mild Suitable
        else if (lcoh <= 300) {
            color = '#fd7e14'; // Orange - Mild Suitable
        }
        // Red: High cost (> 300 ₹/kg) - Unsuitable
        else {
            color = '#dc3545'; // Red - Unsuitable
        }

        return {
            fillColor: color,
            weight: 1,
            opacity: 1,
            color: 'white',
            fillOpacity: 0.8
        };
    }

    onHexagonFeature(feature, layer) {
        const transportType = document.getElementById('transport-type').value;
        const lcohColumn = `Mumbai ${transportType} LCOH`;
        const lcoh = feature.properties[lcohColumn] || 300;
        
        // Create popup content
        const popupContent = this.createHexagonPopup(feature, lcoh, transportType);
        layer.bindPopup(popupContent);

        // Add click event for factory location selection
        layer.on('click', () => {
            this.selectFactoryLocation(feature, lcoh);
        });
    }

    createHexagonPopup(feature) {
        // Use real India data if available, otherwise fallback to sample data
        const transportType = document.getElementById('transport-type').value;
        const lcohColumn = `Mumbai ${transportType} LCOH`;
        const lcoh = feature.properties[lcohColumn] || 300;
        
        // Calculate suitability based on LCOH
        const costThreshold = parseFloat(document.getElementById('cost-threshold').value);
        let suitabilityCategory = "Unsuitable";
        let isSuitable = false;
        
        if (lcoh <= costThreshold * 0.7) {
            suitabilityCategory = "Most Suitable";
            isSuitable = true;
        } else if (lcoh <= costThreshold) {
            suitabilityCategory = "Mild Suitable";
            isSuitable = true;
        }
        
        // Get location info
        const lat = feature.properties.lat || feature.geometry.coordinates[0][0][1];
        const lon = feature.properties.lon || feature.geometry.coordinates[0][0][0];
        
        return `
            <div class="map-popup">
                <h6>Location ${feature.properties.id || 'Unknown'}</h6>
                <div class="cost-info">
                    <strong>Coordinates:</strong> ${lat.toFixed(3)}, ${lon.toFixed(3)}
                </div>
                <div class="cost-info">
                    <strong>Mumbai ${transportType} LCOH:</strong> ${lcoh.toFixed(2)} ₹/kg
                </div>
                <div class="cost-info">
                    <strong>Suitability:</strong> ${suitabilityCategory}
                </div>
                <div class="cost-info">
                    <strong>Cost Threshold:</strong> ${costThreshold} ₹/kg
                </div>
                ${isSuitable ? '<div class="recommendation-badge">Good Location</div>' : ''}
                <p><small>Click to select as factory location</small></p>
            </div>
        `;
    }

    selectFactoryLocation(feature, lcoh) {
        // Highlight selected hexagon
        if (this.selectedLocation) {
            this.selectedLocation.setStyle({ weight: 1, color: 'white' });
        }
        
        feature.setStyle({ weight: 3, color: '#17a2b8' });
        this.selectedLocation = feature;

        // Show notification
        this.showNotification(`Factory location selected! LCOH: ${lcoh.toFixed(0)} ₹/kg`, 'success');
        
        // Update analysis display
        this.updateAnalysisDisplay();
    }

    updateMapDisplay() {
        if (!this.hexagonLayer || !this.hexagonData) {
            console.log('❌ No hexagon data available for display');
            return;
        }

        console.log('🔄 Updating map display with', this.hexagonData.features.length, 'hexagons');
        
        // Clear existing hexagons
        this.hexagonLayer.clearLayers();

        // Add hexagons with updated styling
        this.hexagonLayer.addData(this.hexagonData);
        
        console.log('✅ Map display updated successfully');
    }

    updateAnalysisDisplay() {
        // Update analysis display with real India data if available
        if (this.currentData && this.currentData.features && this.currentData.features.length > 0) {
            // Calculate real statistics from India data
            const transportType = document.getElementById('transport-type').value;
            const lcohColumn = `Mumbai ${transportType} LCOH`;
            
            // Extract LCOH values for the selected transport type
            const lcohValues = this.currentData.features
                .map(f => f.properties[lcohColumn])
                .filter(v => v && v > 0);
            
            if (lcohValues.length > 0) {
                const avgLCOH = (lcohValues.reduce((a, b) => a + b, 0) / lcohValues.length).toFixed(2);
                const minLCOH = Math.min(...lcohValues).toFixed(2);
                const maxLCOH = Math.max(...lcohValues).toFixed(2);
                
                // Update display based on transport type
                if (transportType === 'pipeline') {
                    document.getElementById('pipeline-avg').textContent = `${avgLCOH} ₹/kg`;
                    document.getElementById('pipeline-range').textContent = `${minLCOH}-${maxLCOH} ₹/kg`;
                } else {
                    document.getElementById('trucking-avg').textContent = `${avgLCOH} ₹/kg`;
                    document.getElementById('trucking-range').textContent = `${minLCOH}-${maxLCOH} ₹/kg`;
                }
                
                // Update summary information
                document.getElementById('summary-demand-centers').textContent = "5 Major Cities";
                document.getElementById('summary-locations').textContent = `${this.currentData.features.length} Locations`;
            } else {
                // Fallback to sample data
                this.updateAnalysisDisplayWithSampleData();
            }
        } else {
            // Fallback to sample data
            this.updateAnalysisDisplayWithSampleData();
        }
    }

    updateAnalysisDisplayWithSampleData() {
        // Update cost comparison with sample data
        const pipelineAvg = 250;
        const truckingAvg = 380;
        const pipelineRange = "200-300";
        const truckingRange = "320-450";

        document.getElementById('pipeline-avg').textContent = `${pipelineAvg} ₹/kg`;
        document.getElementById('pipeline-range').textContent = `${pipelineRange} ₹/kg`;
        document.getElementById('trucking-avg').textContent = `${truckingAvg} ₹/kg`;
        document.getElementById('trucking-range').textContent = `${truckingRange} ₹/kg`;

        // Calculate and display cost savings
        const savings = truckingAvg - pipelineAvg;
        const savingsPercent = (savings / truckingAvg * 100).toFixed(1);
        
        document.getElementById('cost-savings').textContent = `${savings} ₹/kg (${savingsPercent}%)`;

        // Update summary information
        document.getElementById('summary-demand-centers').textContent = "5 Major Cities";
        document.getElementById('summary-locations').textContent = "100+ Locations";
    }

    createVisualizations() {
        const chartGallery = document.getElementById('chart-gallery');
        chartGallery.innerHTML = '';

        // Create sample charts
        this.createCostComparisonChart(chartGallery);
        this.createTransportCostChart(chartGallery);
        this.createLocationSuitabilityChart(chartGallery);
        this.createRenewablePotentialChart(chartGallery);
        this.createInfrastructureChart(chartGallery);
    }

    createCostComparisonChart(container) {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'col-lg-6 col-xl-4 mb-4';
        
        chartDiv.innerHTML = `
            <div class="chart-container">
                <h6 class="chart-title">Cost Comparison by Transport</h6>
                <p class="chart-description">Pipeline vs Trucking costs across India</p>
                <canvas id="costComparisonChart" width="400" height="300"></canvas>
            </div>
        `;
        
        container.appendChild(chartDiv);

        // Create the chart
        setTimeout(() => {
            const ctx = document.getElementById('costComparisonChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'],
                    datasets: [{
                        label: 'Pipeline (₹/kg)',
                        data: [220, 240, 230, 235, 245],
                        backgroundColor: '#0dcaf0',
                        borderColor: '#0dcaf0',
                        borderWidth: 1
                    }, {
                        label: 'Trucking (₹/kg)',
                        data: [350, 380, 360, 370, 385],
                        backgroundColor: '#fd7e14',
                        borderColor: '#fd7e14',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'LCOH (₹/kg)'
                            }
                        }
                    }
                }
            });
        }, 100);
    }

    createTransportCostChart(container) {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'col-lg-6 col-xl-4 mb-4';
        
        chartDiv.innerHTML = `
            <div class="chart-container">
                <h6 class="chart-title">Transport Cost Breakdown</h6>
                <p class="chart-description">Cost components for hydrogen transport</p>
                <canvas id="transportCostChart" width="400" height="300"></canvas>
            </div>
        `;
        
        container.appendChild(chartDiv);

        // Create the chart
        setTimeout(() => {
            const ctx = document.getElementById('transportCostChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Infrastructure', 'Energy', 'Maintenance', 'Labor', 'Other'],
                    datasets: [{
                        data: [35, 25, 20, 15, 5],
                        backgroundColor: [
                            '#28a745',
                            '#fd7e14',
                            '#0dcaf0',
                            '#6f42c1',
                            '#6c757d'
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
        }, 100);
    }

    createLocationSuitabilityChart(container) {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'col-lg-6 col-xl-4 mb-4';
        
        chartDiv.innerHTML = `
            <div class="chart-container">
                <h6 class="chart-title">Location Suitability Distribution</h6>
                <p class="chart-description">Suitability levels across analyzed locations</p>
                <canvas id="suitabilityChart" width="400" height="300"></canvas>
            </div>
        `;
        
        container.appendChild(chartDiv);

        // Create the chart
        setTimeout(() => {
            const ctx = document.getElementById('suitabilityChart').getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Most Suitable', 'Mild Suitable', 'Unsuitable'],
                    datasets: [{
                        data: [25, 45, 30],
                        backgroundColor: ['#28a745', '#fd7e14', '#dc3545']
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
        }, 100);
    }

    createRenewablePotentialChart(container) {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'col-lg-6 col-xl-4 mb-4';
        
        chartDiv.innerHTML = `
            <div class="chart-container">
                <h6 class="chart-title">Renewable Energy Potential</h6>
                <p class="chart-description">Wind and solar potential by region</p>
                <canvas id="renewableChart" width="400" height="300"></canvas>
            </div>
        `;
        
        container.appendChild(chartDiv);

        // Create the chart
        setTimeout(() => {
            const ctx = document.getElementById('renewableChart').getContext('2d');
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['North', 'South', 'East', 'West', 'Central'],
                    datasets: [{
                        label: 'Wind Potential (MW)',
                        data: [80, 90, 60, 95, 70],
                        backgroundColor: 'rgba(13, 202, 240, 0.2)',
                        borderColor: '#0dcaf0',
                        borderWidth: 2
                    }, {
                        label: 'Solar Potential (MW)',
                        data: [85, 75, 90, 80, 85],
                        backgroundColor: 'rgba(253, 126, 20, 0.2)',
                        borderColor: '#fd7e14',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }, 100);
    }

    createInfrastructureChart(container) {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'col-lg-6 col-xl-4 mb-4';
        
        chartDiv.innerHTML = `
            <div class="chart-container">
                <h6 class="chart-title">Infrastructure Availability</h6>
                <p class="chart-description">Infrastructure scores by location type</p>
                <canvas id="infrastructureChart" width="400" height="300"></canvas>
            </div>
        `;
        
        container.appendChild(chartDiv);

        // Create the chart
        setTimeout(() => {
            const ctx = document.getElementById('infrastructureChart').getContext('2d');
            new Chart(ctx, {
                type: 'horizontalBar',
                data: {
                    labels: ['Roads', 'Power Grid', 'Water Supply', 'Port Access', 'Railway'],
                    datasets: [{
                        label: 'Infrastructure Score (%)',
                        data: [85, 75, 70, 60, 80],
                        backgroundColor: [
                            '#28a745',
                            '#fd7e14',
                            '#0dcaf0',
                            '#6f42c1',
                            '#6c757d'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }, 100);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GeoH2Frontend();
}); 