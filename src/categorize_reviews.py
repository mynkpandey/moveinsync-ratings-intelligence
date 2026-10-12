
import pandas as pd
import re

df = pd.read_csv("data/low_rated_reviews.csv")

# Prepare review text
df["content"] = df["content"].fillna("").astype(str)
df["review_text"] = df["content"].str.lower()

# Candidate categories based on recurring themes in the reviews
categories = {
    "Login and registration": r"\b(login|log in|sign in|register|registration|otp|not registered|mobile number|phone number)\b",
    "Schedule and booking": r"\b(schedule|scheduled|roster|booking|booked|reschedule|pickup|pick up|drop|trip details)\b",
    "Cab tracking and GPS": r"\b(track|tracking|gps|location|map|cab location|live location|eta|distance)\b",
    "App reliability": r"\b(crash|crashes|crashing|freeze|freezes|hang|hanging|not working|doesn't work|does not work|not open|loading|internet connection)\b",
    "Employee profile data": r"\b(employee id|employee id|wrong address|incorrect address|profile|previous company|wrong company|incorrect details)\b",
    "Missing functionality": r"\b(no option|feature|option to edit|cannot edit|can't edit|not able to edit|should add|please add)\b",
    "Support and resolution": r"\b(customer support|support team|no response|no reply|not responding|helpdesk|help desk)\b",
}

# A review can belong to more than one category
for category, pattern in categories.items():
    df[category] = df["review_text"].apply(
        lambda text: bool(re.search(pattern, text))
    )

# Count matching reviews per category
summary = pd.DataFrame([
    {
        "category": category,
        "matching_reviews": int(df[category].sum()),
        "percentage_of_low_rated_reviews": round(
            df[category].mean() * 100, 2
        )
    }
    for category in categories
]).sort_values("matching_reviews", ascending=False)

summary.to_csv("data/issue_category_summary.csv", index=False)
df.to_csv("data/categorized_low_reviews.csv", index=False)

print("\nIssue categories (keyword-based preliminary results):")
print(summary.to_string(index=False))

print("\nSaved:")
print("- data/issue_category_summary.csv")
print("- data/categorized_low_reviews.csv")
print("\nNote: Categories may overlap; these are keyword matches,")
print("not yet manually validated or confirmed root causes.")
