# Miniconda Setup - Complete Guide

## Step 1: Download and Install Miniconda

### Download Miniconda3
1. Visit: https://docs.conda.io/en/latest/miniconda.html
2. Download: **Miniconda3 Windows 64-bit** (latest version)
3. Run the installer

### Installation Options
- ✅ **Check**: "Add Miniconda3 to my PATH environment variable"
- ✅ **Check**: "Register Miniconda3 as my default Python"
- Install location: `C:\Users\prady\miniconda3` (default is fine)

### After Installation
1. Close all terminals
2. Open a **new** Command Prompt or PowerShell
3. Test: `conda --version`

---

## Step 2: Initialize Conda in PowerShell (If Needed)

If `conda` command is not recognized in PowerShell:

```powershell
C:\Users\prady\miniconda3\Scripts\conda.exe init powershell
```

Then close and reopen PowerShell.

---

## Step 3: Create GeoSentinel Environment

Open **Anaconda Prompt** (or PowerShell with conda initialized):

```bash
# Navigate to project
cd d:\KeyFalcon\geosentinelforestwatch

# Create environment with Python 3.10 (more compatible than 3.13)
conda create -n geosentinel python=3.10 -y

# Activate environment
conda activate geosentinel
```

You should see `(geosentinel)` in your prompt.

---

## Step 4: Install Geospatial Packages

```bash
# Install from conda-forge (this handles GDAL automatically)
conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y
```

This will take 5-10 minutes. ☕

---

## Step 5: Install Python Packages

```bash
# Install remaining packages with pip
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm sentinelsat
```

---

## Step 6: Verify Installation

```bash
# Test imports
python -c "import rasterio, geopandas, flask; print('✅ All packages installed successfully!')"
```

If you see the success message, you're ready!

---

## Step 7: Configure API Credentials

### Option A: Copernicus Data Space (Free - Recommended)

1. Register: https://dataspace.copernicus.eu/
2. Create account (free)
3. Edit `.env` file:

```env
COPERNICUS_USERNAME=your_username
COPERNICUS_PASSWORD=your_password
GEMINI_API_KEY=your_gemini_key
```

### Option B: Sentinel Hub (Trial)

1. Register: https://www.sentinel-hub.com/
2. Get trial credentials
3. Edit `.env` file:

```env
SENTINEL_HUB_CLIENT_ID=your_client_id
SENTINEL_HUB_CLIENT_SECRET=your_client_secret
GEMINI_API_KEY=your_gemini_key
```

---

## Step 8: Start the Application

### Terminal 1: Backend

```bash
# In Anaconda Prompt
cd d:\KeyFalcon\geosentinelforestwatch
conda activate geosentinel
cd backend
python api.py
```

You should see:
```
Starting GeoSentinel Forest Watch API...
 * Running on http://0.0.0.0:5000
```

### Terminal 2: Frontend

```bash
# In regular Command Prompt or PowerShell
cd d:\KeyFalcon\geosentinelforestwatch\frontend
npm install
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

---

## Step 9: Test with Real Data

1. Open browser: http://localhost:5173
2. Select dates:
   - Before: 2023-01-01
   - After: 2024-01-01
3. Click "Analyze Deforestation"
4. Wait 2-5 minutes (downloading real satellite data)
5. View results!

---

## Quick Reference Commands

### Activate environment:
```bash
conda activate geosentinel
```

### Deactivate environment:
```bash
conda deactivate
```

### List environments:
```bash
conda env list
```

### Update packages:
```bash
conda update -c conda-forge rasterio geopandas
```

---

## Troubleshooting

### "conda not recognized"
- Use **Anaconda Prompt** instead of regular PowerShell
- Or run: `C:\Users\prady\miniconda3\Scripts\conda.exe init powershell`

### "Solving environment: failed"
- Try: `conda config --add channels conda-forge`
- Then retry installation

### "DLL load failed"
- Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

### "No Sentinel data found"
- Check API credentials in `.env`
- Verify internet connection
- Check date range (Sentinel-2 launched in 2015)

---

## Copy-Paste Ready Commands

**Complete setup in one go:**

```bash
# Create and activate environment
conda create -n geosentinel python=3.10 -y
conda activate geosentinel

# Install geospatial packages
conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y

# Install Python packages
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm sentinelsat

# Verify
python -c "import rasterio, geopandas, flask; print('✅ Success!')"
```

**Start application:**

```bash
# Terminal 1 (Anaconda Prompt)
cd d:\KeyFalcon\geosentinelforestwatch && conda activate geosentinel && cd backend && python api.py

# Terminal 2 (Regular terminal)
cd d:\KeyFalcon\geosentinelforestwatch\frontend && npm run dev
```

---

**Ready to start? Follow the steps above and let me know if you hit any issues!** 🚀
