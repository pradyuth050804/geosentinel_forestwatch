"""
Check the actual percentile values in the GeoTIFF to understand the data distribution
"""
import rasterio
import numpy as np
from pathlib import Path

cache_dir = Path("d:/KeyFalcon/geosentinelforestwatch/data/cache")

# Find a recent GeoTIFF
tif_files = sorted(cache_dir.glob("sentinel2_*.tif"), key=lambda x: x.stat().st_mtime, reverse=True)

if tif_files:
    tif_path = tif_files[0]
    print(f"Analyzing: {tif_path.name}\n")
    
    with rasterio.open(tif_path) as src:
        # Read RGB bands
        red = src.read(1)
        green = src.read(2)
        blue = src.read(3)
        
        rgb = np.dstack([red, green, blue])
        
        print(f"Data type: {rgb.dtype}")
        print(f"Shape: {rgb.shape}")
        print(f"\nOverall statistics:")
        print(f"  Min: {rgb.min()}")
        print(f"  Max: {rgb.max()}")
        print(f"  Mean: {rgb.mean():.2f}")
        print(f"  Median: {np.median(rgb):.2f}")
        
        print(f"\nPercentiles:")
        for p in [1, 2, 5, 10, 25, 50, 75, 90, 95, 98, 99]:
            val = np.percentile(rgb, p)
            print(f"  {p:3d}%: {val:8.2f}")
        
        print(f"\nPer-channel percentiles (2% and 98%):")
        for i, name in enumerate(['Red', 'Green', 'Blue']):
            channel = rgb[:,:,i]
            p2 = np.percentile(channel, 2)
            p98 = np.percentile(channel, 98)
            print(f"  {name:5s}: {p2:8.2f} to {p98:8.2f} (range: {p98-p2:8.2f})")
