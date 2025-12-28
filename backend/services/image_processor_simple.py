"""
Simplified Image Processor (No Rasterio Required)
Uses PIL and OpenCV for image processing
"""
import numpy as np
from PIL import Image
# import cv2  <-- Removed to save memory (unused)
from pathlib import Path
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Process images for deforestation detection (simplified version)"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_and_resize(self, image_path: Path, target_size: Tuple[int, int] = None) -> np.ndarray:
        """Load image and optionally resize"""
        img = Image.open(image_path).convert('RGB')
        
        if target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        return np.array(img)
    
    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Normalize image to 0-1 range"""
        if image.dtype == np.uint8:
            return image.astype(np.float32) / 255.0
        return image
    
    def apply_contrast_stretch(self, 
                               image_array: np.ndarray,
                               percentile_low: float = 2,
                               percentile_high: float = 98) -> np.ndarray:
        """Apply contrast stretching for better visualization"""
        stretched = np.zeros_like(image_array, dtype=np.float32)
        
        for i in range(image_array.shape[2]):
            channel = image_array[:, :, i]
            p_low = np.percentile(channel, percentile_low)
            p_high = np.percentile(channel, percentile_high)
            
            stretched[:, :, i] = np.clip(
                (channel - p_low) / (p_high - p_low + 1e-8),
                0, 1
            )
        
        return stretched
    
    def save_image(self, image_array: np.ndarray, output_path: Path):
        """Save image array as PNG"""
        # Ensure 0-1 range
        if image_array.max() <= 1.0:
            image_array = (image_array * 255).astype(np.uint8)
        else:
            image_array = image_array.astype(np.uint8)
        
        img = Image.fromarray(image_array, mode='RGB')
        img.save(output_path, 'PNG')
        logger.info(f"Saved image: {output_path}")
    
    def process_image_pair(self,
                           before_path: Path,
                           after_path: Path,
                           output_before_png: Path,
                           output_after_png: Path) -> Tuple[Path, Path]:
        """Process image pair for analysis"""
        logger.info("Processing image pair...")
        
        # Load images
        before = self.load_and_resize(before_path)
        after = self.load_and_resize(after_path)
        
        # Ensure same size
        target_size = before.shape[:2]
        if after.shape[:2] != target_size:
            after_pil = Image.fromarray(after)
            after_pil = after_pil.resize((target_size[1], target_size[0]), Image.Resampling.LANCZOS)
            after = np.array(after_pil)
        
        # Normalize
        before_norm = self.normalize_image(before)
        after_norm = self.normalize_image(after)
        
        # Apply contrast stretching
        before_stretched = self.apply_contrast_stretch(before_norm)
        after_stretched = self.apply_contrast_stretch(after_norm)
        
        # Save
        self.save_image(before_stretched, output_before_png)
        self.save_image(after_stretched, output_after_png)
        
        logger.info("Image pair processing complete!")
        return output_before_png, output_after_png


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Simplified ImageProcessor ready for use")
