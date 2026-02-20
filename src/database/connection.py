from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.database.models import Base
import os

def init_db():
    """Initialize database connection"""
    # Ensure the directory exists for SQLite
    db_path = settings.database_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine

def get_db():
    """Get database session"""
    engine = init_db()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()