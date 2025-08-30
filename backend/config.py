# -*- coding: utf-8 -*-
"""
Backend Configuration for GeoH2
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
RESOURCES_DIR = PROJECT_ROOT / "Resources"
RESULTS_DIR = PROJECT_ROOT / "Results"
PLOTS_DIR = PROJECT_ROOT / "Plots"
PARAMETERS_DIR = PROJECT_ROOT / "Parameters"
SCRIPTS_DIR = PROJECT_ROOT / "Scripts"

# Default analysis parameters
DEFAULT_COUNTRY = "NA"
DEFAULT_WEATHER_YEAR = "2023"

# Analysis settings
MAX_HEXAGONS = 1000  # Maximum hexagons to process in one run
DEFAULT_TRANSPORT_TYPES = ["trucking", "pipeline"]

# Output settings
OUTPUT_FORMATS = ["geojson", "csv", "png"]
DEFAULT_OUTPUT_FORMAT = "geojson"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance settings
CHUNK_SIZE = 100  # Process hexagons in chunks for memory efficiency
MAX_WORKERS = 4   # Maximum number of parallel workers

# File paths
HEXAGON_FILE_PATTERN = "hex_final_{country}.geojson"
WEATHER_DATA_FILE = "weather_data.nc"
COST_COMPONENTS_FILE_PATTERN = "hex_cost_components_{country}_{weather_year}.geojson"

# Validation settings
REQUIRED_HEXAGON_COLUMNS = [
    "waterbody_dist", "waterway_dist", "ocean_dist", 
    "grid_dist", "road_dist", "theo_pv", "theo_wind", "country"
]

REQUIRED_PARAMETER_FILES = [
    "country_parameters.xlsx",
    "demand_parameters.xlsx", 
    "technology_parameters.xlsx",
    "transport_parameters.xlsx",
    "pipeline_parameters.xlsx",
    "conversion_parameters.xlsx"
] 