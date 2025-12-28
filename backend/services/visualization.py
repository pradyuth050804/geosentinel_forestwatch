"""
Deforestation Visualization Service
Creates color-coded highlight images showing detected changes
"""
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
import logging
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

class DeforestationVisualizer:
    """Create visualization overlays for deforestation detection"""
    
    def __init__(self, colors: Dict = None):
        """
        Initialize visualizer
        
        Args:
            colors: Dictionary of RGBA colors for different classes
        """
        self.colors = colors or {
            "deforestation": (255, 0, 0, 153),      # Red with 60% opacity
            "degradation": (255, 255, 0, 128),      # Yellow with 50% opacity
            "intact": (0, 255, 0, 77),              # Green with 30% opacity
            "boundary": (255, 255, 255, 255)        # White boundary
        }
        
        self.thresholds = {
            "deforestation": 0.7,
            "degradation": 0.4
        }
    
    def create_highlight_image(self,
                               base_image_path: Path,
                               prob_map: np.ndarray,
                               geometry,
                               output_path: Path) -> Path:
        """
        Create deforestation highlight image (Image 3)
        
        Args:
            base_image_path: Path to after image (base layer)
            prob_map: Deforestation probability map (H, W)
            geometry: Forest boundary geometry
            output_path: Where to save highlight image
            
        Returns:
            Path to created image
        """
        logger.info("Creating deforestation highlight image...")
        
        # Load base image
        base_img = Image.open(base_image_path).convert('RGBA')
        width, height = base_img.size
        
        # Resize probability map to match image size if needed
        if prob_map.shape != (height, width):
            from scipy.ndimage import zoom
            zoom_factor = (height / prob_map.shape[0], width / prob_map.shape[1])
            prob_map = zoom(prob_map, zoom_factor, order=1)
        
        # Create overlay layer
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_array = np.array(overlay)
        
        # Color code based on probability
        # High probability (>0.7) = Red (deforestation)
        # Medium probability (0.4-0.7) = Yellow (degradation)
        # Low probability (<0.4) = Green (intact)
        
        deforestation_mask = prob_map > self.thresholds["deforestation"]
        degradation_mask = (prob_map > self.thresholds["degradation"]) & (prob_map <= self.thresholds["deforestation"])
        intact_mask = prob_map <= self.thresholds["degradation"]
        
        # Apply colors
        overlay_array[deforestation_mask] = self.colors["deforestation"]
        overlay_array[degradation_mask] = self.colors["degradation"]
        overlay_array[intact_mask] = self.colors["intact"]
        
        overlay = Image.fromarray(overlay_array, 'RGBA')
        
        # Composite base image with overlay
        result = Image.alpha_composite(base_img, overlay)
        
        # Draw boundary
        result = self.draw_boundary(result, geometry, width, height)
        
        # Convert back to RGB for saving as PNG
        result_rgb = result.convert('RGB')
        result_rgb.save(output_path, 'PNG')
        
        logger.info(f"Highlight image saved: {output_path}")
        return output_path
    
    def draw_boundary(self, 
                      image: Image.Image,
                      geometry,
                      img_width: int,
                      img_height: int) -> Image.Image:
        """
        Draw forest boundary on image
        
        Args:
            image: PIL Image
            geometry: Shapely geometry
            img_width: Image width
            img_height: Image height
            
        Returns:
            Image with boundary drawn
        """
        # Get bounds for coordinate transformation
        minx, miny, maxx, maxy = geometry.bounds
        
        def geo_to_pixel(lon, lat):
            """Convert geographic coordinates to pixel coordinates"""
            px = int((lon - minx) / (maxx - minx) * img_width)
            py = int((maxy - lat) / (maxy - miny) * img_height)  # Flip Y axis
            return (px, py)
        
        # Extract coordinates
        if hasattr(geometry, 'exterior'):
            # Polygon
            coords = list(geometry.exterior.coords)
            pixel_coords = [geo_to_pixel(lon, lat) for lon, lat in coords]
            
            # Draw boundary
            draw = ImageDraw.Draw(image)
            draw.line(pixel_coords, fill=self.colors["boundary"], width=3)
            
            # Draw holes if present
            for interior in geometry.interiors:
                hole_coords = list(interior.coords)
                hole_pixels = [geo_to_pixel(lon, lat) for lon, lat in hole_coords]
                draw.line(hole_pixels, fill=self.colors["boundary"], width=2)
        
        return image
    
    def create_legend(self, output_path: Path):
        """Create a legend image explaining the color coding"""
        legend_width = 300
        legend_height = 200
        
        legend = Image.new('RGBA', (legend_width, legend_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(legend)
        
        # Title
        draw.text((10, 10), "Deforestation Legend", fill=(0, 0, 0, 255))
        
        # Color boxes and labels
        items = [
            (self.colors["deforestation"], "Deforestation (>70%)"),
            (self.colors["degradation"], "Degradation (40-70%)"),
            (self.colors["intact"], "Intact Forest (<40%)"),
            (self.colors["boundary"], "Forest Boundary")
        ]
        
        y = 40
        for color, label in items:
            # Draw color box
            draw.rectangle([10, y, 40, y+20], fill=color, outline=(0, 0, 0, 255))
            # Draw label
            draw.text((50, y+5), label, fill=(0, 0, 0, 255))
            y += 35
        
        legend.save(output_path, 'PNG')
        logger.info(f"Legend saved: {output_path}")
        return output_path


if __name__ == "__main__":
    # Test visualizer
    logging.basicConfig(level=logging.INFO)
    
    print("DeforestationVisualizer ready for use")
