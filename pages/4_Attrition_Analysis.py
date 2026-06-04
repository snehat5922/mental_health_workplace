import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Attrition Analysis",
    page_icon="🚪",
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

st.title("🚪 Employee Attrition Analysis")
st.markdown(
    "Identify workforce retention risks and understand factors influencing employee turnover."
)

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

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

work_model = st.sidebar.multiselect(
    "Work Model",
    df["work_model"].unique(),
    default=df["work_model"].unique()
)

filtered_df = df[
    (df["country"].isin(country))
    &
    (df["industry"].isin(industry))
    &
    (df["work_model"].isin(work_model))
]

# --------------------------------------------------
# DETERMINE ATTRITION COLUMN
# --------------------------------------------------

attrition_col = None

possible_cols = [
    "intention_to_leave",
    "turnover_intention",
    "attrition_risk",
    "leave_intention"
]

for col in possible_cols:
    if col in filtered_df.columns:
        attrition_col = col
        break

if attrition_col is None:
    st.error(
        "No attrition/intention-to-leave column found in dataset."
    )
    st.stop()

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

total_employees = len(filtered_df)

high_risk = len(
    filtered_df[
        filtered_df[attrition_col] >= 7
    ]
)

medium_risk = len(
    filtered_df[
        (filtered_df[attrition_col] >= 4)
        &
        (filtered_df[attrition_col] < 7)
    ]
)

avg_attrition = round(
    filtered_df[attrition_col].mean(),
    2
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👥 Employees",
    f"{total_employees:,}"
)

col2.metric(
    "🚨 High Risk",
    f"{high_risk:,}"
)

col3.metric(
    "⚠ Medium Risk",
    f"{medium_risk:,}"
)

col4.metric(
    "📊 Avg Attrition",
    avg_attrition
)

st.divider()

# --------------------------------------------------
# ATTRITION DISTRIBUTION
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig = px.histogram(
        filtered_df,
        x=attrition_col,
        nbins=20,
        title="Attrition Risk Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    attr_df = pd.DataFrame({
        "Risk Level": [
            "Low",
            "Medium",
            "High"
        ],
        "Employees": [
            len(filtered_df[
                filtered_df[attrition_col] < 4
            ]),
            medium_risk,
            high_risk
        ]
    })

    fig = px.pie(
        attr_df,
        names="Risk Level",
        values="Employees",
        hole=0.5,
        title="Attrition Categories"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# BURNOUT VS ATTRITION
# --------------------------------------------------

st.subheader("🔥 Burnout vs Attrition")

fig = px.scatter(
    filtered_df,
    x="burnout_risk_score",
    y=attrition_col,
    color="industry",
    trendline="ols",
    title="Burnout Impact on Attrition"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# SATISFACTION VS ATTRITION
# --------------------------------------------------

st.subheader("😊 Job Satisfaction vs Attrition")

fig = px.scatter(
    filtered_df,
    x="job_satisfaction_score",
    y=attrition_col,
    color="work_model",
    trendline="ols",
    title="Job Satisfaction Impact on Attrition"
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

    work_model_df = (
        filtered_df.groupby("work_model")[attrition_col]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        work_model_df,
        x="work_model",
        y=attrition_col,
        color="work_model",
        title="Attrition by Work Model"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    industry_df = (
        filtered_df.groupby("industry")[attrition_col]
        .mean()
        .reset_index()
        .sort_values(
            attrition_col,
            ascending=False
        )
    )

    fig = px.bar(
        industry_df,
        x="industry",
        y=attrition_col,
        color=attrition_col,
        title="Attrition by Industry"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------

st.subheader("📈 Correlation Analysis")

numeric_cols = filtered_df.select_dtypes(
    include="number"
).columns

corr = filtered_df[numeric_cols].corr()

fig = px.imshow(
    corr,
    text_auto=".2f",
    aspect="auto",
    title="Correlation Matrix"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# HIGH RISK EMPLOYEES
# --------------------------------------------------

st.subheader("🚨 Employees at High Attrition Risk")

risk_df = filtered_df[
    filtered_df[attrition_col] >= 8
]

display_cols = [
    "age",
    "gender",
    "country",
    "industry",
    "work_model",
    "burnout_risk_score",
    "job_satisfaction_score",
    attrition_col
]

display_cols = [
    col for col in display_cols
    if col in risk_df.columns
]

st.dataframe(
    risk_df[display_cols].head(50),
    use_container_width=True
)

# --------------------------------------------------
# ATTRITION RISK INDEX
# --------------------------------------------------

st.subheader("📊 Organizational Attrition Index")

risk_index = avg_attrition * 10

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=risk_index,
        title={"text": "Attrition Risk Index"},
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
# EXECUTIVE INSIGHTS
# --------------------------------------------------

st.subheader("📌 Attrition Insights")

highest_industry = industry_df.iloc[0]["industry"]

highest_score = round(
    industry_df.iloc[0][attrition_col],
    2
)

best_model = (
    work_model_df.sort_values(attrition_col)
    .iloc[0]["work_model"]
)

st.success(
    f"""
### Executive Summary

• Highest attrition risk observed in **{highest_industry}**.

• Lowest attrition risk found in **{best_model}** work model.

• Burnout strongly contributes to employee turnover intentions.

• Job satisfaction is negatively correlated with attrition.

• Employees experiencing high burnout and low satisfaction require immediate attention.

• Strengthening employee wellbeing programs can significantly improve retention.

• Continuous monitoring of workforce sentiment helps reduce future attrition.
"""
)
