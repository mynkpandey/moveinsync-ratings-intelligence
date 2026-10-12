
import pandas as pd

df = pd.read_csv("data/cleaned_reviews.csv")

df["at"] = pd.to_datetime(df["at"], errors="coerce", utc=True)
df["score"] = pd.to_numeric(df["score"], errors="coerce")

df = df.dropna(subset=["at", "score"])
df["month"] = df["at"].dt.strftime("%Y-%m")

period = df[df["month"].isin(["2026-05", "2026-06", "2026-07"])].copy()

period["reviewCreatedVersion"] = (
    period["reviewCreatedVersion"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
    .replace("", "Unknown")
)

period["low_rated"] = period["score"].isin([1, 2])

summary = (
    period.groupby(["month", "reviewCreatedVersion"])
    .agg(
        reviews=("score", "size"),
        average_rating=("score", "mean"),
        low_rated_reviews=("low_rated", "sum"),
        low_rating_share=("low_rated", "mean"),
    )
    .reset_index()
)

summary["average_rating"] = summary["average_rating"].round(2)
summary["low_rating_share_pct"] = (
    summary["low_rating_share"] * 100
).round(2)

# Avoid over-interpreting versions with very few reviews
summary = summary[summary["reviews"] >= 5].copy()

summary = summary.sort_values(
    ["month", "reviews"], ascending=[True, False]
)

print("\nApp version comparison (versions with at least 5 reviews):")
print(
    summary[
        [
            "month",
            "reviewCreatedVersion",
            "reviews",
            "average_rating",
            "low_rated_reviews",
            "low_rating_share_pct",
        ]
    ].to_string(index=False)
)

summary.to_csv("data/app_version_comparison.csv", index=False)
print("\nSaved to data/app_version_comparison.csv")
