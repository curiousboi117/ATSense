import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_history_endpoint():
    response = client.get("/api/history")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_reset_endpoint():
    response = client.post("/api/reset-all")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_upload_rejects_unsupported_format():
    response = client.post(
        "/api/upload",
        files={
            "file": (
                "resume.txt",
                b"some text",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Only PDF and DOCX resume files are supported" in response.json()["detail"]


def test_upload_rejects_empty_file():
    response = client.post(
        "/api/upload",
        files={
            "file": (
                "resume.pdf",
                b"",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_rejects_fake_pdf():
    response = client.post(
        "/api/upload",
        files={
            "file": (
                "resume.pdf",
                b"This is not a real PDF.",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "not a valid PDF" in response.json()["detail"]


def test_upload_rejects_fake_docx():
    response = client.post(
        "/api/upload",
        files={
            "file": (
                "resume.docx",
                b"This is not a real DOCX.",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400
    assert "not a valid DOCX" in response.json()["detail"]


def test_upload_rejects_oversized_file():
    oversized_content = b"a" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/api/upload",
        files={
            "file": (
                "resume.pdf",
                oversized_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "5 MB" in response.json()["detail"]