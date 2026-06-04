import os
import sys
import streamlit as st
from pathlib import Path
import pandas as pd

# Ensure the project root (parent of `ui/`) is on sys.path so sibling packages import correctly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models.semantic_model import SemanticModel
from models.emotion_detector import EmotionDetector
from models.recommender import Recommender
from models.conversation_memory import ConversationMemory
from utils.preprocessing import load_and_merge


PAGE_STYLE = """
<style>
body {
    background: #060b12;
    color: #e8f1ff;
}
.reportview-container .main {
    background-color: #060b12;
}
.css-1d391kg {
    background-color: #060b12;
}
.stApp {
    background: #060b12;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%);
}
.css-1d391kg {
    background-color: #060b12;
}
.stButton>button {
    background-color: #ff4b4b;
    color: white;
    border: none;
}
.stButton>button:hover {
    background-color: #e43f3f;
}
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background-color: #0b1220;
    color: #e8f1ff;
    border: 1px solid #1f2937;
}
.stSlider>div>div>div>div {
    background: #1f2937;
}
.app-card {
    background: #0b1220;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 18px 50px rgba(0,0,0,.22);
    margin-bottom: 18px;
}
.app-card h4 {
    color: #ffffff;
}
.app-card .meta {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 12px;
}
.app-card .badge {
    display: inline-block;
    margin-right: 8px;
    margin-bottom: 8px;
    padding: 5px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,.08);
    color: #cbd5e1;
    font-size: 0.8rem;
}
</style>
"""


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
    ed = EmotionDetector(sem)
    mem = ConversationMemory()
    rec = Recommender(sem, ed, movies, mem)
    return rec, ed, mem


def poster_url(path):
    if not path or pd.isna(path):
        return None
    return f"https://image.tmdb.org/t/p/w300{path}"


def build_recommendation_card(movie, explanation, score):
    poster = poster_url(movie.get("poster_path"))
    title = movie.get("title", "Untitled")
    rating = movie.get("vote_average", "N/A")
    runtime = int(movie.get("runtime") or 0)
    genres = ", ".join(movie.get("genres_list", [])[:3])
    details = []
    if rating != "N/A":
        details.append(f"⭐ {rating}")
    if runtime:
        details.append(f"⏱ {runtime} min")
    if genres:
        details.append(f"🎭 {genres}")

    detail_line = " · ".join(details)

    card = f"""
    <div class='app-card'>
        <div style='display:flex; gap:16px;'>
            {f"<img src='{poster}' style='width:120px; border-radius:14px;'/>" if poster else ""}
            <div style='flex:1;'>
                <h4>{title}</h4>
                <div class='meta'>{detail_line}</div>
                <div style='color:#d1d5db; line-height:1.6; margin-bottom:12px;'>{explanation}</div>
                <div class='badge'>Score {score:.2f}</div>
            </div>
        </div>
    </div>
    """
    return card


def main():
    st.set_page_config(page_title="CineMood AI", layout="wide", initial_sidebar_state="expanded")
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    st.markdown("# 🎬 CineMood AI")
    st.markdown("## Conversational mood-based movie recommendations with semantic understanding")

    movies_df = load_movies()
    rec, ed, mem = init_models()

    with st.sidebar:
        st.subheader("Refine your watchlist")
        max_runtime_opt = st.selectbox("Runtime", ["Any", "Under 90 min", "Under 2 hrs"], index=0)
        if max_runtime_opt == "Under 90 min":
            max_runtime = 90
        elif max_runtime_opt == "Under 2 hrs":
            max_runtime = 120
        else:
            max_runtime = None

        all_genres = sorted({g for lst in movies_df.get("genres_list", []) for g in lst})
        genres = st.multiselect("Genres", options=all_genres, default=[])
        languages = sorted(movies_df["original_language"].dropna().unique().tolist())
        lang = st.selectbox("Language", ["Any"] + languages, index=0)
        min_rating = st.slider("Minimum rating", 0.0, 10.0, 6.0, 0.1)
        vibes = st.multiselect("Vibe", options=["Comforting", "Funny", "Thought-provoking", "Emotional", "Exciting", "Surprise me"], default=[])
        st.markdown("---")
        st.markdown("#### Deployment-ready details")
        st.markdown("- No API key is required for this app.\n- Data is loaded from the repo files directly.\n- If needed, the app will use the sample dataset on deploy.")

    if "history" not in st.session_state:
        st.session_state.history = []

    with st.form("chat"):
        st.markdown("### Tell me about your day")
        user_text = st.text_area("Type naturally — for example, 'I want something relaxing but not boring.'", height=140)
        submitted = st.form_submit_button("Generate recommendations")

    if submitted and user_text:
        st.session_state.history.append({"user": user_text})
        if "hate" in user_text.lower():
            mem.update_from_inference({"disliked_genres": []})

        filters = {}
        if max_runtime:
            filters["max_runtime"] = max_runtime
        if genres:
            filters["genres"] = genres
        if lang and lang != "Any":
            filters["language"] = lang
        filters["min_rating"] = min_rating
        filters["vibe"] = vibes

        with st.spinner("Analyzing mood and scoring movies..."):
            recommendations = rec.recommend(user_text, top_k=12, filters=filters)
        st.session_state.history.append({"assistant": recommendations})

    canvas = st.container()
    canvas.markdown("---")
    if st.session_state.history:
        last = st.session_state.history[-1]
        if "assistant" in last:
            recs = last["assistant"]
            st.markdown("## Recommended movies")
            card_columns = st.columns(3)
            for idx, item in enumerate(recs):
                col = card_columns[idx % 3]
                with col:
                    st.markdown(build_recommendation_card(item["row"], item["explanation"], item["score"]), unsafe_allow_html=True)
    else:
        st.markdown("### Ready when you are")
        st.markdown("Tell me how you're feeling or what kind of story you want, and I'll recommend mood-matched movies.")

    if st.session_state.history:
        chat_expander = st.expander("Conversation history")
        with chat_expander:
            for entry in st.session_state.history:
                if "user" in entry:
                    st.markdown(f"**You:** {entry['user']}")
                if "assistant" in entry:
                    st.markdown(f"**Recommendations returned:** {len(entry['assistant'])} movies")


if __name__ == '__main__':
    main()
