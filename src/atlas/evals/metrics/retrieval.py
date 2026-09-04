from math import log2


def recall_at_k(
    flags: list[int],
    *,
    total_relevant: int,
    k: int,
) -> float:
    if total_relevant <= 0:
        return 1.0

    retrieved_relevant = sum(flags[:k])

    return min(
        retrieved_relevant / total_relevant,
        1.0,
    )


def precision_at_k(
    flags: list[int],
    *,
    k: int,
) -> float:
    selected = flags[:k]

    if not selected:
        return 0.0

    return sum(selected) / len(selected)


def reciprocal_rank(
    flags: list[int],
) -> float:
    for index, relevant in enumerate(
        flags,
        start=1,
    ):
        if relevant:
            return 1.0 / index

    return 0.0


def dcg_at_k(
    flags: list[int],
    *,
    k: int,
) -> float:
    score = 0.0

    for rank, relevance in enumerate(
        flags[:k],
        start=1,
    ):
        score += relevance / log2(rank + 1)

    return score


def ndcg_at_k(
    flags: list[int],
    *,
    k: int,
) -> float:
    actual = dcg_at_k(
        flags,
        k=k,
    )

    ideal_flags = sorted(
        flags,
        reverse=True,
    )

    ideal = dcg_at_k(
        ideal_flags,
        k=k,
    )

    if ideal == 0:
        return 0.0

    return actual / ideal
