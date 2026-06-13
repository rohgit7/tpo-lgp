from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean
)

from app.database.db import Base


class UploadedFile(Base):

    __tablename__ = "uploaded_files"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_id = Column(
        String,
        unique=True,
        nullable=False
    )

    filename = Column(
        String,
        nullable=False
    )

    filepath = Column(
        String,
        nullable=False
    )

    rows_count = Column(
        Integer,
        default=0
    )

    anomaly_count = Column(
        Integer,
        default=0
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_id = Column(
        String,
        nullable=False,
        index=True
    )

    transaction_date = Column(
        String,
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    category = Column(
        String,
        nullable=True
    )

    amount = Column(
        Float,
        default=0
    )

    anomaly_flag = Column(
        Boolean,
        default=False
    )

    anomaly_score = Column(
        Float,
        default=0
    )