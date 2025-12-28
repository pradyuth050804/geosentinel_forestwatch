"""
Change Detection Orchestrator
High-level interface for deforestation detection workflow
"""
import numpy as np
from PIL import Image
from pathlib import Path
import logging
from typing import Tuple, Dict
import json
from scipy import ndimage

from backend.ml.deforestation_model import DeforestationModel, create_simple_change_detector

logger = logging.getLogger(__name__)

class ChangeDetector:
    """Orchestrates the complete change detection workflow"""
    
    def __init__(self, 
                 model_path: Path = None,
                 use_simple_detector: bool = False,
                 threshold: float = 0.5):
        """
        Initialize change detector
        
        Args:
            model_path: Path to trained model (optional)
            use_simple_detector: Use rule-based detector instead of ML
            threshold: Threshold for binary classification
        """
        self.threshold = threshold
        self.use_simple = use_simple_detector
        
        if use_simple_detector:
            logger.info("Using simple rule-based change detector")
            self.detector = create_simple_change_detector()
            self.model = None
        else:
            logger.info("Using TensorFlow model")
            self.model = DeforestationModel(model_path=model_path)
            self.detector = None
    
    def load_image(self, image_path: Path) -> np.ndarray:
        """Load and normalize image"""
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img).astype(np.float32) / 255.0
        return img_array
    
    def detect_changes(self, 
                       before_image_path: Path,
                       after_image_path: Path) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect changes between two images
        
        Args:
            before_image_path: Path to before image (PNG)
            after_image_path: Path to after image (PNG)
            
        Returns:
            Tuple of (probability_map, binary_mask)
        """
        logger.info("Loading images...")
        before = self.load_image(before_image_path)
        after = self.load_image(after_image_path)
        
        # Ensure same dimensions
        if before.shape != after.shape:
            raise ValueError(f"Image dimensions don't match: {before.shape} vs {after.shape}")
        
        logger.info(f"Image shape: {before.shape}")
        
        # Run detection
        if self.use_simple:
            logger.info("Running simple change detection...")
            prob_map = self.detector(before, after)
        else:
            logger.info("Running TensorFlow model inference...")
            prob_map = self.model.predict(before, after)
        
        # Create binary mask
        binary_mask = (prob_map > self.threshold).astype(np.uint8)
        
        # Post-processing: remove small noise
        binary_mask = self.remove_small_objects(binary_mask, min_size=50)
        
        logger.info(f"Detection complete. Deforestation pixels: {binary_mask.sum()}")
        
        return prob_map, binary_mask
    
    def remove_small_objects(self, binary_mask: np.ndarray, min_size: int) -> np.ndarray:
        """Remove small connected components (noise)"""
        labeled, num_features = ndimage.label(binary_mask)
        
        for i in range(1, num_features + 1):
            component = (labeled == i)
            if component.sum() < min_size:
                binary_mask[component] = 0
        
        return binary_mask
    
    def calculate_metrics(self,
                          binary_mask: np.ndarray,
                          pixel_size_m: float,
                          total_area_m2: float) -> Dict:
        """
        Calculate deforestation metrics
        
        Args:
            binary_mask: Binary deforestation mask
            pixel_size_m: Size of one pixel in meters
            total_area_m2: Total forest boundary area in m²
            
        Returns:
            Dictionary of metrics
        """
        # Count deforested pixels
        deforested_pixels = binary_mask.sum()
        
        # Calculate area
        pixel_area_m2 = pixel_size_m ** 2
        deforested_area_m2 = deforested_pixels * pixel_area_m2
        deforested_area_ha = deforested_area_m2 / 10000
        
        # Calculate percentage
        percentage = (deforested_area_m2 / total_area_m2) * 100 if total_area_m2 > 0 else 0
        
        # Count patches (connected components)
        labeled, num_patches = ndimage.label(binary_mask)
        
        # Find largest patch
        largest_patch_size = 0
        if num_patches > 0:
            patch_sizes = [
                (labeled == i).sum() * pixel_area_m2 
                for i in range(1, num_patches + 1)
            ]
            largest_patch_size = max(patch_sizes) if patch_sizes else 0
        
        # Calculate intact forest
        total_pixels = binary_mask.size
        intact_pixels = total_pixels - deforested_pixels
        intact_area_m2 = intact_pixels * pixel_area_m2
        
        metrics = {
            "deforested_area_m2": float(deforested_area_m2),
            "deforested_area_hectares": float(deforested_area_ha),
            "forest_loss_percentage": float(percentage),
            "number_of_patches": int(num_patches),
            "largest_patch_m2": float(largest_patch_size),
            "largest_patch_hectares": float(largest_patch_size / 10000),
            "intact_forest_m2": float(intact_area_m2),
            "intact_forest_hectares": float(intact_area_m2 / 10000),
            "total_area_m2": float(total_area_m2),
            "total_area_hectares": float(total_area_m2 / 10000),
            "pixel_size_meters": float(pixel_size_m),
            "total_pixels": int(total_pixels),
            "deforested_pixels": int(deforested_pixels)
        }
        
        logger.info(f"Metrics calculated: {deforested_area_ha:.2f} ha deforested ({percentage:.2f}%)")
        
        return metrics
    
    def save_outputs(self,
                     prob_map: np.ndarray,
                     binary_mask: np.ndarray,
                     metrics: Dict,
                     output_dir: Path):
        """
        Save detection outputs
        
        Args:
            prob_map: Probability map
            binary_mask: Binary mask
            metrics: Metrics dictionary
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save probability map as numpy array
        prob_path = output_dir / "deforestation_probability.npy"
        np.save(prob_path, prob_map)
        logger.info(f"Saved probability map: {prob_path}")
        
        # Save binary mask as numpy array
        mask_path = output_dir / "deforestation_mask.npy"
        np.save(mask_path, binary_mask)
        logger.info(f"Saved binary mask: {mask_path}")
        
        # Save metrics as JSON
        metrics_path = output_dir / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Saved metrics: {metrics_path}")
        
        return prob_path, mask_path, metrics_path


if __name__ == "__main__":
    # Test change detector
    logging.basicConfig(level=logging.INFO)
    
    print("ChangeDetector ready for use")
