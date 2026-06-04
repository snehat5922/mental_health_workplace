import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Attrition Analysis",
    page_icon="🚪",
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

st.title("🚪 Employee Attrition Analysis")
st.markdown(
    "Analyze employee retention risk and identify factors influencing workforce turnover."
)

# =====================================================
# DETECT ATTRITION COLUMN
# =====================================================

attrition_candidates = [
    "intention_to_leave",
    "attrition_risk",
    "turnover_intention",
    "leave_intention"
]

attrition_col = None

for col in attrition_candidates:
    if col in df.columns:
        attrition_col = col
        break

if attrition_col is None:
    st.warning(
        "No attrition-related column found. Using burnout score as proxy."
    )
    attrition_col = "burnout_risk_score"

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Filters")

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

work_models = st.sidebar.multiselect(
    "Work Model",
    sorted(df["work_model"].unique()),
    default=sorted(df["work_model"].unique())
)

filtered_df = df[
    (df["country"].isin(countries))
    &
    (df["industry"].isin(industries))
    &
    (df["work_model"].isin(work_models))
]

# =====================================================
# KPI SECTION
# =====================================================

total_emp = len(filtered_df)

avg_attrition = round(
    filtered_df[attrition_col].mean(),
    2
)

high_risk = len(
    filtered_df[
        filtered_df[attrition_col] >= 7
    ]
)

risk_percent = round(
    (high_risk / total_emp) * 100,
    1
)

avg_burnout = round(
    filtered_df["burnout_risk_score"].mean(),
    2
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Employees",
    f"{total_emp:,}"
)

col2.metric(
    "Avg Attrition Risk",
    avg_attrition
)

col3.metric(
    "High Risk Employees",
    f"{high_risk:,}"
)

col4.metric(
    "High Risk %",
    f"{risk_percent}%"
)

st.divider()

# =====================================================
# ATTRITION DISTRIBUTION
# =====================================================

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

    risk_data = pd.DataFrame({
        "Category": ["Low", "Medium", "High"],
        "Count": [
            len(filtered_df[
                filtered_df[attrition_col] < 4
            ]),
            len(filtered_df[
                (filtered_df[attrition_col] >= 4)
                &
                (filtered_df[attrition_col] < 7)
            ]),
            len(filtered_df[
                filtered_df[attrition_col] >= 7
            ])
        ]
    })

    fig = px.pie(
        risk_data,
        names="Category",
        values="Count",
        hole=0.5,
        title="Attrition Risk Categories"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# BURNOUT VS ATTRITION
# =====================================================

st.subheader("🔥 Burnout vs Attrition")

fig = px.scatter(
    filtered_df,
    x="burnout_risk_score",
    y=attrition_col,
    color="work_model",
    hover_data=["industry"],
    trendline="ols"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# SATISFACTION VS ATTRITION
# =====================================================

st.subheader("😊 Satisfaction vs Attrition")

fig = px.scatter(
    filtered_df,
    x="job_satisfaction_score",
    y=attrition_col,
    color="industry",
    trendline="ols"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# INDUSTRY ANALYSIS
# =====================================================

col1, col2 = st.columns(2)

with col1:

    industry_df = (
        filtered_df
        .groupby("industry")[attrition_col]
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
        title="Attrition Risk by Industry",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    work_df = (
        filtered_df
        .groupby("work_model")[attrition_col]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        work_df,
        x="work_model",
        y=attrition_col,
        color="work_model",
        title="Attrition Risk by Work Model"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# COUNTRY ANALYSIS
# =====================================================

st.subheader("🌍 Country-wise Attrition Risk")

country_df = (
    filtered_df
    .groupby("country")[attrition_col]
    .mean()
    .reset_index()
)

fig = px.choropleth(
    country_df,
    locations="country",
    locationmode="country names",
    color=attrition_col,
    title="Global Attrition Risk"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# HIGH-RISK EMPLOYEES
# =====================================================

st.subheader("🚨 High-Risk Employees")

high_risk_df = filtered_df[
    filtered_df[attrition_col] >= 8
]

show_cols = [
    c for c in [
        "age",
        "gender",
        "country",
        "industry",
        "work_model",
        "job_satisfaction_score",
        "burnout_risk_score",
        attrition_col
    ]
    if c in high_risk_df.columns
]

st.dataframe(
    high_risk_df[show_cols].head(50),
    use_container_width=True
)

# =====================================================
# ATTRITION INDEX GAUGE
# =====================================================

st.subheader("📊 Attrition Risk Index")

attrition_index = avg_attrition * 10

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=attrition_index,
        title={"text": "Organization Attrition Index"},
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
# INSIGHTS
# =====================================================

st.subheader("🤖 Executive Insights")

highest_industry = industry_df.iloc[0]["industry"]
highest_risk = round(
    industry_df.iloc[0][attrition_col],
    2
)

lowest_model = (
    work_df
    .sort_values(attrition_col)
    .iloc[0]["work_model"]
)

st.success(
    f"""
### Key Findings

• Highest attrition risk observed in **{highest_industry}** industry.

• Average attrition score is **{avg_attrition}**.

• **{lowest_model}** work model demonstrates the best employee retention.

• Higher burnout scores are associated with greater turnover intention.

• Employees with lower job satisfaction are more likely to leave.

• Retention strategies should focus on high-risk employees and workload management.

• Strengthening mental health programs can improve long-term employee retention.
"""
)
