import os
import csv
import pandas as pd
import ast


_MOVIE_CSV_OPTS = {
    "engine": "python",
    "quotechar": '"',
    "doublequote": True,
    "escapechar": "\\",
    "quoting": csv.QUOTE_MINIMAL,
}

_CREDITS_CSV_OPTS = {
    "engine": "python",
    "quotechar": '"',
    "doublequote": True,
    "quoting": csv.QUOTE_MINIMAL,
}

_LANGUAGE_LABELS = {
    "en": "English",
    "hi": "Hindi",
    "ko": "Korean",
    "ja": "Japanese",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "kn": "Kannada",
    "mr": "Marathi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "it": "Italian",
    "zh": "Chinese",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "id": "Indonesian",
    "th": "Thai",
    "vi": "Vietnamese",
    "tr": "Turkish",
    "fa": "Persian",
    "ur": "Urdu",
}

# Popular languages shown first in filters when present in the dataset.
_LANGUAGE_PRIORITY = (
    "en", "hi", "ta", "te", "ml", "kn", "mr", "bn", "pa", "gu",
    "ko", "ja", "zh", "fr", "es", "de", "it", "pt", "ar", "ru", "id", "th", "vi", "tr", "fa", "ur",
)


def _read_movies_csv(path):
    return pd.read_csv(path, **_MOVIE_CSV_OPTS)


def _read_credits_csv(path):
    return pd.read_csv(path, **_CREDITS_CSV_OPTS)


def parse_list_column(x):
    try:
        if pd.isna(x):
            return []
        if isinstance(x, list):
            return x
        if isinstance(x, str) and x.strip().startswith("["):
            parsed = ast.literal_eval(x)
            if isinstance(parsed, list):
                out = []
                for el in parsed:
                    if isinstance(el, dict) and "name" in el:
                        out.append(el["name"])
                    else:
                        out.append(str(el))
                return out
        return []
    except Exception:
        return []


def extract_genre_options(df):
    genres = set()
    if "genres_list" in df.columns:
        for lst in df["genres_list"]:
            if isinstance(lst, list):
                genres.update(g for g in lst if g)
    if not genres and "genres" in df.columns:
        for raw in df["genres"].dropna():
            genres.update(parse_list_column(raw))
    return sorted(genres)


def extract_language_options(df):
    if "original_language" not in df.columns:
        return []
    codes = []
    for value in df["original_language"].dropna().unique():
        code = str(value).strip().lower()
        if not code or code == "nan":
            continue
        try:
            float(code)
            continue
        except ValueError:
            pass
        if len(code) <= 5 and code.replace("-", "").isalpha():
            codes.append(code)
    unique = sorted(set(codes))
    priority = {code: idx for idx, code in enumerate(_LANGUAGE_PRIORITY)}
    return sorted(unique, key=lambda c: (priority.get(c, len(_LANGUAGE_PRIORITY)), c))


def language_label(code):
    if not code or code == "Any":
        return "Any"
    key = str(code).strip().lower()
    name = _LANGUAGE_LABELS.get(key)
    return f"{name} ({key.upper()})" if name else key.upper()


def load_and_merge(tmdb_movies_path, tmdb_credits_path=None):
    movies = _read_movies_csv(tmdb_movies_path)

    if tmdb_credits_path and os.path.isfile(tmdb_credits_path):
        credits = _read_credits_csv(tmdb_credits_path)
        if "movie_id" in credits.columns:
            credits = credits.rename(columns={"movie_id": "id"})
        if "id" not in credits.columns:
            raise ValueError("Credits file must contain 'id' or 'movie_id' column")
        movies["id"] = movies["id"].astype(str)
        credits["id"] = credits["id"].astype(str)
        merged = movies.merge(credits, on="id", how="left", suffixes=("", "_credits"))
    else:
        merged = movies.copy()

    merged["id"] = merged["id"].astype(str)
    merged["genres_list"] = merged.get("genres").apply(parse_list_column)
    merged["keywords_list"] = merged.get("keywords").apply(parse_list_column)
    merged["cast_list"] = merged.get("cast").apply(parse_list_column)
    merged["crew_list"] = merged.get("crew").apply(parse_list_column)
    merged["cast_names"] = merged["cast_list"].apply(
        lambda lst: [el.get("name") if isinstance(el, dict) else str(el) for el in lst][:5]
    )
    merged["crew_names"] = merged["crew_list"].apply(
        lambda lst: [el.get("name") if isinstance(el, dict) else str(el) for el in lst][:5]
    )
    merged["vote_average"] = pd.to_numeric(merged.get("vote_average"), errors="coerce")
    merged["popularity"] = pd.to_numeric(merged.get("popularity"), errors="coerce")
    merged["runtime"] = pd.to_numeric(merged.get("runtime"), errors="coerce")
    if "original_language" in merged.columns:
        merged["original_language"] = merged["original_language"].astype(str).str.strip().str.lower()
    merged["release_year"] = merged.get("release_date").astype(str).str[:4]

    def make_semantic_text(r):
        parts = [str(r.get("title", "")), str(r.get("overview", ""))]
        parts += r.get("genres_list", [])[:3]
        parts += r.get("keywords_list", [])[:5]
        parts += r.get("cast_names", [])[:5]
        parts += r.get("crew_names", [])[:5]
        return " ".join([p for p in parts if p])

    merged["semantic_text"] = merged.apply(make_semantic_text, axis=1)
    merged = merged.set_index("id")
    return merged
