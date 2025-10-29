"""
Supervisor Agent - Tactical management and specialist agent coordination
Manages day-to-day execution and coordinates specialist agents
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from .base_agent import (
    BaseAgent,
    AgentType,
    TaskContext,
    TaskResult,
    TaskStatus
)


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Tactical management layer
    Responsibilities:
    - Day-to-day task execution management
    - Specialist agent coordination and assignment
    - Progress tracking and status reporting
    - Issue resolution and escalation
    - Quality assurance and validation
    """

    def __init__(
        self,
        agent_id: str = "supervisor-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        message_router: Optional[Any] = None
    ):
        """Initialize Supervisor Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.SUPERVISOR,
            api_key=api_key,
            message_bus=message_bus
        )

        self.message_router = message_router

        # MCP servers required
        self.required_mcp_servers = [
            "filesystem",
            "github",
            "memory",
            "qdrant"
        ]

        # Track assigned tasks and specialist agents
        self.assigned_tasks: Dict[str, Dict[str, Any]] = {}
        self.specialist_agents: Dict[str, List[str]] = {}

        self.logger.info("Supervisor Agent initialized")

    def get_system_prompt(self) -> str:
        """Get supervisor-specific system prompt"""
        return """You are the Supervisor Agent in the PM-Agents hierarchical multi-agent system.

Your role is tactical management and specialist agent coordination. You report to the Planner Agent
and manage 9 specialist agents.

Your responsibilities:
1. **Task Assignment**: Assign tasks to appropriate specialist agents based on capabilities
2. **Progress Monitoring**: Track task progress and identify blockers
3. **Quality Assurance**: Validate specialist agent outputs meet standards
4. **Issue Resolution**: Resolve issues or escalate to Planner when needed
5. **Resource Coordination**: Ensure specialist agents have required tools and context
6. **Status Reporting**: Provide regular status updates to Planner

Available Specialist Agents:
1. **Spec-Kit Agent**: Project initialization and templating (Specify)
2. **Qdrant Vector Agent**: Semantic search and vector operations
3. **Frontend Coder Agent**: React/Next.js/TypeScript development
4. **Python ML/DL Agent**: PyTorch/TensorBoard/ML development
5. **R Analytics Agent**: tidyverse/ggplot2/statistical analysis
6. **TypeScript Validator Agent**: Type checking and code quality
7. **Research Agent**: Technical research and documentation
8. **Browser Agent**: Web scraping and automation
9. **Reporter Agent**: Documentation generation and reporting

Task Assignment Strategy:
- Analyze task requirements and match to agent capabilities
- Consider agent availability and current load
- Ensure agents have required MCP tools
- Provide clear context and success criteria
- Monitor execution and provide support

Quality Assurance:
- Validate deliverables against acceptance criteria
- Run automated checks (tests, linting, type checking)
- Ensure documentation is complete
- Verify integration points work correctly

Issue Management:
- Identify blockers early
- Attempt resolution with available resources
- Escalate to Planner if beyond tactical scope
- Track issue resolution and document lessons learned

Output format: Provide structured JSON with:
- deliverables: Completed work and validations
- risks_identified: Tactical risks (resource, technical)
- issues: Current blockers or problems
- next_steps: Immediate action items
- agent_assignments: Which specialists were assigned which tasks
- validation_results: Quality check results
- escalations: Items requiring Planner attention
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return supervisor capabilities"""
        return {
            "agent_type": "supervisor",
            "capabilities": [
                "task_assignment",
                "progress_monitoring",
                "quality_assurance",
                "issue_resolution",
                "resource_coordination",
                "status_reporting",
                "specialist_management"
            ],
            "managed_specialists": [
                "spec_kit",
                "qdrant_vector",
                "frontend_coder",
                "python_ml_dl",
                "r_analytics",
                "typescript_validator",
                "research",
                "browser",
                "reporter"
            ],
            "mcp_servers": self.required_mcp_servers
        }

    async def assign_task_to_specialist(
        self,
        task_id: str,
        task_description: str,
        specialist_type: AgentType,
        context: TaskContext,
        priority: str = "normal"
    ) -> str:
        """
        Assign task to specialist agent

        Args:
            task_id: Task identifier
            task_description: Task description
            specialist_type: Type of specialist agent
            context: Task context
            priority: Task priority

        Returns:
            message_id for tracking
        """
        self.logger.info(f"Assigning task {task_id} to {specialist_type.value} agent")

        # Select best specialist agent using router
        if self.message_router:
            specialist_id = self.message_router.select_agent(
                agent_type=specialist_type.value,
                load_balance=True
            )
        else:
            # Fallback to default agent ID
            specialist_id = f"{specialist_type.value}-001"

        if not specialist_id:
            raise ValueError(f"No available {specialist_type.value} agent")

        # Track assignment
        self.assigned_tasks[task_id] = {
            "task_id": task_id,
            "description": task_description,
            "assigned_to": specialist_id,
            "specialist_type": specialist_type.value,
            "priority": priority,
            "status": "assigned",
            "assigned_at": datetime.now().isoformat()
        }

        # Delegate to specialist
        message_id = await self.delegate_task(
            recipient_id=specialist_id,
            recipient_type=specialist_type,
            task_description=task_description,
            context=context,
            priority=priority
        )

        # Update router load tracking
        if self.message_router:
            self.message_router.increment_agent_load(specialist_id)

        return message_id

    async def coordinate_execution(
        self,
        project_id: str,
        work_packages: List[Dict[str, Any]],
        context: TaskContext
    ) -> TaskResult:
        """
        Coordinate execution of multiple work packages

        Args:
            project_id: Project identifier
            work_packages: List of work packages to execute
            context: Task context

        Returns:
            TaskResult with coordination results
        """
        self.logger.info(f"Coordinating execution of {len(work_packages)} work packages")

        # Analyze work packages and determine agent assignments
        task_description = f"""Analyze work packages and create execution coordination plan:

Work Packages:
{json.dumps(work_packages, indent=2)}

For each work package, determine:
1. Required specialist agent(s)
2. Task breakdown and sequencing
3. Dependencies between tasks
4. Estimated effort and duration
5. Required MCP tools
6. Success criteria and validation method

Create coordination plan that includes:
- Task assignment matrix (task -> agent)
- Execution sequence (considering dependencies)
- Parallel execution opportunities
- Quality checkpoints
- Progress tracking approach
- Issue escalation triggers
"""

        result = await self.process_task(task_description, context)
        return result

    async def validate_deliverable(
        self,
        deliverable: Dict[str, Any],
        acceptance_criteria: List[str],
        validator_type: AgentType = AgentType.TYPESCRIPT_VALIDATOR
    ) -> Dict[str, Any]:
        """
        Validate deliverable against acceptance criteria

        Args:
            deliverable: Deliverable to validate
            acceptance_criteria: List of acceptance criteria
            validator_type: Type of validator agent to use

        Returns:
            Validation results
        """
        self.logger.info(f"Validating deliverable: {deliverable.get('name', 'unknown')}")

        context = TaskContext(
            project_id="validation",
            project_description="Deliverable validation",
            current_phase="execution"
        )

        task_description = f"""Validate deliverable against acceptance criteria:

Deliverable:
{json.dumps(deliverable, indent=2)}

Acceptance Criteria:
{json.dumps(acceptance_criteria, indent=2)}

Perform validation:
1. Check all acceptance criteria are met
2. Run automated tests (if code)
3. Verify documentation completeness
4. Check integration points
5. Validate against quality standards

Provide validation report with:
- Pass/Fail status
- Criteria met/not met
- Issues found
- Recommendations for improvement
"""

        # Use validator agent for validation
        if validator_type == AgentType.TYPESCRIPT_VALIDATOR:
            message_id = await self.assign_task_to_specialist(
                task_id=self._generate_id(),
                task_description=task_description,
                specialist_type=validator_type,
                context=context,
                priority="high"
            )

        # In real implementation, would wait for validator response
        # For now, return pending status
        return {
            "status": "pending",
            "validation_message_id": message_id if 'message_id' in locals() else None,
            "deliverable_name": deliverable.get("name", "unknown")
        }

    def update_task_status(self, task_id: str, status: str, progress: Optional[int] = None):
        """Update status of assigned task"""
        if task_id in self.assigned_tasks:
            self.assigned_tasks[task_id]["status"] = status
            self.assigned_tasks[task_id]["updated_at"] = datetime.now().isoformat()

            if progress is not None:
                self.assigned_tasks[task_id]["progress"] = progress

            self.logger.info(f"Updated task {task_id} status to {status}")

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of assigned task"""
        return self.assigned_tasks.get(task_id)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all assigned tasks"""
        return list(self.assigned_tasks.values())

    def register_specialist(self, agent_type: str, agent_id: str):
        """Register specialist agent with supervisor"""
        if agent_type not in self.specialist_agents:
            self.specialist_agents[agent_type] = []

        self.specialist_agents[agent_type].append(agent_id)
        self.logger.info(f"Registered {agent_type} specialist: {agent_id}")

    def get_available_specialists(self, agent_type: Optional[str] = None) -> Dict[str, List[str]]:
        """Get available specialist agents"""
        if agent_type:
            return {agent_type: self.specialist_agents.get(agent_type, [])}
        return self.specialist_agents
