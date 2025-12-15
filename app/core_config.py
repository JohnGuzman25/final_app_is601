from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"

    JWT_SECRET: str = "CHANGE_ME_IN_PROD"
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    APP_BASE_URL: str = "http://localhost:8000"
    EMAIL_FROM: str = "no-reply@example.com"

    class Config:
        env_file = ".env"


settings = Settings()

