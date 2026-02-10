#!/usr/bin/env python3
"""
Production Deployment Script

This script sets up the email assistant for production deployment.
It validates environment, creates necessary directories,
and starts the production server with proper configuration.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.production_config import validate_production_environment, production_settings
from api.main import app
import uvicorn

def setup_logging():
    """Setup production logging configuration"""
    from core.production_config import get_logging_config
    
    config = get_logging_config()
    
    # Create logs directory
    log_dir = Path(config["file"]).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config["level"]),
        format=config["format"],
        handlers=[
            logging.FileHandler(config["file"]),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Production logging configured")

def setup_directories():
    """Create necessary directories for production"""
    from core.production_config import get_file_config
    
    config = get_file_config()
    
    # Create required directories
    directories = [
        config["knowledge_base_path"],
        config["drafts_path"],
        config["attachments_path"],
        Path(config["file"]).parent,
        Path("./data"),
        Path("./logs")
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def validate_environment():
    """Validate production environment before starting"""
    print("🔍 Validating production environment...")
    
    if not validate_production_environment():
        print("❌ Production environment validation failed!")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    print("✅ Production environment validated successfully")

def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "langchain",
        "langchain_ollama",
        "langgraph",
        "pydantic",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install missing packages with: pip install " + " ".join(missing_packages))
        sys.exit(1)
    
    print("✅ All required dependencies are available")

def check_services():
    """Check if external services are available"""
    from core.production_config import get_llm_config, get_search_config
    
    llm_config = get_llm_config()
    
    # Check Ollama service
    try:
        import requests
        response = requests.get(f"{llm_config['base_url']}/api/tags", timeout=5)
        if response.status_code == 200:
            print(f"✅ Ollama service is running at {llm_config['base_url']}")
        else:
            print(f"⚠️  Ollama service may not be running at {llm_config['base_url']}")
            print("Please ensure Ollama is running: ollama serve")
    except Exception as e:
        print(f"⚠️  Cannot check Ollama service: {str(e)}")
    
    # Check database connectivity
    try:
        from database.connection import get_db_connection
        conn = get_db_connection()
        conn.execute("SELECT 1")  # Simple test query
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")

def create_startup_banner():
    """Create startup banner with production information"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                              ║
║           🚀 EMAIL ASSISTANT PRODUCTION SERVER              ║
║                                                              ║
║  Version: 1.0.0                                           ║
║  Mode: Production                                           ║
║  LLM: {model}                                          ║
║  API: http://{host}:{port}                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════╝
    """.format(
        model=production_settings.PRIMARY_LLM,
        host=production_settings.API_HOST,
        port=production_settings.API_PORT
    )
    
    print(banner)

def main():
    """Main deployment function"""
    print("🚀 Starting Email Assistant Production Deployment...")
    
    # Validate environment
    validate_environment()
    
    # Check dependencies
    check_dependencies()
    
    # Check external services
    check_services()
    
    # Setup directories
    setup_directories()
    
    # Setup logging
    setup_logging()
    
    # Create startup banner
    create_startup_banner()
    
    # Get production configuration
    from core.production_config import get_api_config
    api_config = get_api_config()
    
    # Start production server
    print(f"🌐 Starting production server on {api_config['host']}:{api_config['port']}")
    
    try:
        uvicorn.run(
            app=app,
            host=api_config["host"],
            port=api_config["port"],
            workers=api_config["workers"],
            reload=api_config["reload"],
            log_level="info",
            access_log=True,
            use_colors=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
