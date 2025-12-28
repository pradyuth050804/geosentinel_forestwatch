@echo off
echo ============================================================
echo GeoSentinel Forest Watch - Conda Environment Setup
echo ============================================================
echo.

REM Initialize conda for this session
call %USERPROFILE%\miniconda3\Scripts\activate.bat

echo Step 1: Creating conda environment...
call conda create -n geosentinel python=3.10 -y

echo.
echo Step 2: Activating environment...
call conda activate geosentinel

echo.
echo Step 3: Installing geospatial packages (this will take 5-10 minutes)...
call conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y

echo.
echo Step 4: Installing Python packages...
call pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm sentinelsat

echo.
echo Step 5: Verifying installation...
python -c "import rasterio, geopandas, flask; print('SUCCESS: All packages installed!')"

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Configure API keys in .env file
echo 2. Run: setup_and_start_backend.bat
echo.
pause
