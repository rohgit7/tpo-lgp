from fastapi import APIRouter
from fastapi import HTTPException

from app.models.request_models import (
    ChatRequest
)

import pandas as pd

from app.database.db import SessionLocal

from app.database.crud import (
    get_transactions_by_file
)


from app.services.llm_service import (
    ask_shakun
)

router = APIRouter(
    tags=["Chat"]
)


@router.post(
    "/chat/{file_id}"
)
async def chat(
    file_id: str,
    body: ChatRequest
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

        answer = ask_shakun(
            df,
            body.query
        )

        return {
            "query": body.query,
            "answer": answer,
            "aggregator": "Qwen3-32B"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )