# Nostalgia Rewind

Nostalgia Rewind is your time machine in a browser. Drop in your birth year (or any year 1985-2015) and watch the world reassemble: the movies that ruled the box office, the songs stuck on repeat, the albums that owned the charts, the Oscar winners, and the headlines that defined the moment (all linked out so you can dive straight down memory lane). Scroll through the years to see how culture evolves, then cap it off by blasting through ‘Tux in Space’ at the bottom of the page, because every rewind deserves a little arcade chaos.

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

## Data sources
- Films & awards: [Wikipedia “{year} in film”](https://en.wikipedia.org/wiki/1985_in_film) (1985-2015), Highest-grossing + Awards sections.
- Hit singles: [Wikipedia “{year} in music”](https://en.wikipedia.org/wiki/1985_in_music) (1985-2000, “Biggest hit singles” section) and [Billboard Year-End Hot 100](https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_2001) (2001-2015).
- Albums: [Wikipedia “{year} in music”](https://en.wikipedia.org/wiki/1995_in_music) best-albums sections (1990-1995, 2003, 2007, 2009) and [Billboard 200 number-one albums](https://en.wikipedia.org/wiki/List_of_Billboard_200_number-one_albums_of_1985) (1985-2015).
- Events: generated once via ChatGPT-5.2 Thinking (web UI) with the prompt below (manual, non-reproducible) using [Wikipedia “{year}” pages](https://en.wikipedia.org/wiki/1985) (1985-2015). 

<details>
<summary>Prompt used for events (LLM, manual run)</summary>

```text
You are given a Wikipedia “YEAR” page. 

Your task is to extract **exactly 10 key events** from that page that best represent a global “snapshot” of that year.

**Definition of “important event”:**
An important event is one that was **widely discussed at the time** and/or had a **significant long-term impact** on politics, science, technology, culture, or society.

**Category constraints:**

* Use only the following categories: `politics`, `science`, `technology`, `culture`, `society`
* Each category should have **at least 1 event and at most 3 events**
* The total number of events must be **exactly 10**

**Event description rules:**

* Maximum **10 words per event description**
* Descriptions must be factual and neutral
* Do not include dates unless necessary
* Keep the original formatting, do not put everything in lowercase.
* Do not come up with events that are not mentioned on a given page.

**Output format:**

* Output **CSV only**, no explanations
* Columns must be exactly:
  `year,category,event,importance`
* `importance` is an integer from **1 (less important) to 5 (very important)**, relative *within that year*

**Selection rules:**

* Prefer events with global relevance
* Avoid very local or minor events unless historically significant
* Use the Wikipedia year page as the sole source

**Begin once the page is provided.**

Example of output format:

year,category,event,importance
1985,science,Ozone hole discovery announced,5
1985,technology,Domain Name System created,4
1985,politics,Schengen Agreement signed,4
1985,culture,We Are the World released,3
...

The page is https://en.wikipedia.org/wiki/1985
```
</details>

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
