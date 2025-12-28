# Easy Setup - Just Double-Click!

## 🚀 Quick Start (3 Steps)

Since you've reinstalled Miniconda with PATH enabled, you can use these batch scripts:

### Step 1: Setup Environment (One-Time)

**Double-click:** `setup_conda_environment.bat`

This will:
- Create the `geosentinel` conda environment
- Install all geospatial packages (rasterio, geopandas, etc.)
- Install Python packages (Flask, TensorFlow, etc.)
- Verify everything is working

⏱️ **Takes 10-15 minutes** - grab a coffee! ☕

---

### Step 2: Configure API Keys

Edit `.env` file and add your credentials:

```env
# Get free account at: https://dataspace.copernicus.eu/
COPERNICUS_USERNAME=your_username
COPERNICUS_PASSWORD=your_password

# Get free API key at: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key
```

---

### Step 3: Start the Application

**Terminal 1:** Double-click `start_backend.bat`
- Starts the Flask API server
- Runs on http://localhost:5000

**Terminal 2:** Double-click `start_frontend.bat`  
- Starts the React UI
- Runs on http://localhost:5173

**Open browser:** http://localhost:5173

---

## 🎯 Test It!

1. Select dates:
   - Before: 2023-01-01
   - After: 2024-01-01

2. Click "Analyze Deforestation"

3. Wait 2-5 minutes (downloading real satellite data)

4. View results!

---

## 🔧 If Conda Still Not Working

**Option A: Restart Terminal**
1. Close all PowerShell/Command Prompt windows
2. Open a **new** Command Prompt
3. Run: `conda --version`
4. If it works, run the batch scripts

**Option B: Use Anaconda Prompt**
1. Search "Anaconda Prompt" in Start Menu
2. Navigate: `cd d:\KeyFalcon\geosentinelforestwatch`
3. Run commands manually:
```bash
conda create -n geosentinel python=3.10 -y
conda activate geosentinel
conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm sentinelsat
```

---

## 📝 What Each Script Does

**`setup_conda_environment.bat`**
- One-time setup
- Creates environment and installs all packages

**`start_backend.bat`**
- Starts Flask API server
- Keep this running while using the app

**`start_frontend.bat`**
- Starts React development server
- Keep this running while using the app

---

## ✅ Success Checklist

- [ ] Ran `setup_conda_environment.bat` successfully
- [ ] Configured API keys in `.env`
- [ ] Started backend with `start_backend.bat`
- [ ] Started frontend with `start_frontend.bat`
- [ ] Opened http://localhost:5173
- [ ] Tested deforestation analysis

---

**Ready? Just double-click `setup_conda_environment.bat` to begin!** 🎉
