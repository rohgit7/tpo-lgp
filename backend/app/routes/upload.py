import os
import uuid
import pandas as pd

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.database.db import SessionLocal
from app.database.crud import (
    create_uploaded_file,
    create_transactions
)

from app.services.anomaly_detector import (
    run_iqr_anomaly_detection,
    find_amount_column
)

from app.services.pdf_parser import process_pdf

from app.models.response_models import UploadResponse


router = APIRouter(
    tags=["Upload"]
)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


def _normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    column_map = {}
    aliases = {
        "transaction_date": [
            "transaction_date",
            "transaction date",
            "date",
            "txn_date",
            "txn date",
            "posted_date",
            "posted date",
            "posting_date",
            "posting date"
        ],
        "description": [
            "description",
            "desc",
            "narration",
            "details",
            "memo",
            "transaction",
            "vendor",
            "payee",
            "particulars"
        ],
        "category": [
            "category",
            "cat",
            "type",
            "department",
            "dept",
            "classification"
        ],
        "amount": [
            "amount",
            "amt",
            "value",
            "debit",
            "credit",
            "price",
            "total",
            "transaction amount",
            "amount_usd"
        ]
    }

    for raw_col in df.columns:
        normalized = str(raw_col).strip().lower()
        mapped = None

        for canonical, keys in aliases.items():
            if normalized == canonical:
                mapped = canonical
                break

            for key in keys:
                if key == normalized or key in normalized or normalized in key:
                    mapped = canonical
                    break
            if mapped:
                break

        column_map[raw_col] = mapped or normalized

    return df.rename(columns=column_map)


@router.post(
    "/upload",
    response_model=UploadResponse
)
async def upload_file(
    file: UploadFile = File(...)
):
    db = SessionLocal()

    try:

        # Generate unique file id
        file_id = str(uuid.uuid4())

        # Save uploaded file
        saved_filename = f"{file_id}_{file.filename}"

        filepath = os.path.join(
            UPLOAD_FOLDER,
            saved_filename
        )

        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        filename = file.filename.lower()

        extension = os.path.splitext(
            filename
        )[1]

        # Parse uploaded file

        if extension == ".csv":

            raw_df = pd.read_csv(
                filepath
            )

        elif extension in [
            ".xls",
            ".xlsx"
        ]:

            raw_df = pd.read_excel(
                filepath
            )

        elif extension == ".pdf":

            raw_df = process_pdf(
                filepath
            )

        else:

            raise HTTPException(
                status_code=400,
                detail="Unsupported file format"
            )

        if raw_df is None or raw_df.empty:

            raise HTTPException(
                status_code=400,
                detail="No data extracted from file"
            )

        # Clean and normalize column names

        raw_df = _normalize_dataframe_columns(raw_df)

        # Run anomaly detection

        processed_df = run_iqr_anomaly_detection(
            raw_df
        )

        anomalies_df = processed_df[
            processed_df["anomaly_flag"] == 1
        ]

        # Save metadata

        create_uploaded_file(
            db=db,
            file_id=file_id,
            filename=file.filename,
            filepath=filepath,
            rows_count=len(processed_df),
            anomaly_count=len(anomalies_df)
        )

        # Save transactions

        create_transactions(
            db=db,
            file_id=file_id,
            dataframe=processed_df
        )

        amount_col = find_amount_column(
            processed_df
        )

        return UploadResponse(
            status="Success",
            file_id=file_id,
            filename=file.filename,
            rows=len(processed_df),
            anomalies_detected=len(anomalies_df),
            columns=list(processed_df.columns),
            amount_column=amount_col
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()