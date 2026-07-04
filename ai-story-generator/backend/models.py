from pydantic import BaseModel
from typing import Optional

class CaptionRequest(BaseModel):
    image_b64: str

class DescriptionRequest(BaseModel):
    caption: str
    image_b64: Optional[str] = None

class StoryRequest(BaseModel):
    caption: str
    description: str
    theme: str = "Adventure"
    word_count: int = 100
    image_b64: Optional[str] = None

class CaptionResponse(BaseModel):
    caption: str

class DescriptionResponse(BaseModel):
    description: str

class StoryResponse(BaseModel):
    story: str
