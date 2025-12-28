# 🚀 Deployment Guide: GeoSentinel Forest Watch

This guide walks you through deploying your full-stack application for free using **Render** (Backend) and **Vercel** (Frontend).

## Prerequisites
- GitHub Account
- This project pushed to a GitHub repository

---

## Part 1: Deploy Backend to Render (Free)

1.  **Sign up/Login** to [Render](https://render.com/).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  **Configure the Service**:
    -   **Name**: `geosentinel-backend` (or similar)
    -   **Region**: Closest to you (e.g., Singapore, Frankfurt)
    -   **Branch**: `main`
    -   **Runtime**: **Docker** (Select "Docker" as the runtime environment)
    -   **Instance Type**: **Free**
5.  **Environment Variables** (Scroll down to "Environment"):
    Add these keys from your `.env` file (copy values from your local `.env`):
    -   `GEMINI_API_KEY`: `...`
    -   `COPERNICUS_USERNAME`: `...`
    -   `COPERNICUS_PASSWORD`: `...`
    -   `SENTINEL_HUB_CLIENT_ID`: `...`
    -   `SENTINEL_HUB_CLIENT_SECRET`: `...`
    -   `FLASK_SECRET_KEY`: (Any random string)
    -   `FLASK_ENV`: `production`
6.  Click **Create Web Service**.
    -   *Note*: The first build will take 5-10 minutes because it's installing GDAL.
    -   Once deployed, copy your **backend URL** (e.g., `https://geosentinel-backend.onrender.com`).

---

## Part 2: Deploy Frontend to Vercel (Free)

1.  **Sign up/Login** to [Vercel](https://vercel.com/).
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repository.
4.  **Configure Project**:
    -   **Framework Preset**: Vite (should be auto-detected)
    -   **Root Directory**: Click "Edit" and select `frontend`.
5.  **Environment Variables**:
    -   Key: `VITE_API_URL`
    -   Value: Your **Render Backend URL** (from Part 1) -> e.g., `https://geosentinel-backend.onrender.com`
    -   *Important*: Do NOT add a trailing slash `/`.
6.  Click **Deploy**.

---

## Part 3: Verification

1.  Open your Vercel URL.
2.  Try to "Analyze" a date range.
3.  **Note on Free Tier Limits**:
    -   **Cold Starts**: If the backend hasn't been used in 15 mins, the first request might take 50+ seconds.
    -   **Data Persistence**: Images created will deleted after the backend restarts.
