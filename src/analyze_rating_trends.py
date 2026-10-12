
import pandas as pd

df = pd.read_csv("data/cleaned_reviews.csv")

df["at"] = pd.to_datetime(df["at"], errors="coerce", utc=True)
df["score"] = pd.to_numeric(df["score"], errors="coerce")

df = df.dropna(subset=["at", "score"])
df["month"] = df["at"].dt.to_period("M").astype(str)
df["is_low_rated"] = df["score"].isin([1, 2])

monthly = (
    df.groupby("month")
    .agg(
        total_reviews=("score", "size"),
        average_rating=("score", "mean"),
        low_rated_reviews=("is_low_rated", "sum"),
    )
    .reset_index()
)

monthly["low_rating_share_pct"] = (
    monthly["low_rated_reviews"] / monthly["total_reviews"] * 100
)

monthly["average_rating"] = monthly["average_rating"].round(3)
monthly["low_rating_share_pct"] = monthly["low_rating_share_pct"].round(2)

# Focus on the latest 24 months represented in the dataset
latest_month = pd.Period(df["at"].max(), freq="M")
start_month = latest_month - 23

recent_monthly = monthly[
    (monthly["month"] >= str(start_month))
    & (monthly["month"] <= str(latest_month))
].copy()

print("\nMonthly rating trends — latest 24 months:")
print(recent_monthly.to_string(index=False))

recent_monthly.to_csv("data/monthly_rating_trends.csv", index=False)

print("\nSaved results to data/monthly_rating_trends.csv")
