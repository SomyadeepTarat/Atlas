# Atlas Security Evaluation

Atlas treats user input, retrieved documents, MCP metadata,
tool output, and model output as untrusted input.

## Adversarial scenarios

| Attack | Expected behavior | Result |
|---|---|---|
tests/faults/test_model_failures.py::test_model_timeout_is_preserved PASSED                                                                                                 [ 11%]
tests/faults/test_model_failures.py::test_model_unavailable_is_preserved PASSED                                                                                             [ 22%]
tests/faults/test_model_failures.py::test_invalid_model_output_is_preserved PASSED                                                                                          [ 33%]
tests/faults/test_retrieval_failures.py::test_dense_embedding_failure_propagates PASSED                                                                                     [ 44%]
tests/faults/test_retrieval_failures.py::test_sparse_embedding_failure_propagates PASSED                                                                                    [ 55%]
tests/faults/test_retrieval_failures.py::test_vector_store_failure_propagates PASSED                                                                                        [ 66%]
tests/faults/test_retrieval_failures.py::test_graph_recursion_is_converted_to_domain_error PASSED                                                                           [ 77%]
tests/faults/test_tool_failures.py::test_read_only_timeout_is_timeout_failure PASSED                                                                                        [ 88%]
tests/faults/test_tool_failures.py::test_side_effect_timeout_becomes_unknown PASSED                                                                                         [100%]Running teardown with pytest sessionfinish...


================================================================================ 9 passed in 0.29s ================================================================================
(atlas) somyadeeptarat@Somyadeep-MacBook Atlas % make security
/Applications/Xcode.app/Contents/Developer/usr/bin/make security-unit
uv run pytest tests/security -v
=============================================================================== test session starts ===============================================================================
platform darwin -- Python 3.12.11, pytest-9.1.1, pluggy-1.6.0 -- /Users/somyadeeptarat/Desktop/Atlas/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/somyadeeptarat/Desktop/Atlas
configfile: pyproject.toml
plugins: langsmith-0.12.1, repeat-0.9.4, xdist-3.8.0, asyncio-1.4.0, deepeval-4.2.1, rerunfailures-16.6.1, anyio-4.14.2
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 16 items                                                                                                                                                                

tests/security/test_calculator_security.py::test_python_execution_payloads_rejected[__import__('os').system('echo pwned')] PASSED                                           [  6%]
tests/security/test_calculator_security.py::test_python_execution_payloads_rejected PASSED
tests/security/test_calculator_security.py::test_python_execution_payloads_rejected PASSED
tests/security/test_calculator_security.py::test_python_execution_payloads_rejected PASSED
tests/security/test_calculator_security.py::test_python_execution_payloads_rejected PASSED
tests/security/test_calculator_security.py::test_huge_exponent_rejected PASSED
tests/security/test_citation_security.py::test_chunk_text_cannot_define_valid_citations PASSED
tests/security/test_document_security.py::test_document_is_marked_untrusted PASSED
tests/security/test_document_security.py::test_path_traversal_filename_is_reduced PASSED
tests/security/test_document_security.py::test_non_pdf_content_rejected PASSED
tests/security/test_document_security.py::test_oversized_pdf_rejected PASSED
tests/security/test_mcp_security.py::test_high_risk_write_not_exposed_over_mcp[asyncio] PASSED
tests/security/test_mcp_security.py::test_unknown_mcp_tool_not_allowed PASSED
tests/security/test_memory_security.py::test_document_content_cannot_create_memory PASSED
tests/security/test_tool_security.py::test_model_cannot_self_grant_write_permission PASSE
tests/security/test_tool_security.py::test_high_risk_write_cannot_bypass_approval PASSED 

## Security controls

Atlas includes:

- Explicit trust boundaries
- Tool permission enforcement
- Human approval policy
- MCP allowlists
- Citation validation
- Memory-source restrictions
- Upload/resource limits
- Prompt/data separation
- Security regression tests