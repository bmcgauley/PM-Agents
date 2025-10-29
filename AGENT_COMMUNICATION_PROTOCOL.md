# Agent Communication Protocol Specification

## Overview

This document defines the **Agent-to-Agent (A2A) Communication Protocol** for the PM-Agents multi-agent system. It specifies message formats, routing mechanisms, delivery guarantees, error handling, and observability patterns for inter-agent communication.

### Purpose

- **Task Delegation**: Coordinator → Planner → Supervisor → Specialists
- **Result Propagation**: Specialists → Supervisor → Planner → Coordinator
- **Status Updates**: Agents report progress to parent agents
- **Error Escalation**: Agents escalate blockers up the hierarchy
- **Context Sharing**: Agents share relevant context with peers

---

## Communication Architecture

### Hierarchical Message Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Request                             │
└────────────────────────┬────────────────────────────────────┘
                         ↓
              ┌──────────────────────┐
              │  Coordinator Agent   │ (Tier 1)
              └──────────┬───────────┘
                         ↓ TaskRequest
              ┌──────────────────────┐
              │   Planner Agent      │ (Tier 2)
              └──────────┬───────────┘
                         ↓ ExecutionPlan
              ┌──────────────────────┐
              │  Supervisor Agent    │ (Tier 3)
              └──────────┬───────────┘
                         ↓ SubTask
         ┌───────────────┴───────────────┐
         ↓               ↓               ↓
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │Specialist│    │Specialist│    │Specialist│ (Tier 4)
   │ Agent 1  │    │ Agent 2  │    │ Agent 3  │
   └────┬────┘    └────┬────┘    └────┬────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓ TaskResult
              ┌──────────────────────┐
              │  Supervisor Agent    │
              └──────────┬───────────┘
                         ↓ AggregatedResult
              ┌──────────────────────┐
              │   Planner Agent      │
              └──────────┬───────────┘
                         ↓ FinalReport
              ┌──────────────────────┐
              │  Coordinator Agent   │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │     User Response    │
              └──────────────────────┘
```

### Communication Patterns

1. **Request-Response**: Synchronous task delegation (Coordinator → Planner)
2. **Publish-Subscribe**: Async status updates (Specialists → Supervisor)
3. **Fire-and-Forget**: Non-critical notifications
4. **Request-Reply with Timeout**: Task execution with deadline

---

## Message Schemas

### Base Message Schema

All messages inherit from this base schema:

```json
{
  "message_id": "string (UUID v4)",
  "correlation_id": "string (UUID v4, links related messages)",
  "message_type": "TaskRequest|TaskResult|StatusUpdate|ErrorReport|ContextShare",
  "timestamp": "string (ISO 8601)",
  "sender": {
    "agent_id": "string",
    "agent_type": "Coordinator|Planner|Supervisor|Specialist",
    "agent_name": "string"
  },
  "recipient": {
    "agent_id": "string",
    "agent_type": "string",
    "agent_name": "string"
  },
  "priority": "critical|high|normal|low",
  "ttl_seconds": "number (time-to-live)",
  "metadata": {
    "project_id": "string",
    "session_id": "string",
    "trace_id": "string (for distributed tracing)"
  }
}
```

### 1. TaskRequest Message

Sent when delegating a task to another agent.

```json
{
  ...BaseMessage,
  "message_type": "TaskRequest",
  "payload": {
    "task_id": "string (UUID v4)",
    "task_type": "code_generation|research|validation|documentation",
    "description": "string",
    "requirements": {
      "deliverables": "string[]",
      "constraints": "object",
      "deadline": "string (ISO 8601)"
    },
    "context": {
      "project_path": "string",
      "relevant_files": "string[]",
      "previous_results": "object[]",
      "user_preferences": "object"
    },
    "dependencies": {
      "depends_on": "string[] (task IDs)",
      "blocks": "string[] (task IDs)"
    },
    "config": {
      "max_retries": "number",
      "timeout_seconds": "number",
      "require_approval": "boolean"
    }
  }
}
```

**Example**:
```json
{
  "message_id": "msg-abc123",
  "correlation_id": "corr-xyz789",
  "message_type": "TaskRequest",
  "timestamp": "2025-10-29T10:30:00Z",
  "sender": {
    "agent_id": "coordinator-001",
    "agent_type": "Coordinator",
    "agent_name": "MainCoordinator"
  },
  "recipient": {
    "agent_id": "planner-001",
    "agent_type": "Planner",
    "agent_name": "StrategicPlanner"
  },
  "priority": "high",
  "ttl_seconds": 3600,
  "metadata": {
    "project_id": "proj-456",
    "session_id": "sess-789",
    "trace_id": "trace-012"
  },
  "payload": {
    "task_id": "task-001",
    "task_type": "code_generation",
    "description": "Create a React component for user authentication",
    "requirements": {
      "deliverables": ["LoginForm.tsx", "LoginForm.test.tsx", "types.ts"],
      "constraints": {
        "framework": "React 18",
        "typescript": true,
        "test_coverage": 0.8
      },
      "deadline": "2025-10-29T12:00:00Z"
    },
    "context": {
      "project_path": "/projects/my-app",
      "relevant_files": ["src/components/AuthContext.tsx"],
      "previous_results": [],
      "user_preferences": {
        "style_guide": "airbnb",
        "use_hooks": true
      }
    },
    "dependencies": {
      "depends_on": [],
      "blocks": []
    },
    "config": {
      "max_retries": 3,
      "timeout_seconds": 600,
      "require_approval": false
    }
  }
}
```

---

### 2. TaskResult Message

Sent when an agent completes a task.

```json
{
  ...BaseMessage,
  "message_type": "TaskResult",
  "payload": {
    "task_id": "string",
    "status": "success|partial_success|failure",
    "result": {
      "deliverables": [
        {
          "type": "file|code|documentation|report",
          "path": "string",
          "content": "string (or reference)",
          "metadata": "object"
        }
      ],
      "summary": "string",
      "metrics": {
        "execution_time_ms": "number",
        "tokens_used": "number",
        "cost_usd": "number"
      }
    },
    "issues": [
      {
        "severity": "error|warning|info",
        "message": "string",
        "suggestion": "string"
      }
    ],
    "next_steps": "string[]"
  }
}
```

**Example**:
```json
{
  "message_id": "msg-def456",
  "correlation_id": "corr-xyz789",
  "message_type": "TaskResult",
  "timestamp": "2025-10-29T10:45:00Z",
  "sender": {
    "agent_id": "frontend-001",
    "agent_type": "Specialist",
    "agent_name": "FrontendCoder"
  },
  "recipient": {
    "agent_id": "supervisor-001",
    "agent_type": "Supervisor",
    "agent_name": "TaskSupervisor"
  },
  "priority": "high",
  "ttl_seconds": 3600,
  "metadata": {
    "project_id": "proj-456",
    "session_id": "sess-789",
    "trace_id": "trace-012"
  },
  "payload": {
    "task_id": "task-001",
    "status": "success",
    "result": {
      "deliverables": [
        {
          "type": "file",
          "path": "src/components/LoginForm.tsx",
          "content": "import React from 'react'...",
          "metadata": {
            "lines_of_code": 120,
            "complexity": "low"
          }
        },
        {
          "type": "file",
          "path": "src/components/LoginForm.test.tsx",
          "content": "import { render } from '@testing-library/react'...",
          "metadata": {
            "test_count": 8,
            "coverage": 0.85
          }
        }
      ],
      "summary": "Created LoginForm component with email/password authentication",
      "metrics": {
        "execution_time_ms": 45000,
        "tokens_used": 12000,
        "cost_usd": 0.24
      }
    },
    "issues": [],
    "next_steps": [
      "Integrate with authentication context",
      "Add error boundary",
      "Test in production build"
    ]
  }
}
```

---

### 3. StatusUpdate Message

Sent periodically to report progress on long-running tasks.

```json
{
  ...BaseMessage,
  "message_type": "StatusUpdate",
  "payload": {
    "task_id": "string",
    "status": "queued|in_progress|paused|completed|failed",
    "progress": {
      "percent_complete": "number (0-100)",
      "current_step": "string",
      "total_steps": "number",
      "elapsed_time_ms": "number",
      "estimated_remaining_ms": "number"
    },
    "message": "string",
    "checkpoints": [
      {
        "timestamp": "string (ISO 8601)",
        "description": "string"
      }
    ]
  }
}
```

**Example**:
```json
{
  "message_id": "msg-ghi789",
  "correlation_id": "corr-xyz789",
  "message_type": "StatusUpdate",
  "timestamp": "2025-10-29T10:35:00Z",
  "sender": {
    "agent_id": "frontend-001",
    "agent_type": "Specialist",
    "agent_name": "FrontendCoder"
  },
  "recipient": {
    "agent_id": "supervisor-001",
    "agent_type": "Supervisor",
    "agent_name": "TaskSupervisor"
  },
  "priority": "normal",
  "ttl_seconds": 300,
  "metadata": {
    "project_id": "proj-456",
    "session_id": "sess-789",
    "trace_id": "trace-012"
  },
  "payload": {
    "task_id": "task-001",
    "status": "in_progress",
    "progress": {
      "percent_complete": 60,
      "current_step": "Generating component tests",
      "total_steps": 5,
      "elapsed_time_ms": 27000,
      "estimated_remaining_ms": 18000
    },
    "message": "Component generated successfully. Now writing tests.",
    "checkpoints": [
      {
        "timestamp": "2025-10-29T10:31:00Z",
        "description": "Retrieved context from vector database"
      },
      {
        "timestamp": "2025-10-29T10:33:00Z",
        "description": "Generated component code"
      }
    ]
  }
}
```

---

### 4. ErrorReport Message

Sent when an agent encounters an error or blocker.

```json
{
  ...BaseMessage,
  "message_type": "ErrorReport",
  "payload": {
    "task_id": "string",
    "error": {
      "code": "string",
      "type": "validation_error|dependency_missing|timeout|resource_unavailable|internal_error",
      "message": "string",
      "stack_trace": "string (optional)",
      "context": "object"
    },
    "severity": "critical|high|medium|low",
    "recoverable": "boolean",
    "attempted_recovery": [
      {
        "action": "string",
        "result": "success|failure"
      }
    ],
    "escalation_required": "boolean",
    "user_action_required": "boolean"
  }
}
```

**Example**:
```json
{
  "message_id": "msg-jkl012",
  "correlation_id": "corr-xyz789",
  "message_type": "ErrorReport",
  "timestamp": "2025-10-29T10:40:00Z",
  "sender": {
    "agent_id": "frontend-001",
    "agent_type": "Specialist",
    "agent_name": "FrontendCoder"
  },
  "recipient": {
    "agent_id": "supervisor-001",
    "agent_type": "Supervisor",
    "agent_name": "TaskSupervisor"
  },
  "priority": "critical",
  "ttl_seconds": 300,
  "metadata": {
    "project_id": "proj-456",
    "session_id": "sess-789",
    "trace_id": "trace-012"
  },
  "payload": {
    "task_id": "task-001",
    "error": {
      "code": "DEPENDENCY_MISSING",
      "type": "dependency_missing",
      "message": "Cannot find module '@types/react' in project dependencies",
      "stack_trace": null,
      "context": {
        "missing_dependency": "@types/react",
        "required_by": "LoginForm.tsx"
      }
    },
    "severity": "high",
    "recoverable": true,
    "attempted_recovery": [
      {
        "action": "Searched in node_modules",
        "result": "failure"
      }
    ],
    "escalation_required": true,
    "user_action_required": true
  }
}
```

---

### 5. ContextShare Message

Sent when an agent wants to share context with peers or parent agents.

```json
{
  ...BaseMessage,
  "message_type": "ContextShare",
  "payload": {
    "context_type": "code_snippet|documentation|research_findings|decision|pattern",
    "content": "string or object",
    "relevance": {
      "related_tasks": "string[]",
      "keywords": "string[]",
      "priority": "high|normal|low"
    },
    "expiration": "string (ISO 8601, when context becomes stale)"
  }
}
```

---

## Message Routing

### Routing Table

Each agent maintains a routing table mapping agent types to agent instances:

```typescript
interface RoutingTable {
  [agentType: string]: AgentEndpoint[]
}

interface AgentEndpoint {
  agent_id: string
  agent_name: string
  agent_type: string
  address: string  // URL or message queue topic
  status: 'active' | 'inactive' | 'degraded'
  load: number  // 0-100, current load percentage
  capabilities: string[]
}

// Example routing table
const routingTable: RoutingTable = {
  'Coordinator': [
    {
      agent_id: 'coordinator-001',
      agent_name: 'MainCoordinator',
      agent_type: 'Coordinator',
      address: 'queue://coordinator',
      status: 'active',
      load: 45,
      capabilities: ['orchestration', 'delegation']
    }
  ],
  'Planner': [
    {
      agent_id: 'planner-001',
      agent_name: 'StrategicPlanner',
      agent_type: 'Planner',
      address: 'queue://planner',
      status: 'active',
      load: 30,
      capabilities: ['task_decomposition', 'risk_assessment']
    }
  ],
  'Specialist': [
    {
      agent_id: 'frontend-001',
      agent_name: 'FrontendCoder',
      agent_type: 'Specialist',
      address: 'queue://frontend',
      status: 'active',
      load: 60,
      capabilities: ['react', 'typescript', 'nextjs']
    },
    {
      agent_id: 'backend-001',
      agent_name: 'BackendCoder',
      agent_type: 'Specialist',
      address: 'queue://backend',
      status: 'active',
      load: 20,
      capabilities: ['python', 'fastapi', 'sqlalchemy']
    }
  ]
}
```

### Routing Algorithm

```typescript
function routeMessage(message: Message, routingTable: RoutingTable): AgentEndpoint {
  const recipientType = message.recipient.agent_type
  const candidates = routingTable[recipientType] || []

  // Filter by status
  const activeCandidates = candidates.filter(agent => agent.status === 'active')

  if (activeCandidates.length === 0) {
    throw new Error(`No active agents of type '${recipientType}'`)
  }

  // If specific agent requested, route to it
  if (message.recipient.agent_id) {
    const specificAgent = activeCandidates.find(
      agent => agent.agent_id === message.recipient.agent_id
    )
    if (specificAgent) {
      return specificAgent
    }
  }

  // Load balancing: choose agent with lowest load
  const leastLoadedAgent = activeCandidates.reduce((min, agent) =>
    agent.load < min.load ? agent : min
  )

  return leastLoadedAgent
}
```

---

## Message Passing Infrastructure

### In-Process Communication (Python)

For agents running in the same Python process:

```python
# message_bus.py
import asyncio
from typing import Dict, List, Callable
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    TASK_REQUEST = "TaskRequest"
    TASK_RESULT = "TaskResult"
    STATUS_UPDATE = "StatusUpdate"
    ERROR_REPORT = "ErrorReport"
    CONTEXT_SHARE = "ContextShare"

@dataclass
class Message:
    message_id: str
    correlation_id: str
    message_type: MessageType
    timestamp: str
    sender: dict
    recipient: dict
    priority: str
    ttl_seconds: int
    metadata: dict
    payload: dict

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False

    async def start(self):
        """Start processing messages."""
        self.running = True
        while self.running:
            message = await self.message_queue.get()
            await self._dispatch_message(message)

    async def stop(self):
        """Stop processing messages."""
        self.running = False

    def subscribe(self, agent_id: str, callback: Callable):
        """Subscribe an agent to receive messages."""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)

    async def publish(self, message: Message):
        """Publish a message to the bus."""
        await self.message_queue.put(message)

    async def _dispatch_message(self, message: Message):
        """Dispatch message to recipient."""
        recipient_id = message.recipient['agent_id']

        if recipient_id in self.subscribers:
            callbacks = self.subscribers[recipient_id]
            for callback in callbacks:
                try:
                    await callback(message)
                except Exception as e:
                    print(f"Error dispatching message: {e}")

# Global message bus instance
message_bus = MessageBus()
```

### Agent Implementation with Message Bus

```python
# base_agent.py
import uuid
from datetime import datetime
from typing import Optional

class BaseAgent:
    def __init__(self, agent_id: str, agent_type: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.agent_name = agent_name

        # Subscribe to message bus
        message_bus.subscribe(self.agent_id, self.handle_message)

    async def handle_message(self, message: Message):
        """Handle incoming messages."""
        if message.message_type == MessageType.TASK_REQUEST:
            await self.handle_task_request(message)
        elif message.message_type == MessageType.TASK_RESULT:
            await self.handle_task_result(message)
        elif message.message_type == MessageType.STATUS_UPDATE:
            await self.handle_status_update(message)
        elif message.message_type == MessageType.ERROR_REPORT:
            await self.handle_error_report(message)
        elif message.message_type == MessageType.CONTEXT_SHARE:
            await self.handle_context_share(message)

    async def send_message(
        self,
        recipient_id: str,
        recipient_type: str,
        message_type: MessageType,
        payload: dict,
        priority: str = "normal",
        correlation_id: Optional[str] = None
    ):
        """Send a message to another agent."""
        message = Message(
            message_id=str(uuid.uuid4()),
            correlation_id=correlation_id or str(uuid.uuid4()),
            message_type=message_type,
            timestamp=datetime.utcnow().isoformat(),
            sender={
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'agent_name': self.agent_name
            },
            recipient={
                'agent_id': recipient_id,
                'agent_type': recipient_type,
                'agent_name': ''  # Will be resolved by routing
            },
            priority=priority,
            ttl_seconds=3600,
            metadata={
                'project_id': getattr(self, 'project_id', ''),
                'session_id': getattr(self, 'session_id', ''),
                'trace_id': str(uuid.uuid4())
            },
            payload=payload
        )

        await message_bus.publish(message)

    async def handle_task_request(self, message: Message):
        """Override in subclass."""
        raise NotImplementedError

    async def handle_task_result(self, message: Message):
        """Override in subclass."""
        raise NotImplementedError

    async def handle_status_update(self, message: Message):
        """Override in subclass."""
        pass

    async def handle_error_report(self, message: Message):
        """Override in subclass."""
        pass

    async def handle_context_share(self, message: Message):
        """Override in subclass."""
        pass
```

### Example: Coordinator Delegating to Planner

```python
# coordinator_agent.py
class CoordinatorAgent(BaseAgent):
    async def coordinate_task(self, user_request: dict):
        """Coordinate a user request."""
        # Send TaskRequest to Planner
        await self.send_message(
            recipient_id='planner-001',
            recipient_type='Planner',
            message_type=MessageType.TASK_REQUEST,
            payload={
                'task_id': str(uuid.uuid4()),
                'task_type': 'code_generation',
                'description': user_request['description'],
                'requirements': user_request['requirements'],
                'context': {},
                'dependencies': {'depends_on': [], 'blocks': []},
                'config': {
                    'max_retries': 3,
                    'timeout_seconds': 600,
                    'require_approval': False
                }
            },
            priority='high'
        )

    async def handle_task_result(self, message: Message):
        """Handle result from Planner."""
        print(f"Received result from Planner: {message.payload['status']}")

        # Process result and send response to user
        if message.payload['status'] == 'success':
            await self.send_response_to_user(message.payload['result'])
        else:
            await self.handle_failure(message.payload)
```

---

## Message Queue Implementation

### Redis-Based Message Queue

For distributed agents across multiple processes/servers:

```python
# redis_message_queue.py
import json
import redis
from typing import Callable

class RedisMessageQueue:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.pubsub = self.redis_client.pubsub()

    def subscribe(self, agent_id: str, callback: Callable):
        """Subscribe to messages for an agent."""
        channel = f"agent:{agent_id}"
        self.pubsub.subscribe(channel)

        # Listen for messages in separate thread
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                callback(data)

    def publish(self, recipient_id: str, message: dict):
        """Publish message to recipient's channel."""
        channel = f"agent:{recipient_id}"
        self.redis_client.publish(channel, json.dumps(message))

    def enqueue(self, queue_name: str, message: dict):
        """Add message to a queue (for work distribution)."""
        self.redis_client.lpush(queue_name, json.dumps(message))

    def dequeue(self, queue_name: str, timeout: int = 0):
        """Remove and return message from queue."""
        result = self.redis_client.brpop(queue_name, timeout=timeout)
        if result:
            _, message_data = result
            return json.loads(message_data)
        return None
```

---

## Timeout and Retry Mechanisms

### Timeout Handling

```python
# timeout.py
import asyncio
from typing import Coroutine, TypeVar

T = TypeVar('T')

async def with_timeout(
    coro: Coroutine[None, None, T],
    timeout_seconds: int,
    error_message: str = "Operation timed out"
) -> T:
    """Execute coroutine with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(error_message)

# Usage in agent
class CoordinatorAgent(BaseAgent):
    async def coordinate_task_with_timeout(self, user_request: dict):
        """Coordinate task with timeout."""
        try:
            result = await with_timeout(
                self.coordinate_task(user_request),
                timeout_seconds=600,
                error_message="Task coordination timed out after 10 minutes"
            )
            return result
        except TimeoutError as e:
            # Handle timeout
            await self.send_error_report(str(e))
```

### Retry Strategy

```python
# retry.py
import asyncio
from typing import Callable, TypeVar

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    max_delay: float = 60.0
) -> T:
    """Retry function with exponential backoff."""
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                break

            await asyncio.sleep(delay)
            delay = min(delay * backoff_multiplier, max_delay)

    raise last_exception

# Usage in agent
class FrontendCoderAgent(BaseAgent):
    async def execute_task_with_retry(self, task: dict):
        """Execute task with retry logic."""
        return await retry_with_backoff(
            lambda: self.execute_task(task),
            max_retries=3,
            initial_delay=1.0
        )
```

---

## Communication Logging

### Structured Message Logging

```python
# logger.py
import logging
import json
from datetime import datetime

class MessageLogger:
    def __init__(self, log_file: str = "agent_communication.log"):
        self.logger = logging.getLogger("agent_communication")
        self.logger.setLevel(logging.INFO)

        # File handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)

    def log_message_sent(self, message: Message):
        """Log outgoing message."""
        self.logger.info(json.dumps({
            'event': 'message_sent',
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': message.message_id,
            'correlation_id': message.correlation_id,
            'message_type': message.message_type.value,
            'sender': message.sender['agent_id'],
            'recipient': message.recipient['agent_id'],
            'priority': message.priority
        }))

    def log_message_received(self, message: Message):
        """Log incoming message."""
        self.logger.info(json.dumps({
            'event': 'message_received',
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': message.message_id,
            'correlation_id': message.correlation_id,
            'message_type': message.message_type.value,
            'sender': message.sender['agent_id'],
            'recipient': message.recipient['agent_id']
        }))

    def log_message_error(self, message: Message, error: Exception):
        """Log message handling error."""
        self.logger.error(json.dumps({
            'event': 'message_error',
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': message.message_id,
            'error': str(error),
            'stack_trace': traceback.format_exc()
        }))

# Global logger instance
message_logger = MessageLogger()
```

---

## Delivery Guarantees

### At-Least-Once Delivery

```python
# delivery.py
class MessageDeliveryTracker:
    def __init__(self):
        self.pending_messages = {}  # message_id -> (message, retry_count)
        self.acknowledged_messages = set()

    async def send_with_ack(self, message: Message):
        """Send message and wait for acknowledgment."""
        self.pending_messages[message.message_id] = (message, 0)

        await message_bus.publish(message)

        # Wait for acknowledgment (with timeout)
        try:
            await asyncio.wait_for(
                self.wait_for_ack(message.message_id),
                timeout=30.0
            )
            del self.pending_messages[message.message_id]
        except asyncio.TimeoutError:
            # Retry
            await self.retry_message(message.message_id)

    async def wait_for_ack(self, message_id: str):
        """Wait for message acknowledgment."""
        while message_id not in self.acknowledged_messages:
            await asyncio.sleep(0.1)

    async def acknowledge(self, message_id: str):
        """Acknowledge message receipt."""
        self.acknowledged_messages.add(message_id)

    async def retry_message(self, message_id: str):
        """Retry sending message."""
        if message_id in self.pending_messages:
            message, retry_count = self.pending_messages[message_id]

            if retry_count < 3:
                self.pending_messages[message_id] = (message, retry_count + 1)
                await message_bus.publish(message)
            else:
                # Max retries exceeded, escalate
                await self.escalate_failed_delivery(message)
```

---

## Testing Communication

### Unit Test Example

```python
# test_communication.py
import pytest
from message_bus import MessageBus, Message, MessageType

@pytest.mark.asyncio
async def test_message_delivery():
    bus = MessageBus()
    received_messages = []

    # Create test agent
    async def agent_callback(message: Message):
        received_messages.append(message)

    bus.subscribe('agent-001', agent_callback)

    # Send test message
    test_message = Message(
        message_id='test-123',
        correlation_id='corr-456',
        message_type=MessageType.TASK_REQUEST,
        timestamp='2025-10-29T10:00:00Z',
        sender={'agent_id': 'sender-001', 'agent_type': 'Coordinator', 'agent_name': 'Sender'},
        recipient={'agent_id': 'agent-001', 'agent_type': 'Planner', 'agent_name': 'Recipient'},
        priority='high',
        ttl_seconds=300,
        metadata={},
        payload={'task_id': 'task-001'}
    )

    await bus.publish(test_message)

    # Start bus processing
    bus_task = asyncio.create_task(bus.start())

    # Wait for message delivery
    await asyncio.sleep(0.1)

    # Stop bus
    await bus.stop()

    # Verify message received
    assert len(received_messages) == 1
    assert received_messages[0].message_id == 'test-123'
```

---

## Best Practices

### DO
- ✅ Use correlation IDs to link related messages
- ✅ Set appropriate TTLs for messages
- ✅ Log all message send/receive events
- ✅ Implement retry logic with exponential backoff
- ✅ Use timeouts for all async operations
- ✅ Acknowledge message receipt
- ✅ Include trace IDs for distributed tracing
- ✅ Validate message schemas before processing
- ✅ Handle errors gracefully with ErrorReport messages
- ✅ Use priority queues for critical messages

### DON'T
- ❌ Send large payloads in messages (use references instead)
- ❌ Ignore message timeouts
- ❌ Skip error handling
- ❌ Create circular message dependencies
- ❌ Hardcode agent IDs
- ❌ Forget to clean up completed message correlations
- ❌ Skip message validation
- ❌ Use synchronous blocking calls

---

## Performance Considerations

### Message Batching

For high-throughput scenarios, batch multiple messages:

```python
class MessageBatcher:
    def __init__(self, batch_size: int = 10, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []

    async def add_message(self, message: Message):
        self.buffer.append(message)

        if len(self.buffer) >= self.batch_size:
            await self.flush()

    async def flush(self):
        if self.buffer:
            await message_bus.publish_batch(self.buffer)
            self.buffer.clear()
```

### Metrics

Track communication performance:

```python
class CommunicationMetrics:
    def __init__(self):
        self.message_count = 0
        self.total_latency_ms = 0.0
        self.error_count = 0

    def record_message_sent(self, latency_ms: float):
        self.message_count += 1
        self.total_latency_ms += latency_ms

    def record_error(self):
        self.error_count += 1

    def get_average_latency(self) -> float:
        return self.total_latency_ms / self.message_count if self.message_count > 0 else 0.0

    def get_error_rate(self) -> float:
        return self.error_count / self.message_count if self.message_count > 0 else 0.0
```

---

**Last Updated**: 2025-10-29
**Status**: Complete - Ready for Implementation
