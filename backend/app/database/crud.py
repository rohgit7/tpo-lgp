import pandas as pd
from sqlalchemy.orm import Session

from app.database.models import (
    UploadedFile,
    Transaction
)

def get_transactions_by_file(
    db,
    file_id: str
):
    return (
        db.query(Transaction)
        .filter(
            Transaction.file_id == file_id
        )
        .all()
    )


def create_uploaded_file(
    db: Session,
    file_id: str,
    filename: str,
    filepath: str,
    rows_count: int,
    anomaly_count: int
):

    record = UploadedFile(
        file_id=file_id,
        filename=filename,
        filepath=filepath,
        rows_count=rows_count,
        anomaly_count=anomaly_count
    )

    db.add(record)

    db.commit()

    db.refresh(record)

    return record

def get_file_by_file_id(
    db: Session,
    file_id: str
):

    return (
        db.query(UploadedFile)
        .filter(
            UploadedFile.file_id == file_id
        )
        .first()
    )

def _find_first_matching_value(row_data, candidates, default=""):
    for candidate in candidates:
        for key in row_data:
            if (
                candidate == key
                or candidate in key
                or key in candidate
            ):
                value = row_data[key]
                if value is not None and str(value).strip() != "":
                    return value
    return default


def _normalize_date(value):
    if not value:
        return ""
    try:
        dt = pd.to_datetime(value, dayfirst=True, errors="coerce")
        return dt.strftime("%Y-%m-%d") if not pd.isna(dt) else str(value)
    except Exception:
        return str(value)


def _find_first_numeric_column(dataframe, row_data):
    numeric_cols = [
        col for col in dataframe.columns
        if pd.api.types.is_numeric_dtype(dataframe[col])
        and col not in ["anomaly_flag", "anomaly_score"]
        and not pd.api.types.is_bool_dtype(dataframe[col])
    ]

    if not numeric_cols:
        return 0

    best_col = max(
        numeric_cols,
        key=lambda col: float(dataframe[col].std(skipna=True) or 0)
    )

    return row_data.get(best_col, 0)


def create_transactions(
    db: Session,
    file_id: str,
    dataframe
):

    records = []

    field_aliases = {
        "transaction_date": [
            "transaction_date",
            "transaction date",
            "date",
            "txn_date",
            "txn date",
            "posted_date",
            "posted date",
            "posting_date",
            "posting date",
            "order_date",
            "sale_date"
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
            "particulars",
            "medicine_id",
            "product",
            "product_id"
        ],
        "category": [
            "category",
            "cat",
            "type",
            "department",
            "dept",
            "classification",
            "store_id",
            "location"
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
            "amount_usd",
            "units_sold",
            "sales",
            "revenue",
            "quantity",
            "qty"
        ]
    }

    for _, row in dataframe.iterrows():

        row_data = {
            str(k).strip().lower(): v
            for k, v in row.items()
        }

        transaction_date = _find_first_matching_value(
            row_data,
            field_aliases["transaction_date"],
            ""
        )

        description = _find_first_matching_value(
            row_data,
            field_aliases["description"],
            ""
        )

        category = _find_first_matching_value(
            row_data,
            field_aliases["category"],
            ""
        )

        if not description and "store_id" in row_data:
            description = row_data["store_id"]

        if not category and "medicine_id" in row_data:
            category = row_data["medicine_id"]

        amount = _find_first_matching_value(
            row_data,
            field_aliases["amount"],
            None
        )

        if amount is None:
            amount = _find_first_numeric_column(dataframe, row_data)

        transaction = Transaction(

            file_id=file_id,

            transaction_date=_normalize_date(
                transaction_date
            ),

            description=str(
                description
            ),

            category=str(
                category
            ),

            amount=float(
                amount
            ),

            anomaly_flag=bool(
                row_data.get(
                    "anomaly_flag",
                    0
                )
            ),

            anomaly_score=float(
                row_data.get(
                    "anomaly_score",
                    0
                )
            )
        )

        records.append(
            transaction
        )

    db.bulk_save_objects(
        records
    )

    db.commit()

def get_transactions_by_file(
    db: Session,
    file_id: str
):

    records = (
        db.query(Transaction)
        .filter(
            Transaction.file_id
            ==
            file_id
        )
        .all()
    )

    result = []

    for row in records:

        result.append({
            "transaction_date":
            row.transaction_date,

            "description":
            row.description,

            "category":
            row.category,

            "amount":
            row.amount,

            "anomaly_flag":
            row.anomaly_flag,

            "anomaly_score":
            row.anomaly_score
        })

    return result

import pandas as pd

def get_anomalies_by_file(
    db: Session,
    file_id: str
):
    records = (
        db.query(Transaction)
        .filter(
            Transaction.file_id == file_id,
            Transaction.anomaly_flag == True
        )
        .all()
    )

    return pd.DataFrame([
        {
            "transaction_date": row.transaction_date,
            "description": row.description,
            "category": row.category,
            "amount": row.amount,
            "anomaly_score": row.anomaly_score
        }
        for row in records
    ])