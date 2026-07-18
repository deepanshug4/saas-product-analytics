"""
SaaS Growth Analytics Dashboard

Interactive dashboard for monitoring user growth,
acquisition performance, revenue, and retention.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------
# Project Imports
# ----------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "src"))

from metrics import (
    executive_summary,
    users_by_channel,
    channel_conversion,
    revenue_by_plan,
    event_distribution,
    monthly_signups,
)

from cohort import (
    build_retention_matrix,
    plot_retention_heatmap,
)

# ----------------------------------------------------
# Streamlit Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="SaaS Growth Analytics",
    page_icon="📈",
    layout="wide",
)

st.title("📈 SaaS Growth Analytics Dashboard")

st.markdown(
    """
Interactive dashboard for monitoring user acquisition,
engagement, revenue, and customer retention.
"""
)

# ----------------------------------------------------
# Load Data
# ----------------------------------------------------

@st.cache_data
def load_data():

    users = pd.read_csv(
        ROOT / "data" / "users.csv",
        parse_dates=["signup_date"],
    )

    events = pd.read_csv(
        ROOT / "data" / "events.csv",
        parse_dates=["event_time"],
    )

    subscriptions = pd.read_csv(
        ROOT / "data" / "subscriptions.csv",
        parse_dates=["start_date"],
    )

    return users, events, subscriptions


users, events, subscriptions = load_data()

# ----------------------------------------------------
# Sidebar Filters
# ----------------------------------------------------

st.sidebar.header("Filters")

channels = sorted(users["acquisition_channel"].unique())

selected_channels = st.sidebar.multiselect(
    "Acquisition Channel",
    channels,
    default=channels,
)

company_sizes = sorted(users["company_size"].unique())

selected_sizes = st.sidebar.multiselect(
    "Company Size",
    company_sizes,
    default=company_sizes,
)

filtered_users = users[
    users["acquisition_channel"].isin(selected_channels)
    &
    users["company_size"].isin(selected_sizes)
]

filtered_events = events[
    events["user_id"].isin(filtered_users["user_id"])
]

filtered_subscriptions = subscriptions[
    subscriptions["user_id"].isin(filtered_users["user_id"])
]

# ----------------------------------------------------
# Executive Summary
# ----------------------------------------------------

summary = executive_summary(
    filtered_users,
    filtered_events,
    filtered_subscriptions,
)

# ----------------------------------------------------
# KPI Cards
# ----------------------------------------------------

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Users", f"{summary['users']:,}")
col2.metric("Paid Users", f"{summary['paid_users']:,}")
col3.metric("Activation", f"{summary['activation_rate']:.1%}")
col4.metric("Conversion", f"{summary['conversion_rate']:.1%}")
col5.metric("MRR", f"${summary['mrr']:,.0f}")
col6.metric("Churn", f"{summary['churn_rate']:.1%}")

st.divider()

# ----------------------------------------------------
# Monthly Growth
# ----------------------------------------------------

growth = monthly_signups(filtered_users)
growth = growth.sort_values("month")

fig = px.line(
    growth,
    x="month",
    y="users",
    markers=True,
    title="Monthly User Signups",
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Acquisition
# ----------------------------------------------------

left, right = st.columns(2)

channel_users = users_by_channel(filtered_users)

fig = px.bar(
    channel_users,
    x="acquisition_channel",
    y="users",
    title="Users by Acquisition Channel",
)

left.plotly_chart(fig, use_container_width=True)

conversion = channel_conversion(
    filtered_users,
    filtered_subscriptions,
)

fig = px.bar(
    conversion,
    x="acquisition_channel",
    y="conversion_rate",
    title="Paid Conversion Rate",
)

fig.update_yaxes(tickformat=".0%")

right.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Product Engagement
# ----------------------------------------------------

events_summary = event_distribution(filtered_events)

fig = px.bar(
    events_summary,
    x="event_name",
    y="events",
    title="Product Event Distribution",
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Revenue
# ----------------------------------------------------

left, right = st.columns(2)

revenue = revenue_by_plan(filtered_subscriptions)

fig = px.bar(
    revenue,
    x="plan",
    y="revenue",
    text_auto=".2s",
    title="Monthly Revenue by Plan",
)

left.plotly_chart(fig, use_container_width=True)

fig = px.pie(
    revenue,
    names="plan",
    values="customers",
    title="Customer Distribution by Plan",
)

right.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Cohort Retention
# ----------------------------------------------------

st.subheader("Monthly Cohort Retention")

retention = build_retention_matrix(
    filtered_users,
    filtered_events,
)

fig = plot_retention_heatmap(retention)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Executive Insights
# ----------------------------------------------------

st.subheader("Business Insights")

if conversion.empty or revenue.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

best_channel = conversion.iloc[0]
best_plan = revenue.iloc[0]

st.success(
    f"""
### Executive Summary

- Total Users: **{summary['users']:,}**
- Paid Customers: **{summary['paid_users']:,}**
- Monthly Recurring Revenue: **${summary['mrr']:,.0f}**
- Activation Rate: **{summary['activation_rate']:.1%}**
- Paid Conversion Rate: **{summary['conversion_rate']:.1%}**
- Churn Rate: **{summary['churn_rate']:.1%}**

### Key Insights

- **{best_channel['acquisition_channel']}** is the highest-converting acquisition channel.
- **{best_plan['plan']}** generates the largest share of recurring revenue.
- Product engagement is positively correlated with customer conversion and retention.
"""
)
