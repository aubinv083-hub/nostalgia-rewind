import pytest
import pandas as pd
import os
import sys

# Add the project root to the python path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocess import clean_gross, clean_top_hits


# Helper to check if file exists (optional if you test functions directly)
def test_files_exist():
    assert os.path.exists("data/raw/highest_grossing.csv"), "Raw gross data missing"


def test_gross_schema():
    """Check if the cleaned gross data has the right columns and types."""
    df = clean_gross("data/raw/highest_grossing.csv")

    assert "gross" in df.columns
    assert "year" in df.columns
    # Check that gross is actually a number (float or int), not object/string
    assert pd.api.types.is_numeric_dtype(df["gross"])
    # Check we have data
    assert len(df) > 0


def test_top_hits_cleaning():
    """Check if triple quotes are removed."""
    df = clean_top_hits("data/raw/top_hits.csv")

    # Check that no title starts with a quote
    sample_title = df["title"].iloc[0]
    assert not sample_title.startswith('"'), f"Title still has quotes: {sample_title}"

    # Check year range (should be roughly 1985-2015 based on your data)
    assert df["year"].min() >= 1980
    assert df["year"].max() <= 2026