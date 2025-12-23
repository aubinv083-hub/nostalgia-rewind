import sys
import os

# Add the project root to the python path so we can import local modules.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import PROCESSED_DIR

from src.preprocess import clean_awards, clean_gross, clean_top_hits
from src.analytics import generate_yearly_stats, generate_top_artists, generate_best_picture_list


def main():
    # 1. RUN PREPROCESSING

    df_awards = clean_awards()
    df_awards.to_csv(PROCESSED_DIR / "awards.csv", index=False)

    df_gross = clean_gross()
    df_gross.to_csv(PROCESSED_DIR / "highest_grossing.csv", index=False)

    df_hits = clean_top_hits()
    df_hits.to_csv(PROCESSED_DIR / "top_hits.csv", index=False)

    # 2. RUN ANALYTICS

    stats = generate_yearly_stats(df_gross, df_hits)
    stats.to_csv(PROCESSED_DIR / "analytics_yearly_stats.csv", index=False)

    top_artists = generate_top_artists(df_hits)
    top_artists.to_csv(PROCESSED_DIR / "analytics_top_artists.csv", index=False)

    best_pics = generate_best_picture_list(df_awards)
    best_pics.to_csv(PROCESSED_DIR / "analytics_best_picture.csv", index=False)

if __name__ == "__main__":
    main()
