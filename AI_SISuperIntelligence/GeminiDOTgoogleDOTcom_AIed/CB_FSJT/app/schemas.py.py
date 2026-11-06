"""
Pydantic models for request/response serialization and validation.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# --- Auth Schemas ---

class UserCreate(BaseModel):
    """Payload for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserOut(BaseModel):
    """Response payload for user data."""
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Response payload for JWT authentication."""
    access_token: str
    token_type: str


# --- Chat Schemas ---

class MessageCreate(BaseModel):
    """Payload for creating a user message."""
    content: str = Field(..., min_length=1)


class MessageOut(BaseModel):
    """Response payload for a single chat message."""
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    """Summary response for conversation listings."""
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailOut(BaseModel):
    """Detailed response for a conversation including messages."""
    id: int
    title: str
    created_at: datetime
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True