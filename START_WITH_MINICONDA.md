# Setup Instructions for Your Miniconda Installation

## Your Miniconda Location: D:\miniconda

Since conda commands aren't working in PowerShell, please use **Anaconda Prompt**:

### Step 1: Open Anaconda Prompt

1. Press **Windows Key**
2. Type: **Anaconda Prompt**
3. Open it (should show "Anaconda Prompt (miniconda3)" or similar)

### Step 2: Create Environment

In Anaconda Prompt, run these commands:

```bash
# Navigate to project
cd d:\KeyFalcon\geosentinelforestwatch

# Create environment
conda create -n geosentinel python=3.10 -y

# Activate it
conda activate geosentinel
```

### Step 3: Install Geospatial Packages

```bash
conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y
```

⏱️ This will take 5-10 minutes. Be patient!

### Step 4: Install Python Packages

```bash
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm sentinelsat
```

### Step 5: Verify Installation

```bash
python -c "import rasterio, geopandas, flask; print('✅ All packages installed!')"
```

### Step 6: Configure API Keys

Edit the `.env` file in the project root:

```env
# Copernicus Data Space (Free)
COPERNICUS_USERNAME=your_username_here
COPERNICUS_PASSWORD=your_password_here

# Google Gemini API
GEMINI_API_KEY=your_gemini_key_here
```

**Get credentials:**
- Copernicus: https://dataspace.copernicus.eu/ (register for free)
- Gemini: https://makersuite.google.com/app/apikey (free API key)

### Step 7: Start Backend

In Anaconda Prompt (with geosentinel activated):

```bash
cd d:\KeyFalcon\geosentinelforestwatch\backend
python api.py
```

You should see:
```
Starting GeoSentinel Forest Watch API...
 * Running on http://0.0.0.0:5000
```

**Keep this terminal open!**

### Step 8: Start Frontend

Open a **new** regular Command Prompt or PowerShell:

```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend
npm install
npm run dev
```

You should see:
```
VITE ready
➜  Local:   http://localhost:5173/
```

### Step 9: Open Browser

Go to: **http://localhost:5173**

Test with:
- Before date: 2023-01-01
- After date: 2024-01-01
- Click "Analyze Deforestation"

---

## Quick Commands (Copy-Paste)

**In Anaconda Prompt:**

```bash
# Complete setup
cd d:\KeyFalcon\geosentinelforestwatch
conda create -n geosentinel python=3.10 -y
conda activate geosentinel
conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm sentinelsat
python -c "import rasterio, geopandas, flask; print('✅ Success!')"
```

**Start backend:**
```bash
cd d:\KeyFalcon\geosentinelforestwatch\backend
python api.py
```

**In regular terminal (new window):**
```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend
npm install
npm run dev
```

---

## Troubleshooting

**Can't find Anaconda Prompt?**
- Search in Start Menu for "Anaconda"
- Or use: `D:\miniconda\Scripts\activate.bat`

**Environment already exists?**
```bash
conda env remove -n geosentinel
# Then create again
```

**Import errors?**
- Make sure you see `(geosentinel)` in prompt
- Run: `conda activate geosentinel`

---

**Ready to start? Open Anaconda Prompt and follow the steps above!** 🚀
