from pydantic import BaseModel

class UploadResponse(BaseModel):
    image_id: str
    class_id: list[int]
    class_name: list[str]
    confidence: list[float]

class ErrorResponse(BaseModel):
    error: str
    detail: str