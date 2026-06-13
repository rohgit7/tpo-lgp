from datetime import datetime

from pydantic import BaseModel


class UploadedFileResponse(
    BaseModel
):
    file_id: str
    filename: str
    rows_count: int
    anomaly_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True