"""
Integration Tests for Ollama PM-Agents System
Tests the complete Ollama-based hierarchical multi-agent system
Uses Gemma3:1b model by default
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pm_ollama_agents import (
    OllamaPMAgentsSystem,
    OllamaCoordinatorAgent,
    OllamaPlannerAgent,
    OllamaSupervisorAgent,
    OllamaBaseAgent,
    AgentType,
    TaskContext,
    TaskStatus,
    create_ollama_specialist_agent
)

# Skip all tests if Ollama is not available
pytest_plugins = []

def check_ollama_available():
    """Check if Ollama is running"""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

OLLAMA_AVAILABLE = check_ollama_available()
skip_if_no_ollama = pytest.mark.skipif(
    not OLLAMA_AVAILABLE,
    reason="Ollama is not running. Start with 'ollama serve'"
)


# ============================================================================
# Test OllamaBaseAgent
# ============================================================================

@skip_if_no_ollama
def test_ollama_base_agent_initialization():
    """Test OllamaBaseAgent initialization"""
    agent = OllamaBaseAgent(
        agent_id="test-agent-001",
        agent_type=AgentType.RESEARCH,
        model="gemma3:1b"
    )

    assert agent.agent_id == "test-agent-001"
    assert agent.agent_type == AgentType.RESEARCH
    assert agent.model == "gemma3:1b"
    assert agent.circuit_breaker_open == False
    assert agent.total_calls == 0


@skip_if_no_ollama
@pytest.mark.asyncio
async def test_ollama_base_agent_process_task():
    """Test OllamaBaseAgent task processing"""
    agent = OllamaBaseAgent(
        agent_id="test-agent-002",
        agent_type=AgentType.RESEARCH,
        model="gemma3:1b"
    )

    context = TaskContext(
        project_id="test-project-001",
        project_description="Test project",
        current_phase="execution",
        requirements=["Requirement 1"],
        constraints={}
    )

    result = await agent.process_task(
        task_description="Provide a simple test response",
        context=context
    )

    assert result is not None
    assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
    assert isinstance(result.deliverables, list)
    assert isinstance(result.risks_identified, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.next_steps, list)
    assert result.execution_time_seconds > 0


# ============================================================================
# Test Hierarchy Agents
# ============================================================================

@skip_if_no_ollama
@pytest.mark.asyncio
async def test_coordinator_agent_initiate_project():
    """Test CoordinatorAgent project initiation"""
    coordinator = OllamaCoordinatorAgent(model="gemma3:1b")

    result = await coordinator.initiate_project(
        project_name="Test Project",
        project_description="A test project for validation",
        project_type="frontend",
        requirements=["User authentication", "Responsive design"],
        constraints={"timeline": "2 weeks"}
    )

    assert result is not None
    assert "project_id" in result
    assert result["project_name"] == "Test Project"
    assert result["project_type"] == "frontend"
    assert "initiation_timestamp" in result


@skip_if_no_ollama
@pytest.mark.asyncio
async def test_coordinator_agent_phase_gate():
    """Test CoordinatorAgent phase gate review"""
    coordinator = OllamaCoordinatorAgent(model="gemma3:1b")

    phase_outputs = {
        "deliverables": [
            {"name": "Project Charter", "status": "complete"}
        ],
        "risks": []
    }

    decision = await coordinator.conduct_phase_gate(
        project_id="test-project-001",
        phase="initiation",
        phase_outputs=phase_outputs
    )

    assert decision is not None
    assert "decision" in decision
    assert decision["decision"] in ["GO", "CONDITIONAL_GO", "NO_GO"]


@skip_if_no_ollama
@pytest.mark.asyncio
async def test_planner_agent_create_plan():
    """Test PlannerAgent plan creation"""
    planner = OllamaPlannerAgent(model="gemma3:1b")

    result = await planner.create_project_plan(
        project_id="test-project-002",
        project_description="Build a frontend application",
        project_type="frontend",
        requirements=["React", "TypeScript", "Responsive"],
        constraints={"budget": "limited"}
    )

    assert result is not None
    assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
    assert len(result.deliverables) > 0


@skip_if_no_ollama
@pytest.mark.asyncio
async def test_supervisor_agent_coordination():
    """Test SupervisorAgent coordination"""
    supervisor = OllamaSupervisorAgent(model="gemma3:1b")

    # Register a specialist
    specialist = create_ollama_specialist_agent(
        agent_type=AgentType.FRONTEND_CODER,
        model="gemma3:1b"
    )
    supervisor.register_specialist("frontend_coder", specialist)

    context = TaskContext(
        project_id="test-project-003",
        project_description="Build components",
        current_phase="execution",
        requirements=["Component library"],
        constraints={}
    )

    result = await supervisor.coordinate_execution(
        project_id="test-project-003",
        work_packages=[{"name": "Component", "description": "Build component"}],
        context=context
    )

    assert result is not None
    assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]


# ============================================================================
# Test Specialist Agents
# ============================================================================

@skip_if_no_ollama
def test_create_specialist_agents():
    """Test creation of all specialist agent types"""
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
            model="gemma3:1b"
        )

        assert agent is not None
        assert agent.agent_type == agent_type
        assert agent.model == "gemma3:1b"


# ============================================================================
# Test GPU and Quantization Options
# ============================================================================

@skip_if_no_ollama
def test_gpu_configuration():
    """Test GPU configuration options"""
    # Test auto GPU
    agent_auto = OllamaBaseAgent(
        agent_id="gpu-test-auto",
        agent_type=AgentType.RESEARCH,
        num_gpu=-1
    )
    assert agent_auto.num_gpu == -1

    # Test CPU only
    agent_cpu = OllamaBaseAgent(
        agent_id="gpu-test-cpu",
        agent_type=AgentType.RESEARCH,
        num_gpu=0
    )
    assert agent_cpu.num_gpu == 0

    # Test specific GPU layers
    agent_gpu = OllamaBaseAgent(
        agent_id="gpu-test-layers",
        agent_type=AgentType.RESEARCH,
        num_gpu=35
    )
    assert agent_gpu.num_gpu == 35


@skip_if_no_ollama
def test_quantization_configuration():
    """Test quantization configuration"""
    quantization_formats = ["Q4_0", "Q4_1", "Q5_0", "Q5_1", "Q8_0", "F16", "F32"]

    for quant in quantization_formats:
        agent = OllamaBaseAgent(
            agent_id=f"quant-test-{quant}",
            agent_type=AgentType.RESEARCH,
            quantization=quant
        )
        assert agent.quantization == quant


# ============================================================================
# Test Complete System
# ============================================================================

@skip_if_no_ollama
@pytest.mark.asyncio
async def test_ollama_system_initialization():
    """Test OllamaPMAgentsSystem initialization"""
    system = OllamaPMAgentsSystem(
        model="gemma3:1b",
        log_level="ERROR"  # Suppress logs during testing
    )

    assert system.coordinator is not None
    assert system.planner is not None
    assert system.supervisor is not None
    assert len(system.specialists) == 9

    # Verify all specialists registered
    expected_specialists = [
        "spec_kit", "qdrant_vector", "frontend_coder",
        "python_ml_dl", "r_analytics", "typescript_validator",
        "research", "browser", "reporter"
    ]

    for specialist in expected_specialists:
        assert specialist in system.specialists


@skip_if_no_ollama
@pytest.mark.asyncio
async def test_ollama_system_status():
    """Test system status reporting"""
    system = OllamaPMAgentsSystem(
        model="gemma3:1b",
        log_level="ERROR"
    )

    status = system.get_system_status()

    assert "coordinator" in status
    assert "planner" in status
    assert "supervisor" in status
    assert "specialists" in status
    assert "ollama_url" in status
    assert "model" in status

    assert status["model"] == "gemma3:1b"
    assert len(status["specialists"]) == 9


@skip_if_no_ollama
@pytest.mark.asyncio
async def test_ollama_system_simple_project():
    """Test running a simple project through the system"""
    system = OllamaPMAgentsSystem(
        model="gemma3:1b",
        log_level="ERROR"
    )

    result = await system.run_project(
        project_name="Test Frontend Project",
        project_description="Build a simple React application with user authentication",
        project_type="frontend",
        requirements=["React 18+", "TypeScript", "User login"]
    )

    assert result is not None
    assert "status" in result
    assert result["status"] in ["completed", "halted"]

    if result["status"] == "completed":
        assert "project_id" in result
        assert "phases" in result
        assert "phase_gates" in result


# ============================================================================
# Test Error Handling
# ============================================================================

@skip_if_no_ollama
@pytest.mark.asyncio
async def test_circuit_breaker():
    """Test circuit breaker functionality"""
    agent = OllamaBaseAgent(
        agent_id="circuit-test",
        agent_type=AgentType.RESEARCH,
        model="nonexistent-model"  # This will cause failures
    )

    context = TaskContext(
        project_id="test",
        project_description="Test",
        current_phase="test",
        requirements=[],
        constraints={}
    )

    # Try to trigger circuit breaker
    for i in range(5):
        result = await agent.process_task("Test task", context)
        if result.status == TaskStatus.FAILED:
            agent.total_failures += 1
            agent.circuit_breaker_failures += 1

    # Circuit breaker should open after threshold
    assert agent.circuit_breaker_failures >= agent.circuit_breaker_threshold


# ============================================================================
# Performance Tests
# ============================================================================

@skip_if_no_ollama
@pytest.mark.asyncio
async def test_performance_tracking():
    """Test performance metrics tracking"""
    agent = OllamaBaseAgent(
        agent_id="perf-test",
        agent_type=AgentType.RESEARCH,
        model="gemma3:1b"
    )

    context = TaskContext(
        project_id="perf-test",
        project_description="Performance test",
        current_phase="test",
        requirements=[],
        constraints={}
    )

    # Execute a task
    await agent.process_task("Simple task", context)

    # Check metrics
    status = agent.get_status()
    assert status["total_calls"] > 0
    assert status["total_execution_time"] > 0.0


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    if not OLLAMA_AVAILABLE:
        print("⚠️  Ollama is not running. Please start Ollama:")
        print("   1. Run: ollama serve")
        print("   2. Run: ollama pull gemma3:1b")
        print("   3. Re-run tests")
        sys.exit(1)

    print("Running Ollama PM-Agents integration tests...")
    print("=" * 70)

    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
