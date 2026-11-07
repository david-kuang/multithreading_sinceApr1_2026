#from fastapi import FastAPI
from app.database import engine, Base
from app.routes import router
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, google.generativeai as genai

# Automatically create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="askGemini API",
    description="Full-featured Gemini-like AI query and chat backend",
    version="1.0.0",
)

app.include_router(router)

@app.get("/")
def read_root():
#    return {"message": "Welcome to the askGemini API. Visit /docs for interactive Swagger UI."}
    return {"message": "Welcome to the askGemini API demo YHK. Visit /docs for interactive Swagger UI."}

"""class Prompt(BaseModel):
    prompt:str    
@app.post('/chat')
def chat(p:Prompt):
    key=os.getenv('GEMINI_API_KEY')
    if not key:
        raise HTTPException(500,'Missing GEMINI_API_KEY')
    genai.configure(api_key=key)
    model=genai.GenerativeModel('gemini-1.5-flash')
    r=model.generate_content(p.prompt)
    return {'response': getattr(r,'text','')}
"""