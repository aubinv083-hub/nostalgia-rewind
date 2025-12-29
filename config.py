from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
HTML_DIR = DATA_DIR / "html"

HTML_CACHE_ENABLED = False

YEAR_START = 1985
YEAR_END = 2015

WIKI_ALBUM_YEARS = [1990, 1991, 1992, 1993, 1994, 1995, 2003, 2007, 2009]
