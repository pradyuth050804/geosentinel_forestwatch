"""
KML Boundary Processing Service
Parses Shankar SF.kml and extracts forest boundary geometry
"""
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import transform
import geopandas as gpd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class KMLProcessor:
    """Process KML files to extract boundary geometries"""
    
    def __init__(self, kml_path: Path):
        self.kml_path = kml_path
        self.geometry = None
        self.bounds = None
        self.area_m2 = None
        
    def parse(self):
        """Parse KML file and extract polygon geometry"""
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
            outer_coords = self._parse_coordinates(coordinates_elements[0].text)
            
            # Parse inner boundaries (holes) if present
            holes = []
            if len(coordinates_elements) > 1:
                for coord_elem in coordinates_elements[1:]:
                    hole_coords = self._parse_coordinates(coord_elem.text)
                    holes.append(hole_coords)
            
            # Create Shapely polygon
            if holes:
                self.geometry = Polygon(outer_coords, holes=holes)
            else:
                self.geometry = Polygon(outer_coords)
            
            # Validate geometry
            if not self.geometry.is_valid:
                logger.warning("Invalid geometry detected, attempting to fix...")
                self.geometry = self.geometry.buffer(0)
            
            # Calculate bounds and area
            self.bounds = self.geometry.bounds  # (minx, miny, maxx, maxy)
            
            # Calculate area in square meters (approximate for lat/lon)
            # For accurate area, we need to project to UTM
            gdf = gpd.GeoDataFrame([1], geometry=[self.geometry], crs="EPSG:4326")
            gdf_utm = gdf.to_crs(gdf.estimate_utm_crs())
            self.area_m2 = gdf_utm.geometry.area.iloc[0]
            
            logger.info(f"Parsed KML: {len(outer_coords)} outer points, {len(holes)} holes")
            logger.info(f"Bounds: {self.bounds}")
            logger.info(f"Area: {self.area_m2:.2f} m² ({self.area_m2/10000:.2f} hectares)")
            
            return self.geometry
            
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
    
    def to_geojson(self):
        """Convert geometry to GeoJSON format"""
        if self.geometry is None:
            raise ValueError("No geometry loaded. Call parse() first.")
        
        gdf = gpd.GeoDataFrame([1], geometry=[self.geometry], crs="EPSG:4326")
        return gdf.__geo_interface__
    
    def to_wkt(self):
        """Convert geometry to WKT format"""
        if self.geometry is None:
            raise ValueError("No geometry loaded. Call parse() first.")
        
        return self.geometry.wkt
    
    def get_bbox(self):
        """Get bounding box as (min_lon, min_lat, max_lon, max_lat)"""
        if self.bounds is None:
            raise ValueError("No bounds calculated. Call parse() first.")
        
        return self.bounds
    
    def get_center(self):
        """Get centroid of the polygon"""
        if self.geometry is None:
            raise ValueError("No geometry loaded. Call parse() first.")
        
        centroid = self.geometry.centroid
        return (centroid.x, centroid.y)
    
    def contains_point(self, lon: float, lat: float):
        """Check if a point is within the boundary"""
        if self.geometry is None:
            raise ValueError("No geometry loaded. Call parse() first.")
        
        from shapely.geometry import Point
        point = Point(lon, lat)
        return self.geometry.contains(point)


if __name__ == "__main__":
    # Test the KML processor
    logging.basicConfig(level=logging.INFO)
    
    from pathlib import Path
    kml_path = Path(__file__).parent.parent.parent / "Shankar SF.kml"
    
    processor = KMLProcessor(kml_path)
    geometry = processor.parse()
    
    print(f"\nGeometry type: {geometry.geom_type}")
    print(f"Bounding box: {processor.get_bbox()}")
    print(f"Center: {processor.get_center()}")
    print(f"Area: {processor.area_m2/10000:.2f} hectares")
    print(f"\nWKT (first 200 chars): {processor.to_wkt()[:200]}...")
