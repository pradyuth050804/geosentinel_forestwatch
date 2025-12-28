"""
Simplified Flask API (No GDAL/Rasterio Dependencies)
Uses simplified versions of services
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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import simplified services
from backend.services.kml_processor_simple import KMLProcessor
from backend.services.sentinel_api_simple import SentinelImageRetriever
from backend.services.image_processor_simple import ImageProcessor
from backend.ml.change_detector import ChangeDetector
from backend.services.visualization import DeforestationVisualizer

# Try to import Gemini, but don't fail if not available
try:
    from backend.services.gemini_service import GeminiExplainer
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    logging.warning("Gemini service not available")

# Load config
from backend.config import *

# Try to import Gemini, but don't fail if not available
try:
    from backend.services.gemini_service import GeminiExplainer
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    logging.warning("Gemini service not available")

# Load config
from backend.config import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
# Allow CORS for all domains on all /api routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Job storage
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
    """Run complete deforestation analysis workflow (simplified)"""
    job = jobs[job_id]
    
    try:
        job.status = "processing"
        job.progress = 5
        
        # Step 1: Load KML boundary
        logger.info(f"[{job_id}] Loading KML boundary...")
        kml_processor = KMLProcessor(KML_FILE)
        kml_processor.parse()
        job.progress = 15
        
        # Step 2: Generate mock imagery
        logger.info(f"[{job_id}] Generating mock satellite imagery...")
        retriever = SentinelImageRetriever(cache_dir=CACHE_DIR)
        
        before_img = retriever.get_image_for_date(date_before, is_deforested=False)
        job.progress = 30
        
        after_img = retriever.get_image_for_date(date_after, is_deforested=True)
        job.progress = 45
        
        # Step 3: Process images
        logger.info(f"[{job_id}] Processing images...")
        processor = ImageProcessor(OUTPUT_DIR)
        
        before_png = OUTPUT_DIR / OUTPUT_FILES["before_image"]
        after_png = OUTPUT_DIR / OUTPUT_FILES["after_image"]
        
        processor.process_image_pair(
            before_img,
            after_img,
            before_png,
            after_png
        )
        job.progress = 60
        
        # Step 4: Run deforestation detection
        logger.info(f"[{job_id}] Running deforestation detection...")
        detector = ChangeDetector(use_simple_detector=True, threshold=DEFORESTATION_THRESHOLD)
        
        prob_map, binary_mask = detector.detect_changes(before_png, after_png)
        job.progress = 75
        
        # Step 5: Calculate metrics
        logger.info(f"[{job_id}] Calculating metrics...")
        metrics = detector.calculate_metrics(
            binary_mask,
            IMAGE_RESOLUTION,
            kml_processor.area_m2
        )
        job.progress = 80
        
        # Step 6: Create visualization
        logger.info(f"[{job_id}] Creating visualization...")
        visualizer = DeforestationVisualizer(COLORS)
        
        highlight_png = OUTPUT_DIR / OUTPUT_FILES["highlight_image"]
        
        # Create simple geometry dict for visualization
        geometry_dict = {
            "coordinates": kml_processor.coordinates,
            "bounds": kml_processor.bounds
        }
        
        visualizer.create_highlight_image(
            after_png,
            prob_map,
            geometry_dict,
            highlight_png
        )
        job.progress = 90
        
        # Step 7: Generate explanation
        logger.info(f"[{job_id}] Generating explanation...")
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                explainer = GeminiExplainer(GEMINI_API_KEY)
                explanation = explainer.generate_explanation(metrics)
            except Exception as e:
                logger.warning(f"Gemini API error: {e}")
                explanation = create_fallback_explanation(metrics)
        else:
            explanation = create_fallback_explanation(metrics)
        
        job.progress = 95
        
        # Step 8: Save outputs
        detector.save_outputs(prob_map, binary_mask, metrics, OUTPUT_DIR)
        
        # Prepare results
        job.results = {
            "metrics": metrics,
            "explanation": explanation,
            "images": {
                "before": f"/api/images/{OUTPUT_FILES['before_image']}",
                "after": f"/api/images/{OUTPUT_FILES['after_image']}",
                "highlight": f"/api/images/{OUTPUT_FILES['highlight_image']}"
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


def create_fallback_explanation(metrics):
    """Create explanation when Gemini is not available"""
    deforested_ha = metrics['deforested_area_hectares']
    percentage = metrics['forest_loss_percentage']
    patches = metrics['number_of_patches']
    
    explanation_text = f"""**Deforestation Analysis Summary**

**Magnitude**: {deforested_ha:.2f} hectares ({percentage:.2f}% of total forest area) has been deforested between the two observation dates.

**Spatial Distribution**: The analysis detected {patches} distinct deforestation patches. """
    
    if patches > 10:
        explanation_text += "The high number of scattered patches suggests gradual encroachment or small-scale clearing activities."
    elif patches > 5:
        explanation_text += "Multiple patches indicate distributed deforestation activity across the forest area."
    else:
        explanation_text += "Few large patches suggest concentrated clearing, possibly for planned development or agriculture."
    
    explanation_text += f"""

**Pattern Assessment**: The largest contiguous cleared area is {metrics['largest_patch_hectares']:.2f} hectares, which represents {(metrics['largest_patch_hectares']/deforested_ha*100):.1f}% of total deforestation.

**Human Activity**: Based on the patch distribution and size, this deforestation pattern is likely human-driven, potentially for agricultural expansion, logging, or land development.

**Conservation Status**: {metrics['intact_forest_hectares']:.2f} hectares ({100-percentage:.1f}%) of forest remains intact.

*Note: AI-powered explanation service unavailable. This is a rule-based analysis.*
"""
    
    return {
        "explanation": explanation_text,
        "confidence_score": 70,
        "status": "fallback",
        "model": "rule-based"
    }


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Start a new deforestation analysis"""
    try:
        data = request.get_json()
        date_before = data.get('date_before')
        date_after = data.get('date_after')
        
        if not date_before or not date_after:
            return jsonify({"error": "Missing date_before or date_after"}), 400
        
        try:
            datetime.strptime(date_before, "%Y-%m-%d")
            datetime.strptime(date_after, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        job_id = str(uuid.uuid4())
        job = AnalysisJob(job_id, date_before, date_after)
        jobs[job_id] = job
        
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


@app.route('/api/available-dates', methods=['GET'])
def get_available_dates():
    """Get available Sentinel-2 dates (Mocked for Simple Version)"""
    try:
        quarter = request.args.get('quarter')
        if not quarter:
            return jsonify({'success': False, 'error': 'Quarter parameter required'}), 400
        
        # Mock dates for demo purposes
        # In simple mode, we just return a fixed set of "good" dates
        dates = [
            {'date': '2022-05-06', 'cloud_cover': 5.2, 'cached': True},
            {'date': '2023-01-15', 'cloud_cover': 12.1, 'cached': False},
            {'date': '2024-11-26', 'cloud_cover': 2.5, 'cached': True}
        ]
        
        return jsonify({
            'success': True,
            'quarter': quarter,
            'dates': dates,
            'total': len(dates)
        })
        
    except Exception as e:
        logger.error(f"Error fetching dates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
    
    return jsonify(job.results)


@app.route('/api/images/<filename>', methods=['GET'])
def get_image(filename):
    """Serve generated images"""
    try:
        image_path = OUTPUT_DIR / filename
        
        if not image_path.exists():
            return jsonify({"error": "Image not found"}), 404
        
        return send_file(image_path, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0 (simplified)",
        "kml_loaded": KML_FILE.exists(),
        "gemini_available": GEMINI_AVAILABLE and bool(GEMINI_API_KEY)
    })


@app.route('/', methods=['GET'])
def index():
    """API information"""
    return jsonify({
        "name": "GeoSentinel Forest Watch API (Simplified)",
        "version": "1.0.0",
        "mode": "No GDAL/Rasterio - Mock data only",
        "endpoints": {
            "POST /api/analyze": "Start deforestation analysis",
            "GET /api/status/<job_id>": "Get job status",
            "GET /api/results/<job_id>": "Get analysis results",
            "GET /api/images/<filename>": "Get generated images",
            "GET /api/health": "Health check"
        }
    })


if __name__ == '__main__':
    logger.info("Starting GeoSentinel Forest Watch API (Simplified Version)...")
    logger.info(f"KML file: {KML_FILE}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info("Mode: No GDAL/Rasterio dependencies - using mock data")
    
    app.run(
        host='0.0.0.0',
        port=FLASK_PORT,
        debug=(FLASK_ENV == 'development')
    )
