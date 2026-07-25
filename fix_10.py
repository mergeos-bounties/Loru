from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel
import uvicorn
import os
from typing import Optional

app = FastAPI()

class TextInferRequest(BaseModel):
    sequence: str

class VoiceInferRequest(BaseModel):
    audio_bytes: bytes

@app.post("/infer/text")
async def infer_text(request: TextInferRequest):
    try:
        # Add your text inference logic here
        result = {"result": "Text inference result"}
        return JSONResponse(content=result, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/infer/voice")
async def infer_voice(request: VoiceInferRequest):
    try:
        # Add your voice inference logic here
        result = {"result": "Voice inference result"}
        return JSONResponse(content=result, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"}, media_type="application/json")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Tests with TestClient
client = TestClient(app)

def test_infer_text():
    response = client.post("/infer/text", json={"sequence": "Test sequence"})
    assert response.status_code == 200
    assert response.json() == {"result": "Text inference result"}

def test_infer_voice():
    response = client.post("/infer/voice", content=b"Test audio bytes")
    assert response.status_code == 200
    assert response.json() == {"result": "Voice inference result"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}