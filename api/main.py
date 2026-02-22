import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import FastAPI app
from src.api.main import app

# Vercel serverless function
def handler(request):
    """
    Vercel serverless function handler
    """
    return app

# Export for Vercel
handler = app
