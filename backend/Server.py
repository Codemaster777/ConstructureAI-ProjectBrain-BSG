from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import GetRagResponse, ExtractStructure
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

App = FastAPI()

App.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@App.get("/")
def HealthCheck():
    return {"status": "Online"}

# --- CHAT ENDPOINT ---
@App.post("/chat")
@App.post("/api/chat")
async def ChatRoute(request: Request):
    # 1. Read JSON body flexibly
    try:
        data = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 2. Look for ANY common key
    user_text = data.get("message") or data.get("Msg") or data.get("query") or data.get("question")
    
    if not user_text:
        raise HTTPException(status_code=422, detail="No message found. Please send JSON with 'message' key.")

    # 3. Process
    try:
        return GetRagResponse(user_text)
    except Exception as e:
        print(f"Error: {e}")
        return {"answer": "Sorry, the backend encountered an error processing your request.", "sources": []}

# --- EXTRACT ENDPOINT ---
@App.post("/extract")
@App.post("/api/extract")
async def ExtractRoute(request: Request):
    # 1. Read JSON
    try:
        data = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 2. Look for ANY common key
    user_text = data.get("message") or data.get("Cmd") or data.get("instruction") or data.get("query")

    if not user_text:
        raise HTTPException(status_code=422, detail="No command found. Please send JSON with 'message' key.")

    # 3. Process
    try:
        return ExtractStructure(user_text)
    except Exception as e:
        print(f"Error: {e}")
        return {"data": [], "sources": []}

if __name__ == "__main__":
    # Listen on all interfaces
    uvicorn.run(App, host="0.0.0.0", port=8000)