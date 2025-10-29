"""
Base Agent Class for PM-Agents Multi-Agent System
Provides core functionality for all agent types
"""

import anthropic
import os
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio


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
class AgentMessage:
    """Message structure for agent-to-agent communication"""
    message_id: str
    correlation_id: str
    sender_id: str
    sender_type: AgentType
    recipient_id: str
    recipient_type: AgentType
    message_type: str  # task_request, task_result, status_update, error_report, context_share
    priority: str  # critical, high, normal, low
    timestamp: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "sender": {
                "id": self.sender_id,
                "type": self.sender_type.value
            },
            "recipient": {
                "id": self.recipient_id,
                "type": self.recipient_type.value
            },
            "message_type": self.message_type,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "metadata": self.metadata
        }


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
        """Convert result to dictionary"""
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


class BaseAgent:
    """
    Base class for all PM-Agents
    Provides common functionality for agent communication, task execution, and MCP tool integration
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize base agent

        Args:
            agent_id: Unique identifier for this agent instance
            agent_type: Type of agent (from AgentType enum)
            api_key: Anthropic API key (defaults to env var)
            model: Claude model to use
            message_bus: Message bus for A2A communication
            logger: Logger instance (creates default if not provided)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.model = model
        self.message_bus = message_bus

        # Initialize Anthropic client
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

        # Setup logging
        self.logger = logger or self._setup_logger()

        # Agent state
        self.current_task: Optional[str] = None
        self.task_history: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, str]] = []

        # MCP tools configuration - to be set by subclasses
        self.mcp_tools: List[Dict[str, Any]] = []
        self.required_mcp_servers: List[str] = []

        # Error handling configuration
        self.max_retries = 3
        self.retry_delay_seconds = 2.0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_failures = 0

        self.logger.info(f"Initialized {agent_type.value} agent: {agent_id}")

    def _setup_logger(self) -> logging.Logger:
        """Setup default logger for agent"""
        logger = logging.getLogger(f"{self.agent_type.value}.{self.agent_id}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def get_system_prompt(self) -> str:
        """
        Get agent-specific system prompt
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement get_system_prompt()")

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return agent capabilities
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement get_capabilities()")

    async def process_task(
        self,
        task_description: str,
        context: TaskContext,
        message_id: Optional[str] = None
    ) -> TaskResult:
        """
        Main entry point for task processing
        Handles retry logic, error handling, and circuit breaker

        Args:
            task_description: Description of task to execute
            context: Task context with project information
            message_id: Optional message ID for correlation

        Returns:
            TaskResult with execution results
        """
        start_time = datetime.now()
        task_id = message_id or self._generate_id()

        self.logger.info(f"Processing task {task_id}: {task_description[:100]}...")
        self.current_task = task_id

        # Check circuit breaker
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.logger.error(f"Circuit breaker open - too many failures")
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": "Circuit breaker open - agent experiencing repeated failures"
                }],
                next_steps=["Investigate agent failures", "Reset circuit breaker"],
                execution_time_seconds=0.0,
                metadata={"circuit_breaker": "open"}
            )

        # Retry loop
        for attempt in range(self.max_retries):
            try:
                result = await self._execute_task(task_description, context, task_id)

                # Reset circuit breaker on success
                self.circuit_breaker_failures = 0

                # Calculate execution time
                execution_time = (datetime.now() - start_time).total_seconds()
                result.execution_time_seconds = execution_time

                # Log result
                self.logger.info(
                    f"Task {task_id} completed with status {result.status.value} "
                    f"in {execution_time:.2f}s"
                )

                # Store in history
                self.task_history.append({
                    "task_id": task_id,
                    "description": task_description,
                    "result": result.to_dict(),
                    "timestamp": datetime.now().isoformat()
                })

                self.current_task = None
                return result

            except Exception as e:
                self.logger.error(f"Task {task_id} attempt {attempt + 1} failed: {str(e)}")
                self.circuit_breaker_failures += 1

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay_seconds * (2 ** attempt))
                else:
                    # Final failure
                    execution_time = (datetime.now() - start_time).total_seconds()
                    return TaskResult(
                        task_id=task_id,
                        status=TaskStatus.FAILED,
                        deliverables=[],
                        risks_identified=[],
                        issues=[{
                            "severity": "critical",
                            "description": f"Task failed after {self.max_retries} attempts: {str(e)}"
                        }],
                        next_steps=["Review error logs", "Check agent configuration"],
                        execution_time_seconds=execution_time,
                        metadata={"error": str(e), "attempts": self.max_retries}
                    )

    async def _execute_task(
        self,
        task_description: str,
        context: TaskContext,
        task_id: str
    ) -> TaskResult:
        """
        Execute task with Claude API
        Can be overridden by subclasses for custom behavior

        Args:
            task_description: Task to execute
            context: Task context
            task_id: Unique task identifier

        Returns:
            TaskResult with execution results
        """
        # Build prompt with context
        prompt = self._build_task_prompt(task_description, context)

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0.7,
            system=self.get_system_prompt(),
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        response_text = response.content[0].text

        # Parse structured output (expecting JSON)
        try:
            result_data = json.loads(response_text)
        except json.JSONDecodeError:
            # If not JSON, wrap in basic structure
            result_data = {
                "deliverables": [{"type": "text", "content": response_text}],
                "risks_identified": [],
                "issues": [],
                "next_steps": []
            }

        # Create TaskResult
        return TaskResult(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            deliverables=result_data.get("deliverables", []),
            risks_identified=result_data.get("risks_identified", []),
            issues=result_data.get("issues", []),
            next_steps=result_data.get("next_steps", []),
            execution_time_seconds=0.0,  # Will be set by process_task
            metadata={
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
        )

    def _build_task_prompt(self, task_description: str, context: TaskContext) -> str:
        """Build prompt with task and context information"""
        prompt = f"""# Task

{task_description}

# Project Context

**Project ID**: {context.project_id}
**Description**: {context.project_description}
**Current Phase**: {context.current_phase}

# Previous Outputs

{json.dumps(context.previous_outputs, indent=2)}

# Requirements

{json.dumps(context.requirements, indent=2)}

# Constraints

{json.dumps(context.constraints, indent=2)}

# Available MCP Tools

{json.dumps(context.mcp_tools_available, indent=2)}

# Expected Output Format

Please provide your response in JSON format with the following structure:

```json
{{
  "deliverables": [
    {{
      "type": "document|code|configuration|data",
      "name": "deliverable name",
      "content": "deliverable content or description",
      "file_path": "optional file path if applicable"
    }}
  ],
  "risks_identified": [
    {{
      "severity": "low|medium|high|critical",
      "category": "technical|schedule|resource|quality",
      "description": "risk description",
      "mitigation": "mitigation strategy"
    }}
  ],
  "issues": [
    {{
      "severity": "low|medium|high|critical",
      "description": "issue description",
      "resolution": "proposed resolution"
    }}
  ],
  "next_steps": [
    "step 1",
    "step 2"
  ]
}}
```

Complete the task following best practices for {self.agent_type.value} agents.
"""
        return prompt

    async def send_message(self, message: AgentMessage):
        """Send message to another agent via message bus"""
        if self.message_bus:
            await self.message_bus.publish(message)
        else:
            self.logger.warning("No message bus configured - message not sent")

    async def delegate_task(
        self,
        recipient_id: str,
        recipient_type: AgentType,
        task_description: str,
        context: TaskContext,
        priority: str = "normal"
    ) -> str:
        """
        Delegate task to another agent

        Returns:
            message_id for tracking the delegation
        """
        message_id = self._generate_id()
        correlation_id = self.current_task or self._generate_id()

        message = AgentMessage(
            message_id=message_id,
            correlation_id=correlation_id,
            sender_id=self.agent_id,
            sender_type=self.agent_type,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            message_type="task_request",
            priority=priority,
            timestamp=datetime.now().isoformat(),
            payload={
                "task_description": task_description,
                "context": {
                    "project_id": context.project_id,
                    "project_description": context.project_description,
                    "current_phase": context.current_phase,
                    "previous_outputs": context.previous_outputs,
                    "constraints": context.constraints,
                    "requirements": context.requirements
                }
            }
        )

        await self.send_message(message)
        self.logger.info(f"Delegated task to {recipient_type.value} agent: {message_id}")

        return message_id

    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "current_task": self.current_task,
            "task_history_count": len(self.task_history),
            "circuit_breaker_failures": self.circuit_breaker_failures,
            "circuit_breaker_open": self.circuit_breaker_failures >= self.circuit_breaker_threshold
        }

    def reset_circuit_breaker(self):
        """Manually reset circuit breaker"""
        self.circuit_breaker_failures = 0
        self.logger.info("Circuit breaker reset")
