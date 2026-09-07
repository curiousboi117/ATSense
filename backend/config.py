import os
from typing import List
import json

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./atsense.db"

    cors_origins: str = (
        '["http://localhost:5173","http://127.0.0.1:5173"]'
    )

    app_env: str = "development"

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    use_semantic_transformers: bool = True
    sentence_transformer_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_list(self) -> List[str]:
        try:
            return json.loads(self.cors_origins)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:5173"]


settings = Settings()