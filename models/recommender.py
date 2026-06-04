import ast
import numpy as np
from sklearn.preprocessing import normalize
from utils.scoring import compute_final_score


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

    def recommend(self, user_text, top_k=20, filters=None):
        filters = filters or {}
        # semantic candidates
        sem_results = self.semantic_model.semantic_search(user_text, top_k=top_k * 6)
        candidates = []
        for idx, sem_score in sem_results:
            try:
                row = self.movies.loc[idx]
            except Exception:
                continue
            # skip disliked genres from memory
            mem = self.memory.get()
            genres_list = row.get("genres_list") or []
            if isinstance(genres_list, str):
                try:
                    genres_list = ast.literal_eval(genres_list)
                except Exception:
                    genres_list = []
            if any(g in mem.get("disliked_genres", []) for g in genres_list):
                continue
            # apply user filters early
            if filters.get("genres"):
                if not any(g in filters.get("genres", []) for g in genres_list):
                    continue
            if filters.get("language"):
                if str(row.get("original_language")) != str(filters.get("language")):
                    continue
            if filters.get("min_rating"):
                try:
                    if float(row.get("vote_average") or 0) < float(filters.get("min_rating")):
                        continue
                except Exception:
                    pass
            # emotional fit: compare movie tags vs user inferred tags
            movie_tags = self._movie_emotional_profile(idx, top_k=5)
            user_tags = self.emotion_detector.infer(user_text, top_k=5)
            # emotional fit: overlap between user tags and movie tags weighted by scores
            user_tag_names = {t["tag"]: t["score"] for t in user_tags}
            emotional_fit = 0.0
            for mt in movie_tags:
                emotional_fit += user_tag_names.get(mt.get("tag"), 0.0) * float(mt.get("score", 0.0))
            # normalize emotional fit to [0,1]
            if movie_tags:
                emotional_fit = emotional_fit / (len(movie_tags) or 1)
            # preference match: genres, language, runtime
            pref_score = 0.0
            pref = self.memory.get()
            liked = pref.get("liked_genres", [])
            if liked and any(g in liked for g in row.get("genres_list", [])):
                pref_score += 1.0
            if row.get("original_language") in pref.get("preferred_languages", []):
                pref_score += 0.5

            # runtime suitability: check filters or memory
            runtime_score = 0.0
            rt = _safe_float(row.get("runtime"))
            if filters.get("max_runtime") and rt and rt <= filters["max_runtime"]:
                runtime_score = 1.0
            elif not filters.get("max_runtime"):
                runtime_score = 0.5

            popularity = _safe_float(row.get("popularity"))
            rating = _safe_float(row.get("vote_average"))

            final = compute_final_score(semantic=sem_score, emotional=emotional_fit, preference=pref_score, runtime=runtime_score, popularity=popularity, rating=rating)

            explanation = self._explain(row, user_text, movie_tags)

            candidates.append({"movie_idx": idx, "score": final, "explanation": explanation, "row": row})

        # sort and diversify: pick top by score but avoid same genre repeats
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

    def _explain(self, row, user_text, movie_tags):
        reasons = []
        # example heuristic-based explanation
        reasons.append(f"Semantic match to your description")
        if movie_tags:
            tag_list = ", ".join([t["tag"] for t in movie_tags[:3]])
            reasons.append(f"Emotional profile: {tag_list}")
        if row.get("vote_average"):
            reasons.append(f"Strong rating: {row.get('vote_average')}")
        if row.get("runtime"):
            reasons.append(f"Runtime: {int(row.get('runtime'))} min")
        return "; ".join(reasons)
