import os
import json
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.graph.agent import stream_chat_response
from backend.skills.skills_manager import SkillsManager

app = FastAPI(title="Mini-OpenClaw API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class ChatRequest(BaseModel):
    message: str
    session_id: str = "main_session"
    stream: bool = True

class FileSaveRequest(BaseModel):
    path: str
    content: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # Depending on requirements, SSE streaming is typically sent via text/event-stream
    if req.stream:
        # Note: stream_chat_response yields string chunks prefixed with "data: "
        return StreamingResponse(stream_chat_response(req.message, req.session_id), media_type="text/event-stream")
    else:
        # For non-streaming (not fully implemented in backend yet, fallback)
        return {"error": "Non-streaming not fully implemented in MVP"}

@app.get("/api/files")
async def get_file(path: str):
    """Reads a file relative to backend directory (e.g. memory/MEMORY.md)."""
    full_path = os.path.join(PROJECT_ROOT, "backend", path)
    if not os.path.exists(full_path):
        return {"error": f"File {path} not found."}
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content}

@app.post("/api/files")
async def save_file(req: FileSaveRequest):
    """Saves content to a file relative to backend directory."""
    full_path = os.path.join(PROJECT_ROOT, "backend", req.path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(req.content)
    
    # If a skill changed, we might want to regenerate snapshot
    if "SKILL.md" in req.path:
        SkillsManager.generate_snapshot()
        
    return {"status": "success"}

@app.get("/api/sessions")
async def list_sessions():
    """Lists all available session JSON files."""
    sessions_dir = os.path.join(PROJECT_ROOT, "backend", "sessions")
    if not os.path.exists(sessions_dir):
        return {"sessions": []}
    files = [f for f in os.listdir(sessions_dir) if f.endswith(".json")]
    return {"sessions": files}

if __name__ == "__main__":
    import uvicorn
    # Make sure to run the server efficiently
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8002, reload=True)
