import os
import streamlit as st
from pathlib import Path
import pandas as pd

from models.semantic_model import SemanticModel
from models.emotion_detector import EmotionDetector
from models.recommender import Recommender
from models.conversation_memory import ConversationMemory
from utils.preprocessing import load_and_merge


@st.cache_resource
def load_movies():
    base = Path.cwd()
    movies_csv = base / "data" / "tmdb_5000_movies.csv"
    credits_csv = base / "data" / "tmdb_5000_credits.csv"
    df = load_and_merge(str(movies_csv), str(credits_csv))
    return df


@st.cache_resource
def init_models():
    sem = SemanticModel()
    movies = load_movies()
    sem.build_movie_embeddings(movies)
    emb = sem
    ed = EmotionDetector(sem)
    mem = ConversationMemory()
    rec = Recommender(sem, ed, movies, mem)
    return rec, ed, mem


def poster_url(path):
    if not path or pd.isna(path):
        return None
    return f"https://image.tmdb.org/t/p/w300{path}"


def main():
    st.set_page_config(page_title="CineMood AI", layout="wide", initial_sidebar_state="collapsed")
    # basic dark-themed CSS
    st.markdown(
        "<style>body{background-color:#0b0f14;color:#e6eef6} .stApp { background-color:#0b0f14} .css-1d391kg{background-color:#0b0f14}</style>",
        unsafe_allow_html=True,
    )
    st.markdown("# 🎬 CineMood AI")
    st.markdown("Talk to me about your day — I will pick the perfect movie mood.")

    # Sidebar filters
    movies_df = load_movies()
    st.sidebar.header("Filters")
    max_runtime_opt = st.sidebar.selectbox("Runtime", ["Any", "Under 90 min", "Under 2 hrs"], index=0)
    if max_runtime_opt == "Under 90 min":
        max_runtime = 90
    elif max_runtime_opt == "Under 2 hrs":
        max_runtime = 120
    else:
        max_runtime = None

    all_genres = sorted({g for lst in movies_df.get("genres_list", []) for g in lst})
    genres = st.sidebar.multiselect("Genre", options=all_genres, default=[])
    languages = sorted(movies_df["original_language"].dropna().unique().tolist())
    lang = st.sidebar.selectbox("Language", ["Any"] + languages, index=0)
    min_rating = st.sidebar.slider("Min rating", 0.0, 10.0, 6.0, 0.1)
    vibe = st.sidebar.multiselect("Vibe (optional)", options=["Comforting", "Funny", "Thought-provoking", "Emotional", "Exciting", "Surprise me"], default=[])

    rec, ed, mem = init_models()

    if "history" not in st.session_state:
        st.session_state.history = []

    with st.form("chat"):
        user_text = st.text_area("Your message", height=100, placeholder="Tell me how your day went...")
        submitted = st.form_submit_button("Send")

    if submitted and user_text:
        st.session_state.history.append({"user": user_text})
        # infer emotions and update memory heuristically
        infer = ed.infer(user_text, top_k=3)
        # simple dislike detection
        if "hate" in user_text.lower():
            # placeholder; real parsing would extract actual genre names
            mem.update_from_inference({"disliked_genres": []})
        filters = {}
        if max_runtime:
            filters["max_runtime"] = max_runtime
        if genres:
            filters["genres"] = genres
        if lang and lang != "Any":
            filters["language"] = lang
        filters["min_rating"] = min_rating

        with st.spinner("Finding the best matches for your mood..."):
            recommendations = rec.recommend(user_text, top_k=12, filters=filters)
        st.session_state.history.append({"assistant": recommendations})

    # display recommendations if available
    if st.session_state.history:
        last = st.session_state.history[-1]
        if "assistant" in last:
            recs = last["assistant"]
            cols = st.columns(3)
            for i, r in enumerate(recs):
                col = cols[i % len(cols)]
                row = r["row"]
                title = row.get("title")
                poster = poster_url(row.get("poster_path"))
            with col:
                if poster:
                    st.image(poster, width=200)
                st.markdown(f"**{title}**")
                st.markdown(f"⭐ {row.get('vote_average', 'N/A')}  • ⏱ {int(row.get('runtime') or 0)} min")
                st.markdown(f"Genres: {', '.join(row.get('genres_list', [])[:3])}")
if __name__ == '__main__':
    main()
