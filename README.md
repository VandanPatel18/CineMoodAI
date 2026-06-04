# CineMood AI

CineMood AI is an intelligent conversational semantic mood-based explainable movie recommendation system.

Overview
- Conversational AI that infers mood, emotion, energy and intent from free text.
- Hybrid recommendation combining semantic similarity, emotional fit, user preferences, runtime and popularity.

Quick start
1. Create and activate a Python environment (recommended Python 3.10+)
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the Streamlit UI:

```
streamlit run ui/streamlit_app.py
```

Data
- Place `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` in the `data/` folder.

Notes
- Embeddings are cached to speed up subsequent runs.
- This repository provides a production-ready architecture skeleton. You can extend the emotion seeds and UI styling as needed.

Notes on development
- Embeddings are saved to `data/embeddings.npz` to avoid recomputing.
- Expand `models/emotion_detector.py` seeds for richer mood inference.

