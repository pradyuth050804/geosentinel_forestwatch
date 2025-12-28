# Dockerfile for GeoSentinel Backend

# Use an official Python runtime with GDAL support
# ghcr.io/osgeo/gdal:ubuntu-small-latest provides a good base with GDAL pre-installed
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.9.0

# Set working directory
WORKDIR /app

# Install system dependencies (if any extra are needed)
# python3-pip is often needed if not included in base
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .
COPY backend/requirements-minimal.txt .
COPY backend/requirements-simple.txt .

# Install Python dependencies
# We use requirements-minimal.txt or requirements.txt depending on what we want
# Ideally, we merge them or pick one. Let's assume requirements.txt is the main one.
# If there are conflicts with system GDAL, we might need to handle them.
# Using --break-system-packages might be needed on newer Python versions in these images
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# Copy the rest of the application
COPY . .

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV FLASK_APP=backend/api.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port (Render sets PORT env var, but we expose 5000 as default documentation)
EXPOSE 5000

# Run the application
# We use standard flask run or gunicorn if available
# For now, using python to run api.py which invokes app.run()
# Switch to simplified API to save memory (Render Free Tier Limit: 512MB)
CMD ["python3", "backend/api_simple.py"]
