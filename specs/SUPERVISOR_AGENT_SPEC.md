# Supervisor Agent Specification

**Agent Type**: Tactical Management Layer (Tier 3)
**Version**: 1.0
**Status**: Planning Phase
**Date**: 2025-10-28

---

## Overview

The Supervisor Agent is the tactical management layer in the PM-Agents hierarchical system. It receives detailed plans from the Planner Agent, assigns tasks to specialist agents, monitors their execution, aggregates results, validates deliverables, and reports progress back to the Planner.

---

## Role and Responsibilities

### Primary Responsibilities

1. **Receive execution plan from Planner**
   - Parse detailed plan with tasks and dependencies
   - Understand agent assignments
   - Validate plan feasibility

2. **Task assignment to specialists**
   - Assign tasks to appropriate specialist agents
   - Provide necessary context and requirements
   - Manage task queue and priorities

3. **Monitor specialist execution**
   - Track progress of each specialist agent
   - Collect intermediate results
   - Detect delays, errors, and blockers

4. **Inter-agent coordination**
   - Coordinate handoffs between specialists
   - Manage shared resources (Qdrant, file system)
   - Resolve inter-agent conflicts

5. **Result aggregation**
   - Collect outputs from multiple specialists
   - Merge and validate results
   - Ensure consistency and quality

6. **Quality validation**
   - Verify deliverables meet acceptance criteria
   - Run validation checks (tests, linting, type checking)
   - Ensure quality gates pass

7. **Progress reporting**
   - Send status updates to Planner
   - Report completed tasks
   - Escalate blockers requiring replanning

### Responsibilities Outside Scope

- ❌ Strategic planning (Planner Agent)
- ❌ GO/NO-GO decisions (Coordinator Agent)
- ❌ Direct code generation (Specialist Agents handle this)
- ❌ User communication (via Coordinator only)

---

## Input/Output Schemas

### Input: Execution Request (from Planner)

```json
{
  "message_id": "string (UUID)",
  "from": "planner",
  "to": "supervisor",
  "type": "execution_request",
  "timestamp": "ISO8601 datetime",
  "payload": {
    "plan_id": "string (UUID)",
    "request_id": "string",
    "tasks": [
      {
        "task_id": "string",
        "description": "string",
        "assigned_to": "string (agent type)",
        "dependencies": ["string (task_ids)"],
        "estimated_tokens": "integer",
        "estimated_time_seconds": "integer",
        "priority": "string (critical|high|medium|low)",
        "deliverables": ["string"],
        "validation_criteria": ["string"],
        "context": {
          "files_to_modify": ["string"],
          "references": ["string"],
          "constraints": {}
        }
      }
    ],
    "agent_assignments": {
      "spec_kit": ["task_ids"],
      "qdrant_vector": ["task_ids"],
      "frontend_coder": ["task_ids"],
      "python_ml": ["task_ids"],
      "r_analytics": ["task_ids"],
      "typescript_validator": ["task_ids"],
      "research": ["task_ids"],
      "browser": ["task_ids"],
      "reporter": ["task_ids"]
    },
    "validation_criteria": ["string"],
    "risks": [
      {
        "risk_id": "string",
        "description": "string",
        "mitigation": "string",
        "owner": "string"
      }
    ]
  }
}
```

### Output: Execution Response (to Planner)

```json
{
  "message_id": "string (UUID)",
  "from": "supervisor",
  "to": "planner",
  "type": "execution_response",
  "timestamp": "ISO8601 datetime",
  "in_reply_to": "string (request message_id)",
  "payload": {
    "status": "string (completed|partial|failed|blocked)",
    "plan_id": "string",
    "execution_summary": {
      "tasks_completed": "integer",
      "tasks_failed": "integer",
      "tasks_skipped": "integer",
      "total_tasks": "integer",
      "completion_percentage": "integer (0-100)"
    },
    "deliverables": [
      {
        "deliverable_id": "string",
        "task_id": "string",
        "agent": "string",
        "type": "string (code|documentation|report|config)",
        "path": "string",
        "description": "string",
        "validation_status": "string (passed|failed|skipped)",
        "metadata": {}
      }
    ],
    "validation_results": [
      {
        "validator": "string",
        "status": "string (passed|failed)",
        "details": "string",
        "issues": [
          {
            "severity": "string (error|warning|info)",
            "message": "string",
            "file": "string",
            "line": "integer"
          }
        ]
      }
    ],
    "resource_usage": {
      "tokens_used": "integer",
      "time_elapsed_seconds": "integer",
      "agent_execution_times": {
        "spec_kit": "integer (seconds)",
        "frontend_coder": "integer (seconds)",
        "...": "integer"
      }
    },
    "issues_encountered": [
      {
        "issue_id": "string",
        "task_id": "string",
        "agent": "string",
        "severity": "string (critical|high|medium|low)",
        "description": "string",
        "resolution": "string (resolved|escalated|deferred)",
        "resolution_details": "string"
      }
    ],
    "recommendations": ["string"]
  }
}
```

### Progress Update (to Planner, periodic)

```json
{
  "message_id": "string (UUID)",
  "from": "supervisor",
  "to": "planner",
  "type": "progress_update",
  "timestamp": "ISO8601 datetime",
  "payload": {
    "plan_id": "string",
    "progress_percentage": "integer (0-100)",
    "tasks_completed": ["string (task_ids)"],
    "tasks_in_progress": [
      {
        "task_id": "string",
        "agent": "string",
        "started_at": "ISO8601 datetime",
        "estimated_completion": "ISO8601 datetime"
      }
    ],
    "tasks_pending": ["string (task_ids)"],
    "tasks_blocked": [
      {
        "task_id": "string",
        "reason": "string",
        "requires_replanning": "boolean"
      }
    ],
    "resource_usage": {
      "tokens_used": "integer",
      "time_elapsed_seconds": "integer"
    }
  }
}
```

---

## Task Assignment Strategy

### Assignment Algorithm

```python
def assign_tasks(plan):
    """
    Assign tasks to specialist agents based on dependencies and availability

    Returns:
        Execution schedule with task assignments
    """
    # 1. Build dependency graph
    graph = build_dependency_graph(plan.tasks)

    # 2. Topological sort (execution order)
    sorted_tasks = topological_sort(plan.tasks, graph)

    # 3. Identify parallelizable tasks
    execution_levels = identify_execution_levels(sorted_tasks, graph)

    # 4. Assign to agents
    schedule = ExecutionSchedule()

    for level, tasks_at_level in execution_levels.items():
        # Tasks at same level can run in parallel
        for task in tasks_at_level:
            agent_type = task.assigned_to
            agent = get_or_create_agent(agent_type)

            schedule.add(
                level=level,
                task=task,
                agent=agent,
                parallel_with=[t.task_id for t in tasks_at_level if t != task]
            )

    return schedule
```

### Execution Order

**Example Execution Schedule**:

```
Level 0 (Start):
  - TASK-001: Initialize project (spec_kit) → 30s

Level 1 (After initialization):
  - TASK-002: Index codebase (qdrant_vector) → 20s

Level 2 (Parallel development):
  - TASK-003: Implement auth (frontend_coder) → 60s
  - TASK-004: Research best practices (research) → 45s  [PARALLEL]

Level 3 (More development):
  - TASK-005: Implement product catalog (frontend_coder) → 70s
  - TASK-006: Implement admin UI (frontend_coder) → 50s

Level 4 (Validation):
  - TASK-007: Validate TypeScript (typescript_validator) → 40s

Level 5 (Documentation):
  - TASK-008: Generate docs (reporter) → 25s
```

**Total Critical Path Time**: 30 + 20 + 60 + 70 + 40 + 25 = 245 seconds (~4 minutes)

**With Parallelization**: Tasks 003 and 004 run in parallel, saving 45 seconds

---

## Specialist Agent Management

### Agent Proxy Pattern

```python
class SpecialistAgentProxy:
    """
    Proxy for communicating with specialist agents

    Handles:
    - Message formatting
    - Timeout management
    - Retry logic
    - Result caching
    """

    def __init__(self, agent_type: str, config: AgentConfig):
        self.agent_type = agent_type
        self.config = config
        self.timeout_seconds = config.timeout_seconds
        self.max_retries = 3
        self.circuit_breaker = CircuitBreaker()

    async def execute_task(self, task: Task, context: Dict) -> TaskResult:
        """
        Execute task via specialist agent

        Returns:
            TaskResult with outputs and status
        """
        # Format task for specialist
        agent_request = self.format_request(task, context)

        # Execute with circuit breaker
        try:
            result = await self.circuit_breaker.call(
                self._execute_with_retry,
                agent_request
            )
            return result

        except CircuitBreakerOpenError:
            raise AgentUnavailableError(f"{self.agent_type} is unavailable")

    async def _execute_with_retry(self, request):
        """Execute with retry logic"""
        for attempt in range(self.max_retries):
            try:
                result = await self.call_agent(request)

                # Validate result
                if self.is_valid_result(result):
                    return result
                else:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise InvalidResultError("Invalid result from agent")

            except TimeoutError:
                if attempt < self.max_retries - 1:
                    # Retry with increased timeout
                    self.timeout_seconds *= 1.5
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise

        raise MaxRetriesExceededError(f"Failed after {self.max_retries} attempts")

    async def call_agent(self, request):
        """
        Actual agent call (implementation depends on agent type)

        For MCP-based agents:
        - Use MCP tool calls via agent's MCP server

        For LLM-based agents:
        - Format prompt and call LLM
        """
        # Implementation varies by agent type
        pass
```

### Agent Pool Management

```python
class AgentPool:
    """
    Manages pool of specialist agent instances

    Features:
    - Lazy initialization (create agents on-demand)
    - Agent reuse across tasks
    - Resource limiting (max N agents of each type)
    - Health monitoring
    """

    def __init__(self, config: SupervisorConfig):
        self.config = config
        self.agents = {}  # agent_type -> List[AgentProxy]
        self.max_agents_per_type = 3  # Limit concurrent agents

    def get_agent(self, agent_type: str) -> SpecialistAgentProxy:
        """
        Get available agent of specified type

        Returns:
            AgentProxy instance
        """
        # Check if agents of this type exist
        if agent_type not in self.agents:
            self.agents[agent_type] = []

        # Find available agent
        for agent in self.agents[agent_type]:
            if not agent.is_busy():
                return agent

        # Create new agent if under limit
        if len(self.agents[agent_type]) < self.max_agents_per_type:
            agent = self.create_agent(agent_type)
            self.agents[agent_type].append(agent)
            return agent

        # Wait for agent to become available
        return self.wait_for_available_agent(agent_type)

    def create_agent(self, agent_type: str) -> SpecialistAgentProxy:
        """Create new agent instance"""
        config = self.config.get_agent_config(agent_type)
        return SpecialistAgentProxy(agent_type, config)

    async def wait_for_available_agent(self, agent_type: str) -> SpecialistAgentProxy:
        """Wait for agent to become available"""
        while True:
            for agent in self.agents[agent_type]:
                if not agent.is_busy():
                    return agent
            await asyncio.sleep(1)
```

---

## Progress Monitoring

### Monitoring Strategy

```python
class ProgressMonitor:
    """
    Monitors execution progress and collects metrics

    Features:
    - Real-time progress tracking
    - Resource usage monitoring
    - Anomaly detection
    - Performance metrics
    """

    def __init__(self):
        self.tasks_status = {}  # task_id -> Status
        self.start_times = {}  # task_id -> datetime
        self.completion_times = {}  # task_id -> datetime

    def on_task_started(self, task_id: str, agent: str):
        """Called when task starts execution"""
        self.tasks_status[task_id] = TaskStatus.IN_PROGRESS
        self.start_times[task_id] = datetime.now()

        logger.info(f"Task {task_id} started by {agent}")

    def on_task_completed(self, task_id: str, result: TaskResult):
        """Called when task completes"""
        self.tasks_status[task_id] = TaskStatus.COMPLETED
        self.completion_times[task_id] = datetime.now()

        # Calculate metrics
        elapsed = self.completion_times[task_id] - self.start_times[task_id]

        logger.info(f"Task {task_id} completed in {elapsed.total_seconds()}s")

        # Check for anomalies
        if elapsed.total_seconds() > result.estimated_time * 2:
            logger.warning(f"Task {task_id} took 2x longer than estimated")

    def on_task_failed(self, task_id: str, error: Exception):
        """Called when task fails"""
        self.tasks_status[task_id] = TaskStatus.FAILED

        logger.error(f"Task {task_id} failed: {str(error)}")

    def get_progress_percentage(self) -> int:
        """Calculate overall progress percentage"""
        total_tasks = len(self.tasks_status)
        completed_tasks = sum(
            1 for status in self.tasks_status.values()
            if status == TaskStatus.COMPLETED
        )

        return int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    def get_estimated_completion_time(self, plan: ExecutionPlan) -> datetime:
        """Estimate when execution will complete"""
        # Based on completed tasks and their actual times
        completed = [
            task_id for task_id, status in self.tasks_status.items()
            if status == TaskStatus.COMPLETED
        ]

        if not completed:
            # No data yet, use plan estimates
            return datetime.now() + timedelta(seconds=plan.total_estimated_time)

        # Calculate average slowdown factor
        slowdown_factors = []
        for task_id in completed:
            task = plan.get_task(task_id)
            elapsed = (self.completion_times[task_id] - self.start_times[task_id]).total_seconds()
            slowdown = elapsed / task.estimated_time_seconds
            slowdown_factors.append(slowdown)

        avg_slowdown = sum(slowdown_factors) / len(slowdown_factors)

        # Estimate remaining time
        remaining_tasks = [
            task for task in plan.tasks
            if self.tasks_status.get(task.task_id) != TaskStatus.COMPLETED
        ]
        remaining_time = sum(task.estimated_time_seconds for task in remaining_tasks) * avg_slowdown

        return datetime.now() + timedelta(seconds=remaining_time)
```

---

## Result Aggregation

### Aggregation Strategy

```python
class ResultAggregator:
    """
    Aggregates results from multiple specialist agents

    Handles:
    - Collecting outputs from specialists
    - Merging file changes
    - Resolving conflicts
    - Validating consistency
    """

    def __init__(self):
        self.results = {}  # task_id -> TaskResult

    def add_result(self, task_id: str, result: TaskResult):
        """Add result from specialist agent"""
        self.results[task_id] = result

    def aggregate(self, plan: ExecutionPlan) -> AggregatedResult:
        """
        Aggregate all results into cohesive output

        Returns:
            AggregatedResult with merged deliverables
        """
        aggregated = AggregatedResult()

        # Group results by deliverable type
        code_deliverables = []
        docs_deliverables = []
        config_deliverables = []

        for task_id, result in self.results.items():
            for deliverable in result.deliverables:
                if deliverable.type == 'code':
                    code_deliverables.append(deliverable)
                elif deliverable.type == 'documentation':
                    docs_deliverables.append(deliverable)
                elif deliverable.type == 'config':
                    config_deliverables.append(deliverable)

        # Merge code deliverables (check for conflicts)
        merged_code = self.merge_code_deliverables(code_deliverables)
        aggregated.code = merged_code

        # Merge documentation
        merged_docs = self.merge_docs_deliverables(docs_deliverables)
        aggregated.docs = merged_docs

        # Merge configs
        merged_configs = self.merge_config_deliverables(config_deliverables)
        aggregated.configs = merged_configs

        return aggregated

    def merge_code_deliverables(self, deliverables):
        """
        Merge code files from multiple agents

        Handles:
        - Multiple agents modifying same file
        - Conflict detection
        - Intelligent merging
        """
        file_versions = {}  # file_path -> List[FileVersion]

        for deliverable in deliverables:
            for file_path, content in deliverable.files.items():
                if file_path not in file_versions:
                    file_versions[file_path] = []

                file_versions[file_path].append(FileVersion(
                    agent=deliverable.agent,
                    task_id=deliverable.task_id,
                    content=content
                ))

        merged_files = {}

        for file_path, versions in file_versions.items():
            if len(versions) == 1:
                # Only one version, no conflict
                merged_files[file_path] = versions[0].content
            else:
                # Multiple versions, attempt merge
                merged = self.merge_file_versions(file_path, versions)
                if merged.has_conflicts:
                    raise MergeConflictError(
                        f"Conflict in {file_path} between {[v.agent for v in versions]}"
                    )
                merged_files[file_path] = merged.content

        return merged_files
```

---

## Quality Validation

### Validation Pipeline

```python
class ValidationPipeline:
    """
    Runs validation checks on deliverables

    Validators:
    - TypeScript type checking (for frontend projects)
    - Python linting (for ML projects)
    - R syntax checking (for analytics projects)
    - Test execution
    - Security scans
    - Documentation completeness
    """

    def __init__(self, project_type: str):
        self.project_type = project_type
        self.validators = self.select_validators(project_type)

    def select_validators(self, project_type: str) -> List[Validator]:
        """Select appropriate validators for project type"""
        validators = []

        if project_type in ['frontend', 'fullstack']:
            validators.append(TypeScriptValidator())
            validators.append(ESLintValidator())
            validators.append(TestValidator('jest'))

        if project_type in ['ml', 'data_science']:
            validators.append(PythonLintValidator())
            validators.append(TestValidator('pytest'))

        if project_type in ['analytics']:
            validators.append(RSyntaxValidator())
            validators.append(TestValidator('testthat'))

        # Always validate documentation
        validators.append(DocumentationValidator())

        return validators

    async def validate(self, deliverables: List[Deliverable]) -> ValidationResult:
        """
        Run all validators on deliverables

        Returns:
            ValidationResult with pass/fail and issues
        """
        results = []

        for validator in self.validators:
            result = await validator.validate(deliverables)
            results.append(result)

        # Aggregate validation results
        all_passed = all(r.passed for r in results)
        critical_issues = [
            issue for r in results for issue in r.issues
            if issue.severity == 'error'
        ]

        return ValidationResult(
            passed=all_passed and len(critical_issues) == 0,
            results=results,
            critical_issues=critical_issues
        )
```

---

## Error Handling and Recovery

### Error Categories

1. **Task Execution Errors**
   - Agent timeout
   - Agent returns invalid result
   - Agent crashes
   - **Recovery**: Retry task with same or different agent

2. **Validation Errors**
   - Quality gate failure
   - Test failures
   - Type errors
   - **Recovery**: Request fix from responsible agent

3. **Dependency Errors**
   - Dependent task failed
   - Dependent task blocked
   - **Recovery**: Skip task or replan

4. **Resource Errors**
   - Token budget exhausted
   - Time limit exceeded
   - **Recovery**: Request budget increase or terminate

5. **Coordination Errors**
   - Merge conflicts between agents
   - Inconsistent state
   - **Recovery**: Escalate to Planner for replanning

### Recovery Strategies

```python
def recover_from_error(error: ExecutionError, task: Task, plan: ExecutionPlan):
    """
    Attempt to recover from execution error

    Returns:
        RecoveryAction to take
    """
    if isinstance(error, TaskTimeoutError):
        # Retry with increased timeout
        return RecoveryAction.RETRY_WITH_LONGER_TIMEOUT

    elif isinstance(error, InvalidResultError):
        # Retry with different agent or clarified instructions
        return RecoveryAction.RETRY_WITH_CLARIFICATION

    elif isinstance(error, ValidationError):
        # Request fix from agent
        return RecoveryAction.REQUEST_FIX

    elif isinstance(error, DependencyError):
        # Check if task can be skipped
        if task.priority == 'nice_to_have':
            return RecoveryAction.SKIP_TASK
        else:
            # Escalate for replanning
            return RecoveryAction.ESCALATE_TO_PLANNER

    elif isinstance(error, ResourceExhaustedError):
        # Request budget increase
        return RecoveryAction.REQUEST_BUDGET_INCREASE

    elif isinstance(error, MergeConflictError):
        # Escalate to Planner (needs replanning)
        return RecoveryAction.ESCALATE_TO_PLANNER

    else:
        # Unknown error, escalate
        return RecoveryAction.ESCALATE_TO_COORDINATOR
```

---

## MCP Tools Required

The Supervisor Agent **uses MCP tools indirectly** via specialist agents, but may use:

- **filesystem**: To verify file creation/modification by specialists
- **memory**: To persist execution state and coordination data

**Primary tool usage** is via delegation to specialist agents.

---

## Success Criteria

1. **Task Completion Rate**: ≥90% of assigned tasks complete successfully
2. **Coordination Efficiency**: ≤5% overhead from inter-agent coordination
3. **Error Recovery**: ≥80% of errors recovered automatically
4. **Validation Accuracy**: ≥95% of quality issues detected before escalation
5. **Resource Prediction**: ≤15% variance from planned resource usage
6. **Monitoring Responsiveness**: Progress updates every 10 seconds

---

## Implementation Notes

### Key Classes

```python
class SupervisorAgent:
    """Main Supervisor Agent class"""

    def __init__(self, config: SupervisorConfig):
        self.config = config
        self.agent_pool = AgentPool(config)
        self.progress_monitor = ProgressMonitor()
        self.result_aggregator = ResultAggregator()
        self.validation_pipeline = ValidationPipeline(config.project_type)
        self.recovery_handler = RecoveryHandler()

    async def execute_plan(self, plan: ExecutionPlan) -> ExecutionResponse:
        """
        Execute plan by coordinating specialist agents

        Main entry point
        """
        # 1. Create execution schedule
        schedule = self.create_schedule(plan)

        # 2. Execute tasks in order
        for level in schedule.levels:
            # Tasks at same level run in parallel
            tasks_at_level = schedule.get_tasks_at_level(level)

            results = await asyncio.gather(*[
                self.execute_task(task, plan)
                for task in tasks_at_level
            ])

            # Check for failures
            for task, result in zip(tasks_at_level, results):
                if result.status == 'failed':
                    recovery = self.recovery_handler.recover(result.error, task, plan)
                    if recovery == RecoveryAction.ESCALATE_TO_PLANNER:
                        return self.escalate_to_planner(task, result)

        # 3. Aggregate results
        aggregated = self.result_aggregator.aggregate(plan)

        # 4. Validate
        validation = await self.validation_pipeline.validate(aggregated.deliverables)

        if not validation.passed:
            # Attempt fixes
            fixed = await self.request_fixes(validation.critical_issues)
            if not fixed:
                return ExecutionResponse(status='failed', validation=validation)

        # 5. Return success
        return ExecutionResponse(
            status='completed',
            deliverables=aggregated.deliverables,
            validation=validation
        )

    async def execute_task(self, task: Task, plan: ExecutionPlan) -> TaskResult:
        """Execute single task via specialist agent"""
        # Get agent from pool
        agent = self.agent_pool.get_agent(task.assigned_to)

        # Monitor start
        self.progress_monitor.on_task_started(task.task_id, task.assigned_to)

        try:
            # Execute
            result = await agent.execute_task(task, plan.context)

            # Monitor completion
            self.progress_monitor.on_task_completed(task.task_id, result)

            return result

        except Exception as e:
            # Monitor failure
            self.progress_monitor.on_task_failed(task.task_id, e)
            raise
```

---

**Document Owner**: PM-Agents Architecture Team
**Last Updated**: 2025-10-28
**Status**: ✅ APPROVED for Implementation (Phase 3)
**Next**: Create Specialist Agent Specifications (Spec-Kit, Qdrant Vector, Frontend Coder, etc.)
