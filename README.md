# GeoSentinel Forest Watch 🌲

**AI-Powered Deforestation Detection using Sentinel-2 Satellite Imagery**

A complete geospatial application that detects, quantifies, and explains deforestation between two dates using TensorFlow computer vision and Google Gemini AI.

---

## 🎯 Features

- **Satellite Imagery Retrieval**: Automated Sentinel-2 image acquisition via API
- **AI-Powered Detection**: TensorFlow Siamese CNN for pixel-level change detection
- **Deforestation Quantification**: Precise area calculations and patch analysis
- **Visual Highlights**: Color-coded deforestation maps (red=loss, yellow=degradation, green=intact)
- **AI Explanations**: Gemini-powered textual analysis of detected changes
- **Modern UI**: Clean, responsive dashboard with real-time progress tracking

---

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **API Credentials**:
  - Copernicus Data Space account (free) OR Sentinel Hub API
  - Google Gemini API key

---

## 🚀 Installation

### 1. Clone and Setup

```bash
cd d:\KeyFalcon\geosentinelforestwatch
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Configuration

Copy `.env.example` to `.env` and add your API credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Sentinel API (choose one)
COPERNICUS_USERNAME=your_username
COPERNICUS_PASSWORD=your_password

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Optional: adjust processing parameters
MAX_CLOUD_COVER=20
DEFORESTATION_THRESHOLD=0.5
```

---

## 🎮 Usage

### Start Backend API

```bash
cd backend
python api.py
```

Backend runs on `http://localhost:5000`

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:5173`

### Analyze Deforestation

1. Open `http://localhost:5173` in your browser
2. Select **Before Date** (e.g., 2023-01-01)
3. Select **After Date** (e.g., 2024-01-01)
4. Click **Analyze Deforestation**
5. Wait for processing (2-5 minutes)
6. View results:
   - Before/After satellite images
   - Deforestation highlight map
   - Quantitative metrics
   - AI-generated explanation

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Shankar SF.kml │ (Forest Boundary)
└────────┬────────┘
         ↓
┌─────────────────┐
│ Sentinel-2 API  │ (Image Retrieval)
└────────┬────────┘
         ↓
┌─────────────────┐
│ Image Processor │ (Clipping, Normalization)
└────────┬────────┘
         ↓
┌─────────────────┐
│ TensorFlow CNN  │ (Deforestation Detection)
└────────┬────────┘
         ↓
┌─────────────────┐
│  Visualization  │ (Highlight Image)
└────────┬────────┘
         ↓
┌─────────────────┐
│   Gemini API    │ (Textual Explanation)
└────────┬────────┘
         ↓
┌─────────────────┐
│   Modern UI     │ (Results Dashboard)
└─────────────────┘
```

---

## 📁 Project Structure

```
geosentinelforestwatch/
├── backend/
│   ├── api.py                    # Flask REST API
│   ├── config.py                 # Configuration management
│   ├── services/
│   │   ├── kml_processor.py      # KML boundary parsing
│   │   ├── sentinel_api.py       # Satellite imagery retrieval
│   │   ├── image_processor.py    # Image preprocessing
│   │   ├── visualization.py      # Deforestation highlights
│   │   └── gemini_service.py     # AI explanations
│   ├── ml/
│   │   ├── deforestation_model.py # TensorFlow Siamese CNN
│   │   └── change_detector.py     # Detection orchestrator
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main React app
│   │   ├── components/
│   │   │   ├── ImagePanel.jsx
│   │   │   ├── MetricsCards.jsx
│   │   │   └── InsightsPanel.jsx
│   │   └── styles.css
│   ├── index.html
│   └── package.json
├── data/
│   ├── cache/                    # Downloaded imagery
│   └── outputs/                  # Generated results
├── Shankar SF.kml                # Forest boundary (INPUT)
└── .env                          # API credentials
```

---

## 🔧 API Endpoints

### `POST /api/analyze`
Start deforestation analysis

**Request:**
```json
{
  "date_before": "2023-01-01",
  "date_after": "2024-01-01"
}
```

**Response:**
```json
{
  "status": "success",
  "job_id": "uuid-here"
}
```

### `GET /api/status/{job_id}`
Check analysis status

**Response:**
```json
{
  "status": "processing",
  "progress": 75
}
```

### `GET /api/results/{job_id}`
Get analysis results

**Response:**
```json
{
  "metrics": { ... },
  "explanation": { ... },
  "images": { ... }
}
```

---

## 🧪 Development Mode

The system includes **mock data generation** for development without API credentials:

- Synthetic Sentinel-2 imagery
- Rule-based change detection (fallback)
- Simulated deforestation patterns

To use mock data, simply leave API credentials empty in `.env`.

---

## 📊 Output Files

All outputs are saved to `data/outputs/`:

- `forest_Tprev.png` - Before image
- `forest_T0.png` - After image
- `deforestation_highlight.png` - Color-coded change map
- `deforestation_probability.npy` - Probability map (NumPy array)
- `deforestation_mask.npy` - Binary mask (NumPy array)
- `metrics.json` - Quantitative metrics

---

## 🎨 Color Coding

- 🔴 **Red**: Confirmed deforestation (>70% probability)
- 🟡 **Yellow**: Possible degradation (40-70% probability)
- 🟢 **Green**: Intact forest (<40% probability)
- ⚪ **White**: Forest boundary outline

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set"
Add your Gemini API key to `.env` file

### "No Sentinel API credentials"
Add Copernicus or Sentinel Hub credentials to `.env`

### Black images
Check that imagery is being downloaded correctly. Use mock data mode for testing.

### Model errors
Ensure TensorFlow is installed: `pip install tensorflow`

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using TensorFlow, React, and Google Gemini AI**
