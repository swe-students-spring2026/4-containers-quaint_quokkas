"""Tests for filler word analysis."""
from filler_words import count_fillers, rate_transcript


def test_count_fillers_basic():
    counts = count_fillers("um I uh think so")
    assert counts["um"] == 1
    assert counts["uh"] == 1
    assert counts["so"] == 1


def test_count_fillers_case_insensitive():
    assert count_fillers("UM uh Um")["um"] == 2


def test_count_fillers_whole_words_only():
    # "like" should not match "unlike" or "liked"
    assert "like" not in count_fillers("I unlike liked that")


def test_count_fillers_multiword():
    assert count_fillers("you know, I mean it")["you know"] == 1
    assert count_fillers("you know, I mean it")["i mean"] == 1


def test_count_fillers_empty():
    assert count_fillers("") == {}


def test_rate_transcript_clean_speech():
    result = rate_transcript("The quick brown fox jumps over the lazy dog today")
    assert result["filler_counts"] == {}
    assert result["rating"] == "excellent"


def test_rate_transcript_filler_heavy():
    text = "um uh um uh like so you know I mean basically"
    result = rate_transcript(text)
    assert result["rating"] == "poor"
    assert result["filler_rate_per_100_words"] > 7


def test_rate_transcript_empty():
    result = rate_transcript("")
    assert result["total_words"] == 0
    assert result["filler_rate_per_100_words"] == 0.0


def test_rate_transcript_structure():
    result = rate_transcript("um hello world")
    assert set(result.keys()) == {
        "total_words",
        "filler_counts",
        "filler_score",
        "filler_rate_per_100_words",
        "rating",
    }