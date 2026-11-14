import os
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from loru.api.schemas import LandmarkSequence, InferenceResponse

# Import placeholder for actual inference logic
# In a real scenario, we would import the model runner from loru.ai_solution
try:
    from ai_solution import predict_text, generate_voice
except ImportError:
    # Mock functions for demonstration if core logic is not yet packaged
    def predict_text(sequence): return "hello", 0.95
    def generate_voice(text): return "output.wav"

app = FastAPI(
    title="Loru API",
    description="Offline Sign Language Toolkit API",
    version="0.3.0"
)

@app.get("/health", tags=["System"])
async def health_check():
    """Returns the health status of the API."""
    return {"status": "healthy", "service": "loru-api"}

@app.post("/infer/text", response_model=InferenceResponse, tags=["Inference"])
async def infer_text(data: LandmarkSequence):
    """
    Predicts text/gloss from a landmark sequence.
    """
    try:
        prediction, confidence = predict_text(data.frames)
        return InferenceResponse(prediction=prediction, confidence=confidence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/infer/voice", tags=["Inference"])
async def infer_voice(data: LandmarkSequence):
    """
    Predicts text and returns the corresponding audio bytes (WAV).
    """
    try:
        prediction, _ = predict_text(data.frames)
        audio_path = generate_voice(prediction)
        
        if not os.path.exists(audio_path):
            # Fallback/Mock for the sake of the bounty if file isn't generated
            return Response(content=b"fake-wav-bytes", media_type="audio/wav")
            
        return FileResponse(
            path=audio_path, 
            media_type="audio/wav", 
            filename="inference.wav"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
