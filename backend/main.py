#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified GeoH2 Backend for India Data
Processes real data sources dynamically - no hardcoded values
"""

import logging
import json
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
import xarray as xr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeoH2UnifiedBackend:
    """Unified backend class for GeoH2 India data with real data processing"""
    
    def __init__(self, project_root: str = None):
        """Initialize the backend with project root path"""
        if project_root is None:
            project_root = Path(__file__).parent.parent
        
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "Data"
        self.resources_dir = self.project_root / "Resources"
        self.results_dir = self.project_root / "Results"
        self.plots_dir = self.project_root / "Plots"
        
        # Ensure directories exist
        for directory in [self.data_dir, self.resources_dir, self.results_dir, self.plots_dir]:
            directory.mkdir(exist_ok=True)
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status and available data"""
        try:
            status = {
                "project_name": "GeoH2 India",
                "version": "2.0.0",
                "status": "ready",
                "available_data": {},
                "available_results": {},
                "available_plots": {},
                "data_sources": {}
            }
            
            # Check hexagon data
            if (self.data_dir / "india_hexagons_with_lcoh_clean.geojson").exists():
                status["available_data"]["hexagons"] = "India LCOH Data Available"
                status["data_type"] = "India"
                status["status"] = "ready"
            elif (self.data_dir / "india_hexagons_clean.geojson").exists():
                status["available_data"]["hexagons"] = "India Hexagons Available (No LCOH)"
                status["data_type"] = "India"
                status["status"] = "partial"
            else:
                status["available_data"]["hexagons"] = "Missing"
                status["data_type"] = "None"
                status["status"] = "missing"
            
            # Check weather data sources
            weather_sources = self._check_weather_data_sources()
            status["data_sources"] = weather_sources
            
            # Check results
            if (self.data_dir / "india_hexagons_with_lcoh_clean.geojson").exists():
                status["available_results"]["cost_components"] = "India LCOH Available"
            else:
                status["available_results"]["cost_components"] = "Missing"
            
            # Check plots
            if (self.plots_dir / "india_lcoh_analysis.png").exists():
                status["available_plots"]["lcoh_analysis"] = "Available"
            else:
                status["available_plots"]["lcoh_analysis"] = "Not generated"
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return {"error": str(e)}
    
    def _check_weather_data_sources(self) -> Dict[str, Any]:
        """Check what weather data sources are available"""
        sources = {}
        
        # Check ERA5 data
        if (self.data_dir / "ERA5_data.nc").exists():
            sources["era5"] = {
                "status": "available",
                "file_size_gb": round((self.data_dir / "ERA5_data.nc").stat().st_size / (1024**3), 2),
                "type": "Reanalysis data (temperature, wind, pressure)"
            }
        else:
            sources["era5"] = {"status": "missing"}
        
        # Check Global Wind Atlas data
        wind_files = list(self.data_dir.glob("*wind*.tif")) + list(self.data_dir.glob("*wind*.csv"))
        if wind_files:
            sources["wind_atlas"] = {
                "status": "available",
                "files": [f.name for f in wind_files],
                "type": "Wind speed and power density"
            }
        else:
            sources["wind_atlas"] = {"status": "missing"}
        
        # Check Global Solar Atlas data
        if (self.data_dir / "india_solar_atlas_data.xlsx").exists():
            sources["solar_atlas"] = {
                "status": "available",
                "file": "india_solar_atlas_data.xlsx",
                "type": "Solar radiation data"
            }
        else:
            sources["solar_atlas"] = {"status": "missing"}
        
        return sources
    
    def get_india_hexagons(self, preview_only: bool = False) -> Dict[str, Any]:
        """Get India hexagon data with real processing"""
        try:
            # Try clean hexagons first, fallback to original
            hex_file = self.data_dir / "india_hexagons_clean.geojson"
            if not hex_file.exists():
                hex_file = self.data_dir / "india_hexagons.geojson"
                if not hex_file.exists():
                    return {"error": "India hexagons file not found"}
            
            # Read the data dynamically
            gdf = gpd.read_file(hex_file)
            
            # Process data dynamically (no hardcoded values)
            hex_data = self._process_hexagon_data(gdf, preview_only)
            
            return {
                "status": "success",
                "total_hexagons": len(gdf),
                "data": hex_data,
                "columns": list(gdf.columns),
                "bounds": gdf.total_bounds.tolist(),
                "statistics": self._calculate_hexagon_statistics(gdf)
            }
            
        except Exception as e:
            logger.error(f"Error reading India hexagons: {e}")
            return {"error": str(e)}
    
    def _process_hexagon_data(self, gdf: gpd.GeoDataFrame, preview_only: bool = False) -> Dict[str, Any]:
        """Process hexagon data dynamically"""
        try:
            # Extract numeric columns for statistics
            numeric_cols = gdf.select_dtypes(include=[np.number]).columns.tolist()
            
            if preview_only:
                # Convert to GeoJSON format (first 100 for preview)
                preview_data = json.loads(gdf.head(100).to_json())
                return {
                    "preview_hexagons": preview_data,
                    "numeric_columns": numeric_cols,
                    "total_features": len(gdf),
                    "note": "Showing first 100 hexagons for preview. Use preview_only=False to get all data."
                }
            else:
                # Convert to GeoJSON format (all hexagons)
                all_hexagons = json.loads(gdf.to_json())
                return {
                    "all_hexagons": all_hexagons,
                    "numeric_columns": numeric_cols,
                    "total_features": len(gdf),
                    "note": "Showing all hexagons. Use preview_only=True for faster preview."
                }
        except Exception as e:
            logger.error(f"Error processing hexagon data: {e}")
            return {"error": str(e)}
    
    def _calculate_hexagon_statistics(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Calculate statistics dynamically from hexagon data"""
        try:
            stats = {}
            numeric_cols = gdf.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if col in gdf.columns:
                    stats[col] = {
                        "min": float(gdf[col].min()),
                        "max": float(gdf[col].max()),
                        "mean": float(gdf[col].mean()),
                        "median": float(gdf[col].median())
                    }
            
            return stats
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {"error": str(e)}
    
    def get_all_india_hexagons(self) -> Dict[str, Any]:
        """Get ALL India hexagon data without any limitations"""
        return self.get_india_hexagons(preview_only=False)
    
    def get_india_hexagons_preview(self) -> Dict[str, Any]:
        """Get preview of India hexagon data (first 100)"""
        return self.get_india_hexagons(preview_only=True)
    
    def get_india_lcoh_data(self) -> Dict[str, Any]:
        """Get India LCOH data with real processing"""
        try:
            # Try clean LCOH data first, fallback to original
            lcoh_file = self.data_dir / "india_hexagons_with_lcoh_clean.geojson"
            if not lcoh_file.exists():
                lcoh_file = self.data_dir / "india_hexagons_with_lcoh.geojson"
                if not lcoh_file.exists():
                    return {"error": "India LCOH file not found"}
            
            # Read the data dynamically
            gdf = gpd.read_file(lcoh_file)
            
            # Process LCOH data dynamically
            lcoh_data = self._process_lcoh_data(gdf)
            
            return {
                "status": "success",
                "total_locations": len(gdf),
                "data": lcoh_data,
                "columns": list(gdf.columns),
                "bounds": gdf.total_bounds.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error reading India LCOH data: {e}")
            return {"error": str(e)}
    
    def _process_lcoh_data(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Process LCOH data dynamically"""
        try:
            # Get LCOH statistics if available
            lcoh_stats = None
            if 'lcoh' in gdf.columns:
                lcoh_stats = {
                    "min": float(gdf['lcoh'].min()),
                    "max": float(gdf['lcoh'].max()),
                    "mean": float(gdf['lcoh'].mean()),
                    "median": float(gdf['lcoh'].median())
                }
            
            # Convert to GeoJSON format (all data)
            all_data = json.loads(gdf.to_json())
            
            return {
                "lcoh_statistics": lcoh_stats,
                "all_data": all_data,
                "total_features": len(gdf)
            }
        except Exception as e:
            logger.error(f"Error processing LCOH data: {e}")
            return {"error": str(e)}
    
    def get_weather_summary(self) -> Dict[str, Any]:
        """Get comprehensive weather data summary"""
        try:
            summary = {
                "status": "success",
                "data_overview": {},
                "weather_sources": self._check_weather_data_sources()
            }
            
            # Process hexagon data
            hex_file = self.data_dir / "india_hexagons_clean.geojson"
            if hex_file.exists():
                gdf = gpd.read_file(hex_file)
                summary["data_overview"]["hexagons"] = {
                    "count": len(gdf),
                    "coverage": "India",
                    "resolution": "50 km hexagons"
                }
            
            # Process LCOH data
            lcoh_file = self.data_dir / "india_hexagons_with_lcoh_clean.geojson"
            if lcoh_file.exists():
                gdf = gpd.read_file(lcoh_file)
                if 'lcoh' in gdf.columns:
                    summary["data_overview"]["lcoh"] = {
                        "locations_analyzed": len(gdf),
                        "average_lcoh": float(gdf['lcoh'].mean()),
                        "lcoh_range": f"${gdf['lcoh'].min():.2f} - ${gdf['lcoh'].max():.2f}/kg H2"
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting weather summary: {e}")
            return {"error": str(e)}

# Create a global instance
backend = GeoH2UnifiedBackend()
