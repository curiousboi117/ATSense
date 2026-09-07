import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth import create_access_token
from database import Base, get_db
from main import app


TEST_DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "test_atsense.db",
)

TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

from models import User

TEST_USER_ID = 1

Base.metadata.create_all(bind=test_engine)

with TestingSessionLocal() as db:
    if db.query(User).filter(User.id == TEST_USER_ID).first() is None:
        db.add(
            User(
                id=TEST_USER_ID,
                username="test_user",
                email="test@example.com",
            )
        )
        db.commit()


client = TestClient(app)

AUTH_HEADERS = {
    "Authorization": f"Bearer {create_access_token(str(TEST_USER_ID))}"
}


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_history_endpoint():
    response = client.get("/api/history", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_reset_endpoint():
    response = client.post("/api/reset-all", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_upload_rejects_unsupported_format():
    response = client.post(
        "/api/upload",
        headers=AUTH_HEADERS,
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
        headers=AUTH_HEADERS,
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
        headers=AUTH_HEADERS,
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
        headers=AUTH_HEADERS,
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
        headers=AUTH_HEADERS,
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