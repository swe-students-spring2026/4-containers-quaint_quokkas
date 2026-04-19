"""Rate a transcript based on filler-word usage."""

import re

# Weight reflects how strongly the word is a filler word.
# "um"/"uh" are pretty much always fillers; "like"/"so" sometimes aren't
FILLER_WORDS = {
    "um": 1.0,
    "uh": 1.0,
    "er": 1.0,
    "ah": 1.0,
    "hmm": 0.8,
    "you know": 0.9,
    "i mean": 0.8,
    "sort of": 0.6,
    "kind of": 0.6,
    "like": 0.5,
    "basically": 0.5,
    "literally": 0.5,
    "actually": 0.4,
    "honestly": 0.4,
    "right": 0.3,
    "so": 0.2,
}


def count_fillers(transcript):
    """Return {filler: count} for every filler word that appears."""
    text = transcript.lower()
    counts = {}
    for filler in FILLER_WORDS:
        pattern = r"\b" + re.escape(filler) + r"\b"
        hits = re.findall(pattern, text)
        if hits:
            counts[filler] = len(hits)
    return counts


def rate_transcript(transcript):
    """Produce a filler-word report for a transcript."""
    counts = count_fillers(transcript)
    total_words = len(transcript.split())
    weighted_score = sum(
        count * FILLER_WORDS[filler] for filler, count in counts.items()
    )
    rate = (weighted_score / total_words * 100) if total_words else 0.0

    if rate < 2:
        rating = "excellent"
    elif rate < 4:
        rating = "good"
    elif rate < 7:
        rating = "fair"
    else:
        rating = "poor"

    return {
        "total_words": total_words,
        "filler_counts": counts,
        "filler_score": round(weighted_score, 2),
        "filler_rate_per_100_words": round(rate, 2),
        "rating": rating,
    }
