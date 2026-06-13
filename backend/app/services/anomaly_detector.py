import pandas as pd
import numpy as np


def find_amount_column(df: pd.DataFrame) -> str:
    """
    Dynamically identify the primary transaction amount column.
    """
    keywords = [
        "amount",
        "money",
        "value",
        "amt",
        "debit",
        "credit",
        "price",
        "total"
    ]

    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in keywords):
            return col

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    return numeric_cols[0] if len(numeric_cols) > 0 else None


def find_category_column(df: pd.DataFrame):
    """
    Identify category column for grouped anomaly detection.
    """

    category_keywords = [
        "category",
        "type",
        "kind",
        "dept",
        "department"
    ]

    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in category_keywords):
            if df[col].dtype == object and df[col].nunique() < 50:
                return col

    return None


def run_iqr_anomaly_detection(
    df: pd.DataFrame,
    multiplier: float = 2.5
) -> pd.DataFrame:
    """
    Per-category IQR anomaly detection.
    """

    df_processed = df.copy()

    amount_col = find_amount_column(df_processed)

    if not amount_col:
        df_processed["anomaly_flag"] = 0
        df_processed["anomaly_score"] = 0.0
        return df_processed

    df_processed[amount_col] = pd.to_numeric(
        df_processed[amount_col]
        .astype(str)
        .str.replace(r"[^\d\.]", "", regex=True),
        errors="coerce"
    ).fillna(0.0)

    category_col = find_category_column(df_processed)

    anomaly_flags = pd.Series(
        0,
        index=df_processed.index
    )

    anomaly_scores = pd.Series(
        0.0,
        index=df_processed.index
    )

    groups = (
        df_processed.groupby(category_col)
        if category_col
        else [(None, df_processed)]
    )

    for _, group in groups:

        q1 = group[amount_col].quantile(0.25)
        q3 = group[amount_col].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        is_anomaly = (
            (group[amount_col] < lower_bound)
            |
            (group[amount_col] > upper_bound)
        )

        anomaly_flags[group.index[is_anomaly]] = 1

        mean_value = group[amount_col].mean()
        std_dev = group[amount_col].std()

        if std_dev and std_dev > 0:

            scores = (
                (
                    group[amount_col] - mean_value
                ) / std_dev
            ).abs().round(2)

        else:
            scores = pd.Series(
                0.0,
                index=group.index
            )

        anomaly_scores[group.index] = scores

    df_processed["anomaly_flag"] = anomaly_flags
    df_processed["anomaly_score"] = anomaly_scores

    return df_processed