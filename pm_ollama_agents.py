"""
PM-Agents Multi-Agent System - Ollama Implementation
Hierarchical agent system using local Ollama models (Gemma2/Gemma3)
Matches Anthropic implementation architecture with local inference
"""

import requests
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ============================================================================
# Core Data Structures (matching Anthropic implementation)
# ============================================================================

class AgentType(Enum):
    """Agent type enumeration"""
    COORDINATOR = "coordinator"
    PLANNER = "planner"
    SUPERVISOR = "supervisor"
    SPEC_KIT = "spec_kit"
    QDRANT_VECTOR = "qdrant_vector"
    FRONTEND_CODER = "frontend_coder"
    PYTHON_ML_DL = "python_ml_dl"
    R_ANALYTICS = "r_analytics"
    TYPESCRIPT_VALIDATOR = "typescript_validator"
    RESEARCH = "research"
    BROWSER = "browser"
    REPORTER = "reporter"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskContext:
    """Context information for task execution"""
    project_id: str
    project_description: str
    current_phase: str
    previous_outputs: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    mcp_tools_available: List[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of task execution"""
    task_id: str
    status: TaskStatus
    deliverables: List[Dict[str, Any]]
    risks_identified: List[Dict[str, Any]]
    issues: List[Dict[str, Any]]
    next_steps: List[str]
    execution_time_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "deliverables": self.deliverables,
            "risks_identified": self.risks_identified,
            "issues": self.issues,
            "next_steps": self.next_steps,
            "execution_time_seconds": self.execution_time_seconds,
            "metadata": self.metadata
        }


@dataclass
class ProjectState:
    """Project state tracking"""
    project_id: str
    project_name: str
    project_type: str
    current_phase: str
    status: str
    phase_outputs: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    go_decisions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    completed_phases: List[str] = field(default_factory=list)
    total_tokens_used: int = 0
    total_execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Base Agent Class (Ollama Implementation)
# ============================================================================

class OllamaBaseAgent:
    """
    Base agent class for Ollama-based agents
    Provides core functionality matching Anthropic BaseAgent interface
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        ollama_url: str = "http://localhost:11434",
        model: str = "gemma2:latest",
        temperature: float = 0.7,
        num_gpu: int = -1,  # -1 = auto, 0 = CPU only, >0 = specific GPU layers
        quantization: Optional[str] = None,  # Q4_0, Q4_1, Q5_0, Q5_1, Q8_0, F16, F32
        logger: Optional[logging.Logger] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.ollama_url = ollama_url
        self.model = model
        self.temperature = temperature
        self.num_gpu = num_gpu
        self.quantization = quantization
        self.logger = logger or logging.getLogger(f"OllamaAgent.{agent_id}")

        # Circuit breaker for error handling
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_open = False

        # Performance tracking
        self.total_calls = 0
        self.total_failures = 0
        self.total_execution_time = 0.0

        # Log GPU and quantization settings
        if num_gpu == -1:
            self.logger.info(f"GPU acceleration: AUTO (Ollama will use GPU if available)")
        elif num_gpu == 0:
            self.logger.info(f"GPU acceleration: DISABLED (CPU only)")
        else:
            self.logger.info(f"GPU acceleration: ENABLED ({num_gpu} layers on GPU)")

        if quantization:
            self.logger.info(f"Model quantization: {quantization}")

    def _generate_id(self) -> str:
        """Generate unique message/task ID"""
        import uuid
        return f"{self.agent_type.value}-{uuid.uuid4().hex[:8]}"

    async def call_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call Ollama API for inference

        Args:
            prompt: User prompt
            system_prompt: System instructions
            options: Model options (temperature, top_p, etc.)

        Returns:
            Model response text
        """
        if self.circuit_breaker_open:
            raise Exception("Circuit breaker is open - too many failures")

        url = f"{self.ollama_url}/api/generate"

        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser Request:\n{prompt}"

        # Default options
        default_options = {
            "temperature": self.temperature,
            "top_p": 0.9,
            "num_ctx": 4096  # Context window
        }

        # Add GPU configuration if specified
        if self.num_gpu >= 0:
            default_options["num_gpu"] = self.num_gpu

        # Note: Quantization is applied when pulling the model, not at inference time
        # To use quantized model: `ollama pull gemma2:Q4_0` or similar

        if options:
            default_options.update(options)

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": default_options
        }

        try:
            self.total_calls += 1
            start_time = datetime.now()

            # Use asyncio for async HTTP request
            response = await asyncio.to_thread(requests.post, url, json=payload)
            response.raise_for_status()

            result = response.json()
            response_text = result.get("response", "")

            execution_time = (datetime.now() - start_time).total_seconds()
            self.total_execution_time += execution_time

            # Reset circuit breaker on success
            self.circuit_breaker_failures = 0

            self.logger.debug(f"Ollama call successful: {len(response_text)} chars in {execution_time:.2f}s")

            return response_text

        except Exception as e:
            self.total_failures += 1
            self.circuit_breaker_failures += 1

            if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
                self.circuit_breaker_open = True
                self.logger.error(f"Circuit breaker opened after {self.circuit_breaker_failures} failures")

            self.logger.error(f"Ollama API error: {str(e)}")
            raise

    async def process_task(
        self,
        task_description: str,
        context: TaskContext,
        message_id: Optional[str] = None
    ) -> TaskResult:
        """
        Process a task (main entry point for agent execution)

        Args:
            task_description: Task to execute
            context: Execution context
            message_id: Optional message ID for correlation

        Returns:
            Task execution result
        """
        task_id = message_id or self._generate_id()
        start_time = datetime.now()

        self.logger.info(f"Processing task {task_id}: {task_description[:100]}...")

        try:
            # Execute agent-specific logic
            result = await self._execute(task_description, context)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Ensure result is a TaskResult
            if isinstance(result, TaskResult):
                result.execution_time_seconds = execution_time
                return result

            # If result is a dict, convert to TaskResult
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                deliverables=result.get("deliverables", []),
                risks_identified=result.get("risks_identified", []),
                issues=result.get("issues", []),
                next_steps=result.get("next_steps", []),
                execution_time_seconds=execution_time,
                metadata=result.get("metadata", {})
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Task {task_id} failed: {str(e)}")

            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "type": "execution_error",
                    "severity": "high",
                    "description": str(e),
                    "timestamp": datetime.now().isoformat()
                }],
                next_steps=["Investigate error", "Retry task"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    async def _execute(self, task_description: str, context: TaskContext) -> Dict[str, Any]:
        """
        Execute agent-specific logic (override in subclasses)

        Args:
            task_description: Task to execute
            context: Execution context

        Returns:
            Execution results
        """
        system_prompt = self.get_system_prompt()

        prompt = f"""Task: {task_description}

Project Context:
- Project ID: {context.project_id}
- Description: {context.project_description}
- Phase: {context.current_phase}
- Requirements: {', '.join(context.requirements) if context.requirements else 'None'}
- Constraints: {json.dumps(context.constraints) if context.constraints else 'None'}

Previous Outputs:
{json.dumps(context.previous_outputs, indent=2) if context.previous_outputs else 'None'}

Please complete this task and provide your response in the following JSON format:
{{
    "deliverables": [
        {{"name": "deliverable name", "type": "document|code|config", "description": "what was delivered"}}
    ],
    "risks_identified": [
        {{"type": "technical|resource|schedule", "severity": "high|medium|low", "description": "risk description", "mitigation": "mitigation strategy"}}
    ],
    "issues": [
        {{"type": "blocker|error|warning", "severity": "high|medium|low", "description": "issue description"}}
    ],
    "next_steps": ["step 1", "step 2", "..."]
}}

Respond ONLY with valid JSON. No markdown formatting, no extra text.
"""

        response = await self.call_ollama(prompt, system_prompt)

        # Parse JSON response
        try:
            # Clean response (remove markdown code blocks if present)
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            result = json.loads(response_clean)
            return result

        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {str(e)}")
            # Return structured result anyway
            return {
                "deliverables": [{
                    "name": "response",
                    "type": "document",
                    "description": response[:200]
                }],
                "risks_identified": [],
                "issues": [{
                    "type": "warning",
                    "severity": "low",
                    "description": "Could not parse structured output"
                }],
                "next_steps": ["Review response manually"]
            }

    def get_system_prompt(self) -> str:
        """Get agent-specific system prompt (override in subclasses)"""
        return f"You are a {self.agent_type.value} agent in a project management system."

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities (override in subclasses)"""
        return {
            "agent_type": self.agent_type.value,
            "capabilities": [],
            "mcp_tools": [],
            "mcp_servers": []
        }

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_execution_time": self.total_execution_time,
            "circuit_breaker_open": self.circuit_breaker_open,
            "model": self.model
        }


# ============================================================================
# TIER 1: COORDINATOR AGENT
# ============================================================================

class OllamaCoordinatorAgent(OllamaBaseAgent):
    """
    Coordinator Agent - Top-level orchestration
    Manages project lifecycle and phase gates
    """

    def __init__(
        self,
        agent_id: str = "coordinator-ollama-001",
        ollama_url: str = "http://localhost:11434",
        model: str = "gemma2:latest",
        num_gpu: int = -1,
        quantization: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COORDINATOR,
            ollama_url=ollama_url,
            model=model,
            num_gpu=num_gpu,
            quantization=quantization,
            logger=logger
        )

    def get_system_prompt(self) -> str:
        return """You are the COORDINATOR AGENT - the top-level orchestrator in a hierarchical multi-agent project management system.

Your role and responsibilities:
1. **Project Initiation**: Accept project requests, validate feasibility, create project state
2. **Strategic Oversight**: Make high-level decisions about project direction
3. **Phase Gate Management**: Conduct GO/NO-GO reviews between phases
4. **Delegation**: Delegate strategic planning to Planner Agent
5. **Risk Management**: Monitor project-level risks and make mitigation decisions
6. **Stakeholder Communication**: Report project status to stakeholders

You delegate to:
- Planner Agent (for strategic planning and WBS creation)

Key responsibilities:
- Ensure projects align with objectives
- Make GO/NO-GO decisions at phase gates
- Handle critical escalations from lower tiers
- Track overall project health and metrics

Always make decisions based on:
- Project objectives and success criteria
- Risk assessment and mitigation strategies
- Resource availability and constraints
- Quality standards and acceptance criteria

Provide structured, actionable outputs with clear decisions and rationale.
"""

    async def initiate_project(
        self,
        project_name: str,
        project_description: str,
        project_type: str,
        requirements: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Initiate a new project"""
        project_id = self._generate_id()

        prompt = f"""Initiate a new project with the following details:

Project Name: {project_name}
Project Type: {project_type}
Description: {project_description}

Requirements:
{chr(10).join(f'- {req}' for req in requirements)}

Constraints:
{json.dumps(constraints or {}, indent=2)}

Conduct project initiation including:
1. Feasibility assessment
2. High-level scope definition
3. Key stakeholder identification
4. Initial risk assessment
5. Success criteria definition

Provide response in JSON format with:
- feasibility_score (0-100)
- scope_summary
- key_stakeholders
- critical_risks
- success_criteria
- recommendation (GO/NO-GO)
"""

        response = await self.call_ollama(prompt, self.get_system_prompt())

        return {
            "project_id": project_id,
            "project_name": project_name,
            "project_type": project_type,
            "initiation_timestamp": datetime.now().isoformat(),
            "result": response
        }

    async def conduct_phase_gate(
        self,
        project_id: str,
        phase: str,
        phase_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Conduct phase gate review"""
        prompt = f"""Conduct a PHASE GATE REVIEW for the {phase.upper()} phase.

Project ID: {project_id}

Phase Outputs:
{json.dumps(phase_outputs, indent=2)}

Review Criteria:
1. Completeness: Are all required deliverables present?
2. Quality: Do deliverables meet quality standards?
3. Risks: Are risks manageable for next phase?
4. Resources: Are resources adequate to proceed?

Provide decision in JSON format:
{{
    "decision": "GO|CONDITIONAL_GO|NO_GO",
    "score": 0-100,
    "rationale": "brief explanation",
    "conditions": ["condition 1 if CONDITIONAL_GO"],
    "required_actions": ["action 1", "action 2"]
}}
"""

        response = await self.call_ollama(prompt, self.get_system_prompt())

        try:
            decision_data = json.loads(response.strip().replace("```json", "").replace("```", "").strip())
            return decision_data
        except:
            # Parse manually if JSON parsing fails
            is_go = "GO" in response.upper() and "NO-GO" not in response.upper() and "NO_GO" not in response.upper()
            return {
                "decision": "GO" if is_go else "NO_GO",
                "score": 75 if is_go else 50,
                "rationale": response[:200],
                "conditions": [],
                "required_actions": []
            }


# ============================================================================
# TIER 2: PLANNER AGENT
# ============================================================================

class OllamaPlannerAgent(OllamaBaseAgent):
    """
    Planner Agent - Strategic planning and task decomposition
    Creates Work Breakdown Structure (WBS) and project plans
    """

    def __init__(
        self,
        agent_id: str = "planner-ollama-001",
        ollama_url: str = "http://localhost:11434",
        model: str = "gemma2:latest",
        num_gpu: int = -1,
        quantization: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.PLANNER,
            ollama_url=ollama_url,
            model=model,
            num_gpu=num_gpu,
            quantization=quantization,
            logger=logger
        )

    def get_system_prompt(self) -> str:
        return """You are the PLANNER AGENT - responsible for strategic planning and task decomposition.

Your role and responsibilities:
1. **Work Breakdown Structure (WBS)**: Decompose projects into manageable work packages
2. **Task Decomposition**: Break down high-level goals into specific tasks
3. **Agent Selection**: Determine which specialist agents are needed
4. **Dependency Management**: Identify task dependencies and sequencing
5. **Resource Estimation**: Estimate effort and resources required
6. **Risk Planning**: Identify planning-phase risks

You work with:
- Coordinator Agent (receives strategic direction)
- Supervisor Agent (delegates tactical execution)

Planning Strategies:
1. **Incremental**: Sequential phases with clear milestones
2. **Agile**: Iterative sprints with continuous delivery
3. **Critical Path**: Focus on dependencies and bottlenecks

For each project, create:
- Detailed WBS with work packages
- Task list with dependencies
- Agent assignment strategy
- Timeline with milestones
- Risk register

Provide structured, implementable plans that can be executed by the Supervisor Agent.
"""

    async def create_project_plan(
        self,
        project_id: str,
        project_description: str,
        project_type: str,
        requirements: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Create comprehensive project plan"""
        context = TaskContext(
            project_id=project_id,
            project_description=project_description,
            current_phase="planning",
            requirements=requirements,
            constraints=constraints or {}
        )

        task_description = f"""Create a comprehensive project plan for:

Project Type: {project_type}
Description: {project_description}

Requirements:
{chr(10).join(f'- {req}' for req in requirements)}

Create:
1. Work Breakdown Structure (WBS)
2. Task list with dependencies
3. Agent assignment strategy (which specialists to use)
4. Timeline with milestones
5. Risk register

Consider available specialist agents:
- Spec-Kit Agent (project initialization)
- Qdrant Vector Agent (codebase search)
- Frontend Coder Agent (React/Next.js/TypeScript)
- Python ML/DL Agent (PyTorch/TensorBoard)
- R Analytics Agent (tidyverse/ggplot2)
- TypeScript Validator Agent (quality gates)
- Research Agent (technical research)
- Browser Agent (E2E testing)
- Reporter Agent (documentation)
"""

        result = await self.process_task(task_description, context)
        return result


# ============================================================================
# TIER 3: SUPERVISOR AGENT
# ============================================================================

class OllamaSupervisorAgent(OllamaBaseAgent):
    """
    Supervisor Agent - Tactical management and specialist coordination
    Assigns tasks to specialist agents and monitors execution
    """

    def __init__(
        self,
        agent_id: str = "supervisor-ollama-001",
        ollama_url: str = "http://localhost:11434",
        model: str = "gemma2:latest",
        num_gpu: int = -1,
        quantization: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.SUPERVISOR,
            ollama_url=ollama_url,
            model=model,
            num_gpu=num_gpu,
            quantization=quantization,
            logger=logger
        )
        self.specialists: Dict[str, OllamaBaseAgent] = {}

    def get_system_prompt(self) -> str:
        return """You are the SUPERVISOR AGENT - responsible for tactical management and specialist coordination.

Your role and responsibilities:
1. **Task Assignment**: Assign work packages to appropriate specialist agents
2. **Progress Monitoring**: Track specialist agent execution
3. **Result Aggregation**: Combine outputs from multiple specialists
4. **Quality Validation**: Ensure deliverables meet quality standards
5. **Coordination**: Manage dependencies between specialist tasks
6. **Escalation**: Escalate blockers to Planner/Coordinator

You manage specialist agents:
- Spec-Kit Agent (project initialization)
- Qdrant Vector Agent (semantic search)
- Frontend Coder Agent (UI development)
- Python ML/DL Agent (ML model development)
- R Analytics Agent (data analysis)
- TypeScript Validator Agent (quality gates)
- Research Agent (technical research)
- Browser Agent (testing/automation)
- Reporter Agent (documentation)

For each work package:
1. Select appropriate specialist agent(s)
2. Prepare task context with necessary information
3. Monitor execution and progress
4. Validate outputs against acceptance criteria
5. Aggregate results for upward reporting

Handle issues:
- If specialist fails: Retry or escalate
- If blocker encountered: Escalate to Planner
- If quality issues: Request rework

Provide structured coordination and clear status updates.
"""

    def register_specialist(self, agent_type: str, agent: OllamaBaseAgent):
        """Register a specialist agent"""
        self.specialists[agent_type] = agent
        self.logger.info(f"Registered specialist: {agent_type}")

    async def coordinate_execution(
        self,
        project_id: str,
        work_packages: List[Dict[str, Any]],
        context: TaskContext
    ) -> TaskResult:
        """Coordinate execution of work packages across specialist agents"""
        task_description = f"""Coordinate execution of {len(work_packages)} work packages:

{json.dumps(work_packages, indent=2)}

Available specialists:
{', '.join(self.specialists.keys())}

For each work package:
1. Select appropriate specialist agent
2. Prepare detailed task assignment
3. Monitor execution
4. Validate outputs
5. Report results

Manage dependencies and sequencing appropriately.
"""

        result = await self.process_task(task_description, context)
        return result


# ============================================================================
# Helper function to create specialist agents
# ============================================================================

def create_ollama_specialist_agent(
    agent_type: AgentType,
    ollama_url: str = "http://localhost:11434",
    model: str = "gemma2:latest",
    num_gpu: int = -1,
    quantization: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> OllamaBaseAgent:
    """
    Create a specialist agent of the specified type

    Args:
        agent_type: Type of specialist agent
        ollama_url: Ollama API URL
        model: Ollama model to use
        num_gpu: GPU layers configuration
        quantization: Model quantization
        logger: Optional logger

    Returns:
        Specialist agent instance
    """
    agent_id = f"{agent_type.value}-ollama-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # For now, create generic specialist agent
    # In future iterations, each specialist can have its own class
    agent = OllamaBaseAgent(
        agent_id=agent_id,
        agent_type=agent_type,
        ollama_url=ollama_url,
        model=model,
        num_gpu=num_gpu,
        quantization=quantization,
        logger=logger
    )

    return agent


# ============================================================================
# Ollama PM-Agents System
# ============================================================================

class OllamaPMAgentsSystem:
    """
    Complete PM-Agents system using Ollama for local inference
    Matches PMAgentsSystem interface from Anthropic implementation
    """

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "gemma2:latest",
        num_gpu: int = -1,
        quantization: Optional[str] = None,
        log_level: str = "INFO"
    ):
        """
        Initialize Ollama PM-Agents system

        Args:
            ollama_url: Ollama API URL
            model: Ollama model (gemma2:latest, gemma3, etc.)
            num_gpu: GPU layers (-1=auto, 0=CPU only, >0=specific layers)
            quantization: Model quantization (Q4_0, Q4_1, Q5_0, Q5_1, Q8_0, F16, F32)
            log_level: Logging level
        """
        self.ollama_url = ollama_url
        self.model = model
        self.num_gpu = num_gpu
        self.quantization = quantization
        self.logger = self._setup_logging(log_level)

        # Verify Ollama is running
        self._verify_ollama()

        # Initialize hierarchy agents
        self.logger.info("Initializing hierarchy agents...")

        self.coordinator = OllamaCoordinatorAgent(
            ollama_url=ollama_url,
            model=model,
            num_gpu=num_gpu,
            quantization=quantization,
            logger=self.logger
        )

        self.planner = OllamaPlannerAgent(
            ollama_url=ollama_url,
            model=model,
            num_gpu=num_gpu,
            quantization=quantization,
            logger=self.logger
        )

        self.supervisor = OllamaSupervisorAgent(
            ollama_url=ollama_url,
            model=model,
            num_gpu=num_gpu,
            quantization=quantization,
            logger=self.logger
        )

        # Initialize specialist agents
        self.logger.info("Initializing specialist agents...")
        self.specialists: Dict[str, OllamaBaseAgent] = {}

        specialist_types = [
            AgentType.SPEC_KIT,
            AgentType.QDRANT_VECTOR,
            AgentType.FRONTEND_CODER,
            AgentType.PYTHON_ML_DL,
            AgentType.R_ANALYTICS,
            AgentType.TYPESCRIPT_VALIDATOR,
            AgentType.RESEARCH,
            AgentType.BROWSER,
            AgentType.REPORTER
        ]

        for agent_type in specialist_types:
            agent = create_ollama_specialist_agent(
                agent_type=agent_type,
                ollama_url=ollama_url,
                model=model,
                num_gpu=num_gpu,
                quantization=quantization,
                logger=self.logger
            )
            self.specialists[agent_type.value] = agent
            self.supervisor.register_specialist(agent_type.value, agent)

        self.logger.info("Ollama PM-Agents system initialized successfully")

    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup system-wide logging"""
        logger = logging.getLogger("OllamaPMAgentsSystem")
        logger.setLevel(getattr(logging, log_level.upper()))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _verify_ollama(self):
        """Verify Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            response.raise_for_status()

            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]

            if self.model not in model_names:
                self.logger.warning(f"Model {self.model} not found. Available: {model_names}")
                self.logger.warning(f"Please run: ollama pull {self.model}")

            self.logger.info(f"✓ Ollama is running with {len(models)} models available")

        except Exception as e:
            raise Exception(f"Ollama is not running or not accessible: {str(e)}\n"
                          f"Please start Ollama: 'ollama serve'")

    async def run_project(
        self,
        project_name: str,
        project_description: str,
        project_type: str,
        requirements: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a complete project through the system

        Args:
            project_name: Project name
            project_description: Project description
            project_type: Type (frontend, backend, ml, analytics, fullstack)
            requirements: List of requirements
            constraints: Optional constraints

        Returns:
            Project execution results
        """
        self.logger.info(f"Starting project: {project_name}")

        # Phase 1: Initiation
        self.logger.info("Phase 1: Initiation")
        initiation_result = await self.coordinator.initiate_project(
            project_name=project_name,
            project_description=project_description,
            project_type=project_type,
            requirements=requirements,
            constraints=constraints
        )

        project_id = initiation_result["project_id"]

        # Conduct phase gate 1
        gate_1 = await self.coordinator.conduct_phase_gate(
            project_id=project_id,
            phase="initiation",
            phase_outputs=initiation_result
        )

        if gate_1.get("decision") not in ["GO", "CONDITIONAL_GO"]:
            return {
                "status": "halted",
                "phase": "initiation",
                "gate_decision": gate_1,
                "result": initiation_result
            }

        # Phase 2: Planning
        self.logger.info("Phase 2: Planning")
        planning_result = await self.planner.create_project_plan(
            project_id=project_id,
            project_description=project_description,
            project_type=project_type,
            requirements=requirements,
            constraints=constraints
        )

        # Conduct phase gate 2
        gate_2 = await self.coordinator.conduct_phase_gate(
            project_id=project_id,
            phase="planning",
            phase_outputs=planning_result.to_dict()
        )

        if gate_2.get("decision") not in ["GO", "CONDITIONAL_GO"]:
            return {
                "status": "halted",
                "phase": "planning",
                "gate_decision": gate_2,
                "initiation": initiation_result,
                "planning": planning_result.to_dict()
            }

        # Phase 3: Execution (simplified for now)
        self.logger.info("Phase 3: Execution")

        work_packages = [{
            "name": "Implementation",
            "description": project_description
        }]

        context = TaskContext(
            project_id=project_id,
            project_description=project_description,
            current_phase="execution",
            requirements=requirements,
            constraints=constraints or {}
        )

        execution_result = await self.supervisor.coordinate_execution(
            project_id=project_id,
            work_packages=work_packages,
            context=context
        )

        return {
            "status": "completed",
            "project_id": project_id,
            "phases": {
                "initiation": initiation_result,
                "planning": planning_result.to_dict(),
                "execution": execution_result.to_dict()
            },
            "phase_gates": {
                "gate_1": gate_1,
                "gate_2": gate_2
            }
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "coordinator": self.coordinator.get_status(),
            "planner": self.planner.get_status(),
            "supervisor": self.supervisor.get_status(),
            "specialists": {
                agent_type: agent.get_status()
                for agent_type, agent in self.specialists.items()
            },
            "ollama_url": self.ollama_url,
            "model": self.model
        }


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Main entry point for CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="PM-Agents Multi-Agent System (Ollama)")
    parser.add_argument("--project-name", required=True, help="Project name")
    parser.add_argument("--project-description", required=True, help="Project description")
    parser.add_argument("--project-type", required=True,
                        choices=["frontend", "backend", "ml", "analytics", "fullstack"],
                        help="Project type")
    parser.add_argument("--requirements", nargs="+", required=True, help="Project requirements")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--model", default="gemma2:latest", help="Ollama model")
    parser.add_argument("--num-gpu", type=int, default=-1,
                        help="GPU layers (-1=auto, 0=CPU only, >0=specific layers)")
    parser.add_argument("--quantization", default=None,
                        choices=["Q4_0", "Q4_1", "Q5_0", "Q5_1", "Q8_0", "F16", "F32"],
                        help="Model quantization format")
    parser.add_argument("--log-level", default="INFO", help="Log level")

    args = parser.parse_args()

    # Initialize system
    system = OllamaPMAgentsSystem(
        ollama_url=args.ollama_url,
        model=args.model,
        num_gpu=args.num_gpu,
        quantization=args.quantization,
        log_level=args.log_level
    )

    try:
        # Run project
        result = await system.run_project(
            project_name=args.project_name,
            project_description=args.project_description,
            project_type=args.project_type,
            requirements=args.requirements
        )

        # Print results
        print("\n" + "=" * 80)
        print("PROJECT EXECUTION COMPLETE (OLLAMA)")
        print("=" * 80)
        print(f"\nStatus: {result['status']}")
        print(f"Project ID: {result.get('project_id', 'N/A')}")

        if result['status'] == 'completed':
            print("\nPhase Gates:")
            for gate_name, gate_info in result.get('phase_gates', {}).items():
                print(f"  {gate_name}: {gate_info.get('decision', 'UNKNOWN')}")

        print("\nSystem Status:")
        status = system.get_system_status()
        print(f"  Model: {status['model']}")
        print(f"  Coordinator calls: {status['coordinator']['total_calls']}")
        print(f"  Planner calls: {status['planner']['total_calls']}")
        print(f"  Supervisor calls: {status['supervisor']['total_calls']}")

        print("\n" + "=" * 80)

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
