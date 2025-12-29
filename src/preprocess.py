from pathlib import Path
from typing import Optional
import pandas as pd
import requests

from config import RAW_DIR

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def resolve_film_wiki_url(title: str, year: int) -> str:
    """
    Try film-specific Wikipedia URLs in order, falling back to the generic title.
    Accepts the first non-missing page.
    """
    base_title = title.replace(" ", "_")
    candidates = [
        f"https://en.wikipedia.org/wiki/{base_title}_({year}_Disney_film)",
        f"https://en.wikipedia.org/wiki/{base_title}_({year}_film)",
        f"https://en.wikipedia.org/wiki/{base_title}_(film)",
        f"https://en.wikipedia.org/wiki/{base_title}",
    ]
    for url in candidates:
        try:
            resp = requests.get(url, timeout=5, allow_redirects=True, headers=HEADERS)
            if resp.status_code == 403:
                return url
            if resp.status_code != 200:
                continue
            html = resp.text
            final = resp.url.lower()
            if "wikipedia does not have an article with this exact name" in html:
                continue
            if "may also refer to" in html.lower():
                continue
            if f"({year}_film)" in final or "_(film)" in final:
                return resp.url
            if resp.url.rstrip("/") == url.rstrip("/"):
                return resp.url
        except Exception:
            continue
    return candidates[-1]


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
    df["category"] = df["category"].str.replace("Best Picture", "Best Film", regex=False)

    df = (
        df.assign(
            category=df["category"].str.strip().str.lower(),
            year=pd.to_numeric(df["year"], errors="coerce")
        )
        .sort_values(by=["category", "year"], ascending=[True, True])
        .reset_index(drop=True)
    )

    mask_film = df["category"].str.contains("film", na=False)
    df.loc[mask_film, "winner"] = df.loc[mask_film, "winner"].str.split(" - ", n=1).str[0].str.strip()

    df["url"] = None
    mask_best_film = df["category"] == "best film"
    df.loc[mask_best_film, "url"] = df.loc[mask_best_film].apply(
        lambda r: resolve_film_wiki_url(str(r["winner"]), int(r["year"])), axis=1
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

    df["url"] = df.apply(lambda r: resolve_film_wiki_url(r["title"], int(r["year"])), axis=1)

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
