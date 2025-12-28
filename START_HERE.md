# GeoSentinel Forest Watch - Startup Instructions

## ✅ You've Completed Conda Setup!

Now let's start the application.

---

## Step 1: Activate Conda Environment

**Important**: Conda needs to be initialized in PowerShell. Try one of these:

### Option A: Use Anaconda Prompt (Recommended)
1. Search for "Anaconda Prompt (Miniconda3)" in Windows Start Menu
2. Open it
3. Navigate to project:
   ```bash
   cd d:\KeyFalcon\geosentinelforestwatch
   conda activate geosentinel
   ```

### Option B: Initialize Conda in PowerShell
```powershell
# Run this once to initialize conda in PowerShell
C:\Users\prady\miniconda3\Scripts\conda.exe init powershell

# Close and reopen PowerShell, then:
conda activate geosentinel
```

---

## Step 2: Configure Gemini API Key

Edit the `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

**Get a free API key**: https://makersuite.google.com/app/apikey

---

## Step 3: Start Backend Server

In Anaconda Prompt (or PowerShell with conda activated):

```bash
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

**Keep this terminal open!**

---

## Step 4: Start Frontend (New Terminal)

Open a **new** terminal (regular PowerShell or Command Prompt):

```bash
cd d:\KeyFalcon\geosentinelforestwatch\frontend
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

---

## Step 5: Open Browser

Navigate to: **http://localhost:5173**

You should see the GeoSentinel Forest Watch dashboard!

---

## Quick Test

1. Select dates:
   - Before: 2023-01-01
   - After: 2024-01-01

2. Click "Analyze Deforestation"

3. Wait ~30 seconds for processing

4. View results:
   - Before/After satellite images
   - Deforestation metrics
   - AI-powered analysis

---

## Troubleshooting

### "conda not recognized"
- Use **Anaconda Prompt** instead of PowerShell
- Or run: `C:\Users\prady\miniconda3\Scripts\conda.exe init powershell`

### "GEMINI_API_KEY not set"
- Edit `.env` file
- Add your API key from https://makersuite.google.com/app/apikey

### "Module not found"
- Make sure conda environment is activated: `conda activate geosentinel`
- Reinstall packages: `pip install flask flask-cors python-dotenv google-generativeai`

### Backend won't start
- Check if port 5000 is available
- Try changing FLASK_PORT in `.env` to 5001

---

## Next Steps

Once both servers are running:
1. Open http://localhost:5173
2. Test the deforestation analysis
3. Explore the code
4. Customize for your needs!

---

**Need help?** Let me know which step you're on!
