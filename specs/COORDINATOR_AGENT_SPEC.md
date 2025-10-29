# Coordinator Agent Specification

**Agent Type**: Orchestration Layer (Tier 1)
**Version**: 1.0
**Status**: Planning Phase
**Date**: 2025-10-28

---

## Overview

The Coordinator Agent is the top-level orchestrator in the PM-Agents hierarchical system. It receives user requests, makes high-level strategic decisions, delegates to the Planner Agent, monitors overall progress, and makes GO/NO-GO decisions at critical milestones.

---

## Role and Responsibilities

### Primary Responsibilities

1. **Receive and interpret user requests**
   - Parse natural language requests
   - Identify project type and requirements
   - Determine project scope and complexity

2. **Strategic decision-making**
   - Decide whether to proceed with request
   - Determine overall approach (new project, enhancement, research, etc.)
   - Allocate budget and resources (token limits, API calls)

3. **Delegate to Planner Agent**
   - Formulate high-level objectives
   - Pass context and constraints
   - Await strategic plan

4. **Monitor project progress**
   - Track overall project state
   - Monitor resource consumption (tokens, API calls, time)
   - Identify blockers and critical issues

5. **Make GO/NO-GO decisions**
   - Phase gate reviews at key milestones
   - Escalation handling from lower-tier agents
   - Project continuation or termination decisions

6. **Report to user**
   - Provide high-level progress updates
   - Deliver final results
   - Explain decisions and rationale

### Responsibilities Outside Scope

- ❌ Detailed task planning (Planner Agent)
- ❌ Specialist agent management (Supervisor Agent)
- ❌ Code generation or technical implementation (Specialist Agents)
- ❌ Direct file operations (uses MCP servers via delegation)

---

## Input/Output Schemas

### Input: User Request

```json
{
  "request_id": "string (UUID)",
  "timestamp": "ISO8601 datetime",
  "user_request": "string (natural language)",
  "context": {
    "project_path": "string (optional)",
    "project_type": "string (optional: frontend|ml|analytics|fullstack)",
    "preferences": {
      "model": "string (claude|ollama)",
      "max_budget_tokens": "integer",
      "max_time_seconds": "integer"
    }
  },
  "attachments": [
    {
      "type": "string (file|url|image)",
      "content": "string|base64",
      "description": "string"
    }
  ]
}
```

**Example**:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-28T10:30:00Z",
  "user_request": "Create a Next.js application with Supabase authentication and a product catalog",
  "context": {
    "project_path": "/home/user/projects/my-ecommerce",
    "project_type": "frontend",
    "preferences": {
      "model": "claude",
      "max_budget_tokens": 50000,
      "max_time_seconds": 300
    }
  },
  "attachments": []
}
```

### Output: Coordinator Response

```json
{
  "response_id": "string (UUID)",
  "request_id": "string (references input)",
  "timestamp": "ISO8601 datetime",
  "status": "string (completed|in_progress|failed|blocked)",
  "decision": "string (approved|rejected|needs_clarification)",
  "message": "string (user-friendly explanation)",
  "deliverables": [
    {
      "type": "string (code|documentation|report|plan)",
      "path": "string (file path)",
      "description": "string",
      "metadata": {}
    }
  ],
  "project_state": {
    "phase": "string (initiation|planning|execution|monitoring|closure)",
    "progress_percentage": "integer (0-100)",
    "tasks_completed": "integer",
    "tasks_remaining": "integer"
  },
  "resource_usage": {
    "tokens_used": "integer",
    "api_calls": "integer",
    "time_elapsed_seconds": "integer",
    "cost_usd": "float"
  },
  "next_steps": ["string"],
  "blockers": [
    {
      "severity": "string (critical|high|medium|low)",
      "description": "string",
      "resolution_required": "boolean"
    }
  ]
}
```

**Example**:
```json
{
  "response_id": "660f9511-f30c-42e5-b827-557766551111",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-28T10:35:00Z",
  "status": "completed",
  "decision": "approved",
  "message": "Successfully created Next.js application with Supabase authentication. Project is ready for development.",
  "deliverables": [
    {
      "type": "code",
      "path": "/home/user/projects/my-ecommerce",
      "description": "Next.js 14 application with App Router, Supabase auth, and product catalog structure",
      "metadata": {
        "lines_of_code": 1250,
        "files_created": 23,
        "test_coverage": 0
      }
    },
    {
      "type": "documentation",
      "path": "/home/user/projects/my-ecommerce/README.md",
      "description": "Project documentation with setup instructions",
      "metadata": {}
    }
  ],
  "project_state": {
    "phase": "closure",
    "progress_percentage": 100,
    "tasks_completed": 8,
    "tasks_remaining": 0
  },
  "resource_usage": {
    "tokens_used": 42350,
    "api_calls": 12,
    "time_elapsed_seconds": 178,
    "cost_usd": 0.85
  },
  "next_steps": [
    "Run 'npm install' to install dependencies",
    "Configure Supabase environment variables in .env.local",
    "Run 'npm run dev' to start development server"
  ],
  "blockers": []
}
```

---

## Communication Patterns

### Downward Communication (Coordinator → Planner)

**Message Type**: PlanningRequest

```json
{
  "message_id": "string (UUID)",
  "from": "coordinator",
  "to": "planner",
  "type": "planning_request",
  "timestamp": "ISO8601 datetime",
  "payload": {
    "request_id": "string",
    "objective": "string (high-level goal)",
    "requirements": [
      {
        "requirement": "string",
        "priority": "string (must_have|should_have|nice_to_have)",
        "acceptance_criteria": ["string"]
      }
    ],
    "constraints": {
      "max_tokens": "integer",
      "max_time_seconds": "integer",
      "technologies": ["string"],
      "project_type": "string"
    },
    "context": {}
  }
}
```

### Upward Communication (Planner → Coordinator)

**Message Type**: PlanningResponse

```json
{
  "message_id": "string (UUID)",
  "from": "planner",
  "to": "coordinator",
  "type": "planning_response",
  "timestamp": "ISO8601 datetime",
  "in_reply_to": "string (request message_id)",
  "payload": {
    "status": "string (success|partial|failed)",
    "plan": {
      "phases": [
        {
          "phase": "string",
          "tasks": [
            {
              "task_id": "string",
              "description": "string",
              "assigned_to": "string (agent type)",
              "dependencies": ["string (task_ids)"],
              "estimated_tokens": "integer",
              "estimated_time_seconds": "integer"
            }
          ]
        }
      ],
      "total_estimated_tokens": "integer",
      "total_estimated_time_seconds": "integer"
    },
    "risks": [
      {
        "risk": "string",
        "severity": "string",
        "mitigation": "string"
      }
    ],
    "recommendations": ["string"]
  }
}
```

### Status Updates (Supervisor → Coordinator)

**Message Type**: ProgressUpdate

```json
{
  "message_id": "string (UUID)",
  "from": "supervisor",
  "to": "coordinator",
  "type": "progress_update",
  "timestamp": "ISO8601 datetime",
  "payload": {
    "request_id": "string",
    "progress_percentage": "integer (0-100)",
    "current_phase": "string",
    "current_task": "string",
    "tasks_completed": "integer",
    "tasks_remaining": "integer",
    "blockers": [
      {
        "severity": "string",
        "description": "string",
        "requires_coordinator_decision": "boolean"
      }
    ]
  }
}
```

---

## Decision Logic

### 1. Request Acceptance Decision

**Decision Point**: Should this request be accepted and processed?

**Criteria**:
- ✅ Accept if:
  - Request is clear and actionable
  - Required resources (tokens, time) are within budget
  - Project type is supported (frontend, ML, analytics, etc.)
  - No safety/security concerns

- ❌ Reject if:
  - Request is unclear or ambiguous (ask for clarification)
  - Exceeds resource budgets
  - Violates safety policies (malware, destructive code, etc.)
  - Project type not supported

- ❓ Request clarification if:
  - Ambiguous requirements
  - Multiple valid interpretations
  - Missing critical information

**Algorithm**:
```python
def accept_request(user_request, context, preferences):
    # 1. Parse and analyze request
    intent = parse_intent(user_request)
    project_type = detect_project_type(user_request, context)

    # 2. Safety check
    if not is_safe(user_request):
        return Decision.REJECT, "Request violates safety policies"

    # 3. Clarity check
    if is_ambiguous(user_request):
        clarifications = generate_clarification_questions(user_request)
        return Decision.CLARIFY, clarifications

    # 4. Feasibility check
    estimated_resources = estimate_resources(user_request, project_type)
    if estimated_resources.tokens > preferences.max_budget_tokens:
        return Decision.REJECT, "Exceeds token budget"

    # 5. Support check
    if project_type not in SUPPORTED_TYPES:
        return Decision.REJECT, f"Project type {project_type} not supported"

    return Decision.ACCEPT, "Request approved for processing"
```

### 2. Phase Gate Decision

**Decision Point**: Should the project proceed to the next phase?

**Criteria**:
- ✅ GO if:
  - All phase deliverables are complete
  - Quality standards met (no critical issues)
  - Risks are acceptable
  - Resources available for next phase
  - No critical blockers

- ❌ NO-GO if:
  - Critical deliverables missing
  - Quality below threshold
  - Unacceptable risks identified
  - Critical blocker requires resolution
  - Resource budget exhausted

**Algorithm**:
```python
def phase_gate_decision(phase, phase_outputs, project_state):
    # 1. Check deliverables
    required_deliverables = get_required_deliverables(phase)
    completed = check_deliverables_complete(phase_outputs, required_deliverables)
    if not completed:
        return Decision.NO_GO, "Missing required deliverables"

    # 2. Check quality
    quality_score = assess_quality(phase_outputs)
    if quality_score < QUALITY_THRESHOLD:
        return Decision.NO_GO, f"Quality below threshold: {quality_score}"

    # 3. Check risks
    risks = project_state.get('risks', [])
    critical_risks = [r for r in risks if r['severity'] == 'critical']
    if critical_risks:
        return Decision.NO_GO, f"Critical risks not mitigated: {critical_risks}"

    # 4. Check blockers
    blockers = project_state.get('blockers', [])
    critical_blockers = [b for b in blockers if b['severity'] == 'critical']
    if critical_blockers:
        return Decision.NO_GO, f"Critical blockers: {critical_blockers}"

    # 5. Check resources
    if project_state['tokens_remaining'] < MIN_TOKENS_FOR_NEXT_PHASE:
        return Decision.NO_GO, "Insufficient tokens remaining"

    return Decision.GO, "All criteria met, proceed to next phase"
```

### 3. Escalation Handling

**Decision Point**: How to handle escalations from lower-tier agents?

**Escalation Types**:
- **Technical blocker**: Specialist agent cannot complete task
- **Resource exhaustion**: Token/time budget exceeded
- **Clarification needed**: Agent needs user input
- **Quality failure**: Deliverable doesn't meet standards
- **Safety concern**: Potential security or safety issue

**Response Algorithm**:
```python
def handle_escalation(escalation):
    escalation_type = escalation['type']
    severity = escalation['severity']

    if escalation_type == 'technical_blocker':
        if severity == 'critical':
            # Pause project, ask user for guidance
            return pause_and_ask_user(escalation)
        else:
            # Try alternative approach
            return delegate_alternative_approach(escalation)

    elif escalation_type == 'resource_exhaustion':
        # Request budget increase or terminate
        return request_budget_increase_or_terminate(escalation)

    elif escalation_type == 'clarification_needed':
        # Pass question to user
        return ask_user_for_clarification(escalation)

    elif escalation_type == 'quality_failure':
        # Retry with different approach or specialist
        return retry_with_alternative(escalation)

    elif escalation_type == 'safety_concern':
        # Immediately terminate and report
        return terminate_and_report_safety_issue(escalation)

    else:
        # Unknown escalation type
        return ask_user_for_decision(escalation)
```

---

## State Management

### Project State Structure

```python
class ProjectState:
    request_id: str
    status: str  # 'pending' | 'in_progress' | 'completed' | 'failed' | 'blocked'
    phase: str  # 'initiation' | 'planning' | 'execution' | 'monitoring' | 'closure'

    # Progress tracking
    progress_percentage: int  # 0-100
    tasks_completed: int
    tasks_remaining: int
    start_time: datetime
    last_update_time: datetime

    # Resource tracking
    tokens_budget: int
    tokens_used: int
    tokens_remaining: int
    api_calls: int
    cost_usd: float

    # Plan and outputs
    plan: Dict  # From Planner Agent
    phase_outputs: Dict[str, List]  # Outputs per phase
    deliverables: List[Dict]

    # Risk and issue tracking
    risks: List[Dict]
    issues: List[Dict]
    blockers: List[Dict]

    # Agent communication
    messages: List[Dict]  # All A2A messages
    active_agents: List[str]  # Currently active agent IDs

    # Decisions
    go_decisions: Dict[str, Dict]  # Phase gate decisions

    def to_dict(self) -> Dict:
        """Serialize state to JSON"""
        ...

    def from_dict(cls, data: Dict) -> 'ProjectState':
        """Deserialize state from JSON"""
        ...

    def save(self, path: str):
        """Persist state to disk"""
        ...

    def load(cls, path: str) -> 'ProjectState':
        """Load state from disk"""
        ...
```

### State Transitions

```
User Request → PENDING
    ↓ (accept_request)
PENDING → IN_PROGRESS
    ↓ (delegate to Planner)
IN_PROGRESS → (Planner working)
    ↓ (plan received)
IN_PROGRESS → (delegate to Supervisor via Planner)
    ↓ (execution in progress)
IN_PROGRESS → (monitor progress)
    ↓ (phase gate reviews)
IN_PROGRESS → (deliverables completed)
    ↓ (final review)
IN_PROGRESS → COMPLETED (success)
    OR
IN_PROGRESS → FAILED (unrecoverable error)
    OR
IN_PROGRESS → BLOCKED (needs user input)
```

---

## Error Handling

### Error Categories

1. **User Request Errors**
   - Ambiguous request
   - Unsupported project type
   - Missing required information
   - **Action**: Request clarification from user

2. **Resource Exhaustion Errors**
   - Token budget exceeded
   - Time limit exceeded
   - API rate limit hit
   - **Action**: Request budget increase or terminate gracefully

3. **Agent Communication Errors**
   - Agent timeout
   - Malformed message
   - Lost connection
   - **Action**: Retry with exponential backoff (max 3 attempts)

4. **Quality Errors**
   - Deliverable below quality threshold
   - Tests failing
   - Security vulnerability detected
   - **Action**: Retry with different approach or specialist

5. **Safety Errors**
   - Malicious intent detected
   - Destructive operation attempted
   - Privacy violation
   - **Action**: Terminate immediately and report

### Retry Strategy

```python
class RetryStrategy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    max_delay_seconds: float = 60.0

    def should_retry(self, attempt: int, error: Exception) -> bool:
        if attempt >= self.max_attempts:
            return False

        # Don't retry safety errors or user errors
        if isinstance(error, (SafetyError, UserError)):
            return False

        # Retry communication and transient errors
        if isinstance(error, (TimeoutError, ConnectionError, RateLimitError)):
            return True

        return False

    def get_delay(self, attempt: int) -> float:
        delay = self.base_delay_seconds * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay_seconds)
```

### Circuit Breaker

```python
class CircuitBreaker:
    """Prevent cascading failures by stopping requests to failing agents"""

    failure_threshold: int = 5  # Open after 5 failures
    timeout_seconds: float = 30.0  # Try again after 30 seconds

    state: str = 'closed'  # 'closed' | 'open' | 'half_open'
    failure_count: int = 0
    last_failure_time: datetime = None

    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if (datetime.now() - self.last_failure_time).seconds > self.timeout_seconds:
                self.state = 'half_open'
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            if self.state == 'half_open':
                self.state = 'closed'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = 'open'

            raise e
```

---

## MCP Tools Required

The Coordinator Agent **does not directly use MCP tools**. It operates at a high abstraction level and delegates all tool usage to lower-tier agents.

**Indirect MCP Tool Usage** (via delegation):
- filesystem (via Planner, Supervisor, Specialists)
- github (via Specialists)
- brave-search (via Research Agent)
- memory (via all agents for context persistence)

**Note**: The Coordinator may use the `memory` MCP server to persist project state across sessions.

---

## Success Criteria

The Coordinator Agent is successful when:

1. **Request Understanding**: ≥95% of user requests correctly interpreted
2. **Decision Quality**: ≥90% of GO/NO-GO decisions validated as correct
3. **Resource Management**: ≤10% variance from estimated resource usage
4. **Completion Rate**: ≥80% of accepted projects completed successfully
5. **Response Time**: ≤5 seconds for initial response to user request
6. **Error Recovery**: ≥70% of errors resolved automatically without user intervention

---

## Performance Requirements

- **Latency**:
  - Initial request processing: <2 seconds
  - Phase gate decision: <5 seconds
  - Final response assembly: <3 seconds

- **Throughput**:
  - Handle 100+ concurrent requests (future scaling)

- **Memory**:
  - ≤500MB per active project
  - Support 10+ active projects simultaneously

- **Token Efficiency**:
  - Coordinator itself uses <5% of total project tokens
  - Efficient delegation minimizes redundant context passing

---

## Testing Requirements

### Unit Tests

1. Test request parsing and validation
2. Test decision logic (accept/reject, GO/NO-GO)
3. Test message schema validation
4. Test state serialization/deserialization
5. Test error handling and retry logic
6. Test circuit breaker functionality

### Integration Tests

1. Test full request → plan → execute → deliver flow
2. Test communication with Planner Agent
3. Test progress monitoring and status updates
4. Test escalation handling
5. Test resource tracking and budget management

### End-to-End Tests

1. Test complete project lifecycle (simple project)
2. Test complex project with multiple specialists
3. Test error scenarios (timeout, resource exhaustion)
4. Test user clarification flow
5. Test phase gate reviews

---

## Implementation Notes

### Technology Stack

- **Language**: Python 3.10+
- **LLM**: Anthropic Claude Sonnet 4.5 (primary), Ollama Gemma2 (fallback)
- **Message Queue**: Redis or SQLite (for persistence)
- **State Storage**: JSON files or SQLite
- **Logging**: Structured logging (JSON format)

### Design Patterns

- **Strategy Pattern**: For decision algorithms (different strategies for different project types)
- **State Pattern**: For project state management
- **Observer Pattern**: For progress monitoring and updates
- **Circuit Breaker Pattern**: For fault tolerance
- **Retry Pattern**: For transient error handling

### Key Classes

```python
class CoordinatorAgent:
    """Main Coordinator Agent class"""

    def __init__(self, config: Config):
        self.config = config
        self.state_manager = StateManager()
        self.message_queue = MessageQueue()
        self.planner_agent = PlannerAgentProxy()
        self.decision_engine = DecisionEngine()
        self.retry_strategy = RetryStrategy()
        self.circuit_breaker = CircuitBreaker()

    async def process_request(self, user_request: UserRequest) -> CoordinatorResponse:
        """Main entry point for processing user requests"""
        ...

    async def delegate_to_planner(self, request: PlanningRequest) -> PlanningResponse:
        """Delegate to Planner Agent"""
        ...

    def make_phase_gate_decision(self, phase: str, outputs: Dict) -> GateDecision:
        """Make GO/NO-GO decision at phase gate"""
        ...

    def handle_escalation(self, escalation: Escalation) -> EscalationResponse:
        """Handle escalation from lower-tier agents"""
        ...

    def monitor_progress(self) -> ProgressUpdate:
        """Check progress of active projects"""
        ...
```

---

## Future Enhancements

### Version 2.0

- **Multi-project orchestration**: Coordinate multiple projects simultaneously with shared context
- **Learning from history**: Use past projects to improve decision-making
- **Predictive resource estimation**: Better prediction of token/time requirements
- **Dynamic budget allocation**: Intelligently redistribute resources across phases
- **User preference learning**: Learn user preferences over time

### Version 3.0

- **Multi-agent debate**: Multiple Coordinator agents debate decisions (consensus-based)
- **Explainable AI**: Detailed explanations of all decisions
- **Interactive planning**: Real-time collaboration with user during planning
- **Cost optimization**: Intelligent routing to cheapest/fastest model for each task

---

**Document Owner**: PM-Agents Architecture Team
**Last Updated**: 2025-10-28
**Status**: ✅ APPROVED for Implementation (Phase 3)
**Next**: Create Planner Agent Specification
