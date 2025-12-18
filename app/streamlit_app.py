import pandas as pd
import streamlit as st
import time
from pathlib import Path

st.set_page_config(page_title="Nostalgia Rewind", page_icon="⏪", layout="centered")

css_path = Path(__file__).resolve().parent / "assets" / "style.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------- Load data ----------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    return df.sort_values("year").reset_index(drop=True)

CSV_PATH = "../data/processed/toy_dataset.csv"
df = load_data(CSV_PATH)

years_desc = sorted(df["year"].unique(), reverse=True)
min_year, max_year = min(years_desc), max(years_desc)

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
    if st.button("⏪", use_container_width=True):
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
    if st.button("⏩", use_container_width=True):
        st.session_state.current_year_index = max(
            st.session_state.current_year_index - 1, 0
        )
        st.session_state.reveal = False
        st.rerun()

# ---------- Get current data ----------
year = years_desc[st.session_state.current_year_index]
row = df[df["year"] == year].iloc[0]

# ---------- Reveal animation ----------
st.write("")
if st.button("--REWIND--", type="primary", use_container_width=True):
    st.session_state.reveal = True

if st.session_state.reveal:
    with st.spinner("Rewinding..."):
        time.sleep(0.6)

    st.markdown(f"Your {year} Rewind :")
    st.write("")

    colA, colB = st.columns(2)
    with colA:
        st.markdown(
            f"""
            <div class="card">
              <div class="label">Top Film</div>
              <div class="value">{row['top_film']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with colB:
        st.markdown(
            f"""
            <div class="card">
              <div class="label">Top Music</div>
              <div class="value">{row['top_music']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(
        f"""
        <div class="card">
          <div class="label">Trend</div>
          <div class="trend">🔥 {row['trend']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.caption("Navigate with arrows, then reveal your rewind.")