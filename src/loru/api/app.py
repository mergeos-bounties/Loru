from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Loru API")

class InferTextRequest(BaseModel):
    sequence: list

@app.post("/infer/text")
async def infer_text(req: InferTextRequest):
    return {"text": "dummy_inferred_text"}

@app.post("/infer/voice")
async def infer_voice(req: InferTextRequest):
    return {"audio_path": "dummy_audio.wav"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)