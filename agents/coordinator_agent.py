"""
Coordinator Agent - Top-level orchestrator for PM-Agents system
Manages project lifecycle, phase gates, and agent delegation
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime

from .base_agent import (
    BaseAgent,
    AgentType,
    TaskContext,
    TaskResult,
    TaskStatus,
    AgentMessage
)


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent - Top level of hierarchy
    Responsibilities:
    - Project lifecycle management
    - Phase gate decision-making
    - Strategic resource allocation
    - High-level risk and issue escalation
    - Inter-phase coordination
    """

    def __init__(
        self,
        agent_id: str = "coordinator-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        state_manager: Optional[Any] = None
    ):
        """Initialize Coordinator Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COORDINATOR,
            api_key=api_key,
            message_bus=message_bus
        )

        self.state_manager = state_manager

        # MCP servers required by coordinator
        self.required_mcp_servers = [
            "filesystem",
            "github",
            "memory"
        ]

        # Project lifecycle tracking
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        self.phase_history: List[Dict[str, Any]] = []

        self.logger.info("Coordinator Agent initialized")

    def get_system_prompt(self) -> str:
        """Get coordinator-specific system prompt"""
        return """You are the Coordinator Agent, the top-level orchestrator in the PM-Agents multi-agent system.

Your responsibilities:
1. **Project Lifecycle Management**: Oversee entire project from initiation to closure
2. **Phase Gate Decision-Making**: Make GO/NO-GO decisions at critical phase transitions
3. **Strategic Planning**: Work with Planner Agent to define high-level strategy
4. **Resource Allocation**: Allocate agents and resources across project phases
5. **Risk Management**: Monitor and escalate critical risks that threaten project success
6. **Stakeholder Management**: Ensure stakeholder expectations are met

You follow PMI PMBOK 7th Edition principles and manage projects through five phases:
- Initiation
- Planning
- Execution
- Monitoring & Control
- Closure

Key behaviors:
- Delegate phase-specific work to Planner Agent
- Make data-driven decisions based on metrics and deliverables
- Escalate only the most critical issues
- Maintain big-picture view of project health
- Ensure quality gates are met before phase transitions

When analyzing requests:
- Identify project type (frontend, backend, ML/DL, analytics, fullstack)
- Determine required specialist agents
- Define success criteria and constraints
- Plan phase-by-phase execution strategy

Output format: Always provide structured JSON responses with:
- deliverables: List of concrete outputs
- risks_identified: Potential risks with mitigation strategies
- issues: Current blockers or problems
- next_steps: Clear action items
- phase_gate_recommendation: GO/CONDITIONAL_GO/NO_GO with rationale
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return coordinator capabilities"""
        return {
            "agent_type": "coordinator",
            "capabilities": [
                "project_lifecycle_management",
                "phase_gate_decisions",
                "strategic_planning",
                "resource_allocation",
                "risk_management",
                "stakeholder_management"
            ],
            "supported_project_types": [
                "frontend",
                "backend",
                "ml",
                "analytics",
                "fullstack",
                "research"
            ],
            "mcp_servers": self.required_mcp_servers
        }

    async def initiate_project(
        self,
        project_name: str,
        project_description: str,
        project_type: str,
        requirements: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate a new project

        Args:
            project_name: Project name
            project_description: Project description
            project_type: Type (frontend, backend, ml, analytics, fullstack)
            requirements: List of requirements
            constraints: Optional constraints (budget, timeline, etc.)

        Returns:
            Project initialization results
        """
        project_id = self._generate_id()

        self.logger.info(f"Initiating project {project_id}: {project_name}")

        # Create project entry
        if self.state_manager:
            project_id = self.state_manager.create_project(
                name=project_name,
                description=project_description,
                project_type=project_type,
                metadata={
                    "requirements": requirements,
                    "constraints": constraints or {}
                }
            )

        # Store in active projects
        self.active_projects[project_id] = {
            "project_id": project_id,
            "name": project_name,
            "description": project_description,
            "type": project_type,
            "status": "initiation",
            "current_phase": "initiation",
            "requirements": requirements,
            "constraints": constraints or {},
            "created_at": datetime.now().isoformat()
        }

        # Create task context
        context = TaskContext(
            project_id=project_id,
            project_description=project_description,
            current_phase="initiation",
            requirements=requirements,
            constraints=constraints or {}
        )

        # Execute initiation task
        task_description = f"""Analyze project and create initiation package for: {project_name}

Type: {project_type}
Description: {project_description}

Requirements:
{json.dumps(requirements, indent=2)}

Deliverables needed:
1. Feasibility assessment
2. High-level scope definition
3. Stakeholder identification
4. Initial risk assessment
5. Resource requirements estimate
6. Success criteria definition
7. Phase gate readiness evaluation

Provide comprehensive initiation analysis."""

        result = await self.process_task(task_description, context, project_id)

        # Store result
        self.active_projects[project_id]["initiation_result"] = result.to_dict()

        return {
            "project_id": project_id,
            "status": "initiated",
            "result": result.to_dict()
        }

    async def conduct_phase_gate(
        self,
        project_id: str,
        phase: str,
        phase_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Conduct phase gate review

        Args:
            project_id: Project identifier
            phase: Phase being reviewed
            phase_outputs: Outputs from the phase

        Returns:
            Phase gate decision with rationale
        """
        self.logger.info(f"Conducting phase gate review for {project_id} - {phase}")

        project = self.active_projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        context = TaskContext(
            project_id=project_id,
            project_description=project["description"],
            current_phase=phase,
            previous_outputs=phase_outputs
        )

        task_description = f"""Conduct Phase Gate Review for {phase.upper()} phase.

Project: {project['name']}
Type: {project['type']}

Phase Outputs:
{json.dumps(phase_outputs, indent=2)}

Evaluation Criteria:
1. **Completeness**: Are all required deliverables present and complete?
2. **Quality**: Do deliverables meet quality standards?
3. **Risks**: Are risks acceptable and properly mitigated?
4. **Issues**: Are critical issues resolved or have clear resolution plans?
5. **Readiness**: Is the project ready to proceed to the next phase?

Provide phase gate decision:
- GO: Proceed to next phase
- CONDITIONAL_GO: Proceed with conditions/mitigation actions
- NO_GO: Do not proceed, return to current phase

Include:
- Overall recommendation (GO/CONDITIONAL_GO/NO_GO)
- Detailed rationale
- Required actions if conditional
- Critical risks that must be addressed
- Confidence level (0-100)
"""

        result = await self.process_task(task_description, context)

        # Parse decision from result
        decision_info = {
            "project_id": project_id,
            "phase": phase,
            "decision": self._extract_decision(result),
            "rationale": result.deliverables,
            "risks": result.risks_identified,
            "required_actions": result.next_steps,
            "timestamp": datetime.now().isoformat()
        }

        # Record in history
        self.phase_history.append(decision_info)

        # Update project status
        if decision_info["decision"] == "GO":
            project["current_phase"] = self._get_next_phase(phase)
            project["status"] = decision_info["decision"]

        # Store in state manager
        if self.state_manager:
            gate_number = self._get_phase_gate_number(phase)
            self.state_manager.record_phase_gate(
                project_id=project_id,
                gate_number=gate_number,
                decision=decision_info["decision"],
                overall_score=85.0,  # Would extract from result in production
                criteria_scores={},
                critical_issues=[],
                required_actions=decision_info["required_actions"],
                reviewer_notes=json.dumps(decision_info["rationale"])
            )

        return decision_info

    def _extract_decision(self, result: TaskResult) -> str:
        """Extract phase gate decision from task result"""
        # Look for decision in deliverables
        for deliverable in result.deliverables:
            content = str(deliverable.get("content", "")).upper()
            if "NO-GO" in content or "NO_GO" in content:
                return "NO_GO"
            elif "CONDITIONAL_GO" in content or "CONDITIONAL GO" in content:
                return "CONDITIONAL_GO"
            elif "GO" in content:
                return "GO"

        # Default to conditional if unclear
        return "CONDITIONAL_GO"

    def _get_next_phase(self, current_phase: str) -> str:
        """Get next phase in project lifecycle"""
        phases = ["initiation", "planning", "execution", "monitoring", "closure"]
        try:
            current_index = phases.index(current_phase.lower())
            if current_index < len(phases) - 1:
                return phases[current_index + 1]
        except ValueError:
            pass
        return "closure"

    def _get_phase_gate_number(self, phase: str) -> int:
        """Get phase gate number (1-5)"""
        phases = ["initiation", "planning", "execution", "monitoring", "closure"]
        try:
            return phases.index(phase.lower()) + 1
        except ValueError:
            return 1

    async def delegate_to_planner(
        self,
        project_id: str,
        task_description: str,
        planner_id: str = "planner-001"
    ) -> str:
        """
        Delegate task to Planner Agent

        Returns:
            message_id for tracking
        """
        project = self.active_projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        context = TaskContext(
            project_id=project_id,
            project_description=project["description"],
            current_phase=project["current_phase"],
            requirements=project.get("requirements", []),
            constraints=project.get("constraints", {})
        )

        message_id = await self.delegate_task(
            recipient_id=planner_id,
            recipient_type=AgentType.PLANNER,
            task_description=task_description,
            context=context,
            priority="high"
        )

        return message_id

    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get current project status"""
        project = self.active_projects.get(project_id)
        if not project:
            return None

        return {
            "project_id": project_id,
            "name": project["name"],
            "type": project["type"],
            "current_phase": project["current_phase"],
            "status": project["status"],
            "created_at": project["created_at"],
            "phase_gates_passed": len([
                pg for pg in self.phase_history
                if pg["project_id"] == project_id and pg["decision"] == "GO"
            ])
        }

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all active projects"""
        return [
            self.get_project_status(pid)
            for pid in self.active_projects.keys()
        ]
