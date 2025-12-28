# Step-by-Step Conda Environment Setup

## Run these commands in Anaconda Prompt (base):

### Step 1: Create the environment
```bash
conda create -n geosentinel python=3.10 -y
```

### Step 2: Activate it
```bash
conda activate geosentinel
```

### Step 3: Install geospatial packages from conda-forge
```bash
conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y
```

### Step 4: Install remaining packages with pip
```bash
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm
```

### Step 5: Verify installation
```bash
python -c "import flask, rasterio, geopandas; print('All packages installed successfully!')"
```

---

## If you get errors, try this alternative:

### Create environment with more packages from conda
```bash
conda create -n geosentinel python=3.10 numpy scipy pillow -y
conda activate geosentinel
conda install -c conda-forge rasterio geopandas shapely -y
pip install flask flask-cors python-dotenv tensorflow opencv-python scikit-image google-generativeai tqdm
```

---

## After successful installation:

### Navigate to project
```bash
cd d:\KeyFalcon\geosentinelforestwatch
```

### Start backend
```bash
cd backend
python api.py
```

---

## Copy-Paste Ready Commands:

```bash
# All in one - copy and paste this entire block:
conda create -n geosentinel python=3.10 -y && conda activate geosentinel && conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y && pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm
```

Then:
```bash
cd d:\KeyFalcon\geosentinelforestwatch\backend
python api.py
```
