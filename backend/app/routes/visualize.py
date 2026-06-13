from fastapi import APIRouter
from fastapi import HTTPException

import pandas as pd

from app.database.db import SessionLocal

from app.database.crud import (
    get_transactions_by_file
)

from app.services.visualization_service import (
    create_visualization
)

router = APIRouter(
    tags=["Visualization"]
)


@router.get(
    "/visualize/{file_id}"
)
async def visualize(
    file_id: str
):

    db = SessionLocal()

    transactions = get_transactions_by_file(
        db,
        file_id
    )

    df = pd.DataFrame(
        transactions
    )

    if df is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:

        fig = create_visualization(
            df
        )

        return fig.to_json()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )