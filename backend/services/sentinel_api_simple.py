"""
Simplified Sentinel API (Mock Data Only)
No sentinelsat dependency required
"""
import numpy as np
from PIL import Image
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SentinelImageRetriever:
    """Generate mock Sentinel-2 imagery (simplified version)"""
    
    def __init__(self, username: str = "", password: str = "", cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Using mock data generator (no API connection)")
    
    def create_mock_image(self, 
                          date: str,
                          output_path: Path,
                          is_deforested: bool = False,
                          width: int = 512,
                          height: int = 512) -> Path:
        """Create a mock forest image"""
        logger.info(f"Creating mock image for {date}")
        
        # Base forest color (green)
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:, :, 1] = 120  # Green channel
        img[:, :, 0] = 40   # Red channel
        img[:, :, 2] = 30   # Blue channel
        
        # Add texture
        noise = np.random.randint(-20, 20, (height, width, 3), dtype=np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Add deforestation if requested
        if is_deforested:
            num_patches = np.random.randint(5, 12)
            for _ in range(num_patches):
                x = np.random.randint(0, width - 100)
                y = np.random.randint(0, height - 100)
                w = np.random.randint(40, 120)
                h = np.random.randint(40, 120)
                
                # Brown color for cleared land
                img[y:y+h, x:x+w, 0] = 139  # Red
                img[y:y+h, x:x+w, 1] = 90   # Green
                img[y:y+h, x:x+w, 2] = 43   # Blue
        
        # Save as PNG
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pil_img = Image.fromarray(img, 'RGB')
        pil_img.save(output_path, 'PNG')
        
        logger.info(f"Mock image created: {output_path}")
        return output_path
    
    def get_image_for_date(self, 
                           date: str,
                           is_deforested: bool = False) -> Path:
        """Get mock image for a specific date"""
        date_str = date.replace("-", "")
        cache_file = self.cache_dir / f"sentinel2_{date_str}.png"
        
        if cache_file.exists():
            logger.info(f"Using cached image: {cache_file}")
            return cache_file
        
        return self.create_mock_image(date, cache_file, is_deforested)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    retriever = SentinelImageRetriever()
    before = retriever.get_image_for_date("2023-01-01", is_deforested=False)
    after = retriever.get_image_for_date("2024-01-01", is_deforested=True)
    
    print(f"Before image: {before}")
    print(f"After image: {after}")
