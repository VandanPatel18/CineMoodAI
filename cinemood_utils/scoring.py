def _num(value, default=0.0):
    try:
        if value is None or (isinstance(value, float) and value != value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_final_score(semantic, emotional, preference, runtime, popularity, rating):
    # Normalize components roughly and combine with weights
    # semantic: already in [-1,1] or [0,1]
    s = max(0.0, _num(semantic))
    e = max(0.0, _num(emotional))
    p = max(0.0, _num(preference))
    r = max(0.0, _num(runtime))
    # popularity and rating may be on different scales; scale them
    pop = min(1.0, _num(popularity) / 100.0)
    rat = min(1.0, _num(rating) / 10.0)

    final = 0.35 * s + 0.25 * (e / 3.0) + 0.20 * p + 0.10 * r + 0.05 * pop + 0.05 * rat
    return float(final)
