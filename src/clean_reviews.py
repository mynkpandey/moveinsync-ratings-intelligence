
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "raw_reviews.csv"
OUTPUT_FILE = ROOT / "data" / "cleaned_reviews.csv"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    original_count = len(df)

    print("========== RAW DATA ==========")
    print(f"Original rows: {original_count}")

    required = {"score", "content", "at"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    # Normalize text and validate fields
    df["content"] = df["content"].fillna("").astype(str).str.strip()
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["at"] = pd.to_datetime(df["at"], errors="coerce", utc=True)

    df = df.dropna(subset=["score", "at"])
    df = df[df["score"].between(1, 5)]
    df = df[df["score"] == df["score"].astype(int)]
    df = df[df["content"].ne("")]

    valid_count = len(df)

    # 1. Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    exact_duplicates = before - len(df)

    # 2. Remove repeated Google Play review IDs
    id_duplicates = 0
    if "reviewId" in df.columns:
        before = len(df)
        valid_ids = df["reviewId"].notna() & (
            df["reviewId"].astype(str).str.strip() != ""
        )
        identified = df[valid_ids].drop_duplicates(
            subset=["reviewId"], keep="last"
        )
        unidentified = df[~valid_ids]
        df = pd.concat([identified, unidentified], ignore_index=True)
        id_duplicates = before - len(df)

    # 3. Detect identical review text by normalized content.
    # Only remove repeated text when rating and date also match.
    # This is a conservative heuristic, not proof of duplication.
    df["normalized_text"] = (
        df["content"]
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    before = len(df)
    df = df.drop_duplicates(
        subset=["normalized_text", "score", "at"],
        keep="last"
    )
    matching_review_duplicates = before - len(df)

    # Remove helper column and sort by date
    df = df.drop(columns=["normalized_text"])
    df = df.sort_values("at").reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\n========== CLEANING SUMMARY ==========")
    print(f"Original rows: {original_count}")
    print(f"Rows after validation: {valid_count}")
    print(f"Exact duplicate rows removed: {exact_duplicates}")
    print(f"Duplicate review IDs removed: {id_duplicates}")
    print(
        "Matching text/rating/date duplicates removed: "
        f"{matching_review_duplicates}"
    )
    print(f"Final cleaned rows: {len(df)}")
    print(f"Total rows removed: {original_count - len(df)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\n========== RATING DISTRIBUTION ==========")
    print(df["score"].value_counts().sort_index())

    print(f"\nAverage rating: {df['score'].mean():.3f}")
    print(
        "1-2 star share: "
        f"{df['score'].isin([1, 2]).mean() * 100:.2f}%"
    )
    print(f"Oldest review: {df['at'].min()}")
    print(f"Newest review: {df['at'].max()}")


if __name__ == "__main__":
    main()
