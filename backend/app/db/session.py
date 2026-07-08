import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/ai_secretary"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Creates all tables if they don't exist, and seeds the default user."""
    from app.db import models  # noqa: ensures models are registered on Base
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        default_user = db.query(models.User).filter(models.User.id == 1).first()
        if not default_user:
            default_user = models.User(
                id=1,
                email="local@aria.dev",
                name="Default User",
            )
            db.add(default_user)
            db.commit()
            print("[DB] Seeded default user (id=1)")
    finally:
        db.close()