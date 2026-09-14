import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth import hash_password
from database import SessionLocal
from models import User

USERNAME = os.getenv("BOOTSTRAP_USERNAME", "ats_user")
EMAIL = os.getenv("BOOTSTRAP_EMAIL", "student@atsense.edu")
PASSWORD = os.getenv("BOOTSTRAP_PASSWORD")


def main():
    if not PASSWORD:
        print("BOOTSTRAP_PASSWORD not set; skipping user bootstrap.")
        return

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.username == USERNAME).first()

        if user:
            print(f"Bootstrap user '{USERNAME}' already exists; skipping.")
            return

        user = User(
            username=USERNAME,
            email=EMAIL,
            password_hash=hash_password(PASSWORD),
        )

        db.add(user)
        db.commit()

        print(f"Bootstrap user '{USERNAME}' created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()