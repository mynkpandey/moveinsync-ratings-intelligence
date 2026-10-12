
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "raw_reviews.csv"


def main():
    df = pd.read_csv(FILE)
    print(f"Total rows: {len(df):,}")

    # 1. Duplicate review IDs
    if "reviewId" in df.columns:
        ids = df["reviewId"].dropna().astype(str).str.strip()
        ids = ids[ids.ne("")]
        duplicate_ids = ids.duplicated(keep=False)

        print("\n1. DUPLICATE REVIEW IDs")
        print(f"Rows with repeated IDs: {duplicate_ids.sum():,}")
        print(f"Extra copies beyond first: {ids.duplicated().sum():,}")
    else:
        print("\nNo reviewId column found.")

    # 2. Completely identical rows
    exact_mask = df.duplicated(keep=False)
    print("\n2. EXACT DUPLICATE ROWS")
    print(f"Rows involved: {exact_mask.sum():,}")
    print(f"Extra copies beyond first: {df.duplicated().sum():,}")

    # 3. Repeated review text, ignoring case and whitespace
    text = (
        df["content"].fillna("").astype(str)
        .str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    )
    has_text = text.ne("")
    text_counts = text[has_text].value_counts()
    repeated_text = text_counts[text_counts > 1]

    print("\n3. REPEATED REVIEW TEXT")
    print(f"Distinct texts repeated: {len(repeated_text):,}")
    print(
        "Rows containing repeated text: "
        f"{text[has_text].isin(repeated_text.index).sum():,}"
    )
    print(
        "Extra occurrences beyond first: "
        f"{(repeated_text - 1).sum():,}"
    )

    print("\nExamples of repeated text:")
    for review, count in repeated_text.head(10).items():
        print(f"\nCount: {count} | Text: {review[:200]}")

    print("\nAudit complete. No files were modified.")


if __name__ == "__main__":
    main()
