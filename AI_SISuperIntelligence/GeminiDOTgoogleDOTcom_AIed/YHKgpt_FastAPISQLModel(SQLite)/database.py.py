"""
Database configuration and models using SQLModel.
Handles SQLite database setup, session management, and table definitions.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, Relationship

DATABASE_URL = "sqlite:///./chat_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class Conversation(SQLModel, table=True):
    """Represents a chat conversation session."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, default="New Chat")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    messages: List["Message"] = Relationship(
        back_populates="conversation", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Message(SQLModel, table=True):
    """Represents an individual message within a conversation."""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str = Field(description="Role of the sender: 'user' or 'assistant'")
    content: str = Field(description="Content of the message")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Optional[Conversation] = Relationship(back_populates="messages")

def init_db() -> None:
    """Initializes the database by creating all tables defined in SQLModel metadata."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency generator that yields a database session for request handling."""
    with Session(engine) as session:
        yield session