from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    default_token_limit: int = 200
    session_timeout_seconds: int = 300
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:54853"]
    host: str = "127.0.0.1"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
