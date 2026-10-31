from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "development-secret-key-32-chars-min-len"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WEB_PORT: int = 3000
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # AI Models
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL_FLASH: str = "gemini-3.8-flash"
    GEMINI_MODEL_STRONG: str | None = None

    # Google Cloud STT
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    GOOGLE_CLOUD_PROJECT: str | None = None
    GOOGLE_STT_REGION: str = "asia-southeast1"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./local_dev.db"

    # Storage
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: str = "./storage"

    # Queues
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
