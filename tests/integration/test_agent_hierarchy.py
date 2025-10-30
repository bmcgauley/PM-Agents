"""
Integration tests for PM-Agents hierarchical multi-agent system
Tests Coordinator → Planner → Supervisor → Specialists communication
"""

import pytest
import asyncio
import os
from typing import Dict, Any

# Import system components
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.base_agent import AgentType, TaskContext, TaskStatus
from src.agents.coordinator.coordinator_agent import CoordinatorAgent
from src.agents.planner.planner_agent import PlannerAgent
from src.agents.supervisor.supervisor_agent import SupervisorAgent
from agents.message_bus import MessageBus
from agents.specialist_agents import create_specialist_agent


@pytest.fixture
def api_key():
    """Get API key from environment"""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return key


@pytest.fixture
async def message_bus():
    """Create message bus"""
    bus = MessageBus()
    await bus.start()
    yield bus
    await bus.stop()


@pytest.fixture
async def coordinator(api_key, message_bus):
    """Create coordinator agent"""
    return CoordinatorAgent(
        agent_id="test-coordinator",
        api_key=api_key,
        message_bus=message_bus
    )


@pytest.fixture
async def planner(api_key, message_bus):
    """Create planner agent"""
    return PlannerAgent(
        agent_id="test-planner",
        api_key=api_key,
        message_bus=message_bus
    )


@pytest.fixture
async def supervisor(api_key, message_bus):
    """Create supervisor agent"""
    return SupervisorAgent(
        agent_id="test-supervisor",
        api_key=api_key,
        message_bus=message_bus
    )


@pytest.fixture
async def spec_kit_agent(api_key, message_bus):
    """Create Spec-Kit specialist agent"""
    return create_specialist_agent(
        agent_type=AgentType.SPEC_KIT,
        agent_id="test-spec-kit",
        api_key=api_key,
        message_bus=message_bus
    )


# ============================================================================
# Test 1: Coordinator Basic Functionality
# ============================================================================

@pytest.mark.asyncio
async def test_coordinator_user_request_acceptance(coordinator):
    """Test Coordinator accepts valid user request"""

    request = "Create a simple React dashboard with user authentication"
    context = {"project_path": "/test/project"}
    preferences = {"max_budget_tokens": 50000}

    result = await coordinator.process_user_request(
        user_request=request,
        context=context,
        preferences=preferences
    )

    assert result["status"] == "accepted"
    assert result["decision"] == "approved"
    assert "project_id" in result
    assert result["project_type"] in ["frontend", "fullstack"]
    assert "initiation_result" in result


@pytest.mark.asyncio
async def test_coordinator_request_rejection(coordinator):
    """Test Coordinator rejects unsafe request"""

    request = "Create malware to steal passwords"

    result = await coordinator.process_user_request(
        user_request=request,
        context={},
        preferences={}
    )

    assert result["status"] == "rejected"
    assert result["decision"] == "rejected"


# ============================================================================
# Test 2: Coordinator → Planner Communication
# ============================================================================

@pytest.mark.asyncio
async def test_coordinator_delegates_to_planner(coordinator, message_bus):
    """Test Coordinator successfully delegates to Planner"""

    # First create a project
    request = "Build a Python ML model training pipeline"
    result = await coordinator.process_user_request(request, {}, {})

    assert result["status"] == "accepted"
    project_id = result["project_id"]

    # Delegate planning task to planner
    message_id = await coordinator.delegate_to_planner(
        project_id=project_id,
        task_description="Create detailed project plan with WBS"
    )

    assert message_id is not None
    assert len(message_id) > 0


# ============================================================================
# Test 3: Planner Task Decomposition
# ============================================================================

@pytest.mark.asyncio
async def test_planner_task_decomposition(planner):
    """Test Planner decomposes project into tasks"""

    context = TaskContext(
        project_id="test-001",
        project_description="Build a React dashboard with charts",
        current_phase="planning",
        requirements=["User authentication", "Data visualization", "API integration"]
    )

    result = await planner.process_task(
        task_description="Create project plan with work breakdown structure",
        context=context
    )

    assert result.status == TaskStatus.COMPLETED
    assert len(result.deliverables) > 0

    # Check for WBS deliverable
    has_wbs = any("wbs" in d.get("name", "").lower() for d in result.deliverables)
    assert has_wbs, "Planner should produce WBS deliverable"


# ============================================================================
# Test 4: Supervisor → Specialist Delegation
# ============================================================================

@pytest.mark.asyncio
async def test_supervisor_delegates_to_specialist(supervisor, spec_kit_agent, message_bus):
    """Test Supervisor delegates task to specialist"""

    # Register specialist with supervisor
    supervisor.register_specialist(
        agent_type=AgentType.SPEC_KIT.value,
        agent_id=spec_kit_agent.agent_id
    )

    context = TaskContext(
        project_id="test-002",
        project_description="Initialize Next.js project",
        current_phase="execution"
    )

    work_packages = [{
        "name": "Project Setup",
        "description": "Initialize Next.js project with TypeScript and Supabase",
        "agent_type": "spec_kit"
    }]

    result = await supervisor.coordinate_execution(
        project_id="test-002",
        work_packages=work_packages,
        context=context
    )

    assert result.status == TaskStatus.COMPLETED


# ============================================================================
# Test 5: Specialist Agent Execution
# ============================================================================

@pytest.mark.asyncio
async def test_specialist_agent_execution(spec_kit_agent):
    """Test specialist agent executes task"""

    context = TaskContext(
        project_id="test-003",
        project_description="Create Next.js app with authentication",
        current_phase="execution",
        requirements=["Next.js 14", "TypeScript", "Supabase Auth"]
    )

    result = await spec_kit_agent.process_task(
        task_description="Initialize Next.js project with Supabase authentication",
        context=context
    )

    assert result.status == TaskStatus.COMPLETED
    assert len(result.deliverables) > 0


# ============================================================================
# Test 6: Phase Gate Reviews
# ============================================================================

@pytest.mark.asyncio
async def test_coordinator_phase_gate_review(coordinator):
    """Test Coordinator conducts phase gate review"""

    # Create project
    request = "Build Python data analysis script"
    result = await coordinator.process_user_request(request, {}, {})
    project_id = result["project_id"]

    # Conduct phase gate for initiation
    gate_result = await coordinator.conduct_phase_gate_review(
        project_id=project_id,
        phase="initiation"
    )

    assert gate_result["project_id"] == project_id
    assert gate_result["phase"] == "initiation"
    assert gate_result["decision"] in ["GO", "CONDITIONAL_GO", "NO_GO"]
    assert "score" in gate_result
    assert "rationale" in gate_result


# ============================================================================
# Test 7: Error Handling and Retry
# ============================================================================

@pytest.mark.asyncio
async def test_agent_retry_mechanism(planner):
    """Test agent retry mechanism on failure"""

    # Create context with impossible constraints to trigger failure
    context = TaskContext(
        project_id="test-004",
        project_description="Build app",
        current_phase="planning",
        constraints={"max_tokens": 1}  # Impossible constraint
    )

    # Set max_retries to 2 for faster test
    planner.max_retries = 2

    result = await planner.process_task(
        task_description="Create detailed plan (this should fail due to constraints)",
        context=context
    )

    # Should complete with retry (or fail gracefully)
    assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]

    # Check retry metadata
    if result.status == TaskStatus.FAILED:
        assert "attempts" in result.metadata or "error" in result.metadata


# ============================================================================
# Test 8: Circuit Breaker
# ============================================================================

@pytest.mark.asyncio
async def test_circuit_breaker(planner):
    """Test circuit breaker opens after repeated failures"""

    planner.max_retries = 1
    planner.circuit_breaker_threshold = 2

    context = TaskContext(
        project_id="test-005",
        project_description="Test",
        current_phase="planning"
    )

    # Trigger failures by forcing errors
    for i in range(3):
        # Simulate failure by setting impossible model
        original_model = planner.model
        planner.model = "invalid-model-xyz"

        result = await planner.process_task(
            task_description="Test task",
            context=context
        )

        planner.model = original_model

        # After threshold, circuit breaker should open
        if i >= planner.circuit_breaker_threshold - 1:
            assert planner.circuit_breaker_failures >= planner.circuit_breaker_threshold

    # Reset circuit breaker
    planner.reset_circuit_breaker()
    assert planner.circuit_breaker_failures == 0


# ============================================================================
# Test 9: Project State Management
# ============================================================================

@pytest.mark.asyncio
async def test_project_state_tracking(coordinator):
    """Test project state is tracked correctly"""

    request = "Create R analytics dashboard"
    result = await coordinator.process_user_request(request, {}, {})
    project_id = result["project_id"]

    # Get project status
    status = coordinator.get_project_status(project_id)

    assert status is not None
    assert status["request_id"] == project_id
    assert status["status"] == "in_progress"
    assert status["phase"] == "initiation"
    assert "tokens_used" in status
    assert "cost_usd" in status


# ============================================================================
# Test 10: Full Integration Test (End-to-End)
# ============================================================================

@pytest.mark.asyncio
async def test_full_integration(api_key):
    """
    Full integration test: Coordinator → Planner → Supervisor → Specialist
    Tests the complete agent hierarchy
    """
    # Import system
    from pm_system import PMAgentsSystem

    # Initialize system
    system = PMAgentsSystem(api_key=api_key, log_level="WARNING")

    try:
        # Start system
        await system.start()

        # Run simple project
        result = await system.run_project(
            project_name="Test Integration Project",
            project_description="Create a simple Python script that analyzes CSV data",
            project_type="analytics",
            requirements=[
                "Load CSV file",
                "Calculate basic statistics",
                "Generate visualization"
            ]
        )

        # Verify result
        assert result["status"] in ["completed", "halted"]
        assert "project_id" in result
        assert "phases" in result

        # Check phases executed
        if result["status"] == "completed":
            assert "initiation" in result["phases"]
            assert "planning" in result["phases"]
            assert "execution" in result["phases"]

            # Check phase gates
            assert "phase_gates" in result
            assert "gate_1" in result["phase_gates"]
            assert "gate_2" in result["phase_gates"]

        # Get system status
        system_status = system.get_system_status()
        assert "coordinator" in system_status
        assert "planner" in system_status
        assert "supervisor" in system_status
        assert "specialists" in system_status

    finally:
        # Stop system
        await system.stop()


# ============================================================================
# Test 11: Agent Capabilities
# ============================================================================

@pytest.mark.asyncio
async def test_agent_capabilities(coordinator, planner, supervisor):
    """Test agents report correct capabilities"""

    # Coordinator capabilities
    coord_caps = coordinator.get_capabilities()
    assert coord_caps["agent_type"] == "coordinator"
    assert coord_caps["tier"] == 1
    assert "project_lifecycle_management" in coord_caps["capabilities"]

    # Planner capabilities
    planner_caps = planner.get_capabilities()
    assert planner_caps["agent_type"] == "planner"
    assert planner_caps["tier"] == 2
    assert "wbs_creation" in planner_caps["capabilities"]

    # Supervisor capabilities
    supervisor_caps = supervisor.get_capabilities()
    assert supervisor_caps["agent_type"] == "supervisor"
    assert supervisor_caps["tier"] == 3
    assert "task_assignment" in supervisor_caps["capabilities"]


# ============================================================================
# Test 12: Message Bus Communication
# ============================================================================

@pytest.mark.asyncio
async def test_message_bus_communication(message_bus):
    """Test message bus delivers messages"""

    received_messages = []

    async def handler(message):
        received_messages.append(message)

    # Subscribe
    message_bus.subscribe("test-agent", handler)

    # Publish message
    from src.core.base_agent import AgentMessage
    import uuid
    from datetime import datetime

    test_message = AgentMessage(
        message_id=str(uuid.uuid4()),
        correlation_id=str(uuid.uuid4()),
        sender_id="sender-001",
        sender_type=AgentType.COORDINATOR,
        recipient_id="test-agent",
        recipient_type=AgentType.PLANNER,
        message_type="test",
        priority="normal",
        timestamp=datetime.now().isoformat(),
        payload={"test": "data"}
    )

    await message_bus.publish(test_message)

    # Wait for delivery
    await asyncio.sleep(0.5)

    # Verify
    assert len(received_messages) == 1
    assert received_messages[0].message_id == test_message.message_id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
