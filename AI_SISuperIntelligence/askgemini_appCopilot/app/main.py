
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, google.generativeai as genai
app=FastAPI()
class Prompt(BaseModel):
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
