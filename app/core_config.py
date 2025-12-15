from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # For CI and Docker, we use DATABASE_URL env var
    DATABASE_URL: str = "postgresql+psycopg2://project14:project14@localhost:5432/project14"

    # JWT
    JWT_SECRET: str = "CHANGE_ME_IN_PROD"
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    # Email confirmation (for demo we can log the link)
    APP_BASE_URL: str = "http://localhost:8000"
    EMAIL_FROM: str = "no-reply@example.com"

    class Config:
        env_file = ".env"


settings = Settings()
