from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models import User, SearchSession, Query
from app.schemas import (
    UserCreate,
    UserOut,
    Token,
    SessionCreate,
    SearchSessionOut,
    QueryCreate,
    QueryOut,
    SearchSessionDetailOut,
)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/api/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_pw = get_password_hash(user_in.password)
    new_user = User(username=user_in.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/api/auth/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Authenticate user and return a mock JWT bearer token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": f"mock-token-for-{user.username}", "token_type": "bearer"}


@router.post("/api/sessions", response_model=SearchSessionOut, status_code=status.HTTP_201_CREATED)
def create_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    """Create a new AI chat search session."""
    # For simplicity, assign to user ID 1 or a default user in this demo
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=400, detail="No users found. Register first.")
    
    new_session = SearchSession(title=session_in.title, user_id=user.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.post("/api/sessions/{session_id}/queries", response_model=QueryOut, status_code=status.HTTP_201_CREATED)
def submit_query(session_id: int, query_in: QueryCreate, db: Session = Depends(get_db)):
    """Submit a prompt to Gemini AI within a specific search session."""
    session = db.query(SearchSession).filter(SearchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Search session not found")

    # Simulate Gemini AI response generation
    ai_response = f"Gemini AI Response to: '{query_in.prompt}'"

    new_query = Query(session_id=session.id, prompt=query_in.prompt, response=ai_response)
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    return new_query


@router.get("/api/sessions/{session_id}", response_model=SearchSessionDetailOut)
def get_session_details(session_id: int, db: Session = Depends(get_db)):
    """Retrieve details and query history for a specific search session."""
    session = db.query(SearchSession).filter(SearchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Search session not found")
    return session