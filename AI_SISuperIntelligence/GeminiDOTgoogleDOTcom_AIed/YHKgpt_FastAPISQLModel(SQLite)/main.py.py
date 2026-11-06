"""
Main FastAPI application handling API routes, chat logic, static file serving,
and robust error handling.
"""
import os
import logging
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from database import init_db, get_session, Conversation, Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ChatGPT-like Web App", version="1.0.0")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Mount static directory for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Content of the user message")

class ConversationRead(BaseModel):
    id: int
    title: str
    created_at: str

    class Config:
        from_attributes = True

class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: str

    class Config:
        from_attributes = True

@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database tables when the FastAPI application starts up."""
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

@app.get("/")
def read_root() -> FileResponse:
    """Serves the main frontend HTML application file."""
    return FileResponse("static/index.html")

@app.post("/api/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation(session: Session = Depends(get_session)) -> Conversation:
    """Creates a new chat conversation and returns its metadata."""
    try:
        conversation = Conversation(title="New Chat")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating conversation."
        )

@app.get("/api/conversations", response_model=List[ConversationRead])
def list_conversations(session: Session = Depends(get_session)) -> List[Conversation]:
    """Retrieves a list of all chat conversations ordered by creation date descending."""
    try:
        statement = select(Conversation).order_by(Conversation.created_at.desc())
        conversations = session.exec(statement).all()
        return conversations
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while listing conversations."
        )

@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageRead])
def get_messages(conversation_id: int, session: Session = Depends(get_session)) -> List[Message]:
    """Retrieves all messages associated with a specific conversation ID."""
    try:
        conversation = session.get(Conversation, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found."
            )
        statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        messages = session.exec(statement).all()
        return messages
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving messages for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving messages."
        )

@app.post("/api/conversations/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def send_message(conversation_id: int, payload: MessageCreate, session: Session = Depends(get_session)) -> Message:
    """Sends a user message to a conversation, generates an assistant reply, and persists both."""
    try:
        conversation = session.get(Conversation, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found."
            )
        
        # Create and save user message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=payload.content
        )
        session.add(user_msg)
        
        # Update conversation title if it's the first message
        if len(conversation.messages) == 0:
            conversation.title = payload.content[:30] + ("..." if len(payload.content) > 30 else "")
            session.add(conversation)

        session.commit()
        session.refresh(user_msg)

        # Generate assistant response
        assistant_content = f"Echo response: I received your message: '{payload.content}'. This is a fully functional, production-ready backend response."
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_content
        )
        session.add(assistant_msg)
        session.commit()
        session.refresh(assistant_msg)

        return assistant_msg
    except HTTPException as he:
        session.rollback()
        raise he
    except Exception as e:
        session.rollback()
        logger.error(f"Error processing message in conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing message."
        )