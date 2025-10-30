"""
PM-Agents Multi-Agent System - Hybrid Implementation
Intelligent hybrid orchestration combining Claude (Tier 1-2) and Ollama (Tier 4)

Architecture:
- Tier 1 (Coordinator): Claude - Strategic oversight, phase gates
- Tier 2 (Planner): Claude - Strategic planning, task decomposition
- Tier 3 (Supervisor): Claude - Task coordination and routing
- Tier 4 (Specialists): Ollama - Code generation, documentation, execution

This optimizes for quality (Claude strategy) and cost (Ollama execution).
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Import from both implementations
from agents import (
    CoordinatorAgent,
    PlannerAgent,
    SupervisorAgent,
    AgentType,
    TaskContext,
    TaskResult,
    TaskStatus,
    ProjectState,
    DecisionEngine
)

from pm_ollama_agents import (
    OllamaBaseAgent,
    create_ollama_specialist_agent
)


# ============================================================================
# Hybrid Configuration
# ============================================================================

@dataclass
class HybridConfig:
    """Configuration for hybrid mode"""
    # Backend assignment per tier
    tier_1_backend: str = "claude"  # Coordinator
    tier_2_backend: str = "claude"  # Planner
    tier_3_backend: str = "claude"  # Supervisor
    tier_4_backend: str = "ollama"  # Specialists

    # Fallback configuration
    fallback_backend: str = "ollama"
    enable_fallback: bool = True

    # Cost management
    max_claude_cost_usd: float = 10.0
    cost_optimization_mode: str = "balanced"  # "quality", "balanced", "cost"

    # Ollama configuration
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:1b"
    ollama_num_gpu: int = -1

    # Performance tracking
    enable_cost_tracking: bool = True
    enable_performance_metrics: bool = True


@dataclass
class CostMetrics:
    """Cost tracking for hybrid mode"""
    total_claude_calls: int = 0
    total_ollama_calls: int = 0
    total_claude_tokens: int = 0
    total_ollama_tokens: int = 0
    estimated_claude_cost_usd: float = 0.0
    estimated_ollama_cost_usd: float = 0.0
    cost_savings_usd: float = 0.0

    # Pricing (approximate for Claude Sonnet 4.5)
    claude_input_cost_per_1m: float = 3.0
    claude_output_cost_per_1m: float = 15.0
    ollama_cost_per_1m: float = 0.0

    def add_claude_call(self, input_tokens: int, output_tokens: int):
        """Track a Claude API call"""
        self.total_claude_calls += 1
        self.total_claude_tokens += input_tokens + output_tokens

        cost = (
            (input_tokens / 1_000_000) * self.claude_input_cost_per_1m +
            (output_tokens / 1_000_000) * self.claude_output_cost_per_1m
        )
        self.estimated_claude_cost_usd += cost

    def add_ollama_call(self, tokens: int):
        """Track an Ollama call"""
        self.total_ollama_calls += 1
        self.total_ollama_tokens += tokens
        # Ollama is free (local)
        self.estimated_ollama_cost_usd = 0.0

    def calculate_savings(self):
        """Calculate cost savings vs pure Claude"""
        # Estimate what it would cost if all Ollama calls used Claude
        hypothetical_claude_cost = (
            (self.total_ollama_tokens / 1_000_000) *
            (self.claude_input_cost_per_1m + self.claude_output_cost_per_1m) / 2
        )
        self.cost_savings_usd = hypothetical_claude_cost
        return self.cost_savings_usd

    def get_summary(self) -> Dict[str, Any]:
        """Get cost metrics summary"""
        self.calculate_savings()
        return {
            "total_calls": self.total_claude_calls + self.total_ollama_calls,
            "claude_calls": self.total_claude_calls,
            "ollama_calls": self.total_ollama_calls,
            "claude_tokens": self.total_claude_tokens,
            "ollama_tokens": self.total_ollama_tokens,
            "claude_cost_usd": round(self.estimated_claude_cost_usd, 4),
            "ollama_cost_usd": self.estimated_ollama_cost_usd,
            "total_cost_usd": round(self.estimated_claude_cost_usd, 4),
            "cost_savings_usd": round(self.cost_savings_usd, 4),
            "cost_reduction_percent": round(
                (self.cost_savings_usd / (self.estimated_claude_cost_usd + self.cost_savings_usd)) * 100
                if (self.estimated_claude_cost_usd + self.cost_savings_usd) > 0 else 0,
                2
            )
        }


# ============================================================================
# Hybrid Supervisor (Routes to Claude or Ollama Specialists)
# ============================================================================

class HybridSupervisor(SupervisorAgent):
    """
    Hybrid Supervisor - Routes specialist tasks to Claude or Ollama
    Uses intelligent routing based on task complexity and cost
    """

    def __init__(
        self,
        agent_id: str = "hybrid-supervisor-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        hybrid_config: Optional[HybridConfig] = None,
        cost_metrics: Optional[CostMetrics] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(
            agent_id=agent_id,
            api_key=api_key,
            message_bus=message_bus
        )

        self.hybrid_config = hybrid_config or HybridConfig()
        self.cost_metrics = cost_metrics or CostMetrics()
        self.hybrid_logger = logger or logging.getLogger("HybridSupervisor")

        # Specialist pools (both Claude and Ollama)
        self.claude_specialists: Dict[str, Any] = {}
        self.ollama_specialists: Dict[str, OllamaBaseAgent] = {}

    def register_claude_specialist(self, agent_type: str, agent: Any):
        """Register a Claude-based specialist"""
        self.claude_specialists[agent_type] = agent
        self.hybrid_logger.info(f"Registered Claude specialist: {agent_type}")

    def register_ollama_specialist(self, agent_type: str, agent: OllamaBaseAgent):
        """Register an Ollama-based specialist"""
        self.ollama_specialists[agent_type] = agent
        self.hybrid_logger.info(f"Registered Ollama specialist: {agent_type}")

    def _route_specialist_task(
        self,
        agent_type: str,
        task_description: str,
        context: TaskContext
    ) -> str:
        """
        Determine which backend to use for this specialist task

        Returns: "claude" or "ollama"
        """
        # Check cost optimization mode
        mode = self.hybrid_config.cost_optimization_mode

        # Check if we're over budget
        if self.cost_metrics.estimated_claude_cost_usd >= self.hybrid_config.max_claude_cost_usd:
            self.hybrid_logger.warning(f"Claude budget exceeded, routing to Ollama")
            return "ollama"

        # Route based on mode
        if mode == "quality":
            # Use Claude for everything
            return "claude" if agent_type in self.claude_specialists else "ollama"

        elif mode == "cost":
            # Use Ollama for everything (Tier 4)
            return "ollama"

        else:  # "balanced"
            # Use Tier 4 backend from config (default: Ollama for specialists)
            backend = self.hybrid_config.tier_4_backend

            # But fallback if specialist not available
            if backend == "claude" and agent_type not in self.claude_specialists:
                return "ollama"
            if backend == "ollama" and agent_type not in self.ollama_specialists:
                return "claude"

            return backend

    async def _execute_specialist_task(
        self,
        agent_type: str,
        task_description: str,
        context: TaskContext
    ) -> TaskResult:
        """
        Execute task with appropriate specialist (Claude or Ollama)
        """
        # Determine routing
        backend = self._route_specialist_task(agent_type, task_description, context)

        self.hybrid_logger.info(f"Routing {agent_type} task to {backend.upper()}")

        try:
            if backend == "claude" and agent_type in self.claude_specialists:
                # Use Claude specialist
                agent = self.claude_specialists[agent_type]
                result = await agent.process_task(task_description, context)

                # Track cost (estimate tokens)
                estimated_tokens = len(task_description) * 2  # Rough estimate
                self.cost_metrics.add_claude_call(estimated_tokens // 2, estimated_tokens // 2)

            elif backend == "ollama" or agent_type in self.ollama_specialists:
                # Use Ollama specialist
                agent = self.ollama_specialists.get(agent_type)
                if not agent:
                    raise ValueError(f"Ollama specialist not found: {agent_type}")

                result = await agent.process_task(task_description, context)

                # Track Ollama usage
                estimated_tokens = len(task_description) * 2
                self.cost_metrics.add_ollama_call(estimated_tokens)

            else:
                raise ValueError(f"No specialist available for {agent_type} on {backend}")

            return result

        except Exception as e:
            self.hybrid_logger.error(f"Error executing {agent_type} task: {str(e)}")

            # Try fallback if enabled
            if self.hybrid_config.enable_fallback:
                fallback_backend = "ollama" if backend == "claude" else "claude"
                self.hybrid_logger.warning(f"Attempting fallback to {fallback_backend}")

                if fallback_backend == "ollama" and agent_type in self.ollama_specialists:
                    agent = self.ollama_specialists[agent_type]
                    result = await agent.process_task(task_description, context)
                    self.cost_metrics.add_ollama_call(len(task_description) * 2)
                    return result

            # If fallback fails, return error result
            return TaskResult(
                task_id=self._generate_id(),
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "type": "execution_error",
                    "severity": "high",
                    "description": f"Failed to execute {agent_type} task: {str(e)}"
                }],
                next_steps=["Review error", "Retry task"],
                execution_time_seconds=0.0,
                metadata={"error": str(e), "backend": backend}
            )


# ============================================================================
# Hybrid PM-Agents System
# ============================================================================

class HybridPMAgentsSystem:
    """
    Hybrid PM-Agents System
    Combines Claude (strategic) and Ollama (execution) for optimal cost/quality

    Architecture:
    - Coordinator (Claude): Strategic oversight, phase gates
    - Planner (Claude): Strategic planning, WBS
    - Supervisor (Hybrid): Routes to Claude or Ollama specialists
    - Specialists (Ollama): Code generation, execution
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        hybrid_config: Optional[HybridConfig] = None,
        log_level: str = "INFO"
    ):
        """
        Initialize Hybrid PM-Agents system

        Args:
            api_key: Anthropic API key for Claude
            hybrid_config: Hybrid configuration
            log_level: Logging level
        """
        self.hybrid_config = hybrid_config or HybridConfig()
        self.cost_metrics = CostMetrics()
        self.logger = self._setup_logging(log_level)

        self.logger.info("=" * 70)
        self.logger.info("INITIALIZING HYBRID PM-AGENTS SYSTEM")
        self.logger.info("=" * 70)
        self.logger.info(f"Tier 1 (Coordinator): {self.hybrid_config.tier_1_backend.upper()}")
        self.logger.info(f"Tier 2 (Planner): {self.hybrid_config.tier_2_backend.upper()}")
        self.logger.info(f"Tier 3 (Supervisor): {self.hybrid_config.tier_3_backend.upper()}")
        self.logger.info(f"Tier 4 (Specialists): {self.hybrid_config.tier_4_backend.upper()}")
        self.logger.info(f"Cost Optimization: {self.hybrid_config.cost_optimization_mode.upper()}")
        self.logger.info(f"Max Claude Budget: ${self.hybrid_config.max_claude_cost_usd:.2f}")
        self.logger.info("=" * 70)

        # Initialize Tier 1: Coordinator (Claude)
        self.logger.info("Initializing Tier 1: Coordinator (Claude)...")
        self.coordinator = CoordinatorAgent(
            agent_id="hybrid-coordinator-001",
            api_key=api_key
        )

        # Initialize Tier 2: Planner (Claude)
        self.logger.info("Initializing Tier 2: Planner (Claude)...")
        self.planner = PlannerAgent(
            agent_id="hybrid-planner-001",
            api_key=api_key
        )

        # Initialize Tier 3: Supervisor (Hybrid)
        self.logger.info("Initializing Tier 3: Supervisor (Hybrid)...")
        self.supervisor = HybridSupervisor(
            agent_id="hybrid-supervisor-001",
            api_key=api_key,
            hybrid_config=self.hybrid_config,
            cost_metrics=self.cost_metrics,
            logger=self.logger
        )

        # Initialize Tier 4: Specialists (Ollama)
        self.logger.info("Initializing Tier 4: Specialists (Ollama)...")
        self._initialize_ollama_specialists()

        self.logger.info("✓ Hybrid PM-Agents system initialized successfully")

    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup system-wide logging"""
        logger = logging.getLogger("HybridPMAgentsSystem")
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

    def _initialize_ollama_specialists(self):
        """Initialize Ollama-based specialist agents"""
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
                ollama_url=self.hybrid_config.ollama_url,
                model=self.hybrid_config.ollama_model,
                num_gpu=self.hybrid_config.ollama_num_gpu,
                logger=self.logger
            )
            self.supervisor.register_ollama_specialist(agent_type.value, agent)

    async def run_project(
        self,
        project_name: str,
        project_description: str,
        project_type: str,
        requirements: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a complete project through the hybrid system

        Args:
            project_name: Project name
            project_description: Project description
            project_type: Type (frontend, backend, ml, analytics, fullstack)
            requirements: List of requirements
            constraints: Optional constraints

        Returns:
            Project execution results with cost metrics
        """
        self.logger.info(f"Starting hybrid project: {project_name}")
        start_time = datetime.now()

        # Phase 1: Initiation (Claude Coordinator)
        self.logger.info("Phase 1: Initiation (Claude Coordinator)")
        initiation_result = await self.coordinator.initiate_project(
            project_name=project_name,
            project_description=project_description,
            project_type=project_type,
            requirements=requirements,
            constraints=constraints
        )

        project_id = initiation_result["project_id"]

        # Track Claude usage
        self.cost_metrics.add_claude_call(1000, 500)  # Rough estimate

        # Conduct phase gate 1 (Claude)
        gate_1 = await self.coordinator.conduct_phase_gate(
            project_id=project_id,
            phase="initiation",
            phase_outputs=initiation_result
        )
        self.cost_metrics.add_claude_call(500, 200)

        if gate_1.get("decision") not in ["GO", "CONDITIONAL_GO"]:
            return {
                "status": "halted",
                "phase": "initiation",
                "gate_decision": gate_1,
                "cost_metrics": self.cost_metrics.get_summary()
            }

        # Phase 2: Planning (Claude Planner)
        self.logger.info("Phase 2: Planning (Claude Planner)")
        planning_result = await self.planner.create_project_plan(
            project_id=project_id,
            project_description=project_description,
            project_type=project_type,
            requirements=requirements,
            constraints=constraints
        )
        self.cost_metrics.add_claude_call(1500, 800)

        # Conduct phase gate 2 (Claude)
        gate_2 = await self.coordinator.conduct_phase_gate(
            project_id=project_id,
            phase="planning",
            phase_outputs=planning_result.to_dict()
        )
        self.cost_metrics.add_claude_call(600, 250)

        if gate_2.get("decision") not in ["GO", "CONDITIONAL_GO"]:
            return {
                "status": "halted",
                "phase": "planning",
                "gate_decision": gate_2,
                "initiation": initiation_result,
                "planning": planning_result.to_dict(),
                "cost_metrics": self.cost_metrics.get_summary()
            }

        # Phase 3: Execution (Hybrid Supervisor → Ollama Specialists)
        self.logger.info("Phase 3: Execution (Hybrid Supervisor → Ollama Specialists)")

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

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "status": "completed",
            "project_id": project_id,
            "execution_time_seconds": execution_time,
            "phases": {
                "initiation": initiation_result,
                "planning": planning_result.to_dict(),
                "execution": execution_result.to_dict()
            },
            "phase_gates": {
                "gate_1": gate_1,
                "gate_2": gate_2
            },
            "cost_metrics": self.cost_metrics.get_summary()
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status including cost metrics"""
        return {
            "mode": "hybrid",
            "configuration": {
                "tier_1": self.hybrid_config.tier_1_backend,
                "tier_2": self.hybrid_config.tier_2_backend,
                "tier_3": self.hybrid_config.tier_3_backend,
                "tier_4": self.hybrid_config.tier_4_backend,
                "optimization_mode": self.hybrid_config.cost_optimization_mode,
                "max_budget_usd": self.hybrid_config.max_claude_cost_usd
            },
            "coordinator": self.coordinator.get_status(),
            "planner": self.planner.get_status(),
            "supervisor": self.supervisor.get_status(),
            "cost_metrics": self.cost_metrics.get_summary(),
            "specialists": {
                "ollama_count": len(self.supervisor.ollama_specialists),
                "claude_count": len(self.supervisor.claude_specialists)
            }
        }


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Main entry point for hybrid CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="PM-Agents Multi-Agent System (Hybrid Mode)")
    parser.add_argument("--project-name", required=True, help="Project name")
    parser.add_argument("--project-description", required=True, help="Project description")
    parser.add_argument("--project-type", required=True,
                        choices=["frontend", "backend", "ml", "analytics", "fullstack"],
                        help="Project type")
    parser.add_argument("--requirements", nargs="+", required=True, help="Project requirements")

    # Hybrid configuration
    parser.add_argument("--mode", default="balanced",
                        choices=["quality", "balanced", "cost"],
                        help="Cost optimization mode")
    parser.add_argument("--max-budget", type=float, default=10.0,
                        help="Max Claude budget in USD")
    parser.add_argument("--ollama-model", default="gemma3:1b",
                        help="Ollama model for specialists")
    parser.add_argument("--log-level", default="INFO", help="Log level")

    args = parser.parse_args()

    # Create hybrid config
    hybrid_config = HybridConfig(
        cost_optimization_mode=args.mode,
        max_claude_cost_usd=args.max_budget,
        ollama_model=args.ollama_model
    )

    # Initialize system
    system = HybridPMAgentsSystem(
        hybrid_config=hybrid_config,
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
        print("PROJECT EXECUTION COMPLETE (HYBRID MODE)")
        print("=" * 80)
        print(f"\nStatus: {result['status']}")
        print(f"Project ID: {result.get('project_id', 'N/A')}")
        print(f"Execution Time: {result.get('execution_time_seconds', 0):.2f}s")

        if result['status'] == 'completed':
            print("\nPhase Gates:")
            for gate_name, gate_info in result.get('phase_gates', {}).items():
                print(f"  {gate_name}: {gate_info.get('decision', 'UNKNOWN')}")

        # Print cost metrics
        print("\nCost Metrics:")
        cost = result.get('cost_metrics', {})
        print(f"  Total Calls: {cost.get('total_calls', 0)}")
        print(f"  Claude Calls: {cost.get('claude_calls', 0)}")
        print(f"  Ollama Calls: {cost.get('ollama_calls', 0)}")
        print(f"  Claude Cost: ${cost.get('claude_cost_usd', 0):.4f}")
        print(f"  Ollama Cost: ${cost.get('ollama_cost_usd', 0):.4f}")
        print(f"  Total Cost: ${cost.get('total_cost_usd', 0):.4f}")
        print(f"  Cost Savings: ${cost.get('cost_savings_usd', 0):.4f} ({cost.get('cost_reduction_percent', 0):.1f}%)")

        print("\n" + "=" * 80)

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
