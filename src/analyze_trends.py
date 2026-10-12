
import pandas as pd

df = pd.read_csv("data/categorized_low_reviews.csv")

df["at"] = pd.to_datetime(df["at"], errors="coerce", utc=True)
df = df.dropna(subset=["at"])

# Restrict to the latest 24 months available in the dataset
latest_date = df["at"].max()
cutoff = latest_date - pd.DateOffset(months=24)

recent = df[df["at"] >= cutoff].copy()

print("Latest review date:", latest_date)
print("Recent-period start:", cutoff)
print("Recent low-rated reviews:", len(recent))

# Count recent complaints by category
categories = [
    "Cab tracking and GPS",
    "Schedule and booking",
    "App reliability",
    "Login and registration",
    "Missing functionality",
    "Support and resolution",
    "Employee profile data",
]

results = []

for category in categories:
    results.append({
        "category": category,
        "matching_reviews": int(recent[category].sum()),
        "percentage_of_recent_low_reviews": round(
            recent[category].mean() * 100, 2
        ) if len(recent) else 0
    })

summary = pd.DataFrame(results).sort_values(
    "matching_reviews", ascending=False
)

print("\nRecent complaint patterns:")
print(summary.to_string(index=False))

summary.to_csv("data/recent_issue_summary.csv", index=False)
recent.to_csv("data/recent_low_rated_reviews.csv", index=False)

print("\nSaved recent-period analysis files.")
