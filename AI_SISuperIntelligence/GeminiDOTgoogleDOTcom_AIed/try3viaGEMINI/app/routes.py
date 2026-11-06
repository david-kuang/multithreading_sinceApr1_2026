"""
FastAPI router definitions for user authentication, session management, AskGemini queries, and UI rendering.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.database import get_db
from app.models import User, SearchSession, QueryItem
from app.schemas import (
    UserCreate, UserOut, Token,
    SearchSessionOut, SearchSessionDetailOut,
    QueryCreate, QueryOut
)
from app.services import gemini_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def serve_frontend_ui(request: Request):
    """Renders the AskGemini single-page web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/api/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user account."""
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user = User(username=user_in.username, hashed_password=get_password_hash(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/api/auth/token", response_model=Token)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticates user credentials and returns a JWT access token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(data={"sub": user.username}), "token_type": "bearer"}


@router.get("/api/sessions", response_model=List[SearchSessionOut])
def get_user_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieves all search/chat sessions belonging to the authenticated user."""
    return db.query(SearchSession).filter(SearchSession.user_id == current_user.id).order_by(SearchSession.created_at.desc()).all()


@router.post("/api/sessions", response_model=SearchSessionDetailOut, status_code=status.HTTP_201_CREATED)
def create_session(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Creates a new search session for the active user."""
    session = SearchSession(title="New Search", user_id=current_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/api/sessions/{session_id}", response_model=SearchSessionDetailOut)
def get_session_details(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches details and query history for a specific search session."""
    session = db.query(SearchSession).filter(SearchSession.id == session_id, SearchSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/api/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletes a search session and all associated queries."""
    session = db.query(SearchSession).filter(SearchSession.id == session_id, SearchSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return None


@router.post("/api/sessions/{session_id}/queries", response_model=QueryOut)
def submit_query(
    session_id: int,
    query_in: QueryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits a query to AskGemini, invokes the Gemini service with conversation context,
    stores the interaction, and updates session titles dynamically.
    """
    session = db.query(SearchSession).filter(SearchSession.id == session_id, SearchSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update session title if default
    if session.title == "New Search":
        session.title = query_in.prompt[:35] + ("..." if len(query_in.prompt) > 35 else "")
        db.add(session)
        db.commit()

    # Collect previous conversation history for context
    existing_queries = db.query(QueryItem).filter(QueryItem.session_id == session.id).order_by(QueryItem.created_at.asc()).all()
    history = []
    for q in existing_queries:
        history.append({"role": "user", "content": q.prompt})
        history.append({"role": "assistant", "content": q.response})
    
    history.append({"role": "user", "content": query_in.prompt})

    # Generate answer via Gemini service
    answer_text = gemini_service.generate_answer(history, query_in.prompt)

    # Store query and answer
    query_item = QueryItem(session_id=session.id, prompt=query_in.prompt, response=answer_text)
    db.add(query_item)
    db.commit()
    db.refresh(query_item)

    return query_item