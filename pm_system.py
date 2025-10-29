"""
PM-Agents System Orchestrator
Main entry point for the hierarchical multi-agent project management system
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add agents package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from agents import (
    CoordinatorAgent,
    PlannerAgent,
    SupervisorAgent,
    MessageBus,
    MessageRouter,
    AgentType,
    AgentMessage,
    create_specialist_agent,
    TaskContext
)


class PMAgentsSystem:
    """
    PM-Agents System Orchestrator
    Manages the entire hierarchical multi-agent system
    """

    def __init__(self, api_key: Optional[str] = None, log_level: str = "INFO"):
        """
        Initialize PM-Agents system

        Args:
            api_key: Anthropic API key (defaults to env var)
            log_level: Logging level
        """
        # Setup logging
        self.logger = self._setup_logging(log_level)

        # Initialize message bus
        self.logger.info("Initializing message bus...")
        self.message_bus = MessageBus(logger=self.logger)

        # Initialize message router
        self.logger.info("Initializing message router...")
        self.message_router = MessageRouter(
            message_bus=self.message_bus,
            logger=self.logger
        )

        # Initialize hierarchy agents
        self.logger.info("Initializing hierarchy agents...")

        self.coordinator = CoordinatorAgent(
            agent_id="coordinator-001",
            api_key=api_key,
            message_bus=self.message_bus
        )

        self.planner = PlannerAgent(
            agent_id="planner-001",
            api_key=api_key,
            message_bus=self.message_bus
        )

        self.supervisor = SupervisorAgent(
            agent_id="supervisor-001",
            api_key=api_key,
            message_bus=self.message_bus,
            message_router=self.message_router
        )

        # Initialize specialist agents
        self.logger.info("Initializing specialist agents...")
        self.specialists: Dict[str, Any] = {}

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
            agent = create_specialist_agent(
                agent_type=agent_type,
                api_key=api_key,
                message_bus=self.message_bus
            )
            self.specialists[agent_type.value] = agent

            # Register with router
            capabilities = agent.get_capabilities()
            self.message_router.register_agent(
                agent_id=agent.agent_id,
                agent_type=agent_type.value,
                capabilities=capabilities
            )

            # Register with supervisor
            self.supervisor.register_specialist(
                agent_type=agent_type.value,
                agent_id=agent.agent_id
            )

        # Subscribe agents to message bus
        self._subscribe_agents()

        self.logger.info("PM-Agents system initialized successfully")

    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup system-wide logging"""
        logger = logging.getLogger("PMAgentsSystem")
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

    def _subscribe_agents(self):
        """Subscribe all agents to message bus"""
        # Subscribe hierarchy agents
        for agent in [self.coordinator, self.planner, self.supervisor]:
            self.message_bus.subscribe(agent.agent_id, self._create_message_handler(agent))

        # Subscribe specialist agents
        for agent in self.specialists.values():
            self.message_bus.subscribe(agent.agent_id, self._create_message_handler(agent))

    def _create_message_handler(self, agent):
        """Create message handler for agent"""
        async def handler(message):
            self.logger.debug(f"Agent {agent.agent_id} received message {message.message_id}")

            if message.message_type == "task_request":
                # Extract task info
                payload = message.payload
                task_description = payload.get("task_description", "")
                context_data = payload.get("context", {})

                # Create TaskContext
                context = TaskContext(
                    project_id=context_data.get("project_id", "unknown"),
                    project_description=context_data.get("project_description", ""),
                    current_phase=context_data.get("current_phase", "execution"),
                    previous_outputs=context_data.get("previous_outputs", {}),
                    constraints=context_data.get("constraints", {}),
                    requirements=context_data.get("requirements", [])
                )

                # Process task
                try:
                    result = await agent.process_task(
                        task_description=task_description,
                        context=context,
                        message_id=message.message_id
                    )

                    # Send result back
                    response_message = AgentMessage(
                        message_id=agent._generate_id(),
                        correlation_id=message.correlation_id,
                        sender_id=agent.agent_id,
                        sender_type=agent.agent_type,
                        recipient_id=message.sender_id,
                        recipient_type=message.sender_type,
                        message_type="task_result",
                        priority=message.priority,
                        timestamp=datetime.now().isoformat(),
                        payload={
                            "task_id": message.message_id,
                            "result": result.to_dict()
                        }
                    )

                    await self.message_bus.publish(response_message)

                    # Acknowledge message
                    await self.message_bus.acknowledge(
                        message_id=message.message_id,
                        recipient_id=agent.agent_id,
                        status="processed"
                    )

                except Exception as e:
                    self.logger.error(f"Error processing task: {str(e)}")

                    # Send error response
                    error_message = AgentMessage(
                        message_id=agent._generate_id(),
                        correlation_id=message.correlation_id,
                        sender_id=agent.agent_id,
                        sender_type=agent.agent_type,
                        recipient_id=message.sender_id,
                        recipient_type=message.sender_type,
                        message_type="error_report",
                        priority="high",
                        timestamp=datetime.now().isoformat(),
                        payload={
                            "task_id": message.message_id,
                            "error": str(e)
                        }
                    )

                    await self.message_bus.publish(error_message)

        return handler

    async def start(self):
        """Start the PM-Agents system"""
        self.logger.info("Starting PM-Agents system...")
        await self.message_bus.start()

    async def stop(self):
        """Stop the PM-Agents system"""
        self.logger.info("Stopping PM-Agents system...")
        await self.message_bus.stop()

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

        # Initiate project with coordinator
        result = await self.coordinator.initiate_project(
            project_name=project_name,
            project_description=project_description,
            project_type=project_type,
            requirements=requirements,
            constraints=constraints
        )

        project_id = result["project_id"]

        # Phase 1: Initiation (already done)
        self.logger.info(f"Phase 1: Initiation complete for {project_id}")

        # Conduct phase gate 1
        gate_1 = await self.coordinator.conduct_phase_gate(
            project_id=project_id,
            phase="initiation",
            phase_outputs=result["result"]
        )

        if gate_1["decision"] != "GO":
            return {
                "status": "halted",
                "phase": "initiation",
                "gate_decision": gate_1
            }

        # Phase 2: Planning
        self.logger.info(f"Phase 2: Planning starting for {project_id}")

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

        if gate_2["decision"] != "GO":
            return {
                "status": "halted",
                "phase": "planning",
                "gate_decision": gate_2
            }

        # Phase 3: Execution
        self.logger.info(f"Phase 3: Execution starting for {project_id}")

        # Extract work packages from plan
        work_packages = []
        for deliverable in planning_result.deliverables:
            if deliverable.get("type") == "document" and "wbs" in deliverable.get("name", "").lower():
                # Extract work packages from WBS
                # In production, would parse WBS structure
                work_packages.append({
                    "name": "Implementation",
                    "description": project_description
                })

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
                "initiation": result["result"],
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
            "message_bus": self.message_bus.get_statistics(),
            "coordinator": self.coordinator.get_status(),
            "planner": self.planner.get_status(),
            "supervisor": self.supervisor.get_status(),
            "specialists": {
                agent_type: agent.get_status()
                for agent_type, agent in self.specialists.items()
            },
            "router": self.message_router.get_agent_load_stats()
        }


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Main entry point for CLI"""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="PM-Agents Multi-Agent System")
    parser.add_argument("--project-name", required=True, help="Project name")
    parser.add_argument("--project-description", required=True, help="Project description")
    parser.add_argument("--project-type", required=True,
                        choices=["frontend", "backend", "ml", "analytics", "fullstack"],
                        help="Project type")
    parser.add_argument("--requirements", nargs="+", required=True, help="Project requirements")
    parser.add_argument("--log-level", default="INFO", help="Log level")

    args = parser.parse_args()

    # Initialize system
    system = PMAgentsSystem(log_level=args.log_level)

    try:
        # Start system
        await system.start()

        # Run project
        result = await system.run_project(
            project_name=args.project_name,
            project_description=args.project_description,
            project_type=args.project_type,
            requirements=args.requirements
        )

        # Print results
        print("\n" + "=" * 80)
        print("PROJECT EXECUTION COMPLETE")
        print("=" * 80)
        print(f"\nStatus: {result['status']}")
        print(f"Project ID: {result.get('project_id', 'N/A')}")

        if result['status'] == 'completed':
            print("\nPhase Gates:")
            for gate_name, gate_info in result.get('phase_gates', {}).items():
                print(f"  {gate_name}: {gate_info['decision']}")

        print("\n" + "=" * 80)

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise
    finally:
        # Stop system
        await system.stop()


if __name__ == "__main__":
    asyncio.run(main())
