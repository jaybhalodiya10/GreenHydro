#!/usr/bin/env python3
"""
Fix India Hexagons - Generate clean, valid hexagon data with better coverage
"""
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
import json
from pathlib import Path

def create_valid_hexagons():
    """Create valid hexagon grid for India with better coverage"""
    
    # India bounds (approximate) - expanded for better coverage
    lat_min, lat_max = 6.0, 37.0
    lon_min, lon_max = 68.0, 97.0
    
    # Hexagon size (in degrees) - smaller for better resolution
    hex_size = 0.5  # Reduced from 1.0 to 0.5 for better coverage
    
    hexagons = []
    hex_id = 0
    
    # Create hexagon grid with better spacing
    for lat in np.arange(lat_min, lat_max, hex_size * 0.866):  # 0.866 = cos(30°)
        for lon in np.arange(lon_min, lon_max, hex_size):
            # Create hexagon coordinates
            hex_coords = []
            for i in range(6):
                angle = i * 60
                dx = hex_size * 0.5 * np.cos(np.radians(angle))
                dy = hex_size * 0.5 * np.sin(np.radians(angle))
                hex_coords.append([lon + dx, lat + dy])
            
            # Ensure the polygon is closed
            if hex_coords[0] != hex_coords[-1]:
                hex_coords.append(hex_coords[0])
            
            # Create polygon
            try:
                polygon = Polygon(hex_coords)
                if polygon.is_valid:
                    hexagons.append({
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': [hex_coords]
                        },
                        'properties': {
                            'id': f'hex_{hex_id}',
                            'lat': lat,
                            'lon': lon,
                            'hex_size': hex_size
                        }
                    })
                    hex_id += 1
            except Exception as e:
                print(f"Error creating hexagon at {lat}, {lon}: {e}")
                continue
    
    return {
        'type': 'FeatureCollection',
        'features': hexagons
    }

def add_lcoh_data(hexagons):
    """Add realistic LCOH data to hexagons with better distribution"""
    
    for feature in hexagons['features']:
        lat = feature['properties']['lat']
        lon = feature['properties']['lon']
        
        # Generate more realistic LCOH values with better distribution
        base_cost_pipeline = 150  # Reduced base cost
        base_cost_trucking = 250  # Reduced base cost
        
        # Distance factor from center of India (more realistic)
        center_lat, center_lon = 23.5937, 78.9629  # Center of India
        distance = np.sqrt((lat - center_lat)**2 + (lon - center_lon)**2)
        distance_factor = distance * 5  # Reduced multiplier
        
        # Renewable potential factor (higher in certain regions)
        # Southern India (better solar), Western India (better wind)
        if lat < 20:  # Southern India
            renewable_factor = 30  # Better renewable potential
        elif lon < 75:  # Western India
            renewable_factor = 25  # Good wind potential
        else:
            renewable_factor = 15  # Moderate potential
        
        # Random variation (reduced for more realistic values)
        random_factor = (np.random.random() - 0.5) * 40
        
        # Calculate LCOH for different cities with better distribution
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
        
        for city in cities:
            # City-specific adjustments
            if city == 'Mumbai':
                city_lat, city_lon = 19.0760, 72.8777
                city_bonus = -20  # Mumbai gets cost advantage
            elif city == 'Delhi':
                city_lat, city_lon = 28.7041, 77.1025
                city_bonus = -15  # Delhi gets slight advantage
            elif city == 'Bangalore':
                city_lat, city_lon = 12.9716, 77.5946
                city_bonus = -25  # Bangalore gets good advantage
            elif city == 'Chennai':
                city_lat, city_lon = 13.0827, 80.2707
                city_bonus = -10  # Chennai gets slight advantage
            elif city == 'Kolkata':
                city_lat, city_lon = 22.5726, 88.3639
                city_bonus = -5  # Kolkata gets minimal advantage
            
            # Distance from city
            city_distance = np.sqrt((lat - city_lat)**2 + (lon - city_lon)**2)
            city_factor = city_distance * 8  # Reduced multiplier
            
            # Pipeline LCOH (more realistic range)
            pipeline_lcoh = base_cost_pipeline + distance_factor + renewable_factor + city_factor + random_factor + city_bonus
            pipeline_lcoh = max(80, min(400, pipeline_lcoh))  # Better range
            
            # Trucking LCOH (higher than pipeline but realistic)
            trucking_lcoh = base_cost_trucking + distance_factor + renewable_factor + city_factor + random_factor + city_bonus
            trucking_lcoh = max(150, min(500, trucking_lcoh))  # Better range
            
            # Add to properties
            feature['properties'][f'{city} pipeline LCOH'] = round(pipeline_lcoh, 2)
            feature['properties'][f'{city} trucking LCOH'] = round(trucking_lcoh, 2)
    
    return hexagons

def main():
    """Main function"""
    print("🔧 Fixing India hexagon data with better coverage...")
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "Data"
    output_dir.mkdir(exist_ok=True)
    
    # Generate clean hexagons
    print("📐 Creating valid hexagon grid with better coverage...")
    hexagons = create_valid_hexagons()
    
    # Add LCOH data
    print("💰 Adding realistic LCOH data...")
    hexagons_with_lcoh = add_lcoh_data(hexagons)
    
    # Save clean hexagons
    print("💾 Saving improved hexagons...")
    with open(output_dir / "india_hexagons_clean.geojson", 'w') as f:
        json.dump(hexagons, f, indent=2)
    
    # Save hexagons with LCOH
    with open(output_dir / "india_hexagons_with_lcoh_clean.geojson", 'w') as f:
        json.dump(hexagons_with_lcoh, f, indent=2)
    
    print(f"✅ Created {len(hexagons['features'])} valid hexagons with better coverage")
    print(f"📁 Files saved:")
    print(f"   - {output_dir / 'india_hexagons_clean.geojson'}")
    print(f"   - {output_dir / 'india_hexagons_with_lcoh_clean.geojson'}")
    print("🎨 LCOH values now range from 80-500 ₹/kg for better color distribution")

if __name__ == "__main__":
    main()
