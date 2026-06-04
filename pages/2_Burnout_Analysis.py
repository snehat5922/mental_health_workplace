import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Burnout Analysis",
    page_icon="🔥",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("data/mental_health_workplace.csv")

df = load_data()

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🔥 Employee Burnout Analysis")
st.markdown(
    "Analyze burnout trends across industries, work models, workload, and demographics."
)

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

selected_country = st.sidebar.multiselect(
    "Country",
    df["country"].unique(),
    default=df["country"].unique()
)

selected_industry = st.sidebar.multiselect(
    "Industry",
    df["industry"].unique(),
    default=df["industry"].unique()
)

selected_work_model = st.sidebar.multiselect(
    "Work Model",
    df["work_model"].unique(),
    default=df["work_model"].unique()
)

filtered_df = df[
    (df["country"].isin(selected_country)) &
    (df["industry"].isin(selected_industry)) &
    (df["work_model"].isin(selected_work_model))
]

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

avg_burnout = round(
    filtered_df["burnout_risk_score"].mean(),
    2
)

high_risk = len(
    filtered_df[
        filtered_df["burnout_risk_score"] >= 7
    ]
)

moderate_risk = len(
    filtered_df[
        (filtered_df["burnout_risk_score"] >= 4)
        &
        (filtered_df["burnout_risk_score"] < 7)
    ]
)

low_risk = len(
    filtered_df[
        filtered_df["burnout_risk_score"] < 4
    ]
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🔥 Avg Burnout",
    avg_burnout
)

col2.metric(
    "🚨 High Risk",
    f"{high_risk:,}"
)

col3.metric(
    "⚠ Moderate Risk",
    f"{moderate_risk:,}"
)

col4.metric(
    "✅ Low Risk",
    f"{low_risk:,}"
)

st.divider()

# --------------------------------------------------
# BURNOUT DISTRIBUTION
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig = px.histogram(
        filtered_df,
        x="burnout_risk_score",
        nbins=25,
        title="Burnout Risk Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    burnout_zone = pd.DataFrame({
        "Risk Level": ["Low", "Moderate", "High"],
        "Employees": [
            low_risk,
            moderate_risk,
            high_risk
        ]
    })

    fig = px.pie(
        burnout_zone,
        names="Risk Level",
        values="Employees",
        hole=0.5,
        title="Burnout Risk Categories"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# INDUSTRY ANALYSIS
# --------------------------------------------------

st.subheader("🏭 Burnout by Industry")

industry_df = (
    filtered_df.groupby("industry")
    ["burnout_risk_score"]
    .mean()
    .reset_index()
    .sort_values(
        "burnout_risk_score",
        ascending=False
    )
)

fig = px.bar(
    industry_df,
    x="industry",
    y="burnout_risk_score",
    color="burnout_risk_score",
    title="Average Burnout Risk by Industry",
    text_auto=".2f"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# WORK MODEL ANALYSIS
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    model_df = (
        filtered_df.groupby("work_model")
        ["burnout_risk_score"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        model_df,
        x="work_model",
        y="burnout_risk_score",
        color="work_model",
        title="Burnout by Work Model"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.box(
        filtered_df,
        x="work_model",
        y="burnout_risk_score",
        color="work_model",
        title="Burnout Spread by Work Model"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# WORKLOAD IMPACT
# --------------------------------------------------

st.subheader("⏰ Workload Impact")

col1, col2 = st.columns(2)

with col1:

    fig = px.scatter(
        filtered_df,
        x="weekly_work_hours",
        y="burnout_risk_score",
        color="industry",
        trendline="ols",
        title="Work Hours vs Burnout"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.scatter(
        filtered_df,
        x="overtime_hours",
        y="burnout_risk_score",
        color="work_model",
        trendline="ols",
        title="Overtime vs Burnout"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# COUNTRY ANALYSIS
# --------------------------------------------------

st.subheader("🌍 Country-wise Burnout")

country_df = (
    filtered_df.groupby("country")
    ["burnout_risk_score"]
    .mean()
    .reset_index()
)

fig = px.choropleth(
    country_df,
    locations="country",
    locationmode="country names",
    color="burnout_risk_score",
    title="Global Burnout Risk Map"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# HIGH RISK EMPLOYEES
# --------------------------------------------------

st.subheader("🚨 High Burnout Risk Employees")

risk_df = filtered_df[
    filtered_df["burnout_risk_score"] >= 8
]

display_cols = [
    "age",
    "gender",
    "industry",
    "country",
    "weekly_work_hours",
    "overtime_hours",
    "burnout_risk_score"
]

available_cols = [
    col for col in display_cols
    if col in risk_df.columns
]

st.dataframe(
    risk_df[available_cols].head(50),
    use_container_width=True
)

# --------------------------------------------------
# GAUGE CHART
# --------------------------------------------------

st.subheader("📈 Burnout Index")

burnout_index = avg_burnout * 10

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=burnout_index,
        title={"text": "Organization Burnout Index"},
        gauge={
            "axis": {"range": [0, 100]},
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

# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------

st.subheader("📌 Key Insights")

highest_industry = (
    industry_df.iloc[0]["industry"]
)

highest_score = round(
    industry_df.iloc[0]["burnout_risk_score"],
    2
)

lowest_model = (
    model_df.sort_values(
        "burnout_risk_score"
    )
    .iloc[0]["work_model"]
)

avg_hours = round(
    filtered_df["weekly_work_hours"].mean(),
    1
)

st.success(
    f"""
### Executive Summary

• Highest burnout observed in **{highest_industry}**
with an average score of **{highest_score}**.

• Employees work an average of **{avg_hours} hours/week**.

• **{lowest_model}** work model records the lowest burnout.

• Overtime hours show a strong positive relationship with burnout.

• High-risk employees should be prioritized for intervention programs.

• Workload balancing and mental health initiatives can significantly reduce burnout risk.
"""
)
