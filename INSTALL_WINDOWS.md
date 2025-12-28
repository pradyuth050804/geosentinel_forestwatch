# GeoSentinel Forest Watch - Installation Guide for Windows

## Quick Start (Recommended)

### Option 1: Use Conda (Easiest)

Conda handles all the complex geospatial dependencies automatically:

```bash
# Install Miniconda from: https://docs.conda.io/en/latest/miniconda.html

# Create environment
conda create -n geosentinel python=3.10
conda activate geosentinel

# Install geospatial packages
conda install -c conda-forge rasterio geopandas shapely fiona pyproj

# Install remaining packages
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm

# Navigate to project
cd d:\KeyFalcon\geosentinelforestwatch

# Start backend
cd backend
python api.py
```

### Option 2: Use Pre-built Wheels (Windows)

If you prefer pip, use pre-compiled wheels:

```bash
# Download GDAL wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
# Choose the version matching your Python (e.g., GDAL‑3.4.3‑cp310‑cp310‑win_amd64.whl for Python 3.10)

# Install GDAL
pip install path\to\downloaded\GDAL‑3.4.3‑cp310‑cp310‑win_amd64.whl

# Install rasterio wheel
# Download from same site: rasterio‑1.3.9‑cp310‑cp310‑win_amd64.whl
pip install path\to\downloaded\rasterio‑1.3.9‑cp310‑cp310‑win_amd64.whl

# Install remaining packages
pip install flask flask-cors python-dotenv geopandas shapely tensorflow pillow opencv-python google-generativeai
```

### Option 3: Minimal Installation (No Geospatial)

For testing the UI and basic functionality without full geospatial support:

```bash
cd d:\KeyFalcon\geosentinelforestwatch
python -m venv venv
venv\Scripts\activate

# Install only core packages
pip install flask flask-cors python-dotenv pillow numpy scipy google-generativeai

# Note: This will work with mock data but won't process real GeoTIFF files
```

---

## Frontend Setup

```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend

# Install Node.js from: https://nodejs.org/ (if not installed)

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Configuration

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

Get a free Gemini API key from: https://makersuite.google.com/app/apikey

---

## Running the Application

### Start Backend (Terminal 1)
```bash
cd d:\KeyFalcon\geosentinelforestwatch\backend
python api.py
```

Backend will run on `http://localhost:5000`

### Start Frontend (Terminal 2)
```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

### Open Browser
Navigate to `http://localhost:5173`

---

## Testing Without Installation

If you're having dependency issues, you can still explore the code:

1. **View the Architecture**: Check [`README.md`](file:///d:/KeyFalcon/geosentinelforestwatch/README.md)
2. **Review the Code**: All components are well-documented
3. **Read the Walkthrough**: See what was implemented

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'rasterio'"
- Use Conda installation (Option 1 above)
- Or download pre-built wheels (Option 2)

### "GDAL not found"
- Install GDAL from Christoph Gohlke's wheels
- Or use Conda which handles GDAL automatically

### "TensorFlow installation failed"
- Ensure you have Python 3.9-3.11 (TensorFlow doesn't support 3.12 yet)
- Try: `pip install tensorflow-cpu` for CPU-only version

### "npm install failed"
- Ensure Node.js 18+ is installed
- Try: `npm install --legacy-peer-deps`

---

## Next Steps After Installation

1. **Configure API Keys**: Add Gemini API key to `.env`
2. **Test Backend**: Run `python scripts/test_workflow.py`
3. **Start Servers**: Backend and frontend as shown above
4. **Analyze Deforestation**: Use the web interface!

---

## Alternative: Docker (Future Enhancement)

For a completely isolated environment, Docker support can be added:

```dockerfile
# Future: docker-compose.yml
services:
  backend:
    image: python:3.10
    volumes:
      - ./backend:/app
    command: python api.py
  
  frontend:
    image: node:18
    volumes:
      - ./frontend:/app
    command: npm run dev
```

---

## Support

If you encounter issues:
1. Check the [README.md](file:///d:/KeyFalcon/geosentinelforestwatch/README.md) for detailed documentation
2. Review the [walkthrough.md](file:///C:/Users/prady/.gemini/antigravity/brain/23b4ec2b-1f08-46ac-a176-9e67c72baa18/walkthrough.md) for implementation details
3. Open an issue on GitHub (if applicable)

---

**Recommended**: Use **Conda** for the smoothest installation experience on Windows!
