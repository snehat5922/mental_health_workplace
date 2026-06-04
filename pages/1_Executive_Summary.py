import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Executive Summary",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/mental_health_workplace.csv")

df = load_data()

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title("📊 Executive Summary Dashboard")
st.markdown(
    "Comprehensive overview of workplace mental health, productivity, and employee wellbeing."
)

st.divider()

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_employees = len(df)

avg_burnout = round(df["burnout_risk_score"].mean(), 2)

avg_satisfaction = round(df["job_satisfaction_score"].mean(), 2)

avg_productivity = round(df["productivity_score"].mean(), 2)

avg_wlb = round(df["work_life_balance_score"].mean(), 2)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "👥 Employees",
    f"{total_employees:,}"
)

col2.metric(
    "🔥 Avg Burnout",
    avg_burnout
)

col3.metric(
    "😊 Satisfaction",
    avg_satisfaction
)

col4.metric(
    "⚡ Productivity",
    avg_productivity
)

col5.metric(
    "⚖ Work-Life Balance",
    avg_wlb
)

st.divider()

# ---------------------------------------------------
# ROW 1
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    country_data = (
        df.groupby("country")
        .size()
        .reset_index(name="Employees")
        .sort_values(
            "Employees",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(
        country_data,
        x="country",
        y="Employees",
        title="Top 10 Countries by Employee Count",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    gender_data = (
        df["gender"]
        .value_counts()
        .reset_index()
    )

    gender_data.columns = ["Gender", "Count"]

    fig = px.pie(
        gender_data,
        names="Gender",
        values="Count",
        title="Gender Distribution",
        hole=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# ROW 2
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    industry_data = (
        df.groupby("industry")
        ["burnout_risk_score"]
        .mean()
        .reset_index()
        .sort_values(
            "burnout_risk_score",
            ascending=False
        )
    )

    fig = px.bar(
        industry_data,
        x="industry",
        y="burnout_risk_score",
        color="burnout_risk_score",
        title="Average Burnout Risk by Industry"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    work_model_data = (
        df.groupby("work_model")
        ["job_satisfaction_score"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        work_model_data,
        x="work_model",
        y="job_satisfaction_score",
        color="work_model",
        title="Job Satisfaction by Work Model"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# ROW 3
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig = px.scatter(
        df,
        x="job_satisfaction_score",
        y="productivity_score",
        color="work_model",
        size="burnout_risk_score",
        title="Productivity vs Satisfaction"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.histogram(
        df,
        x="burnout_risk_score",
        nbins=20,
        title="Burnout Risk Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ---------------------------------------------------
# EXECUTIVE INSIGHTS
# ---------------------------------------------------

st.subheader("📌 Executive Insights")

highest_burnout = (
    df.groupby("industry")
    ["burnout_risk_score"]
    .mean()
    .idxmax()
)

best_work_model = (
    df.groupby("work_model")
    ["job_satisfaction_score"]
    .mean()
    .idxmax()
)

top_country = (
    df["country"]
    .value_counts()
    .idxmax()
)

avg_sleep = round(
    df["sleep_hours_per_night"].mean(),
    2
)

st.success(
    f"""
    • Highest burnout risk observed in **{highest_burnout}** industry.

    • Employees prefer **{best_work_model}** work model with highest satisfaction.

    • Largest workforce comes from **{top_country}**.

    • Average employee sleep duration is **{avg_sleep} hours/night**.

    • Productivity shows a positive relationship with job satisfaction.

    • Burnout levels increase noticeably with long working hours.
    """
)

# ---------------------------------------------------
# HEALTH SCORE GAUGE
# ---------------------------------------------------

st.subheader("🏆 Organization Wellness Index")

wellness_score = round(
    (
        avg_satisfaction +
        avg_productivity +
        avg_wlb
    ) / 3 * 10,
    1
)

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=wellness_score,
        title={"text": "Overall Wellness Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"thickness": 0.3},
            "steps": [
                {"range": [0, 40]},
                {"range": [40, 70]},
                {"range": [70, 100]}
            ]
        }
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    "Wellness Index combines Productivity, Job Satisfaction and Work-Life Balance indicators."
)
