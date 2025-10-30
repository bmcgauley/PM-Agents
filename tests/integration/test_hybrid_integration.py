"""
Integration Tests for Hybrid PM-Agents System
Tests the hybrid orchestration combining Claude and Ollama
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pm_hybrid_agents import (
    HybridPMAgentsSystem,
    HybridConfig,
    CostMetrics,
    HybridSupervisor
)

from agents import TaskContext, AgentType
from pm_ollama_agents import create_ollama_specialist_agent

# Skip tests if either backend unavailable
pytest_plugins = []

def check_anthropic_available():
    """Check if Anthropic API key is set"""
    import os
    return os.getenv("ANTHROPIC_API_KEY") is not None

def check_ollama_available():
    """Check if Ollama is running"""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

ANTHROPIC_AVAILABLE = check_anthropic_available()
OLLAMA_AVAILABLE = check_ollama_available()
HYBRID_AVAILABLE = ANTHROPIC_AVAILABLE and OLLAMA_AVAILABLE

skip_if_no_hybrid = pytest.mark.skipif(
    not HYBRID_AVAILABLE,
    reason="Hybrid mode requires both Anthropic API key and Ollama running"
)


# ============================================================================
# Test Cost Metrics
# ============================================================================

def test_cost_metrics_initialization():
    """Test CostMetrics initialization"""
    metrics = CostMetrics()

    assert metrics.total_claude_calls == 0
    assert metrics.total_ollama_calls == 0
    assert metrics.estimated_claude_cost_usd == 0.0
    assert metrics.cost_savings_usd == 0.0


def test_cost_metrics_claude_tracking():
    """Test Claude cost tracking"""
    metrics = CostMetrics()

    # Track a Claude call
    metrics.add_claude_call(input_tokens=1000, output_tokens=500)

    assert metrics.total_claude_calls == 1
    assert metrics.total_claude_tokens == 1500
    assert metrics.estimated_claude_cost_usd > 0

    # Calculate expected cost
    expected_cost = (1000 / 1_000_000) * 3.0 + (500 / 1_000_000) * 15.0
    assert abs(metrics.estimated_claude_cost_usd - expected_cost) < 0.0001


def test_cost_metrics_ollama_tracking():
    """Test Ollama cost tracking"""
    metrics = CostMetrics()

    # Track an Ollama call
    metrics.add_ollama_call(tokens=2000)

    assert metrics.total_ollama_calls == 1
    assert metrics.total_ollama_tokens == 2000
    assert metrics.estimated_ollama_cost_usd == 0.0  # Ollama is free


def test_cost_metrics_savings_calculation():
    """Test cost savings calculation"""
    metrics = CostMetrics()

    # Add some calls
    metrics.add_claude_call(1000, 500)
    metrics.add_ollama_call(2000)

    # Calculate savings
    savings = metrics.calculate_savings()

    assert savings > 0  # Should have savings from using Ollama
    assert metrics.cost_savings_usd > 0


def test_cost_metrics_summary():
    """Test metrics summary"""
    metrics = CostMetrics()

    metrics.add_claude_call(1000, 500)
    metrics.add_ollama_call(2000)

    summary = metrics.get_summary()

    assert "total_calls" in summary
    assert summary["total_calls"] == 2
    assert summary["claude_calls"] == 1
    assert summary["ollama_calls"] == 1
    assert "cost_savings_usd" in summary
    assert "cost_reduction_percent" in summary


# ============================================================================
# Test Hybrid Configuration
# ============================================================================

def test_hybrid_config_defaults():
    """Test HybridConfig default values"""
    config = HybridConfig()

    assert config.tier_1_backend == "claude"
    assert config.tier_2_backend == "claude"
    assert config.tier_3_backend == "claude"
    assert config.tier_4_backend == "ollama"
    assert config.fallback_backend == "ollama"
    assert config.cost_optimization_mode == "balanced"


def test_hybrid_config_custom():
    """Test HybridConfig with custom values"""
    config = HybridConfig(
        tier_4_backend="claude",
        max_claude_cost_usd=5.0,
        cost_optimization_mode="quality"
    )

    assert config.tier_4_backend == "claude"
    assert config.max_claude_cost_usd == 5.0
    assert config.cost_optimization_mode == "quality"


# ============================================================================
# Test Hybrid Supervisor
# ============================================================================

@skip_if_no_hybrid
@pytest.mark.asyncio
async def test_hybrid_supervisor_initialization():
    """Test HybridSupervisor initialization"""
    config = HybridConfig()
    metrics = CostMetrics()

    supervisor = HybridSupervisor(
        hybrid_config=config,
        cost_metrics=metrics
    )

    assert supervisor.hybrid_config is not None
    assert supervisor.cost_metrics is not None
    assert len(supervisor.claude_specialists) == 0
    assert len(supervisor.ollama_specialists) == 0


@skip_if_no_hybrid
def test_hybrid_supervisor_register_specialists():
    """Test registering specialists"""
    config = HybridConfig()
    metrics = CostMetrics()

    supervisor = HybridSupervisor(
        hybrid_config=config,
        cost_metrics=metrics
    )

    # Register Ollama specialist
    ollama_agent = create_ollama_specialist_agent(
        agent_type=AgentType.FRONTEND_CODER,
        model="gemma3:1b"
    )
    supervisor.register_ollama_specialist("frontend_coder", ollama_agent)

    assert len(supervisor.ollama_specialists) == 1
    assert "frontend_coder" in supervisor.ollama_specialists


@skip_if_no_hybrid
def test_hybrid_supervisor_routing_balanced():
    """Test routing in balanced mode"""
    config = HybridConfig(cost_optimization_mode="balanced")
    metrics = CostMetrics()

    supervisor = HybridSupervisor(
        hybrid_config=config,
        cost_metrics=metrics
    )

    # Register specialists
    ollama_agent = create_ollama_specialist_agent(
        agent_type=AgentType.FRONTEND_CODER,
        model="gemma3:1b"
    )
    supervisor.register_ollama_specialist("frontend_coder", ollama_agent)

    # Test routing
    context = TaskContext(
        project_id="test-001",
        project_description="Test",
        current_phase="execution"
    )

    backend = supervisor._route_specialist_task(
        "frontend_coder",
        "Generate React component",
        context
    )

    # In balanced mode with tier_4_backend="ollama", should route to Ollama
    assert backend == "ollama"


@skip_if_no_hybrid
def test_hybrid_supervisor_routing_cost_mode():
    """Test routing in cost optimization mode"""
    config = HybridConfig(cost_optimization_mode="cost")
    metrics = CostMetrics()

    supervisor = HybridSupervisor(
        hybrid_config=config,
        cost_metrics=metrics
    )

    context = TaskContext(
        project_id="test-002",
        project_description="Test",
        current_phase="execution"
    )

    backend = supervisor._route_specialist_task(
        "frontend_coder",
        "Generate component",
        context
    )

    # Cost mode should always use Ollama for Tier 4
    assert backend == "ollama"


@skip_if_no_hybrid
def test_hybrid_supervisor_budget_limit():
    """Test budget limit enforcement"""
    config = HybridConfig(max_claude_cost_usd=0.01)  # Very low budget
    metrics = CostMetrics()

    # Simulate going over budget
    metrics.add_claude_call(100000, 50000)  # Large call

    supervisor = HybridSupervisor(
        hybrid_config=config,
        cost_metrics=metrics
    )

    context = TaskContext(
        project_id="test-003",
        project_description="Test",
        current_phase="execution"
    )

    backend = supervisor._route_specialist_task(
        "frontend_coder",
        "Generate component",
        context
    )

    # Should route to Ollama because budget exceeded
    assert backend == "ollama"


# ============================================================================
# Test Hybrid System
# ============================================================================

@skip_if_no_hybrid
@pytest.mark.asyncio
async def test_hybrid_system_initialization():
    """Test HybridPMAgentsSystem initialization"""
    config = HybridConfig(cost_optimization_mode="balanced")

    system = HybridPMAgentsSystem(
        hybrid_config=config,
        log_level="ERROR"  # Suppress logs
    )

    assert system.coordinator is not None
    assert system.planner is not None
    assert system.supervisor is not None
    assert len(system.supervisor.ollama_specialists) == 9


@skip_if_no_hybrid
@pytest.mark.asyncio
async def test_hybrid_system_status():
    """Test system status reporting"""
    config = HybridConfig()

    system = HybridPMAgentsSystem(
        hybrid_config=config,
        log_level="ERROR"
    )

    status = system.get_system_status()

    assert status["mode"] == "hybrid"
    assert "configuration" in status
    assert status["configuration"]["tier_1"] == "claude"
    assert status["configuration"]["tier_4"] == "ollama"
    assert "cost_metrics" in status
    assert "coordinator" in status


@skip_if_no_hybrid
@pytest.mark.asyncio
async def test_hybrid_system_simple_project():
    """Test running a simple project in hybrid mode"""
    config = HybridConfig(
        cost_optimization_mode="balanced",
        max_claude_cost_usd=5.0
    )

    system = HybridPMAgentsSystem(
        hybrid_config=config,
        log_level="ERROR"
    )

    result = await system.run_project(
        project_name="Test Hybrid Project",
        project_description="Build a simple React application",
        project_type="frontend",
        requirements=["React 18+", "TypeScript"]
    )

    assert result is not None
    assert "status" in result
    assert "cost_metrics" in result

    # Check cost metrics
    cost = result["cost_metrics"]
    assert cost["claude_calls"] > 0  # Should have Claude calls for planning
    assert cost["ollama_calls"] >= 0  # May have Ollama calls for execution
    assert cost["total_cost_usd"] >= 0


@skip_if_no_hybrid
@pytest.mark.asyncio
async def test_hybrid_system_cost_optimization():
    """Test that hybrid mode actually saves cost"""
    config = HybridConfig(cost_optimization_mode="balanced")

    system = HybridPMAgentsSystem(
        hybrid_config=config,
        log_level="ERROR"
    )

    result = await system.run_project(
        project_name="Cost Test Project",
        project_description="Test cost optimization",
        project_type="frontend",
        requirements=["React"]
    )

    cost = result["cost_metrics"]

    # Verify we used both backends
    assert cost["claude_calls"] > 0
    assert cost["ollama_calls"] > 0

    # Verify cost savings
    assert cost["cost_savings_usd"] > 0
    assert cost["cost_reduction_percent"] > 0

    # Total cost should be less than if we used only Claude
    total_tokens = cost["claude_tokens"] + cost["ollama_tokens"]
    hypothetical_all_claude_cost = (total_tokens / 1_000_000) * 9.0  # Average cost
    assert cost["total_cost_usd"] < hypothetical_all_claude_cost


# ============================================================================
# Test Different Optimization Modes
# ============================================================================

@skip_if_no_hybrid
@pytest.mark.asyncio
async def test_quality_mode():
    """Test quality optimization mode"""
    config = HybridConfig(cost_optimization_mode="quality")

    system = HybridPMAgentsSystem(
        hybrid_config=config,
        log_level="ERROR"
    )

    status = system.get_system_status()
    assert status["configuration"]["optimization_mode"] == "quality"


@skip_if_no_hybrid
@pytest.mark.asyncio
async def test_cost_mode():
    """Test cost optimization mode"""
    config = HybridConfig(cost_optimization_mode="cost")

    system = HybridPMAgentsSystem(
        hybrid_config=config,
        log_level="ERROR"
    )

    status = system.get_system_status()
    assert status["configuration"]["optimization_mode"] == "cost"


@skip_if_no_hybrid
@pytest.mark.asyncio
async def test_balanced_mode():
    """Test balanced optimization mode"""
    config = HybridConfig(cost_optimization_mode="balanced")

    system = HybridPMAgentsSystem(
        hybrid_config=config,
        log_level="ERROR"
    )

    status = system.get_system_status()
    assert status["configuration"]["optimization_mode"] == "balanced"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    if not HYBRID_AVAILABLE:
        print("⚠️  Hybrid mode unavailable:")
        if not ANTHROPIC_AVAILABLE:
            print("   - Anthropic API key not set (export ANTHROPIC_API_KEY)")
        if not OLLAMA_AVAILABLE:
            print("   - Ollama not running (run 'ollama serve')")
        print("\nPlease fix the above issues and re-run tests.")
        sys.exit(1)

    print("Running Hybrid PM-Agents integration tests...")
    print("=" * 70)

    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
