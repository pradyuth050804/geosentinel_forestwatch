"""
Simplified KML Processor (No GDAL/Rasterio Required)
Uses only standard libraries and shapely
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)

class KMLProcessor:
    """Process KML files to extract boundary geometries (simplified version)"""
    
    def __init__(self, kml_path: Path):
        self.kml_path = kml_path
        self.coordinates = []
        self.bounds = None
        self.area_m2 = None
        
    def parse(self):
        """Parse KML file and extract polygon coordinates"""
        try:
            tree = ET.parse(self.kml_path)
            root = tree.getroot()
            
            # Define KML namespace
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            # Find all coordinate elements
            coordinates_elements = root.findall('.//kml:coordinates', ns)
            
            if not coordinates_elements:
                raise ValueError("No coordinates found in KML file")
            
            # Parse outer boundary (first coordinates element)
            self.coordinates = self._parse_coordinates(coordinates_elements[0].text)
            
            # Calculate bounds
            lons = [coord[0] for coord in self.coordinates]
            lats = [coord[1] for coord in self.coordinates]
            
            self.bounds = (min(lons), min(lats), max(lons), max(lats))
            
            # Approximate area calculation (simple method)
            # For accurate area, would need proper projection
            self.area_m2 = self._approximate_area()
            
            logger.info(f"Parsed KML: {len(self.coordinates)} points")
            logger.info(f"Bounds: {self.bounds}")
            logger.info(f"Approximate area: {self.area_m2/10000:.2f} hectares")
            
            return self.coordinates
            
        except Exception as e:
            logger.error(f"Error parsing KML: {e}")
            raise
    
    def _parse_coordinates(self, coord_text: str):
        """Parse coordinate string from KML into list of (lon, lat) tuples"""
        coords = []
        for coord_str in coord_text.strip().split():
            parts = coord_str.split(',')
            if len(parts) >= 2:
                lon, lat = float(parts[0]), float(parts[1])
                coords.append((lon, lat))
        return coords
    
    def _approximate_area(self):
        """Approximate area in square meters (simple method)"""
        if len(self.coordinates) < 3:
            return 0
        
        # Shoelace formula for area (approximate for lat/lon)
        area = 0
        n = len(self.coordinates)
        
        for i in range(n):
            j = (i + 1) % n
            area += self.coordinates[i][0] * self.coordinates[j][1]
            area -= self.coordinates[j][0] * self.coordinates[i][1]
        
        area = abs(area) / 2.0
        
        # Convert from degrees² to m² (very rough approximation)
        # At ~14°N latitude, 1 degree ≈ 111km
        meters_per_degree = 111000
        area_m2 = area * (meters_per_degree ** 2)
        
        return area_m2
    
    def get_bbox(self):
        """Get bounding box as (min_lon, min_lat, max_lon, max_lat)"""
        if self.bounds is None:
            raise ValueError("No bounds calculated. Call parse() first.")
        return self.bounds
    
    def get_center(self):
        """Get centroid of the polygon"""
        if not self.coordinates:
            raise ValueError("No coordinates loaded. Call parse() first.")
        
        lons = [coord[0] for coord in self.coordinates]
        lats = [coord[1] for coord in self.coordinates]
        
        return (sum(lons) / len(lons), sum(lats) / len(lats))
    
    def to_dict(self):
        """Export as dictionary"""
        return {
            "coordinates": self.coordinates,
            "bounds": self.bounds,
            "area_m2": self.area_m2,
            "area_hectares": self.area_m2 / 10000 if self.area_m2 else 0
        }


if __name__ == "__main__":
    # Test the KML processor
    logging.basicConfig(level=logging.INFO)
    
    from pathlib import Path
    kml_path = Path(__file__).parent.parent.parent / "Shankar SF.kml"
    
    processor = KMLProcessor(kml_path)
    coords = processor.parse()
    
    print(f"\nCoordinates: {len(coords)} points")
    print(f"Bounding box: {processor.get_bbox()}")
    print(f"Center: {processor.get_center()}")
    print(f"Area: {processor.area_m2/10000:.2f} hectares")
