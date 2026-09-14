import os
from typing import List
import json

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./atsense.db"

    @model_validator(mode="after")
    def normalize_database_url(self):
        if self.database_url.startswith("sqlite:///"):
            database_path = self.database_url[len("sqlite:///"):]

            if database_path not in {":memory:", ""}:
                from pathlib import Path

                path = Path(database_path)

                if not path.is_absolute():
                    path = Path(__file__).resolve().parent / path

                self.database_url = f"sqlite:///{path.as_posix()}"

        return self

    cors_origins: str = (
        '["http://localhost:5173","http://127.0.0.1:5173"]'
    )

    app_env: str = "development"

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    rate_limit_login: str = "5/minute"
    rate_limit_upload: str = "10/minute"
    rate_limit_match_job: str = "10/minute"

    use_semantic_transformers: bool = True
    sentence_transformer_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_config(self):
        if self.app_env.lower() == "production" and not self.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY must be configured in production.")
        return self

    @property
    def cors_list(self) -> List[str]:
        try:
            origins = json.loads(self.cors_origins)
        except (json.JSONDecodeError, TypeError) as exc:
            if self.app_env.lower() == "production":
                raise ValueError(
                    "CORS_ORIGINS must be valid JSON in production."
                ) from exc
            return ["http://localhost:5173"]

        if not isinstance(origins, list) or not all(
            isinstance(origin, str) and origin.strip()
            for origin in origins
        ):
            if self.app_env.lower() == "production":
                raise ValueError(
                    "CORS_ORIGINS must be a non-empty JSON list of origins in production."
                )
            return ["http://localhost:5173"]

        return origins

    
settings = Settings()