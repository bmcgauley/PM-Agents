# TensorBoard MCP Server Specification

## Overview

The **@pm-agents/mcp-tensorboard** MCP server provides ML/DL experiment monitoring and visualization capabilities for the PM-Agents multi-agent system. It exposes TensorBoard operations through the Model Context Protocol, enabling agents to launch TensorBoard servers, query training metrics, and retrieve experiment data.

### Purpose

- **Experiment monitoring**: Track training progress and metrics in real-time
- **Model visualization**: View model architectures and computation graphs
- **Log management**: Access training logs and event files
- **Data export**: Extract metrics for analysis and reporting
- **Server lifecycle**: Start/stop TensorBoard servers as background services

### Target Agents

- **Python ML/DL Agent**: Primary consumer, manages all TensorBoard operations
- **Reporter Agent**: Retrieves metrics for documentation and reports
- **Supervisor Agent**: Monitors training progress and convergence

---

## MCP Server Architecture

### Technology Stack

- **Runtime**: Node.js 18+ with TypeScript
- **MCP SDK**: `@modelcontextprotocol/sdk` (^1.0.0)
- **TensorBoard**: Python `tensorboard` package (via subprocess)
- **Event File Parser**: `@tensorflow/tfjs-node` or custom parser
- **Process Management**: `child_process` with supervision
- **Transport**: stdio (standard input/output)

### Package Structure

```
@pm-agents/mcp-tensorboard/
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── tools/
│   │   ├── server.ts         # TensorBoard server management
│   │   ├── metrics.ts        # Metrics retrieval tools
│   │   ├── experiments.ts    # Experiment listing/info
│   │   └── export.ts         # Data export tools
│   ├── tensorboard/
│   │   ├── process.ts        # Process lifecycle management
│   │   ├── parser.ts         # Event file parser
│   │   └── client.ts         # TensorBoard API client
│   ├── utils/
│   │   ├── validation.ts     # Input validation
│   │   └── errors.ts         # Error handling
│   └── config.ts             # Configuration management
├── tests/
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
├── package.json
├── tsconfig.json
└── README.md
```

---

## MCP Tools Specification

### 1. Server Lifecycle Tools

#### `tensorboard_start_server`

Launch a TensorBoard server as a background service.

**Input Schema**:
```json
{
  "logdir": "string (required, path to log directory)",
  "port": "number (default: 6006)",
  "host": "string (default: localhost)",
  "reload_interval": "number (default: 30, seconds)",
  "name": "string (optional, server instance name)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "server_id": "string (UUID)",
  "url": "string (http://localhost:port)",
  "pid": "number",
  "logdir": "string",
  "message": "string"
}
```

**Implementation**:
```typescript
interface TensorBoardServer {
  id: string
  name?: string
  process: ChildProcess
  logdir: string
  port: number
  host: string
  url: string
  startTime: Date
}

const activeServers = new Map<string, TensorBoardServer>()

async function startTensorBoard(params: StartServerParams): Promise<StartServerResponse> {
  const {
    logdir,
    port = 6006,
    host = 'localhost',
    reload_interval = 30,
    name
  } = params

  // Validate logdir exists
  if (!fs.existsSync(logdir)) {
    throw new ValidationError(`Log directory not found: ${logdir}`)
  }

  // Check if port is available
  if (await isPortInUse(port)) {
    throw new Error(`Port ${port} is already in use. Choose a different port.`)
  }

  // Generate server ID
  const serverId = name || uuidv4()

  // Launch TensorBoard process
  const tbProcess = spawn('tensorboard', [
    '--logdir', logdir,
    '--port', port.toString(),
    '--host', host,
    '--reload_interval', reload_interval.toString(),
    '--bind_all'
  ], {
    detached: true,
    stdio: ['ignore', 'pipe', 'pipe']
  })

  // Wait for server to be ready
  await waitForServer(`http://${host}:${port}`, 30000)

  // Store server info
  const server: TensorBoardServer = {
    id: serverId,
    name: name,
    process: tbProcess,
    logdir: logdir,
    port: port,
    host: host,
    url: `http://${host}:${port}`,
    startTime: new Date()
  }

  activeServers.set(serverId, server)

  return {
    success: true,
    server_id: serverId,
    url: server.url,
    pid: tbProcess.pid,
    logdir: logdir,
    message: `TensorBoard server started at ${server.url}`
  }
}

async function waitForServer(url: string, timeoutMs: number): Promise<void> {
  const startTime = Date.now()
  while (Date.now() - startTime < timeoutMs) {
    try {
      const response = await fetch(url)
      if (response.ok) return
    } catch (error) {
      // Server not ready yet
    }
    await sleep(500)
  }
  throw new Error(`TensorBoard server failed to start within ${timeoutMs}ms`)
}
```

**Error Handling**:
- Log directory not found → Fail immediately
- Port in use → Suggest alternative port
- TensorBoard not installed → Provide installation instructions
- Server fails to start → Return stderr logs

---

#### `tensorboard_stop_server`

Stop a running TensorBoard server.

**Input Schema**:
```json
{
  "server_id": "string (required, UUID or name)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "server_id": "string",
  "message": "string"
}
```

**Implementation**:
```typescript
async function stopTensorBoard(params: StopServerParams): Promise<StopServerResponse> {
  const { server_id } = params

  const server = activeServers.get(server_id)
  if (!server) {
    throw new Error(`TensorBoard server '${server_id}' not found`)
  }

  // Gracefully terminate process
  server.process.kill('SIGTERM')

  // Wait for process to exit
  await new Promise<void>((resolve) => {
    server.process.on('exit', () => resolve())
    setTimeout(() => {
      // Force kill if not exited after 5 seconds
      server.process.kill('SIGKILL')
      resolve()
    }, 5000)
  })

  activeServers.delete(server_id)

  return {
    success: true,
    server_id: server_id,
    message: `TensorBoard server '${server_id}' stopped`
  }
}
```

---

#### `tensorboard_list_servers`

List all active TensorBoard servers.

**Input Schema**: None (empty object)

```json
{}
```

**Output Schema**:
```json
{
  "servers": [
    {
      "server_id": "string",
      "name": "string (optional)",
      "url": "string",
      "pid": "number",
      "logdir": "string",
      "uptime_seconds": "number",
      "status": "running|stopped"
    }
  ]
}
```

---

#### `tensorboard_get_server_status`

Get detailed status of a TensorBoard server.

**Input Schema**:
```json
{
  "server_id": "string (required)"
}
```

**Output Schema**:
```json
{
  "server_id": "string",
  "status": "running|stopped",
  "url": "string",
  "logdir": "string",
  "uptime_seconds": "number",
  "memory_usage_mb": "number (optional)",
  "cpu_percent": "number (optional)"
}
```

---

### 2. Experiment Discovery Tools

#### `tensorboard_list_experiments`

List all experiments (runs) in a log directory.

**Input Schema**:
```json
{
  "logdir": "string (required)",
  "recursive": "boolean (default: true)"
}
```

**Output Schema**:
```json
{
  "experiments": [
    {
      "name": "string (run name)",
      "path": "string (absolute path)",
      "start_time": "string (ISO 8601)",
      "last_modified": "string (ISO 8601)",
      "event_files": "number",
      "tags": "string[] (available metric tags)"
    }
  ]
}
```

**Implementation**:
```typescript
async function listExperiments(params: ListExperimentsParams): Promise<ListExperimentsResponse> {
  const { logdir, recursive = true } = params

  if (!fs.existsSync(logdir)) {
    throw new ValidationError(`Log directory not found: ${logdir}`)
  }

  const experiments: ExperimentInfo[] = []

  // Find all event files
  const eventFiles = recursive
    ? glob.sync(`${logdir}/**/events.out.tfevents.*`)
    : glob.sync(`${logdir}/events.out.tfevents.*`)

  // Group by run directory
  const runDirs = new Map<string, string[]>()
  for (const eventFile of eventFiles) {
    const runDir = path.dirname(eventFile)
    if (!runDirs.has(runDir)) {
      runDirs.set(runDir, [])
    }
    runDirs.get(runDir)!.push(eventFile)
  }

  // Extract experiment info
  for (const [runDir, files] of runDirs.entries()) {
    const runName = path.relative(logdir, runDir) || 'default'

    // Parse first event file to get start time and tags
    const eventData = await parseEventFile(files[0])

    experiments.push({
      name: runName,
      path: runDir,
      start_time: new Date(eventData.startTime * 1000).toISOString(),
      last_modified: fs.statSync(files[0]).mtime.toISOString(),
      event_files: files.length,
      tags: eventData.tags
    })
  }

  return { experiments }
}
```

---

### 3. Metrics Retrieval Tools

#### `tensorboard_get_scalars`

Retrieve scalar metrics from an experiment.

**Input Schema**:
```json
{
  "logdir": "string (required)",
  "run": "string (optional, default: all runs)",
  "tag": "string (optional, default: all tags)",
  "max_points": "number (default: 1000, for downsampling)"
}
```

**Output Schema**:
```json
{
  "scalars": [
    {
      "run": "string",
      "tag": "string",
      "data": [
        {
          "step": "number",
          "value": "number",
          "wall_time": "number (Unix timestamp)"
        }
      ]
    }
  ]
}
```

**Implementation**:
```typescript
async function getScalars(params: GetScalarsParams): Promise<GetScalarsResponse> {
  const { logdir, run, tag, max_points = 1000 } = params

  // Find event files for specified run
  const eventFiles = run
    ? glob.sync(`${logdir}/${run}/events.out.tfevents.*`)
    : glob.sync(`${logdir}/**/events.out.tfevents.*`)

  const scalars: ScalarData[] = []

  for (const eventFile of eventFiles) {
    const runName = path.relative(logdir, path.dirname(eventFile)) || 'default'

    // Parse event file
    const events = await parseEventFile(eventFile)

    // Filter by tag if specified
    const filteredEvents = tag
      ? events.scalars.filter(e => e.tag === tag)
      : events.scalars

    // Group by tag
    const tagGroups = new Map<string, Array<{ step: number; value: number; wall_time: number }>>()
    for (const event of filteredEvents) {
      if (!tagGroups.has(event.tag)) {
        tagGroups.set(event.tag, [])
      }
      tagGroups.get(event.tag)!.push({
        step: event.step,
        value: event.value,
        wall_time: event.wall_time
      })
    }

    // Downsample if needed
    for (const [tagName, data] of tagGroups.entries()) {
      const downsampledData = data.length > max_points
        ? downsample(data, max_points)
        : data

      scalars.push({
        run: runName,
        tag: tagName,
        data: downsampledData
      })
    }
  }

  return { scalars }
}

function downsample<T>(data: T[], maxPoints: number): T[] {
  if (data.length <= maxPoints) return data

  const step = data.length / maxPoints
  const result: T[] = []

  for (let i = 0; i < maxPoints; i++) {
    const index = Math.floor(i * step)
    result.push(data[index])
  }

  return result
}
```

---

#### `tensorboard_get_latest_metrics`

Get the latest metric values from an experiment (useful for monitoring convergence).

**Input Schema**:
```json
{
  "logdir": "string (required)",
  "run": "string (optional)",
  "tags": "string[] (optional, metric tags to retrieve)"
}
```

**Output Schema**:
```json
{
  "metrics": [
    {
      "run": "string",
      "tag": "string",
      "latest_value": "number",
      "latest_step": "number",
      "wall_time": "number"
    }
  ]
}
```

**Use Case**:
- Check if model has converged
- Monitor training progress
- Trigger early stopping

---

#### `tensorboard_get_histograms`

Retrieve histogram data (weights, gradients, activations).

**Input Schema**:
```json
{
  "logdir": "string (required)",
  "run": "string (optional)",
  "tag": "string (optional)",
  "steps": "number[] (optional, specific steps to retrieve)"
}
```

**Output Schema**:
```json
{
  "histograms": [
    {
      "run": "string",
      "tag": "string",
      "step": "number",
      "bins": "number[]",
      "counts": "number[]"
    }
  ]
}
```

---

#### `tensorboard_get_images`

Retrieve logged images (useful for generative models, attention visualizations).

**Input Schema**:
```json
{
  "logdir": "string (required)",
  "run": "string (optional)",
  "tag": "string (optional)",
  "step": "number (optional, get images at specific step)"
}
```

**Output Schema**:
```json
{
  "images": [
    {
      "run": "string",
      "tag": "string",
      "step": "number",
      "image_data": "string (base64-encoded image)",
      "width": "number",
      "height": "number"
    }
  ]
}
```

---

### 4. Model Graph Tools

#### `tensorboard_get_model_graph`

Retrieve model architecture as a graph.

**Input Schema**:
```json
{
  "logdir": "string (required)",
  "run": "string (optional)"
}
```

**Output Schema**:
```json
{
  "graph": {
    "nodes": [
      {
        "name": "string",
        "op": "string (operation type)",
        "input": "string[] (input node names)",
        "device": "string (CPU/GPU)"
      }
    ],
    "edges": [
      {
        "from": "string (source node)",
        "to": "string (target node)"
      }
    ]
  }
}
```

---

### 5. Data Export Tools

#### `tensorboard_export_scalars`

Export scalar metrics to CSV format.

**Input Schema**:
```json
{
  "logdir": "string (required)",
  "output_path": "string (required, CSV file path)",
  "run": "string (optional)",
  "tags": "string[] (optional)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "output_path": "string",
  "rows_exported": "number",
  "message": "string"
}
```

**CSV Format**:
```csv
run,tag,step,value,wall_time
train,loss,0,2.3456,1730198400
train,loss,100,1.8234,1730198410
train,accuracy,0,0.234,1730198400
train,accuracy,100,0.678,1730198410
```

---

#### `tensorboard_export_summary`

Export training summary (best metrics, final values, convergence info).

**Input Schema**:
```json
{
  "logdir": "string (required)",
  "run": "string (optional)"
}
```

**Output Schema**:
```json
{
  "summary": {
    "run": "string",
    "duration_seconds": "number",
    "total_steps": "number",
    "metrics": [
      {
        "tag": "string",
        "final_value": "number",
        "best_value": "number",
        "best_step": "number",
        "converged": "boolean"
      }
    ]
  }
}
```

---

## Configuration

### Environment Variables

```bash
# TensorBoard executable (optional, defaults to 'tensorboard')
TENSORBOARD_EXECUTABLE=tensorboard

# Default log directory (optional)
TENSORBOARD_LOGDIR=./logs

# Default port range (optional)
TENSORBOARD_PORT_START=6006
TENSORBOARD_PORT_END=6016

# Server timeout (optional)
TENSORBOARD_STARTUP_TIMEOUT_MS=30000
```

### Configuration File

`mcp-tensorboard-config.json`:
```json
{
  "tensorboard": {
    "executable": "tensorboard",
    "default_logdir": "./logs",
    "default_port": 6006,
    "startup_timeout_ms": 30000,
    "max_servers": 5
  },
  "parsing": {
    "cache_enabled": true,
    "cache_ttl_seconds": 60,
    "max_points_per_tag": 10000
  },
  "logging": {
    "level": "info",
    "log_server_output": true
  }
}
```

---

## Error Handling

### Error Categories

#### 1. Process Errors
- **Cause**: TensorBoard executable not found
- **Recovery**: None (fail immediately)
- **User Message**: "TensorBoard not found. Install with: pip install tensorboard"

#### 2. Port Conflicts
- **Cause**: Port already in use
- **Recovery**: Try next port in range (6006-6016)
- **User Message**: "Port {port} in use. Trying port {next_port}..."

#### 3. Invalid Log Directory
- **Cause**: Log directory doesn't exist or has no event files
- **Recovery**: None (fail immediately)
- **User Message**: "Log directory '{logdir}' not found or contains no event files"

#### 4. Parsing Errors
- **Cause**: Corrupted event files
- **Recovery**: Skip corrupted file, log warning
- **User Message**: "Warning: Failed to parse event file '{file}'. Skipping."

#### 5. Server Timeout
- **Cause**: TensorBoard server fails to start
- **Recovery**: Kill process, return error
- **User Message**: "TensorBoard server failed to start. Check logs: {stderr}"

### Error Response Schema

```json
{
  "error": {
    "code": "PROCESS_ERROR|PORT_CONFLICT|INVALID_LOGDIR|PARSING_ERROR|TIMEOUT",
    "message": "string",
    "details": "object (optional)",
    "suggestion": "string (optional, remediation steps)"
  }
}
```

---

## Performance Optimization

### Event File Caching
```typescript
// Cache parsed event files to avoid re-parsing
const eventCache = new Map<string, { data: EventData, mtime: number }>()

async function parseEventFile(filePath: string): Promise<EventData> {
  const stats = fs.statSync(filePath)
  const cached = eventCache.get(filePath)

  // Return cached data if file hasn't been modified
  if (cached && cached.mtime === stats.mtimeMs) {
    return cached.data
  }

  // Parse event file
  const data = await parseEventFileImpl(filePath)

  // Update cache
  eventCache.set(filePath, { data, mtime: stats.mtimeMs })

  return data
}
```

### Downsampling Strategy
- Large experiments (>10k steps): Downsample to 1000 points
- Use Largest-Triangle-Three-Buckets (LTTB) algorithm for intelligent downsampling
- Preserve peaks and valleys in metric curves

### Server Management
- Limit to 5 concurrent TensorBoard servers (configurable)
- Auto-cleanup inactive servers after 1 hour (optional)
- Graceful shutdown on MCP server exit

---

## Testing Strategy

### Unit Tests

**Test Coverage Targets**: 85%+ for all tool functions

**Key Test Cases**:
```typescript
describe('tensorboard_start_server', () => {
  it('starts TensorBoard server successfully', async () => {
    const result = await startTensorBoard({
      logdir: '/tmp/test-logs',
      port: 6007
    })
    expect(result.success).toBe(true)
    expect(result.url).toBe('http://localhost:6007')
  })

  it('rejects invalid log directory', async () => {
    await expect(startTensorBoard({ logdir: '/nonexistent', port: 6007 }))
      .rejects.toThrow(ValidationError)
  })

  it('handles port conflicts', async () => {
    // Start first server on port 6006
    await startTensorBoard({ logdir: '/tmp/test-logs', port: 6006 })

    // Try to start second server on same port
    await expect(startTensorBoard({ logdir: '/tmp/test-logs', port: 6006 }))
      .rejects.toThrow(/Port .* already in use/)
  })
})

describe('tensorboard_get_scalars', () => {
  it('retrieves scalar metrics', async () => {
    const result = await getScalars({
      logdir: '/tmp/test-logs',
      tag: 'loss'
    })
    expect(result.scalars.length).toBeGreaterThan(0)
  })

  it('downsamples large datasets', async () => {
    const result = await getScalars({
      logdir: '/tmp/large-logs',
      max_points: 100
    })
    result.scalars.forEach(scalar => {
      expect(scalar.data.length).toBeLessThanOrEqual(100)
    })
  })
})
```

### Integration Tests

**Test Environment**: PyTorch training script that logs to TensorBoard

```python
# test_training.py
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('logs/test-run')

for step in range(100):
    writer.add_scalar('loss', 1.0 / (step + 1), step)
    writer.add_scalar('accuracy', step / 100, step)

writer.close()
```

**Test Cases**:
1. Start TensorBoard → List experiments → Get scalars → Stop server
2. Parse event files with multiple runs
3. Export scalars to CSV and verify format
4. Get latest metrics and verify values

### Performance Benchmarks

**Target Metrics**:
- Server startup: <5 seconds
- Parse 1000 events: <100ms
- Get scalars (10k points): <500ms
- Export to CSV (100k points): <2 seconds

---

## Installation

### Prerequisites

```bash
# Install TensorBoard
pip install tensorboard

# Verify installation
tensorboard --version
```

### NPM Package

```bash
npm install -g @pm-agents/mcp-tensorboard
```

### Claude Code MCP Configuration

Add to `~/.claude/mcp_servers.json`:

```json
{
  "mcpServers": {
    "tensorboard": {
      "command": "npx",
      "args": ["-y", "@pm-agents/mcp-tensorboard"],
      "env": {
        "TENSORBOARD_LOGDIR": "./logs",
        "TENSORBOARD_PORT_START": "6006"
      }
    }
  }
}
```

### Verification

```bash
# Test MCP server
echo '{"method":"tools/list"}' | npx @pm-agents/mcp-tensorboard

# Expected output: List of all tensorboard_* tools
```

---

## Integration with PM-Agents

### Python ML/DL Agent Usage

```python
# Python ML/DL Agent using MCP tool
async def train_model(self, config: TrainingConfig) -> TrainingResponse:
    # 1. Start TensorBoard server
    tb_server = await self.mcp_call("tensorboard_start_server", {
        "logdir": config.logdir,
        "port": 6006,
        "name": f"{config.project_name}-training"
    })

    print(f"TensorBoard available at: {tb_server['url']}")

    # 2. Train model (TensorBoard logs written during training)
    training_result = self.train_pytorch_model(config)

    # 3. Monitor training progress (during or after training)
    latest_metrics = await self.mcp_call("tensorboard_get_latest_metrics", {
        "logdir": config.logdir,
        "tags": ["loss", "accuracy", "val_loss", "val_accuracy"]
    })

    # 4. Check convergence
    converged = self.check_convergence(latest_metrics["metrics"])

    # 5. Export training summary
    summary = await self.mcp_call("tensorboard_export_summary", {
        "logdir": config.logdir
    })

    # 6. Stop TensorBoard server (optional, or leave running for inspection)
    # await self.mcp_call("tensorboard_stop_server", {
    #     "server_id": tb_server["server_id"]
    # })

    return TrainingResponse(
        model_path=training_result.model_path,
        final_loss=latest_metrics["metrics"][0]["latest_value"],
        tensorboard_url=tb_server["url"],
        summary=summary
    )

def check_convergence(self, metrics: List[Dict]) -> bool:
    """Check if training has converged."""
    loss_metric = next((m for m in metrics if m["tag"] == "loss"), None)
    if not loss_metric:
        return False

    # Check if loss change is below threshold
    # (requires getting historical data)
    return False  # Placeholder
```

---

## Future Enhancements

### Post-MVP Features

1. **Real-time Streaming**: WebSocket API for real-time metric updates
2. **Comparison Tool**: Compare multiple runs side-by-side
3. **Hyperparameter Tuning**: Integration with Optuna/Ray Tune
4. **Model Checkpointing**: Link metrics to saved model checkpoints
5. **Profiler Integration**: TensorBoard Profiler for performance analysis
6. **Custom Plugins**: Support TensorBoard plugins (What-If Tool, Debugger)
7. **Multi-framework Support**: JAX, MXNet, Keras event files

---

## Security Considerations

### Process Isolation
- Run TensorBoard servers with user permissions (no sudo)
- Bind to localhost by default (not 0.0.0.0)
- Limit number of concurrent servers (DoS prevention)

### File Access
- Validate log directory paths (prevent path traversal)
- Read-only access to event files (no modifications)

### Network Security
- Support authentication for TensorBoard servers (optional)
- HTTPS support for cloud deployments

---

## Monitoring and Logging

### Metrics to Track
- Active server count
- Server uptime
- Event file parsing time
- Memory usage per server

### Logging Format
```json
{
  "timestamp": "2025-10-29T10:15:30Z",
  "level": "info",
  "tool": "tensorboard_start_server",
  "server_id": "abc-123",
  "logdir": "/path/to/logs",
  "port": 6006,
  "startup_time_ms": 3200
}
```

---

## Support and Maintenance

### Documentation
- API reference: https://pm-agents.dev/mcp/tensorboard
- Examples: https://github.com/pm-agents/examples/tensorboard
- Troubleshooting: https://pm-agents.dev/docs/troubleshooting/tensorboard

### Issue Reporting
- GitHub Issues: https://github.com/pm-agents/mcp-tensorboard/issues

### Versioning
- Semantic versioning (semver)
- Compatibility with TensorBoard 2.x

---

## Implementation Checklist

- [ ] Set up TypeScript project structure
- [ ] Implement TensorBoard process management
- [ ] Implement event file parser (TFRecord format)
- [ ] Implement all 14 MCP tools
- [ ] Add input validation for all tools
- [ ] Add error handling with process supervision
- [ ] Write unit tests (85%+ coverage)
- [ ] Write integration tests with PyTorch
- [ ] Create performance benchmarks
- [ ] Write README with installation instructions
- [ ] Publish to npm registry
- [ ] Add to Claude Code MCP documentation
- [ ] Create example PyTorch training scripts
- [ ] Set up CI/CD pipeline (GitHub Actions)

---

**Last Updated**: 2025-10-29
**Status**: Specification Complete - Ready for Implementation
