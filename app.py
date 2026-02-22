"""
FastAPI app entrypoint for Vercel deployment
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the actual FastAPI app
from src.api.main import app

# Export for Vercel
app = app
