from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core_config import settings


class Base(DeclarativeBase):
    pass


def get_engine():
    if settings.DATABASE_URL.startswith("sqlite"):
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

