import pandas as pd
import plotly.graph_objects as go

from app.services.anomaly_detector import (
    find_amount_column
)


def create_visualization(df: pd.DataFrame):
    """
    Generate Plotly visualization
    highlighting anomalies.
    """

    amount_col = find_amount_column(df)

    if not amount_col:
        raise Exception(
            "No amount column found"
        )

    plot_df = df.copy()

    plot_df[amount_col] = pd.to_numeric(
        plot_df[amount_col]
        .astype(str)
        .str.replace(
            r"[^\d\.]",
            "",
            regex=True
        ),
        errors="coerce"
    ).fillna(0)

    # Find date column

    date_col = None

    for col in plot_df.columns:

        if any(
            keyword in str(col).lower()
            for keyword in [
                "date",
                "time",
                "timestamp"
            ]
        ):

            try:

                plot_df[col] = pd.to_datetime(
                    plot_df[col],
                    errors="coerce"
                )

                if plot_df[col].notna().sum() > 0:
                    date_col = col
                    break

            except Exception:
                pass

    x_axis = (
        plot_df[date_col]
        if date_col
        else plot_df.index
    )

    normal_df = plot_df[
        plot_df["anomaly_flag"] == 0
    ]

    anomaly_df = plot_df[
        plot_df["anomaly_flag"] == 1
    ]

    fig = go.Figure()

    # Transaction trend

    fig.add_trace(
        go.Scatter(
            x=x_axis,
            y=plot_df[amount_col],
            mode="lines",
            name="Transactions"
        )
    )

    # Normal transactions

    fig.add_trace(
        go.Scatter(
            x=(
                normal_df[date_col]
                if date_col
                else normal_df.index
            ),
            y=normal_df[amount_col],
            mode="markers",
            name="Normal"
        )
    )

    # Anomalies

    fig.add_trace(
        go.Scatter(
            x=(
                anomaly_df[date_col]
                if date_col
                else anomaly_df.index
            ),
            y=anomaly_df[amount_col],
            mode="markers",
            name="Anomaly",
            marker=dict(
                size=12,
                symbol="x"
            )
        )
    )

    fig.update_layout(
        title="Transaction Anomaly Analysis",
        xaxis_title=(
            date_col
            if date_col
            else "Index"
        ),
        yaxis_title=amount_col
    )

    return fig