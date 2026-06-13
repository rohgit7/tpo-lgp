from pydantic import BaseModel
from typing import List, Optional,Dict,Any


class UploadResponse(BaseModel):
    status: str
    file_id: str
    filename: str
    rows: int
    anomalies_detected: int
    columns: List[str]
    amount_column: Optional[str] = None


class ChatResponse(BaseModel):
    query: str
    answer: str
    aggregator: str


class SummaryResponse(BaseModel):
    dtypes: Dict[str, str]
    describe: Dict[str, Any]


class AnomalyResponse(BaseModel):
    count: int
    anomalies: List[Dict[str, Any]]