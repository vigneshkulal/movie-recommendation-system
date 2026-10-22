import base64
import os
import pandas as pd
import streamlit as st
from recommender import load

st.set_page_config(page_title="Movie Recommendation System", layout="centered")

def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #ffffff;
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #ffffff !important;
            text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9);
            margin-bottom: 1.5rem !important;
        }}
        /* Label styling: bright white font */
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] p,
        .stSelectbox label,
        .stSelectbox label * {{
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.9) !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
        }}
        [data-testid="stMarkdownContainer"] p {{
            color: #ffffff !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.9);
        }}
        [data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"] {{
            color: #e0e0e0 !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.9);
        }}
        /* Selectbox styling: solid white box, black text inside */
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] div {{
            background-color: #ffffff !important;
            background: #ffffff !important;
            border-color: #cccccc !important;
            border-radius: 8px !important;
        }}
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div,
        div[data-baseweb="select"] p {{
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
            text-shadow: none !important;
            font-weight: 500 !important;
        }}
        /* Faded example placeholder font */
        div[data-baseweb="select"] input::placeholder,
        div[data-baseweb="select"] div[aria-hidden="true"],
        div[data-baseweb="select"] span[aria-hidden="true"] {{
            color: #888888 !important;
            -webkit-text-fill-color: #888888 !important;
            font-style: italic !important;
            font-weight: 400 !important;
        }}
        div[data-baseweb="select"] svg {{
            fill: #000000 !important;
            color: #000000 !important;
        }}
        div[data-baseweb="popover"] ul,
        div[data-baseweb="menu"],
        ul[role="listbox"] {{
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid #dcdcdc !important;
        }}
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] li *,
        li[role="option"],
        li[role="option"] * {{
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
            text-shadow: none !important;
            background-color: #ffffff !important;
        }}
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] li:hover *,
        li[role="option"]:hover,
        li[role="option"]:hover * {{
            background-color: #f0f0f0 !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }}
        /* Button styling: inside white, font black */
        .stButton > button,
        button[kind="secondary"],
        button[data-testid="baseButton-secondary"] {{
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #cccccc !important;
            font-weight: 500 !important;
            text-shadow: none !important;
            transition: background-color 0.2s ease;
        }}
        .stButton > button:hover,
        button[kind="secondary"]:hover,
        button[data-testid="baseButton-secondary"]:hover {{
            background-color: #f0f0f0 !important;
            color: #000000 !important;
            border-color: #999999 !important;
        }}
        .stButton > button * {{
            color: #000000 !important;
            text-shadow: none !important;
        }}
        /* Movie suggestion card: clean white background box */
        .movie-card {{
            background-color: #ffffff !important;
            background: #ffffff !important;
            border-radius: 12px !important;
            padding: 10px 8px 12px 8px !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45) !important;
            border: 1px solid #e2e8f0 !important;
            display: flex !important;
            flex-direction: column !important;
            height: 100% !important;
            text-align: center !important;
            box-sizing: border-box !important;
        }}
        .movie-card,
        .movie-card * {{
            text-shadow: none !important;
        }}
        .movie-card .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            margin-bottom: 8px;
        }}
        .movie-card .badge-rank {{
            background-color: #111827 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            border-radius: 5px !important;
            padding: 2px 7px !important;
            line-height: 1.2 !important;
        }}
        .movie-card .badge-match {{
            background-color: #10b981 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            padding: 2px 8px !important;
            line-height: 1.2 !important;
        }}
        .movie-card .poster-placeholder {{
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 4px 8px 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 8px;
        }}
        .movie-card .photo-text {{
            font-size: 0.85rem !important;
            font-weight: 800 !important;
            color: #94a3b8 !important;
            -webkit-text-fill-color: #94a3b8 !important;
            letter-spacing: 2px !important;
            line-height: 1.1 !important;
            margin-top: 6px !important;
        }}
        .movie-card .coming-soon-text {{
            font-size: 0.62rem !important;
            font-weight: 700 !important;
            color: #94a3b8 !important;
            -webkit-text-fill-color: #94a3b8 !important;
            letter-spacing: 1.5px !important;
            margin-top: 2px !important;
        }}
        .movie-card .movie-title {{
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            font-size: 0.92rem !important;
            font-weight: 700 !important;
            line-height: 1.25 !important;
            margin-bottom: 4px !important;
            min-height: 2.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            word-break: break-word;
        }}
        .movie-card .movie-meta {{
            font-size: 0.78rem !important;
            color: #64748b !important;
            -webkit-text-fill-color: #64748b !important;
            margin-bottom: 6px !important;
        }}
        .movie-card .movie-meta .score-val {{
            color: #059669 !important;
            -webkit-text-fill-color: #059669 !important;
            font-weight: 600 !important;
        }}
        .movie-card .genres-wrap {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            justify-content: center;
            margin-bottom: 6px;
        }}
        .movie-card .genre-tag {{
            background-color: #1e293b !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-size: 0.65rem !important;
            font-weight: 600 !important;
            border-radius: 5px !important;
            padding: 2px 6px !important;
            line-height: 1.2 !important;
        }}
        .movie-card .movie-why {{
            color: #64748b !important;
            -webkit-text-fill-color: #64748b !important;
            font-size: 0.68rem !important;
            line-height: 1.35 !important;
            margin-top: auto !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

bg_path = os.path.join(os.path.dirname(__file__), "background.jpg")
if os.path.exists(bg_path):
    set_background(bg_path)


@st.cache_resource
def get_model():
    return load("movies.csv")


rec = get_model()

st.markdown("<h1 style='text-align:center'>Movie Recommendation System</h1>", unsafe_allow_html=True)

choice = st.selectbox("Type or select a movie you like:", rec.titles(), index=None, placeholder="ex. Space Journey")

if st.button("Show Recommendation"):
    if not choice:
        st.warning("Please enter a movie title.")
    else:
        res = rec.recommend(choice)
        if res["status"] != "ok":
            st.warning(res["message"])
        else:
            st.markdown(f"<p style='text-align:center; font-size:1.1rem; font-weight:600; margin-bottom:1.5rem; text-shadow:0 2px 4px rgba(0,0,0,0.8);'>{res['message']}</p>", unsafe_allow_html=True)
            cols = st.columns(len(res["results"]))
            for col, (_, row) in zip(cols, res["results"].iterrows()):
                m = rec.df[rec.df["label"] == row["title"]]
                if m.empty:
                    m = rec.df[rec.df["title"] == row["title"]]
                year_str = ""
                genres_list = []
                if not m.empty:
                    y = m.iloc[0].get("year")
                    if pd.notna(y):
                        try:
                            year_str = str(int(y))
                        except Exception:
                            year_str = str(y)
                    raw_g = m.iloc[0].get("genres")
                    if pd.notna(raw_g) and str(raw_g).strip():
                        genres_list = [g.strip() for g in str(raw_g).split(",") if g.strip()]

                score_val = float(row["score"])
                match_pct = max(50, min(98, int(round(49 + score_val * 100))))

                genre_tags_html = "".join(f'<span class="genre-tag">{g}</span>' for g in genres_list)
                year_display = f"{year_str} &nbsp;" if year_str else ""

                card_html = f"""
                <div class="movie-card">
                    <div class="card-header">
                        <span class="badge-rank">#{row['rank']}</span>
                        <span class="badge-match">{match_pct}% Match</span>
                    </div>
                    <div class="poster-placeholder">
                        <svg width="76" height="48" viewBox="0 0 140 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="140" height="90" rx="10" fill="#dbe1e8"/>
                            <circle cx="108" cy="30" r="10" fill="#9ca3af"/>
                            <path d="M 0 90 L 0 65 C 20 48, 45 68, 70 52 C 95 38, 115 58, 140 46 L 140 90 Z" fill="#ffffff"/>
                            <rect width="140" height="90" rx="10" stroke="#cbd5e1" stroke-width="2"/>
                        </svg>
                        <div class="photo-text">PHOTO</div>
                        <div class="coming-soon-text">COMING SOON</div>
                    </div>
                    <div class="movie-title">{row['title']}</div>
                    <div class="movie-meta">{year_display}<span class="score-val">Score: {row['score']}</span></div>
                    <div class="genres-wrap">{genre_tags_html}</div>
                    <div class="movie-why">{row['why']}</div>
                </div>
                """
                with col:
                    st.markdown(card_html, unsafe_allow_html=True)
