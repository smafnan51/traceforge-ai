import pytest
from app.evaluation import evaluate, score_case

def test_exact_match_is_case_and_whitespace_insensitive():
    assert score_case(" Hello ", "hello", "exact_match") == 1.0

def test_similarity_returns_fraction():
    score = score_case("cat sat", "cat sits", "normalized_similarity")
    assert 0 < score < 1

def test_evaluation_aggregates_cases():
    result = evaluate([
        {"input": "a", "actual": "yes", "expected": "yes"},
        {"input": "b", "actual": "no", "expected": "yes"},
    ], "exact_match")
    assert result["score"] == 0.5
    assert result["passed_cases"] == 1

def test_unknown_metric_rejected():
    with pytest.raises(ValueError):
        score_case("a", "a", "made_up")
