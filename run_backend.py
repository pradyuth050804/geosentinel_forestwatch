"""
Launcher script for backend API
Ensures we're in the correct directory before starting
"""
import os
import sys
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()

# Change to the script directory (project root)
os.chdir(script_dir)

# Add project root to Python path
sys.path.insert(0, str(script_dir))

# Now import and run the backend API
backend_dir = script_dir / "backend"
os.chdir(backend_dir)

# Import the api module
sys.path.insert(0, str(backend_dir))

# Run the API
exec(open(backend_dir / "api.py").read())
