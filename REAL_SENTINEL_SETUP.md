# Real Sentinel-2 Data Setup (Windows - No Conda)

## Option 1: Automated Installation (Recommended)

I'll download and install the pre-built wheels for you automatically.

### Step 1: Check Your Python Version

```bash
python --version
```

Note the version (e.g., 3.10, 3.11, 3.12)

### Step 2: Run Automated Installer

```bash
cd d:\KeyFalcon\geosentinelforestwatch
venv\Scripts\activate
python scripts\install_gdal_windows.py
```

This script will:
1. Detect your Python version
2. Download correct GDAL wheel
3. Download correct rasterio wheel
4. Install all dependencies
5. Verify installation

---

## Option 2: Manual Installation

If automated doesn't work, follow these steps:

### Step 1: Download Pre-built Wheels

Visit: https://github.com/cgohlke/geospatial-wheels/releases

Download these files (match your Python version):
- `GDAL-3.8.3-cp310-cp310-win_amd64.whl` (for Python 3.10)
- `rasterio-1.3.9-cp310-cp310-win_amd64.whl` (for Python 3.10)

**Replace `cp310` with your Python version:**
- Python 3.10 → `cp310`
- Python 3.11 → `cp311`
- Python 3.12 → `cp312`

### Step 2: Install GDAL First

```bash
cd d:\KeyFalcon\geosentinelforestwatch
venv\Scripts\activate
pip install path\to\downloaded\GDAL-3.8.3-cp310-cp310-win_amd64.whl
```

### Step 3: Install Rasterio

```bash
pip install path\to\downloaded\rasterio-1.3.9-cp310-cp310-win_amd64.whl
```

### Step 4: Install Other Geospatial Libraries

```bash
pip install geopandas shapely fiona pyproj
```

### Step 5: Install Remaining Dependencies

```bash
pip install -r backend\requirements.txt
```

---

## Option 3: Use pipwin (Easiest Manual Method)

```bash
venv\Scripts\activate
pip install pipwin
pipwin install gdal
pipwin install rasterio
pipwin install fiona
pip install geopandas shapely pyproj
pip install -r backend\requirements.txt
```

---

## Verify Installation

```bash
python -c "import rasterio, geopandas; print('Success! Geospatial libraries installed.')"
```

---

## Configure Sentinel API

You'll need credentials for one of these:

### Option A: Copernicus Data Space (Free)

1. Register: https://dataspace.copernicus.eu/
2. Create account
3. Add to `.env`:
```env
COPERNICUS_USERNAME=your_username
COPERNICUS_PASSWORD=your_password
```

### Option B: Sentinel Hub (Commercial Trial)

1. Register: https://www.sentinel-hub.com/
2. Get trial account
3. Add to `.env`:
```env
SENTINEL_HUB_CLIENT_ID=your_client_id
SENTINEL_HUB_CLIENT_SECRET=your_client_secret
```

---

## Start Backend with Real Data

```bash
cd backend
python api.py  # Use the full version, not api_simple.py
```

---

## Troubleshooting

### "GDAL not found"
- Make sure you installed GDAL wheel BEFORE rasterio
- Restart terminal after installation

### "DLL load failed"
- Download Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart

### "Wrong wheel version"
- Check Python version: `python --version`
- Download matching wheel (cp310 for 3.10, cp311 for 3.11, etc.)

---

**Let me know which option you'd like to try, and I can help you through it!**
