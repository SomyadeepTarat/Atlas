from atlas.evals.metrics.retrieval import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_recall_at_k():
    flags = [1, 0, 1, 0]

    assert (
        recall_at_k(
            flags,
            total_relevant=2,
            k=2,
        )
        == 0.5
    )


def test_precision_at_k():
    flags = [1, 0, 1, 0]

    assert (
        precision_at_k(
            flags,
            k=4,
        )
        == 0.5
    )


def test_reciprocal_rank():
    flags = [0, 0, 1, 1]

    assert reciprocal_rank(flags) == 1 / 3


def test_ndcg_is_one_for_ideal_ranking():
    flags = [1, 1, 0, 0]

    assert (
        ndcg_at_k(
            flags,
            k=4,
        )
        == 1.0
    )
