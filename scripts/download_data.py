from pathlib import Path
import sys
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

# temporary shim to adjust import paths for running this script directly
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import HTML_DIR, RAW_DIR, WIKI_ALBUM_YEARS, YEAR_END, YEAR_START
from src.io_utils import ensure_data_dirs


FILM_URL = "https://en.wikipedia.org/wiki/{year}_in_film"
MUSIC_URL = "https://en.wikipedia.org/wiki/{year}_in_music"
SINGLES_BILLBOARD_URL = "https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_{year}"
ALBUMS_BILLBOARD_URL = "https://en.wikipedia.org/wiki/List_of_Billboard_200_number-one_albums_of_{year}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def cached_film_path(year: int) -> Path:
    return HTML_DIR / f"{year}_in_film.html"


def cached_music_path(year: int) -> Path:
    return HTML_DIR / f"{year}_in_music.html"


def cached_billboard_singles_path(year: int) -> Path:
    return HTML_DIR / f"billboard_hot_100_{year}.html"


def cached_billboard_albums_path(year: int) -> Path:
    return HTML_DIR / f"billboard_200_{year}.html"


def fetch_with_cache(url: str, cache_path: Path) -> str:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.text
    cache_path.write_text(html, encoding=resp.encoding or "utf-8")
    return html


def fetch_film_page(year: int) -> str:
    """Download the Wikipedia page for the given year with a browser-like user agent and cache HTML locally."""
    url = FILM_URL.format(year=year)
    return fetch_with_cache(url, cached_film_path(year))


def fetch_music_page(year: int) -> str:
    url = MUSIC_URL.format(year=year)
    return fetch_with_cache(url, cached_music_path(year))


def fetch_billboard_singles_page(year: int) -> str:
    url = SINGLES_BILLBOARD_URL.format(year=year)
    return fetch_with_cache(url, cached_billboard_singles_path(year))


def fetch_billboard_albums_page(year: int) -> str:
    url = ALBUMS_BILLBOARD_URL.format(year=year)
    return fetch_with_cache(url, cached_billboard_albums_path(year))


def _section_tables(html: str, keyword: str):
    """Return tables that appear under the first heading matching the keyword."""
    soup = BeautifulSoup(html, "html.parser")
    needle = keyword.lower()
    for heading in soup.find_all(["h2", "h3"]):
        title = heading.get_text(" ", strip=True).lower()
        if needle in title:
            tables = []
            for sibling in heading.find_all_next():
                if sibling.name in ("h2", "h3") and sibling is not heading:
                    break
                if sibling.name == "table":
                    tables.append(sibling)
            return tables
    return []


def parse_html_table(table) -> pd.DataFrame:
    """Parse an HTML table into a DataFrame."""
    rows = table.find_all("tr")
    if not rows:
        return pd.DataFrame()

    grid = []
    span_map = {} 
    first_row_has_header = any(cell.name == "th" for cell in rows[0].find_all(["th", "td"]))

    for row in rows:
        row_vals = []
        col_idx = 0

        def append_spans():
            nonlocal col_idx
            while col_idx in span_map:
                val, remaining = span_map[col_idx]
                row_vals.append(val)
                remaining -= 1
                if remaining == 0:
                    span_map.pop(col_idx)
                else:
                    span_map[col_idx] = (val, remaining)
                col_idx += 1

        append_spans()
        for cell in row.find_all(["td", "th"]):
            text = cell.get_text(" ", strip=True)
            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))
            for _ in range(colspan):
                row_vals.append(text)
                if rowspan > 1:
                    span_map[col_idx] = (text, rowspan - 1)
                col_idx += 1
            append_spans()

        grid.append(row_vals)

    max_cols = max(len(r) for r in grid)
    grid = [r + [None] * (max_cols - len(r)) for r in grid]

    if first_row_has_header:
        headers = [h or f"col_{i}" for i, h in enumerate(grid[0])]
        data = grid[1:]
    else:
        headers = [f"col_{i}" for i in range(max_cols)]
        data = grid

    return pd.DataFrame(data, columns=headers)


def scrape_highest_grossing(year: int) -> pd.DataFrame:
    """Scrape the highest-grossing films table for a given year."""
    html = fetch_film_page(year)
    tables = _section_tables(html, "highest-grossing")
    if not tables:
        return pd.DataFrame()
    df = parse_html_table(tables[0]).ffill()
    col_map = {}
    for col in df.columns:
        c = str(col).lower()
        if "rank" in c:
            col_map[col] = "rank"
        elif "title" in c:
            col_map[col] = "title"
        elif "distributor" in c:
            col_map[col] = "distributor"
        elif "box" in c or "gross" in c:
            col_map[col] = "gross"
    df = df.rename(columns=col_map)
    df["year"] = year
    df = df[["rank", "title", "distributor", "gross", "year"]]
    return df


def scrape_awards(year: int) -> pd.DataFrame:
    """Scrape awards tables for a given year, keeping only category/org + Academy Awards columns."""
    html = fetch_film_page(year)
    tables = _section_tables(html, "awards")
    if not tables:
        return pd.DataFrame()

    frames = []
    for table in tables:
        frame = parse_html_table(table).ffill()
        if frame.empty:
            continue
        cols = list(frame.columns)
        if not cols:
            continue
        keep = [cols[0]]
        for col in cols[1:]:
            col_lower = str(col).lower()
            if "academy" in col_lower:
                keep.append(col)

        if len(keep) < 2:
            continue
        frame = frame[keep]
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True).ffill()
    cols = list(df.columns)
    df = df.rename(columns={cols[0]: "category", cols[1]: "winner"})
    df["year"] = year
    df = df[["category", "winner", "year"]]
    return df


def scrape_wiki_albums(year: int) -> pd.DataFrame:
    """
    Scrape top albums from the {year}_in_music page.
    Only available for specific years noted in config.WIKI_ALBUM_YEARS.
    """
    if year not in WIKI_ALBUM_YEARS:
        return pd.DataFrame()

    html = fetch_music_page(year)
    soup = BeautifulSoup(html, "html.parser")
    keywords = [
        "top ten best albums",
        "top 10 best albums",
        "top best albums",
        "best-selling albums globally",
        "top 5 albums",
    ]
    heading = None
    for h in soup.find_all(["h2", "h3"]):
        title = h.get_text(" ", strip=True).lower()
        if any(k in title for k in keywords):
            heading = h
            break
    if heading is None:
        return pd.DataFrame()

    tables = []
    lists = []
    for sibling in heading.find_all_next():
        if sibling.name in ("h2", "h3") and sibling is not heading:
            break
        if sibling.name == "table":
            tables.append(sibling)
        if sibling.name in ("ul", "ol"):
            lists.append(sibling)

    if tables:
        df = parse_html_table(tables[0]).ffill()
        col_map = {}
        for col in df.columns:
            c = str(col).lower()
            if "position" in c:
                col_map[col] = "rank"
            elif "album" in c:
                col_map[col] = "album"
            elif "artist" in c:
                col_map[col] = "artist"
        df = df.rename(columns=col_map)
        desired = ["rank", "artist", "album"]
        for col in desired:
            if col not in df.columns:
                df[col] = None
        df = df[desired]
    elif lists:
        items = []
        rank = 1
        for li in lists[0].find_all("li", recursive=False):
            text = li.get_text(" ", strip=True)
            text = re.sub(r"^\d+\.\s*", "", text)
            artist, album = None, None
            for sep in [" – ", " - ", "–", "-"]:
                if sep in text:
                    artist, album = text.split(sep, 1)
                    break
            if artist is None or album is None:
                continue
            items.append({"rank": rank, "artist": artist.strip(), "album": album.strip()})
            rank += 1
        df = pd.DataFrame(items)
        if df.empty:
            return df
    else:
        return pd.DataFrame()

    df["year"] = year
    return df[["rank", "artist", "album", "year"]]


def scrape_billboard_albums(year: int) -> pd.DataFrame:
    """Scrape Billboard 200 number-one albums list for a given year."""
    html = fetch_billboard_albums_page(year)
    soup = BeautifulSoup(html, "html.parser")
    tables = (
        _section_tables(html, "chart history")
        or _section_tables(html, "number-ones")
        or soup.find_all("table")
    )
    table = None
    for t in tables:
        header_text = " ".join(h.get_text(" ", strip=True).lower() for h in t.find_all("th"))
        if any(key in header_text for key in ["issue", "date", "album", "artist"]):
            table = t
            break
    if table is None:
        return pd.DataFrame()

    df = parse_html_table(table).ffill()
    df = df[[col for col in df.columns if "ref" not in str(col).lower()]]
    df = df.loc[:, ~pd.Index(df.columns).duplicated()]
    col_map = {}
    for col in df.columns:
        c = str(col).lower()
        if "date" in c:
            col_map[col] = "date"
        elif "album" in c:
            col_map[col] = "album"
        elif "artist" in c:
            col_map[col] = "artist"
        elif "label" in c:
            col_map[col] = "label"
        elif "sales" or "units" in c:
            col_map[col] = "sales"
    df = df.rename(columns=col_map)
    desired = ["date", "album", "artist", "label", "sales"]
    for col in desired:
        if col not in df.columns:
            df[col] = None
    df = df[desired]
    df["year"] = year
    return df


def scrape_top_hits(year: int) -> pd.DataFrame:
    """
    Scrape biggest hit singles for the given year.
    1985-2000: use {year}_in_music page, "Biggest hit singles" section.
    2001+: use Billboard Year-End Hot 100 page.
    """
    desired_cols = ["rank", "artist", "title"]

    if year <= 2000:
        html = fetch_music_page(year)
        tables = _section_tables(html, "biggest hit singles")
        if not tables:
            return pd.DataFrame()
        df = parse_html_table(tables[0]).iloc[:, :3]
        rename_map = {df.columns[i]: desired_cols[i] for i in range(min(len(df.columns), len(desired_cols)))}
        df = df.rename(columns=rename_map)
    else:
        html = fetch_billboard_singles_page(year)
        soup = BeautifulSoup(html, "html.parser")
        tables = _section_tables(html, "list") or soup.find_all("table")
        table = None
        for t in tables:
            header_text = " ".join([h.get_text(" ", strip=True).lower() for h in t.find_all("th")])
            if any(key in header_text for key in ["title", "artist", "no", "№"]):
                table = t
                break
        if table is None:
            return pd.DataFrame()
        df = parse_html_table(table).iloc[:, :3]
        rename_map = {}
        if len(df.columns) >= 1:
            rename_map[df.columns[0]] = "rank"
        if len(df.columns) >= 2:
            rename_map[df.columns[1]] = "title"
        if len(df.columns) >= 3:
            rename_map[df.columns[2]] = "artist"
        df = df.rename(columns=rename_map)
        df = df[["rank", "artist", "title"]] if "artist" in df.columns else df

    for col in desired_cols:
        if col not in df.columns:
            df[col] = None
    df = df[desired_cols]
    df["year"] = year
    return df


def scrape_films_range(year_start: int = 1985, year_end: int = 2015):
    """Scrape highest-grossing and awards tables across a year range and persist CSVs."""
    hg_frames = []
    awards_frames = []

    for year in range(year_start, year_end + 1):
        hg = scrape_highest_grossing(year)
        if not hg.empty:
            hg_frames.append(hg)

        aw = scrape_awards(year)
        if not aw.empty:
            awards_frames.append(aw)

    highest = pd.concat(hg_frames, ignore_index=True) if hg_frames else pd.DataFrame()
    awards = pd.concat(awards_frames, ignore_index=True) if awards_frames else pd.DataFrame()

    if not highest.empty:
        highest.to_csv(RAW_DIR / "highest_grossing.csv", index=False)
    if not awards.empty:
        awards.to_csv(RAW_DIR / "awards.csv", index=False)

    return highest, awards


def scrape_music_range(year_start: int = 1985, year_end: int = 2015):
    """Scrape top hits across a year range and persist a CSV."""
    frames = []
    for year in range(year_start, year_end + 1):
        df = scrape_top_hits(year)
        if not df.empty:
            frames.append(df)
    hits = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not hits.empty:
        hits.to_csv(RAW_DIR / "top_hits.csv", index=False)
    return hits


def scrape_wiki_albums_range():
    """Scrape available wiki album lists and persist a CSV."""
    frames = []
    for year in WIKI_ALBUM_YEARS:
        df = scrape_wiki_albums(year)
        if not df.empty:
            frames.append(df)
    albums = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not albums.empty:
        albums.to_csv(RAW_DIR / "albums_wiki.csv", index=False)
    return albums


def scrape_billboard_albums_range(year_start: int = 1985, year_end: int = 2015):
    """Scrape Billboard 200 number-one albums across a year range and persist a CSV."""
    frames = []
    for year in range(year_start, year_end + 1):
        df = scrape_billboard_albums(year)
        if not df.empty:
            frames.append(df)
    if frames:
        base_cols = ["date", "album", "artist", "label", "sales", "year"]
        cleaned = []
        for f in frames:
            f = f.loc[:, ~f.columns.duplicated()]
            cleaned.append(f.reindex(columns=base_cols))
        albums = pd.concat(cleaned, ignore_index=True)
    else:
        albums = pd.DataFrame()
    if not albums.empty:
        albums.to_csv(RAW_DIR / "albums_billboard.csv", index=False)
    return albums


def main():
    ensure_data_dirs()
    scrape_films_range(YEAR_START, YEAR_END)
    scrape_music_range(YEAR_START, YEAR_END)
    scrape_wiki_albums_range()
    scrape_billboard_albums_range(YEAR_START, YEAR_END)


if __name__ == "__main__":
    main()
