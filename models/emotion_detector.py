import os
import numpy as np

class EmotionDetector:
    """Lightweight semantic emotion/mood detector using seed phrases and embeddings."""

    def __init__(self, embedder, seeds=None):
        self.embedder = embedder
        # default seeds map to descriptive emotion/mood tags and energy/intensity
        self.seeds = seeds or {
            "comforting": ["comforting", "warm", "cozy", "soothing", "heartwarming"],
            "relaxing": ["relaxing", "calm", "laid-back", "easy to watch"],
            "funny": ["funny", "comedic", "hilarious", "light"],
            "mind-bending": ["mind-bending", "twisty", "complex", "surprising"],
            "thrilling": ["thrilling", "suspense", "edge of the seat", "intense"],
            "nostalgic": ["nostalgic", "sentimental", "retro", "nostalgia"],
            "uplifting": ["uplifting", "inspiring", "hopeful"],
            "emotional": ["emotional", "moving", "tearjerker", "touching"],
        }
        self._compile_seed_embeddings()

    def _compile_seed_embeddings(self):
        self.seed_keys = list(self.seeds.keys())
        phrases = [" ".join(self.seeds[k]) for k in self.seed_keys]
        self.seed_emb = self.embedder.embed_text(phrases)

    def infer(self, text, top_k=3):
        q = self.embedder.embed_text(text)[0]
        sims = np.dot(self.seed_emb, q)
        idx = np.argsort(-sims)[:top_k]
        results = []
        for i in idx:
            key = self.seed_keys[i]
            score = float(sims[i])
            # rough energy/intensity heuristic
            energy = "low"
            if key in ("mind-bending", "thrilling"):
                energy = "high"
            elif key in ("funny", "uplifting"):
                energy = "medium"
            results.append({"tag": key, "score": score, "energy": energy})
        return results
