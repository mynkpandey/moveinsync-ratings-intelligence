
import pandas as pd

df = pd.read_csv("data/categorized_low_reviews.csv")

df["at"] = pd.to_datetime(df["at"], errors="coerce", utc=True)
df["month"] = df["at"].dt.strftime("%Y-%m")

df = df[df["month"] == "2026-06"].copy()

df["reviewCreatedVersion"] = (
    df["reviewCreatedVersion"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
    .replace("", "Unknown")
)

categories = [
    "Login and registration",
    "Schedule and booking",
    "Cab tracking and GPS",
    "App reliability",
    "Support and resolution",
]

# Keep versions with at least 5 low-rated reviews
version_counts = df["reviewCreatedVersion"].value_counts()
eligible = version_counts[version_counts >= 5].index
df = df[df["reviewCreatedVersion"].isin(eligible)]

print("\nJune low-rated reviews by version and issue:")
print(
    df.groupby("reviewCreatedVersion")[categories]
    .sum()
    .sort_index()
    .to_string()
)

print("\nNumber of low-rated reviews per version:")
print(df["reviewCreatedVersion"].value_counts().to_string())

print("\nNote: these are counts within low-rated reviews only.")
print("They do not establish that a version caused the complaints.")
