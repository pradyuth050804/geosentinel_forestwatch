"""
Image Processing Pipeline
Handles clipping, normalization, and PNG conversion of satellite imagery
"""
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from PIL import Image
from pathlib import Path
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Process satellite imagery for deforestation detection"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def clip_to_boundary(self, 
                         image_path: Path, 
                         geometry,
                         output_path: Optional[Path] = None) -> Path:
        """
        Clip raster image to polygon boundary
        
        Args:
            image_path: Path to input GeoTIFF
            geometry: Shapely geometry to clip to (Lat/Lon EPSG:4326)
            output_path: Optional output path
            
        Returns:
            Path to clipped image
        """
        if output_path is None:
            output_path = self.output_dir / f"clipped_{image_path.name}"
        
        try:
            with rasterio.open(image_path) as src:
                # Reproject geometry to match image CRS
                if src.crs != 'EPSG:4326':
                    import pyproj
                    from shapely.ops import transform
                    
                    project = pyproj.Transformer.from_crs(
                        'EPSG:4326', src.crs, always_xy=True
                    ).transform
                    
                    projected_geometry = transform(project, geometry)
                else:
                    projected_geometry = geometry
                
                # Clip the raster
                out_image, out_transform = rio_mask(
                    src, 
                    [projected_geometry], 
                    crop=True,
                    all_touched=True
                )
                
                # Update metadata
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })
                
                # Write clipped image
                with rasterio.open(output_path, "w", **out_meta) as dest:
                    dest.write(out_image)
                
                logger.info(f"Clipped image to boundary: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error clipping image: {e}")
            raise
    
    def normalize_reflectance(self, image_array: np.ndarray) -> np.ndarray:
        """
        Normalize reflectance values to 0-1 range
        
        Args:
            image_array: Input array (bands, height, width)
            
        Returns:
            Normalized array
        """
        # Sentinel-2 L2A reflectance values are typically 0-10000
        # Normalize to 0-1
        normalized = image_array.astype(np.float32) / 10000.0
        normalized = np.clip(normalized, 0, 1)
        
        return normalized
    
    def apply_contrast_stretch(self, 
                               image_array: np.ndarray,
                               percentile_low: float = 2,
                               percentile_high: float = 98) -> np.ndarray:
        """
        Apply contrast stretching for better visualization
        
        Args:
            image_array: Input array (height, width, channels)
            percentile_low: Lower percentile for stretching
            percentile_high: Upper percentile for stretching
            
        Returns:
            Contrast-stretched array
        """
    def apply_contrast_stretch(self, 
                             image_array: np.ndarray, 
                             percentile_low: float = 1, 
                             percentile_high: float = 99) -> np.ndarray:
        """
        Apply percentile stretch with nodata masking
        Ignores black edges (nodata) and stretches only valid pixels
        """
        # Convert to float
        img = image_array.astype(np.float32)
        stretched = np.zeros_like(img)
        
        # Create mask for valid (non-zero) pixels
        # Sum across channels - if all channels are 0, it's nodata
        valid_mask = np.sum(img, axis=2) > 0
        
        # Process each channel
        for i in range(img.shape[2]):
            channel = img[:, :, i]
            
            # Get only valid pixels for percentile calculation
            valid_pixels = channel[valid_mask]
            
            if len(valid_pixels) > 0:
                p_low = np.percentile(valid_pixels, percentile_low)
                p_high = np.percentile(valid_pixels, percentile_high)
                
                if p_high - p_low > 0:
                    stretched[:, :, i] = np.clip(
                        (channel - p_low) / (p_high - p_low),
                        0, 1
                    )
                else:
                    stretched[:, :, i] = channel / (p_high + 1e-6)
            else:
                stretched[:, :, i] = 0
        
        # Keep nodata areas black
        stretched[~valid_mask] = 0
        
        # Apply gamma correction to brighten (gamma 1.3)
        stretched = np.power(stretched, 1.0/1.3)
        stretched[~valid_mask] = 0  # Keep edges black after gamma
        
        return stretched
    
    def geotiff_to_png(self, 
                       geotiff_path: Path,
                       output_path: Path,
                       apply_stretch: bool = True) -> Path:
        """
        Convert GeoTIFF to PNG for visualization and ML input
        
        Args:
            geotiff_path: Path to input GeoTIFF
            output_path: Path for output PNG
            apply_stretch: Whether to apply contrast stretching
            
        Returns:
            Path to created PNG
        """
        try:
            with rasterio.open(geotiff_path) as src:
                # Read RGB bands (assuming bands 1, 2, 3 are R, G, B)
                if src.count >= 3:
                    red = src.read(1)
                    green = src.read(2)
                    blue = src.read(3)
                else:
                    raise ValueError(f"Image has only {src.count} bands, need at least 3")
                
                # Stack bands
                rgb = np.dstack([red, green, blue])
                
                # Normalization is now handled robustly in apply_contrast_stretch
                # to support both DN and Reflectance inputs properly.
                # Normalization is now handled robustly in apply_contrast_stretch
                # to support both DN and Reflectance inputs properly.
                
                # Apply contrast stretching
                if apply_stretch:
                    rgb = self.apply_contrast_stretch(rgb)
                
                # Convert to 8-bit
                rgb_8bit = (rgb * 255).astype(np.uint8)
                
                # Create PIL Image and save
                img = Image.fromarray(rgb_8bit, mode='RGB')
                img.save(output_path, 'PNG')
                
                logger.info(f"Converted to PNG: {output_path}")
                logger.info(f"Image size: {img.size}")
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error converting to PNG: {e}")
            raise
    
    def ensure_same_dimensions(self, 
                               image1_path: Path,
                               image2_path: Path) -> Tuple[Path, Path]:
        """
        Ensure two images have identical dimensions and alignment
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            
        Returns:
            Tuple of paths to aligned images
        """
        with rasterio.open(image1_path) as src1, rasterio.open(image2_path) as src2:
            # Check if already aligned
            if (src1.shape == src2.shape and 
                src1.bounds == src2.bounds and
                src1.crs == src2.crs):
                logger.info("Images already aligned")
                return image1_path, image2_path
            
            # Reproject image2 to match image1
            logger.info("Aligning images...")
            
            aligned_path = self.output_dir / f"aligned_{image2_path.name}"
            
            with rasterio.open(
                aligned_path,
                'w',
                driver='GTiff',
                height=src1.height,
                width=src1.width,
                count=src2.count,
                dtype=src2.dtypes[0],
                crs=src1.crs,
                transform=src1.transform
            ) as dst:
                for i in range(1, src2.count + 1):
                    reproject(
                        source=rasterio.band(src2, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src2.transform,
                        src_crs=src2.crs,
                        dst_transform=src1.transform,
                        dst_crs=src1.crs,
                        resampling=Resampling.bilinear
                    )
            
            return image1_path, aligned_path
    
    def process_image_pair(self,
                           before_path: Path,
                           after_path: Path,
                           geometry,
                           output_before_png: Path,
                           output_after_png: Path) -> Tuple[Path, Path]:
        """
        Complete processing pipeline for image pair
        
        Args:
            before_path: Path to before GeoTIFF
            after_path: Path to after GeoTIFF
            geometry: Boundary geometry
            output_before_png: Output path for before PNG
            output_after_png: Output path for after PNG
            
        Returns:
            Tuple of (before_png_path, after_png_path)
        """
        logger.info("Starting image pair processing...")
        
        # Step 1: Clip to boundary
        logger.info("Clipping images to boundary...")
        clipped_before = self.clip_to_boundary(before_path, geometry)
        clipped_after = self.clip_to_boundary(after_path, geometry)
        
        # Step 2: Ensure same dimensions
        logger.info("Aligning images...")
        aligned_before, aligned_after = self.ensure_same_dimensions(
            clipped_before, clipped_after
        )
        
        # Step 3: Convert to PNG
        logger.info("Converting to PNG...")
        png_before = self.geotiff_to_png(aligned_before, output_before_png)
        png_after = self.geotiff_to_png(aligned_after, output_after_png)
        
        logger.info("Image pair processing complete!")
        return png_before, png_after


if __name__ == "__main__":
    # Test the processor
    logging.basicConfig(level=logging.INFO)
    
    from pathlib import Path
    from shapely.geometry import box
    
    # This would be used with real data
    print("ImageProcessor ready for use")
