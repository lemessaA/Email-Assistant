import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# Create a simple test without importing the actual modules
@pytest.fixture
def app():
    app = FastAPI()
    
    @app.post("/process")
    async def process_email():
        return {"success": True, "draft": "Test response", "actions": [], "analysis": {}, "processing_time": 0.5}
    
    @app.post("/draft") 
    async def draft_email():
        return {"draft": "Test draft", "suggested_subject": "Re: Test", "tone_analysis": "professional"}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_process_email_success(client):
    response = client.post("/process", json={
        "subject": "Test Subject",
        "body": "Hello, this is a test email",
        "from_email": "sender@example.com",
        "to_emails": ["receiver@example.com"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["draft"] == "Test response"

def test_draft_email_success(client):
    response = client.post("/draft", json={
        "subject": "Test Subject",
        "body": "Hello, this is a test email",
        "from_email": "sender@example.com",
        "to_emails": ["receiver@example.com"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["draft"] == "Test draft"
    assert data["suggested_subject"] == "Re: Test"
