"""
SaaS Cohort Retention Analysis

Builds a monthly cohort retention matrix based on user activity.
"""

import pandas as pd
import plotly.express as px


# ----------------------------------------------------
# Build Cohort Matrix
# ----------------------------------------------------

def build_retention_matrix(users: pd.DataFrame,
                           events: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a monthly cohort retention matrix.

    Returns
    -------
    DataFrame
        Cohort retention percentages.
    """

    # -----------------------------
    # Prepare users
    # -----------------------------

    users = users.copy()

    users["cohort_month"] = (
        users["signup_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # -----------------------------
    # Prepare events
    # -----------------------------

    events = events.copy()

    events["activity_month"] = (
        events["event_time"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # -----------------------------
    # Merge users with activity
    # -----------------------------

    cohort = events.merge(
        users[
            [
                "user_id",
                "cohort_month",
            ]
        ],
        on="user_id",
        how="left",
    )

    # -----------------------------
    # Calculate cohort age
    # -----------------------------

    cohort["cohort_index"] = (
        (
            cohort["activity_month"].dt.year
            - cohort["cohort_month"].dt.year
        ) * 12
        +
        (
            cohort["activity_month"].dt.month
            - cohort["cohort_month"].dt.month
        )
    )

    # -----------------------------
    # Users per cohort/month
    # -----------------------------

    grouped = (
        cohort.groupby(
            [
                "cohort_month",
                "cohort_index",
            ]
        )["user_id"]
        .nunique()
        .reset_index()
    )

    # -----------------------------
    # Pivot
    # -----------------------------

    retention = grouped.pivot(
        index="cohort_month",
        columns="cohort_index",
        values="user_id",
    )

    # -----------------------------
    # Divide by Month 0
    # -----------------------------

    cohort_size = retention[0]

    retention = retention.fillna(0)

    retention = retention.divide(
        cohort_size,
        axis=0,
    )

    retention = (
        retention * 100
    ).round(1)

    retention.index = (
        retention.index.strftime("%Y-%m")
    )

    return retention


# ----------------------------------------------------
# Heatmap
# ----------------------------------------------------

def plot_retention_heatmap(
    retention: pd.DataFrame,
):
    """
    Creates an interactive Plotly
    retention heatmap.
    """

    fig = px.imshow(
        retention,
        text_auto=True,
        color_continuous_scale="Blues",
        aspect="auto",
        labels={
            "x": "Months Since Signup",
            "y": "Signup Cohort",
            "color": "Retention %",
        },
        title="Monthly Cohort Retention",
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Signup Cohort",
    )

    return fig


# ----------------------------------------------------
# CLI Runner
# ----------------------------------------------------

if __name__ == "__main__":

    users = pd.read_csv(
        "data/users.csv",
        parse_dates=["signup_date"],
    )

    events = pd.read_csv(
        "data/events.csv",
        parse_dates=["event_time"],
    )

    retention = build_retention_matrix(
        users,
        events,
    )

    print(retention)

    fig = plot_retention_heatmap(
        retention,
    )

    fig.show()