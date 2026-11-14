from pydantic import BaseModel, Field
from typing import List, Dict, Any

class LandmarkSequence(BaseModel):
    """Schema for landmark sequences (JSON body)."""
    frames: List[Dict[str, Any]] = Field(..., description="List of landmark frames from MediaPipe or similar.")

class InferenceResponse(BaseModel):
    """Schema for text inference response."""
    prediction: str = Field(..., description="The predicted gloss or sentence.")
    confidence: float = Field(..., description="Confidence score of the prediction.")
