"""Small, dependency-free helpers for embedding-based novelty filtering."""

from __future__ import annotations

from math import sqrt


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions must match")
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


def select_semantically_novel(
    existing: list[list[float]],
    candidates: list[list[float]],
    threshold: float,
) -> list[tuple[int, float]]:
    """Return `(candidate index, max prior similarity)` for novel candidates.

    Each accepted candidate becomes part of the comparison pool, preventing a
    generated batch from containing semantic duplicates of itself.
    """
    comparison_pool = list(existing)
    accepted: list[tuple[int, float]] = []
    for index, vector in enumerate(candidates):
        max_similarity = max(
            (cosine_similarity(vector, previous) for previous in comparison_pool),
            default=-1.0,
        )
        if max_similarity >= threshold:
            continue
        accepted.append((index, max_similarity))
        comparison_pool.append(vector)
    return accepted
