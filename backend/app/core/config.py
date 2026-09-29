from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./normex.db"
    secret_key: str = "development-secret"
    llm_provider: str = "none"
    llm_api_key: str | None = None
    embedding_model: str | None = None
    cors_origins: str = "http://localhost:5173"
    upload_max_size: int = 10 * 1024 * 1024
    storage_path: str = "./storage"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
