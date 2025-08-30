#!/usr/bin/env python3
"""
Download Real ERA5 Weather Data for India
Downloads actual weather measurements from ERA5 reanalysis
"""

import cdsapi
import xarray as xr
import numpy as np
from pathlib import Path
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndiaERA5Downloader:
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
        
        # Initialize CDS API client
        try:
            self.cds = cdsapi.Client()
            logger.info("CDS API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CDS API client: {e}")
            logger.info("Please ensure you have CDS API credentials set up")
            self.cds = None
    
    def download_era5_weather(self, year="2023", month="01"):
        """
        Download ERA5 weather data for India
        """
        if not self.cds:
            logger.error("CDS API client not available")
            return None
        
        logger.info(f"Downloading ERA5 weather data for {year}-{month}")
        
        try:
            # Download surface weather data
            surface_file = self._download_surface_data(year, month)
            
            # Download wind data at different heights
            wind_file = self._download_wind_data(year, month)
            
            # Download solar radiation data
            solar_file = self._download_solar_data(year, month)
            
            # Combine all data
            if surface_file and wind_file and solar_file:
                combined_file = self._combine_weather_data(surface_file, wind_file, solar_file, year, month)
                return combined_file
            
        except Exception as e:
            logger.error(f"Error downloading ERA5 data: {e}")
            return None
    
    def _download_surface_data(self, year, month):
        """Download surface weather parameters"""
        try:
            logger.info("Downloading surface weather data...")
            
            surface_file = self.data_dir / f"india_era5_surface_{year}_{month}.nc"
            
            self.cds.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        '2m_temperature',
                        '2m_dewpoint_temperature',
                        'surface_pressure',
                        'total_precipitation',
                        'relative_humidity_at_2m',
                        'surface_solar_radiation_downwards_hourly',
                        'surface_thermal_radiation_downwards_hourly',
                    ],
                    'year': year,
                    'month': month,
                    'day': [f"{i:02d}" for i in range(1, 32)],  # All days
                    'time': [f"{i:02d}:00" for i in range(24)],   # All hours
                    'area': [
                        self.india_bounds['lat_max'],  # North
                        self.india_bounds['lon_min'],  # West
                        self.india_bounds['lat_min'],  # South
                        self.india_bounds['lon_max'],  # East
                    ],
                    'format': 'netcdf',
                },
                surface_file
            )
            
            logger.info(f"Surface data downloaded: {surface_file}")
            return surface_file
            
        except Exception as e:
            logger.error(f"Error downloading surface data: {e}")
            return None
    
    def _download_wind_data(self, year, month):
        """Download wind data at different heights"""
        try:
            logger.info("Downloading wind data...")
            
            wind_file = self.data_dir / f"india_era5_wind_{year}_{month}.nc"
            
            self.cds.retrieve(
                'reanalysis-era5-pressure-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        'u_component_of_wind',
                        'v_component_of_wind',
                    ],
                    'pressure_level': [
                        '10',
                        '50',
                        '100',
                        '200',
                        '500',
                        '850',
                        '1000',
                    ],
                    'year': year,
                    'month': month,
                    'day': [f"{i:02d}" for i in range(1, 32)],
                    'time': [f"{i:02d}:00" for i in range(24)],
                    'area': [
                        self.india_bounds['lat_max'],
                        self.india_bounds['lon_min'],
                        self.india_bounds['lat_min'],
                        self.india_bounds['lon_max'],
                    ],
                    'format': 'netcdf',
                },
                wind_file
            )
            
            logger.info(f"Wind data downloaded: {wind_file}")
            return wind_file
            
        except Exception as e:
            logger.error(f"Error downloading wind data: {e}")
            return None
    
    def _download_solar_data(self, year, month):
        """Download solar radiation data"""
        try:
            logger.info("Downloading solar radiation data...")
            
            solar_file = self.data_dir / f"india_era5_solar_{year}_{month}.nc"
            
            self.cds.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        'surface_solar_radiation_downwards_hourly',
                        'surface_thermal_radiation_downwards_hourly',
                        'total_sky_direct_solar_radiation_at_surface',
                        'total_sky_direct_solar_radiation_at_surface_1_hour_Accumulation',
                    ],
                    'year': year,
                    'month': month,
                    'day': [f"{i:02d}" for i in range(1, 32)],
                    'time': [f"{i:02d}:00" for i in range(24)],
                    'area': [
                        self.india_bounds['lat_max'],
                        self.india_bounds['lon_min'],
                        self.india_bounds['lat_min'],
                        self.india_bounds['lon_max'],
                    ],
                    'format': 'netcdf',
                },
                solar_file
            )
            
            logger.info(f"Solar data downloaded: {solar_file}")
            return solar_file
            
        except Exception as e:
            logger.error(f"Error downloading solar data: {e}")
            return None
    
    def _combine_weather_data(self, surface_file, wind_file, solar_file, year, month):
        """Combine all weather data into a single file"""
        try:
            logger.info("Combining weather data...")
            
            # Load all datasets
            surface_ds = xr.open_dataset(surface_file)
            wind_ds = xr.open_dataset(wind_file)
            solar_ds = xr.open_dataset(solar_file)
            
            # Merge datasets
            combined_ds = xr.merge([surface_ds, wind_ds, solar_ds])
            
            # Add metadata
            combined_ds.attrs['title'] = 'India ERA5 Weather Data'
            combined_ds.attrs['source'] = 'ERA5 Reanalysis'
            combined_ds.attrs['coverage'] = 'India'
            combined_ds.attrs['date_range'] = f"{year}-{month}"
            combined_ds.attrs['geographic_bounds'] = str(self.india_bounds)
            
            # Save combined data
            combined_file = self.data_dir / f"india_era5_weather_{year}_{month}.nc"
            combined_ds.to_netcdf(combined_file)
            
            # Close datasets
            surface_ds.close()
            wind_ds.close()
            solar_ds.close()
            combined_ds.close()
            
            logger.info(f"Combined weather data saved: {combined_file}")
            return combined_file
            
        except Exception as e:
            logger.error(f"Error combining weather data: {e}")
            return None
    
    def create_weather_summary(self, weather_file):
        """Create a summary of the weather data"""
        try:
            if not weather_file or not weather_file.exists():
                return None
            
            # Load dataset
            ds = xr.open_dataset(weather_file)
            
            # Create summary
            summary = {
                'file': str(weather_file),
                'source': 'ERA5 Reanalysis',
                'coverage': 'India',
                'variables': list(ds.data_vars.keys()),
                'dimensions': {dim: size for dim, size in ds.dims.items()},
                'coordinates': {
                    'latitude': {
                        'min': float(ds.latitude.min()),
                        'max': float(ds.latitude.max()),
                        'count': len(ds.latitude)
                    },
                    'longitude': {
                        'min': float(ds.longitude.min()),
                        'max': float(ds.longitude.max()),
                        'count': len(ds.longitude)
                    },
                    'time': {
                        'start': str(ds.time.min().values),
                        'end': str(ds.time.max().values),
                        'count': len(ds.time)
                    }
                },
                'attributes': dict(ds.attrs),
                'download_timestamp': datetime.now().isoformat()
            }
            
            # Close dataset
            ds.close()
            
            # Save summary
            summary_file = self.data_dir / "india_era5_weather_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Weather summary saved: {summary_file}")
            return summary
            
        except Exception as e:
            logger.error(f"Error creating weather summary: {e}")
            return None

def main():
    """Main function"""
    print("🌤️  Starting India ERA5 Weather Data Download...")
    print("=" * 60)
    
    downloader = IndiaERA5Downloader()
    
    if not downloader.cds:
        print("\n❌ CDS API client not available!")
        print("Please set up CDS API credentials:")
        print("1. Visit: https://cds.climate.copernicus.eu/")
        print("2. Create an account and get your API key")
        print("3. Create ~/.cdsapirc file with your credentials")
        print("4. Run this script again")
        return
    
    # Download weather data for January 2023 (as an example)
    weather_file = downloader.download_era5_weather(year="2023", month="01")
    
    if weather_file:
        print("\n✅ India ERA5 Weather Data Download Completed!")
        print("=" * 60)
        print(f"📁 Weather data file: {weather_file}")
        
        # Create summary
        summary = downloader.create_weather_summary(weather_file)
        if summary:
            print(f"📊 Total variables: {len(summary['variables'])}")
            print(f"🌍 Coverage: {summary['coordinates']['latitude']['count']} x {summary['coordinates']['longitude']['count']} grid points")
            print(f"⏰ Time range: {summary['coordinates']['time']['start']} to {summary['coordinates']['time']['end']}")
        
        print("\n💡 Next steps:")
        print("   1. Use the NetCDF file for analysis")
        print("   2. Check the summary JSON file for data details")
        print("   3. Download additional months if needed")
        
    else:
        print("\n❌ ERA5 weather data download failed!")
        print("Check the logs above for error details.")

if __name__ == "__main__":
    main() 