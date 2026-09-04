# Atlas Retrieval Benchmarks

This directory contains benchmark results for Atlas's retrieval pipeline.

The current benchmark compares five retrieval configurations:

- Dense retrieval
- Sparse retrieval
- Hybrid retrieval
- Hybrid retrieval with reranking
- Hybrid retrieval with reranking and adjacent-chunk deduplication

The evaluation dataset is based on an ingested RAGAS research paper and measures how effectively each retrieval strategy ranks relevant evidence.

## Results

| Configuration | Recall@K | Precision@K | MRR | nDCG@K | Mean Latency |
|---|---:|---:|---:|---:|---:|
| Dense | 1.0000 | 0.2250 | 0.7375 | 0.7852 | 0.0179 s |
| Sparse | 1.0000 | 0.2250 | 0.8750 | 0.8977 | 0.0030 s |
| Hybrid | 1.0000 | 0.2250 | 0.8750 | 0.8977 | 0.0129 s |
| Hybrid + Rerank | 1.0000 | 0.2250 | **0.9062** | **0.9188** | 0.1369 s |
| Hybrid + Rerank + Dedupe | 1.0000 | 0.2250 | **0.9062** | **0.9188** | 0.0927 s |

## Interpretation

All retrieval configurations achieved a Recall@K of `1.0`, meaning relevant evidence was successfully retrieved for every evaluated query.

The main difference between configurations is therefore ranking quality.

Sparse retrieval substantially outperformed dense retrieval on this benchmark, likely because the evaluation questions contain distinctive technical terms such as framework names and metric terminology that benefit from lexical matching.

Hybrid retrieval preserved the strong ranking performance of sparse retrieval while combining lexical and semantic retrieval signals.

Adding the cross-encoder reranker produced the strongest overall ranking quality:

- MRR improved from `0.8750` to `0.9062`
- nDCG improved from `0.8977` to `0.9188`

This indicates that reranking improves the position of relevant evidence after candidate retrieval.

The reranking stage introduces additional latency, increasing mean retrieval time from approximately `13 ms` for hybrid retrieval to approximately `137 ms`. For a research-agent workflow, this is an acceptable tradeoff for improved evidence ranking.

Adjacent-chunk deduplication preserved the same retrieval quality in this benchmark. The lower measured latency in this individual run should not be interpreted as a guaranteed performance improvement without repeated measurements.

## Current Retrieval Strategy

Based on these results, Atlas currently uses:

```text
Dense retrieval
        +
Sparse retrieval
        ↓
Hybrid candidate retrieval
        ↓
Cross-encoder reranking
        ↓
Adjacent-chunk deduplication
        ↓
Context selection
        ↓
Grounded generation
```

This configuration provides the strongest ranking quality among the evaluated approaches while remaining suitable for local, production-style retrieval.

## Limitations

These results are an initial benchmark rather than a final evaluation.

The current evaluation set is relatively small and is based on a single technical document. Its terminology-heavy questions favor lexical retrieval, which helps explain the strong sparse retrieval performance.

Future benchmarks should include:

- Multiple documents and domains
- More paraphrased and semantic questions
- Hard negative retrieval cases
- Document-scoped retrieval
- Larger evaluation datasets
- Multiple benchmark runs for more reliable latency measurements
- Grounded answer and citation-quality evaluation

Benchmark results should therefore be interpreted as evidence for the current retrieval architecture, not as a general claim that one retrieval method always outperforms another.