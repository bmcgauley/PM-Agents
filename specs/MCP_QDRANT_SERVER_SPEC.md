# Qdrant MCP Server Specification

## Overview

The **@pm-agents/mcp-qdrant** MCP server provides semantic search and vector database operations for the PM-Agents multi-agent system. It exposes Qdrant operations through the Model Context Protocol, enabling agents to perform codebase indexing, semantic search, and context retrieval.

### Purpose

- **Codebase indexing**: Index source code files for semantic search
- **Documentation search**: Index and search project documentation
- **Context retrieval**: Provide relevant code context to agents
- **Knowledge management**: Maintain project-specific knowledge bases

### Target Agents

- **Qdrant Vector Agent**: Primary consumer, manages all vector operations
- **Coordinator Agent**: Retrieves relevant context for task delegation
- **Supervisor Agent**: Searches for similar past tasks and solutions
- **All Specialist Agents**: Query for relevant code examples and documentation

---

## MCP Server Architecture

### Technology Stack

- **Runtime**: Node.js 18+ with TypeScript
- **MCP SDK**: `@modelcontextprotocol/sdk` (^1.0.0)
- **Qdrant Client**: `@qdrant/js-client-rest` (^1.8.0)
- **Transport**: stdio (standard input/output)

### Package Structure

```
@pm-agents/mcp-qdrant/
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── tools/
│   │   ├── collection.ts     # Collection management tools
│   │   ├── search.ts         # Search tools
│   │   ├── upsert.ts         # Data insertion tools
│   │   └── admin.ts          # Admin tools
│   ├── qdrant/
│   │   ├── client.ts         # Qdrant client wrapper
│   │   └── schemas.ts        # Type definitions
│   ├── utils/
│   │   ├── validation.ts     # Input validation
│   │   └── errors.ts         # Error handling
│   └── config.ts             # Configuration management
├── tests/
│   ├── integration/          # Integration tests with Qdrant
│   └── unit/                 # Unit tests
├── package.json
├── tsconfig.json
└── README.md
```

---

## MCP Tools Specification

### 1. Collection Management Tools

#### `qdrant_list_collections`

List all collections in Qdrant.

**Input Schema**: None (empty object)

```json
{}
```

**Output Schema**:
```json
{
  "collections": [
    {
      "name": "string",
      "vectors_count": "number",
      "points_count": "number",
      "status": "green|yellow|red"
    }
  ]
}
```

**Implementation**:
```typescript
async function listCollections(): Promise<ListCollectionsResponse> {
  const client = getQdrantClient()
  const response = await client.getCollections()

  return {
    collections: response.collections.map(col => ({
      name: col.name,
      vectors_count: col.vectors_count ?? 0,
      points_count: col.points_count ?? 0,
      status: col.status
    }))
  }
}
```

**Error Handling**:
- Connection errors → Retry with exponential backoff (3 attempts)
- Timeout → Return empty list with warning
- Authentication errors → Fail immediately with clear message

---

#### `qdrant_create_collection`

Create a new collection with specified vector configuration.

**Input Schema**:
```json
{
  "name": "string (required)",
  "vector_size": "number (required, default: 384)",
  "distance": "Cosine|Euclid|Dot (default: Cosine)",
  "on_disk_payload": "boolean (default: false)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "collection_name": "string",
  "message": "string"
}
```

**Implementation**:
```typescript
async function createCollection(params: CreateCollectionParams): Promise<CreateCollectionResponse> {
  const { name, vector_size = 384, distance = "Cosine", on_disk_payload = false } = params

  // Validate collection name (kebab-case, alphanumeric + hyphens)
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(name)) {
    throw new ValidationError("Collection name must be kebab-case")
  }

  const client = getQdrantClient()

  // Check if collection exists
  try {
    await client.getCollection(name)
    return {
      success: false,
      collection_name: name,
      message: "Collection already exists"
    }
  } catch (error) {
    // Collection doesn't exist, proceed with creation
  }

  await client.createCollection(name, {
    vectors: {
      size: vector_size,
      distance: distance
    },
    on_disk_payload: on_disk_payload
  })

  return {
    success: true,
    collection_name: name,
    message: `Collection '${name}' created successfully`
  }
}
```

**Validation Rules**:
- `name`: Required, kebab-case, 1-64 characters
- `vector_size`: Required, positive integer (common: 384, 768, 1536)
- `distance`: Must be one of ["Cosine", "Euclid", "Dot"]

---

#### `qdrant_get_collection_info`

Get detailed information about a collection.

**Input Schema**:
```json
{
  "collection_name": "string (required)"
}
```

**Output Schema**:
```json
{
  "name": "string",
  "vectors_count": "number",
  "points_count": "number",
  "status": "green|yellow|red",
  "optimizer_status": "string",
  "vector_size": "number",
  "distance": "Cosine|Euclid|Dot",
  "indexed_vectors_count": "number"
}
```

---

#### `qdrant_delete_collection`

Delete a collection (destructive operation - requires confirmation).

**Input Schema**:
```json
{
  "collection_name": "string (required)",
  "confirm": "boolean (required, must be true)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "collection_name": "string",
  "message": "string"
}
```

**Safety Features**:
- Requires explicit `confirm: true` parameter
- Logs deletion with timestamp
- Returns error if collection doesn't exist (idempotent)

---

### 2. Search Tools

#### `qdrant_search`

Search for similar vectors in a collection.

**Input Schema**:
```json
{
  "collection_name": "string (required)",
  "query_vector": "number[] (required)",
  "limit": "number (default: 10, max: 100)",
  "score_threshold": "number (default: 0.0, range: 0-1)",
  "filter": "object (optional, Qdrant filter syntax)",
  "with_payload": "boolean (default: true)",
  "with_vector": "boolean (default: false)"
}
```

**Output Schema**:
```json
{
  "results": [
    {
      "id": "string|number",
      "score": "number",
      "payload": "object (if with_payload=true)",
      "vector": "number[] (if with_vector=true)"
    }
  ],
  "query_time_ms": "number"
}
```

**Implementation**:
```typescript
async function search(params: SearchParams): Promise<SearchResponse> {
  const {
    collection_name,
    query_vector,
    limit = 10,
    score_threshold = 0.0,
    filter,
    with_payload = true,
    with_vector = false
  } = params

  // Validate query vector
  if (!Array.isArray(query_vector) || query_vector.length === 0) {
    throw new ValidationError("query_vector must be a non-empty array")
  }

  const startTime = Date.now()
  const client = getQdrantClient()

  const searchResult = await client.search(collection_name, {
    vector: query_vector,
    limit: Math.min(limit, 100),
    score_threshold: score_threshold,
    filter: filter,
    with_payload: with_payload,
    with_vector: with_vector
  })

  const queryTime = Date.now() - startTime

  return {
    results: searchResult.map(result => ({
      id: result.id,
      score: result.score,
      payload: with_payload ? result.payload : undefined,
      vector: with_vector ? result.vector : undefined
    })),
    query_time_ms: queryTime
  }
}
```

**Performance Expectations**:
- Query time: <500ms for collections <100k points
- Query time: <2s for collections <1M points
- Concurrent queries: Support up to 10 simultaneous searches

---

#### `qdrant_search_batch`

Search multiple query vectors in a single request (more efficient than multiple calls).

**Input Schema**:
```json
{
  "collection_name": "string (required)",
  "queries": [
    {
      "query_vector": "number[] (required)",
      "limit": "number (default: 10)",
      "score_threshold": "number (default: 0.0)",
      "filter": "object (optional)"
    }
  ]
}
```

**Output Schema**:
```json
{
  "results": [
    {
      "results": [...],
      "query_index": "number"
    }
  ],
  "total_query_time_ms": "number"
}
```

---

### 3. Data Insertion Tools

#### `qdrant_upsert`

Insert or update points in a collection.

**Input Schema**:
```json
{
  "collection_name": "string (required)",
  "points": [
    {
      "id": "string|number (required)",
      "vector": "number[] (required)",
      "payload": "object (optional)"
    }
  ],
  "wait": "boolean (default: true)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "points_inserted": "number",
  "operation_time_ms": "number",
  "message": "string"
}
```

**Implementation**:
```typescript
async function upsert(params: UpsertParams): Promise<UpsertResponse> {
  const { collection_name, points, wait = true } = params

  // Validate points
  if (!Array.isArray(points) || points.length === 0) {
    throw new ValidationError("points must be a non-empty array")
  }

  // Validate each point
  for (const point of points) {
    if (!point.id) {
      throw new ValidationError("Each point must have an 'id'")
    }
    if (!Array.isArray(point.vector) || point.vector.length === 0) {
      throw new ValidationError("Each point must have a non-empty 'vector'")
    }
  }

  const startTime = Date.now()
  const client = getQdrantClient()

  await client.upsert(collection_name, {
    wait: wait,
    points: points.map(p => ({
      id: p.id,
      vector: p.vector,
      payload: p.payload ?? {}
    }))
  })

  const operationTime = Date.now() - startTime

  return {
    success: true,
    points_inserted: points.length,
    operation_time_ms: operationTime,
    message: `Successfully upserted ${points.length} points`
  }
}
```

**Batch Processing**:
- Recommended batch size: 100-500 points per request
- Large datasets: Use multiple upsert calls with batching
- Progress tracking: Return count of points inserted

---

#### `qdrant_delete_points`

Delete specific points from a collection.

**Input Schema**:
```json
{
  "collection_name": "string (required)",
  "points": "number[]|string[] (required, point IDs)",
  "wait": "boolean (default: true)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "points_deleted": "number",
  "message": "string"
}
```

---

### 4. Admin Tools

#### `qdrant_scroll`

Retrieve all points from a collection (paginated).

**Input Schema**:
```json
{
  "collection_name": "string (required)",
  "limit": "number (default: 100, max: 1000)",
  "offset": "string|number (optional, pagination cursor)",
  "with_payload": "boolean (default: true)",
  "with_vector": "boolean (default: false)",
  "filter": "object (optional)"
}
```

**Output Schema**:
```json
{
  "points": [
    {
      "id": "string|number",
      "payload": "object",
      "vector": "number[]"
    }
  ],
  "next_offset": "string|number|null"
}
```

---

#### `qdrant_count`

Count points in a collection (with optional filter).

**Input Schema**:
```json
{
  "collection_name": "string (required)",
  "filter": "object (optional, Qdrant filter syntax)"
}
```

**Output Schema**:
```json
{
  "count": "number"
}
```

---

## Configuration

### Environment Variables

```bash
# Qdrant connection (required)
QDRANT_URL=http://localhost:6333

# Authentication (optional, for Qdrant Cloud)
QDRANT_API_KEY=your-api-key

# Performance tuning (optional)
QDRANT_TIMEOUT_MS=30000
QDRANT_MAX_RETRIES=3
QDRANT_BATCH_SIZE=500
```

### Configuration File

`mcp-qdrant-config.json` (optional, for local overrides):
```json
{
  "qdrant": {
    "url": "http://localhost:6333",
    "timeout_ms": 30000,
    "max_retries": 3,
    "batch_size": 500
  },
  "logging": {
    "level": "info",
    "log_queries": true,
    "log_performance": true
  }
}
```

---

## Error Handling

### Error Categories

#### 1. Connection Errors
- **Cause**: Qdrant server unreachable
- **Recovery**: Retry with exponential backoff (3 attempts: 1s, 2s, 4s)
- **User Message**: "Cannot connect to Qdrant server at {url}. Ensure Qdrant is running."

#### 2. Authentication Errors
- **Cause**: Invalid API key
- **Recovery**: None (fail immediately)
- **User Message**: "Qdrant authentication failed. Check QDRANT_API_KEY."

#### 3. Validation Errors
- **Cause**: Invalid input parameters
- **Recovery**: None (fail immediately)
- **User Message**: Specific validation message (e.g., "vector_size must be positive integer")

#### 4. Not Found Errors
- **Cause**: Collection or point doesn't exist
- **Recovery**: Return empty result or create collection (if appropriate)
- **User Message**: "Collection '{name}' not found. Create it first with qdrant_create_collection."

#### 5. Timeout Errors
- **Cause**: Query takes too long
- **Recovery**: Cancel query, return partial results if available
- **User Message**: "Query timed out after {timeout}ms. Try reducing limit or adding filters."

### Error Response Schema

```json
{
  "error": {
    "code": "CONNECTION_ERROR|AUTH_ERROR|VALIDATION_ERROR|NOT_FOUND|TIMEOUT",
    "message": "string",
    "details": "object (optional)",
    "retry_after_ms": "number (optional, for transient errors)"
  }
}
```

---

## Performance Optimization

### Connection Pooling
```typescript
// Maintain persistent connection to Qdrant
let qdrantClient: QdrantClient | null = null

function getQdrantClient(): QdrantClient {
  if (!qdrantClient) {
    qdrantClient = new QdrantClient({
      url: process.env.QDRANT_URL || 'http://localhost:6333',
      apiKey: process.env.QDRANT_API_KEY,
      timeout: parseInt(process.env.QDRANT_TIMEOUT_MS || '30000')
    })
  }
  return qdrantClient
}
```

### Query Optimization
- **Use filters**: Narrow search space before vector similarity
- **Batch operations**: Use `qdrant_search_batch` for multiple queries
- **Limit results**: Request only what you need (default: 10, max: 100)
- **Disable vectors**: Set `with_vector=false` if not needed (reduces payload size)

### Indexing Strategy
- **HNSW index**: Default, optimized for high-recall search
- **On-disk payloads**: Enable for large datasets (>1M points)
- **Quantization**: Use scalar quantization for 4x memory reduction (slight accuracy trade-off)

---

## Testing Strategy

### Unit Tests

**Test Coverage Targets**: 90%+ for all tool functions

**Key Test Cases**:
```typescript
describe('qdrant_create_collection', () => {
  it('creates collection with default parameters', async () => {
    const result = await createCollection({ name: 'test-collection', vector_size: 384 })
    expect(result.success).toBe(true)
  })

  it('rejects invalid collection names', async () => {
    await expect(createCollection({ name: 'Invalid Name', vector_size: 384 }))
      .rejects.toThrow(ValidationError)
  })

  it('returns false when collection exists', async () => {
    await createCollection({ name: 'test-collection', vector_size: 384 })
    const result = await createCollection({ name: 'test-collection', vector_size: 384 })
    expect(result.success).toBe(false)
  })
})

describe('qdrant_search', () => {
  it('returns top-k results', async () => {
    const result = await search({
      collection_name: 'test-collection',
      query_vector: [0.1, 0.2, ..., 0.384],
      limit: 5
    })
    expect(result.results.length).toBeLessThanOrEqual(5)
  })

  it('filters by score threshold', async () => {
    const result = await search({
      collection_name: 'test-collection',
      query_vector: [0.1, 0.2, ..., 0.384],
      score_threshold: 0.8
    })
    result.results.forEach(r => expect(r.score).toBeGreaterThanOrEqual(0.8))
  })
})
```

### Integration Tests

**Test Environment**: Docker Compose with Qdrant container

```yaml
version: '3'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
```

**Test Cases**:
1. Full workflow: Create collection → Upsert → Search → Delete
2. Large dataset: Index 10k points, measure search latency
3. Concurrent operations: 10 simultaneous searches
4. Error handling: Test with Qdrant server down

### Performance Benchmarks

**Target Metrics**:
- Collection creation: <500ms
- Upsert (100 points): <200ms
- Search (10 results): <100ms for <10k points
- Search (10 results): <500ms for <100k points

---

## Installation

### NPM Package

```bash
npm install -g @pm-agents/mcp-qdrant
```

### Claude Code MCP Configuration

Add to `~/.claude/mcp_servers.json` (user-level configuration):

```json
{
  "mcpServers": {
    "qdrant": {
      "command": "npx",
      "args": ["-y", "@pm-agents/mcp-qdrant"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": ""
      }
    }
  }
}
```

### Verification

```bash
# Test MCP server
echo '{"method":"tools/list"}' | npx @pm-agents/mcp-qdrant

# Expected output: List of all qdrant_* tools
```

---

## Integration with PM-Agents

### Agent Usage Pattern

```python
# Qdrant Vector Agent using MCP tool
async def index_codebase(self, project_path: str) -> IndexingResponse:
    # 1. Parse code files
    code_chunks = self.parse_codebase(project_path)

    # 2. Generate embeddings
    embeddings = self.generate_embeddings(code_chunks)

    # 3. Upsert to Qdrant via MCP
    collection_name = f"{project_name}-codebase"

    # Create collection if needed
    await self.mcp_call("qdrant_create_collection", {
        "name": collection_name,
        "vector_size": 384,
        "distance": "Cosine"
    })

    # Batch upsert
    points = [
        {
            "id": chunk.id,
            "vector": embedding,
            "payload": {
                "file_path": chunk.file_path,
                "content": chunk.content,
                "language": chunk.language,
                "type": chunk.type  # function, class, comment, etc.
            }
        }
        for chunk, embedding in zip(code_chunks, embeddings)
    ]

    await self.mcp_call("qdrant_upsert", {
        "collection_name": collection_name,
        "points": points,
        "wait": True
    })

    return IndexingResponse(indexed_chunks=len(points))

async def search_codebase(self, query: str, project_name: str) -> List[CodeChunk]:
    # 1. Generate query embedding
    query_embedding = self.generate_embedding(query)

    # 2. Search Qdrant via MCP
    results = await self.mcp_call("qdrant_search", {
        "collection_name": f"{project_name}-codebase",
        "query_vector": query_embedding,
        "limit": 10,
        "score_threshold": 0.7,
        "with_payload": True
    })

    # 3. Return code chunks
    return [
        CodeChunk(
            file_path=r["payload"]["file_path"],
            content=r["payload"]["content"],
            score=r["score"]
        )
        for r in results["results"]
    ]
```

---

## Future Enhancements

### Post-MVP Features

1. **Hybrid Search**: Combine vector search with keyword filtering
2. **Recommendation API**: "Find similar code" based on current context
3. **Clustering**: Group similar code chunks automatically
4. **Collection Templates**: Pre-configured collections for common use cases
5. **Backup/Restore**: Export/import collections
6. **Analytics Dashboard**: Query metrics, collection stats, usage patterns
7. **Multi-tenancy**: Support multiple projects with namespace isolation

---

## Security Considerations

### Input Validation
- Sanitize collection names (prevent injection attacks)
- Validate vector dimensions (prevent memory exhaustion)
- Limit batch sizes (prevent DoS)

### Authentication
- Support API key authentication for Qdrant Cloud
- Rotate keys regularly (document best practices)

### Access Control
- MCP server runs with user permissions (no privilege escalation)
- Read-only mode option (disable destructive operations)

---

## Monitoring and Logging

### Metrics to Track
- Query latency (p50, p95, p99)
- Error rate by error type
- Collection sizes (points, vectors)
- API call volume

### Logging Format
```json
{
  "timestamp": "2025-10-29T10:15:30Z",
  "level": "info",
  "tool": "qdrant_search",
  "collection": "pm-agents-codebase",
  "query_time_ms": 120,
  "results_count": 10
}
```

---

## Support and Maintenance

### Documentation
- API reference: https://pm-agents.dev/mcp/qdrant
- Examples: https://github.com/pm-agents/examples
- Troubleshooting: https://pm-agents.dev/docs/troubleshooting

### Issue Reporting
- GitHub Issues: https://github.com/pm-agents/mcp-qdrant/issues
- Bug template includes: MCP version, Qdrant version, error logs

### Versioning
- Semantic versioning (semver)
- Backwards compatibility for minor/patch versions
- Migration guides for major versions

---

## Implementation Checklist

- [ ] Set up TypeScript project structure
- [ ] Implement Qdrant client wrapper
- [ ] Implement all 11 MCP tools
- [ ] Add input validation for all tools
- [ ] Add error handling with retry logic
- [ ] Write unit tests (90%+ coverage)
- [ ] Write integration tests with Docker
- [ ] Create performance benchmarks
- [ ] Write README with installation instructions
- [ ] Publish to npm registry
- [ ] Add to Claude Code MCP documentation
- [ ] Create example usage documentation
- [ ] Set up CI/CD pipeline (GitHub Actions)

---

**Last Updated**: 2025-10-29
**Status**: Specification Complete - Ready for Implementation
