from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    from_email = Column(String, nullable=False)
    to_email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    response_generated = Column(Text, nullable=True)

class EmailHistory(Base):
    __tablename__ = "email_history"
    
    id = Column(Integer, primary_key=True, index=True)
    original_email_id = Column(Integer, nullable=False)
    response = Column(Text, nullable=False)
    processing_time = Column(Integer, nullable=False)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)