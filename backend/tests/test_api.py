import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth import create_access_token, hash_password
from database import Base, get_db
from main import app
from models import User, Resume, Analysis


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


TEST_USER_ID = 1
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password_123"


Base.metadata.create_all(bind=test_engine)

with TestingSessionLocal() as db:
    user = db.query(User).filter(User.id == TEST_USER_ID).first()

    if user is None:
        db.add(
            User(
                id=TEST_USER_ID,
                username=TEST_USERNAME,
                email="test@example.com",
                password_hash=hash_password(TEST_PASSWORD),
            )
        )
        db.commit()
    elif not user.password_hash:
        user.password_hash = hash_password(TEST_PASSWORD)
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


def test_login_with_valid_credentials():
    response = client.post(
        "/api/auth/login",
        json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_invalid_password():
    response = client.post(
        "/api/auth/login",
        json={
            "username": TEST_USERNAME,
            "password": "wrong_password",
        },
    )

    assert response.status_code == 401


def test_protected_endpoint_requires_authentication():
    response = client.get("/api/history")

    assert response.status_code == 401


def test_protected_endpoint_rejects_invalid_token():
    response = client.get(
        "/api/history",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_history_endpoint():
    response = client.get("/api/history", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_reset_endpoint():
    response = client.post("/api/reset-all", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_user_cannot_access_another_users_analysis():
    with TestingSessionLocal() as db:
        user_a = db.query(User).filter(User.id == TEST_USER_ID).first()

        user_b = (
            db.query(User)
            .filter(User.username == "test_user_b")
            .first()
        )

        if user_b is None:
            user_b = User(
                username="test_user_b",
                email="test_b@example.com",
                password_hash=hash_password("test_password_b_123"),
            )
            db.add(user_b)
            db.commit()
            db.refresh(user_b)

        resume = Resume(
            user_id=user_a.id,
            filename="user_a_resume.pdf",
            file_size=100,
            version=1,
            extracted_text="User A resume content",
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        analysis = Analysis(
            resume_id=resume.id,
            ats_score=85.0,
            score_breakdown={},
            personal_info={},
            skills=[],
            ats_checks={},
            recommendations=[],
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        user_b_token = create_access_token(str(user_b.id))

        response = client.get(
            f"/api/analysis/{analysis.id}",
            headers={
                "Authorization": f"Bearer {user_b_token}",
            },
        )

        assert response.status_code == 404


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
    assert (
        "Only PDF and DOCX resume files are supported"
        in response.json()["detail"]
    )


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