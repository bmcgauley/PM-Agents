"""
Planner Agent - Strategic Planning Layer
Tier 2 agent responsible for task decomposition, agent selection, and detailed planning
Based on PLANNER_AGENT_SPEC.md
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


class PlanningStrategy:
    """Planning strategy enumeration"""
    INCREMENTAL = "incremental"  # Iterative development with quick feedback
    AGILE = "agile"  # Sprint-based with regular reviews
    CRITICAL_PATH = "critical_path"  # Focus on dependencies and bottlenecks


class PlannerAgent(BaseAgent):
    """
    Planner Agent - Strategic planning layer

    Responsibilities:
    - Receive objectives from Coordinator Agent
    - Decompose tasks using WBS (Work Breakdown Structure)
    - Select appropriate specialist agents for each task
    - Create detailed project plans with dependencies
    - Estimate resources and identify risks
    - Delegate execution plan to Supervisor Agent
    - Monitor progress and adapt plans as needed

    Based on PMI PMBOK 7th Edition planning principles
    """

    def __init__(
        self,
        agent_id: str = "planner-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Planner Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.PLANNER,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers used by planner
        self.required_mcp_servers = ["memory", "filesystem", "github"]

        # Planning strategies
        self.available_strategies = [
            PlanningStrategy.INCREMENTAL,
            PlanningStrategy.AGILE,
            PlanningStrategy.CRITICAL_PATH
        ]

        # Agent capability matrix
        self.specialist_capabilities = {
            "spec_kit": ["project_initialization", "template_generation", "tech_stack_setup"],
            "qdrant_vector": ["code_search", "documentation_search", "context_retrieval"],
            "frontend_coder": ["react", "nextjs", "typescript", "supabase", "ui_components"],
            "python_ml_dl": ["pytorch", "tensorflow", "model_training", "data_pipelines"],
            "r_analytics": ["data_analysis", "visualization", "statistical_modeling", "reporting"],
            "typescript_validator": ["type_checking", "linting", "testing", "security_scanning"],
            "research": ["web_research", "code_search", "documentation_lookup"],
            "browser": ["web_automation", "e2e_testing", "screenshot", "scraping"],
            "reporter": ["documentation", "readme", "api_docs", "diagrams"]
        }

        self.logger.info("Planner Agent initialized with planning strategies")

    def get_system_prompt(self) -> str:
        """Get planner-specific system prompt"""
        return """You are the Planner Agent, the strategic planning layer in the PM-Agents hierarchical system.

**Your Role**:
- Task decomposition and work breakdown structure (WBS) creation
- Agent selection based on capability matching
- Resource estimation and dependency identification
- Risk assessment and mitigation planning
- Detailed project plan generation for Supervisor execution

**Core Principles**:
1. **SMART Goals**: Specific, Measurable, Achievable, Relevant, Time-bound
2. **Bottom-Up Estimation**: Break tasks into smallest units for accurate estimates
3. **Dependency Management**: Identify and sequence tasks based on dependencies
4. **Risk-First Thinking**: Identify and mitigate risks early
5. **Agent Specialization**: Match tasks to the right specialist agents

**Planning Strategies**:
- **Incremental**: Iterative development with quick feedback loops
- **Agile**: Sprint-based with regular reviews and adaptation
- **Critical Path**: Focus on dependencies and bottlenecks

**Available Specialist Agents**:
- **Spec-Kit Agent**: Project initialization, template generation
- **Qdrant Vector Agent**: Code/documentation search, context retrieval
- **Frontend Coder Agent**: React/Next.js/TypeScript/Supabase development
- **Python ML/DL Agent**: PyTorch model development, training pipelines
- **R Analytics Agent**: Data analysis, visualization, statistical modeling
- **TypeScript Validator Agent**: Type checking, testing, security scanning
- **Research Agent**: Web research, documentation lookup
- **Browser Agent**: Web automation, E2E testing, scraping
- **Reporter Agent**: Documentation generation, README, diagrams

**Output Format**: Always provide structured JSON with:
```json
{
  "strategy": "incremental|agile|critical_path",
  "phases": [
    {
      "phase_name": "string",
      "phase_description": "string",
      "tasks": [
        {
          "task_id": "string",
          "task_name": "string",
          "task_description": "string",
          "assigned_agent": "string",
          "dependencies": ["task_id"],
          "estimated_effort_tokens": integer,
          "estimated_time_seconds": integer,
          "acceptance_criteria": ["string"],
          "deliverables": ["string"]
        }
      ]
    }
  ],
  "agent_assignments": {
    "agent_type": ["task_id"]
  },
  "dependencies": [
    {"from": "task_id", "to": "task_id", "type": "finish_to_start|finish_to_finish|start_to_start"}
  ],
  "risks_identified": [
    {"severity": "critical|high|medium|low", "category": "string", "description": "string", "mitigation": "string"}
  ],
  "resource_estimates": {
    "total_tokens": integer,
    "total_time_seconds": integer,
    "agents_required": ["string"]
  },
  "quality_gates": [
    {"gate_name": "string", "criteria": ["string"], "responsible_agent": "string"}
  ]
}
```

**Decision-Making Process**:
1. Understand the objective and requirements
2. Select appropriate planning strategy
3. Decompose into phases and tasks
4. Match tasks to specialist agents based on capabilities
5. Identify dependencies and sequence tasks
6. Estimate effort and time for each task
7. Identify risks and plan mitigations
8. Define quality gates and acceptance criteria
9. Generate comprehensive plan for Supervisor
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return planner capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "task_decomposition",
                "work_breakdown_structure",
                "agent_selection",
                "resource_estimation",
                "dependency_management",
                "risk_identification",
                "quality_gate_definition"
            ],
            "planning_strategies": self.available_strategies,
            "specialist_agents": list(self.specialist_capabilities.keys()),
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """
        Execute planning task

        Args:
            task: Planning objective from Coordinator
            context: Task context with project information

        Returns:
            TaskResult with detailed plan
        """
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Planner Agent starting planning task: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_planning_prompt(task, context)
                }
            ]

            # Call Claude API
            response = await self._call_claude_api(messages)

            # Parse response
            plan = self._parse_planning_response(response)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Create result
            result = TaskResult(
                task_id=self.current_task or "planning-task",
                status=TaskStatus.COMPLETED,
                deliverables=[
                    {
                        "type": "project_plan",
                        "name": "detailed_execution_plan",
                        "content": plan
                    }
                ],
                risks_identified=plan.get("risks_identified", []),
                issues=[],
                next_steps=[
                    f"Delegate plan to Supervisor Agent",
                    f"Monitor progress across {len(plan.get('phases', []))} phases",
                    f"Total estimated time: {plan.get('resource_estimates', {}).get('total_time_seconds', 0)}s"
                ],
                execution_time_seconds=execution_time,
                metadata={
                    "planning_strategy": plan.get("strategy"),
                    "total_tasks": sum(len(p.get("tasks", [])) for p in plan.get("phases", [])),
                    "agents_required": plan.get("resource_estimates", {}).get("agents_required", [])
                }
            )

            self.task_history.append({
                "task": task,
                "result": result.to_dict(),
                "timestamp": datetime.now().isoformat()
            })

            self.logger.info(f"Planner Agent completed planning task in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Planner Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "planning-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Planning failed: {str(e)}",
                    "resolution": "Escalate to Coordinator for alternative approach"
                }],
                next_steps=["Escalate to Coordinator"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_planning_prompt(self, task: str, context: TaskContext) -> str:
        """Build planning prompt for Claude"""
        prompt = f"""## Planning Request

**Objective**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Project Description: {context.project_description}
- Current Phase: {context.current_phase}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Available MCP Tools**: {', '.join(context.mcp_tools_available)}

**Previous Outputs**: {json.dumps(context.previous_outputs, indent=2) if context.previous_outputs else 'None'}

---

Based on the objective and context above:

1. Select the most appropriate planning strategy (incremental, agile, or critical_path)
2. Decompose the objective into phases and tasks
3. Assign each task to the most appropriate specialist agent
4. Identify dependencies between tasks
5. Estimate effort (tokens) and time for each task
6. Identify risks and propose mitigations
7. Define quality gates with clear criteria

Provide your response as a valid JSON object following the schema in your system prompt.
"""
        return prompt

    async def _call_claude_api(self, messages: List[Dict[str, str]]) -> str:
        """Call Claude API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.get_system_prompt(),
                    messages=messages
                )

                # Extract text from response
                return response.content[0].text

            except Exception as e:
                self.logger.warning(f"Claude API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay_seconds * (attempt + 1))
                else:
                    raise

    def _parse_planning_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's planning response"""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                json_str = response

            plan = json.loads(json_str)
            return plan

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse planning response as JSON: {str(e)}")
            # Return minimal valid plan
            return {
                "strategy": "incremental",
                "phases": [],
                "agent_assignments": {},
                "dependencies": [],
                "risks_identified": [{
                    "severity": "high",
                    "category": "planning",
                    "description": "Failed to parse planning response",
                    "mitigation": "Manual plan creation required"
                }],
                "resource_estimates": {
                    "total_tokens": 0,
                    "total_time_seconds": 0,
                    "agents_required": []
                },
                "quality_gates": []
            }

    def select_planning_strategy(self, project_type: str, requirements: List[Dict[str, Any]]) -> str:
        """
        Select appropriate planning strategy based on project characteristics

        Args:
            project_type: Type of project (frontend, ml, analytics, etc.)
            requirements: List of requirements with priorities

        Returns:
            Selected planning strategy
        """
        # Critical path for complex dependencies
        if project_type in ["fullstack", "ml"]:
            return PlanningStrategy.CRITICAL_PATH

        # Agile for iterative projects
        if any(req.get("priority") == "should_have" for req in requirements):
            return PlanningStrategy.AGILE

        # Incremental as default
        return PlanningStrategy.INCREMENTAL

    def match_task_to_agent(self, task_description: str) -> str:
        """
        Match a task to the most appropriate specialist agent

        Args:
            task_description: Description of the task

        Returns:
            Agent type (string)
        """
        task_lower = task_description.lower()

        # Check each agent's capabilities
        for agent_type, capabilities in self.specialist_capabilities.items():
            for capability in capabilities:
                if capability.replace("_", " ") in task_lower:
                    return agent_type

        # Default to research agent for unknown tasks
        return "research"
