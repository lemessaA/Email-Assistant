from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.crud import get_user_settings, update_user_settings

router = APIRouter()

class SettingsSchema(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    imap_server: Optional[str] = None
    imap_port: Optional[int] = 993
    email_user: Optional[str] = None
    email_password: Optional[str] = None

@router.get("/")
def read_settings(db: Session = Depends(get_db)):
    settings = get_user_settings(db)
    return {
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_username": settings.smtp_username,
        "smtp_password": settings.smtp_password,
        "imap_server": settings.imap_server,
        "imap_port": settings.imap_port,
        "email_user": settings.email_user,
        "email_password": settings.email_password,
    }

@router.post("/")
def write_settings(settings_data: SettingsSchema, db: Session = Depends(get_db)):
    updated = update_user_settings(db, settings_data.model_dump(exclude_unset=True))
    return {"message": "Settings updated successfully", "success": True}
