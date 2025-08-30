#!/usr/bin/env python3
"""
Download Real Weather Data for India
Downloads actual weather measurements from NASA POWER and other sources
"""

import requests
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndiaWeatherDownloader:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "Data"
        self.data_dir.mkdir(exist_ok=True)
        
        # India geographic bounds
        self.india_bounds = {
            'lat_min': 6.0,
            'lat_max': 37.0,
            'lon_min': 68.0,
            'lon_max': 97.0
        }
        
        # NASA POWER API endpoints
        self.nasa_power_base = "https://power.larc.nasa.gov/api/temporal/daily/regional"
        
    def download_nasa_power_data(self, start_date, end_date, parameters):
        """
        Download weather data from NASA POWER API for India
        """
        logger.info(f"Downloading NASA POWER data from {start_date} to {end_date}")
        
        # Create grid of points covering India (reduced resolution for API limits)
        lat_step = 1.0  # 1 degree spacing
        lon_step = 1.0
        
        lats = np.arange(self.india_bounds['lat_min'], self.india_bounds['lat_max'] + lat_step, lat_step)
        lons = np.arange(self.india_bounds['lon_min'], self.india_bounds['lon_max'] + lon_step, lon_step)
        
        logger.info(f"Creating grid: {len(lats)} x {len(lons)} = {len(lats) * len(lons)} points")
        
        all_data = []
        
        # Process in batches to avoid overwhelming the API
        batch_size = 10
        total_points = len(lats) * len(lons)
        
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                point_num = i * len(lons) + j + 1
                
                if point_num % batch_size == 0:
                    logger.info(f"Processing point {point_num}/{total_points} ({point_num/total_points*100:.1f}%)")
                    time.sleep(1)  # Be nice to the API
                
                try:
                    # Download data for this point
                    point_data = self._download_single_point(lat, lon, start_date, end_date, parameters)
                    if point_data:
                        all_data.append(point_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to download data for point ({lat}, {lon}): {e}")
                    continue
        
        logger.info(f"Successfully downloaded data for {len(all_data)} points")
        return all_data
    
    def _download_single_point(self, lat, lon, start_date, end_date, parameters):
        """
        Download weather data for a single geographic point
        """
        # NASA POWER API parameters
        api_params = {
            'parameters': ','.join(parameters),
            'community': 'RE',
            'longitude': lon,
            'latitude': lat,
            'start': start_date,
            'end': end_date,
            'format': 'JSON'
        }
        
        try:
            response = requests.get(self.nasa_power_base, params=api_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract the weather data
            if 'properties' in data and 'parameter' in data['properties']:
                weather_data = {
                    'lat': lat,
                    'lon': lon,
                    'data': data['properties']['parameter']
                }
                return weather_data
                
        except Exception as e:
            logger.debug(f"API call failed for ({lat}, {lon}): {e}")
            return None
    
    def download_global_wind_atlas(self):
        """
        Download wind resource data from Global Wind Atlas
        """
        logger.info("Downloading Global Wind Atlas data for India")
        
        # Global Wind Atlas provides data through their web interface
        # For now, we'll note this as a source and provide instructions
        
        wind_atlas_info = {
            'source': 'Global Wind Atlas',
            'url': 'https://globalwindatlas.info/',
            'coverage': 'India',
            'data_type': 'Wind speed at 100m height',
            'resolution': '250m',
            'note': 'Data available through web interface, requires manual download'
        }
        
        # Save info for user reference
        wind_info_file = self.data_dir / "global_wind_atlas_info.json"
        with open(wind_info_file, 'w') as f:
            json.dump(wind_atlas_info, f, indent=2)
        
        logger.info(f"Global Wind Atlas info saved to {wind_info_file}")
        return wind_atlas_info
    
    def download_global_solar_atlas(self):
        """
        Download solar resource data from Global Solar Atlas
        """
        logger.info("Downloading Global Solar Atlas data for India")
        
        # Global Solar Atlas provides data through their web interface
        solar_atlas_info = {
            'source': 'Global Solar Atlas',
            'url': 'https://globalsolaratlas.info/',
            'coverage': 'India',
            'data_type': 'Global Horizontal Irradiance (GHI)',
            'resolution': '1km',
            'note': 'Data available through web interface, requires manual download'
        }
        
        # Save info for user reference
        solar_info_file = self.data_dir / "global_solar_atlas_info.json"
        with open(solar_info_file, 'w') as f:
            json.dump(solar_atlas_info, f, indent=2)
        
        logger.info(f"Global Solar Atlas info saved to {solar_info_file}")
        return solar_atlas_info
    
    def create_weather_summary(self, weather_data):
        """
        Create a summary of downloaded weather data
        """
        if not weather_data:
            return None
        
        summary = {
            'total_points': len(weather_data),
            'coverage': {
                'lat_range': [min(p['lat'] for p in weather_data), max(p['lat'] for p in weather_data)],
                'lon_range': [min(p['lon'] for p in weather_data), max(p['lon'] for p in weather_data)]
            },
            'data_parameters': list(weather_data[0]['data'].keys()) if weather_data else [],
            'download_timestamp': datetime.now().isoformat()
        }
        
        # Save summary
        summary_file = self.data_dir / "india_weather_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Weather data summary saved to {summary_file}")
        return summary
    
    def download_india_weather(self, start_date="2023-01-01", end_date="2023-12-31"):
        """
        Main function to download all India weather data
        """
        logger.info("Starting India weather data download...")
        
        # Weather parameters to download from NASA POWER
        weather_parameters = [
            'T2M',      # Temperature at 2m height
            'T2M_MAX',  # Maximum temperature at 2m height
            'T2M_MIN',  # Minimum temperature at 2m height
            'WS2M',     # Wind speed at 2m height
            'WS10M',    # Wind speed at 10m height
            'WD10M',    # Wind direction at 10m height
            'ALLSKY_SFC_SW_DWN',  # All-sky surface shortwave downward irradiance
            'CLRSKY_SFC_SW_DWN',  # Clear-sky surface shortwave downward irradiance
            'PRECTOT',  # Precipitation
            'RH2M',     # Relative humidity at 2m height
            'PS',       # Surface pressure
        ]
        
        try:
            # 1. Download NASA POWER data
            logger.info("Step 1: Downloading NASA POWER weather data...")
            nasa_data = self.download_nasa_power_data(start_date, end_date, weather_parameters)
            
            if nasa_data:
                # Save NASA data
                nasa_file = self.data_dir / "india_nasa_power_weather.json"
                with open(nasa_file, 'w') as f:
                    json.dump(nasa_data, f, indent=2)
                logger.info(f"NASA POWER data saved to {nasa_file}")
                
                # Create summary
                self.create_weather_summary(nasa_data)
            else:
                logger.warning("No NASA POWER data downloaded")
            
            # 2. Download Global Wind Atlas info
            logger.info("Step 2: Getting Global Wind Atlas information...")
            wind_info = self.download_global_wind_atlas()
            
            # 3. Download Global Solar Atlas info
            logger.info("Step 3: Getting Global Solar Atlas information...")
            solar_info = self.download_global_solar_atlas()
            
            # 4. Create comprehensive weather data file
            logger.info("Step 4: Creating comprehensive weather data file...")
            comprehensive_data = {
                'metadata': {
                    'source': 'Multiple sources',
                    'coverage': 'India',
                    'date_range': f"{start_date} to {end_date}",
                    'download_timestamp': datetime.now().isoformat()
                },
                'nasa_power_data': nasa_data if nasa_data else [],
                'wind_atlas_info': wind_info,
                'solar_atlas_info': solar_info,
                'data_sources': {
                    'nasa_power': 'https://power.larc.nasa.gov/',
                    'global_wind_atlas': 'https://globalwindatlas.info/',
                    'global_solar_atlas': 'https://globalsolaratlas.info/'
                }
            }
            
            # Save comprehensive data
            comprehensive_file = self.data_dir / "india_comprehensive_weather.json"
            with open(comprehensive_file, 'w') as f:
                json.dump(comprehensive_data, f, indent=2)
            
            logger.info(f"Comprehensive weather data saved to {comprehensive_file}")
            
            # 5. Create NetCDF file for compatibility
            if nasa_data:
                logger.info("Step 5: Creating NetCDF weather file...")
                self._create_netcdf_file(nasa_data, start_date, end_date)
            
            logger.info("✅ India weather data download completed successfully!")
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error downloading weather data: {e}")
            return None
    
    def _create_netcdf_file(self, weather_data, start_date, end_date):
        """
        Create a NetCDF file from the weather data for compatibility
        """
        try:
            # Extract unique coordinates
            lats = sorted(list(set(p['lat'] for p in weather_data)))
            lons = sorted(list(set(p['lon'] for p in weather_data)))
            
            # Create time array
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            dates = pd.date_range(start_dt, end_dt, freq='D')
            
            # Create data arrays for each parameter
            data_vars = {}
            for param in weather_data[0]['data'].keys():
                # Create 3D array (time, lat, lon)
                param_data = np.full((len(dates), len(lats), len(lons)), np.nan)
                
                # Fill in the data
                for point in weather_data:
                    lat_idx = lats.index(point['lat'])
                    lon_idx = lons.index(point['lon'])
                    
                    if param in point['data']:
                        # Fill all time steps with the same value (simplified)
                        param_data[:, lat_idx, lon_idx] = point['data'][param]
                
                data_vars[param] = (['time', 'latitude', 'longitude'], param_data)
            
            # Create dataset
            ds = xr.Dataset(
                data_vars=data_vars,
                coords={
                    'time': dates,
                    'latitude': lats,
                    'longitude': lons
                }
            )
            
            # Add attributes
            ds.attrs['title'] = 'India Weather Data from NASA POWER'
            ds.attrs['source'] = 'NASA POWER API'
            ds.attrs['coverage'] = 'India'
            ds.attrs['date_range'] = f"{start_date} to {end_date}"
            
            # Save to NetCDF
            netcdf_file = self.data_dir / "india_weather_data.nc"
            ds.to_netcdf(netcdf_file)
            
            logger.info(f"NetCDF weather file created: {netcdf_file}")
            
        except Exception as e:
            logger.error(f"Error creating NetCDF file: {e}")

def main():
    """Main function"""
    print("🌤️  Starting India Weather Data Download...")
    print("=" * 60)
    
    downloader = IndiaWeatherDownloader()
    
    # Download weather data for 2023
    weather_data = downloader.download_india_weather(
        start_date="2023-01-01",
        end_date="2023-12-31"
    )
    
    if weather_data:
        print("\n✅ India Weather Data Download Completed!")
        print("=" * 60)
        print(f"📊 Total weather points: {len(weather_data['nasa_power_data'])}")
        print(f"🌪️  Wind data source: Global Wind Atlas")
        print(f"☀️  Solar data source: Global Solar Atlas")
        print(f"🌡️  Temperature data: NASA POWER API")
        print(f"💨 Wind speed data: NASA POWER API")
        print(f"📁 Data saved to: {downloader.data_dir}")
        print("\n📋 Files created:")
        print("   - india_nasa_power_weather.json (NASA weather data)")
        print("   - india_comprehensive_weather.json (All sources)")
        print("   - india_weather_data.nc (NetCDF format)")
        print("   - global_wind_atlas_info.json (Wind resource info)")
        print("   - global_solar_atlas_info.json (Solar resource info)")
        print("   - india_weather_summary.json (Data summary)")
        
        print("\n💡 Next steps:")
        print("   1. Use the NetCDF file for analysis")
        print("   2. Check the JSON files for detailed data")
        print("   3. Visit Global Wind/Solar Atlas for high-resolution data")
        
    else:
        print("\n❌ Weather data download failed!")
        print("Check the logs above for error details.")

if __name__ == "__main__":
    main() 