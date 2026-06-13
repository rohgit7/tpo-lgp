from fastapi import APIRouter
from fastapi import HTTPException


from app.database.db import SessionLocal

from app.database.crud import (
    get_anomalies_by_file
)
from app.models.response_models import (
    AnomalyResponse
)


router = APIRouter(
    tags=["Anomalies"]
)


@router.get(
    "/anomalies/{file_id}",
    response_model=AnomalyResponse
)
async def get_anomalies(
    file_id: str
):

    db = SessionLocal()

    anomalies_df = get_anomalies_by_file(
        db,
        file_id
    )

    if anomalies_df is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    if anomalies_df.empty:

        return AnomalyResponse(
            count=0,
            anomalies=[]
        )

    anomalies_df = anomalies_df.fillna("")

    records = anomalies_df.to_dict(
        orient="records"
    )

    return AnomalyResponse(
        count=len(records),
        anomalies=records
    )