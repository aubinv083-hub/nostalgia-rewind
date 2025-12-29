from pathlib import Path
from typing import Optional
import pandas as pd

from config import RAW_DIR

def clean_awards(input_path: Optional[str | Path] = None) -> pd.DataFrame:
    """
    Clean the awards dataset.

    Args:
        input_path: Optional path to awards CSV; defaults to data/raw/awards.csv.

    Returns:
        DataFrame with category (lowercased), winner, and numeric year, sorted.
    """
    awards_path = Path(input_path) if input_path else (RAW_DIR / "awards.csv")
    df = pd.read_csv(awards_path)

    keep_col = ['category', 'year', 'winner']

    df = df[keep_col]

    df = df[~df["category"].str.contains("Category/", na=False, case=False)]
    df = df[df["winner"] != "—"]

    df = (
        df.assign(
            category=df["category"].str.strip().str.lower(),
            year=pd.to_numeric(df["year"], errors="coerce")
        )
        .sort_values(by=["category", "year"], ascending=[True, True])
        .reset_index(drop=True)
    )
    return df


def clean_gross(input_path: Optional[str | Path] = None) -> pd.DataFrame:
    """
    Clean the box office dataset.

    Args:
        input_path: Optional path to highest_grossing CSV; defaults to data/raw/.

    Returns:
        DataFrame with rank, title, distributor, gross (numeric), year, sorted by year/rank.
    """
    gross_path = Path(input_path) if input_path else (RAW_DIR / "highest_grossing.csv")
    df = pd.read_csv(gross_path)

    df["gross"] = (df["gross"]
                   .astype(str)
                   .str.replace(r"\[.*?\]", "", regex=True)
                   .str.replace("$", "", regex=False)
                   .str.replace(",", "", regex=False)
                   .str.strip())

    df["gross"] = pd.to_numeric(df["gross"], errors='coerce')

    keep_col = ['rank', 'title', 'distributor', 'gross', 'year']

    df = df[keep_col].sort_values(by=["year", "rank"]).reset_index(drop=True)

    return df


def clean_top_hits(input_path: Optional[str | Path] = None) -> pd.DataFrame:
    """
    Clean the music dataset.

    Args:
        input_path: Optional path to top_hits CSV; defaults to data/raw/.

    Returns:
        DataFrame with rank, title, main_artist (normalized), display_artist (original casing), year.
    """
    hits_path = Path(input_path) if input_path else (RAW_DIR / "top_hits.csv")
    df = pd.read_csv(hits_path)

    df["title"] = (df["title"].str.replace('"', '', regex=False))

    df["artist"] = df["artist"].astype(str).str.strip()
    df["display_artist"] = (
        df["artist"]
        .str.split(r",", n=1).str[0]
        .str.split(r"\s*&\s*", n=1).str[0]
        .str.split(r"\bwith\b", n=1).str[0]
        .str.split(r"\bfeaturing\b", n=1).str[0]
        .str.split(r"\band\b", n=1).str[0]
        .str.split(r"\bor\b", n=1).str[0]
        .str.strip()
    )

    df['artist'] = df['artist'].str.lower()
    df['is_feature'] = df['artist'].str.contains(r"(?:\:|&|,|\band\b|\bor\b|\bwith\b|\bfeaturing\b|\bfeat\.?\b|\bft\.?\b)").astype(int)

    df["main_artist"] = (
        df["artist"]
        .str.split(r",", n=1).str[0]
        .str.split(r"\s*&\s*", n=1).str[0]
        .str.split(r"\bwith\b", n=1).str[0]
        .str.split(r"\bfeaturing\b", n=1).str[0]
        .str.split(r"\band\b", n=1).str[0]
        .str.split(r"\bor\b", n=1).str[0]
        .str.strip()
    )

    keep_col = ['rank', 'title', 'main_artist', 'display_artist', 'year']

    df = df[keep_col].sort_values(by=["year", "rank"]).reset_index(drop=True)

    return df

def clean_albums_global(input_path: str = "data/raw/albums_wiki.csv") -> pd.DataFrame:
    """
    Clean Wikipedia albums data.

    Args:
        input_path: Path to albums_wiki.csv.

    Returns:
        DataFrame sorted by year/rank with stripped artist/album fields.
    """
    df = pd.read_csv(input_path)

    df["artist"] = df["artist"].astype(str).str.strip()
    df["album"] = df["album"].astype(str).str.strip()

    df = df.sort_values(by=["year", "rank"]).reset_index(drop=True)

    return df

def clean_albums_us(input_path: str = "data/raw/albums_billboard.csv") -> pd.DataFrame:
    """
    Clean Billboard 200 number-one albums data.

    Args:
        input_path: Path to albums_billboard.csv.

    Returns:
        Aggregated DataFrame with rank per year, album, artist, year, weeks_at_one.

    Notes:
        - Normalizes sales to numeric.
        - Flags and strips dagger markers.
        - Aggregates by year/album/artist to count weeks at #1 and derive ranks.
    """
    df = pd.read_csv(input_path)

    df["sales"] = (
        df["sales"].astype(str)
        .str.replace(",", "", regex=False)
        .replace("nan", "0")
    )
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")

    df["is_best_performing"] = df["album"].str.contains("†", na=False)

    df["album"] = df["album"].str.replace("†", "", regex=False).str.strip()
    df["artist"] = df["artist"].str.strip()

    grouped = df.groupby(["year", "album", "artist"]).agg(
        weeks_at_one=("date", "count"),
        is_best=("is_best_performing", "max"),
        max_sales=("sales", "max")
    ).reset_index()

    grouped = grouped.sort_values(
        by=["year", "is_best", "weeks_at_one", "max_sales"],
        ascending=[True, False, False, False]
    )

    grouped["rank"] = grouped.groupby("year").cumcount() + 1

    final_df = grouped[["rank", "album", "artist", "year", "weeks_at_one"]]

    return final_df
