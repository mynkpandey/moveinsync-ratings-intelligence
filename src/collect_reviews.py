
import pandas as pd
from google_play_scraper import reviews, Sort
from pathlib import Path
import time

# MoveInSync employee transport app
APP_ID = "com.moveinsync.ets"
LANGUAGE = "en"
COUNTRY = "in"

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "raw_reviews.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def collect_reviews():
    all_reviews = []
    continuation_token = None
    target_reviews = 25000
    batch_size = 200

    print("Starting MoveInSync review collection...")

    while len(all_reviews) < target_reviews:
        try:
            batch, continuation_token = reviews(
                APP_ID,
                lang=LANGUAGE,
                country=COUNTRY,
                sort=Sort.NEWEST,
                count=batch_size,
                continuation_token=continuation_token,
                filter_score_with=None,
            )

            if not batch:
                print("No more reviews returned by Google Play.")
                break

            all_reviews.extend(batch)
            print(f"Collected {len(all_reviews)} reviews so far")

            if continuation_token is None:
                print("Reached the end of accessible reviews.")
                break

            time.sleep(0.3)

        except Exception as exc:
            print(f"Collection stopped: {exc}")
            break

    if not all_reviews:
        print("No reviews collected. Check the app ID or connection.")
        return

    df = pd.DataFrame(all_reviews)

    # Save the raw data before performing any cleaning
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\nCollection finished.")
    print(f"Reviews collected: {len(df)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nRating distribution:")
    print(df["score"].value_counts().sort_index())

    if "at" in df.columns:
        print("\nReview date range:")
        print("Oldest:", df["at"].min())
        print("Newest:", df["at"].max())


if __name__ == "__main__":
    collect_reviews()
