"""
Pydantic schemas for request validation, type serialization, and response formatting.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Payload schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserOut(BaseModel):
    """Response schema for public user info."""
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Response schema for JWT authentication token."""
    access_token: str
    token_type: str


class QueryCreate(BaseModel):
    """Payload schema for submitting a question to AskGemini."""
    prompt: str = Field(..., min_length=1)


class QueryOut(BaseModel):
    """Response schema for a single Q&A turn."""
    id: int
    prompt: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True


class SearchSessionOut(BaseModel):
    """Summary schema for search sessions in the sidebar."""
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class SearchSessionDetailOut(BaseModel):
    """Detailed schema for a session including all queries."""
    id: int
    title: str
    created_at: datetime
    queries: List[QueryOut] = []

    class Config:
        from_attributes = True