import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()

random.seed(42)
np.random.seed(42)

NUM_USERS = 10000

START_DATE = datetime(2024, 1, 1)

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

CHANNELS = {
    "Organic Search": {"convert": 0.30, "churn": 0.12},
    "Referral": {"convert": 0.40, "churn": 0.08},
    "Partner": {"convert": 0.28, "churn": 0.15},
    "Social Media": {"convert": 0.18, "churn": 0.22},
    "Paid Ads": {"convert": 0.15, "churn": 0.30},
}

COMPANY_SIZES = [
    "SMB",
    "Mid Market",
    "Enterprise",
]

PLANS = {
    "Starter": 29,
    "Growth": 99,
    "Enterprise": 499,
}

PLAN_WEIGHTS = {
    "SMB": [0.75, 0.22, 0.03],
    "Mid Market": [0.25, 0.60, 0.15],
    "Enterprise": [0.05, 0.35, 0.60],
}

EVENTS = [
    "used_dashboard",
    "created_project",
    "created_report",
    "invited_team_member",
    "exported_data",
]

# ----------------------------------------------------
# Generate Users
# ----------------------------------------------------

users = []

for user_id in range(1, NUM_USERS + 1):

    signup = START_DATE + timedelta(
        days=random.randint(0, 365)
    )

    channel = random.choice(list(CHANNELS.keys()))

    company_size = random.choices(
        COMPANY_SIZES,
        weights=[0.60, 0.30, 0.10],
    )[0]

    engagement = random.randint(20, 100)

    users.append(
        {
            "user_id": user_id,
            "signup_date": signup.date(),
            "country": fake.country(),
            "acquisition_channel": channel,
            "company_size": company_size,
            "engagement_score": engagement,
        }
    )

users_df = pd.DataFrame(users)

# ----------------------------------------------------
# Generate Events
# ----------------------------------------------------

events = []

for _, user in users_df.iterrows():

    signup = datetime.combine(
        user.signup_date,
        datetime.min.time(),
    )

    # signup event
    events.append(
        {
            "user_id": user.user_id,
            "event_name": "signup",
            "event_time": signup,
        }
    )

    engagement = user.engagement_score

    # Higher engagement = more active months
    active_months = random.randint(2, 6)

    invited = False

    for month in range(active_months):

        month_start = signup + timedelta(days=30 * month)

        monthly_events = max(
            1,
            int(
                np.random.normal(
                    engagement / 8,
                    2,
                )
            ),
        )

        for _ in range(monthly_events):

            event = random.choices(
                EVENTS,
                weights=[5, 3, 3, 1, 2],
            )[0]

            if event == "invited_team_member":
                invited = True

            event_time = month_start + timedelta(
                days=random.randint(0, 27),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            events.append(
                {
                    "user_id": user.user_id,
                    "event_name": event,
                    "event_time": event_time,
                }
            )

    users_df.loc[
        users_df.user_id == user.user_id,
        "invited_team"
    ] = invited

events_df = pd.DataFrame(events)

# ----------------------------------------------------
# Generate Subscriptions
# ----------------------------------------------------

subscriptions = []

for _, user in users_df.iterrows():

    convert_prob = CHANNELS[
        user.acquisition_channel
    ]["convert"]

    engagement_bonus = (
        user.engagement_score / 100
    ) * 0.25

    final_probability = min(
        convert_prob + engagement_bonus,
        0.90,
    )

    if random.random() > final_probability:
        continue

    plan = random.choices(
        list(PLANS.keys()),
        weights=PLAN_WEIGHTS[user.company_size],
    )[0]

    start_date = (
        datetime.combine(
            user.signup_date,
            datetime.min.time(),
        )
        + timedelta(days=random.randint(5, 30))
    )

    churn_prob = CHANNELS[
        user.acquisition_channel
    ]["churn"]

    if user.invited_team:
        churn_prob *= 0.6

    if user.engagement_score > 70:
        churn_prob *= 0.7

    status = (
        "Cancelled"
        if random.random() < churn_prob
        else "Active"
    )

    subscriptions.append(
        {
            "user_id": user.user_id,
            "plan": plan,
            "start_date": start_date.date(),
            "monthly_revenue": PLANS[plan],
            "status": status,
        }
    )

subscriptions_df = pd.DataFrame(subscriptions)

# ----------------------------------------------------
# Save Files
# ----------------------------------------------------

users_df.to_csv(
    "data/users.csv",
    index=False,
)

events_df.to_csv(
    "data/events.csv",
    index=False,
)

subscriptions_df.to_csv(
    "data/subscriptions.csv",
    index=False,
)

# ----------------------------------------------------
# Summary
# ----------------------------------------------------

print("=" * 60)
print("DATA GENERATED")
print("=" * 60)

print(f"Users          : {len(users_df):,}")
print(f"Events         : {len(events_df):,}")
print(f"Subscriptions  : {len(subscriptions_df):,}")

print()

print("Conversion by Channel")

merged = (
    users_df.merge(
        subscriptions_df[["user_id"]],
        on="user_id",
        how="left",
        indicator=True,
    )
)

conversion = (
    merged.assign(
        converted=lambda x: x["_merge"] == "both"
    )
    .groupby("acquisition_channel")
    .converted.mean()
)

print(conversion.round(3))

print()

print("Plan Distribution")

print(
    subscriptions_df["plan"]
    .value_counts(normalize=True)
    .round(2)
)