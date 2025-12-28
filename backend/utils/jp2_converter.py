"""
Convert JP2 bands to GeoTIFF using GDAL
"""
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def convert_jp2_to_geotiff(jp2_file: Path, output_file: Path) -> Path:
    """
    Convert JP2 file to GeoTIFF using gdal_translate
    
    Args:
        jp2_file: Path to JP2 file
        output_file: Path for output GeoTIFF
        
    Returns:
        Path to created GeoTIFF
    """
    logger.info(f"Converting {jp2_file.name} to GeoTIFF...")
    
    cmd = [
        'gdal_translate',
        '-of', 'GTiff',
        '-co', 'COMPRESS=LZW',
        str(jp2_file),
        str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info(f"Successfully converted to {output_file.name}")
            return output_file
        else:
            logger.error(f"gdal_translate failed: {result.stderr}")
            raise RuntimeError(f"Failed to convert JP2: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("gdal_translate timed out")
        raise
    except FileNotFoundError:
        logger.error("gdal_translate not found. Make sure GDAL is installed.")
        raise
