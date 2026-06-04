import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize


class SemanticModel:
    def __init__(self, model_name="all-MiniLM-L6-v2", cache_path=None):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        # default to project data folder so embeddings persist between runs
        default_cache = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "embeddings.npz"))
        self.cache_path = cache_path or default_cache
        self.movie_embeddings = None
        self.movie_ids = None

    def build_movie_embeddings(self, movies_df, text_column="semantic_text", force=False):
        if os.path.exists(self.cache_path) and not force:
            try:
                d = np.load(self.cache_path, allow_pickle=True)
                self.movie_embeddings = d["embeddings"]
                self.movie_ids = d["ids"].tolist()
                return
            except Exception:
                pass

        texts = movies_df[text_column].fillna("").tolist()
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        embeddings = normalize(embeddings)
        self.movie_embeddings = embeddings
        self.movie_ids = movies_df.index.tolist()
        # ensure directory exists
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        np.savez(self.cache_path, embeddings=self.movie_embeddings, ids=np.array(self.movie_ids, dtype=object))

    def embed_text(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        emb = self.model.encode(texts, convert_to_numpy=True)
        return normalize(emb)

    def semantic_search(self, query, top_k=20):
        if self.movie_embeddings is None:
            raise RuntimeError("Movie embeddings not built")
        q_emb = self.embed_text(query)[0]
        scores = np.dot(self.movie_embeddings, q_emb)
        idx = np.argsort(-scores)[:top_k]
        results = [(self.movie_ids[i], float(scores[i])) for i in idx]
        return results

import pandas as pd
import ast
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticMovieRecommender:
    def __init__(self, movie_path, credits_path):
        print("Loading dataset...")

        self.movies = pd.read_csv(movie_path)
        self.credits = pd.read_csv(credits_path)

        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.prepare_data()

    def convert_json_column(self, text):
        try:
            items = ast.literal_eval(text)
            return [item['name'] for item in items]
        except:
            return []

    def prepare_data(self):
        print("Cleaning movie data...")

        self.movies['genres'] = self.movies['genres'].apply(
            self.convert_json_column
        )

        self.movies['keywords'] = self.movies['keywords'].apply(
            self.convert_json_column
        )

        self.movies['combined_features'] = (
            self.movies['overview'].fillna('') + " " +
            self.movies['genres'].astype(str) + " " +
            self.movies['keywords'].astype(str)
        )

        print("Creating semantic embeddings...")

        self.embeddings = self.model.encode(
            self.movies['combined_features'].tolist(),
            show_progress_bar=True
        )

        print("Semantic model ready!")

    def recommend_movies(self, user_text, top_n=10):

        print("\nAnalyzing user intent...")

        user_embedding = self.model.encode([user_text])

        similarity_scores = cosine_similarity(
            user_embedding,
            self.embeddings
        )[0]

        top_indices = similarity_scores.argsort()[-top_n:][::-1]

        recommendations = []

        for idx in top_indices:

            movie = self.movies.iloc[idx]

            recommendations.append({
                'title': movie['title'],
                'rating': movie['vote_average'],
                'overview': movie['overview']
            })

        return recommendations
    

