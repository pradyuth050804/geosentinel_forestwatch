"""
Flask REST API Server
Main entry point for the deforestation detection API
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import logging
import uuid
import threading
from datetime import datetime
import traceback
import sys
import os

# Add parent directory to path so we can import from backend package
sys.path.insert(0, str(Path(__file__).parent.parent))
os.chdir(Path(__file__).parent.parent)  # Change to project root
from backend.config import *
from backend.services.kml_processor import KMLProcessor
from backend.services.sentinel_api import SentinelImageRetriever
from backend.services.image_processor import ImageProcessor
from backend.ml.change_detector import ChangeDetector
from backend.services.visualization import DeforestationVisualizer
from backend.services.gemini_service import GeminiExplainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
# Allow CORS for all domains on all /api routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Job storage (in-memory for simplicity)
jobs = {}

class AnalysisJob:
    """Represents an analysis job"""
    def __init__(self, job_id, date_before, date_after):
        self.job_id = job_id
        self.date_before = date_before
        self.date_after = date_after
        self.status = "queued"
        self.progress = 0
        self.error = None
        self.results = None
        self.created_at = datetime.now()


def run_analysis(job_id: str, date_before: str, date_after: str):
    """
    Run complete deforestation analysis workflow
    
    Args:
        job_id: Unique job identifier
        date_before: Earlier date (YYYY-MM-DD)
        date_after: Later date (YYYY-MM-DD)
    """
    job = jobs[job_id]
    
    try:
        job.status = "processing"
        job.progress = 5
        
        # Step 1: Load KML boundary
        logger.info(f"[{job_id}] Loading KML boundary...")
        kml_processor = KMLProcessor(KML_FILE)
        geometry = kml_processor.parse()
        job.progress = 10
        
        # Step 2: Retrieve Sentinel imagery
        logger.info(f"[{job_id}] Retrieving Sentinel imagery...")
        retriever = SentinelImageRetriever(
            COPERNICUS_USERNAME,
            COPERNICUS_PASSWORD,
            CACHE_DIR
        )
        
        # Download REAL Sentinel-2 data from Copernicus (NO MOCK DATA)
        logger.info(f"[{job_id}] Downloading REAL Sentinel-2 imagery from Copernicus...")
        before_geotiff = retriever.get_image_for_date(geometry, date_before)
        job.progress = 25
        
        after_geotiff = retriever.get_image_for_date(geometry, date_after)
        job.progress = 40
        
        # Step 3: Setup output directory & Check cache
        logger.info(f"[{job_id}] Preparing output directory...")
        
        # Structure: output/analysis_YYYY-MM-DD_to_YYYY-MM-DD
        folder_name = f"analysis_{date_before}_to_{date_after}"
        job_dir = OUTPUT_DIR / folder_name
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if already processed (Cache)
        metrics_file = job_dir / "metrics.json"
        
        if metrics_file.exists():
            logger.info(f"[{job_id}] Found cached results in {folder_name}")
            try:
                import json
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                
                job.results = {
                    "metrics": metrics,
                    "explanation": "Loaded from cache (re-using existing analysis).",
                    "images": {
                        "before": f"/api/images/{folder_name}/{OUTPUT_FILES['before_image']}",
                        "after": f"/api/images/{folder_name}/{OUTPUT_FILES['after_image']}",
                        "highlight": f"/api/images/{folder_name}/{OUTPUT_FILES['highlight_image']}"
                    },
                    "dates": {"before": date_before, "after": date_after}
                }
                job.status = "completed"
                job.progress = 100
                return
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}, re-running.")

        # Not cached - Run Processing
        logger.info(f"[{job_id}] Processing images...")
        processor = ImageProcessor(job_dir)
        
        before_png = job_dir / OUTPUT_FILES["before_image"]
        after_png = job_dir / OUTPUT_FILES["after_image"]
        
        processor.process_image_pair(
            before_geotiff,
            after_geotiff,
            geometry,
            before_png,
            after_png
        )
        logger.info(f"[{job_id}] Processed pair: {before_geotiff.name} -> {before_png.name} | {after_geotiff.name} -> {after_png.name}")
        job.progress = 55
        
        # Step 4: Run deforestation detection
        logger.info(f"[{job_id}] Running deforestation detection...")
        detector = ChangeDetector(use_simple_detector=True, threshold=DEFORESTATION_THRESHOLD)
        
        prob_map, binary_mask = detector.detect_changes(before_png, after_png)
        job.progress = 70
        
        # Step 5: Calculate metrics
        logger.info(f"[{job_id}] Calculating metrics...")
        # Estimate pixel size (approximate for lat/lon)
        pixel_size_m = IMAGE_RESOLUTION  # 10m for Sentinel-2
        
        metrics = detector.calculate_metrics(
            binary_mask,
            pixel_size_m,
            kml_processor.area_m2
        )
        job.progress = 75
        
        # Step 6: Create visualization
        logger.info(f"[{job_id}] Creating visualization...")
        visualizer = DeforestationVisualizer(COLORS)
        
        highlight_png = job_dir / OUTPUT_FILES["highlight_image"]
        visualizer.create_highlight_image(
            after_png,
            prob_map,
            geometry,
            highlight_png
        )
        job.progress = 85
        
        # Step 7: Generate Gemini explanation
        logger.info(f"[{job_id}] Generating AI explanation...")
        try:
            explainer = GeminiExplainer(GEMINI_API_KEY)
            explanation_response = explainer.generate_explanation(metrics)
            # Extract the string explanation from the response dict
            explanation = explanation_response.get('explanation', 'Analysis completed successfully.')
            logger.info(f"Gemini API response status: {explanation_response.get('status', 'unknown')}")
        except Exception as e:
            logger.warning(f"Gemini API error: {e}, using fallback explanation")
            explanation = "AI explanation unavailable. Please check API credentials or quota limits."
        job.progress = 95
        
        # Step 8: Save outputs
        logger.info(f"[{job_id}] Saving outputs...")
        detector.save_outputs(prob_map, binary_mask, metrics, job_dir)
        
        # Prepare results
        job.results = {
            "metrics": metrics,
            "explanation": str(explanation),  # Force to string
            "images": {
                "before": f"/api/images/{folder_name}/{OUTPUT_FILES['before_image']}",
                "after": f"/api/images/{folder_name}/{OUTPUT_FILES['after_image']}",
                "highlight": f"/api/images/{folder_name}/{OUTPUT_FILES['highlight_image']}"
            },
            "dates": {
                "before": date_before,
                "after": date_after
            }
        }
        
        job.status = "completed"
        job.progress = 100
        logger.info(f"[{job_id}] Analysis complete!")
        
    except Exception as e:
        logger.error(f"[{job_id}] Error: {e}")
        logger.error(traceback.format_exc())
        job.status = "failed"
        job.error = str(e)


@app.route('/api/available-dates', methods=['GET'])
def get_available_dates():
    """Get available Sentinel-2 dates for a specific quarter"""
    try:
        # Get quarter parameter (e.g., "2020-Q1")
        quarter = request.args.get('quarter')
        
        if not quarter:
            return jsonify({
                'success': False,
                'error': 'Quarter parameter required (e.g., 2020-Q1)'
            }), 400
        
        # Parse quarter
        year, q = quarter.split('-Q')
        year = int(year)
        quarter_num = int(q)
        
        # Calculate date range for quarter
        from datetime import datetime, timedelta
        quarter_starts = {
            1: (1, 1),
            2: (4, 1),
            3: (7, 1),
            4: (10, 1)
        }
        
        start_month, start_day = quarter_starts[quarter_num]
        start_date = datetime(year, start_month, start_day)
        
        # End date is start of next quarter
        if quarter_num == 4:
            end_date = datetime(year + 1, 1, 1)
        else:
            next_month, _ = quarter_starts[quarter_num + 1]
            end_date = datetime(year, next_month, 1)
        
        # Load KML
        kml_processor = KMLProcessor(KML_FILE)
        kml_processor.parse()
        geometry = kml_processor.geometry
        
        # Initialize Sentinel API
        retriever = SentinelImageRetriever(
            COPERNICUS_USERNAME,
            COPERNICUS_PASSWORD,
            CACHE_DIR
        )
        
        # Load KML
        kml_processor = KMLProcessor(KML_FILE)
        kml_processor.parse()
        geometry = kml_processor.geometry
        
        # Initialize Sentinel API
        retriever = SentinelImageRetriever(
            COPERNICUS_USERNAME,
            COPERNICUS_PASSWORD,
            CACHE_DIR
        )
        
        dates_info = []
        seen_dates = set()
        
        # 1. SCAN LOCAL CACHE (Offline Capability)
        # Find SAFE directories to offer guaranteed valid dates
        try:
            import re
            safe_dirs = list(CACHE_DIR.glob("*.SAFE"))
            logger.info(f"Scanning {len(safe_dirs)} local SAFE directories for {quarter}")
            
            for safe_dir in safe_dirs:
                # Parse date from name: S2A_MSIL2A_20241126T... or similar
                # Looking for 8 digits followed by T
                match = re.search(r'[_A-Z0-9]+_(\d{8})T', safe_dir.name)
                if match:
                    d_str = match.group(1) # e.g. 20241126
                    try:
                        d_obj = datetime.strptime(d_str, "%Y%m%d")
                        
                        # Check if in quarter
                        if start_date <= d_obj < end_date:
                            date_only = d_obj.strftime("%Y-%m-%d")
                            if date_only not in seen_dates:
                                seen_dates.add(date_only)
                                dates_info.append({
                                    'date': date_only,
                                    'cloud_cover': 0.0, # Cached data is good
                                    'cached': True
                                })
                                logger.info(f"Found local cached date: {date_only}")
                    except ValueError:
                        continue
        except Exception as e:
            logger.error(f"Error scanning local cache: {e}")

        # 2. QUERY API (Online Capability)
        try:
            # Get access token
            token = retriever._get_access_token()
            
            # Build query
            minx, miny, maxx, maxy = geometry.bounds
            polygon_wkt = f"POLYGON(({minx} {miny}, {maxx} {miny}, {maxx} {maxy}, {minx} {maxy}, {minx} {miny}))"
            
            filter_query = (
                f"Collection/Name eq 'SENTINEL-2' and "
                f"OData.CSC.Intersects(area=geography'SRID=4326;{polygon_wkt}') and "
                f"ContentDate/Start ge {start_date.isoformat()}Z and "
                f"ContentDate/Start lt {end_date.isoformat()}Z and "
                f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 100)"
            )
            
            params = {
                "$filter": filter_query,
                "$top": 100,
                "$orderby": "ContentDate/Start desc"
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            
            import requests
            response = requests.get(
                f"{retriever.catalogue_url}/Products",
                params=params,
                headers=headers,
                timeout=60 # Increased timeout to ensure we find all dates
            )
            
            if response.status_code == 200:
                products = response.json().get('value', [])
                for product in products:
                    date_str = product['ContentDate']['Start']
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_only = date_obj.strftime('%Y-%m-%d')
                    
                    if date_only not in seen_dates:
                        seen_dates.add(date_only)
                        
                        # Get cloud cover
                        cloud_cover = None
                        for attr in product.get('Attributes', []):
                            if attr.get('Name') == 'cloudCover':
                                cloud_cover = round(attr.get('Value', 0), 1)
                                break
                        
                        dates_info.append({
                            'date': date_only,
                            'cloud_cover': cloud_cover,
                            'cached': False
                        })
        except Exception as e:
            logger.error(f"Error querying Copernicus API: {e}")
            # Do NOT fail, just use what we have (cached)
            if not dates_info:
                 # Only fail if we have NOTHING
                logger.error("No cached dates and API failed")
        
        # Sort by date
        dates_info.sort(key=lambda x: x['date'])
        
        logger.info(f"Found {len(dates_info)} dates for {quarter}")
        
        return jsonify({
            'success': True,
            'quarter': quarter,
            'dates': dates_info,
            'total': len(dates_info)
        })
        
    except Exception as e:
        logger.error(f"Error fetching dates for quarter: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Start a new deforestation analysis"""
    try:
        data = request.get_json()
        date_before = data.get('date_before')
        date_after = data.get('date_after')
        
        # Validate inputs
        if not date_before or not date_after:
            return jsonify({"error": "Missing date_before or date_after"}), 400
        
        # Validate date format
        try:
            datetime.strptime(date_before, "%Y-%m-%d")
            datetime.strptime(date_after, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Create job
        job_id = str(uuid.uuid4())
        job = AnalysisJob(job_id, date_before, date_after)
        jobs[job_id] = job
        
        # Start analysis in background thread
        thread = threading.Thread(
            target=run_analysis,
            args=(job_id, date_before, date_after)
        )
        thread.start()
        
        logger.info(f"Started analysis job: {job_id}")
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "message": "Analysis started"
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get status of an analysis job"""
    job = jobs.get(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    response = {
        "job_id": job_id,
        "status": job.status,
        "progress": job.progress,
        "created_at": job.created_at.isoformat()
    }
    
    if job.error:
        response["error"] = job.error
    
    return jsonify(response)


@app.route('/api/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Get results of a completed analysis"""
    job = jobs.get(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    if job.status != "completed":
        return jsonify({
            "error": f"Job not completed. Current status: {job.status}"
        }), 400
    
    logger.info(f"[RESULTS] Fetching results for job: {job_id}")
    logger.info(f"[RESULTS] job.results keys: {list(job.results.keys()) if job.results else 'None'}")
    
    # Return results - job.results already has the correct structure from run_analysis
    response_data = {
        'job_id': job_id,
        'images': job.results.get('images', {
            'before': f'/api/images/{OUTPUT_FILES["before_image"]}',
            'after': f'/api/images/{OUTPUT_FILES["after_image"]}',
            'highlight': f'/api/images/{OUTPUT_FILES["highlight_image"]}'
        }),
        'dates': job.results.get('dates', {
            'before': job.date_before,
            'after': job.date_after
        }),
        'metrics': job.results.get('metrics', {}),
        'explanation': job.results.get('explanation', 'Analysis completed successfully.')
    }
    
    logger.info(f"[RESULTS] Image URLs being returned:")
    logger.info(f"[RESULTS]   Before: {response_data['images']['before']}")
    logger.info(f"[RESULTS]   After: {response_data['images']['after']}")
    logger.info(f"[RESULTS]   Highlight: {response_data['images']['highlight']}")
    
    return jsonify(response_data)




@app.route('/api/image/<job_id>/<image_type>', methods=['GET'])
def get_job_image(job_id, image_type):
    """Serve images for a specific job by type (before/after/highlight)"""
    try:
        # Map image type to OUTPUT_FILES key
        type_to_key = {
            'before': 'before_image',
            'after': 'after_image',
            'highlight': 'highlight_image'
        }
        
        if image_type not in type_to_key:
            return jsonify({"error": "Invalid image type"}), 400
        
        # Get filename from OUTPUT_FILES
        filename = OUTPUT_FILES[type_to_key[image_type]]
        image_path = OUTPUT_DIR / filename
        
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            return jsonify({"error": f"Image not found: {filename}"}), 404
        
        return send_file(image_path, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/images/<path:filename>', methods=['GET'])
def get_image(filename):
    """Serve generated images"""
    try:
        image_path = OUTPUT_DIR / filename
        
        logger.info(f"[IMAGE REQUEST] Filename: {filename}")
        logger.info(f"[IMAGE REQUEST] Full path: {image_path}")
        logger.info(f"[IMAGE REQUEST] Exists: {image_path.exists()}")
        
        if image_path.exists():
            file_size = image_path.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"[IMAGE REQUEST] File size: {file_size:.2f} MB")
        
        if not image_path.exists():
            logger.error(f"[IMAGE REQUEST] Image not found: {image_path}")
            return jsonify({"error": "Image not found"}), 404
        
        logger.info(f"[IMAGE REQUEST] Serving image: {filename}")
        return send_file(image_path, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"[IMAGE REQUEST] Error serving image: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "kml_loaded": KML_FILE.exists()
    })


@app.route('/', methods=['GET'])
def index():
    """API information"""
    return jsonify({
        "name": "GeoSentinel Forest Watch API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/analyze": "Start deforestation analysis",
            "GET /api/status/<job_id>": "Get job status",
            "GET /api/results/<job_id>": "Get analysis results",
            "GET /api/images/<filename>": "Get generated images",
            "GET /api/health": "Health check"
        }
    })


if __name__ == '__main__':
    logger.info("Starting GeoSentinel Forest Watch API...")
    logger.info(f"KML file: {KML_FILE}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    
    # Validate configuration
    errors = validate_config()
    if errors:
        logger.warning("Configuration warnings:")
        for error in errors:
            logger.warning(f"  - {error}")
        logger.warning("Some features may not work correctly")
    
    # Debug: Print loaded environment variables (Masked)
    logger.info("--- Environment Check ---")
    logger.info(f"COPERNICUS_USERNAME set: {bool(COPERNICUS_USERNAME)}")
    logger.info(f"GEMINI_API_KEY set: {bool(GEMINI_API_KEY)}")
    logger.info(f"SENTINEL_HUB_CLIENT_ID set: {bool(SENTINEL_HUB_CLIENT_ID)}")
    logger.info(f"Starting host: 0.0.0.0 on port: {FLASK_PORT}")

    app.run(
        host='0.0.0.0',
        port=FLASK_PORT,
        debug=(FLASK_ENV == 'development')
    )
