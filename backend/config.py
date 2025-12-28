"""
Configuration management for GeoSentinel Forest Watch
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = DATA_DIR / "outputs"
KML_FILE = BASE_DIR / "Shankar SF.kml"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
COPERNICUS_USERNAME = os.getenv("COPERNICUS_USERNAME", "")
COPERNICUS_PASSWORD = os.getenv("COPERNICUS_PASSWORD", "")
SENTINEL_HUB_CLIENT_ID = os.getenv("SENTINEL_HUB_CLIENT_ID", "")
SENTINEL_HUB_CLIENT_SECRET = os.getenv("SENTINEL_HUB_CLIENT_SECRET", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Flask Configuration
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
# Render/Heroku use PORT, local uses FLASK_PORT or 5000
FLASK_PORT = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))

# Processing Parameters
MAX_CLOUD_COVER = float(os.getenv("MAX_CLOUD_COVER", 20))
IMAGE_RESOLUTION = int(os.getenv("IMAGE_RESOLUTION", 10))  # meters per pixel
DEFORESTATION_THRESHOLD = float(os.getenv("DEFORESTATION_THRESHOLD", 0.5))

# Sentinel-2 Band Configuration
SENTINEL_BANDS = {
    "B02": "Blue",
    "B03": "Green", 
    "B04": "Red",
    "B08": "NIR"
}

# Output file names
OUTPUT_FILES = {
    "before_image": "forest_Tprev.png",
    "after_image": "forest_T0.png",
    "highlight_image": "deforestation_highlight.png",
    "probability_map": "deforestation_probability.npy",
    "binary_mask": "deforestation_mask.npy",
    "metrics": "metrics.json"
}

# TensorFlow Model Configuration
MODEL_PATH = BASE_DIR / "backend" / "ml" / "models" / "deforestation_model.h5"
MODEL_INPUT_SIZE = 256
BATCH_SIZE = 8

# Visualization Colors (RGBA)
COLORS = {
    "deforestation": (255, 0, 0, 200),      # Red with ~80% opacity (Strong indicator)
    "degradation": (255, 255, 0, 100),      # Yellow with ~40% opacity (Subtle)
    "intact": (0, 0, 0, 0),                 # Transparent (Show original image)
    "boundary": (255, 255, 255, 255)        # White boundary
}

# Probability thresholds for classification
PROBABILITY_THRESHOLDS = {
    "deforestation": 0.7,
    "degradation": 0.4
}

def validate_config():
    """Validate that required configuration is present"""
    errors = []
    
    if not KML_FILE.exists():
        errors.append(f"KML file not found: {KML_FILE}")
    
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY not set in environment")
    
    if not (COPERNICUS_USERNAME and COPERNICUS_PASSWORD) and \
       not (SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET):
        errors.append("No Sentinel API credentials configured")
    
    return errors

if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration valid!")
