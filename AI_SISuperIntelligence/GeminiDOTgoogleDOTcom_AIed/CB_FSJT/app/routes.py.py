"""
FastAPI Route Handlers containing API endpoints for Auth, Chat, and HTML UI serving.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.database import get_db
from app.models import User, Conversation, Message
from app.schemas import UserCreate, UserOut, Token, ConversationOut, ConversationDetailOut, MessageCreate, MessageOut
from app.services import llm_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# --- UI Endpoints ---

@router.get("/", response_class=HTMLResponse)
def get_index_page(request: Request):
    """Renders the main single-page web app template."""
    return templates.TemplateResponse("index.html", {"request": request})


# --- Authentication Endpoints ---

@router.post("/api/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user account."""
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(username=user_in.username, hashed_password=hashed_pwd)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/api/auth/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticates credentials and returns a JWT access token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Conversation & Chat Endpoints ---

@router.get("/api/conversations", response_model=List[ConversationOut])
def get_user_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieves all chat conversations belonging to the active user."""
    return db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.created_at.desc()).all()


@router.post("/api/conversations", response_model=ConversationDetailOut, status_code=status.HTTP_201_CREATED)
def create_conversation(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Creates a new empty conversation for the active user."""
    conv = Conversation(title="New Chat", user_id=current_user.id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/api/conversations/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation_details(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches full conversation history for a specific conversation ID."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/api/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletes a conversation and all associated messages."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return None


@router.post("/api/conversations/{conversation_id}/messages", response_model=MessageOut)
def send_message(
    conversation_id: int,
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sends a user prompt to a chat session, queries the LLM service, stores both messages,
    and auto-generates a conversation title from the first message.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 1. Store User Message
    user_msg = Message(conversation_id=conv.id, role="user", content=msg_in.content)
    db.add(user_msg)
    db.commit()

    # Update title if it's the first message
    if conv.title == "New Chat":
        conv.title = msg_in.content[:30] + ("..." if len(msg_in.content) > 30 else "")
        db.add(conv)
        db.commit()

    # 2. Collect history for LLM prompt context
    all_messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in all_messages]

    # 3. Request LLM completion
    ai_response_text = llm_service.generate_chat_response(history)

    # 4. Save AI Response
    ai_msg = Message(conversation_id=conv.id, role="assistant", content=ai_response_text)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ai_msg