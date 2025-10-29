"""
PM-Agents Package
Hierarchical multi-agent system for software development project management
"""

from .base_agent import (
    BaseAgent,
    AgentType,
    TaskStatus,
    AgentMessage,
    TaskContext,
    TaskResult
)

from .message_bus import MessageBus, MessageRouter, MessageAcknowledgment

from .coordinator_agent import CoordinatorAgent
from .planner_agent import PlannerAgent
from .supervisor_agent import SupervisorAgent

from .specialist_agents import (
    SpecKitAgent,
    QdrantVectorAgent,
    FrontendCoderAgent,
    PythonMLDLAgent,
    RAnalyticsAgent,
    TypeScriptValidatorAgent,
    ResearchAgent,
    BrowserAgent,
    ReporterAgent,
    create_specialist_agent
)

__version__ = "0.1.0"

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentType",
    "TaskStatus",
    "AgentMessage",
    "TaskContext",
    "TaskResult",
    # Communication
    "MessageBus",
    "MessageRouter",
    "MessageAcknowledgment",
    # Hierarchy agents
    "CoordinatorAgent",
    "PlannerAgent",
    "SupervisorAgent",
    # Specialist agents
    "SpecKitAgent",
    "QdrantVectorAgent",
    "FrontendCoderAgent",
    "PythonMLDLAgent",
    "RAnalyticsAgent",
    "TypeScriptValidatorAgent",
    "ResearchAgent",
    "BrowserAgent",
    "ReporterAgent",
    # Factory
    "create_specialist_agent"
]
