import pandas as pd


# ----------------------------------------------------
# User Metrics
# ----------------------------------------------------

def total_users(users: pd.DataFrame) -> int:
    """
    Total registered users.
    """
    return users["user_id"].nunique()


def paid_users(subscriptions: pd.DataFrame) -> int:
    """
    Total paying customers.
    """
    return subscriptions["user_id"].nunique()


# ----------------------------------------------------
# Activation Metrics
# ----------------------------------------------------

def activation_rate(users: pd.DataFrame, events: pd.DataFrame) -> float:
    """
    Percentage of users that completed at least one
    meaningful activation event.
    """

    activation_events = [
        "created_project",
        "created_report",
        "invited_team_member",
    ]

    activated = (
        events[
            events["event_name"].isin(activation_events)
        ]["user_id"]
        .nunique()
    )

    if users.empty:
        return 0

    return activated / len(users)


# ----------------------------------------------------
# Conversion Metrics
# ----------------------------------------------------

def paid_conversion(users: pd.DataFrame,
                    subscriptions: pd.DataFrame) -> float:
    """
    Percentage of users that converted to paid.
    """

    if users.empty:
        return 0
    
    return (
        subscriptions["user_id"].nunique() / len(users)
    )


# ----------------------------------------------------
# Revenue Metrics
# ----------------------------------------------------

def monthly_recurring_revenue(
    subscriptions: pd.DataFrame,
) -> float:
    """
    Current Monthly Recurring Revenue.
    """

    active = subscriptions[
        subscriptions["status"] == "Active"
    ]

    return active["monthly_revenue"].sum()


def arpu(subscriptions: pd.DataFrame) -> float:
    """
    Average Revenue Per Paying User.
    """

    active = subscriptions[
        subscriptions["status"] == "Active"
    ]

    if active.empty:
        return 0

    return active["monthly_revenue"].mean()


def revenue_by_plan(
    subscriptions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Monthly revenue split by subscription plan.
    """

    active = subscriptions[
        subscriptions["status"] == "Active"
    ]

    return (
        active.groupby("plan", as_index=False)
        .agg(
            revenue=("monthly_revenue", "sum"),
            customers=("user_id", "count"),
        )
        .sort_values(
            "revenue",
            ascending=False,
        )
    )


# ----------------------------------------------------
# Acquisition Metrics
# ----------------------------------------------------

def users_by_channel(
    users: pd.DataFrame,
) -> pd.DataFrame:
    """
    Total users acquired by channel.
    """

    return (
        users.groupby(
            "acquisition_channel",
            as_index=False,
        )
        .agg(
            users=("user_id", "count")
        )
        .sort_values(
            "users",
            ascending=False,
        )
    )


def channel_conversion(
    users: pd.DataFrame,
    subscriptions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Paid conversion rate by acquisition channel.
    """

    conversion = (
        users.merge(
            subscriptions[["user_id"]],
            on="user_id",
            how="left",
            indicator=True,
        )
        .assign(
            converted=lambda x: x["_merge"] == "both"
        )
        .groupby(
            "acquisition_channel",
            as_index=False,
        )
        .agg(
            conversion_rate=("converted", "mean"),
            users=("user_id", "count"),
        )
        .sort_values(
            "conversion_rate",
            ascending=False,
        )
    )

    return conversion


# ----------------------------------------------------
# Engagement Metrics
# ----------------------------------------------------

def event_distribution(
    events: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count of each product event.
    """

    return (
        events.groupby(
            "event_name",
            as_index=False,
        )
        .agg(
            events=("user_id", "count")
        )
        .sort_values(
            "events",
            ascending=False,
        )
    )


def monthly_signups(
    users: pd.DataFrame,
) -> pd.DataFrame:
    """
    Monthly signup trend.
    """

    signup = users.copy()

    signup["month"] = (
        signup["signup_date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        signup.groupby(
            "month",
            as_index=False,
        )
        .agg(
            users=("user_id", "count")
        )
    )


# ----------------------------------------------------
# Churn Metrics
# ----------------------------------------------------

def churn_rate(
    subscriptions: pd.DataFrame,
) -> float:
    """
    Percentage of paying customers
    that have churned.
    """

    if subscriptions.empty:
        return 0

    churned = (
        subscriptions["status"]
        == "Cancelled"
    ).sum()

    return churned / len(subscriptions)


# ----------------------------------------------------
# Executive Summary
# ----------------------------------------------------

def executive_summary(
    users,
    events,
    subscriptions,
):
    """
    Returns dashboard KPI dictionary.
    """

    return {
        "users": total_users(users),
        "paid_users": paid_users(subscriptions),
        "activation_rate": activation_rate(
            users,
            events,
        ),
        "conversion_rate": paid_conversion(
            users,
            subscriptions,
        ),
        "mrr": monthly_recurring_revenue(
            subscriptions,
        ),
        "arpu": arpu(subscriptions),
        "churn_rate": churn_rate(
            subscriptions,
        ),
    }