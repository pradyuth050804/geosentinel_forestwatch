"""
Sentinel-2 Image Retrieval using Copernicus Data Space Ecosystem OAuth2 API
"""
import requests
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
import zipfile
import io

logger = logging.getLogger(__name__)

class SentinelImageRetriever:
    """Retrieve Sentinel-2 imagery from Copernicus Data Space Ecosystem using OAuth2"""
    
    def __init__(self, username: str, password: str, cache_dir: Path):
        """
        Initialize Sentinel-2 retriever with OAuth2 authentication
        
        Args:
            username: Copernicus Data Space username
            password: Copernicus Data Space password
            cache_dir: Directory for caching downloaded images
        """
        self.username = username
        self.password = password
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.catalogue_url = "https://catalogue.dataspace.copernicus.eu/odata/v1"
        self.download_url = "https://zipper.dataspace.copernicus.eu/odata/v1"
        
        self.access_token = None
        self.token_expires_at = None
        
        logger.info("Initialized Copernicus Data Space API client")
    
    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token
        
        Returns:
            Access token string
        """
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # Get new token
        logger.info("Obtaining OAuth2 access token...")
        
        token_data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "client_id": "cdse-public"
        }
        
        try:
            response = requests.post(self.token_url, data=token_data, timeout=30)
            response.raise_for_status()
            
            token_info = response.json()
            self.access_token = token_info['access_token']
            
            # Set expiration time (subtract 60 seconds for safety)
            expires_in = token_info.get('expires_in', 1800)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            logger.info(f"Access token obtained (expires in {expires_in} seconds)")
            return self.access_token
            
        except Exception as e:
            logger.error(f"Failed to obtain access token: {e}")
            raise
    
    def query_images(self, 
                     geometry, 
                     date: str, 
                     date_window: int = 7,
                     max_cloud_cover: float = 100) -> List[Dict]:
        """
        Query Sentinel-2 images for a given date and geometry
        
        Args:
            geometry: Shapely geometry
            date: Target date (YYYY-MM-DD)
            date_window: Days before/after to search
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            List of product dictionaries
        """
        logger.info(f"Querying Sentinel-2 products for {date}")
        
        # Get access token
        token = self._get_access_token()
        
        # Get bounding box
        minx, miny, maxx, maxy = geometry.bounds
        
        # Build OData filter query
        polygon_wkt = f"POLYGON(({minx} {miny}, {maxx} {miny}, {maxx} {maxy}, {minx} {maxy}, {minx} {miny}))"
        
        # Parse date and create date range
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        if date_window == 0:
            # Exact date match: Cover the full 24 hours of that day
            start_date = target_date
            end_date = target_date + timedelta(days=1) - timedelta(seconds=1)
        else:
            # Window search around the date
            start_date = target_date - timedelta(days=date_window)
            end_date = target_date + timedelta(days=date_window)
        
        filter_query = (
            f"Collection/Name eq 'SENTINEL-2' and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{polygon_wkt}') and "
            f"ContentDate/Start ge {start_date.isoformat()}Z and "
            f"ContentDate/Start le {end_date.isoformat()}Z and "
            f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt {max_cloud_cover})"
        )
        
        params = {
            "$filter": filter_query,
            "$top": 10,
            "$orderby": "ContentDate/Start desc"
        }
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.get(
                f"{self.catalogue_url}/Products",
                params=params,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            results = response.json()
            products = results.get('value', [])
            
            logger.info(f"Found {len(products)} products")
            
            return products
            
        except Exception as e:
            logger.error(f"Error querying products: {e}")
            return []
    
    def download_product(self, product_id: str, output_path: Path) -> Path:
        """
        Download a Sentinel-2 product
        
        Args:
            product_id: Product UUID
            output_path: Where to save the downloaded product
            
        Returns:
            Path to downloaded product directory
        """
        logger.info(f"Downloading product: {product_id}")
        
        # Get access token
        token = self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Download URL
        download_url = f"{self.download_url}/Products({product_id})/$value"
        
        try:
            # Stream download
            response = requests.get(download_url, headers=headers, stream=True, timeout=300)
            response.raise_for_status()
            
            # Save to zip file
            zip_path = output_path.parent / f"{product_id}.zip"
            
            total_size = int(response.headers.get('content-length', 0))
            logger.info(f"Downloading {total_size / 1024 / 1024:.2f} MB...")
            
            with open(zip_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and downloaded % (10 * 1024 * 1024) == 0:  # Log every 10MB
                            progress = (downloaded / total_size) * 100
                            logger.info(f"Download progress: {progress:.1f}%")
            
            logger.info("Download complete, extracting...")
            
            # Extract zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_path.parent)
            
            # Remove zip file
            zip_path.unlink()
            
            # Find extracted .SAFE directory
            safe_dirs = list(output_path.parent.glob("*.SAFE"))
            if safe_dirs:
                return safe_dirs[0]
            else:
                raise FileNotFoundError("Could not find extracted .SAFE directory")
                
        except Exception as e:
            logger.error(f"Error downloading product: {e}")
            raise
    
    def download_product_robust(self, product_id: str, output_dir: Path, product_name: str) -> Path:
        """Download product with retries and strict validation"""
        import time
        import zipfile
        import shutil
        
        logger.info(f"Downloading product: {product_name} ({product_id})")
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        download_url = f"{self.download_url}/Products({product_id})/$value"
        zip_path = output_dir / f"{product_name}.zip"
        target_dir = output_dir / f"{product_name}.SAFE"
        
        for attempt in range(3):
            try:
                if attempt > 0: 
                    logger.info(f"Retry attempt {attempt+1}...")
                    time.sleep(5)
                    
                response = requests.get(download_url, headers=headers, stream=True, timeout=300)
                response.raise_for_status()
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk: f.write(chunk)
                        
                if target_dir.exists(): shutil.rmtree(target_dir)
                
                # Inspect zip content to find the root folder name
                extracted_dir_name = None
                with zipfile.ZipFile(zip_path, 'r') as z:
                    # Get the root directory from the zip content
                    # Sentinel-2 zips always have a single root folder like 'S2A_...SAFE/'
                    file_list = z.namelist()
                    if file_list:
                        # Get the first item's root path
                        extracted_dir_name = file_list[0].split('/')[0]
                    
                    z.extractall(output_dir)
                    
                if zip_path.exists(): zip_path.unlink()
                
                # Check the detected root folder
                if extracted_dir_name:
                    target_dir = output_dir / extracted_dir_name
                    if target_dir.exists():
                        logger.info(f"Extracted to: {target_dir.name}")
                        return target_dir

                # Fallback: strict name check (old logic)
                target_dir = output_dir / f"{product_name}.SAFE"
                if target_dir.exists(): return target_dir
                
                # Fallback: Glob search
                candidates = list(output_dir.glob(f"*{product_name}*.SAFE"))
                if candidates: return candidates[0]
                
                # Fallback: Check for ANY SAFE directory created? No, too risky if concurrent.
                # But since we use introspection, we should be good.
                
                raise FileNotFoundError(f"SAFE directory not found. Expected {product_name}.SAFE or {extracted_dir_name}")
                
            except Exception as e:
                logger.error(f"Download error: {e}")
                if zip_path.exists(): zip_path.unlink()
                if attempt == 2: raise

    def _extract_rgb_bands(self, product_dir: Path, geometry, output_path: Path) -> Path:
        """
        Extract RGB bands from Sentinel-2 product and create composite
        Supports both L1C and L2A products
        
        Args:
            product_dir: Path to downloaded .SAFE directory
            geometry: Shapely geometry for clipping
            output_path: Where to save the RGB composite
            
        Returns:
            Path to created RGB GeoTIFF
        """
        logger.info("Extracting RGB bands from Sentinel-2 product...")
        
        # Sentinel-2 RGB band mapping
        # B04 = Red, B03 = Green, B02 = Blue
        band_files = {
            'red': None,
            'green': None,
            'blue': None
        }
        
        # Find band files
        img_data_dir = product_dir / "GRANULE"
        
        if not img_data_dir.exists():
            raise FileNotFoundError(f"GRANULE directory not found in {product_dir}")
        
        # Find the granule directory (L2A or L1C)
        granule_dirs = list(img_data_dir.glob("L2A_*")) + list(img_data_dir.glob("L1C_*"))
        
        if not granule_dirs:
            raise FileNotFoundError(f"No granule directory found in {img_data_dir}")
        
        granule_dir = granule_dirs[0]
        logger.info(f"Using granule: {granule_dir.name}")
        
        img_dir = granule_dir / "IMG_DATA"
        if not img_dir.exists():
            raise FileNotFoundError(f"IMG_DATA directory not found in {granule_dir}")
        
        # Try different locations for bands
        search_dirs = []
        
        # For L2A: bands are in R10m folder
        r10m_dir = img_dir / "R10m"
        if r10m_dir.exists():
            search_dirs.append(r10m_dir)
            logger.info("Found R10m folder (L2A product)")
        
        # For L1C: bands are directly in IMG_DATA
        search_dirs.append(img_dir)
        
        # Search for band files with different naming patterns
        for search_dir in search_dirs:
            if not band_files['red']:
                # Try different patterns
                patterns = [
                    "*_B04_10m.jp2",  # L2A pattern
                    "*_B04.jp2",       # L1C pattern
                    "T*_B04.jp2"       # Alternative pattern
                ]
                for pattern in patterns:
                    matches = list(search_dir.glob(pattern))
                    if matches:
                        band_files['red'] = matches[0]
                        break
            
            if not band_files['green']:
                patterns = ["*_B03_10m.jp2", "*_B03.jp2", "T*_B03.jp2"]
                for pattern in patterns:
                    matches = list(search_dir.glob(pattern))
                    if matches:
                        band_files['green'] = matches[0]
                        break
            
            if not band_files['blue']:
                patterns = ["*_B02_10m.jp2", "*_B02.jp2", "T*_B02.jp2"]
                for pattern in patterns:
                    matches = list(search_dir.glob(pattern))
                    if matches:
                        band_files['blue'] = matches[0]
                        break
            
            # If all bands found, stop searching
            if all(band_files.values()):
                break
        
        # Verify all bands found
        if not all(band_files.values()):
            missing = [k for k, v in band_files.items() if v is None]
            logger.error(f"Could not find RGB bands: {missing}")
            logger.error(f"Searched in: {[str(d) for d in search_dirs]}")
            
            # List available files for debugging
            logger.error("Available .jp2 files:")
            for search_dir in search_dirs:
                for f in search_dir.glob("*.jp2"):
                    logger.error(f"  - {f.name}")
            
            raise FileNotFoundError(f"Could not find RGB bands: {missing}")
        
        logger.info(f"Found RGB bands:")
        logger.info(f"  Red:   {band_files['red'].name}")
        logger.info(f"  Green: {band_files['green'].name}")
        logger.info(f"  Blue:  {band_files['blue'].name}")
        
        # Read JP2 files using PIL (Pillow) which has better JP2 support
        from PIL import Image
        import io
        
        logger.info("Reading JP2 files with PIL/Pillow...")
        
        try:
            # Read each band with PIL
            red_img = Image.open(band_files['red'])
            green_img = Image.open(band_files['green'])
            blue_img = Image.open(band_files['blue'])
            
            logger.info(f"Successfully opened JP2 files")
            logger.info(f"  Image size: {red_img.size}")
            logger.info(f"  Image mode: {red_img.mode}")
            
            # Convert to numpy arrays
            red = np.array(red_img)
            green = np.array(green_img)
            blue = np.array(blue_img)
            
            # Stack into RGB
            rgb = np.stack([red, green, blue], axis=0)
            
            logger.info(f"Created RGB stack: {rgb.shape}")
            
            # Get georeferencing from one of the original JP2 files using rasterio
            # (rasterio can read metadata even if it can't read pixel data)
            try:
                with rasterio.open(band_files['red']) as src:
                    transform = src.transform
                    crs = src.crs
                    logger.info(f"Got georeferencing: CRS={crs}")
            except:
                # If rasterio fails, create a simple transform
                logger.warning("Could not read georeferencing, using default")
                from rasterio.transform import from_bounds
                # Use approximate bounds for the area
                minx, miny, maxx, maxy = geometry.bounds
                transform = from_bounds(minx, miny, maxx, maxy, rgb.shape[2], rgb.shape[1])
                crs = 'EPSG:4326'
            
            # Write RGB composite as GeoTIFF
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=rgb.shape[1],
                width=rgb.shape[2],
                count=3,
                dtype=rgb.dtype,
                crs=crs,
                transform=transform
            ) as dst:
                dst.write(rgb)
            
            logger.info(f"Created RGB composite: {output_path}")
            
        except Exception as e:
            logger.error(f"Error reading JP2 files with PIL: {e}")
            logger.error("Trying alternative method with gdal_translate...")
            
            # Fallback: try gdal_translate
            import subprocess
            converted_files = {}
            temp_dir = output_path.parent / "temp_bands"
            temp_dir.mkdir(exist_ok=True)
            
            for band_name, jp2_file in band_files.items():
                tif_file = temp_dir / f"{jp2_file.stem}.tif"
                
                if not tif_file.exists():
                    logger.info(f"Converting {jp2_file.name} to GeoTIFF...")
                    cmd = ['gdal_translate', '-of', 'GTiff', '-co', 'COMPRESS=LZW', str(jp2_file), str(tif_file)]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    if result.returncode != 0:
                        logger.error(f"gdal_translate stderr: {result.stderr}")
                        raise RuntimeError(f"Failed to convert {jp2_file.name}: {result.stderr}")
                
                converted_files[band_name] = tif_file
            
            # Read converted files
            with rasterio.open(converted_files['red']) as red_src:
                meta = red_src.meta.copy()
                red = red_src.read(1)
                
                with rasterio.open(converted_files['green']) as green_src:
                    green = green_src.read(1)
                
                with rasterio.open(converted_files['blue']) as blue_src:
                    blue = blue_src.read(1)
                
                rgb = np.stack([red, green, blue], axis=0)
                
                meta.update({'count': 3, 'dtype': 'uint16', 'driver': 'GTiff'})
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with rasterio.open(output_path, 'w', **meta) as dst:
                    dst.write(rgb)
                
                logger.info(f"Created RGB composite: {output_path}")
            
        return output_path
    
    def get_image_for_date(self, geometry, date: str) -> Optional[Path]:
        """
        Get REAL Sentinel-2 image for a specific date from Copernicus API
        
        Args:
            geometry: Shapely geometry
            date: Target date (YYYY-MM-DD)
            
        Returns:
            Path to GeoTIFF image (REAL satellite data only)
        """
        # Generate cache filename
        date_str = date.replace("-", "")
        cache_file = self.cache_dir / f"sentinel2_{date_str}.tif"
        
        # Check cache first
        if cache_file.exists():
            logger.info(f"Using cached image: {cache_file}")
            return cache_file
            
        # CRITICAL FIX: Check for local SAFE directory before querying API
        # This allows working with cached data even if internet/query fails
        try:
            local_safe_files = list(self.cache_dir.glob(f"*{date_str}*.SAFE"))
            if local_safe_files:
                logger.info(f"Found local SAFE directory for {date}: {local_safe_files[0].name}")
                # Use the first match directly
                rgb_image = self._extract_rgb_bands(local_safe_files[0], geometry, cache_file)
                return rgb_image
        except Exception as e:
            logger.error(f"Error checking local SAFE files: {e}")
            # Continue to query if this fails
        
        # Download REAL Sentinel-2 data (NO MOCK DATA ALLOWED)
        # Use window=0 to ensure we get the EXACT date requested, avoiding "same image" bug
        products = self.query_images(geometry, date, date_window=0)
        
        if not products:
            logger.error(f"No Sentinel-2 products found for {date}")
            raise ValueError(f"No Sentinel-2 imagery available for {date}")
        
        # Download best product (first one, already sorted by date)
        product = products[0]
        product_id = product['Id']
        product_name = product['Name']
        
        logger.info(f"Selected product: {product_name}")
        logger.info(f"Date: {product['ContentDate']['Start']}")
        logger.info(f"Cloud cover: {product.get('CloudCover', 'unknown')}%")
        
        # Check if already downloaded
        product_dir = self.cache_dir / f"{product_name}.SAFE"
        
        if not product_dir.exists():
            # Download product
            product_dir = self.download_product_robust(product_id, self.cache_dir, product_name)
        else:
            logger.info(f"Product already downloaded: {product_dir}")
        
        # Extract RGB bands and create composite
        rgb_image = self._extract_rgb_bands(product_dir, geometry, cache_file)
        
        return rgb_image
