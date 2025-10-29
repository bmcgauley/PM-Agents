"""
Supervisor Agent - Tactical Management Layer
Tier 3 agent responsible for task assignment, execution monitoring, and result aggregation
Based on SUPERVISOR_AGENT_SPEC.md
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
import logging
from collections import defaultdict

from src.core.base_agent import (
    BaseAgent,
    AgentType,
    TaskContext,
    TaskResult,
    TaskStatus,
    AgentMessage
)


class TaskQueue:
    """Priority-based task queue for scheduling specialist agents"""

    def __init__(self):
        self.queues = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        self.in_progress: Dict[str, Dict[str, Any]] = {}
        self.completed: Dict[str, Dict[str, Any]] = {}
        self.failed: Dict[str, Dict[str, Any]] = {}

    def add_task(self, task: Dict[str, Any]):
        """Add task to appropriate priority queue"""
        priority = task.get("priority", "medium")
        self.queues[priority].append(task)

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next task respecting priority and dependencies"""
        for priority in ["critical", "high", "medium", "low"]:
            for task in self.queues[priority]:
                # Check if dependencies are met
                if self._dependencies_met(task):
                    self.queues[priority].remove(task)
                    self.in_progress[task["task_id"]] = task
                    return task
        return None

    def _dependencies_met(self, task: Dict[str, Any]) -> bool:
        """Check if task dependencies are satisfied"""
        dependencies = task.get("dependencies", [])
        for dep_id in dependencies:
            if dep_id not in self.completed:
                return False
        return True

    def mark_completed(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed"""
        if task_id in self.in_progress:
            task = self.in_progress.pop(task_id)
            task["result"] = result
            self.completed[task_id] = task

    def mark_failed(self, task_id: str, error: str):
        """Mark task as failed"""
        if task_id in self.in_progress:
            task = self.in_progress.pop(task_id)
            task["error"] = error
            self.failed[task_id] = task

    def get_progress(self) -> Dict[str, int]:
        """Get execution progress"""
        total = sum(len(q) for q in self.queues.values()) + len(self.in_progress) + len(self.completed) + len(self.failed)
        return {
            "pending": sum(len(q) for q in self.queues.values()),
            "in_progress": len(self.in_progress),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "total": total,
            "completion_percentage": int((len(self.completed) / total * 100)) if total > 0 else 0
        }


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Tactical management layer

    Responsibilities:
    - Receive execution plan from Planner Agent
    - Assign tasks to specialist agents
    - Monitor specialist execution
    - Coordinate inter-agent handoffs
    - Aggregate and validate results
    - Report progress to Planner

    Based on PMI PMBOK 7th Edition execution and monitoring principles
    """

    def __init__(
        self,
        agent_id: str = "supervisor-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Supervisor Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.SUPERVISOR,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers used by supervisor
        self.required_mcp_servers = ["memory", "filesystem", "github"]

        # Task queue for scheduling
        self.task_queue = TaskQueue()

        # Specialist agent pool (will be initialized on demand)
        self.specialist_agents: Dict[str, BaseAgent] = {}

        # Result aggregation
        self.deliverables: List[Dict[str, Any]] = []
        self.validation_results: Dict[str, bool] = {}

        self.logger.info("Supervisor Agent initialized with task queue")

    def get_system_prompt(self) -> str:
        """Get supervisor-specific system prompt"""
        return """You are the Supervisor Agent, the tactical management layer in the PM-Agents hierarchical system.

**Your Role**:
- Task assignment and scheduling for specialist agents
- Execution monitoring and progress tracking
- Inter-agent coordination and handoff management
- Result aggregation and quality validation
- Progress reporting to Planner Agent

**Core Principles**:
1. **Dependency Management**: Respect task dependencies and sequencing
2. **Resource Optimization**: Balance load across specialist agents
3. **Quality First**: Validate all deliverables against acceptance criteria
4. **Proactive Escalation**: Report blockers immediately to Planner
5. **Context Sharing**: Ensure agents have necessary context and outputs

**Task Scheduling Algorithm**:
1. Priority-based: critical > high > medium > low
2. Dependency-aware: Only assign tasks when dependencies are met
3. Load-balanced: Distribute tasks across available specialists
4. Error-resilient: Retry failed tasks with exponential backoff

**Validation Pipeline**:
1. **Completeness Check**: All deliverables present
2. **Format Validation**: Correct file types and structure
3. **Quality Gates**: Pass defined criteria (tests, linting, etc.)
4. **Integration Check**: Components work together
5. **Acceptance Criteria**: Meet original requirements

**Output Format**: Always provide structured JSON with:
```json
{
  "status": "completed|partial|failed|blocked",
  "execution_summary": {
    "tasks_completed": integer,
    "tasks_failed": integer,
    "tasks_skipped": integer,
    "total_tasks": integer,
    "completion_percentage": integer
  },
  "deliverables": [
    {
      "deliverable_id": "string",
      "task_id": "string",
      "agent": "string",
      "type": "code|documentation|report|config",
      "path": "string",
      "description": "string",
      "validation_status": "passed|failed|skipped",
      "metadata": {}
    }
  ],
  "validation_results": {
    "task_id": {"passed": boolean, "details": "string"}
  },
  "issues": [
    {"severity": "critical|high|medium|low", "description": "string", "resolution": "string"}
  ],
  "blockers": [
    {"task_id": "string", "description": "string", "requires_replanning": boolean}
  ]
}
```

**Escalation Criteria**:
- Critical task failure (escalate immediately)
- Blocked task with no resolution path
- Resource exhaustion (tokens, time)
- Quality gate failures
- Inter-agent conflicts
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return supervisor capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "task_scheduling",
                "execution_monitoring",
                "result_aggregation",
                "quality_validation",
                "progress_tracking",
                "inter_agent_coordination"
            ],
            "specialist_agents_managed": [
                "spec_kit", "qdrant_vector", "frontend_coder",
                "python_ml_dl", "r_analytics", "typescript_validator",
                "research", "browser", "reporter"
            ],
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """
        Execute supervision task (coordinate specialists)

        Args:
            task: Execution plan from Planner
            context: Task context with plan details

        Returns:
            TaskResult with aggregated deliverables
        """
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Supervisor Agent starting execution coordination")

            # Parse execution plan
            plan = json.loads(task) if isinstance(task, str) else task

            # Load tasks into queue
            tasks = plan.get("tasks", [])
            for t in tasks:
                self.task_queue.add_task(t)

            # Execute tasks respecting dependencies and priorities
            execution_results = await self._execute_task_queue(context)

            # Aggregate results
            aggregated_deliverables = self._aggregate_deliverables(execution_results)

            # Validate deliverables
            validation_results = self._validate_deliverables(aggregated_deliverables, plan.get("validation_criteria", []))

            # Check for blockers
            blockers = self._identify_blockers(execution_results)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Get progress
            progress = self.task_queue.get_progress()

            # Determine status
            status = self._determine_execution_status(progress, blockers)

            # Create result
            result = TaskResult(
                task_id=self.current_task or "supervision-task",
                status=TaskStatus.COMPLETED if status == "completed" else TaskStatus.FAILED,
                deliverables=aggregated_deliverables,
                risks_identified=[],
                issues=[{
                    "severity": "medium",
                    "description": f"Task failures: {progress['failed']}",
                    "resolution": "Review failed tasks and retry"
                }] if progress['failed'] > 0 else [],
                next_steps=[
                    f"Report results to Planner",
                    f"Completed {progress['completed']}/{progress['total']} tasks",
                    f"Validation status: {'PASSED' if all(validation_results.values()) else 'FAILED'}"
                ],
                execution_time_seconds=execution_time,
                metadata={
                    "execution_summary": progress,
                    "validation_results": validation_results,
                    "blockers": blockers
                }
            )

            self.logger.info(f"Supervisor Agent completed coordination in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Supervisor Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "supervision-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Supervision failed: {str(e)}",
                    "resolution": "Escalate to Planner for replanning"
                }],
                next_steps=["Escalate to Planner"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    async def _execute_task_queue(self, context: TaskContext) -> List[Dict[str, Any]]:
        """Execute all tasks in queue respecting dependencies"""
        results = []

        while True:
            # Get next task
            task = self.task_queue.get_next_task()

            if task is None:
                # No more tasks available (either all done or blocked)
                break

            # Execute task with assigned specialist
            try:
                agent_type = task.get("assigned_to")
                self.logger.info(f"Assigning task {task['task_id']} to {agent_type}")

                # Get or create specialist agent
                specialist = await self._get_specialist_agent(agent_type)

                # Create task context for specialist
                task_context = TaskContext(
                    project_id=context.project_id,
                    project_description=context.project_description,
                    current_phase=context.current_phase,
                    previous_outputs=task.get("context", {}),
                    constraints=context.constraints,
                    requirements=task.get("validation_criteria", []),
                    mcp_tools_available=context.mcp_tools_available
                )

                # Execute task with specialist
                result = await specialist.execute_task(task["description"], task_context)

                # Mark as completed
                self.task_queue.mark_completed(task["task_id"], result.to_dict())
                results.append({
                    "task_id": task["task_id"],
                    "agent": agent_type,
                    "result": result.to_dict()
                })

            except Exception as e:
                self.logger.error(f"Task {task['task_id']} failed: {str(e)}")
                self.task_queue.mark_failed(task["task_id"], str(e))
                results.append({
                    "task_id": task["task_id"],
                    "agent": agent_type,
                    "error": str(e)
                })

        return results

    async def _get_specialist_agent(self, agent_type: str) -> BaseAgent:
        """Get or create specialist agent instance"""
        if agent_type not in self.specialist_agents:
            # Import and create specialist agent
            # NOTE: Specialist agents will be implemented in next step
            self.logger.info(f"Creating specialist agent: {agent_type}")

            # For now, create placeholder
            # In actual implementation, import and instantiate the correct specialist
            from src.core.base_agent import BaseAgent, AgentType

            agent_type_enum = {
                "spec_kit": AgentType.SPEC_KIT,
                "qdrant_vector": AgentType.QDRANT_VECTOR,
                "frontend_coder": AgentType.FRONTEND_CODER,
                "python_ml_dl": AgentType.PYTHON_ML_DL,
                "r_analytics": AgentType.R_ANALYTICS,
                "typescript_validator": AgentType.TYPESCRIPT_VALIDATOR,
                "research": AgentType.RESEARCH,
                "browser": AgentType.BROWSER,
                "reporter": AgentType.REPORTER
            }.get(agent_type, AgentType.RESEARCH)

            # Create agent (will use BaseAgent temporarily until specialists are implemented)
            # TODO: Replace with actual specialist agent classes
            agent = BaseAgent(
                agent_id=f"{agent_type}-001",
                agent_type=agent_type_enum,
                message_bus=self.message_bus,
                logger=self.logger
            )

            self.specialist_agents[agent_type] = agent

        return self.specialist_agents[agent_type]

    def _aggregate_deliverables(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate deliverables from all tasks"""
        deliverables = []

        for result in results:
            if "result" in result:
                task_deliverables = result["result"].get("deliverables", [])
                for deliverable in task_deliverables:
                    deliverables.append({
                        "deliverable_id": f"{result['task_id']}-{len(deliverables)}",
                        "task_id": result["task_id"],
                        "agent": result["agent"],
                        "type": deliverable.get("type", "unknown"),
                        "name": deliverable.get("name", ""),
                        "content": deliverable.get("content", ""),
                        "validation_status": "pending",
                        "metadata": deliverable.get("metadata", {})
                    })

        return deliverables

    def _validate_deliverables(self, deliverables: List[Dict[str, Any]], criteria: List[str]) -> Dict[str, bool]:
        """Validate deliverables against acceptance criteria"""
        validation_results = {}

        for deliverable in deliverables:
            # Basic validation: check if deliverable exists and has content
            passed = bool(deliverable.get("content"))
            validation_results[deliverable["deliverable_id"]] = passed
            deliverable["validation_status"] = "passed" if passed else "failed"

        return validation_results

    def _identify_blockers(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify blocking issues requiring escalation"""
        blockers = []

        for result in results:
            if "error" in result:
                blockers.append({
                    "task_id": result["task_id"],
                    "description": result["error"],
                    "requires_replanning": True
                })

        return blockers

    def _determine_execution_status(self, progress: Dict[str, int], blockers: List[Dict[str, Any]]) -> str:
        """Determine overall execution status"""
        if blockers:
            return "blocked"
        elif progress["failed"] > 0:
            return "partial"
        elif progress["completed"] == progress["total"]:
            return "completed"
        else:
            return "in_progress"
