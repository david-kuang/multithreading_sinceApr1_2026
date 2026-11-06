"""
Database connection, session management, and SQLAlchemy Base model definition.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config import settings

# Configure SQLite connect arguments for thread safety
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator yielding database sessions.
    Ensures safe session teardown after request processing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()