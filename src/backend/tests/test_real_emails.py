#!/usr/bin/env python3
"""
Test the Email Assistant app with real sender and recipient emails.
Uses the /draft and /process API endpoints.

Usage:
    python scripts/test_real_emails.py SENDER_EMAIL RECIPIENT_EMAIL

Example:
    python scripts/test_real_emails.py john@gmail.com jane@outlook.com

Or set via env:
    SENDER_EMAIL=john@gmail.com RECIPIENT_EMAIL=jane@outlook.com python scripts/test_real_emails.py
"""

import os
import sys
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE = os.environ.get("API_URL", "http://localhost:8000")

SAMPLE_EMAIL = {
    "subject": "Project Update - Q1 Timeline Discussion",
    "body": """Hi,

I hope this email finds you well. I wanted to reach out regarding the project timeline we discussed last week.

Could you please provide an update on:
1. The current status of the design phase
2. Any blockers we should be aware of
3. Your estimated completion date for the first milestone

I'd also like to schedule a quick call this week to align on next steps. Let me know your availability.

Best regards""",
}


def test_draft(sender: str, recipient: str) -> dict:
    """Test the /api/v1/email/draft endpoint."""
    print("\n" + "=" * 60)
    print("1. TESTING DRAFT ENDPOINT")
    print("=" * 60)
    print(f"From: {sender}")
    print(f"To: {recipient}")
    print(f"Subject: {SAMPLE_EMAIL['subject'][:50]}...")

    payload = {
        "subject": SAMPLE_EMAIL["subject"],
        "body": SAMPLE_EMAIL["body"],
        "from_email": sender,
        "to_emails": [recipient],
        "cc_emails": [],
    }

    try:
        resp = requests.post(
            f"{API_BASE}/api/v1/email/draft",
            json=payload,
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
        print("\n✅ Draft generated successfully!")
        print("\n--- AI Draft Response ---")
        print(data.get("draft", "(no draft)"))
        print("\n--- Suggested Subject ---")
        print(data.get("suggested_subject", "N/A"))
        print("\n--- Tone Analysis ---")
        print(data.get("tone_analysis", "N/A"))
        return data
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Draft request failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Body: {e.response.text[:500]}")
        raise


def test_process(sender: str, recipient: str) -> dict:
    """Test the /api/v1/email/process endpoint."""
    print("\n" + "=" * 60)
    print("2. TESTING PROCESS ENDPOINT")
    print("=" * 60)
    print(f"From: {sender}")
    print(f"To: {recipient}")

    payload = {
        "subject": SAMPLE_EMAIL["subject"],
        "body": SAMPLE_EMAIL["body"],
        "from_email": sender,
        "to_emails": [recipient],
        "cc_emails": [],
    }

    try:
        resp = requests.post(
            f"{API_BASE}/api/v1/email/process",
            json=payload,
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
        print("\n✅ Email processed successfully!")
        print(f"\nSuccess: {data.get('success')}")
        print("\n--- AI Response ---")
        print(data.get("draft", "(no draft)"))
        print("\n--- Actions Taken ---")
        print(data.get("actions", []))
        return data
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Process request failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Body: {e.response.text[:500]}")
        raise


def check_health() -> bool:
    """Verify the API is running."""
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def main():
    sender = os.environ.get("SENDER_EMAIL")
    recipient = os.environ.get("RECIPIENT_EMAIL")

    if len(sys.argv) >= 3:
        sender = sys.argv[1]
        recipient = sys.argv[2]

    if not sender or not recipient:
        print("Usage: python scripts/test_real_emails.py SENDER_EMAIL RECIPIENT_EMAIL")
        print("\nExample:")
        print("  python scripts/test_real_emails.py john@gmail.com jane@outlook.com")
        print("\nOr use environment variables:")
        print("  SENDER_EMAIL=john@gmail.com RECIPIENT_EMAIL=jane@outlook.com python scripts/test_real_emails.py")
        sys.exit(1)

    print("Email Assistant - Real Email Test")
    print(f"API: {API_BASE}")
    print(f"Sender: {sender}")
    print(f"Recipient: {recipient}")

    if not check_health():
        print(f"\n❌ Backend not reachable at {API_BASE}")
        print("   Start the backend first: uvicorn src.api.main:app --reload")
        sys.exit(1)
    print("\n✅ Backend is running")

    test_draft(sender, recipient)
    test_process(sender, recipient)
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
