# GeoH2 Backend

## Overview
GeoH2 Backend is a comprehensive hydrogen cost analysis system that provides geospatial optimization for green hydrogen production, storage, transport, and conversion costs.

## Features
- **Geospatial Analysis**: Analyze hydrogen costs across 616 hexagons in Namibia
- **Transport Optimization**: Compare trucking vs pipeline transport costs
- **Cost Components**: Detailed breakdown of wind, solar, electrolyzer, battery, and storage costs
- **Visualization**: Generate clear charts and maps for decision-making
- **REST API**: HTTP endpoints for integration with frontend applications

## Project Structure
```
backend/
├── __init__.py              # Package initialization
├── main.py                  # Main backend class and logic
├── config.py                # Configuration settings
├── api_server.py            # HTTP API server
├── test_backend.py          # Functionality tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Data Files
Ensure the following files exist in the project root:
- `Data/hex_final_NA.geojson` - Hexagon data for Namibia
- `Data/weather_data.nc` - Weather data
- `Parameters/NA/*.xlsx` - Parameter files

## Usage

### 1. Test Backend Functionality
```bash
python test_backend.py
```

### 2. Run API Server
```bash
python api_server.py
```
The server will start on `http://localhost:8000`

### 3. Use Backend Programmatically
```python
from main import GeoH2Backend

# Initialize backend
backend = GeoH2Backend()

# Get project status
status = backend.get_project_status()

# Run full analysis
results = backend.run_full_analysis("NA", "2023")

# Get analysis results
analysis_results = backend.get_analysis_results()

# Get visualization files
plots = backend.get_visualization_files()
```

## API Endpoints

### GET `/api/health`
Check if the backend is running
```json
{
  "status": "healthy",
  "message": "GeoH2 Backend is running"
}
```

### GET `/api/status`
Get project status and available data
```json
{
  "project_name": "GeoH2",
  "version": "1.0.0",
  "status": "ready",
  "available_data": {...},
  "available_results": {...},
  "available_plots": {...}
}
```

### GET `/api/results`
Get hydrogen cost analysis results
```json
{
  "country": "NA",
  "weather_year": "2023",
  "data": {
    "Lüderitz": {
      "trucking": {
        "min_lcoh": 1.88,
        "max_lcoh": 5.43,
        "mean_lcoh": 3.50,
        "median_lcoh": 3.51,
        "std_lcoh": 0.49
      },
      "pipeline": {
        "min_lcoh": 1.34,
        "max_lcoh": 4.23,
        "mean_lcoh": 2.81,
        "median_lcoh": 2.82,
        "std_lcoh": 0.52
      }
    }
  }
}
```

### GET `/api/plots`
Get available visualization files
```json
{
  "status": "success",
  "plots_directory": "Plots/NA_2023_clear",
  "available_plots": [
    "lcoh_comparison.png",
    "cost_breakdown.png",
    "simple_cost_map.png",
    "cost_summary_table.png",
    "cost_savings_histogram.png"
  ],
  "total_plots": 5
}
```

### POST `/api/analyze`
Run complete hydrogen cost analysis
```json
{
  "country": "NA",
  "weather_year": "2023"
}
```

## Analysis Workflow

The backend implements a 7-step analysis workflow:

1. **Assign Country Parameters** - Load country-specific economic parameters
2. **Optimize Transport** - Calculate transport costs for each hexagon
3. **Calculate Water Costs** - Determine water availability and costs
4. **Optimize Hydrogen Plant** - Design optimal plant configurations
5. **Calculate Total Hydrogen Cost** - Combine all cost components
6. **Calculate Cost Components** - Break down costs by technology
7. **Create Visualizations** - Generate charts and maps

## Key Results

### Cost Comparison (Lüderitz, Namibia)
- **Trucking Transport**: 3.50 €/kg H2 (average)
- **Pipeline Transport**: 2.81 €/kg H2 (average)
- **Cost Savings**: 0.69 €/kg H2 with pipeline (20% cheaper)

### Analysis Coverage
- **Hexagons**: 616 locations across Namibia
- **Demand Centers**: 1 (Lüderitz)
- **Transport Types**: Trucking and Pipeline
- **Technologies**: Wind, Solar, Electrolyzer, Battery, Storage

## Configuration

Modify `config.py` to adjust:
- Default country and weather year
- Performance settings (chunk size, max workers)
- Output formats and file paths
- Validation requirements

## Testing

Run the comprehensive test suite:
```bash
python test_backend.py
```

Tests cover:
- Module imports
- Data file availability
- Basic function functionality
- Complete analysis workflow
- Output file generation

## Error Handling

The backend includes comprehensive error handling:
- Graceful degradation for missing data
- Detailed error messages and logging
- Fallback options for failed analysis steps
- Input validation and sanitization

## Performance

- **Memory Efficient**: Processes hexagons in chunks
- **Parallel Processing**: Supports multiple workers
- **Optimized I/O**: Efficient file reading and writing
- **Caching**: Reuses intermediate results when possible

## Integration

The backend is designed for easy integration:
- **REST API**: Standard HTTP endpoints
- **JSON Output**: Machine-readable results
- **Modular Design**: Easy to extend and modify
- **Documentation**: Comprehensive API documentation

## Support

For issues or questions:
1. Check the test output for errors
2. Verify all required data files exist
3. Check the logs for detailed error messages
4. Ensure all dependencies are installed correctly

## License

MIT License - see LICENSE file in project root 