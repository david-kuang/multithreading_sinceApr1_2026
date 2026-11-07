import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Gemini Web Chat App")

# Initialize the Gemini Client
# The SDK automatically picks up GEMINI_API_KEY from the environment
try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing GenAI Client: {e}")
    client = None

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini Client is not initialized. Check your GEMINI_API_KEY.")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        # Call the lightweight Gemini model for chat completions
        response = client.models.generate_content(
#            model='gemini-2.5-flash',
            model='gemini-3.8-flash',
            contents=request.message,
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful, friendly AI chat assistant."
            )
        )
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files directory for frontend UI
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))