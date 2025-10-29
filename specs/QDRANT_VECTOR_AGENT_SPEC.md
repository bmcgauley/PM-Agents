# Qdrant Vector Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Semantic Search & Vector Storage
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The Qdrant Vector Agent provides semantic search capabilities over codebases and documentation. It indexes code, generates embeddings, and retrieves contextually relevant information for other agents.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: All specialist agents (provides context retrieval)
- **Primary responsibility**: Vector search, codebase indexing, context retrieval

### 1.3 Key Responsibilities
1. **Codebase Indexing**: Parse and index source code into vector collections
2. **Documentation Indexing**: Index README files, API docs, comments
3. **Semantic Search**: Retrieve relevant code/documentation based on natural language queries
4. **Similarity Search**: Find similar code patterns or implementations
5. **Context Retrieval**: Provide relevant context to other agents before task execution
6. **Index Management**: Create, update, and delete vector collections

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `QdrantVectorRequest`

```json
{
  "request_id": "string (UUID)",
  "task_type": "index|search|update|delete|analyze",
  "operation": {
    "type": "index_codebase|search_code|search_docs|find_similar|get_context",
    "parameters": {
      // For index_codebase
      "codebase_path": "string (absolute path)",
      "collection_name": "string (e.g., 'project-name-codebase')",
      "file_patterns": ["*.ts", "*.tsx", "*.py", "*.r"],
      "exclude_patterns": ["node_modules/**", "dist/**", ".git/**"],
      "chunk_size": "integer (default: 1000 tokens)",
      "chunk_overlap": "integer (default: 200 tokens)",

      // For search operations
      "query": "string (natural language query)",
      "collection_name": "string",
      "top_k": "integer (default: 10)",
      "score_threshold": "float (default: 0.7)",
      "filters": {
        "file_type": "string (e.g., 'typescript')",
        "directory": "string (e.g., 'src/components')",
        "tags": ["string", ...]
      },

      // For find_similar
      "reference_code": "string (code snippet)",
      "similarity_threshold": "float (default: 0.8)",

      // For get_context
      "task_description": "string",
      "agent_type": "string (requesting agent)",
      "max_tokens": "integer (default: 4000)"
    }
  },
  "embedding_config": {
    "model": "text-embedding-3-small|text-embedding-3-large|all-MiniLM-L6-v2",
    "dimensions": "integer (default: 384 for MiniLM, 1536 for OpenAI)",
    "batch_size": "integer (default: 100)"
  },
  "context": {
    "project_name": "string",
    "project_type": "frontend|backend|ml|analytics|fullstack",
    "priority": "high|normal|low"
  }
}
```

### 2.2 Output Schema: `QdrantVectorResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "success|partial|failed",
  "execution_time_seconds": "float",
  "operation_type": "index|search|update|delete|analyze",
  "results": {
    // For index operations
    "indexed_items": {
      "total_files": "integer",
      "total_chunks": "integer",
      "total_vectors": "integer",
      "collection_name": "string",
      "index_size_bytes": "integer",
      "indexing_time_seconds": "float"
    },

    // For search operations
    "search_results": [
      {
        "id": "string (vector ID)",
        "score": "float (0.0 - 1.0)",
        "content": "string (code or documentation snippet)",
        "metadata": {
          "file_path": "string",
          "file_type": "string",
          "line_start": "integer",
          "line_end": "integer",
          "function_name": "string (optional)",
          "class_name": "string (optional)",
          "tags": ["string", ...]
        },
        "context": {
          "before": "string (surrounding context)",
          "after": "string (surrounding context)"
        }
      }
    ],

    // For find_similar
    "similar_items": [
      {
        "similarity_score": "float (0.0 - 1.0)",
        "file_path": "string",
        "code_snippet": "string",
        "explanation": "string (why it's similar)"
      }
    ],

    // For get_context
    "context_bundle": {
      "relevant_code": ["string (code snippets)", ...],
      "relevant_docs": ["string (documentation)", ...],
      "related_files": ["string (file paths)", ...],
      "total_tokens": "integer",
      "confidence": "float (0.0 - 1.0)"
    }
  },
  "metrics": {
    "query_time_ms": "float",
    "vectors_searched": "integer",
    "cache_hit": "boolean",
    "embedding_time_ms": "float"
  },
  "recommendations": [
    "string (actionable suggestions)",
    "e.g., 'Consider indexing the docs/ directory for better results'",
    "e.g., 'Query too broad, try adding file type filter'"
  ],
  "errors": [
    {
      "type": "qdrant_error|embedding_error|parse_error",
      "message": "string",
      "file": "string (optional)",
      "severity": "critical|warning|info"
    }
  ]
}
```

---

## 3. MCP Tools Required

### 3.1 Essential Tools

1. **qdrant** (Custom MCP Server: `@pm-agents/mcp-qdrant`)
   - **Usage**: All vector database operations
   - **Operations**:
     - `create_collection`: Initialize vector collections
     - `upsert_vectors`: Add/update vectors
     - `search_vectors`: Semantic search
     - `delete_vectors`: Remove outdated vectors
     - `get_collection_info`: Collection statistics

2. **filesystem** (MCP Server)
   - **Usage**: Read codebase files for indexing
   - **Operations**:
     - `read_file`: Read source code files
     - `list_directory`: Discover files to index
     - `search_files`: Find files matching patterns

### 3.2 Optional Tools

1. **github** (MCP Server)
   - **Usage**: Index GitHub repositories directly
   - **Operations**: Fetch repository contents, get file metadata

2. **brave-search** (MCP Server)
   - **Usage**: Augment context with external documentation
   - **Operations**: Search for library/framework documentation

---

## 4. Algorithms & Workflows

### 4.1 Codebase Indexing Algorithm

```python
def index_codebase(request: QdrantVectorRequest) -> QdrantVectorResponse:
    """
    Index an entire codebase into Qdrant vector database.

    Steps:
    1. Discover files matching patterns
    2. Parse files and extract code chunks
    3. Generate embeddings for each chunk
    4. Store vectors in Qdrant with metadata
    5. Validate index completeness
    6. Return indexing statistics
    """

    # Step 1: Discover Files
    files = discover_files(
        codebase_path=request.operation.parameters.codebase_path,
        include_patterns=request.operation.parameters.file_patterns,
        exclude_patterns=request.operation.parameters.exclude_patterns
    )

    # Step 2: Parse Files into Chunks
    chunks = []
    for file in files:
        file_content = read_file(file.path)
        file_chunks = parse_code_file(
            content=file_content,
            file_type=file.extension,
            chunk_size=request.operation.parameters.chunk_size,
            chunk_overlap=request.operation.parameters.chunk_overlap
        )
        chunks.extend(file_chunks)

    # Step 3: Generate Embeddings
    embeddings = generate_embeddings_batch(
        texts=[chunk.content for chunk in chunks],
        model=request.embedding_config.model,
        batch_size=request.embedding_config.batch_size
    )

    # Step 4: Store in Qdrant
    collection_name = request.operation.parameters.collection_name
    ensure_collection_exists(
        collection_name=collection_name,
        vector_size=request.embedding_config.dimensions
    )

    points = [
        {
            "id": generate_id(chunk),
            "vector": embedding,
            "payload": {
                "file_path": chunk.file_path,
                "file_type": chunk.file_type,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "content": chunk.content,
                "function_name": chunk.function_name,
                "class_name": chunk.class_name,
                "tags": chunk.tags
            }
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    upsert_result = upsert_vectors(collection_name, points)

    # Step 5: Validate Index
    validation = validate_index(
        collection_name=collection_name,
        expected_count=len(chunks)
    )

    # Step 6: Return Statistics
    return create_response(
        status="success" if validation.valid else "partial",
        results={
            "indexed_items": {
                "total_files": len(files),
                "total_chunks": len(chunks),
                "total_vectors": len(embeddings),
                "collection_name": collection_name,
                "index_size_bytes": calculate_size(points),
                "indexing_time_seconds": execution_time
            }
        }
    )
```

### 4.2 Code Parsing Strategy

```python
def parse_code_file(
    content: str,
    file_type: str,
    chunk_size: int,
    chunk_overlap: int
) -> List[CodeChunk]:
    """
    Parse code file into semantically meaningful chunks.

    Strategies by File Type:
    - TypeScript/JavaScript: Parse by function/class definitions
    - Python: Parse by function/class definitions using AST
    - R: Parse by function definitions
    - Markdown: Parse by section headers

    Fallback: Sliding window chunking if parsing fails
    """

    parser = get_parser(file_type)

    try:
        # Try semantic parsing first
        if file_type in ["typescript", "javascript", "python", "r"]:
            return parser.parse_by_definitions(content)
        elif file_type == "markdown":
            return parser.parse_by_sections(content)
        else:
            # Fallback to sliding window
            return sliding_window_chunk(content, chunk_size, chunk_overlap)

    except ParsingError:
        # Fallback to sliding window if parsing fails
        return sliding_window_chunk(content, chunk_size, chunk_overlap)


class TypeScriptParser:
    """Parse TypeScript/JavaScript files using tree-sitter"""

    def parse_by_definitions(self, content: str) -> List[CodeChunk]:
        """
        Extract functions, classes, interfaces, types.

        Each chunk includes:
        - The definition itself
        - JSDoc comments
        - Surrounding context (imports, related types)
        """
        tree = self.parser.parse(bytes(content, "utf8"))
        chunks = []

        for node in tree.root_node.children:
            if node.type in ["function_declaration", "class_declaration",
                             "interface_declaration", "type_alias_declaration"]:
                chunk = CodeChunk(
                    content=self.extract_with_context(node),
                    file_type="typescript",
                    line_start=node.start_point[0],
                    line_end=node.end_point[0],
                    function_name=self.extract_name(node),
                    tags=self.extract_tags(node)
                )
                chunks.append(chunk)

        return chunks


class PythonParser:
    """Parse Python files using AST"""

    def parse_by_definitions(self, content: str) -> List[CodeChunk]:
        """
        Extract functions, classes, methods.

        Each chunk includes:
        - The definition
        - Docstrings
        - Decorators
        """
        tree = ast.parse(content)
        chunks = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                chunk = CodeChunk(
                    content=ast.unparse(node),
                    file_type="python",
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    function_name=node.name,
                    class_name=self.get_class_name(node),
                    tags=self.extract_decorators(node)
                )
                chunks.append(chunk)

        return chunks
```

### 4.3 Semantic Search Algorithm

```python
def search_code(request: QdrantVectorRequest) -> QdrantVectorResponse:
    """
    Perform semantic search over indexed code.

    Steps:
    1. Generate embedding for query
    2. Search Qdrant with filters
    3. Re-rank results by relevance
    4. Add surrounding context
    5. Return top-k results
    """

    # Step 1: Generate Query Embedding
    query_embedding = generate_embedding(
        text=request.operation.parameters.query,
        model=request.embedding_config.model
    )

    # Step 2: Search Qdrant
    search_results = search_vectors(
        collection_name=request.operation.parameters.collection_name,
        query_vector=query_embedding,
        top_k=request.operation.parameters.top_k * 2,  # Over-fetch for re-ranking
        score_threshold=request.operation.parameters.score_threshold,
        filters=build_filters(request.operation.parameters.filters)
    )

    # Step 3: Re-rank Results
    reranked_results = rerank_results(
        query=request.operation.parameters.query,
        results=search_results,
        top_k=request.operation.parameters.top_k
    )

    # Step 4: Add Surrounding Context
    enriched_results = []
    for result in reranked_results:
        context = get_surrounding_context(
            file_path=result.payload["file_path"],
            line_start=result.payload["line_start"],
            line_end=result.payload["line_end"],
            context_lines=5
        )

        enriched_results.append({
            "id": result.id,
            "score": result.score,
            "content": result.payload["content"],
            "metadata": {
                "file_path": result.payload["file_path"],
                "file_type": result.payload["file_type"],
                "line_start": result.payload["line_start"],
                "line_end": result.payload["line_end"],
                "function_name": result.payload.get("function_name"),
                "class_name": result.payload.get("class_name"),
                "tags": result.payload.get("tags", [])
            },
            "context": context
        })

    # Step 5: Return Results
    return create_response(
        status="success",
        results={"search_results": enriched_results},
        metrics={
            "query_time_ms": execution_time,
            "vectors_searched": len(search_results),
            "cache_hit": check_cache(request.operation.parameters.query)
        }
    )
```

### 4.4 Context Retrieval for Agents

```python
def get_context_for_task(
    task_description: str,
    agent_type: str,
    max_tokens: int
) -> ContextBundle:
    """
    Retrieve relevant context for an agent before task execution.

    Strategy:
    1. Search for relevant code based on task description
    2. Search for relevant documentation
    3. Identify related files (imports, dependencies)
    4. Prioritize and truncate to max_tokens
    5. Return context bundle
    """

    # Step 1: Search Code
    code_results = search_code(
        query=task_description,
        collection_name=f"{project_name}-codebase",
        top_k=20,
        filters=get_agent_filters(agent_type)
    )

    # Step 2: Search Documentation
    doc_results = search_documentation(
        query=task_description,
        collection_name=f"{project_name}-documentation",
        top_k=10
    )

    # Step 3: Identify Related Files
    related_files = identify_related_files(code_results)

    # Step 4: Prioritize and Truncate
    context = prioritize_context(
        code_results=code_results,
        doc_results=doc_results,
        related_files=related_files,
        max_tokens=max_tokens
    )

    # Step 5: Return Bundle
    return ContextBundle(
        relevant_code=context.code_snippets,
        relevant_docs=context.doc_snippets,
        related_files=context.file_paths,
        total_tokens=context.token_count,
        confidence=calculate_confidence(code_results, doc_results)
    )
```

---

## 5. Success Criteria

### 5.1 Functional Requirements
- ✅ Index 10,000 files in <5 minutes
- ✅ Search queries return results in <500ms
- ✅ Semantic search accuracy: >80% relevance (human evaluation)
- ✅ Support TypeScript, Python, R, Markdown file types
- ✅ Handle codebases up to 1GB in size

### 5.2 Quality Requirements
- ✅ No duplicate vectors in index
- ✅ All indexed files retrievable
- ✅ Embeddings generated consistently (deterministic given same input)
- ✅ Context retrieval includes only relevant information

### 5.3 Performance Requirements
- ✅ Indexing throughput: >100 files/second
- ✅ Search latency: <500ms (p95)
- ✅ Embedding generation: <100ms per chunk
- ✅ Memory usage: <2GB for typical codebase

### 5.4 Integration Requirements
- ✅ All specialist agents can request context via Supervisor
- ✅ Compatible with Anthropic, OpenAI, and local embedding models
- ✅ Qdrant server accessible via MCP
- ✅ Graceful degradation if Qdrant unavailable (warn and continue)

---

## 6. Error Handling

### 6.1 Error Categories

1. **Qdrant Connection Errors**
   - Qdrant server unreachable
   - Authentication failed
   - Collection not found
   - **Recovery**: Retry with exponential backoff, create collection if missing

2. **Embedding Errors**
   - API rate limit exceeded
   - Invalid input text (too long)
   - Model unavailable
   - **Recovery**: Batch retry, truncate text, fall back to alternative model

3. **Parsing Errors**
   - Invalid file encoding
   - Syntax errors in code
   - Unsupported file type
   - **Recovery**: Skip file, log warning, continue indexing

4. **Resource Errors**
   - Out of memory
   - Disk space exhausted
   - Timeout during indexing
   - **Recovery**: Reduce batch size, clean up old indices, resume from checkpoint

### 6.2 Validation Checks

```python
def validate_index(collection_name: str, expected_count: int) -> ValidationResult:
    """
    Validate that indexing completed successfully.

    Checks:
    1. Collection exists
    2. Vector count matches expected
    3. All vectors have valid embeddings
    4. Sample search returns results
    """

    result = ValidationResult()

    # Check collection exists
    result.collection_exists = check_collection_exists(collection_name)

    # Check vector count
    actual_count = get_vector_count(collection_name)
    result.count_matches = actual_count == expected_count

    # Check vector validity
    sample_vectors = get_sample_vectors(collection_name, sample_size=10)
    result.vectors_valid = all(
        validate_vector(v) for v in sample_vectors
    )

    # Check searchability
    test_query = "function to handle user authentication"
    search_results = search_vectors(collection_name, test_query, top_k=5)
    result.search_works = len(search_results) > 0

    result.valid = all([
        result.collection_exists,
        result.count_matches,
        result.vectors_valid,
        result.search_works
    ])

    return result
```

---

## 7. Implementation Notes

### 7.1 Technology Stack
- **Vector Database**: Qdrant (self-hosted or cloud)
- **Embedding Models**:
  - Local: `all-MiniLM-L6-v2` (384 dimensions, fast)
  - Cloud: `text-embedding-3-small` (1536 dimensions, accurate)
- **Code Parsers**: tree-sitter (TypeScript/JavaScript), AST (Python), custom (R)
- **MCP Integration**: Custom Qdrant MCP server

### 7.2 Design Patterns
- **Repository Pattern**: Abstract Qdrant operations
- **Strategy Pattern**: Different parsing strategies per file type
- **Circuit Breaker Pattern**: Protect against Qdrant downtime
- **Cache-Aside Pattern**: Cache frequent queries

### 7.3 Dependencies
```python
# Python Implementation Dependencies
dependencies = [
    "anthropic>=0.40.0",           # Claude API
    "qdrant-client>=1.7.0",        # Qdrant Python client
    "sentence-transformers>=2.2.0", # Local embeddings
    "tree-sitter>=0.20.0",         # Code parsing
    "tree-sitter-typescript>=0.20.0",
    "tiktoken>=0.5.0",             # Token counting
    "pydantic>=2.0.0",             # Schema validation
]
```

### 7.4 Configuration
```python
class QdrantVectorConfig:
    """Configuration for Qdrant Vector Agent"""

    # Qdrant connection
    qdrant_url = "http://localhost:6333"
    qdrant_api_key = None  # Optional for cloud

    # Embedding models
    embedding_model_local = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_model_cloud = "text-embedding-3-small"
    embedding_dimensions = 384  # For MiniLM

    # Indexing settings
    chunk_size = 1000  # tokens
    chunk_overlap = 200  # tokens
    batch_size = 100  # for embedding generation

    # Search settings
    default_top_k = 10
    default_score_threshold = 0.7
    rerank_enabled = True

    # Performance
    max_concurrent_embeddings = 10
    cache_ttl_seconds = 3600  # 1 hour
    max_cache_size_mb = 100
```

### 7.5 Example Usage

```python
# Index a Next.js codebase
request = QdrantVectorRequest(
    request_id="123e4567-e89b-12d3-a456-426614174000",
    task_type="index",
    operation=Operation(
        type="index_codebase",
        parameters={
            "codebase_path": "/home/user/projects/my-saas-app",
            "collection_name": "my-saas-app-codebase",
            "file_patterns": ["*.ts", "*.tsx", "*.js", "*.jsx"],
            "exclude_patterns": ["node_modules/**", ".next/**", "dist/**"],
            "chunk_size": 1000,
            "chunk_overlap": 200
        }
    ),
    embedding_config=EmbeddingConfig(
        model="all-MiniLM-L6-v2",
        dimensions=384,
        batch_size=100
    ),
    context=Context(
        project_name="my-saas-app",
        project_type="frontend",
        priority="high"
    )
)

response = qdrant_vector_agent.execute(request)
# => {
#   "status": "success",
#   "results": {
#     "indexed_items": {
#       "total_files": 127,
#       "total_chunks": 1543,
#       "total_vectors": 1543,
#       "collection_name": "my-saas-app-codebase",
#       "indexing_time_seconds": 23.4
#     }
#   }
# }

# Search for authentication code
search_request = QdrantVectorRequest(
    request_id="223e4567-e89b-12d3-a456-426614174001",
    task_type="search",
    operation=Operation(
        type="search_code",
        parameters={
            "query": "user authentication with Supabase",
            "collection_name": "my-saas-app-codebase",
            "top_k": 5,
            "score_threshold": 0.75,
            "filters": {"file_type": "typescript"}
        }
    ),
    embedding_config=EmbeddingConfig(model="all-MiniLM-L6-v2")
)

search_response = qdrant_vector_agent.execute(search_request)
# => Returns top 5 most relevant code snippets with context
```

---

## 8. Testing Strategy

### 8.1 Unit Tests
- ✅ Code parsing for each file type
- ✅ Embedding generation
- ✅ Vector storage and retrieval
- ✅ Filter application
- ✅ Re-ranking algorithm

### 8.2 Integration Tests
- ✅ Full indexing pipeline (files → vectors → Qdrant)
- ✅ Search with various query types
- ✅ Context retrieval for agents
- ✅ MCP server communication

### 8.3 Performance Tests
- ✅ Index 10,000 files and measure time
- ✅ 1000 concurrent search queries
- ✅ Memory usage during large indexing jobs

### 8.4 Quality Tests
- ✅ Semantic search accuracy (human evaluation on 100 queries)
- ✅ No duplicate vectors
- ✅ All indexed content retrievable

---

## 9. Monitoring & Metrics

### 9.1 Key Metrics
- **Indexing Metrics**: Files indexed, vectors created, indexing time
- **Search Metrics**: Query latency, result relevance, cache hit rate
- **Quality Metrics**: Search accuracy, duplicate rate
- **Resource Metrics**: Memory usage, Qdrant storage size

### 9.2 Logging
```python
# Log format
{
    "timestamp": "2025-10-28T10:00:00Z",
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "agent": "qdrant_vector",
    "action": "index_codebase",
    "collection_name": "my-saas-app-codebase",
    "files_indexed": 127,
    "vectors_created": 1543,
    "execution_time_seconds": 23.4,
    "status": "success"
}
```

---

## 10. Future Enhancements

1. **Hybrid Search**: Combine semantic search with keyword search (BM25)
2. **Incremental Indexing**: Re-index only changed files
3. **Multi-Collection Search**: Search across multiple projects simultaneously
4. **Code Similarity Detection**: Find duplicate or similar code patterns
5. **Automatic Re-ranking**: Learn from user feedback to improve relevance
6. **GraphRAG Integration**: Combine vector search with code graph traversal
7. **Multimodal Embeddings**: Index diagrams, screenshots, UI components

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
