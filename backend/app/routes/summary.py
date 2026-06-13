import json
import numpy as np

from fastapi import APIRouter
from fastapi import HTTPException

from app.services.anomaly_detector import (
    find_amount_column
)

import pandas as pd

from app.database.crud import (
    get_file_by_file_id,
    get_transactions_by_file
)

from app.database.db import SessionLocal

from app.database.crud import (
    get_file_by_file_id
)

router = APIRouter(
    tags=["Summary"]
)


@router.get("/summary/{file_id}")
async def get_summary(
    file_id: str
):

    db = SessionLocal()

    file = get_file_by_file_id(
        db,
        file_id
    )

    if file is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    transactions = get_transactions_by_file(
        db,
        file_id
    )

    df = pd.DataFrame(transactions)# Column datatypes

    dtypes_map = {
        str(col): str(dtype)
        for col, dtype in df.dtypes.items()
    }

    # Numeric statistics

    numeric_cols = df.select_dtypes(
        include=[np.number]
    ).columns.tolist()

    describe_map = {}

    if numeric_cols:

        describe_df = (
            df[numeric_cols]
            .describe()
            .round(2)
        )

        describe_map = json.loads(
            describe_df.to_json()
        )

    amount_col = find_amount_column(df)

    total_amount = 0

    if amount_col:

        total_amount = float(
            df[amount_col]
            .sum()
        )

    anomaly_count = 0

    if "anomaly_flag" in df.columns:

        anomaly_count = int(
            df["anomaly_flag"]
            .sum()
        )

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "amount_column": amount_col,
        "total_amount": total_amount,
        "anomaly_count": anomaly_count,
        "dtypes": dtypes_map,
        "describe": describe_map
    }