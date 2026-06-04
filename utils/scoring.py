def compute_final_score(semantic, emotional, preference, runtime, popularity, rating):
    # Normalize components roughly and combine with weights
    # semantic: already in [-1,1] or [0,1]
    s = max(0.0, float(semantic))
    e = max(0.0, float(emotional))
    p = max(0.0, float(preference))
    r = max(0.0, float(runtime))
    # popularity and rating may be on different scales; scale them
    pop = min(1.0, float(popularity) / 100.0)
    rat = min(1.0, float(rating) / 10.0)

    final = 0.35 * s + 0.25 * (e / 3.0) + 0.20 * p + 0.10 * r + 0.05 * pop + 0.05 * rat
    return float(final)
