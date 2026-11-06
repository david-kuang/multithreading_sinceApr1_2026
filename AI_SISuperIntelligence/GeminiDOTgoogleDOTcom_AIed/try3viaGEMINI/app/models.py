"""
SQLAlchemy ORM data models defining User accounts, Query Sessions, and Q&A interactions.
"""

import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """
    ORM Model representing application users.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("SearchSession", back_populates="owner", cascade="all, delete-orphan")


class SearchSession(Base):
    """
    ORM Model representing a logical grouping of AskGemini queries.
    """
    __tablename__ = "search_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), default="New Search", nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="sessions")
    queries = relationship("QueryItem", back_populates="session", cascade="all, delete-orphan", order_by="QueryItem.created_at")


class QueryItem(Base):
    """
    ORM Model representing a single user question and its corresponding Gemini answer.
    """
    __tablename__ = "query_items"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("search_sessions.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("SearchSession", back_populates="queries")