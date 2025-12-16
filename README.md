# Nostalgia Rewind

Data pipeline and Streamlit UI for exploring nostalgia-driven music trends. The project scrapes multiple sources, standardises them into a common schema, and surfaces quick analytics (genre shares, yearly counts, peak trends).

## Project layout
- `app/streamlit_app.py` — Streamlit UI for the processed dataset.
- `src/data_sources.py` — scraping + Google Trends helpers.
- `src/preprocess.py` — cleaning, standardising columns, joining sources.
- `src/analytics.py` — simple stats helpers.
- `src/io_utils.py` — paths, caching, I/O.
- `scripts/download_data.py` — reproducible fetch step.
- `scripts/build_dataset.py` — end-to-end preprocessing.
- `data/raw/` and `data/processed/` — local artifacts (not committed if large).
- `tests/` — lightweight checks (schema shape, empty years).

## Getting started
1) Create a virtual environment (recommended):
```bash
python -m venv .venv
. .venv/Scripts/activate
```
2) Install dependencies:
```bash
pip install -r requirements.txt
```
3) Download raw data (adjust sources/keywords inside the script as needed):
```bash
python scripts/download_data.py
```
4) Build the processed dataset:
```bash
python scripts/build_dataset.py
```
5) Launch the UI:
```bash
streamlit run app/streamlit_app.py
```

## Notes
- Add or swap data sources in `src/data_sources.py`.
- Update schema rules or cleaning steps in `src/preprocess.py`.
- Processed artifacts are saved under `data/processed/`; raw pulls under `data/raw/`.
