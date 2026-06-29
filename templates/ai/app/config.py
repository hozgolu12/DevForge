from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    env: str = "development"
    port: int = 8000
    allowed_hosts: str = "*"

    # AI Service Dependencies (Internal Docker network DNS names)
    ollama_host: str = "http://ollama:11434"
    chromadb_host: str = "http://chromadb:8000"
    qdrant_host: str = "http://qdrant:6333"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
