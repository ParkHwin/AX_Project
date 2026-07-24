from pydantic import BaseModel


class UploadResponse(BaseModel):
    image_id: str
    class_id: list[int]
    class_name: list[str]
    confidence: list[float]
    gradcam_data: str | None = None
    process_info: list | None = None


class ErrorResponse(BaseModel):
    error: str
    detail: str