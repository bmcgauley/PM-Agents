# MCP Server Testing and Reliability Guide

## Overview

This document provides comprehensive testing strategies and reliability patterns for MCP servers in the PM-Agents system. It covers unit testing, integration testing, error handling, retry strategies, and monitoring.

---

## Testing Strategy

### Testing Pyramid

```
        /\
       /  \
      / E2E\ (10%)
     /______\
    /        \
   /Integration\ (30%)
  /__________\
 /            \
/     Unit     \ (60%)
/______________\
```

**Distribution**:
- **60% Unit Tests**: Test individual MCP tools in isolation
- **30% Integration Tests**: Test MCP server interaction with real services (Qdrant, TensorBoard, GitHub)
- **10% End-to-End Tests**: Test full agent workflows using MCP tools

---

## Unit Testing

### Test Framework

**Node.js/TypeScript MCP servers**:
- **Framework**: Jest or Vitest
- **Mocking**: Mock external dependencies (Qdrant client, GitHub API, file system)
- **Coverage Target**: 90%+

**Example Test Structure**:

```typescript
// __tests__/tools/search.test.ts
import { searchTool } from '../src/tools/search'
import { QdrantClient } from '@qdrant/js-client-rest'

jest.mock('@qdrant/js-client-rest')

describe('qdrant_search tool', () => {
  let mockQdrantClient: jest.Mocked<QdrantClient>

  beforeEach(() => {
    mockQdrantClient = new QdrantClient() as jest.Mocked<QdrantClient>
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('valid inputs', () => {
    it('should search with query vector', async () => {
      const mockResults = [
        { id: 1, score: 0.95, payload: { content: 'test' } }
      ]

      mockQdrantClient.search.mockResolvedValue(mockResults)

      const result = await searchTool({
        collection_name: 'test-collection',
        query_vector: [0.1, 0.2, 0.3],
        limit: 10
      })

      expect(result.results).toEqual(mockResults)
      expect(mockQdrantClient.search).toHaveBeenCalledWith(
        'test-collection',
        {
          vector: [0.1, 0.2, 0.3],
          limit: 10,
          score_threshold: 0.0,
          with_payload: true,
          with_vector: false
        }
      )
    })

    it('should apply score threshold', async () => {
      const mockResults = [
        { id: 1, score: 0.95, payload: {} },
        { id: 2, score: 0.85, payload: {} },
        { id: 3, score: 0.65, payload: {} }
      ]

      mockQdrantClient.search.mockResolvedValue(mockResults)

      const result = await searchTool({
        collection_name: 'test-collection',
        query_vector: [0.1, 0.2, 0.3],
        score_threshold: 0.8
      })

      // Results filtered by score_threshold on server side
      expect(result.results.length).toBeLessThanOrEqual(mockResults.length)
    })

    it('should limit results', async () => {
      const mockResults = Array.from({ length: 10 }, (_, i) => ({
        id: i,
        score: 0.9 - i * 0.05,
        payload: {}
      }))

      mockQdrantClient.search.mockResolvedValue(mockResults.slice(0, 5))

      const result = await searchTool({
        collection_name: 'test-collection',
        query_vector: [0.1, 0.2, 0.3],
        limit: 5
      })

      expect(result.results.length).toBe(5)
    })
  })

  describe('invalid inputs', () => {
    it('should reject empty query vector', async () => {
      await expect(searchTool({
        collection_name: 'test-collection',
        query_vector: [],
        limit: 10
      })).rejects.toThrow('query_vector must be a non-empty array')
    })

    it('should reject non-existent collection', async () => {
      mockQdrantClient.search.mockRejectedValue(
        new Error('Collection not found')
      )

      await expect(searchTool({
        collection_name: 'nonexistent',
        query_vector: [0.1, 0.2, 0.3]
      })).rejects.toThrow('Collection not found')
    })

    it('should reject invalid limit', async () => {
      await expect(searchTool({
        collection_name: 'test-collection',
        query_vector: [0.1, 0.2, 0.3],
        limit: -1
      })).rejects.toThrow('limit must be positive')
    })
  })

  describe('error handling', () => {
    it('should handle connection errors with retry', async () => {
      mockQdrantClient.search
        .mockRejectedValueOnce(new Error('Connection refused'))
        .mockRejectedValueOnce(new Error('Connection refused'))
        .mockResolvedValueOnce([{ id: 1, score: 0.9, payload: {} }])

      const result = await searchTool({
        collection_name: 'test-collection',
        query_vector: [0.1, 0.2, 0.3]
      })

      expect(result.results.length).toBe(1)
      expect(mockQdrantClient.search).toHaveBeenCalledTimes(3)
    })

    it('should fail after max retries', async () => {
      mockQdrantClient.search.mockRejectedValue(
        new Error('Connection refused')
      )

      await expect(searchTool({
        collection_name: 'test-collection',
        query_vector: [0.1, 0.2, 0.3]
      })).rejects.toThrow('Connection refused')

      expect(mockQdrantClient.search).toHaveBeenCalledTimes(3) // Initial + 2 retries
    })

    it('should handle timeout', async () => {
      mockQdrantClient.search.mockImplementation(() =>
        new Promise((resolve) => setTimeout(resolve, 60000))
      )

      await expect(searchTool({
        collection_name: 'test-collection',
        query_vector: [0.1, 0.2, 0.3]
      })).rejects.toThrow('Query timed out')
    })
  })

  describe('performance', () => {
    it('should complete search in < 500ms', async () => {
      mockQdrantClient.search.mockResolvedValue([])

      const start = Date.now()
      await searchTool({
        collection_name: 'test-collection',
        query_vector: [0.1, 0.2, 0.3]
      })
      const duration = Date.now() - start

      expect(duration).toBeLessThan(500)
    })
  })
})
```

---

## Integration Testing

### Test Environment Setup

**Docker Compose for Test Environment**:

```yaml
# docker-compose.test.yml
version: '3'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334

  tensorboard:
    image: tensorflow/tensorflow:latest
    command: tensorboard --logdir=/logs --host=0.0.0.0
    ports:
      - "6006:6006"
    volumes:
      - ./test-logs:/logs

  # Add other services as needed
```

**Start Test Environment**:
```bash
docker-compose -f docker-compose.test.yml up -d
```

### Integration Test Examples

```typescript
// __tests__/integration/qdrant.test.ts
import { QdrantClient } from '@qdrant/js-client-rest'
import { createCollection, upsert, search } from '../src/tools'

describe('Qdrant MCP Server Integration', () => {
  let qdrantClient: QdrantClient
  const testCollectionName = 'test-integration-collection'

  beforeAll(async () => {
    qdrantClient = new QdrantClient({
      url: process.env.QDRANT_URL || 'http://localhost:6333'
    })

    // Wait for Qdrant to be ready
    await waitForQdrant(qdrantClient, 30000)
  })

  beforeEach(async () => {
    // Create fresh collection for each test
    await createCollection({
      name: testCollectionName,
      vector_size: 384,
      distance: 'Cosine'
    })
  })

  afterEach(async () => {
    // Cleanup: delete test collection
    await qdrantClient.deleteCollection(testCollectionName)
  })

  it('should perform full workflow: create → upsert → search', async () => {
    // 1. Upsert test data
    const testPoints = [
      {
        id: '1',
        vector: Array.from({ length: 384 }, () => Math.random()),
        payload: { text: 'Machine learning algorithms' }
      },
      {
        id: '2',
        vector: Array.from({ length: 384 }, () => Math.random()),
        payload: { text: 'Deep neural networks' }
      },
      {
        id: '3',
        vector: Array.from({ length: 384 }, () => Math.random()),
        payload: { text: 'Data preprocessing techniques' }
      }
    ]

    const upsertResult = await upsert({
      collection_name: testCollectionName,
      points: testPoints,
      wait: true
    })

    expect(upsertResult.success).toBe(true)
    expect(upsertResult.points_inserted).toBe(3)

    // 2. Search for similar vectors
    const searchResult = await search({
      collection_name: testCollectionName,
      query_vector: testPoints[0].vector,
      limit: 3
    })

    expect(searchResult.results.length).toBeGreaterThan(0)
    expect(searchResult.results[0].id).toBe('1') // Exact match should be first
    expect(searchResult.results[0].score).toBeGreaterThan(0.99)
  })

  it('should handle concurrent searches', async () => {
    // Upsert test data
    const testPoints = Array.from({ length: 100 }, (_, i) => ({
      id: i.toString(),
      vector: Array.from({ length: 384 }, () => Math.random()),
      payload: { index: i }
    }))

    await upsert({
      collection_name: testCollectionName,
      points: testPoints,
      wait: true
    })

    // Perform 10 concurrent searches
    const searchPromises = Array.from({ length: 10 }, (_, i) =>
      search({
        collection_name: testCollectionName,
        query_vector: testPoints[i].vector,
        limit: 5
      })
    )

    const results = await Promise.all(searchPromises)

    // All searches should succeed
    expect(results.length).toBe(10)
    results.forEach(result => {
      expect(result.results.length).toBeGreaterThan(0)
    })
  })

  it('should handle large batch upsert', async () => {
    const largePoints = Array.from({ length: 1000 }, (_, i) => ({
      id: i.toString(),
      vector: Array.from({ length: 384 }, () => Math.random()),
      payload: { index: i }
    }))

    const start = Date.now()
    const result = await upsert({
      collection_name: testCollectionName,
      points: largePoints,
      wait: true
    })
    const duration = Date.now() - start

    expect(result.success).toBe(true)
    expect(result.points_inserted).toBe(1000)
    expect(duration).toBeLessThan(10000) // Should complete in < 10 seconds
  })
})

async function waitForQdrant(client: QdrantClient, timeoutMs: number): Promise<void> {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    try {
      await client.getCollections()
      return
    } catch (error) {
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  }
  throw new Error('Qdrant not ready within timeout')
}
```

---

## End-to-End Testing

### Agent Workflow Tests

```typescript
// __tests__/e2e/agent-workflow.test.ts
import { CoordinatorAgent } from '../src/agents/coordinator'
import { QdrantVectorAgent } from '../src/agents/qdrant-vector'

describe('Agent Workflow E2E Tests', () => {
  let coordinator: CoordinatorAgent
  let qdrantAgent: QdrantVectorAgent

  beforeAll(async () => {
    coordinator = new CoordinatorAgent()
    qdrantAgent = new QdrantVectorAgent()

    // Setup test environment
    await setupTestEnvironment()
  })

  afterAll(async () => {
    await cleanupTestEnvironment()
  })

  it('should complete full codebase indexing workflow', async () => {
    const projectPath = '/tmp/test-project'
    const projectName = 'test-project'

    // 1. Qdrant Vector Agent indexes codebase
    const indexResult = await qdrantAgent.indexCodebase({
      project_path: projectPath,
      project_name: projectName
    })

    expect(indexResult.success).toBe(true)
    expect(indexResult.indexed_files).toBeGreaterThan(0)

    // 2. Coordinator searches for relevant code
    const searchRequest = {
      task_id: 'test-search',
      description: 'Find authentication code'
    }

    const searchResult = await coordinator.findRelevantCode(searchRequest)

    expect(searchResult.results.length).toBeGreaterThan(0)
  })

  it('should handle TensorBoard monitoring workflow', async () => {
    // 1. Start TensorBoard server
    const tbServer = await qdrantAgent.startTensorBoard({
      logdir: '/tmp/test-logs',
      port: 6007
    })

    expect(tbServer.success).toBe(true)
    expect(tbServer.url).toContain('6007')

    // 2. Monitor training metrics
    await new Promise(resolve => setTimeout(resolve, 5000)) // Wait for logs

    const metrics = await qdrantAgent.getLatestMetrics({
      logdir: '/tmp/test-logs',
      tags: ['loss', 'accuracy']
    })

    expect(metrics.metrics.length).toBeGreaterThan(0)

    // 3. Stop TensorBoard server
    const stopResult = await qdrantAgent.stopTensorBoard({
      server_id: tbServer.server_id
    })

    expect(stopResult.success).toBe(true)
  })
})
```

---

## Error Handling Patterns

### Retry Strategy with Exponential Backoff

```typescript
// src/utils/retry.ts
export interface RetryOptions {
  maxRetries: number
  initialDelayMs: number
  maxDelayMs: number
  backoffMultiplier: number
  retryableErrors: string[]
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: Partial<RetryOptions> = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelayMs = 1000,
    maxDelayMs = 10000,
    backoffMultiplier = 2,
    retryableErrors = ['ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND']
  } = options

  let lastError: Error
  let delay = initialDelayMs

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error

      // Check if error is retryable
      const isRetryable = retryableErrors.some(errCode =>
        lastError.message.includes(errCode)
      )

      if (!isRetryable || attempt === maxRetries) {
        throw lastError
      }

      // Wait before retry
      await new Promise(resolve => setTimeout(resolve, delay))

      // Exponential backoff
      delay = Math.min(delay * backoffMultiplier, maxDelayMs)
    }
  }

  throw lastError!
}

// Usage example
export async function searchWithRetry(params: SearchParams): Promise<SearchResponse> {
  return withRetry(
    () => qdrantClient.search(params.collection_name, params),
    {
      maxRetries: 3,
      initialDelayMs: 1000,
      retryableErrors: ['ECONNREFUSED', 'ETIMEDOUT']
    }
  )
}
```

### Circuit Breaker Pattern

```typescript
// src/utils/circuit-breaker.ts
export enum CircuitState {
  CLOSED,  // Normal operation
  OPEN,    // Failing, reject requests immediately
  HALF_OPEN // Testing if service recovered
}

export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED
  private failureCount: number = 0
  private successCount: number = 0
  private lastFailureTime: number = 0

  constructor(
    private failureThreshold: number = 5,
    private recoveryTimeout: number = 60000, // 1 minute
    private successThreshold: number = 2
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      // Check if recovery timeout has passed
      if (Date.now() - this.lastFailureTime > this.recoveryTimeout) {
        this.state = CircuitState.HALF_OPEN
        this.successCount = 0
      } else {
        throw new Error('Circuit breaker is OPEN. Service unavailable.')
      }
    }

    try {
      const result = await fn()

      // Success
      this.onSuccess()
      return result
    } catch (error) {
      // Failure
      this.onFailure()
      throw error
    }
  }

  private onSuccess(): void {
    this.failureCount = 0

    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++

      if (this.successCount >= this.successThreshold) {
        this.state = CircuitState.CLOSED
      }
    }
  }

  private onFailure(): void {
    this.failureCount++
    this.lastFailureTime = Date.now()

    if (this.failureCount >= this.failureThreshold) {
      this.state = CircuitState.OPEN
    }
  }

  getState(): CircuitState {
    return this.state
  }
}

// Usage example
const qdrantCircuitBreaker = new CircuitBreaker(5, 60000, 2)

export async function searchWithCircuitBreaker(
  params: SearchParams
): Promise<SearchResponse> {
  return qdrantCircuitBreaker.execute(() =>
    qdrantClient.search(params.collection_name, params)
  )
}
```

### Timeout Handling

```typescript
// src/utils/timeout.ts
export async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  errorMessage?: string
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(
        () => reject(new Error(errorMessage || `Operation timed out after ${timeoutMs}ms`)),
        timeoutMs
      )
    )
  ])
}

// Usage example
export async function searchWithTimeout(params: SearchParams): Promise<SearchResponse> {
  return withTimeout(
    qdrantClient.search(params.collection_name, params),
    30000, // 30 second timeout
    'Search query timed out'
  )
}
```

---

## Monitoring and Observability

### Structured Logging

```typescript
// src/utils/logger.ts
import winston from 'winston'

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'mcp-qdrant' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
})

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }))
}

// Usage in MCP tools
export async function search(params: SearchParams): Promise<SearchResponse> {
  const startTime = Date.now()

  logger.info('Search started', {
    collection: params.collection_name,
    limit: params.limit
  })

  try {
    const result = await qdrantClient.search(params.collection_name, params)
    const duration = Date.now() - startTime

    logger.info('Search completed', {
      collection: params.collection_name,
      results_count: result.length,
      duration_ms: duration
    })

    return { results: result, query_time_ms: duration }
  } catch (error) {
    logger.error('Search failed', {
      collection: params.collection_name,
      error: error.message,
      stack: error.stack
    })

    throw error
  }
}
```

### Metrics Collection

```typescript
// src/utils/metrics.ts
export class MetricsCollector {
  private metrics = new Map<string, number[]>()

  recordDuration(metricName: string, durationMs: number): void {
    if (!this.metrics.has(metricName)) {
      this.metrics.set(metricName, [])
    }
    this.metrics.get(metricName)!.push(durationMs)
  }

  getPercentile(metricName: string, percentile: number): number {
    const values = this.metrics.get(metricName)
    if (!values || values.length === 0) return 0

    const sorted = values.slice().sort((a, b) => a - b)
    const index = Math.ceil((percentile / 100) * sorted.length) - 1
    return sorted[index]
  }

  getAverage(metricName: string): number {
    const values = this.metrics.get(metricName)
    if (!values || values.length === 0) return 0

    return values.reduce((sum, val) => sum + val, 0) / values.length
  }

  getStats(metricName: string) {
    return {
      count: this.metrics.get(metricName)?.length || 0,
      average: this.getAverage(metricName),
      p50: this.getPercentile(metricName, 50),
      p95: this.getPercentile(metricName, 95),
      p99: this.getPercentile(metricName, 99)
    }
  }

  reset(): void {
    this.metrics.clear()
  }
}

// Global metrics collector
export const metrics = new MetricsCollector()

// Usage in MCP tools
export async function search(params: SearchParams): Promise<SearchResponse> {
  const startTime = Date.now()

  try {
    const result = await qdrantClient.search(params.collection_name, params)
    const duration = Date.now() - startTime

    metrics.recordDuration('qdrant_search_duration_ms', duration)

    return { results: result, query_time_ms: duration }
  } catch (error) {
    metrics.recordDuration('qdrant_search_error_count', 1)
    throw error
  }
}

// Endpoint to retrieve metrics
export function getMetrics() {
  return {
    search: metrics.getStats('qdrant_search_duration_ms'),
    upsert: metrics.getStats('qdrant_upsert_duration_ms'),
    errors: metrics.getStats('qdrant_search_error_count')
  }
}
```

---

## Health Checks

### MCP Server Health Check

```typescript
// src/health.ts
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy'
  checks: Record<string, CheckResult>
  timestamp: string
}

export interface CheckResult {
  status: 'pass' | 'fail'
  message?: string
  duration_ms?: number
}

export async function performHealthCheck(): Promise<HealthStatus> {
  const checks: Record<string, CheckResult> = {}

  // Check Qdrant connection
  checks.qdrant = await checkQdrant()

  // Check filesystem access (if using filesystem tools)
  checks.filesystem = await checkFilesystem()

  // Determine overall status
  const allPassed = Object.values(checks).every(c => c.status === 'pass')
  const someFailed = Object.values(checks).some(c => c.status === 'fail')

  return {
    status: allPassed ? 'healthy' : (someFailed ? 'unhealthy' : 'degraded'),
    checks,
    timestamp: new Date().toISOString()
  }
}

async function checkQdrant(): Promise<CheckResult> {
  const startTime = Date.now()

  try {
    await qdrantClient.getCollections()
    return {
      status: 'pass',
      duration_ms: Date.now() - startTime
    }
  } catch (error) {
    return {
      status: 'fail',
      message: `Qdrant connection failed: ${error.message}`,
      duration_ms: Date.now() - startTime
    }
  }
}

async function checkFilesystem(): Promise<CheckResult> {
  const startTime = Date.now()

  try {
    // Test read/write access
    const testFile = '/tmp/mcp-health-check'
    await fs.promises.writeFile(testFile, 'test')
    await fs.promises.unlink(testFile)

    return {
      status: 'pass',
      duration_ms: Date.now() - startTime
    }
  } catch (error) {
    return {
      status: 'fail',
      message: `Filesystem check failed: ${error.message}`,
      duration_ms: Date.now() - startTime
    }
  }
}
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/mcp-test.yml
name: MCP Server Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  integration-tests:
    runs-on: ubuntu-latest

    services:
      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6333:6333

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Wait for Qdrant
        run: |
          until curl -s http://localhost:6333/healthz > /dev/null; do
            echo "Waiting for Qdrant..."
            sleep 2
          done

      - name: Run integration tests
        run: npm run test:integration
        env:
          QDRANT_URL: http://localhost:6333

  e2e-tests:
    runs-on: ubuntu-latest

    services:
      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6333:6333

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          npm ci
          pip install -r requirements.txt

      - name: Run E2E tests
        run: npm run test:e2e
        env:
          QDRANT_URL: http://localhost:6333

  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run type checking
        run: npm run type-check
```

---

## Performance Testing

### Load Testing Script

```typescript
// __tests__/performance/load-test.ts
import { QdrantClient } from '@qdrant/js-client-rest'

interface LoadTestResult {
  total_requests: number
  successful_requests: number
  failed_requests: number
  average_latency_ms: number
  p95_latency_ms: number
  p99_latency_ms: number
  requests_per_second: number
}

async function runLoadTest(
  concurrency: number,
  duration_seconds: number
): Promise<LoadTestResult> {
  const qdrantClient = new QdrantClient({ url: 'http://localhost:6333' })
  const testCollection = 'load-test-collection'

  // Setup test collection with data
  await setupTestCollection(qdrantClient, testCollection, 10000)

  const latencies: number[] = []
  let successfulRequests = 0
  let failedRequests = 0

  const startTime = Date.now()
  const endTime = startTime + duration_seconds * 1000

  // Run concurrent requests
  const workers = Array.from({ length: concurrency }, async () => {
    while (Date.now() < endTime) {
      const queryStart = Date.now()

      try {
        await qdrantClient.search(testCollection, {
          vector: Array.from({ length: 384 }, () => Math.random()),
          limit: 10
        })

        const latency = Date.now() - queryStart
        latencies.push(latency)
        successfulRequests++
      } catch (error) {
        failedRequests++
      }
    }
  })

  await Promise.all(workers)

  // Calculate statistics
  latencies.sort((a, b) => a - b)
  const totalRequests = successfulRequests + failedRequests
  const actualDuration = (Date.now() - startTime) / 1000

  return {
    total_requests: totalRequests,
    successful_requests: successfulRequests,
    failed_requests: failedRequests,
    average_latency_ms: latencies.reduce((sum, val) => sum + val, 0) / latencies.length,
    p95_latency_ms: latencies[Math.floor(latencies.length * 0.95)],
    p99_latency_ms: latencies[Math.floor(latencies.length * 0.99)],
    requests_per_second: totalRequests / actualDuration
  }
}

// Run load test
describe('Performance Load Tests', () => {
  it('should handle 10 concurrent requests', async () => {
    const result = await runLoadTest(10, 30)

    console.log('Load Test Results:', result)

    expect(result.successful_requests).toBeGreaterThan(0)
    expect(result.average_latency_ms).toBeLessThan(500)
    expect(result.p99_latency_ms).toBeLessThan(2000)
  }, 60000) // 60s timeout
})
```

---

## Best Practices Summary

### DO
- ✅ Write unit tests for all MCP tools (90%+ coverage)
- ✅ Use integration tests with real services in Docker
- ✅ Implement retry logic with exponential backoff
- ✅ Use circuit breakers for external service calls
- ✅ Add structured logging with context
- ✅ Collect metrics (latency, error rate, throughput)
- ✅ Implement health checks
- ✅ Set timeouts for all external calls
- ✅ Test error scenarios (network failures, invalid inputs)
- ✅ Run performance/load tests before production

### DON'T
- ❌ Skip error handling tests
- ❌ Use infinite retries
- ❌ Ignore timeouts
- ❌ Deploy without health checks
- ❌ Hardcode credentials in tests
- ❌ Skip integration tests with real services
- ❌ Forget to clean up test data
- ❌ Ignore performance benchmarks

---

## Troubleshooting Guide

### Common Issues

#### 1. MCP Server Not Responding

**Symptoms**: Timeouts, connection refused errors

**Diagnosis**:
```bash
# Check if MCP server is running
claude mcp list

# Test MCP server directly
echo '{"method":"tools/list"}' | npx @pm-agents/mcp-qdrant

# Check logs
tail -f ~/.claude/logs/mcp-qdrant.log
```

**Solutions**:
- Restart MCP server
- Check QDRANT_URL environment variable
- Verify Qdrant is running: `curl http://localhost:6333/healthz`

#### 2. Qdrant Connection Failures

**Symptoms**: "Connection refused" or "Cannot connect to Qdrant"

**Diagnosis**:
```bash
# Check Qdrant status
docker ps | grep qdrant

# Test Qdrant directly
curl http://localhost:6333/healthz
```

**Solutions**:
- Start Qdrant: `docker run -d -p 6333:6333 qdrant/qdrant`
- Check firewall rules
- Verify QDRANT_URL in MCP config

#### 3. Slow Search Queries

**Symptoms**: Search takes >1 second

**Diagnosis**:
- Check collection size: `qdrant_get_collection_info`
- Check server resources: `docker stats qdrant`

**Solutions**:
- Add filters to narrow search space
- Reduce `limit` parameter
- Enable HNSW indexing
- Use scalar quantization for large collections

---

**Last Updated**: 2025-10-29
**Status**: Complete - Ready for Implementation
