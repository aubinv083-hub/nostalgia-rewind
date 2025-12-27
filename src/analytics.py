from typing import Tuple
import pandas as pd

def generate_yearly_stats(df_gross: pd.DataFrame, df_music: pd.DataFrame) -> pd.DataFrame:
    """
    Merge box office totals and unique song counts by year.

    Args:
        df_gross: Cleaned box office data.
        df_music: Cleaned top hits data.

    Returns:
        DataFrame with year, total_box_office, unique_songs_charted.
    """
    yearly_gross = df_gross.groupby("year")["gross"].sum().reset_index(name="total_box_office")
    yearly_songs = df_music.groupby("year")["title"].nunique().reset_index(name="unique_songs_charted")

    stats = pd.merge(yearly_gross, yearly_songs, on="year", how="outer")
    return stats


def generate_top_artists(df_music: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate top 20 artists of all time.

    Args:
        df_music: Cleaned top hits data.

    Returns:
        DataFrame with main_artist, display_artist, total_hits (top 20).
    """
    display_map = (
        df_music.groupby("main_artist")["display_artist"]
        .agg(lambda x: x.mode().iat[0] if not x.mode().empty else x.iloc[0])
    )

    top = (
        df_music.groupby("main_artist")
        .agg(total_hits=("title", "count"))
        .sort_values("total_hits", ascending=False)
        .head(20)
        .reset_index()
    )
    top["display_artist"] = top["main_artist"].map(display_map)
    return top


def generate_best_picture_list(df_awards: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Best Picture winners for the timeline.

    Args:
        df_awards: Cleaned awards data.

    Returns:
        DataFrame with year and best_picture.
    """
    mask = df_awards['category'].isin(['best film', 'best picture', 'best motion picture'])
    best_pics = df_awards[mask][['year', 'winner']].rename(columns={'winner': 'best_picture'})
    return best_pics


def generate_album_stats(df_us: pd.DataFrame, df_global: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate summary stats for albums.

    Args:
        df_us: Billboard albums data (cleaned).
        df_global: Wiki global albums data (cleaned).

    Returns:
        Tuple of (top_us_albums, top_us_artists, top_global_artists).
    """

    # Who spent the most weeks at #1 across all years?
    top_us_albums = (
        df_us.sort_values("weeks_at_one", ascending=False)
        .head(20)
        [["year", "album", "artist", "weeks_at_one"]]
    )

    # Who are the leaders of Billboard? (Total weeks at #1 across all albums)
    top_us_artists = (
        df_us.groupby("artist")["weeks_at_one"].sum()
        .reset_index()
        .sort_values("weeks_at_one", ascending=False)
        .head(10)
        .rename(columns={"weeks_at_one": "total_weeks_at_one"})
    )

    # Who appears most often in the "Best of Year" lists?
    top_global_artists = (
        df_global["artist"].value_counts()
        .reset_index(name="count")
        .rename(columns={"index": "artist"})
        .head(10)
    )
    return top_us_albums, top_us_artists, top_global_artists
