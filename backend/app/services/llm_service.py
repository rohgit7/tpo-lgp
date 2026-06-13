import os
import pandas as pd

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from app.services.anomaly_detector import (
    find_amount_column
)

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


def build_context(
    df: pd.DataFrame,
    question: str
):
    """
    Build compact dataframe context
    for the LLM.
    """

    total_rows = len(df)

    amount_col = find_amount_column(df)

    total_amount = 0

    if amount_col:

        numeric_series = pd.to_numeric(
            df[amount_col]
            .astype(str)
            .str.replace(
                r"[^\d\.]",
                "",
                regex=True
            ),
            errors="coerce"
        ).fillna(0)

        total_amount = round(
            numeric_series.sum(),
            2
        )

    anomalies_df = pd.DataFrame()

    if "anomaly_flag" in df.columns:

        anomalies_df = df[
            df["anomaly_flag"] == 1
        ]

    anomaly_count = len(
        anomalies_df
    )

    sample_df = pd.concat([
        df.head(10),
        anomalies_df.head(10)
    ]).drop_duplicates()

    if "raw_text" in sample_df.columns:

        sample_df = sample_df.drop(
            columns=["raw_text"]
        )

    markdown_table = sample_df.to_markdown(
        index=False
    )

    if len(markdown_table) > 10000:

        markdown_table = (
            markdown_table[:10000]
            +
            "\n\n[Context Truncated]"
        )

    return f"""
Dataset Statistics

Total Transactions: {total_rows}

Total Amount: {total_amount}

Anomalies Found: {anomaly_count}

Dataset Sample:

{markdown_table}

User Question:

{question}

Answer:
"""


def ask_shakun(
    df: pd.DataFrame,
    question: str
):
    """
    Query HuggingFace model.
    """

    if not HF_TOKEN:

        raise Exception(
            "HF_TOKEN not configured"
        )

    context = build_context(
        df,
        question
    )

    client = InferenceClient(
        api_key=HF_TOKEN
    )

    response = (
        client.chat.completions.create(
            model="Qwen/Qwen3-32B",
            messages=[
                {
                    "role": "system",
                    "content":
                    """
                    You are Shakun AI,
                    an expert financial
                    forensic analyst.

                    Analyze anomalies,
                    unusual transactions,
                    spending patterns
                    and risks.

                    Be concise and actionable.
                    """
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            max_tokens=400,
            temperature=0.6
        )
    )

    return (
        response
        .choices[0]
        .message
        .content
    )