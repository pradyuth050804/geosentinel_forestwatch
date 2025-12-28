# NO CONDA NEEDED! - Quick Start Guide

## ✅ Simple Installation (Just pip!)

### Step 1: Install Dependencies

```bash
cd d:\KeyFalcon\geosentinelforestwatch

# Use existing venv or create new one
python -m venv venv
venv\Scripts\activate

# Install minimal requirements
pip install -r backend\requirements-minimal.txt
```

**That's it!** No conda, no GDAL, no complex dependencies.

---

## Step 2: Configure (Optional)

Edit `.env` file and add Gemini API key (optional):
```env
GEMINI_API_KEY=your_key_here
```

Get free key: https://makersuite.google.com/app/apikey

---

## Step 3: Start Backend

```bash
cd backend
python api_simple.py
```

You should see:
```
Starting GeoSentinel Forest Watch API (Simplified Version)...
Mode: No GDAL/Rasterio dependencies - using mock data
 * Running on http://0.0.0.0:5000
```

---

## Step 4: Start Frontend (New Terminal)

```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend
npm install
npm run dev
```

---

## Step 5: Test It!

1. Open http://localhost:5173
2. Select dates (e.g., 2023-01-01 to 2024-01-01)
3. Click "Analyze Deforestation"
4. Wait ~10 seconds
5. See results!

---

## What's Different?

**Simplified Version:**
- ✅ Works with pip only (no conda)
- ✅ Uses mock satellite images
- ✅ Full UI functionality
- ✅ Deforestation detection
- ✅ Metrics calculation
- ✅ AI explanations (if Gemini key provided)
- ❌ No real GeoTIFF processing
- ❌ No actual Sentinel-2 API calls

**Perfect for:**
- Testing the UI
- Understanding the workflow
- Development without complex dependencies
- Quick demos

---

## Copy-Paste Commands

```bash
# All in one:
cd d:\KeyFalcon\geosentinelforestwatch && venv\Scripts\activate && pip install -r backend\requirements-minimal.txt && cd backend && python api_simple.py
```

Then in a new terminal:
```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend && npm run dev
```

---

## Troubleshooting

### "No module named 'flask'"
```bash
venv\Scripts\activate
pip install -r backend\requirements-minimal.txt
```

### "Pillow installation failed"
```bash
pip install --upgrade pip
pip install Pillow --no-cache-dir
```

### "Port 5000 already in use"
Edit `.env` and change:
```env
FLASK_PORT=5001
```

---

## Upgrade to Full Version Later

When you're ready for real satellite data:
1. Install conda
2. Run: `conda install -c conda-forge rasterio geopandas`
3. Use `backend/api.py` instead of `api_simple.py`

---

**This is the easiest way to get started! No conda required!** 🎉
