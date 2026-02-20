import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import your router module
from api.routes.email import router, EmailAssistantAgent


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sample_request():
    return {
        "subject": "Test Subject",
        "body": "Hello, this is a test email",
        "from_email": "sender@example.com",
        "to_emails": ["receiver@example.com"],
        "cc_emails": [],
        "attachments": None,
        "priority": "normal",
        "metadata": {}
    }


def test_process_email_success(client, sample_request):
    mock_result = {
        "response": "Draft response",
        "actions_taken": [{"type": "reply"}],
        "analysis": {"tone": "neutral"}
    }

    with patch.object(
        EmailAssistantAgent,
        "process_email",
        new=AsyncMock(return_value=mock_result),
    ):
        response = client.post("/process", json=sample_request)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["draft"] == "Draft response"
    assert data["actions"] == [{"type": "reply"}]
    assert data["analysis"]["tone"] == "neutral"


def test_process_email_failure(client, sample_request):
    with patch.object(
        EmailAssistantAgent,
        "process_email",
        new=AsyncMock(side_effect=Exception("Processing failed")),
    ):
        response = client.post("/process", json=sample_request)

    assert response.status_code == 500
    assert "Processing failed" in response.json()["detail"]


def test_draft_email_success(client, sample_request):
    mock_result = {
        "response": "Generated draft",
        "analysis": {"tone": "professional"}
    }

    with patch.object(
        EmailAssistantAgent,
        "process_email",
        new=AsyncMock(return_value=mock_result),
    ):
        response = client.post("/draft", json=sample_request)

    assert response.status_code == 200
    data = response.json()
    assert data["draft"] == "Generated draft"
    assert data["suggested_subject"] == f"Re: {sample_request['subject']}"
    assert data["tone_analysis"] == "professional"