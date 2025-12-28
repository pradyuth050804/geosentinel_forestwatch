# Quick Start Checklist

## ✅ Miniconda Installation Checklist

Follow these steps in order:

### 1. Download Miniconda
- [ ] Go to: https://docs.conda.io/en/latest/miniconda.html
- [ ] Download: Miniconda3 Windows 64-bit
- [ ] Run installer
- [ ] ✅ Check "Add to PATH"
- [ ] ✅ Check "Register as default Python"
- [ ] Complete installation

### 2. Verify Installation
- [ ] Close all terminals
- [ ] Open new Command Prompt
- [ ] Run: `conda --version`
- [ ] Should show version number

### 3. Create Environment
Open **Anaconda Prompt** and run:
```bash
conda create -n geosentinel python=3.10 -y
```
- [ ] Wait for completion (~2 minutes)

### 4. Activate Environment
```bash
conda activate geosentinel
```
- [ ] Prompt should show `(geosentinel)`

### 5. Install Geospatial Packages
```bash
conda install -c conda-forge rasterio geopandas shapely fiona pyproj -y
```
- [ ] Wait for completion (~5-10 minutes)

### 6. Install Python Packages
```bash
pip install flask flask-cors python-dotenv tensorflow pillow opencv-python scikit-image scipy google-generativeai tqdm sentinelsat
```
- [ ] Wait for completion (~3-5 minutes)

### 7. Verify Installation
```bash
python -c "import rasterio, geopandas, flask; print('Success!')"
```
- [ ] Should print "Success!"

### 8. Configure API Keys
- [ ] Register at: https://dataspace.copernicus.eu/
- [ ] Get Gemini key: https://makersuite.google.com/app/apikey
- [ ] Edit `.env` file with credentials

### 9. Start Backend
```bash
cd d:\KeyFalcon\geosentinelforestwatch\backend
python api.py
```
- [ ] Should show "Running on http://0.0.0.0:5000"

### 10. Start Frontend (New Terminal)
```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend
npm install
npm run dev
```
- [ ] Should show "Local: http://localhost:5173"

### 11. Test Application
- [ ] Open: http://localhost:5173
- [ ] Select dates
- [ ] Click "Analyze Deforestation"
- [ ] View results!

---

## 🆘 Having Issues?

**Conda not recognized?**
→ Use "Anaconda Prompt" from Start Menu

**Installation failed?**
→ Run: `conda config --add channels conda-forge`
→ Retry installation

**Import errors?**
→ Make sure `(geosentinel)` is shown in prompt
→ Run: `conda activate geosentinel`

**Need help?**
→ Check `MINICONDA_COMPLETE_GUIDE.md` for detailed instructions

---

## 📝 Current Status

Mark your progress:
- [ ] Miniconda installed
- [ ] Environment created
- [ ] Packages installed
- [ ] API keys configured
- [ ] Backend running
- [ ] Frontend running
- [ ] Application tested

---

**Once all checkboxes are complete, you're ready to analyze real deforestation data!** 🌲
