import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import uvicorn

from agent import run_agent

app = FastAPI(title="Grok Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    response: str
    youtube_action: dict | None = None

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "grok-assistant"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Accepts user message + chat history.
    Returns assistant response and optional YouTube action.
    """
    try:
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        response_text = run_agent(request.message, history)
        
        # Parse optional YouTube action from response
        youtube_action = None
        if '{"action": "play_youtube"' in response_text:
            try:
                start = response_text.rfind('{"action": "play_youtube"')
                end = response_text.find('}', start) + 1
                action_json = response_text[start:end]
                youtube_action = json.loads(action_json)
                # Clean the JSON from the displayed text
                response_text = response_text[:start].strip()
            except json.JSONDecodeError:
                pass
        
        return ChatResponse(response=response_text, youtube_action=youtube_action)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming endpoint for real-time token streaming.
    """
    async def event_generator():
        try:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
            
            # For streaming, we'll simulate token-by-token delivery
            # Replace with actual streaming if needed
            response_text = run_agent(request.message, history)
            
            # Stream word by word for natural TTS effect
            words = response_text.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'token': chunk, 'done': False})}\n\n"
                await asyncio.sleep(0.02)
            
            yield f"data: {json.dumps({'token': '', 'done': True, 'full': response_text})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
