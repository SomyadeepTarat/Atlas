# Atlas Architecture

```mermaid
flowchart TD
    U[User] --> FE[Next.js Frontend]

    FE -->|REST + SSE| API[FastAPI API]

    API --> LG[LangGraph Research Workflow]

    LG --> PLAN[Plan]
    PLAN --> RET[Retrieve]

    RET --> DR[Dense Retrieval]
    RET --> SR[Sparse BM25 Retrieval]

    DR --> Q[(Qdrant)]
    SR --> Q

    RET --> RRF[Reciprocal Rank Fusion]
    RRF --> RR[Cross-Encoder Reranker]

    RR --> EV[Evidence Assessment]

    EV -->|Insufficient| RET
    EV -->|Sufficient| SYN[Synthesize]

    SYN --> VER[Verify]

    VER -->|Failure| REP[Repair]
    REP --> VER

    VER -->|Valid| OUT[Grounded Answer]

    LG --> TOOL[Policy-Controlled Tool Runtime]
    TOOL --> LOCAL[Local Tools]
    TOOL --> MCP[MCP Client]

    API --> PG[(PostgreSQL)]
    API --> MEM[Persistent Memory]
    MEM --> PG

    MODEL[Ollama / Qwen3 4B] --> LG

    OBS[OpenTelemetry + Langfuse]
    API -. telemetry .-> OBS
    LG -. telemetry .-> OBS
    TOOL -. telemetry .-> OBS

    SEC[Security + Reliability Policies]
    SEC -. controls .-> LG
    SEC -. controls .-> TOOL
```

## Research workflow

```mermaid
flowchart LR
    A[Question] --> B[Plan]

    B --> C[Retrieve]

    C --> D[Assess Evidence]

    D -->|Insufficient| E[Refine Query]

    E --> C

    D -->|Sufficient| F[Synthesize]

    F --> G[Verify]

    G -->|Unsupported| H[Repair]

    H --> G

    G -->|Valid| I[Answer]
```

## Architectural boundaries

### PostgreSQL vs Qdrant

PostgreSQL stores canonical application state:

- research threads
- messages
- memories
- document metadata

Qdrant stores derived retrieval state:

- dense vectors
- sparse vectors
- document chunks

### Model layer

Atlas does not couple application logic directly to Ollama.
Model providers implement a common model-client abstraction with
structured outputs, retry handling, metadata, and readiness.

### Tool layer

LLM output never grants permissions directly.

Tool execution passes through:

1. Tool lookup
2. Input validation
3. Permission enforcement
4. Approval policy
5. Timeout handling
6. Execution
7. Output validation

### Trust boundary

Retrieved documents, user input, MCP metadata, tool output,
and model output are treated as untrusted data.