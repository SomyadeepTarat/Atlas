# Atlas v1 Benchmark

This directory contains the reproducible evaluation results used
to evaluate Atlas v1.

## Environment

- Pipeline: Atlas v1
- Python: 3.12
- Local generation model: Qwen3 4B via Ollama
- Dense embeddings: BAAI/bge-small-en-v1.5
- Sparse retrieval: Qdrant/BM25
- Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2
- Vector database: Qdrant

## Retrieval configuration

- Chunk size: 1200 characters
- Chunk overlap: 200 characters
- Candidate K: 20
- Final K: 5

## Dataset

Dataset:

`evals/datasets/retrieval_v1.json`

Ground-truth labels were manually verified.

The benchmark compares:

1. Dense retrieval
2. Sparse retrieval
3. Hybrid retrieval
4. Hybrid retrieval + reranking
5. Hybrid retrieval + reranking + deduplication

## Important

All results in this directory were generated from actual Atlas
evaluation runs. No illustrative or fabricated metrics are
included.