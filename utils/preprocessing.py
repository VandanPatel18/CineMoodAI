import os
import pandas as pd
import ast


def load_and_merge(tmdb_movies_path, tmdb_credits_path):
    movies = pd.read_csv(tmdb_movies_path)
    credits = pd.read_csv(tmdb_credits_path)
    # merge on title/Id: credits has movie_id and title
    # credits file uses movie_id; align to movies 'id'
    if "movie_id" in credits.columns:
        credits = credits.rename(columns={"movie_id": "id"})
    merged = movies.merge(credits, on="id", how="left", suffixes=("", "_credits"))
    # parse genres and keywords if stored as stringified lists
    def parse_list_column(x):
        try:
            if pd.isna(x):
                return []
            if isinstance(x, list):
                return x
            if isinstance(x, str) and x.strip().startswith("["):
                parsed = ast.literal_eval(x)
                if isinstance(parsed, list):
                    # extract 'name' if dicts
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

    merged["genres_list"] = merged.get("genres").apply(parse_list_column)
    merged["keywords_list"] = merged.get("keywords").apply(parse_list_column)
    # cast runtime, year
    merged["runtime"] = pd.to_numeric(merged.get("runtime"), errors="coerce")
    merged["release_year"] = merged.get("release_date").astype(str).str[:4]

    # combine semantic text
    def make_semantic_text(r):
        parts = [str(r.get("title", "")), str(r.get("overview", ""))]
        parts += r.get("genres_list", [])[:3]
        parts += r.get("keywords_list", [])[:5]
        parts += [str(r.get("cast", "")), str(r.get("crew", ""))]
        return " ".join([p for p in parts if p])

    merged["semantic_text"] = merged.apply(make_semantic_text, axis=1)
    merged = merged.set_index("id")
    return merged
