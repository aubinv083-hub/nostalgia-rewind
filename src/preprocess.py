from pathlib import Path
import pandas as pd
import re

from config import RAW_DIR

def clean_awards(input_path=None):
    """Cleans the awards dataset."""
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


def clean_gross(input_path=None):
    """Cleans the box office dataset."""
    gross_path = Path(input_path) if input_path else (RAW_DIR / "highest_grossing.csv")
    df = pd.read_csv(gross_path)

    # Robust Regex cleaning for the 'gross' column
    df["gross"] = (df["gross"]
                   .astype(str)
                   .str.replace(r"\[.*?\]", "", regex=True)  # Removes [ 1 ], [ nb 2 ]
                   .str.replace("$", "", regex=False)
                   .str.replace(",", "", regex=False)
                   .str.strip())

    df["gross"] = pd.to_numeric(df["gross"], errors='coerce')

    # Aggregation per distributor
    df["gross_per_distr"] = df.groupby('distributor')['gross'].transform('sum')

    keep_col = ['distributor', 'year', 'gross', 'gross_per_distr', 'title']
    df = df[keep_col].sort_values(by=["distributor", "year"]).reset_index(drop=True)

    return df


def clean_top_hits(input_path=None):
    """Cleans the music dataset."""
    hits_path = Path(input_path) if input_path else (RAW_DIR / "top_hits.csv")
    df = pd.read_csv(hits_path)

    df["title"] = (df["title"].str.replace('"', '', regex=False))

    df['artist'] = df['artist'].str.lower()
    df['is_feature'] = df['artist'].str.contains(r"(?:\:|&|,|\band\b|\bor\b|\bwith\b|\bfeaturing\b|\bfeat\.?\b|\bft\.?\b)").astype(int)

    # Extract main artist
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

    df['artist_featuring'] = (
        df['artist']
        .str.split(r":|,|&|\bwith\b|\bfeaturing\b|\band\b|\bor\b", n=1, regex=True)
        .str[1]
        .str.strip()
    )

    df['artist_number_sing'] = df.groupby('main_artist')['main_artist'].transform('count')

    keep_col = ['main_artist', 'artist_number_sing', 'artist_featuring', 'title', 'year']
    df = df[keep_col]

    df = df.sort_values(by=["artist_number_sing", "main_artist", "year"], ascending=[False, False, True]).reset_index(
        drop=True)

    return df
