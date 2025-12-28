"""
Simple Rule-Based Change Detector
Does NOT depend on TensorFlow.
"""
import numpy as np
from scipy import ndimage
from scipy.ndimage import gaussian_filter

def create_simple_change_detector():
    """
    Create a simple rule-based change detector as fallback
    Uses NDVI differencing for quick baseline results
    """
    def detect_changes(before_rgb: np.ndarray, after_rgb: np.ndarray) -> np.ndarray:
        """
        Simple change detection using color differences
        
        Args:
            before_rgb: Before image (H, W, 3)
            after_rgb: After image (H, W, 3)
            
        Returns:
            Change probability map (H, W)
        """
        # Calculate vegetation index approximation from RGB
        # Green - Red as proxy for vegetation
        def vegetation_index(rgb):
            green = rgb[:, :, 1].astype(np.float32)
            red = rgb[:, :, 0].astype(np.float32)
            return (green - red) / (green + red + 1e-8)
        
        vi_before = vegetation_index(before_rgb)
        vi_after = vegetation_index(after_rgb)
        
        # Calculate change (negative = vegetation loss)
        change = vi_after - vi_before
        
        # Convert to probability (more negative = higher deforestation probability)
        prob = np.clip(-change * 2, 0, 1)
        
        # Apply some smoothing
        prob = gaussian_filter(prob, sigma=2)
        
        return prob
    
    return detect_changes
