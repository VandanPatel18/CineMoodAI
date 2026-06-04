import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
from pathlib import Path
import pandas as pd

from models.semantic_model import SemanticModel
from models.emotion_detector import EmotionDetector
from models.recommender import Recommender
from models.conversation_memory import ConversationMemory
from cinemood_utils.preprocessing import (
    load_and_merge,
    extract_genre_options,
    extract_language_options,
    language_label,
    build_recommendation_query,
)

DATA_DIR = Path(ROOT) / "data"

PAGE_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 10% -10%, rgba(59,130,246,.22), transparent),
        radial-gradient(ellipse 60% 40% at 100% 0%, rgba(236,72,153,.18), transparent),
        radial-gradient(ellipse 50% 30% at 50% 100%, rgba(99,102,241,.12), transparent),
        #030712;
    color: #e8f1ff;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(12,22,42,.98), rgba(4,8,18,.99));
    border-right: 1px solid rgba(148,163,184,.08);
}
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h4 {
    color: #f1f5f9;
    letter-spacing: -0.02em;
}
.stButton>button {
    background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    width: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 8px 24px rgba(236,72,153,.25);
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 32px rgba(59,130,246,.35);
}
.stTextArea textarea {
    background: rgba(15,23,42,.92) !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(148,163,184,.2) !important;
    border-radius: 16px !important;
    font-size: 1rem !important;
}
div[data-baseweb="select"] > div,
div[data-baseweb="input"] {
    background: rgba(15,23,42,.9) !important;
    border-color: rgba(148,163,184,.18) !important;
    border-radius: 12px !important;
}
.hero {
    padding: 2rem 0 1.25rem;
    max-width: 720px;
}
.hero h1 {
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    margin: 0 0 0.5rem;
    background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p {
    color: #94a3b8;
    font-size: 1.08rem;
    line-height: 1.6;
    margin: 0;
}
.suggestion-block {
    background: rgba(15,23,42,.75);
    border: 1px solid rgba(148,163,184,.12);
    border-radius: 16px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
    color: #94a3b8;
    font-size: 0.95rem;
}
.suggestion-block strong { color: #e2e8f0; }
.chat-panel {
    background: rgba(10,18,35,.6);
    border: 1px solid rgba(148,163,184,.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
.chat-panel h3 {
    margin-top: 0;
    color: #f8fafc;
    font-size: 1.15rem;
}
.app-card {
    background: rgba(10,18,35,.88);
    border: 1px solid rgba(148,163,184,.12);
    border-radius: 20px;
    padding: 1.25rem;
    box-shadow: 0 16px 48px rgba(0,0,0,.2);
    margin-bottom: 1rem;
    height: 100%;
    transition: transform 0.2s, border-color 0.2s;
}
.app-card:hover {
    transform: translateY(-4px);
    border-color: rgba(236,72,153,.25);
}
.app-card h4 {
    color: #fff;
    margin: 0 0 0.5rem;
    font-size: 1.05rem;
}
.app-card .meta {
    color: #64748b;
    font-size: 0.88rem;
    margin-bottom: 0.75rem;
}
.app-card .badge {
    display: inline-block;
    margin-top: 0.5rem;
    padding: 4px 12px;
    border-radius: 999px;
    background: linear-gradient(135deg, rgba(236,72,153,.2), rgba(59,130,246,.2));
    color: #e2e8f0;
    font-size: 0.8rem;
    font-weight: 600;
}
.chat-bubble {
    background: rgba(15,23,42,.9);
    border: 1px solid rgba(148,163,184,.1);
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 10px;
    line-height: 1.5;
}
.chat-user { border-left: 3px solid #3b82f6; }
.chat-assistant { border-left: 3px solid #ec4899; }
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #64748b;
}
.empty-state h3 { color: #cbd5e1; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
"""


@st.cache_resource
def load_movies():
    movies_csv = DATA_DIR / "tmdb_5000_movies.csv"
    credits_csv = DATA_DIR / "tmdb_5000_credits.csv"
    credits_path = str(credits_csv) if credits_csv.is_file() else None
    return load_and_merge(str(movies_csv), credits_path)


@st.cache_resource
def init_models():
    sem = SemanticModel()
    movies = load_movies()
    sem.build_movie_embeddings(movies)
    ed = EmotionDetector(sem)
    mem = ConversationMemory()
    rec = Recommender(sem, ed, movies, mem)
    return rec, ed, mem


def poster_url(path):
    if not path or pd.isna(path):
        return None
    path = str(path)
    if path.startswith("http"):
        return path
    return f"https://image.tmdb.org/t/p/w300{path}"


def build_recommendation_card(movie, explanation, score):
    poster = poster_url(movie.get("poster_path"))
    title = movie.get("title", "Untitled")
    rating = movie.get("vote_average", "N/A")
    runtime = int(movie.get("runtime") or 0) if pd.notna(movie.get("runtime")) else 0
    genres = ", ".join(movie.get("genres_list", [])[:3])
    lang_code = movie.get("original_language", "")
    details = []
    if rating != "N/A" and pd.notna(rating):
        details.append(f"⭐ {float(rating):.1f}")
    if runtime:
        details.append(f"⏱ {runtime} min")
    if genres:
        details.append(f"🎭 {genres}")
    if lang_code:
        details.append(f"🌐 {language_label(lang_code)}")

    detail_line = " · ".join(details)
    poster_html = (
        f"<img src='{poster}' style='width:100px; border-radius:12px; object-fit:cover;'/>"
        if poster and "/sample" not in poster
        else "<div style='width:100px;height:140px;border-radius:12px;background:linear-gradient(135deg,#1e293b,#0f172a);display:flex;align-items:center;justify-content:center;font-size:2rem;'>🎬</div>"
    )

    return f"""
    <div class='app-card'>
        <div style='display:flex; gap:14px; align-items:flex-start;'>
            {poster_html}
            <div style='flex:1; min-width:0;'>
                <h4>{title}</h4>
                <div class='meta'>{detail_line}</div>
                <div style='color:#cbd5e1; font-size:0.9rem; line-height:1.55;'>{explanation}</div>
                <div class='badge'>Match {score:.0%}</div>
            </div>
        </div>
    </div>
    """


def main():
    st.set_page_config(page_title="CineMood AI", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    st.markdown(
        "<div class='hero'>"
        "<h1>🎬 CineMood AI</h1>"
        "<p>Describe your mood in plain English — I'll find films that fit how you feel right now.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='suggestion-block'><strong>Try:</strong> "
        "<em>cozy family drama with uplifting energy</em> · "
        "<em>dark sci-fi that still feels emotional</em></div>",
        unsafe_allow_html=True,
    )

    movies_df = load_movies()
    rec, ed, mem = init_models()

    with st.sidebar:
        st.markdown("### Your preferences")
        max_runtime_opt = st.selectbox("Runtime", ["Any", "Under 90 min", "Under 2 hrs"], index=0)
        if max_runtime_opt == "Under 90 min":
            max_runtime = 90
        elif max_runtime_opt == "Under 2 hrs":
            max_runtime = 120
        else:
            max_runtime = None

        all_genres = extract_genre_options(movies_df)
        genres = st.multiselect("Genres", options=all_genres, default=[], placeholder="Crime, Thriller, Drama…")
        languages = extract_language_options(movies_df)
        language_options = ["Any"] + languages
        lang = st.selectbox(
            "Language",
            language_options,
            index=0,
            format_func=language_label,
        )
        min_rating = st.slider("Minimum rating", 0.0, 10.0, 6.0, 0.5)
        vibes = st.multiselect(
            "Vibe",
            options=["Comforting", "Funny", "Thought-provoking", "Emotional", "Exciting", "Surprise me"],
            default=[],
            placeholder="Pick a mood",
        )

        active = []
        if genres:
            active.append(", ".join(genres[:3]) + ("…" if len(genres) > 3 else ""))
        if lang and lang != "Any":
            active.append(language_label(lang))
        if vibes:
            active.append(", ".join(vibes))
        if max_runtime:
            active.append(max_runtime_opt)
        if active:
            st.markdown("**Matching:**")
            for chip in active:
                st.markdown(f"<span style='display:inline-block;margin:2px 4px 2px 0;padding:4px 10px;border-radius:999px;background:rgba(59,130,246,.2);color:#cbd5e1;font-size:0.82rem;'>{chip}</span>", unsafe_allow_html=True)

        st.markdown("---")
        filter_submit = st.button("🎯 Recommend from sidebar", use_container_width=True, type="primary")
        st.caption("Uses your genre, language, vibe & rating picks — no typing required.")

    if "history" not in st.session_state:
        st.session_state.history = []

    def run_recommendations(user_text="", source="chat"):
        query = build_recommendation_query(user_text, genres=genres, vibes=vibes, language=lang)
        filters = {"min_rating": min_rating, "vibe": vibes}
        if max_runtime:
            filters["max_runtime"] = max_runtime
        if genres:
            filters["genres"] = genres
        if lang and lang != "Any":
            filters["language"] = lang

        label = user_text.strip() if user_text.strip() else f"Sidebar picks: {query[:120]}"
        st.session_state.history.append({"user": label, "source": source})

        with st.spinner("Finding films that match your demand…"):
            try:
                recommendations = rec.recommend(query, top_k=12, filters=filters)
            except Exception as exc:
                st.error(f"Something went wrong while scoring movies: {exc}")
                recommendations = []

        if not recommendations:
            st.warning("No matches for these filters — try fewer genres or lower the rating.")
        st.session_state.history.append({"assistant": recommendations})

    st.markdown("<div class='chat-panel'>", unsafe_allow_html=True)
    with st.form("chat", clear_on_submit=False):
        st.markdown("### What are you in the mood for?")
        user_text = st.text_area(
            "Your message",
            placeholder="e.g. I'm exhausted after work and want something warm but not boring…",
            height=120,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("✨ Get recommendations", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if filter_submit:
        run_recommendations(source="sidebar")

    if submitted:
        run_recommendations(user_text, source="chat")

    if st.session_state.history:
        last = st.session_state.history[-1]
        if "assistant" in last and last["assistant"]:
            st.markdown("## For you tonight")
            cols = st.columns(3)
            for idx, item in enumerate(last["assistant"]):
                with cols[idx % 3]:
                    st.markdown(
                        build_recommendation_card(item["row"], item["explanation"], item["score"]),
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown(
            "<div class='empty-state'>"
            "<h3>Ready when you are</h3>"
            "<p>Tell me how you're feeling or what kind of story you want.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.history:
        with st.expander("Conversation history", expanded=False):
            for entry in st.session_state.history:
                if "user" in entry:
                    st.markdown(
                        f"<div class='chat-bubble chat-user'><strong>You</strong><br>{entry['user']}</div>",
                        unsafe_allow_html=True,
                    )
                if "assistant" in entry:
                    n = len(entry["assistant"]) if entry["assistant"] else 0
                    msg = (
                        f"Found {n} mood-matched films."
                        if n
                        else "No strong matches — try broadening your request."
                    )
                    st.markdown(
                        f"<div class='chat-bubble chat-assistant'><strong>CineMood AI</strong><br>{msg}</div>",
                        unsafe_allow_html=True,
                    )


if __name__ == "__main__":
    main()
