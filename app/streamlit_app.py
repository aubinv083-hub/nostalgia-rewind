import pandas as pd
import streamlit as st
import time

st.set_page_config(page_title="Nostalgia Rewind", page_icon="⏪", layout="centered")

# ---------- Enhanced CSS with custom button styling ----------
st.markdown(
    """
    <style>
      /* Background GIF/Image */
      .stApp {
        background-image: url('https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWF4Z3dpdmQ2ZXl4c2t5NnVyYjZ4dGx5aGlncTB3bjZwZ21qcWo2NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT9Igqq02d80wIqUpy/giphy.gif');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
      }
      
      /* Optional: Add overlay to make text more readable */
      .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        z-index: -1;
      }
      
      .rewind-title {font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px;}
      .rewind-sub {opacity: 0.75; margin-top: -8px;}
      .card {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 18px 18px;
        background: rgba(255,255,255,0.03);
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
        backdrop-filter: blur(10px);
      }
      .label {opacity: 0.7; font-size: 0.9rem; margin-bottom: 4px;}
      .value {font-size: 1.2rem; font-weight: 700; line-height: 1.35;}
      .trend {font-size: 1.1rem; font-weight: 650;}
      .pill {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        font-size: 0.9rem;
      }
            .year-display {
        text-align: center;
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: -1px;
        margin: 0;
        padding: 0;
        line-height: 1;
        color: #FF4B4B;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
      }

      
      /* Custom button styling */
      .stButton button {
        border-radius: 12px;
        border: 2px solid rgba(255, 75, 75, 0.3);
        background: linear-gradient(135deg, rgba(255, 75, 75, 0.1), rgba(255, 75, 75, 0.05));
        transition: all 0.2s ease;
        font-size: 1.5rem;
        padding: 12px;
        backdrop-filter: blur(5px);
      }
      
      .stButton button:hover {
        border-color: rgba(255, 75, 75, 0.6);
        background: linear-gradient(135deg, rgba(255, 75, 75, 0.2), rgba(255, 75, 75, 0.1));
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
      }
      
      .stButton button:active {
        transform: scale(0.95);
      }
      
      /* Style for primary button (Reveal) */
      .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #FF4B4B, #FF6B6B);
        border: none;
        font-weight: 600;
      }
      
      .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #FF6B6B, #FF8B8B);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

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
st.markdown('<div class="rewind-title">⏪ Nostalgia Rewind</div>', unsafe_allow_html=True)
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
if st.button("✨ Reveal my rewind", type="primary", use_container_width=True):
    st.session_state.reveal = True

if st.session_state.reveal:
    with st.spinner("Rewinding..."):
        time.sleep(0.6)

    st.markdown(f"### 🎬🎵 {year} Rewind")
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