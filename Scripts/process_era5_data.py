#!/usr/bin/env python3
"""
Process ERA5 Reanalysis Data for India
Extracts weather data from the large ERA5 NetCDF file
"""

import xarray as xr
import pandas as pd
import numpy as np
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_era5_data():
    """Process the ERA5 reanalysis data file"""
    
    data_dir = Path(__file__).parent.parent / "Data"
    era5_file = data_dir / "ERA5_data.nc"
    
    if not era5_file.exists():
        logger.error("ERA5 data file not found!")
        return None
    
    try:
        logger.info("Reading ERA5 reanalysis data...")
        logger.info(f"File size: {era5_file.stat().st_size / (1024**3):.2f} GB")
        
        # Open the dataset
        ds = xr.open_dataset(era5_file)
        
        logger.info("Successfully read ERA5 data!")
        
        # Extract key information
        variables = list(ds.data_vars.keys())
        dimensions = dict(ds.sizes)  # Fixed: use sizes instead of dims
        coordinates = list(ds.coords.keys())
        
        logger.info(f"Variables: {variables}")
        logger.info(f"Dimensions: {dimensions}")
        logger.info(f"Coordinates: {coordinates}")
        
        # Check for India region (approximate bounds)
        if 'latitude' in ds.coords and 'longitude' in ds.coords:
            lats = ds.latitude.values
            lons = ds.longitude.values
            
            logger.info(f"Latitude range: {lats.min():.2f} to {lats.max():.2f}")
            logger.info(f"Longitude range: {lons.min():.2f} to {lons.max():.2f}")
            
            # India bounds: 6°N to 37°N, 68°E to 97°E
            # Note: ERA5 uses 0-360° longitude, so 68°E = 68°, 97°E = 97°
            india_mask = (
                (lats >= 6) & (lats <= 37) & 
                (lons >= 68) & (lons <= 97)
            )
            
            if india_mask.any():
                logger.info("✅ India region found in ERA5 data!")
                
                # Extract India subset
                india_ds = ds.sel(
                    latitude=slice(6, 37),
                    longitude=slice(68, 97)
                )
                
                logger.info(f"India subset shape: {dict(india_ds.sizes)}")
                
                # Process each variable
                weather_summary = process_weather_variables(india_ds)
                
                # Save summary
                summary_file = data_dir / "era5_india_summary.json"
                with open(summary_file, 'w') as f:
                    json.dump(weather_summary, f, indent=2)
                
                logger.info(f"Summary saved to {summary_file}")
                
                # Update comprehensive weather file
                update_comprehensive_weather(weather_summary)
                
                return weather_summary
            else:
                logger.warning("India region not found in ERA5 data")
                return None
        else:
            logger.warning("Latitude/longitude coordinates not found")
            return None
            
    except Exception as e:
        logger.error(f"Error processing ERA5 data: {e}")
        return None

def process_weather_variables(ds):
    """Process individual weather variables"""
    
    summary = {
        "status": "success",
        "data_source": "ERA5 Reanalysis",
        "coverage": "India",
        "variables": {},
        "spatial_info": {},
        "temporal_info": {}
    }
    
    # Process each variable
    for var_name in ds.data_vars:
        var = ds[var_name]
        
        # Get basic info
        var_info = {
            "shape": list(var.shape),
            "dtype": str(var.dtype),
            "units": str(var.units) if hasattr(var, 'units') else "Unknown"
        }
        
        # Get statistics
        try:
            var_info["min"] = float(var.min())
            var_info["max"] = float(var.max())
            var_info["mean"] = float(var.mean())
        except:
            var_info["statistics"] = "Unable to compute"
        
        summary["variables"][var_name] = var_info
    
    # Spatial information
    if 'latitude' in ds.coords and 'longitude' in ds.coords:
        summary["spatial_info"] = {
            "lat_range": [float(ds.latitude.min()), float(ds.latitude.max())],
            "lon_range": [float(ds.longitude.min()), float(ds.longitude.max())],
            "resolution": "ERA5 native resolution (0.25°)"
        }
    
    # Temporal information
    if 'valid_time' in ds.coords:
        times = ds.valid_time.values
        summary["temporal_info"] = {
            "start_date": str(times[0]),
            "end_date": str(times[-1]),
            "total_timesteps": len(times),
            "time_frequency": "3-6 hourly"
        }
    
    return summary

def update_comprehensive_weather(era5_summary):
    """Update the comprehensive weather file with ERA5 data"""
    
    data_dir = Path(__file__).parent.parent / "Data"
    comp_file = data_dir / "india_comprehensive_weather.json"
    
    if not comp_file.exists():
        logger.warning("Comprehensive weather file not found")
        return
    
    try:
        # Read existing data
        with open(comp_file, 'r') as f:
            comp_data = json.load(f)
        
        # Update with ERA5 data
        comp_data["era5_data"] = {
            "status": "available",
            "variables": list(era5_summary["variables"].keys()),
            "spatial_coverage": era5_summary["spatial_info"],
            "temporal_coverage": era5_summary["temporal_info"],
            "file_size_gb": 2.6
        }
        
        # Update metadata
        comp_data["metadata"]["last_updated"] = pd.Timestamp.now().isoformat()
        comp_data["metadata"]["era5_data_status"] = "processed"
        
        # Save updated file
        with open(comp_file, 'w') as f:
            json.dump(comp_data, f, indent=2)
        
        logger.info("Updated comprehensive weather file with ERA5 data")
        
    except Exception as e:
        logger.error(f"Error updating comprehensive weather file: {e}")

if __name__ == "__main__":
    print("🌤️ Processing ERA5 Reanalysis Data for India...")
    print("=" * 60)
    
    result = process_era5_data()
    
    if result:
        print("\n✅ ERA5 Data Processing Completed!")
        print("=" * 60)
        print(f"📊 Variables found: {len(result['variables'])}")
        print(f"🌍 Coverage: {result['coverage']}")
        print(f"📁 Summary saved to: Data/era5_india_summary.json")
        print(f"🔄 Comprehensive weather file updated")
        
        print("\n💡 Next steps:")
        print("   1. Check the ERA5 summary for data details")
        print("   2. Restart the API server to see new data")
        print("   3. Use /api/status for updated weather info")
        
    else:
        print("\n❌ Failed to process ERA5 data")
        print("Check the logs above for error details")
