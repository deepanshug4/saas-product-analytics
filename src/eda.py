"""
SaaS Growth Analytics

Main exploratory analysis script.

This script loads the generated SaaS datasets,
computes key business metrics, and visualizes
growth, acquisition, engagement, and revenue.

Author: <Your Name>
"""

import pandas as pd
import plotly.express as px

from metrics import (
    executive_summary,
    users_by_channel,
    channel_conversion,
    revenue_by_plan,
    event_distribution,
    monthly_signups,
)

# ----------------------------------------------------
# Load Data
# ----------------------------------------------------

users = pd.read_csv(
    "data/users.csv",
    parse_dates=["signup_date"],
)

events = pd.read_csv(
    "data/events.csv",
    parse_dates=["event_time"],
)

subscriptions = pd.read_csv(
    "data/subscriptions.csv",
    parse_dates=["start_date"],
)

print("\nDataset Shapes")
print(users.shape)
print(events.shape)
print(subscriptions.shape)

# ----------------------------------------------------
# Dataset Overview
# ----------------------------------------------------

print("=" * 70)
print("DATASET OVERVIEW")
print("=" * 70)

print(f"Users           : {len(users):,}")
print(f"Events          : {len(events):,}")
print(f"Subscriptions   : {len(subscriptions):,}")

print("\nUsers")
print(users.head())

print("\nEvents")
print(events.head())

print("\nSubscriptions")
print(subscriptions.head())

print("\nMissing Values")
print(users.isnull().sum())

# ----------------------------------------------------
# Executive KPIs
# ----------------------------------------------------

summary = executive_summary(
    users,
    events,
    subscriptions,
)

print("\n" + "=" * 70)
print("EXECUTIVE METRICS")
print("=" * 70)

print(f"Total Users             : {summary['users']:,}")
print(f"Paid Customers          : {summary['paid_users']:,}")
print(f"Activation Rate         : {summary['activation_rate']:.2%}")
print(f"Paid Conversion Rate    : {summary['conversion_rate']:.2%}")
print(f"Current MRR             : ${summary['mrr']:,.0f}")
print(f"ARPU                    : ${summary['arpu']:.2f}")
print(f"Churn Rate              : {summary['churn_rate']:.2%}")

# ----------------------------------------------------
# Monthly User Growth
# ----------------------------------------------------

growth = monthly_signups(users)

fig = px.line(
    growth,
    x="month",
    y="users",
    markers=True,
    title="Monthly User Signups",
)

fig.show()

# ----------------------------------------------------
# Acquisition Channels
# ----------------------------------------------------

channels = users_by_channel(users)

print("\nAcquisition Channels")
print(channels)

fig = px.bar(
    channels,
    x="acquisition_channel",
    y="users",
    title="Users by Acquisition Channel",
)

fig.show()

# ----------------------------------------------------
# Paid Conversion
# ----------------------------------------------------

conversion = channel_conversion(
    users,
    subscriptions,
)

print("\nChannel Conversion")
print(conversion)

fig = px.bar(
    conversion,
    x="acquisition_channel",
    y="conversion_rate",
    title="Paid Conversion Rate by Channel",
)

fig.show()

# ----------------------------------------------------
# Product Usage
# ----------------------------------------------------

events_summary = event_distribution(events)

print("\nEvent Distribution")
print(events_summary)

fig = px.bar(
    events_summary,
    x="event_name",
    y="events",
    title="Product Event Distribution",
)

fig.show()

# ----------------------------------------------------
# Revenue Analysis
# ----------------------------------------------------

revenue = revenue_by_plan(subscriptions)

print("\nRevenue by Plan")
print(revenue)

fig = px.bar(
    revenue,
    x="plan",
    y="revenue",
    text="revenue",
    title="Revenue by Subscription Plan",
)

fig.show()

# ----------------------------------------------------
# Business Insights
# ----------------------------------------------------

best_channel = conversion.iloc[0]

highest_plan = revenue.iloc[0]

print("\n" + "=" * 70)
print("BUSINESS INSIGHTS")
print("=" * 70)

print(
    f"""
1. Total user base has grown to {summary['users']:,} users.

2. Overall activation rate is {summary['activation_rate']:.1%},
   indicating how effectively new users reach product value.

3. Paid conversion currently stands at
   {summary['conversion_rate']:.1%}.

4. {best_channel['acquisition_channel']} is the highest
   converting acquisition channel
   ({best_channel['conversion_rate']:.1%}).

5. The {highest_plan['plan']} plan contributes the highest
   recurring revenue.

6. Current Monthly Recurring Revenue (MRR)
   is ${summary['mrr']:,.0f}.

7. Overall customer churn is
   {summary['churn_rate']:.1%}.
"""
)

print("=" * 70)
print("Analysis Complete")
print("=" * 70)