from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Loru API")

class InferenceRequest(BaseModel):
    landmarks: List[List[float]]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/infer/text")
def infer_text(data: InferenceRequest):
    # Placeholder for actual inference logic
    return {"text": "hello"}

@app.post("/infer/voice")
def infer_voice(data: InferenceRequest):
    # Placeholder for actual voice generation logic
    return {"audio_path": "/tmp/output.wav"}