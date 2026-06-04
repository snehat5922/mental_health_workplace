import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Productivity Insights",
    page_icon="📈",
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

st.title("📈 Productivity Insights Dashboard")
st.markdown(
    "Explore factors influencing employee productivity and performance."
)

st.divider()

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

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

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

avg_productivity = round(
    filtered_df["productivity_score"].mean(),
    2
)

avg_satisfaction = round(
    filtered_df["job_satisfaction_score"].mean(),
    2
)

avg_burnout = round(
    filtered_df["burnout_risk_score"].mean(),
    2
)

high_performers = len(
    filtered_df[
        filtered_df["productivity_score"] >= 8
    ]
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "⚡ Avg Productivity",
    avg_productivity
)

col2.metric(
    "😊 Avg Satisfaction",
    avg_satisfaction
)

col3.metric(
    "🔥 Avg Burnout",
    avg_burnout
)

col4.metric(
    "🏆 High Performers",
    f"{high_performers:,}"
)

st.divider()

# ---------------------------------------------------
# PRODUCTIVITY DISTRIBUTION
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig = px.histogram(
        filtered_df,
        x="productivity_score",
        nbins=20,
        title="Productivity Score Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    productivity_levels = pd.DataFrame({
        "Category": [
            "Low",
            "Medium",
            "High"
        ],
        "Employees": [
            len(filtered_df[
                filtered_df["productivity_score"] < 4
            ]),
            len(filtered_df[
                (filtered_df["productivity_score"] >= 4)
                &
                (filtered_df["productivity_score"] < 7)
            ]),
            len(filtered_df[
                filtered_df["productivity_score"] >= 7
            ])
        ]
    })

    fig = px.pie(
        productivity_levels,
        names="Category",
        values="Employees",
        hole=0.5,
        title="Productivity Categories"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# SATISFACTION VS PRODUCTIVITY
# ---------------------------------------------------

st.subheader("😊 Satisfaction vs Productivity")

fig = px.scatter(
    filtered_df,
    x="job_satisfaction_score",
    y="productivity_score",
    color="work_model",
    size="burnout_risk_score",
    hover_data=["industry"],
    title="Productivity Relationship with Satisfaction"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# BURNOUT IMPACT
# ---------------------------------------------------

st.subheader("🔥 Burnout Impact on Productivity")

fig = px.scatter(
    filtered_df,
    x="burnout_risk_score",
    y="productivity_score",
    color="industry",
    trendline="ols",
    title="Burnout vs Productivity"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# INDUSTRY ANALYSIS
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    industry_df = (
        filtered_df.groupby("industry")
        ["productivity_score"]
        .mean()
        .reset_index()
        .sort_values(
            "productivity_score",
            ascending=False
        )
    )

    fig = px.bar(
        industry_df,
        x="industry",
        y="productivity_score",
        color="productivity_score",
        title="Productivity by Industry",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    model_df = (
        filtered_df.groupby("work_model")
        ["productivity_score"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        model_df,
        x="work_model",
        y="productivity_score",
        color="work_model",
        title="Productivity by Work Model"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# SLEEP ANALYSIS
# ---------------------------------------------------

st.subheader("😴 Sleep Impact")

fig = px.scatter(
    filtered_df,
    x="sleep_hours_per_night",
    y="productivity_score",
    color="work_model",
    trendline="ols",
    title="Sleep Hours vs Productivity"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# EXERCISE ANALYSIS
# ---------------------------------------------------

if "exercise_frequency" in filtered_df.columns:

    st.subheader("🏃 Exercise Impact")

    exercise_df = (
        filtered_df.groupby("exercise_frequency")
        ["productivity_score"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        exercise_df,
        x="exercise_frequency",
        y="productivity_score",
        color="productivity_score",
        title="Exercise Frequency vs Productivity"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# TOP PERFORMING SEGMENTS
# ---------------------------------------------------

st.subheader("🏆 Top Performing Employee Segments")

top_df = (
    filtered_df.groupby(
        ["industry", "work_model"]
    )["productivity_score"]
    .mean()
    .reset_index()
    .sort_values(
        "productivity_score",
        ascending=False
    )
)

st.dataframe(
    top_df.head(15),
    use_container_width=True
)

# ---------------------------------------------------
# PRODUCTIVITY INDEX
# ---------------------------------------------------

st.subheader("📊 Organizational Productivity Index")

prod_index = avg_productivity * 10

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=prod_index,
        title={"text": "Productivity Index"},
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

# ---------------------------------------------------
# AI INSIGHTS
# ---------------------------------------------------

st.subheader("🤖 Productivity Insights")

best_industry = industry_df.iloc[0]["industry"]

best_score = round(
    industry_df.iloc[0]["productivity_score"],
    2
)

best_model = (
    model_df.sort_values(
        "productivity_score",
        ascending=False
    )
    .iloc[0]["work_model"]
)

avg_sleep = round(
    filtered_df["sleep_hours_per_night"].mean(),
    2
)

st.success(
    f"""
### Key Findings

• Highest productivity is observed in **{best_industry}** industry.

• Employees in **{best_model}** work model achieve the best productivity.

• Average sleep duration is **{avg_sleep} hours/night**.

• Higher job satisfaction strongly correlates with increased productivity.

• Burnout negatively affects employee performance.

• Employees maintaining healthy sleep and exercise habits tend to perform better.

• Continuous wellbeing initiatives can improve organizational productivity.
"""
)
