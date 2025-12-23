import streamlit as st
import streamlit.components.v1 as components
import time
from pathlib import Path

st.set_page_config(page_title="Nostalgia Rewind", page_icon="🎦", layout="centered")

# GAME DEPENDENCIES
base = Path(__file__).parent / "assets"
html = (base / "game.html").read_text(encoding="utf-8")

# CSS DEPENDENCIES
css_path = Path(__file__).resolve().parent / "assets" / "style.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------- Year range for navigation ----------
years_desc = list(range(2024, 1979, -1))

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
if st.button("⏮️ REWIND ⏮️", type="primary", use_container_width=True):
    st.session_state.reveal = True

# ---------- Reveal section (placeholder) ----------
if st.session_state.reveal:
    with st.spinner("Rewinding..."):
        time.sleep(0.6)

    year = years_desc[st.session_state.current_year_index]
    st.markdown(f"Your {year} Rewind ✨")
    st.write("")

    # TODO: Replace with teammate's data structure
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown(
            """
            <div class="card">
              <div class="label">Top Film</div>
              <div class="value">Coming soon</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with colB:
        st.markdown(
            """
            <div class="card">
              <div class="label">Top Music</div>
              <div class="value">Coming soon</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(
        """
        <div class="card">
          <div class="label">Trend</div>
          <div class="trend">Coming soon</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.caption("Navigate with arrows, then reveal your rewind.")

# ---------- Game component ----------
components.html(html, height=700, scrolling=False)