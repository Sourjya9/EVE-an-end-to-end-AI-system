# Eve System Architecture & Engineering Guide

## 1. System Overview

Eve is designed as a production-style, modular AI assistant. The primary goal is delivering high-performance conversational AI and grounded retrieval (RAG) with transparent, testable, and loosely coupled components.

```mermaid
graph TD
    User([User Browser]) -->|HTTP / SSE| Frontend[Next.js 14 App Router]
    Frontend -->|REST API / SSE Streams| Backend[FastAPI Async API Server]

    subgraph Backend Core
        Backend --> RouterChat[Chat Router]
        Backend --> RouterDoc[Document Router]
        Backend --> RouterSearch[Search Router]
    end

    subgraph LangGraph Orchestrator
        RouterChat --> StateGraph[LangGraph StateMachine]
        StateGraph --> NodeClassify[Node: classify_request]
        NodeClassify -->|needs retrieval| NodeRetrieve[Node: retrieve_context]
        NodeClassify -->|conversational greeting| NodeGenerate[Node: generate_response]
        NodeRetrieve --> NodeGenerate
    end

    subgraph AI Service Integrations
        NodeGenerate -->|Streaming Completion| Groq[Groq Llama 3.3-70B]
        RouterDoc -->|Batch Passage Embeddings| Jina[Jina AI v3 1024-dim]
        NodeRetrieve -->|Query Embedding| Jina
    end

    subgraph Persistent Storage
        NodeRetrieve -->|Cosine Distance <=> | PGVector[(PostgreSQL + pgvector)]
        RouterDoc -->|Store Chunks & Embeddings| PGVector
        RouterChat -->|Store Conversations & Runs| PGVector
    end

    subgraph Observability
        Backend --> Sentry[Sentry Error Tracking]
        StateGraph --> Opik[Comet Opik LLM Tracing]
        Backend --> CloudWatch[AWS CloudWatch JSON Logs]
    end
```

---

## 2. RAG (Retrieval-Augmented Generation) Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as Next.js UI
    participant Backend as FastAPI
    participant Extractor as Text Extractor
    participant Jina as Jina AI API
    participant DB as PostgreSQL + pgvector
    participant Groq as Groq API

    Note over User,DB: Phase 1: Ingestion & Indexing
    User->>Frontend: Upload Document (PDF / TXT / MD)
    Frontend->>Backend: POST /api/documents/upload
    Backend->>Extractor: Extract and clean text
    Backend->>Backend: Split text recursively (size 800, overlap 150)
    Backend->>Jina: POST /v1/embeddings (task: retrieval.passage)
    Jina-->>Backend: 1024-dimensional normalized vectors
    Backend->>DB: INSERT into documents & document_chunks (pgvector)
    Backend-->>Frontend: 200 OK (Indexed with chunk count)

    Note over User,Groq: Phase 2: Grounded Retrieval & Answer Generation
    User->>Frontend: "What are the main system components?"
    Frontend->>Backend: POST /api/chat (stream: true)
    Backend->>Backend: LangGraph: classify_request -> needs_retrieval: true
    Backend->>Jina: Embed query (task: retrieval.query)
    Jina-->>Backend: Query vector
    Backend->>DB: SELECT chunk WHERE distance < threshold ORDER BY embedding <=> query_vector LIMIT 4
    DB-->>Backend: Top 4 chunks + metadata
    Backend->>Frontend: SSE Event (Citations metadata)
    Backend->>Groq: Stream chat completion with grounded context prompt
    Groq-->>Backend: Response token stream
    Backend-->>Frontend: SSE Token Chunks
    Backend->>DB: Persist User message, Assistant message & AgentRun latency
```

---

## 3. LangGraph Workflow Explanation

Eve uses a compiled `StateGraph` with a typed state dictionary (`AgentState`):

1. **`classify_request`**:
   - Inspects the user query, length, and conversation context.
   - Detects conversational greetings versus information-seeking queries.
   - Sets `needs_retrieval: boolean`.

2. **Conditional Routing (`route_after_classification`)**:
   - If `needs_retrieval == True`: Routes to `retrieve_context`.
   - If `needs_retrieval == False`: Skips directly to `generate_response`.

3. **`retrieve_context`**:
   - Generates the query embedding via Jina AI.
   - Performs a cosine similarity search against `document_chunks`.
   - Formats citations and returns them in the state.

4. **`generate_response`**:
   - Assembles system instructions, past turns, grounded excerpts, and current query.
   - Invokes Groq LLM (or prepares streaming prompt).
   - Records Opik spans and latency metrics.

---

## 4. Database Schema

- **`users`**: Optional user account and authentication mapping.
- **`conversations`**: Thread containers with title, timestamps, and message links.
- **`messages`**: Chronological turns with role, content, token count, and JSON citation references.
- **`documents`**: Ingested asset metadata, mime-type, status (`processing`, `indexed`, `failed`), and chunk counter.
- **`document_chunks`**: Discrete text segments, character boundaries, and `Vector(1024)` column with an HNSW index.
- **`agent_runs`**: Operational audit log recording node execution, retrieval decisions, and millisecond latencies.
