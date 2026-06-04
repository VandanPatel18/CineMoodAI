import ast
import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize
from cinemood_utils.scoring import compute_final_score


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, str):
            cleaned = value.strip().replace(",", "")
            return float(cleaned) if cleaned else default
        return float(value)
    except Exception:
        return default


VIBE_TO_MOOD = {
    "Comforting": "comforting",
    "Funny": "funny",
    "Thought-provoking": "mind-bending",
    "Emotional": "emotional",
    "Exciting": "thrilling",
    "Surprise me": "mind-bending",
}


class Recommender:
    def __init__(self, semantic_model, emotion_detector, movies_df, memory):
        self.semantic_model = semantic_model
        self.emotion_detector = emotion_detector
        self.movies = movies_df
        self.memory = memory

    def _movie_emotional_profile(self, movie_idx, top_k=3):
        # infer tags for a movie by passing its semantic text through emotion detector
        text = self.movies.loc[movie_idx, "semantic_text"]
        tags = self.emotion_detector.infer(text, top_k=top_k)
        return tags

    def _passes_filters(self, row, genres_list, filters):
        if filters.get("genres"):
            if not any(g in filters["genres"] for g in genres_list):
                return False
        if filters.get("language"):
            if str(self._cell(row, "original_language", "")) != str(filters.get("language")):
                return False
        if filters.get("min_rating"):
            if _safe_float(self._cell(row, "vote_average")) < float(filters.get("min_rating")):
                return False
        if filters.get("max_runtime"):
            rt = _safe_float(self._cell(row, "runtime"))
            if rt and rt > filters["max_runtime"]:
                return False
        return True

    def _cell(self, row, key, default=None):
        value = row.get(key, default)
        if isinstance(value, pd.Series):
            value = value.iloc[0]
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return value

    def _normalize_genres(self, row):
        genres_list = self._cell(row, "genres_list", [])
        if isinstance(genres_list, str):
            try:
                genres_list = ast.literal_eval(genres_list)
            except Exception:
                genres_list = []
        return genres_list if isinstance(genres_list, list) else []

    def _vibe_boost(self, movie_tags, filters):
        requested = filters.get("vibe") or []
        if not requested or "Surprise me" in requested:
            return 0.0
        wanted = {VIBE_TO_MOOD.get(v, v.lower()) for v in requested}
        boost = 0.0
        for tag in movie_tags:
            if tag.get("tag") in wanted:
                boost += float(tag.get("score", 0.0))
        return boost / max(len(wanted), 1)

    def recommend(self, user_text, top_k=20, filters=None):
        filters = filters or {}
        mem = self.memory.get()
        sem_results = self.semantic_model.semantic_search(user_text, top_k=top_k * 8)
        seen = set()
        candidates = []

        def score_row(idx, sem_score):
            try:
                row = self.movies.loc[idx]
            except Exception:
                return None
            genres_list = self._normalize_genres(row)
            if any(g in mem.get("disliked_genres", []) for g in genres_list):
                return None
            if not self._passes_filters(row, genres_list, filters):
                return None

            movie_tags = self._movie_emotional_profile(idx, top_k=5)
            user_tags = self.emotion_detector.infer(user_text, top_k=5)
            user_tag_names = {t["tag"]: t["score"] for t in user_tags}
            emotional_fit = 0.0
            for mt in movie_tags:
                emotional_fit += user_tag_names.get(mt.get("tag"), 0.0) * float(mt.get("score", 0.0))
            if movie_tags:
                emotional_fit = emotional_fit / len(movie_tags)
            emotional_fit += self._vibe_boost(movie_tags, filters)

            pref_score = 0.0
            liked = mem.get("liked_genres", [])
            if liked and any(g in liked for g in genres_list):
                pref_score += 1.0
            if self._cell(row, "original_language") in mem.get("preferred_languages", []):
                pref_score += 0.5
            if filters.get("genres") and any(g in filters["genres"] for g in genres_list):
                pref_score += 0.75

            runtime_score = 0.0
            rt = _safe_float(self._cell(row, "runtime"))
            if filters.get("max_runtime") and rt and rt <= filters["max_runtime"]:
                runtime_score = 1.0
            elif not filters.get("max_runtime"):
                runtime_score = 0.5
            elif filters.get("max_runtime") and not rt:
                runtime_score = 0.35

            popularity = _safe_float(self._cell(row, "popularity"))
            rating = _safe_float(self._cell(row, "vote_average"))
            final = compute_final_score(
                semantic=sem_score,
                emotional=emotional_fit,
                preference=pref_score,
                runtime=runtime_score,
                popularity=popularity,
                rating=rating,
            )
            explanation = self._explain(row, user_text, movie_tags, filters)
            return {"movie_idx": idx, "score": final, "explanation": explanation, "row": row}

        for idx, sem_score in sem_results:
            seen.add(idx)
            item = score_row(idx, sem_score)
            if item:
                candidates.append(item)

        # If sidebar filters are strict, fill from the full catalog that matches demand.
        if len(candidates) < top_k and any(filters.get(k) for k in ("genres", "language", "max_runtime", "vibe")):
            for idx in self.movies.index:
                if idx in seen:
                    continue
                item = score_row(idx, 0.35)
                if item:
                    candidates.append(item)
                if len(candidates) >= top_k * 4:
                    break

        candidates = sorted(candidates, key=lambda x: -x["score"])[:top_k * 3]
        selected = []
        genres_seen = set()
        for c in candidates:
            gset = tuple(c["row"].get("genres_list", [])[:2])
            if len(selected) >= top_k:
                break
            # diversity: prefer new genre packs
            if any(g in genres_seen for g in gset):
                # allow occasional repeats (lower chance)
                if np.random.rand() < 0.2:
                    selected.append(c)
                    genres_seen.update(gset)
            else:
                selected.append(c)
                genres_seen.update(gset)

        return selected

    def _explain(self, row, user_text, movie_tags, filters=None):
        filters = filters or {}
        reasons = []
        genres = self._normalize_genres(row)
        if filters.get("genres") and any(g in filters["genres"] for g in genres):
            matched = [g for g in genres if g in filters["genres"]]
            reasons.append(f"Matches your genre pick: {', '.join(matched[:2])}")
        else:
            reasons.append("Semantic match to your description")
        if filters.get("language"):
            reasons.append(f"Language: {str(self._cell(row, 'original_language', '')).upper()}")
        if movie_tags:
            tag_list = ", ".join([t["tag"] for t in movie_tags[:3]])
            reasons.append(f"Mood: {tag_list}")
        vote = self._cell(row, "vote_average")
        if vote is not None:
            reasons.append(f"Rating: {float(vote):.1f}")
        runtime = self._cell(row, "runtime")
        if runtime:
            reasons.append(f"Runtime: {int(float(runtime))} min")
        return "; ".join(reasons)
