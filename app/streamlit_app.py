import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
from pathlib import Path

st.set_page_config(page_title="Nostalgia Rewind", page_icon="🎦", layout="wide")

# GAME DEPENDENCIES
base = Path(__file__).parent / "assets"
html = (base / "game.html").read_text(encoding="utf-8")

# CSS DEPENDENCIES
css_path = Path(__file__).resolve().parent / "assets" / "style.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# DATA DEPENDENCIES 
data_folder = Path(__file__).resolve().parent.parent / "data" / "processed"
movies_path = data_folder / "highest_grossing.csv"
music_path = data_folder / "top_hits.csv"
@st.cache_data
def load_movie_data():
    return pd.read_csv(movies_path)

@st.cache_data
def load_music_data():
    return pd.read_csv(music_path)

# ---------- Year range for navigation ----------
years_desc = list(range(2015, 1984, -1))

# ---------- Initialize session state ----------
if "current_year_index" not in st.session_state:
    st.session_state.current_year_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False

# ---------- Header ----------
st.markdown('<div class="rewind-title">Nostalgia Rewind</div>', unsafe_allow_html=True)
st.write("")
st.write("")

# ---------- Navigation Controls ----------
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("◀", key="prev", use_container_width=True):
        st.session_state.current_year_index = min(
            st.session_state.current_year_index + 1, len(years_desc) - 1
        )
        st.session_state.reveal = False
        st.rerun()
    
with col2:
    current_year = years_desc[st.session_state.current_year_index]
    st.markdown(
        f'<div class="year-display">{current_year}</div>',
        unsafe_allow_html=True
    )

with col3:
    if st.button("▶", key="next", use_container_width=True):
        st.session_state.current_year_index = max(
            st.session_state.current_year_index - 1, 0
        )
        st.session_state.reveal = False
        st.rerun()

# ---------- Reveal button ----------
st.write("")
if st.button("⏮ REWIND ⏮", type="primary", use_container_width=True):
    st.session_state.reveal = True

# ---------- Reveal section (placeholder) ----------
if st.session_state.reveal:
    with st.spinner("Rewinding..."):
        time.sleep(0.6)

    year = years_desc[st.session_state.current_year_index]
    st.markdown(f"Your {year} Rewind")
    st.write("")

    # ---------- Yearly Snapshot Section ----------
    colA, colB = st.columns([2,1])
    
    # LEFT COLUMN - Movies
    with colA:
        st.markdown('<div style="text-align: center;">Top 5 Movies</div>', unsafe_allow_html=True)

        try:
            movies_df = load_movie_data()
            year_movies = movies_df[movies_df["year"] == year].head(5)

            if not year_movies.empty:
                display_movies = year_movies[
                    ["rank", "title", "distributor", "gross"]
                ].copy()

                display_movies.columns = [
                    "Rank", "Title", "Distributor", "Box Office"
                ]
                display_movies = display_movies.set_index("Rank")
                st.table(display_movies)


            else:
                st.info(f"No movie data available for {year}")

        except Exception as e:
            st.error(f"Error loading movie data: {str(e)}")

    
    # RIGHT COLUMN - Music
    with colB:
        st.markdown('<div style="text-align: center;">Top 5 Hits</div>', unsafe_allow_html=True)
        
        try:
            music_df = load_music_data()
            year_music = music_df[music_df['year'] == year].head(5)
            
            if not year_music.empty:
                display_music = year_music[['rank', 'title', 'main_artist']].copy()
                display_music.columns = ['Rank', 'Song', 'Artist']
                
                display_music = display_music.set_index("Rank")
                st.table(display_music)
            else:
                st.info(f"No music data available for {year}")
                
        except Exception as e:
            st.error(f"Error loading music data: {str(e)}")
else:
    st.caption("Navigate with arrows, then reveal your rewind.")

# ---------- Game component ----------
st.markdown('<div style="text-align: center;">Bored ? Help Tux to destroy Bill Gates army !!</div>', unsafe_allow_html=True)
components.html(html, height=700, scrolling=False)