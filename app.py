
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="MoveInSync Ratings Intelligence",
    page_icon="🚕",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    required_files = {
        "reviews": DATA_DIR / "cleaned_reviews.csv",
        "monthly": DATA_DIR / "monthly_rating_trends.csv",
        "issues": DATA_DIR / "issue_category_summary.csv",
        "recent_issues": DATA_DIR / "recent_issue_summary.csv",
        "versions": DATA_DIR / "app_version_comparison.csv",
    }

    missing_files = [
        str(path)
        for path in required_files.values()
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "The following data files are missing:\n"
            + "\n".join(missing_files)
        )

    return {
        name: pd.read_csv(path)
        for name, path in required_files.items()
    }


try:
    data = load_data()
except Exception as e:
    st.error(f"Unable to load dashboard data: {e}")
    st.info(
        "Check that the required CSV files exist inside "
        "the project's data folder."
    )
    st.stop()

reviews = data["reviews"].copy()
monthly = data["monthly"].copy()
issues = data["issues"].copy()
recent_issues = data["recent_issues"].copy()
versions = data["versions"].copy()

# --------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------
if "score" not in reviews.columns:
    st.error("The reviews file does not contain a 'score' column.")
    st.stop()

if "at" not in reviews.columns:
    st.error("The reviews file does not contain an 'at' column.")
    st.stop()

reviews["score"] = pd.to_numeric(
    reviews["score"], errors="coerce"
)

reviews["at"] = pd.to_datetime(
    reviews["at"], errors="coerce", utc=True
)

reviews = reviews.dropna(subset=["score", "at"])
reviews = reviews[reviews["score"].between(1, 5)].copy()
reviews["score"] = reviews["score"].astype(int)

# Ensure review text is usable for searching and display
if "content" not in reviews.columns:
    reviews["content"] = ""

reviews["content"] = reviews["content"].fillna("").astype(str)

# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------
st.title("🚕 MoveInSync Ratings Intelligence")

st.caption(
    "Google Play Store review analysis | "
    "Understanding complaints and prioritizing product improvements"
)

st.divider()

# --------------------------------------------------
# KEY PERFORMANCE INDICATORS
# --------------------------------------------------
total_reviews = len(reviews)

if total_reviews > 0:
    average_rating = reviews["score"].mean()
    low_rating_share = (
        reviews["score"].isin([1, 2]).mean() * 100
    )
    five_star_share = (
        (reviews["score"] == 5).mean() * 100
    )
else:
    average_rating = 0
    low_rating_share = 0
    five_star_share = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Reviews analyzed",
    f"{total_reviews:,}",
)

col2.metric(
    "Average rating",
    f"{average_rating:.2f} / 5",
)

col3.metric(
    "1–2 star reviews",
    f"{low_rating_share:.2f}%",
)

col4.metric(
    "5-star reviews",
    f"{five_star_share:.2f}%",
)

st.divider()

# --------------------------------------------------
# RATING DISTRIBUTION
# --------------------------------------------------
st.subheader("⭐ Rating Distribution")

rating_counts = (
    reviews["score"]
    .value_counts()
    .reindex([1, 2, 3, 4, 5], fill_value=0)
    .rename_axis("Rating")
    .reset_index(name="Number of reviews")
)

rating_counts["Rating label"] = (
    rating_counts["Rating"].astype(str) + " star"
)

fig_distribution = px.bar(
    rating_counts,
    x="Rating label",
    y="Number of reviews",
    text="Number of reviews",
    title="Number of reviews for each star rating",
    labels={
        "Rating label": "Star rating",
        "Number of reviews": "Number of reviews",
    },
)

fig_distribution.update_layout(
    xaxis_title="Star rating",
    yaxis_title="Number of reviews",
)

st.plotly_chart(
    fig_distribution,
    use_container_width=True,
)

st.divider()

# --------------------------------------------------
# MONTHLY RATING TRENDS
# --------------------------------------------------
st.subheader("📈 Monthly Rating Trends")

if "month" in monthly.columns:
    monthly["month"] = monthly["month"].astype(str)

    if "average_rating" in monthly.columns:
        monthly["average_rating"] = pd.to_numeric(
            monthly["average_rating"], errors="coerce"
        )

        monthly_chart_data = monthly.dropna(
            subset=["average_rating"]
        )

        fig_monthly = px.line(
            monthly_chart_data,
            x="month",
            y="average_rating",
            markers=True,
            title="Average monthly star rating",
            labels={
                "month": "Month",
                "average_rating": "Average rating",
            },
        )

        fig_monthly.update_yaxes(range=[1, 5])

        st.plotly_chart(
            fig_monthly,
            use_container_width=True,
        )

    if "low_rating_share_pct" in monthly.columns:
        fig_low_share = px.line(
            monthly,
            x="month",
            y="low_rating_share_pct",
            markers=True,
            title="Monthly share of 1–2 star reviews",
            labels={
                "month": "Month",
                "low_rating_share_pct": "Low-rating share (%)",
            },
        )

        st.plotly_chart(
            fig_low_share,
            use_container_width=True,
        )

    elif "low_rating_share" in monthly.columns:
        fig_low_share = px.line(
            monthly,
            x="month",
            y="low_rating_share",
            markers=True,
            title="Monthly share of 1–2 star reviews",
            labels={
                "month": "Month",
                "low_rating_share": "Low-rating share (%)",
            },
        )

        st.plotly_chart(
            fig_low_share,
            use_container_width=True,
        )

    st.dataframe(
        monthly,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning(
        "The monthly trend file does not contain a 'month' column."
    )

st.divider()

# --------------------------------------------------
# HISTORICAL COMPLAINT CATEGORIES
# --------------------------------------------------
st.subheader("🔎 Complaint Categories")

if not issues.empty:
    category_col = (
        "category"
        if "category" in issues.columns
        else None
    )

    count_col = (
        "matching_reviews"
        if "matching_reviews" in issues.columns
        else None
    )

    if category_col and count_col:
        issues[count_col] = pd.to_numeric(
            issues[count_col], errors="coerce"
        ).fillna(0)

        fig_issues = px.bar(
            issues.sort_values(count_col, ascending=True),
            x=count_col,
            y=category_col,
            orientation="h",
            text=count_col,
            title="Keyword matches among low-rated reviews",
            labels={
                count_col: "Matching reviews",
                category_col: "Complaint category",
            },
        )

        st.plotly_chart(
            fig_issues,
            use_container_width=True,
        )

        st.dataframe(
            issues,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.dataframe(
            issues,
            use_container_width=True,
            hide_index=True,
        )
else:
    st.info("No complaint category data is available.")

st.divider()

# --------------------------------------------------
# RECENT COMPLAINT PATTERNS
# --------------------------------------------------
st.subheader("🕒 Recent Complaint Patterns")

st.caption(
    "These categories show keyword matches in recent low-rated "
    "reviews. A review may match more than one category."
)

st.dataframe(
    recent_issues,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# --------------------------------------------------
# APP VERSION COMPARISON
# --------------------------------------------------
st.subheader("📱 App-Version Comparison")

st.caption(
    "Version-level differences are investigation leads, not proof "
    "that a release caused a rating change."
)

st.dataframe(
    versions,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# --------------------------------------------------
# INTERACTIVE REVIEW EXPLORER
# --------------------------------------------------
st.subheader("💬 Explore Individual Reviews")

st.write(
    "Choose one exact star rating or a combined range to inspect "
    "the corresponding reviews."
)

rating_filter = st.selectbox(
    "Filter by star rating",
    options=[
        "All ratings",
        "1 star",
        "2 stars",
        "3 stars",
        "4 stars",
        "5 stars",
        "1–2 stars",
        "2–3 stars",
        "3–4 stars",
        "4–5 stars",
        "1–3 stars",
        "3–5 stars",
    ],
    index=0,
)

# Optional date filter
use_date_filter = st.checkbox(
    "Filter reviews by date",
    value=False,
)

if use_date_filter:
    min_date = reviews["at"].min().date()
    max_date = reviews["at"].max().date()

    date_range = st.date_input(
        "Select review date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
else:
    date_range = None

# Optional app-version filter
if "reviewCreatedVersion" in reviews.columns:
    versions_available = sorted(
        reviews["reviewCreatedVersion"]
        .fillna("Unknown")
        .astype(str)
        .unique()
        .tolist()
    )

    selected_versions = st.multiselect(
        "Filter by app version (optional)",
        options=versions_available,
        default=[],
        help="Leave empty to include all app versions.",
    )
else:
    selected_versions = []

# Text search
search_text = st.text_input(
    "Search review text",
    placeholder="For example: GPS, OTP, login, cab, booking...",
)

# Apply rating selection
if rating_filter == "All ratings":
    filtered = reviews.copy()

elif rating_filter == "1–2 stars":
    filtered = reviews[reviews["score"].isin([1, 2])].copy()

elif rating_filter == "2–3 stars":
    filtered = reviews[reviews["score"].isin([2, 3])].copy()

elif rating_filter == "3–4 stars":
    filtered = reviews[reviews["score"].isin([3, 4])].copy()

elif rating_filter == "4–5 stars":
    filtered = reviews[reviews["score"].isin([4, 5])].copy()

elif rating_filter == "1–3 stars":
    filtered = reviews[reviews["score"].between(1, 3)].copy()

elif rating_filter == "3–5 stars":
    filtered = reviews[reviews["score"].between(3, 5)].copy()

else:
    selected_rating = int(rating_filter.split()[0])
    filtered = reviews[
        reviews["score"] == selected_rating
    ].copy()

# Apply date filter
if use_date_filter and date_range:
    if len(date_range) == 2:
        start_date, end_date = date_range

        filtered = filtered[
            (filtered["at"].dt.date >= start_date)
            & (filtered["at"].dt.date <= end_date)
        ].copy()
    else:
        st.info("Select both a start date and an end date.")

# Apply app-version filter
if selected_versions and "reviewCreatedVersion" in filtered.columns:
    filtered_version = (
        filtered["reviewCreatedVersion"]
        .fillna("Unknown")
        .astype(str)
    )

    filtered = filtered[
        filtered_version.isin(selected_versions)
    ].copy()

# Apply text search
if search_text.strip():
    filtered = filtered[
        filtered["content"].str.contains(
            search_text.strip(),
            case=False,
            regex=False,
            na=False,
        )
    ].copy()

# Review explorer metrics
st.markdown("#### Filter Results")

result_col1, result_col2 = st.columns(2)

result_col1.metric(
    "Matching reviews",
    f"{len(filtered):,}",
)

if not filtered.empty:
    result_col2.metric(
        "Average rating in selection",
        f"{filtered['score'].mean():.2f} / 5",
    )
else:
    result_col2.metric(
        "Average rating in selection",
        "N/A",
    )

# Display review records
display_columns = [
    column
    for column in [
        "at",
        "score",
        "content",
        "reviewCreatedVersion",
        "thumbsUpCount",
        "replyContent",
    ]
    if column in filtered.columns
]

if filtered.empty:
    st.warning(
        "No reviews match the selected filters. "
        "Try a different rating, date range, app version, or search term."
    )
else:
    display_reviews = filtered[display_columns].copy()

    display_reviews = display_reviews.sort_values(
        "at",
        ascending=False,
    )

    st.dataframe(
        display_reviews,
        use_container_width=True,
        hide_index=True,
    )

    # Download filtered results
    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download filtered reviews as CSV",
        data=csv_data,
        file_name="moveinsync_filtered_reviews.csv",
        mime="text/csv",
    )

st.divider()

# --------------------------------------------------
# PRIORITIZED ENGINEERING ACTION PLAN
# --------------------------------------------------
st.subheader("🛠️ Recommended Engineering Priorities")

st.markdown(
    """
    **Priority 0 — Scheduling and trip fulfillment**
    - Investigate failed bookings, incorrect pickup times, and unfulfilled trips.
    - Track booking success rate, trip fulfillment rate, and on-time pickups.

    **Priority 0 — GPS tracking and ETA accuracy**
    - Check GPS freshness, route accuracy, and ETA prediction errors.
    - Track location update latency and ETA error.

    **Priority 1 — Authentication reliability**
    - Investigate OTP delivery failures and login or registration errors.
    - Track OTP success rate, authentication failure rate, and login completion.

    **Priority 1 — Safety and support**
    - Escalate safety-related complaints and improve complaint resolution.
    - Track first-response time, resolution time, and unresolved incidents.
    """
)

st.caption(
    "Methodology: publicly available Play Store reviews were cleaned, "
    "summarized by rating and month, and grouped using keyword-based "
    "complaint categories. Category counts may overlap and do not "
    "establish causality. Validate findings against backend logs, "
    "crash reports, release history, and transport operations data."
)
