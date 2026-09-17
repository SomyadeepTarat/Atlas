# Atlas Reliability Evaluation

Atlas includes explicit failure handling rather than assuming
all dependencies remain healthy.

## Failure scenarios

| Injected failure | Expected behavior | Result |
|---|---|---|
tests/faults/test_model_failures.py::test_model_timeout_is_preserved PASSED
tests/faults/test_model_failures.py::test_model_unavailable_is_preserved PASSED
tests/faults/test_model_failures.py::test_invalid_model_output_is_preserved PASSED
tests/faults/test_retrieval_failures.py::test_dense_embedding_failure_propagates PASSED
tests/faults/test_retrieval_failures.py::test_sparse_embedding_failure_propagates PASSED
tests/faults/test_retrieval_failures.py::test_vector_store_failure_propagates PASSED
tests/faults/test_retrieval_failures.py::test_graph_recursion_is_converted_to_domain_error PASSED
tests/faults/test_tool_failures.py::test_read_only_timeout_is_timeout_failure PASSED
tests/faults/test_tool_failures.py::test_side_effect_timeout_becomes_unknown PASSED

## Reliability guarantees

Atlas implements:

- Per-operation timeouts
- Workflow-wide deadlines
- Bounded retries
- Exponential backoff
- Circuit breakers
- Concurrency limits
- Graceful retrieval degradation
- LangGraph iteration limits
- Dependency health reporting