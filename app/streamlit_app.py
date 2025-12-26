import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
from pathlib import Path
import altair as alt
import plotly.graph_objects as go
import plotly.express as px

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
awards_path = data_folder / "awards.csv"
albums_us_path = data_folder / "albums_us.csv"
analytics_longest_reigning_path = data_folder / "analytics_longest_reigning_albums.csv"
analytics_top_artists_path = data_folder / "analytics_top_artists.csv"
analytics_yearly_stats_path = data_folder / "analytics_yearly_stats.csv"
events_path = data_folder / "events.csv"
albums_global_path = data_folder / "albums_global.csv"

@st.cache_data
def load_movie_data():
    return pd.read_csv(movies_path)

@st.cache_data
def load_music_data():
    return pd.read_csv(music_path)

@st.cache_data
def load_awards_data():
    return pd.read_csv(awards_path)

@st.cache_data
def load_albums_us():
    return pd.read_csv(albums_us_path)

@st.cache_data
def load_analytics_longest_reigning():
    return pd.read_csv(analytics_longest_reigning_path)

@st.cache_data
def load_analytics_top_artists():
    return pd.read_csv(analytics_top_artists_path)

@st.cache_data
def load_analytics_yearly_stats():
    return pd.read_csv(analytics_yearly_stats_path)

@st.cache_data
def load_events_data():
    return pd.read_csv(events_path)

@st.cache_data
def load_albums_global():
    return pd.read_csv(albums_global_path)
# YEAR RANGE
years_desc = list(range(2015, 1984, -1))

# INITIALIZE
if "current_year_index" not in st.session_state:
    st.session_state.current_year_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False

# HEADER
st.markdown('<div class="rewind-title">Nostalgia Rewind</div>', unsafe_allow_html=True)
st.write("")
st.write("")

# CONTROL BUTTONS
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

# REVEAL BUTTON
st.write("")
if st.button("⏮ REWIND ⏮", type="primary", use_container_width=True):
    st.session_state.reveal = True

# DYNAMIC SECTION
if st.session_state.reveal:
    with st.spinner("Rewinding..."):
        time.sleep(0.6)

    year = years_desc[st.session_state.current_year_index]
    st.markdown(f"Your {year} Rewind")
    st.write("")

    
    colA, colB = st.columns([2,1])
    
    with colA:
        st.markdown('<div style="text-align: center;">Top 5 Movies</div>', unsafe_allow_html=True)

        try:
            movies_df = load_movie_data()
            year_movies = movies_df[movies_df["year"] == year].head(5)

            if not year_movies.empty:
                display_movies = year_movies[["rank", "title", "distributor", "gross"]].copy()

                display_movies.columns = ["Rank", "Title", "Distributor", "Box Office"]
                display_movies["Box Office"] = display_movies["Box Office"].apply(
                    lambda x: f"$ {pd.to_numeric(x, errors='coerce'):,.0f}"
                    if pd.notnull(pd.to_numeric(x, errors="coerce"))
                    else ""
                )
                display_movies = display_movies.set_index("Rank")
                st.table(display_movies)


            else:
                st.info(f"No movie data available for {year}")

        except Exception as e:
            st.error(f"Error loading movie data: {str(e)}")

    
    with colB:
        st.markdown('<div style="text-align: center;">Top 5 Hits</div>', unsafe_allow_html=True)
        
        try:
            music_df = load_music_data()
            year_music = music_df[music_df['year'] == year].head(5)
            
            if not year_music.empty:
                display_music = year_music[['rank', 'title', 'display_artist']].copy()
                display_music.columns = ['Rank', 'Song', 'Artist']
                
                display_music = display_music.set_index("Rank")
                st.table(display_music)
            else:
                st.info(f"No music data available for {year}")
                
        except Exception as e:
            st.error(f"Error loading music data: {str(e)}")
    try:
        awards_df = load_awards_data()
        best_film_row = awards_df[
            (awards_df["category"].str.lower() == "best film") &
            (awards_df["year"] == year)
        ]

        if not best_film_row.empty:
            best_film = best_film_row.iloc[0]["winner"]

            st.markdown(
                f"""
                <div class="award-card">
                  <div class="award-badge">🏆 Academy Awards Winner</div>
                  <div class="award-title">{best_film}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info(f"No best film award data available for {year}")

    except Exception as e:
        st.error(f"Error loading awards data: {str(e)}")
    try:
        albums_df = load_albums_us()
        year_albums = albums_df[albums_df["year"] == year].copy()

        if not year_albums.empty:
            
            winner = (
                year_albums
                .sort_values(["weeks_at_one", "rank"], ascending=[False, True])
                .iloc[0]
            )

            album_title = winner["album"]
            album_artist = winner["artist"]
            weeks = int(winner["weeks_at_one"])

            st.markdown(
                f"""
                <div class="award-card">
                <div class="award-badge">🎵 Album of the Year (US)</div>
                <div class="award-title">{album_title}</div>
                <div class="award-sub">{album_artist} • {weeks} week(s) at #1</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info(f"No US album data available for {year}")

    except Exception as e:
        st.error(f"Error loading albums data: {str(e)}")
    
    try : 
        if year in range(1990,2010) : 
            albums_global_df = load_albums_global()
            year_global = albums_global_df[albums_global_df["year"] == year].copy()

            if not year_global.empty:
                top_album = year_global[year_global["rank"] == 1].iloc[0]
                album_title = top_album["album"]
                album_artist = top_album["artist"]

                st.markdown(
                    f"""
                    <div class="award-card">
                    <div class="award-badge">🌍 Best Album Worldwide</div>
                    <div class="award-title">{album_title}</div>
                    <div class="award-sub">{album_artist}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    except Exception as e: 
        st.error(f"Error loading global albums data: {str(e)}")  
    st.markdown("")
    st.markdown('<div class="static-title">MAJOR WORLD EVENTS</div>',unsafe_allow_html=True)
    try : 
        events_df = load_events_data()
        year_events = (
        events_df[events_df["year"] == year]
        .sort_values("importance", ascending=False)
        )
        if year_events.empty:
            st.caption("No major world events available for this year.")

        else :
             top_n = st.slider(
                "Number of events to display",
                min_value=3,
                max_value=10,
                value=5,
                key=f"events_{year}"
             )

             for _, r in year_events.head(top_n).iterrows():
                st.markdown(f"**[{r['category'].title()}]** {r['event']}")
                st.progress(r["importance"] / events_df["importance"].max())
    except Exception as e :
        st.error(f"Error loading events data: {str(e)}")
else:
    st.caption("Navigate with arrows, then reveal your rewind.")


# STATIC SECTION
st.markdown(
    '<div class="static-title">BEST OF THE ERA</div>',
    unsafe_allow_html=True
)
st.caption("--Static Insights Across Time--",text_alignment="center")

try : 
    reign_df = load_analytics_longest_reigning()
    top_artist_df = load_analytics_top_artists() 
    top_weeks = reign_df[~reign_df['artist'].str.contains('Soundtrack', na=False)].sort_values("weeks_at_one", ascending=False).head(5).copy()
    top_hits = top_artist_df.sort_values("total_hits", ascending=False).head(5).copy()

    col1, col2 = st.columns(2 , gap="large")

    chart_weeks = (
        alt.Chart(top_weeks)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("artist:N", sort="-y",
                    axis=alt.Axis(labelAngle=-30, labelColor="#E0F7FF", title=None)),
            y=alt.Y("weeks_at_one:Q",
                    axis=alt.Axis(title="Weeks at #1", titleColor="#E0F7FF",
                                labelColor="#E0F7FF", grid=True,
                                gridColor="rgba(255,255,255,0.08)")),
            color=alt.value("#00FFFF"),
            tooltip=["artist:N", "weeks_at_one:Q"],
        )
        .properties(height=300)
        .configure(background="rgba(0, 0, 0, 0.45)")
    )

    chart_hits = (
        alt.Chart(top_hits)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X(
                "display_artist:N",
                sort="-y",
                axis=alt.Axis(labelAngle=-30, labelColor="#E0F7FF", title=None),
            ),
            y=alt.Y(
                "total_hits:Q",
                axis=alt.Axis(
                    title="Total Hits",
                    titleColor="#E0F7FF",
                    labelColor="#E0F7FF",
                    grid=True,
                    gridColor="rgba(255,255,255,0.08)",
                ),
            ),
            color=alt.value("#2FE6FF"),
            tooltip=["display_artist:N", "total_hits:Q"],
        )
        .properties(height=300)
        .configure(background="rgba(0, 0, 0, 0.45)")   
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("Longest Reign at #1")
        st.altair_chart(chart_weeks, use_container_width=True)

    with col2:
        st.subheader("Most Total Hits")
        st.altair_chart(chart_hits, use_container_width=True)
    
except Exception as e:
    st.error(f"Error building 'Who Ruled the Era' section: {str(e)}")   

st.markdown(
    '<div class="static-title">BOX OFFICE TOTAL</div>',
    unsafe_allow_html=True
)
st.caption("-- How Box Office Evolved Over Time --",text_alignment="center")
df_yearly_stats = load_analytics_yearly_stats()
df_yearly_stats = df_yearly_stats.sort_values("year")

frames_data = []
for i in range(2, len(df_yearly_stats) + 1):
    temp_df = df_yearly_stats.iloc[:i].copy()
    temp_df['frame'] = i - 1  # Frame identifier
    frames_data.append(temp_df)

df_animated = pd.concat(frames_data, ignore_index=True)

fig = px.line(
    df_animated,
    x='year',
    y='total_box_office',
    animation_frame='frame',
    range_x=[df_yearly_stats['year'].min(), df_yearly_stats['year'].max()],
    range_y=[0, df_yearly_stats['total_box_office'].max() * 1.1]
)

fig.update_traces(
    line=dict(color='#00FFFF', width=3),
    marker=dict(size=8, color='#00FFFF')
)

fig.update_layout(
    height=320,
    paper_bgcolor='rgba(0,0,0,0.45)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        title=None,
        tickfont=dict(color='#E0F7FF'),
        gridcolor='rgba(255,255,255,0.08)'
    ),
    yaxis=dict(
        title='Total Box Office',
        title_font=dict(color='#E0F7FF'),
        tickfont=dict(color='#E0F7FF'),
        gridcolor='rgba(255,255,255,0.08)'
    ),
    showlegend=False,
   
)
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 150  
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 100
st.plotly_chart(fig, use_container_width=True)

# TUX IN SPACE
st.markdown("")
st.markdown("")
st.markdown('<div style="text-align: center;">Bored? Help Tux destroy the Bill Gates army!</div>', unsafe_allow_html=True)
components.html(html, height=700, scrolling=False)
 
