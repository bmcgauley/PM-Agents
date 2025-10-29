"""
Unit tests for ProjectState class
"""

import pytest
from src.core.project_state import ProjectState


def test_project_state_creation():
    """Test basic project state creation"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test Project",
        project_description="A test project",
        project_type="frontend"
    )

    assert state.request_id == "test-123"
    assert state.project_name == "Test Project"
    assert state.status == "pending"
    assert state.phase == "initiation"
    assert state.progress_percentage == 0


def test_update_progress():
    """Test progress tracking"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test",
        project_description="Test",
        project_type="frontend"
    )

    state.update_progress(tasks_completed=5, tasks_remaining=5)

    assert state.tasks_completed == 5
    assert state.tasks_remaining == 5
    assert state.progress_percentage == 50


def test_add_deliverable():
    """Test adding deliverables"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test",
        project_description="Test",
        project_type="frontend"
    )

    state.add_deliverable({
        "type": "documentation",
        "name": "README.md",
        "content": "Test content"
    })

    assert len(state.deliverables) == 1
    assert state.deliverables[0]["type"] == "documentation"
    assert "timestamp" in state.deliverables[0]


def test_phase_advancement():
    """Test phase advancement"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test",
        project_description="Test",
        project_type="frontend"
    )

    assert state.phase == "initiation"

    state.advance_phase()
    assert state.phase == "planning"

    state.advance_phase()
    assert state.phase == "execution"


def test_blocker_management():
    """Test blocker tracking"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test",
        project_description="Test",
        project_type="frontend"
    )

    state.add_blocker({
        "severity": "critical",
        "description": "API key missing"
    })

    assert state.status == "blocked"
    assert len(state.blockers) == 1

    state.resolve_blocker(0)
    assert state.blockers[0]["status"] == "resolved"
    assert state.status == "in_progress"


def test_token_usage_tracking():
    """Test token usage tracking"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test",
        project_description="Test",
        project_type="frontend",
        tokens_budget=10000
    )

    state.update_token_usage(tokens=500, cost=0.015)

    assert state.tokens_used == 500
    assert state.tokens_remaining == 9500
    assert state.cost_usd == 0.015
    assert state.api_calls == 1


def test_phase_gate_decision():
    """Test phase gate decision recording"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test",
        project_description="Test",
        project_type="frontend"
    )

    state.record_phase_gate_decision(
        phase="initiation",
        decision="GO",
        score=85.0,
        notes="All criteria met"
    )

    assert "initiation" in state.go_decisions
    assert state.go_decisions["initiation"]["decision"] == "GO"
    assert state.go_decisions["initiation"]["score"] == 85.0
    assert state.phase == "planning"  # Should advance on GO


def test_health_check():
    """Test project health check"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test",
        project_description="Test",
        project_type="frontend",
        tokens_budget=10000
    )

    # Healthy state
    assert state.is_healthy() is True

    # Add critical blocker
    state.add_blocker({
        "severity": "critical",
        "description": "Critical issue"
    })

    assert state.is_healthy() is False


def test_serialization():
    """Test state serialization/deserialization"""
    state = ProjectState(
        request_id="test-123",
        project_name="Test",
        project_description="Test",
        project_type="frontend"
    )

    state.add_deliverable({"type": "code", "content": "test"})

    # Serialize
    data = state.to_dict()
    assert isinstance(data, dict)
    assert data["request_id"] == "test-123"

    # Deserialize
    restored = ProjectState.from_dict(data)
    assert restored.request_id == state.request_id
    assert len(restored.deliverables) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
