"""
Main FastAPI application entry point. Initializes database tables, registers routes, and boots the server.
"""

from fastapi import FastAPI
from app.config import settings
from app.database import Base, engine
from app.routes import router

# Automatically create database schema tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="A complete production-ready AskGemini web application powered by FastAPI and Google Gemini."
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)