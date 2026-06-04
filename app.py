import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Mental Health Analytics",
    page_icon="🧠",
    layout="wide"
)

@st.cache_data
def load_data():
    return pd.read_csv("data/mental_health_workplace.csv")

df = load_data()

st.title("🧠 Mental Health Workplace Analytics Dashboard")

st.sidebar.header("Filters")

country = st.sidebar.multiselect(
    "Country",
    df["country"].unique(),
    default=df["country"].unique()
)

industry = st.sidebar.multiselect(
    "Industry",
    df["industry"].unique(),
    default=df["industry"].unique()
)

filtered_df = df[
    (df["country"].isin(country)) &
    (df["industry"].isin(industry))
]

# KPI CARDS

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric(
    "Employees",
    len(filtered_df)
)

col2.metric(
    "Avg Burnout",
    round(filtered_df["burnout_risk_score"].mean(),2)
)

col3.metric(
    "Avg Satisfaction",
    round(filtered_df["job_satisfaction_score"].mean(),2)
)

col4.metric(
    "Avg Productivity",
    round(filtered_df["productivity_score"].mean(),2)
)

col5.metric(
    "Avg WLB",
    round(filtered_df["work_life_balance_score"].mean(),2)
)

st.divider()

# Burnout by Industry

fig = px.bar(
    filtered_df.groupby("industry")["burnout_risk_score"]
    .mean()
    .reset_index(),
    x="industry",
    y="burnout_risk_score",
    title="Burnout Risk by Industry"
)

st.plotly_chart(fig, use_container_width=True)

# Satisfaction vs Productivity

fig2 = px.scatter(
    filtered_df,
    x="job_satisfaction_score",
    y="productivity_score",
    color="work_model",
    title="Productivity vs Satisfaction"
)

st.plotly_chart(fig2, use_container_width=True)
