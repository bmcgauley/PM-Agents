"""
Coordinator Agent - Enhanced Implementation
Top-level orchestrator for PM-Agents hierarchical multi-agent system
Based on COORDINATOR_AGENT_SPEC.md
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
import logging

from src.core.base_agent import (
    BaseAgent,
    AgentType,
    TaskContext,
    TaskResult,
    TaskStatus,
    AgentMessage
)
from src.core.project_state import ProjectState
from src.core.decision_engine import DecisionEngine, Decision


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent - Top-level orchestrator

    Responsibilities:
    - Receive and interpret user requests
    - Strategic decision-making (accept/reject requests)
    - Delegate to Planner Agent
    - Monitor project progress across all phases
    - Conduct phase gate reviews (GO/NO-GO decisions)
    - Handle escalations from lower-tier agents
    - Report final results to user

    Based on PMI PMBOK 7th Edition principles
    """

    def __init__(
        self,
        agent_id: str = "coordinator-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Coordinator Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COORDINATOR,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # Decision engine for GO/NO-GO and request acceptance
        self.decision_engine = DecisionEngine()

        # Project state tracking
        self.active_projects: Dict[str, ProjectState] = {}

        # MCP servers used by coordinator (indirectly via delegation)
        self.required_mcp_servers = ["memory"]  # For state persistence

        self.logger.info("Coordinator Agent initialized with decision engine")

    def get_system_prompt(self) -> str:
        """Get coordinator-specific system prompt"""
        return """You are the Coordinator Agent, the top-level orchestrator in the PM-Agents hierarchical multi-agent system.

**Your Role**:
- Project lifecycle orchestration across all PMBOK phases (Initiation → Planning → Execution → Monitoring → Closure)
- Strategic decision-making at phase gates
- High-level resource allocation and risk management
- Delegation to Planner Agent for detailed planning
- Escalation handling for critical issues

**Core Principles**:
1. **Big Picture Focus**: Maintain strategic view, delegate tactical details
2. **Data-Driven Decisions**: Base GO/NO-GO decisions on metrics, deliverables, and quality standards
3. **Risk Management**: Proactively identify and escalate critical risks
4. **Clear Communication**: Provide structured, actionable responses

**Decision Framework**:
- **Request Acceptance**: Evaluate feasibility, safety, clarity before proceeding
- **Phase Gates**: Assess completeness, quality, risks before phase transition
- **Escalations**: Handle blockers, resource exhaustion, quality failures appropriately

**Output Format**: Always provide structured JSON with:
```json
{
  "deliverables": [{"type": "...", "name": "...", "content": "..."}],
  "risks_identified": [{"severity": "...", "category": "...", "description": "...", "mitigation": "..."}],
  "issues": [{"severity": "...", "description": "...", "resolution": "..."}],
  "next_steps": ["...", "..."],
  "phase_gate_recommendation": "GO|CONDITIONAL_GO|NO_GO",
  "rationale": "..."
}
```

**Project Types Supported**: frontend, backend, ml, analytics, fullstack, research

Delegate planning and execution to specialized agents. You orchestrate, others execute.
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return coordinator capabilities"""
        return {
            "agent_type": "coordinator",
            "tier": 1,
            "capabilities": [
                "project_lifecycle_management",
                "phase_gate_decisions",
                "strategic_planning_oversight",
                "resource_allocation",
                "risk_escalation",
                "stakeholder_communication",
                "request_acceptance_evaluation"
            ],
            "supported_project_types": DecisionEngine.SUPPORTED_TYPES,
            "pmbok_phases": ["initiation", "planning", "execution", "monitoring", "closure"],
            "mcp_servers": self.required_mcp_servers
        }

    async def process_user_request(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user request - main entry point

        Args:
            user_request: Natural language request from user
            context: Optional context (project_path, project_type, etc.)
            preferences: Optional preferences (model, max_budget_tokens, etc.)

        Returns:
            Response dictionary with decision and next steps
        """
        self.logger.info(f"Processing user request: {user_request[:100]}...")

        context = context or {}
        preferences = preferences or {
            "model": "claude",
            "max_budget_tokens": 50000,
            "max_time_seconds": 300
        }

        # Step 1: Decide whether to accept request
        decision_result = self.decision_engine.accept_request(
            user_request=user_request,
            context=context,
            preferences=preferences
        )

        self.logger.info(f"Request decision: {decision_result.decision.value} (confidence: {decision_result.confidence:.2f})")

        # Handle rejection or clarification
        if decision_result.decision == Decision.REJECT:
            return {
                "status": "rejected",
                "decision": "rejected",
                "message": decision_result.rationale,
                "required_actions": decision_result.required_actions,
                "metadata": decision_result.metadata
            }

        if decision_result.decision == Decision.CLARIFY:
            return {
                "status": "needs_clarification",
                "decision": "needs_clarification",
                "message": decision_result.rationale,
                "clarification_questions": decision_result.required_actions,
                "metadata": decision_result.metadata
            }

        # Step 2: Request accepted - initiate project
        project_id = self._generate_id()
        project_name = context.get("project_name", f"Project-{project_id[:8]}")
        project_type = decision_result.metadata.get("project_type", "unknown")

        # Create project state
        project_state = ProjectState(
            request_id=project_id,
            project_name=project_name,
            project_description=user_request,
            project_type=project_type,
            status="in_progress",
            phase="initiation",
            tokens_budget=preferences.get("max_budget_tokens", 50000)
        )

        self.active_projects[project_id] = project_state
        self.logger.info(f"Created project {project_id}: {project_name}")

        # Step 3: Begin initiation phase
        initiation_result = await self._execute_initiation_phase(
            project_id=project_id,
            user_request=user_request,
            context=context
        )

        # Step 4: Return response
        return {
            "status": "accepted",
            "decision": "approved",
            "project_id": project_id,
            "project_name": project_name,
            "project_type": project_type,
            "message": f"Project initiated successfully: {project_name}",
            "initiation_result": initiation_result,
            "next_steps": [
                "Review initiation deliverables",
                "Proceed to planning phase if initiation gate passes",
                "Coordinator will conduct phase gate review"
            ],
            "resource_usage": {
                "tokens_used": project_state.tokens_used,
                "tokens_remaining": project_state.tokens_remaining,
                "cost_usd": project_state.cost_usd
            }
        }

    async def _execute_initiation_phase(
        self,
        project_id: str,
        user_request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute project initiation phase"""
        project_state = self.active_projects[project_id]

        task_context = TaskContext(
            project_id=project_id,
            project_description=user_request,
            current_phase="initiation",
            requirements=context.get("requirements", []),
            constraints=context.get("constraints", {})
        )

        task_description = f"""Perform project initiation analysis for: {project_state.project_name}

**Project Type**: {project_state.project_type}
**Description**: {user_request}

**Required Deliverables**:
1. Feasibility Assessment: Technical and resource feasibility
2. Scope Definition: High-level scope boundaries
3. Stakeholder Identification: Key stakeholders and roles
4. Initial Risk Assessment: Top 5 risks with severity
5. Resource Requirements: Estimated resources needed
6. Success Criteria: Measurable success indicators
7. Phase Gate Readiness: Readiness for planning phase

Provide comprehensive analysis in JSON format."""

        result = await self.process_task(task_description, task_context, project_id)

        # Update project state with initiation outputs
        project_state.add_phase_output("initiation", {
            "task_id": result.task_id,
            "deliverables": result.deliverables,
            "risks": result.risks_identified,
            "issues": result.issues
        })

        # Track token usage
        tokens_used = result.metadata.get("tokens_used", 0)
        project_state.update_token_usage(tokens_used, tokens_used * 0.00003)

        return result.to_dict()

    async def conduct_phase_gate_review(
        self,
        project_id: str,
        phase: str
    ) -> Dict[str, Any]:
        """
        Conduct phase gate review

        Args:
            project_id: Project identifier
            phase: Phase being reviewed

        Returns:
            Phase gate decision with rationale
        """
        self.logger.info(f"Conducting phase gate review: {project_id} - {phase}")

        project_state = self.active_projects.get(project_id)
        if not project_state:
            raise ValueError(f"Project {project_id} not found")

        # Get phase outputs
        phase_outputs = {
            "deliverables": project_state.phase_outputs.get(phase, []),
            "risks": project_state.risks,
            "issues": project_state.issues
        }

        # Use decision engine
        decision_result = self.decision_engine.phase_gate_decision(
            phase=phase,
            phase_outputs=phase_outputs,
            project_state=project_state.to_dict()
        )

        self.logger.info(
            f"Phase gate decision: {decision_result.decision.value} "
            f"(score: {decision_result.metadata.get('score', 0):.1f}, "
            f"confidence: {decision_result.confidence:.2f})"
        )

        # Record decision in project state
        score = decision_result.metadata.get("score", 0)
        project_state.record_phase_gate_decision(
            phase=phase,
            decision=decision_result.decision.value,
            score=score,
            notes=decision_result.rationale
        )

        return {
            "project_id": project_id,
            "phase": phase,
            "decision": decision_result.decision.value,
            "score": score,
            "confidence": decision_result.confidence,
            "rationale": decision_result.rationale,
            "required_actions": decision_result.required_actions,
            "issues_found": decision_result.metadata.get("issues", []),
            "timestamp": datetime.now().isoformat()
        }

    async def delegate_to_planner(
        self,
        project_id: str,
        task_description: str,
        planner_id: str = "planner-001"
    ) -> str:
        """
        Delegate task to Planner Agent

        Args:
            project_id: Project identifier
            task_description: Task description for planner
            planner_id: Planner agent ID

        Returns:
            message_id for tracking
        """
        project_state = self.active_projects.get(project_id)
        if not project_state:
            raise ValueError(f"Project {project_id} not found")

        context = TaskContext(
            project_id=project_id,
            project_description=project_state.project_description,
            current_phase=project_state.phase,
            requirements=[],
            constraints={}
        )

        message_id = await self.delegate_task(
            recipient_id=planner_id,
            recipient_type=AgentType.PLANNER,
            task_description=task_description,
            context=context,
            priority="high"
        )

        self.logger.info(f"Delegated to Planner: {message_id}")
        return message_id

    def handle_escalation(self, escalation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle escalation from lower-tier agents"""
        self.logger.warning(f"Handling escalation: {escalation.get('type')} - {escalation.get('severity')}")

        response = self.decision_engine.handle_escalation(escalation)

        self.logger.info(f"Escalation response: {response.get('action')}")
        return response

    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get current project status"""
        project_state = self.active_projects.get(project_id)
        if not project_state:
            return None

        return {
            **project_state.get_summary(),
            "is_healthy": project_state.is_healthy(),
            "phase_completions": {
                phase: project_state.get_phase_completion(phase)
                for phase in ["initiation", "planning", "execution", "monitoring", "closure"]
            }
        }

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all active projects"""
        return [
            self.get_project_status(project_id)
            for project_id in self.active_projects.keys()
        ]

    def save_project_state(self, project_id: str, path: str):
        """Save project state to disk"""
        project_state = self.active_projects.get(project_id)
        if project_state:
            project_state.save(path)
            self.logger.info(f"Saved project state: {path}")

    def load_project_state(self, path: str) -> str:
        """Load project state from disk"""
        project_state = ProjectState.load(path)
        self.active_projects[project_state.request_id] = project_state
        self.logger.info(f"Loaded project state: {project_state.request_id}")
        return project_state.request_id
