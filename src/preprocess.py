import pandas as pd
import re

def clean_awards(input_path="data/raw/awards.csv"):
    """Cleans the awards dataset."""
    df = pd.read_csv(input_path)

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


def clean_gross(input_path="data/raw/highest_grossing.csv"):
    """Cleans the box office dataset."""
    df = pd.read_csv(input_path)

    # Robust cleaning
    df["gross"] = (df["gross"]
                   .astype(str)
                   .str.replace(r"\[.*?\]", "", regex=True)
                   .str.replace("$", "", regex=False)
                   .str.replace(",", "", regex=False)
                   .str.strip())

    df["gross"] = pd.to_numeric(df["gross"], errors='coerce')

    # Keep the rank!
    keep_col = ['rank', 'title', 'distributor', 'gross', 'year']

    # Sort by Year and Rank (Best for the App display)
    df = df[keep_col].sort_values(by=["year", "rank"]).reset_index(drop=True)

    return df


def clean_top_hits(input_path="data/raw/top_hits.csv"):
    """Cleans the music dataset."""
    df = pd.read_csv(input_path)

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

    keep_col = ['rank', 'title', 'main_artist', 'year']

    df = df[keep_col].sort_values(by=["year", "rank"]).reset_index(drop=True)

    return df

def clean_albums_global(input_path="data/raw/albums_wiki.csv"):

    df = pd.read_csv(input_path)

    # specific cleaning if needed
    df["artist"] = df["artist"].astype(str).str.strip()
    df["album"] = df["album"].astype(str).str.strip()

    # Ensure sorted
    df = df.sort_values(by=["year", "rank"]).reset_index(drop=True)

    return df

def clean_albums_us(input_path="data/raw/albums_billboard.csv"):

    df = pd.read_csv(input_path)

    # 1. Clean Sales (remove commas, handle NaNs)
    df["sales"] = (
        df["sales"].astype(str)
        .str.replace(",", "", regex=False)
        .replace("nan", "0")
    )
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")

    # 2. Detect the "Best Performing" marker (†)
    df["is_best_performing"] = df["album"].str.contains("†", na=False)

    # 3. Clean Album Name (remove the dagger)
    df["album"] = df["album"].str.replace("†", "", regex=False).str.strip()
    df["artist"] = df["artist"].str.strip()

    # 4. Aggregate by Year + Album
    grouped = df.groupby(["year", "album", "artist"]).agg(
        weeks_at_one=("date", "count"),
        is_best=("is_best_performing", "max"),
        max_sales=("sales", "max")
    ).reset_index()

    # 5. Calculate Ranks per Year
    grouped = grouped.sort_values(
        by=["year", "is_best", "weeks_at_one", "max_sales"],
        ascending=[True, False, False, False]
    )

    grouped["rank"] = grouped.groupby("year").cumcount() + 1

    final_df = grouped[["rank", "album", "artist", "year", "weeks_at_one"]]

    return final_df