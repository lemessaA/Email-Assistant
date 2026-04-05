from sqlalchemy.orm import Session
from src.database.models import UserSettings

def get_user_settings(db: Session, user_id: int = 1):
    settings = db.query(UserSettings).filter(UserSettings.id == user_id).first()
    if not settings:
        # Create default
        settings = UserSettings(id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_user_settings(db: Session, user_settings_data: dict, user_id: int = 1):
    settings = get_user_settings(db, user_id)
    for key, value in user_settings_data.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings
