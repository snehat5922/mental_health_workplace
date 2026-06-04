import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Lifestyle Impact",
    page_icon="🌱",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    return pd.read_csv("data/mental_health_workplace.csv")

df = load_data()

# =====================================================
# TITLE
# =====================================================

st.title("🌱 Lifestyle Impact Analysis")
st.markdown(
    "Understand how lifestyle habits influence employee wellbeing, productivity, and burnout."
)

st.divider()

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Lifestyle Filters")

countries = st.sidebar.multiselect(
    "Country",
    sorted(df["country"].unique()),
    default=sorted(df["country"].unique())
)

industries = st.sidebar.multiselect(
    "Industry",
    sorted(df["industry"].unique()),
    default=sorted(df["industry"].unique())
)

filtered_df = df[
    (df["country"].isin(countries))
    &
    (df["industry"].isin(industries))
]

# =====================================================
# KPI SECTION
# =====================================================

avg_sleep = round(
    filtered_df["sleep_hours_per_night"].mean(),
    2
)

avg_wlb = round(
    filtered_df["work_life_balance_score"].mean(),
    2
)

avg_productivity = round(
    filtered_df["productivity_score"].mean(),
    2
)

avg_burnout = round(
    filtered_df["burnout_risk_score"].mean(),
    2
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "😴 Avg Sleep",
    f"{avg_sleep} hrs"
)

col2.metric(
    "⚖ Work-Life Balance",
    avg_wlb
)

col3.metric(
    "⚡ Productivity",
    avg_productivity
)

col4.metric(
    "🔥 Burnout",
    avg_burnout
)

st.divider()

# =====================================================
# SLEEP ANALYSIS
# =====================================================

st.subheader("😴 Sleep Impact")

col1, col2 = st.columns(2)

with col1:

    fig = px.scatter(
        filtered_df,
        x="sleep_hours_per_night",
        y="productivity_score",
        color="work_model",
        trendline="ols",
        title="Sleep vs Productivity"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.scatter(
        filtered_df,
        x="sleep_hours_per_night",
        y="burnout_risk_score",
        color="industry",
        trendline="ols",
        title="Sleep vs Burnout"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# EXERCISE ANALYSIS
# =====================================================

if "exercise_frequency" in filtered_df.columns:

    st.subheader("🏃 Exercise Impact")

    col1, col2 = st.columns(2)

    with col1:

        exercise_prod = (
            filtered_df.groupby("exercise_frequency")
            ["productivity_score"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            exercise_prod,
            x="exercise_frequency",
            y="productivity_score",
            color="productivity_score",
            title="Exercise vs Productivity"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        exercise_sat = (
            filtered_df.groupby("exercise_frequency")
            ["job_satisfaction_score"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            exercise_sat,
            x="exercise_frequency",
            y="job_satisfaction_score",
            color="job_satisfaction_score",
            title="Exercise vs Satisfaction"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# WORK-LIFE BALANCE
# =====================================================

st.subheader("⚖ Work-Life Balance Analysis")

col1, col2 = st.columns(2)

with col1:

    fig = px.scatter(
        filtered_df,
        x="work_life_balance_score",
        y="productivity_score",
        color="work_model",
        trendline="ols",
        title="Work-Life Balance vs Productivity"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.scatter(
        filtered_df,
        x="work_life_balance_score",
        y="burnout_risk_score",
        color="industry",
        trendline="ols",
        title="Work-Life Balance vs Burnout"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# WELLNESS SEGMENTATION
# =====================================================

st.subheader("🌟 Wellness Segmentation")

wellness_df = filtered_df.copy()

wellness_df["Wellness Category"] = pd.cut(
    wellness_df["work_life_balance_score"],
    bins=[0, 4, 7, 10],
    labels=["Low", "Moderate", "High"]
)

segment = (
    wellness_df.groupby("Wellness Category")
    .agg({
        "productivity_score": "mean",
        "burnout_risk_score": "mean"
    })
    .reset_index()
)

fig = px.bar(
    segment,
    x="Wellness Category",
    y=["productivity_score", "burnout_risk_score"],
    barmode="group",
    title="Wellness Category Comparison"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# HEALTH SCORE GAUGE
# =====================================================

st.subheader("🏆 Wellness Score")

wellness_score = round(
    (
        avg_sleep +
        avg_wlb +
        avg_productivity
    ) / 3 * 10,
    1
)

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=wellness_score,
        title={"text": "Employee Wellness Index"},
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

# =====================================================
# TOP HEALTHY SEGMENTS
# =====================================================

st.subheader("🏅 Top Healthy Employee Segments")

top_segments = (
    filtered_df.groupby(
        ["industry", "work_model"]
    )
    .agg({
        "productivity_score": "mean",
        "burnout_risk_score": "mean",
        "job_satisfaction_score": "mean"
    })
    .reset_index()
)

top_segments["Health Score"] = (
    top_segments["productivity_score"]
    +
    top_segments["job_satisfaction_score"]
    -
    top_segments["burnout_risk_score"]
)

top_segments = top_segments.sort_values(
    "Health Score",
    ascending=False
)

st.dataframe(
    top_segments.head(15),
    use_container_width=True
)

# =====================================================
# EXECUTIVE INSIGHTS
# =====================================================

st.subheader("🤖 Lifestyle Insights")

best_segment = (
    top_segments.iloc[0]["industry"]
)

best_model = (
    top_segments.iloc[0]["work_model"]
)

st.success(
    f"""
### Key Findings

• Average employee sleep duration is **{avg_sleep} hours/night**.

• Work-Life Balance score across the organization is **{avg_wlb}**.

• Employees with healthier sleep patterns tend to show higher productivity.

• Strong work-life balance is associated with lower burnout levels.

• Regular exercise contributes positively to satisfaction and performance.

• Highest-performing wellness segment:
  **{best_segment} - {best_model}**

• Investing in employee wellness programs can significantly improve retention, productivity, and mental wellbeing.
"""
)
