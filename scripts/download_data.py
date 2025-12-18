from pathlib import Path
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import HTML_DIR, RAW_DIR, YEAR_END, YEAR_START

BASE_URL = "https://en.wikipedia.org/wiki/{year}_in_film"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def cached_html_path(year: int) -> Path:
    return HTML_DIR / f"{year}_in_film.html"


def fetch_page(year: int) -> str:
    """Download the Wikipedia page for the given year with a browser-like user agent and cache HTML locally."""
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    cached = cached_html_path(year)
    if cached.exists():
        return cached.read_text(encoding="utf-8")

    url = BASE_URL.format(year=year)
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.text
    cached.write_text(html, encoding=resp.encoding or "utf-8")
    return html


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
    """Parse an HTML table into a DataFrame handling rowspan/colspan with BeautifulSoup only."""
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
    """Scrape the first Highest-grossing films table for a given year."""
    html = fetch_page(year)
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
    """Scrape Awards tables for a given year, keeping only category/org + Academy Awards columns."""
    html = fetch_page(year)
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


def scrape_range(year_start: int = 1985, year_end: int = 2015):
    """Scrape Highest-grossing and Awards tables across a year range and persist CSVs."""
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

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not highest.empty:
        highest.to_csv(RAW_DIR / "highest_grossing.csv", index=False)
    if not awards.empty:
        awards.to_csv(RAW_DIR / "awards.csv", index=False)

    return highest, awards


def main():
    scrape_range(YEAR_START, YEAR_END)


if __name__ == "__main__":
    main()
