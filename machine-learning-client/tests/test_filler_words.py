"""Tests for filler word analysis."""

from filler_words import count_fillers, rate_transcript


def test_count_fillers_basic():
    """Common fillers are each counted once."""
    counts = count_fillers("um I uh think so")
    assert counts["um"] == 1
    assert counts["uh"] == 1
    assert counts["so"] == 1


def test_count_fillers_case_insensitive():
    """Matching ignores case."""
    assert count_fillers("UM uh Um")["um"] == 2


def test_count_fillers_whole_words_only():
    """Filler tokens don't match inside other words."""
    # "like" should not match "unlike" or "liked"
    assert "like" not in count_fillers("I unlike liked that")


def test_count_fillers_multiword():
    """Multi-word fillers like 'you know' are detected."""
    assert count_fillers("you know, I mean it")["you know"] == 1
    assert count_fillers("you know, I mean it")["i mean"] == 1


def test_count_fillers_empty():
    """Empty input yields no counts."""
    assert not count_fillers("")


def test_rate_transcript_clean_speech():
    """Speech with no fillers gets the top rating."""
    result = rate_transcript("The quick brown fox jumps over the lazy dog today")
    assert not result["filler_counts"]
    assert result["rating"] == "excellent"


def test_rate_transcript_filler_heavy():
    """Speech packed with fillers gets the worst rating."""
    text = "um uh um uh like so you know I mean basically"
    result = rate_transcript(text)
    assert result["rating"] == "poor"
    assert result["filler_rate_per_100_words"] > 7


def test_rate_transcript_empty():
    """Empty transcript produces zeroed-out metrics."""
    result = rate_transcript("")
    assert result["total_words"] == 0
    assert result["filler_rate_per_100_words"] == 0.0


def test_rate_transcript_structure():
    """The report dict has exactly the expected keys."""
    result = rate_transcript("um hello world")
    assert set(result.keys()) == {
        "total_words",
        "filler_counts",
        "filler_score",
        "filler_rate_per_100_words",
        "rating",
    }
