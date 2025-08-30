#!/usr/bin/env python3
"""
Process NASA POWER Weather Data for India
Reads the .nc file and converts it to usable format
"""

import xarray as xr
import pandas as pd
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_nasa_weather_data():
    """Process the NASA POWER weather data file"""
    
    data_dir = Path(__file__).parent.parent / "Data"
    nc_file = data_dir / "weather_india.nc"
    
    if not nc_file.exists():
        logger.error("NASA weather file not found!")
        return None
    
    try:
        logger.info("Reading NASA POWER weather data...")
        
        # Try to read with xarray
        ds = xr.open_dataset(nc_file)
        
        logger.info("Successfully read NASA POWER data!")
        logger.info(f"Dataset info: {ds.info()}")
        
        # Extract key information
        variables = list(ds.data_vars.keys())
        dimensions = dict(ds.dims)
        coordinates = list(ds.coords.keys())
        
        logger.info(f"Variables: {variables}")
        logger.info(f"Dimensions: {dimensions}")
        logger.info(f"Coordinates: {coordinates}")
        
        # Check if we have the expected data
        if 'ALLSKY_SFC_SW_DWN' in variables:
            logger.info("✅ Solar radiation data found!")
            
            # Get solar data
            solar_data = ds['ALLSKY_SFC_SW_DWN']
            logger.info(f"Solar data shape: {solar_data.shape}")
            logger.info(f"Solar data range: {float(solar_data.min())} to {float(solar_data.max())}")
            
            # Create summary
            summary = {
                "status": "success",
                "data_source": "NASA POWER",
                "variables": variables,
                "dimensions": dimensions,
                "coordinates": coordinates,
                "solar_data": {
                    "available": True,
                    "shape": list(solar_data.shape),
                    "min_value": float(solar_data.min()),
                    "max_value": float(solar_data.max()),
                    "units": str(solar_data.units) if hasattr(solar_data, 'units') else "Unknown"
                },
                "file_size_kb": nc_file.stat().st_size / 1024
            }
            
            # Save summary
            summary_file = data_dir / "nasa_weather_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Summary saved to {summary_file}")
            
            # Update the comprehensive weather file
            update_comprehensive_weather(summary)
            
            return summary
            
        else:
            logger.warning("Solar radiation data not found in expected format")
            return None
            
    except Exception as e:
        logger.error(f"Error processing NASA weather data: {e}")
        return None

def update_comprehensive_weather(nasa_summary):
    """Update the comprehensive weather file with NASA data"""
    
    data_dir = Path(__file__).parent.parent / "Data"
    comp_file = data_dir / "india_comprehensive_weather.json"
    
    if not comp_file.exists():
        logger.warning("Comprehensive weather file not found")
        return
    
    try:
        # Read existing data
        with open(comp_file, 'r') as f:
            comp_data = json.load(f)
        
        # Update with NASA data
        comp_data["nasa_power_data"] = {
            "status": "available",
            "variables": nasa_summary["variables"],
            "solar_data": nasa_summary["solar_data"],
            "file_size_kb": nasa_summary["file_size_kb"]
        }
        
        # Update metadata
        comp_data["metadata"]["last_updated"] = pd.Timestamp.now().isoformat()
        comp_data["metadata"]["nasa_data_status"] = "processed"
        
        # Save updated file
        with open(comp_file, 'w') as f:
            json.dump(comp_data, f, indent=2)
        
        logger.info("Updated comprehensive weather file with NASA data")
        
    except Exception as e:
        logger.error(f"Error updating comprehensive weather file: {e}")

if __name__ == "__main__":
    print("🌤️ Processing NASA POWER Weather Data for India...")
    print("=" * 60)
    
    result = process_nasa_weather_data()
    
    if result:
        print("\n✅ NASA Weather Data Processing Completed!")
        print("=" * 60)
        print(f"📊 Variables found: {len(result['variables'])}")
        print(f"🌞 Solar data: {'Available' if result['solar_data']['available'] else 'Missing'}")
        print(f"📁 File size: {result['file_size_kb']:.1f} KB")
        print(f"📋 Summary saved to: Data/nasa_weather_summary.json")
        print(f"🔄 Comprehensive weather file updated")
        
        print("\n💡 Next steps:")
        print("   1. Restart the API server to see new data")
        print("   2. Check /api/status for updated weather info")
        print("   3. Use /api/india/summary to see integrated data")
        
    else:
        print("\n❌ Failed to process NASA weather data")
        print("Check the logs above for error details")
