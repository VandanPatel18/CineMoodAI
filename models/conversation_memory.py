import os
import json


class ConversationMemory:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "..", "data", "memory.json")
        self.path = os.path.abspath(self.path)
        self._data = {"liked_genres": [], "disliked_genres": [], "preferred_languages": [], "min_runtime": None, "max_runtime": None, "intensity_pref": None}
        self._load()

    def _load(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data.update(json.load(f))
        except Exception:
            pass

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def update_from_inference(self, inference):
        # inference: dict with keys like liked_genres, disliked_genres, preferred_languages, intensity
        for k, v in inference.items():
            if k in ("liked_genres", "disliked_genres") and isinstance(v, list):
                for g in v:
                    if k == "liked_genres" and g not in self._data["liked_genres"]:
                        self._data["liked_genres"].append(g)
                    if k == "disliked_genres" and g not in self._data["disliked_genres"]:
                        self._data["disliked_genres"].append(g)
            elif k == "preferred_languages" and isinstance(v, list):
                for l in v:
                    if l not in self._data["preferred_languages"]:
                        self._data["preferred_languages"].append(l)
            else:
                self._data[k] = v
        self.save()

    def get(self):
        return self._data
