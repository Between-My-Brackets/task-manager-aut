"""
FlowBoard Configuration
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "FlowBoard"
    app_version: str = "1.0.0"
    app_env: str = "development"

    # Auth
    secret_key: str = "dev-secret-key-change-in-production-please"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:80",
        "http://localhost",
    ]


settings = Settings()
