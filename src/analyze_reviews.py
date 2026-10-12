
import pandas as pd

# Load cleaned reviews
df = pd.read_csv("data/cleaned_reviews.csv")

# Show the dataset structure
print("\nDataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

# Show the lowest-rated reviews
low_reviews = df[df["score"].isin([1, 2])]

print("\nNumber of 1–2 star reviews:", len(low_reviews))
print("\nSample low-rated reviews:\n")

for _, row in low_reviews.head(20).iterrows():
    print(f"Rating: {row['score']}")
    print(f"Review: {row['content']}")
    print("-" * 70)

# Save low-rated reviews for focused analysis
low_reviews.to_csv("data/low_rated_reviews.csv", index=False)

print("\nSaved low-rated reviews to data/low_rated_reviews.csv")
