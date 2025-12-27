import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import PROCESSED_DIR

from src.preprocess import clean_awards, clean_gross, clean_top_hits, clean_albums_us, clean_albums_global
from src.analytics import generate_yearly_stats, generate_top_artists, generate_best_picture_list, generate_album_stats


def main() -> None:
    """Run preprocessing and analytics to produce processed datasets."""
    # 1. RUN PREPROCESSING

    df_awards = clean_awards()
    df_awards.to_csv(PROCESSED_DIR / "awards.csv", index=False)

    df_gross = clean_gross()
    df_gross.to_csv(PROCESSED_DIR / "highest_grossing.csv", index=False)

    df_hits = clean_top_hits()
    df_hits.to_csv(PROCESSED_DIR / "top_hits.csv", index=False)

    df_global = clean_albums_global("data/raw/albums_wiki.csv")
    df_global.to_csv("data/processed/albums_global.csv", index=False)

    df_us = clean_albums_us("data/raw/albums_billboard.csv")
    df_us.to_csv("data/processed/albums_us.csv", index=False)

    # 2. RUN ANALYTICS

    stats = generate_yearly_stats(df_gross, df_hits)
    stats.to_csv(PROCESSED_DIR / "analytics_yearly_stats.csv", index=False)

    top_artists = generate_top_artists(df_hits)
    top_artists.to_csv(PROCESSED_DIR / "analytics_top_artists.csv", index=False)

    best_pics = generate_best_picture_list(df_awards)
    best_pics.to_csv(PROCESSED_DIR / "analytics_best_picture.csv", index=False)

    top_us_alb, top_us_art, top_glob_art = generate_album_stats(df_us, df_global)

    top_us_alb.to_csv("data/processed/analytics_longest_reigning_albums.csv", index=False)
    top_us_art.to_csv("data/processed/analytics_top_billboard_artists.csv", index=False)
    top_glob_art.to_csv("data/processed/analytics_top_critics_artists.csv", index=False)

if __name__ == "__main__":
    main()
