"""
Automated GDAL and Rasterio Installer for Windows
Downloads and installs pre-built wheels automatically
"""
import sys
import subprocess
import platform
import urllib.request
from pathlib import Path

def get_python_version():
    """Get Python version tag (e.g., cp310 for Python 3.10)"""
    version_info = sys.version_info
    return f"cp{version_info.major}{version_info.minor}"

def get_architecture():
    """Get system architecture"""
    arch = platform.machine().lower()
    if 'amd64' in arch or 'x86_64' in arch:
        return 'win_amd64'
    else:
        return 'win32'

def download_file(url, destination):
    """Download file from URL"""
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, destination)
        print(f"✓ Downloaded to {destination}")
        return True
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False

def install_wheel(wheel_path):
    """Install a wheel file"""
    print(f"Installing {wheel_path}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", str(wheel_path)])
        print(f"✓ Installed {wheel_path}")
        return True
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        return False

def main():
    print("=" * 60)
    print("GDAL & Rasterio Installer for Windows")
    print("=" * 60)
    
    # Get system info
    py_version = get_python_version()
    arch = get_architecture()
    
    print(f"\nDetected:")
    print(f"  Python version: {sys.version.split()[0]}")
    print(f"  Version tag: {py_version}")
    print(f"  Architecture: {arch}")
    
    # Create downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # Define wheel URLs (using GitHub releases from cgohlke/geospatial-wheels)
    base_url = "https://github.com/cgohlke/geospatial-wheels/releases/download/v2024.2.18"
    
    wheels = {
        "GDAL": f"GDAL-3.8.4-{py_version}-{py_version}-{arch}.whl",
        "rasterio": f"rasterio-1.3.9-{py_version}-{py_version}-{arch}.whl"
    }
    
    print("\n" + "=" * 60)
    print("Step 1: Downloading Wheels")
    print("=" * 60)
    
    downloaded_wheels = {}
    
    for name, filename in wheels.items():
        url = f"{base_url}/{filename}"
        dest = downloads_dir / filename
        
        if dest.exists():
            print(f"✓ {filename} already downloaded")
            downloaded_wheels[name] = dest
        else:
            if download_file(url, dest):
                downloaded_wheels[name] = dest
            else:
                print(f"\n⚠️  Failed to download {name}")
                print(f"Please download manually from:")
                print(f"  {url}")
                print(f"And place in: {downloads_dir}")
                return False
    
    print("\n" + "=" * 60)
    print("Step 2: Installing Wheels")
    print("=" * 60)
    
    # Install GDAL first (rasterio depends on it)
    if "GDAL" in downloaded_wheels:
        if not install_wheel(downloaded_wheels["GDAL"]):
            print("\n✗ GDAL installation failed")
            return False
    
    # Install rasterio
    if "rasterio" in downloaded_wheels:
        if not install_wheel(downloaded_wheels["rasterio"]):
            print("\n✗ Rasterio installation failed")
            return False
    
    print("\n" + "=" * 60)
    print("Step 3: Installing Additional Geospatial Libraries")
    print("=" * 60)
    
    additional_packages = ["geopandas", "shapely", "fiona", "pyproj", "sentinelsat"]
    
    for package in additional_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except Exception as e:
            print(f"⚠️  Failed to install {package}: {e}")
    
    print("\n" + "=" * 60)
    print("Step 4: Verification")
    print("=" * 60)
    
    # Verify installation
    try:
        import rasterio
        import geopandas
        print("✓ Rasterio imported successfully")
        print("✓ GeoPandas imported successfully")
        print(f"✓ GDAL version: {rasterio.__gdal_version__}")
        print(f"✓ Rasterio version: {rasterio.__version__}")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Installation Complete!")
    print("=" * 60)
    print("\nYou can now use real Sentinel-2 data!")
    print("\nNext steps:")
    print("1. Configure Sentinel API credentials in .env")
    print("2. Run: cd backend && python api.py")
    print("3. Start frontend: cd frontend && npm run dev")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
