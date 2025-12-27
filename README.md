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
### CLI 
1) Create a virtual environment (recommended):
```bash
python -m venv .venv
. .venv/Scripts/activate
```
2) Install dependencies:
```bash
pip install -r requirements.txt
```
3) Run the pipeline at the repo root through the CLI 
```bash
python run_all.py
```
### Docker
Prerequisites: Docker Desktop installed and running <br>
Docker Hub repository: https://hub.docker.com/r/noamlevillayer/nostalgia-rewind
1) Run from Docker Hub:
```bash
docker run -p 8501:8501 noamlevillayer/nostalgia-rewind:latest
```
Then open your browser to: http://localhost:8501

2) Build from source : 
```bash
docker build -t nostalgia-rewind .
docker run -p 8501:8501 nostalgia-rewind
```
## Notes
- Add or swap data sources in `src/data_sources.py`.
- Update schema rules or cleaning steps in `src/preprocess.py`.
- Processed artifacts are saved under `data/processed/`; raw pulls under `data/raw/`.
- Docker container automatically runs the full pipeline (download → build → launch UI).
- For local setup, the Streamlit app launches at http://localhost:8501 after running python run_all.py.
