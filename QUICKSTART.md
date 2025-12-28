# Quick Setup Guide - Choose Your Path

## ⚠️ Conda Not Detected

Conda is not installed on your system. You have two options:

---

## Option A: Install Miniconda (Recommended for Full Features)

### Step 1: Download Miniconda
1. Visit: https://docs.conda.io/en/latest/miniconda.html
2. Download **Miniconda3 Windows 64-bit** installer
3. Run the installer (accept defaults)
4. **Important**: Check "Add Miniconda to PATH" during installation

### Step 2: Restart Terminal
Close and reopen PowerShell/Command Prompt

### Step 3: Create Environment
```bash
cd d:\KeyFalcon\geosentinelforestwatch
conda create -n geosentinel python=3.10 -y
conda activate geosentinel
```

### Step 4: Install Geospatial Packages
```bash
conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y
```

### Step 5: Install Remaining Packages
```bash
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm
```

### Step 6: Configure and Run
```bash
# Copy environment file
copy .env.example .env

# Edit .env and add your Gemini API key

# Start backend
cd backend
python api.py
```

---

## Option B: Simplified Setup (Works Now, Limited Features)

This option works immediately but won't process real GeoTIFF files (mock data only):

### Step 1: Install Core Dependencies
```bash
cd d:\KeyFalcon\geosentinelforestwatch

# Use existing venv
venv\Scripts\activate

# Install working packages
pip install flask flask-cors python-dotenv google-generativeai numpy scipy
```

### Step 2: Install TensorFlow (CPU version)
```bash
pip install tensorflow-cpu
```

### Step 3: Install Image Processing (try pre-built)
```bash
pip install --only-binary :all: pillow opencv-python scikit-image
```

### Step 4: Configure
```bash
copy .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
```

### Step 5: Run Backend
```bash
cd backend
python api.py
```

---

## Option C: Frontend Only (No Backend Setup)

If you just want to see the UI design:

```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend
npm install
npm run dev
```

Open http://localhost:5173 (will show UI but backend calls will fail)

---

## What I Recommend

**For full functionality**: Use **Option A** (Miniconda)
- Takes 10 minutes to set up
- Handles all complex dependencies automatically
- Full geospatial processing capabilities

**For quick testing**: Use **Option B** (Simplified)
- Works with existing venv
- Mock data only
- Good for UI testing and development

**Just to see the UI**: Use **Option C** (Frontend only)
- Fastest to set up
- See the modern design
- No backend functionality

---

## Need Help?

Let me know which option you'd like to pursue and I can guide you through it step by step!
