import pytest
import pandas as pd
import os
from src.preprocess import clean_gross, clean_top_hits, clean_albums_us, clean_albums_global


# ==========================================
# 1. TEST MOVIES (Highest Grossing)
# ==========================================
def test_gross_schema():
    """Check if the cleaned gross data has the right columns and types."""
    df = clean_gross("data/raw/highest_grossing.csv")

    assert "rank" in df.columns, "Rank column is missing in movies!"

    # Check numeric types
    assert pd.api.types.is_numeric_dtype(df["gross"])
    assert pd.api.types.is_numeric_dtype(df["rank"])

    # Sanity check: Rank 1 should have more money than Rank 10 in the same year
    # Let's pick a random year, e.g., 2014
    subset = df[df["year"] == 2014].sort_values("rank")
    if len(subset) > 1:
        assert subset.iloc[0]["gross"] >= subset.iloc[-1]["gross"]


# ==========================================
# 2. TEST SONGS (Top Hits)
# ==========================================
def test_top_hits_cleaning():
    """Check if triple quotes are removed and Rank exists."""
    df = clean_top_hits("data/raw/top_hits.csv")

    # Check Rank
    assert "rank" in df.columns, "Rank column is missing in songs!"

    # Check Clean Titles
    sample_title = df["title"].iloc[0]
    assert not sample_title.startswith('"'), f"Title still has quotes: {sample_title}"


# ==========================================
# 3. TEST ALBUMS (New Logic)
# ==========================================
def test_albums_us_logic():
    """
    Test the complex 'dagger' (†) logic for Billboard albums.
    The album with '†' MUST be Rank 1.
    """
    df = clean_albums_us("data/raw/albums_billboard.csv")

    # Let's check 1985 (Bruce Springsteen had the †)
    year_1985 = df[df["year"] == 1985].sort_values("rank")

    # The Rank 1 album should be "Born in the U.S.A."
    winner = year_1985.iloc[0]
    assert "Born in the U.S.A." in winner["album"], f"Expected Born in the U.S.A. at #1, got {winner['album']}"
    assert winner["rank"] == 1


def test_albums_global_schema():
    """Simple sanity check for the Wiki albums."""
    df = clean_albums_global("data/raw/albums_wiki.csv")
    assert "rank" in df.columns
    assert "artist" in df.columns
    assert len(df) > 0