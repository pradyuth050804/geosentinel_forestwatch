"""
Quick Test Script for GeoSentinel Forest Watch
Tests the complete workflow with mock data
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.kml_processor import KMLProcessor
from backend.services.sentinel_api import SentinelImageRetriever
from backend.services.image_processor import ImageProcessor
from backend.ml.change_detector import ChangeDetector
from backend.services.visualization import DeforestationVisualizer
from backend.config import *

import logging
logging.basicConfig(level=logging.INFO)

def test_workflow():
    """Test the complete deforestation detection workflow"""
    
    print("=" * 60)
    print("GeoSentinel Forest Watch - System Test")
    print("=" * 60)
    
    # Step 1: Load KML
    print("\n[1/7] Loading KML boundary...")
    kml_processor = KMLProcessor(KML_FILE)
    geometry = kml_processor.parse()
    print(f"✓ Loaded boundary: {kml_processor.area_m2/10000:.2f} hectares")
    
    # Step 2: Retrieve mock imagery
    print("\n[2/7] Generating mock satellite imagery...")
    retriever = SentinelImageRetriever("", "", CACHE_DIR)
    
    before_geotiff = retriever.get_image_for_date(
        geometry, "2023-01-01", use_mock=True, is_deforested=False
    )
    after_geotiff = retriever.get_image_for_date(
        geometry, "2024-01-01", use_mock=True, is_deforested=True
    )
    print(f"✓ Created mock images")
    
    # Step 3: Process images
    print("\n[3/7] Processing images...")
    processor = ImageProcessor(OUTPUT_DIR)
    
    before_png = OUTPUT_DIR / "forest_Tprev.png"
    after_png = OUTPUT_DIR / "forest_T0.png"
    
    processor.process_image_pair(
        before_geotiff,
        after_geotiff,
        geometry,
        before_png,
        after_png
    )
    print(f"✓ Generated PNG images")
    
    # Step 4: Run detection
    print("\n[4/7] Running deforestation detection...")
    detector = ChangeDetector(use_simple_detector=True)
    
    prob_map, binary_mask = detector.detect_changes(before_png, after_png)
    print(f"✓ Detection complete")
    
    # Step 5: Calculate metrics
    print("\n[5/7] Calculating metrics...")
    metrics = detector.calculate_metrics(
        binary_mask,
        IMAGE_RESOLUTION,
        kml_processor.area_m2
    )
    print(f"✓ Metrics calculated")
    print(f"  - Deforested area: {metrics['deforested_area_hectares']:.2f} ha")
    print(f"  - Forest loss: {metrics['forest_loss_percentage']:.2f}%")
    print(f"  - Number of patches: {metrics['number_of_patches']}")
    
    # Step 6: Create visualization
    print("\n[6/7] Creating visualization...")
    visualizer = DeforestationVisualizer()
    
    highlight_png = OUTPUT_DIR / "deforestation_highlight.png"
    visualizer.create_highlight_image(
        after_png,
        prob_map,
        geometry,
        highlight_png
    )
    print(f"✓ Highlight image created")
    
    # Step 7: Save outputs
    print("\n[7/7] Saving outputs...")
    detector.save_outputs(prob_map, binary_mask, metrics, OUTPUT_DIR)
    print(f"✓ All outputs saved to: {OUTPUT_DIR}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE!")
    print("=" * 60)
    print(f"\nGenerated files:")
    print(f"  - {before_png}")
    print(f"  - {after_png}")
    print(f"  - {highlight_png}")
    print(f"  - {OUTPUT_DIR / 'metrics.json'}")
    print(f"\nYou can now start the API server with: python backend/api.py")

if __name__ == "__main__":
    test_workflow()
