from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import typing

app = FastAPI(title="Loru Inference Engine", version="0.1.0")

class TextInferRequest(BaseModel):
    prompt: str
    model: typing.Optional[str] = "default"

class TextInferResponse(BaseModel):
    output: str
    latency_ms: float

@app.get("/health")
async def health_check():
    return {"status": "HEALTHY", "service": "loru-api"}

@app.post("/infer/text", response_model=TextInferResponse)
async def infer_text(payload: TextInferRequest):
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    return TextInferResponse(output=f"Processed inference for: {payload.prompt}", latency_ms=12.4)

@app.post("/infer/voice")
async def infer_voice(audio_file: UploadFile = File(...)):
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="Invalid audio stream payload")
    content = await audio_file.read()
    return {"status": "AUDIO_PROCESSED", "filename": audio_file.filename, "bytes_received": len(content)}
