
import pandas as pd

df = pd.read_csv("data/categorized_low_reviews.csv")

df["at"] = pd.to_datetime(df["at"], errors="coerce", utc=True)
df["score"] = pd.to_numeric(df["score"], errors="coerce")

# Compare low-rated reviews from May, June and July 2026
df["month"] = df["at"].dt.strftime("%Y-%m")
period = df[df["month"].isin(["2026-05", "2026-06", "2026-07"])].copy()

categories = [
    "Login and registration",
    "Schedule and booking",
    "Cab tracking and GPS",
    "App reliability",
    "Support and resolution",
    "Missing functionality",
    "Employee profile data",
]

print("\nLow-rated review counts by month:")
print(period.groupby("month").size().to_string())

print("\nComplaint-category counts by month:")
print(period.groupby("month")[categories].sum().T.to_string())

print("\nJune 2026 sample of low-rated reviews:")
june = period[period["month"] == "2026-06"]

for _, row in june.head(25).iterrows():
    print(f"\nRating: {row['score']}")
    print(f"App version: {row.get('reviewCreatedVersion', 'Unknown')}")
    print(f"Review: {row['content']}")
    print("-" * 60)

print("\nJune app-version distribution:")
print(june["reviewCreatedVersion"].fillna("Unknown").value_counts().head(15))
