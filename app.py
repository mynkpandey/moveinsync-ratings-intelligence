
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="MoveInSync Ratings Intelligence",
    page_icon="📊",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# =========================================================
# LOAD SUMMARY DATA
# =========================================================
@st.cache_data
def load_data():
    required_files = {
        "monthly": DATA_DIR / "monthly_rating_trends.csv",
        "issues": DATA_DIR / "issue_category_summary.csv",
        "recent_issues": DATA_DIR / "recent_issue_summary.csv",
        "versions": DATA_DIR / "app_version_comparison.csv",
    }

    missing_files = [
        str(path)
        for path in required_files.values()
        if not path.is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Required summary files are missing:\n"
            + "\n".join(missing_files)
        )

    return {
        name: pd.read_csv(path)
        for name, path in required_files.items()
    }


try:
    data = load_data()
except Exception as exc:
    st.error(f"Unable to load dashboard data: {exc}")
    st.info(
        "Check that the four summary CSV files exist "
        "inside the repository's data folder."
    )
    st.stop()


monthly = data["monthly"].copy()
issues = data["issues"].copy()
recent_issues = data["recent_issues"].copy()
versions = data["versions"].copy()


# =========================================================
# VALIDATE AND PREPARE DATA
# =========================================================
def validate_columns(frame, required_columns, filename):
    missing = [
        column
        for column in required_columns
        if column not in frame.columns
    ]

    if missing:
        raise ValueError(
            f"{filename} is missing columns: {', '.join(missing)}"
        )


try:
    validate_columns(
        monthly,
        [
            "month",
            "total_reviews",
            "average_rating",
            "low_rated_reviews",
            "low_rating_share_pct",
        ],
        "monthly_rating_trends.csv",
    )

    validate_columns(
        issues,
        [
            "category",
            "matching_reviews",
            "percentage_of_low_rated_reviews",
        ],
        "issue_category_summary.csv",
    )

    validate_columns(
        recent_issues,
        [
            "category",
            "matching_reviews",
            "percentage_of_recent_low_reviews",
        ],
        "recent_issue_summary.csv",
    )

    validate_columns(
        versions,
        [
            "month",
            "reviewCreatedVersion",
            "reviews",
            "average_rating",
            "low_rated_reviews",
            "low_rating_share_pct",
        ],
        "app_version_comparison.csv",
    )

except ValueError as exc:
    st.error(f"Data validation failed: {exc}")
    st.stop()


# Convert numeric columns safely.
monthly_numeric = [
    "total_reviews",
    "average_rating",
    "low_rated_reviews",
    "low_rating_share_pct",
]

for column in monthly_numeric:
    monthly[column] = pd.to_numeric(
        monthly[column], errors="coerce"
    )

version_numeric = [
    "reviews",
    "average_rating",
    "low_rated_reviews",
    "low_rating_share_pct",
]

for column in version_numeric:
    versions[column] = pd.to_numeric(
        versions[column], errors="coerce"
    )

issues["matching_reviews"] = pd.to_numeric(
    issues["matching_reviews"], errors="coerce"
)

issues["percentage_of_low_rated_reviews"] = pd.to_numeric(
    issues["percentage_of_low_rated_reviews"],
    errors="coerce",
)

recent_issues["matching_reviews"] = pd.to_numeric(
    recent_issues["matching_reviews"], errors="coerce"
)

recent_issues["percentage_of_recent_low_reviews"] = pd.to_numeric(
    recent_issues["percentage_of_recent_low_reviews"],
    errors="coerce",
)

monthly["month_date"] = pd.to_datetime(
    monthly["month"].astype(str),
    format="%Y-%m",
    errors="coerce",
)

monthly = monthly.dropna(
    subset=["month_date", "total_reviews", "average_rating"]
).sort_values("month_date")

versions["month"] = versions["month"].astype(str)
versions["reviewCreatedVersion"] = (
    versions["reviewCreatedVersion"]
    .fillna("Unknown")
    .astype(str)
)

issues = issues.dropna(subset=["category"])
recent_issues = recent_issues.dropna(subset=["category"])

if monthly.empty:
    st.error("Monthly rating data contains no usable records.")
    st.stop()


# =========================================================
# DASHBOARD HEADER
# =========================================================
st.title("MoveInSync Ratings Intelligence")

st.markdown(
    """
    **Google Play Store review analytics**

    An interactive dashboard to investigate rating trends,
    identify recurring complaints, and prioritize product
    and engineering improvements.
    """
)

st.caption(
    "Source: locally analyzed Google Play Store review data. "
    "This deployed dashboard uses aggregate summary CSVs."
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("Dashboard Filters")

available_months = monthly["month"].dropna().astype(str).tolist()

if available_months:
    selected_months = st.sidebar.select_slider(
        "Monthly trend range",
        options=available_months,
        value=(available_months[0], available_months[-1]),
    )

    filtered_monthly = monthly[
        monthly["month"].between(
            selected_months[0],
            selected_months[1],
        )
    ].copy()
else:
    filtered_monthly = monthly.copy()

available_version_months = sorted(
    versions["month"].dropna().unique().tolist()
)

if available_version_months:
    selected_version_month = st.sidebar.selectbox(
        "Month for app-version comparison",
        options=available_version_months,
        index=len(available_version_months) - 1,
    )

    filtered_versions = versions[
        versions["month"] == selected_version_month
    ].copy()
else:
    selected_version_month = None
    filtered_versions = versions.copy()


# =========================================================
# KPI METRICS
# =========================================================
st.subheader("Review Overview")

total_reviews = int(monthly["total_reviews"].sum())

valid_weighted = monthly.dropna(
    subset=["average_rating", "total_reviews"]
)

if (
    not valid_weighted.empty
    and valid_weighted["total_reviews"].sum() > 0
):
    overall_average = (
        (
            valid_weighted["average_rating"]
            * valid_weighted["total_reviews"]
        ).sum()
        / valid_weighted["total_reviews"].sum()
    )
else:
    overall_average = float("nan")

total_low_rated = int(
    monthly["low_rated_reviews"].fillna(0).sum()
)

low_rating_share = (
    total_low_rated / total_reviews * 100
    if total_reviews > 0
    else 0
)

latest_month = monthly.iloc[-1]
latest_month_name = str(latest_month["month"])

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Reviews in monthly dataset",
    f"{total_reviews:,}",
)

col2.metric(
    "Weighted average rating",
    f"{overall_average:.2f}/5"
    if pd.notna(overall_average)
    else "N/A",
)

col3.metric(
    "1–2 star reviews",
    f"{total_low_rated:,}",
)

col4.metric(
    "Low-rating share",
    f"{low_rating_share:.2f}%",
)

st.caption(
    "Overview metrics are calculated by summing monthly counts "
    "and weighting monthly average ratings by review volume. "
    "The displayed review count is based on the monthly summary."
)


# =========================================================
# MONTHLY RATING TRENDS
# =========================================================
st.divider()
st.subheader("Monthly Rating Trends")

if filtered_monthly.empty:
    st.warning("No monthly data is available for this selection.")
else:
    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:
        rating_fig = px.line(
            filtered_monthly,
            x="month_date",
            y="average_rating",
            markers=True,
            title="Average Rating Over Time",
            labels={
                "month_date": "Month",
                "average_rating": "Average rating",
            },
        )

        rating_fig.update_yaxes(
            range=[0, 5],
            title="Average rating (out of 5)",
        )

        rating_fig.update_layout(
            hovermode="x unified",
        )

        st.plotly_chart(
            rating_fig,
            use_container_width=True,
        )

    with trend_col2:
        share_fig = px.line(
            filtered_monthly,
            x="month_date",
            y="low_rating_share_pct",
            markers=True,
            title="Percentage of 1–2 Star Reviews",
            labels={
                "month_date": "Month",
                "low_rating_share_pct": "Low-rating share (%)",
            },
        )

        share_fig.update_layout(
            hovermode="x unified",
        )

        st.plotly_chart(
            share_fig,
            use_container_width=True,
        )

    st.markdown("#### Monthly Review Volume")

    volume_fig = px.bar(
        filtered_monthly,
        x="month_date",
        y="total_reviews",
        title="Number of Reviews per Month",
        labels={
            "month_date": "Month",
            "total_reviews": "Review count",
        },
    )

    st.plotly_chart(
        volume_fig,
        use_container_width=True,
    )

    with st.expander("View monthly trend data"):
        display_monthly = filtered_monthly[
            [
                "month",
                "total_reviews",
                "average_rating",
                "low_rated_reviews",
                "low_rating_share_pct",
            ]
        ].copy()

        st.dataframe(
            display_monthly,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# HISTORICAL ISSUE CATEGORIES
# =========================================================
st.divider()
st.subheader("Historical Complaint Categories")

st.write(
    "These categories summarize keyword matches among historical "
    "low-rated reviews. Categories can overlap, so counts should "
    "not be added together as if each review belonged to only one category."
)

historical_issues = issues.sort_values(
    "matching_reviews",
    ascending=True,
)

issue_fig = px.bar(
    historical_issues,
    x="matching_reviews",
    y="category",
    orientation="h",
    text="matching_reviews",
    title="Low-Rated Reviews Matching Each Issue Category",
    labels={
        "matching_reviews": "Matching reviews",
        "category": "Issue category",
    },
)

issue_fig.update_layout(
    yaxis_title="",
    xaxis_title="Matching low-rated reviews",
)

st.plotly_chart(
    issue_fig,
    use_container_width=True,
)

with st.expander("View historical issue summary"):
    st.dataframe(
        issues.sort_values(
            "matching_reviews",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# RECENT ISSUE CATEGORIES
# =========================================================
st.divider()
st.subheader("Recent Complaint Categories")

st.write(
    "Issue categories identified in the recent review window "
    "used by the analysis scripts."
)

recent_sorted = recent_issues.sort_values(
    "matching_reviews",
    ascending=True,
)

recent_fig = px.bar(
    recent_sorted,
    x="matching_reviews",
    y="category",
    orientation="h",
    text="matching_reviews",
    title="Recent Low-Rated Reviews by Issue Category",
    labels={
        "matching_reviews": "Matching reviews",
        "category": "Issue category",
    },
)

recent_fig.update_layout(
    yaxis_title="",
    xaxis_title="Matching recent low-rated reviews",
)

st.plotly_chart(
    recent_fig,
    use_container_width=True,
)

with st.expander("View recent issue summary"):
    st.dataframe(
        recent_issues.sort_values(
            "matching_reviews",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# APP VERSION COMPARISON
# =========================================================
st.divider()
st.subheader("App Version Analysis")

st.write(
    "Compare average ratings and low-rating shares for app "
    "versions in the selected month. Small review counts can "
    "produce volatile percentages."
)

if filtered_versions.empty:
    st.info(
        "No app-version comparison data is available "
        "for the selected month."
    )
else:
    version_col1, version_col2 = st.columns(2)

    with version_col1:
        version_rating_fig = px.bar(
            filtered_versions.sort_values("average_rating"),
            x="average_rating",
            y="reviewCreatedVersion",
            orientation="h",
            text="average_rating",
            title=f"Average Rating by Version — {selected_version_month}",
            labels={
                "average_rating": "Average rating",
                "reviewCreatedVersion": "App version",
            },
        )

        version_rating_fig.update_xaxes(
            range=[0, 5],
        )

        st.plotly_chart(
            version_rating_fig,
            use_container_width=True,
        )

    with version_col2:
        version_share_fig = px.bar(
            filtered_versions.sort_values("low_rating_share_pct"),
            x="low_rating_share_pct",
            y="reviewCreatedVersion",
            orientation="h",
            text="low_rating_share_pct",
            title=f"Low-Rating Share by Version — {selected_version_month}",
            labels={
                "low_rating_share_pct": "1–2 star reviews (%)",
                "reviewCreatedVersion": "App version",
            },
        )

        st.plotly_chart(
            version_share_fig,
            use_container_width=True,
        )

    with st.expander("View app-version comparison data"):
        st.dataframe(
            filtered_versions.sort_values(
                "low_rating_share_pct",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# ENGINEERING ACTION PLAN
# =========================================================
st.divider()
st.subheader("Recommended Engineering Action Plan")

action_plan = pd.DataFrame(
    [
        {
            "Priority": "P0",
            "Area": "Scheduling and booking",
            "Recommended action": (
                "Investigate failed bookings, pickup-time mismatches, "
                "and unfulfilled trips."
            ),
            "Success metric": (
                "Booking success rate; trip fulfillment rate; "
                "on-time pickup rate."
            ),
        },
        {
            "Priority": "P0",
            "Area": "Cab tracking and GPS",
            "Recommended action": (
                "Investigate stale GPS updates, inaccurate ETAs, "
                "and live-tracking failures."
            ),
            "Success metric": (
                "GPS freshness; ETA prediction error; "
                "tracking success rate."
            ),
        },
        {
            "Priority": "P1",
            "Area": "Login and OTP",
            "Recommended action": (
                "Investigate OTP delivery, authentication errors, "
                "and failed login attempts."
            ),
            "Success metric": (
                "Authentication completion rate; OTP failure rate."
            ),
        },
        {
            "Priority": "P1",
            "Area": "App reliability",
            "Recommended action": (
                "Correlate crashes, latency, and error reports "
                "with release versions."
            ),
            "Success metric": (
                "Crash-free sessions; API error rate; "
                "app response time."
            ),
        },
        {
            "Priority": "P1",
            "Area": "Safety and support",
            "Recommended action": (
                "Improve safety escalation and complaint resolution."
            ),
            "Success metric": (
                "First response time; resolution time; "
                "safety escalation completion."
            ),
        },
    ]
)

st.dataframe(
    action_plan,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# METHODOLOGY AND LIMITATIONS
# =========================================================
st.divider()
st.subheader("Methodology and Limitations")

with st.expander("How to interpret this dashboard"):
    st.markdown(
        """
        **Methodology**

        - Publicly accessible Google Play Store reviews were collected.
        - Review records were cleaned and validated.
        - Low-rated reviews were defined as 1–2 star reviews.
        - Complaint categories were assigned using keyword-based,
          multi-label classification.
        - Monthly rating trends and app-version comparisons were
          calculated from the analyzed review dataset.
        - Aggregate CSV files are used by this deployed dashboard.

        **Limitations**

        - Reviews are self-selected and may not represent all users.
        - Keyword-based complaint categories can overlap and may miss
          complaints expressed in unexpected language.
        - A category match is not proof of a technical root cause.
        - App-version differences are observational and do not prove
          that a particular release caused a rating change.
        - The monthly average shown in the overview is weighted by
          monthly review volume.
        - The latest month may be incomplete and should not be compared
          directly with complete months.
        - Production telemetry, release records, booking outcomes,
          GPS logs, and authentication logs are needed to validate
          engineering hypotheses.
        """
    )

st.caption(
    "MoveInSync Ratings Intelligence | Aggregate review analysis "
    "| Recommendations require validation with production telemetry."
)
