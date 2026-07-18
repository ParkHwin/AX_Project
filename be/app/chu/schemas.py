from pydantic import BaseModel

class UploadResponse(BaseModel):
    image_id: str
    class_id: int
    class_name: str
    confidence: float

class ErrorResponse(BaseModel):
    error: str
    detail: str