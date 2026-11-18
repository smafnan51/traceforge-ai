from difflib import SequenceMatcher


def score_case(actual: str, expected: str, metric: str) -> float:
    actual_norm = actual.strip().casefold()
    expected_norm = expected.strip().casefold()
    if metric == "exact_match":
        return float(actual_norm == expected_norm)
    if metric == "normalized_similarity":
        return SequenceMatcher(a=expected_norm, b=actual_norm).ratio()
    raise ValueError(f"Unsupported metric: {metric}")


def evaluate(cases: list[dict], metric: str) -> dict:
    scores = [score_case(c["actual"], c["expected"], metric) for c in cases]
    passed = sum(score >= (1.0 if metric == "exact_match" else 0.8) for score in scores)
    return {
        "score": round(sum(scores) / len(scores), 4),
        "total_cases": len(scores),
        "passed_cases": passed,
        "details": [
            {"input": c["input"], "actual": c["actual"], "expected": c["expected"], "score": round(s, 4)}
            for c, s in zip(cases, scores)
        ],
    }
