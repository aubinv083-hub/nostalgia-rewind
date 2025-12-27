# Nostalgia Rewind

Nostalgia Rewind is your time machine in a browser. Drop in your birth year (or any year 1985-2015) and watch the world reassemble: the movies that ruled the box office, the songs stuck on repeat, the albums that owned the charts, the Oscar winners, and the headlines that defined the moment. Scroll through the years to see how culture evolves, then cap it off by blasting through ‘Tux in Space’ at the bottom of the page, because every rewind deserves a little arcade chaos.

## Repo structure
```
app/
├── assets/
│   ├── game.html          # Tux in Space mini-game
│   └── style.css          # UI styling
└── streamlit_app.py       # Main Streamlit UI

config.py                  # Paths and year ranges

data/
├── html/                  # Cached HTML files
├── raw/                   # Scraped CSVs (films, hits, awards, albums)
└── processed/             # Cleaned/analytic outputs and events

scripts/
├── build_dataset.py       # Runs preprocessing + analytics
└── download_data.py       # Scrapes Wikipedia/Billboard to raw CSVs

src/
├── analytics.py           # Aggregations (yearly stats, top artists, album summaries)
├── io_utils.py            # Filesystem helpers
└── preprocess.py          # Cleaning/standardising films, awards, singles, albums

Dockerfile
LICENSE
README.md                  # This file
requirements.txt           # Python deps
run_all.py                 # Orchestrates download -> build -> app
```

## Getting started
### CLI 
1) Create a virtual environment
```bash
python -m venv .venv

source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
```

2) Install dependencies
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

2) Build from source: 
```bash
docker build -t nostalgia-rewind .
docker run -p 8501:8501 nostalgia-rewind
```
