"""
Planner Agent - Strategic planning and work breakdown
Creates detailed project plans, schedules, and resource allocations
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


class PlannerAgent(BaseAgent):
    """
    Planner Agent - Strategic planning layer
    Responsibilities:
    - WBS (Work Breakdown Structure) creation
    - Schedule and timeline planning
    - Resource allocation planning
    - Risk planning and mitigation strategies
    - Quality planning and standards definition
    """

    def __init__(
        self,
        agent_id: str = "planner-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None
    ):
        """Initialize Planner Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.PLANNER,
            api_key=api_key,
            message_bus=message_bus
        )

        # MCP servers required
        self.required_mcp_servers = [
            "filesystem",
            "github",
            "memory"
        ]

        self.logger.info("Planner Agent initialized")

    def get_system_prompt(self) -> str:
        """Get planner-specific system prompt"""
        return """You are the Planner Agent in the PM-Agents hierarchical multi-agent system.

Your role is strategic planning and detailed work breakdown. You report to the Coordinator Agent
and delegate tactical execution to the Supervisor Agent.

Your responsibilities:
1. **Work Breakdown Structure (WBS)**: Decompose projects into manageable tasks and subtasks
2. **Schedule Planning**: Create realistic timelines with dependencies and critical paths
3. **Resource Planning**: Identify required agents, tools, and external resources
4. **Risk Planning**: Identify risks and develop mitigation strategies
5. **Quality Planning**: Define quality standards, acceptance criteria, and validation methods
6. **Communication Planning**: Define reporting structure and status update frequency

Planning Principles:
- **Decomposition**: Break complex projects into smaller, manageable units
- **Dependency Analysis**: Identify task dependencies and critical paths
- **Realistic Estimation**: Provide realistic time and effort estimates
- **Risk-Aware**: Consider and plan for potential risks
- **Iterative**: Support iterative and incremental development approaches

For different project types, apply specialized planning:

**Frontend Projects**:
- Component hierarchy planning
- State management architecture
- API integration points
- UI/UX implementation phases
- Testing strategy (unit, integration, e2e)

**Backend/API Projects**:
- API endpoint design and documentation
- Database schema planning
- Authentication/authorization strategy
- Performance and scalability planning
- Deployment strategy

**ML/DL Projects**:
- Data pipeline planning
- Model architecture selection
- Training strategy and hyperparameter planning
- Evaluation metrics definition
- Deployment and monitoring strategy

**Analytics Projects**:
- Data source identification
- Analysis methodology
- Visualization requirements
- Reporting format and frequency
- Statistical validation approach

**Research Projects**:
- Research questions and hypotheses
- Literature review strategy
- Experimental design
- Data collection methodology
- Analysis and documentation plan

Output format: Provide structured JSON with:
- deliverables: Detailed plans, WBS, schedules
- risks_identified: Potential planning risks
- issues: Planning constraints or blockers
- next_steps: Tasks to delegate to Supervisor
- required_agents: List of specialist agents needed
- dependencies: Task dependencies and critical path
- success_criteria: Clear definition of done
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return planner capabilities"""
        return {
            "agent_type": "planner",
            "capabilities": [
                "wbs_creation",
                "schedule_planning",
                "resource_planning",
                "risk_planning",
                "quality_planning",
                "dependency_analysis",
                "critical_path_identification"
            ],
            "supported_methodologies": [
                "waterfall",
                "agile",
                "iterative",
                "hybrid"
            ],
            "mcp_servers": self.required_mcp_servers
        }

    async def create_project_plan(
        self,
        project_id: str,
        project_description: str,
        project_type: str,
        requirements: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """
        Create comprehensive project plan

        Args:
            project_id: Project identifier
            project_description: Project description
            project_type: Type of project
            requirements: List of requirements
            constraints: Optional constraints

        Returns:
            TaskResult with project plan
        """
        self.logger.info(f"Creating project plan for {project_id}")

        context = TaskContext(
            project_id=project_id,
            project_description=project_description,
            current_phase="planning",
            requirements=requirements,
            constraints=constraints or {}
        )

        task_description = f"""Create comprehensive project plan for: {project_description}

Project Type: {project_type}

Requirements:
{json.dumps(requirements, indent=2)}

Constraints:
{json.dumps(constraints or {}, indent=2)}

Deliverables Required:

1. **Work Breakdown Structure (WBS)**
   - Level 1: Major phases
   - Level 2: Key deliverables per phase
   - Level 3: Specific tasks
   - Level 4: Subtasks (where applicable)

2. **Task Estimates**
   - Duration estimates for each task
   - Effort estimates (agent hours)
   - Complexity ratings

3. **Dependencies**
   - Task dependencies (predecessor/successor)
   - Critical path identification
   - Parallel work opportunities

4. **Resource Plan**
   - Specialist agents required per phase
   - External tools/services needed
   - MCP servers to be utilized

5. **Risk Management Plan**
   - Identified risks with probability and impact
   - Mitigation strategies
   - Contingency plans

6. **Quality Plan**
   - Quality standards and criteria
   - Testing strategy
   - Validation checkpoints

7. **Schedule**
   - High-level timeline
   - Milestone dates
   - Phase durations

8. **Success Criteria**
   - Definition of done for each phase
   - Acceptance criteria
   - Quality metrics

Provide detailed, actionable plan that can be executed by Supervisor and specialist agents.
"""

        result = await self.process_task(task_description, context)
        return result

    async def delegate_to_supervisor(
        self,
        project_id: str,
        task_description: str,
        context: TaskContext,
        supervisor_id: str = "supervisor-001"
    ) -> str:
        """
        Delegate execution task to Supervisor Agent

        Returns:
            message_id for tracking
        """
        message_id = await self.delegate_task(
            recipient_id=supervisor_id,
            recipient_type=AgentType.SUPERVISOR,
            task_description=task_description,
            context=context,
            priority="high"
        )

        self.logger.info(f"Delegated task to Supervisor: {message_id}")
        return message_id

    async def create_wbs(
        self,
        project_description: str,
        requirements: List[str],
        project_type: str
    ) -> Dict[str, Any]:
        """
        Create Work Breakdown Structure

        Returns:
            WBS as hierarchical dictionary
        """
        context = TaskContext(
            project_id="temp",
            project_description=project_description,
            current_phase="planning",
            requirements=requirements
        )

        task_description = f"""Create detailed Work Breakdown Structure (WBS) for {project_type} project:

{project_description}

Requirements:
{json.dumps(requirements, indent=2)}

Create hierarchical WBS with:
- Level 1: Project phases
- Level 2: Major deliverables
- Level 3: Work packages
- Level 4: Specific tasks

For each task, include:
- Task ID
- Task name
- Description
- Estimated duration
- Required specialist agent(s)
- Dependencies
- Acceptance criteria
"""

        result = await self.process_task(task_description, context)

        # Extract WBS from deliverables
        wbs = {}
        for deliverable in result.deliverables:
            if deliverable.get("type") == "document" and "wbs" in deliverable.get("name", "").lower():
                wbs = deliverable.get("content", {})
                break

        return wbs
