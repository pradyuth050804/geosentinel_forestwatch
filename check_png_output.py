"""
Quick diagnostic to check what's in the PNG files
"""
import numpy as np
from PIL import Image
from pathlib import Path

output_dir = Path("d:/KeyFalcon/geosentinelforestwatch/data/outputs")

for png_file in output_dir.glob("*.png"):
    if "highlight" in png_file.name:
        continue
        
    img = Image.open(png_file)
    arr = np.array(img)
    
    print(f"\n{png_file.name}:")
    print(f"  Shape: {arr.shape}")
    print(f"  Dtype: {arr.dtype}")
    print(f"  Min: {arr.min()}")
    print(f"  Max: {arr.max()}")
    print(f"  Mean: {arr.mean():.2f}")
    print(f"  Unique values: {len(np.unique(arr))}")
    
    # Check if it's all white
    if arr.min() == 255 and arr.max() == 255:
        print("  ⚠️ IMAGE IS ALL WHITE (255)")
    elif arr.min() == arr.max():
        print(f"  ⚠️ IMAGE IS SOLID COLOR ({arr.min()})")
