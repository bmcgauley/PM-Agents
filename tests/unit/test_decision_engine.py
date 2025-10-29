"""
Unit tests for DecisionEngine
"""

import pytest
from src.core.decision_engine import DecisionEngine, Decision


def test_request_acceptance_valid():
    """Test accepting a valid request"""
    engine = DecisionEngine()

    result = engine.accept_request(
        user_request="Create a React Next.js application with authentication",
        context={"project_path": "/home/user/project"},
        preferences={"max_budget_tokens": 50000}
    )

    assert result.decision == Decision.ACCEPT
    assert result.confidence > 0.9
    assert "frontend" in result.metadata.get("project_type", "")


def test_request_rejection_safety():
    """Test rejecting unsafe request"""
    engine = DecisionEngine()

    result = engine.accept_request(
        user_request="Create a malware keylogger application",
        context={},
        preferences={"max_budget_tokens": 50000}
    )

    assert result.decision == Decision.REJECT
    assert "safety" in result.rationale.lower()


def test_request_rejection_budget():
    """Test rejecting request that exceeds budget"""
    engine = DecisionEngine()

    result = engine.accept_request(
        user_request="Create a comprehensive fullstack application with ML backend",
        context={},
        preferences={"max_budget_tokens": 1000}  # Very low budget
    )

    assert result.decision == Decision.REJECT
    assert "budget" in result.rationale.lower() or "token" in result.rationale.lower()


def test_request_clarification():
    """Test requesting clarification for ambiguous request"""
    engine = DecisionEngine()

    result = engine.accept_request(
        user_request="Build app",  # Too vague
        context={},
        preferences={"max_budget_tokens": 50000}
    )

    assert result.decision == Decision.CLARIFY
    assert len(result.required_actions) > 0


def test_project_type_detection_frontend():
    """Test frontend project type detection"""
    engine = DecisionEngine()

    project_type = engine._detect_project_type(
        "Create a React application with Next.js",
        {}
    )

    assert project_type == "frontend"


def test_project_type_detection_ml():
    """Test ML project type detection"""
    engine = DecisionEngine()

    project_type = engine._detect_project_type(
        "Train a PyTorch neural network model",
        {}
    )

    assert project_type == "ml"


def test_phase_gate_go_decision():
    """Test GO decision at phase gate"""
    engine = DecisionEngine()

    phase_outputs = {
        "deliverables": [
            {"type": "feasibility_assessment", "content": "Complete"},
            {"type": "scope_definition", "content": "Complete"},
            {"type": "stakeholder_identification", "content": "Complete"},
            {"type": "initial_risk_assessment", "content": "Complete"},
            {"type": "documentation", "content": "Complete"}
        ],
        "risks": [],
        "issues": []
    }

    project_state = {
        "risks": [],
        "blockers": [],
        "tokens_remaining": 30000
    }

    result = engine.phase_gate_decision(
        phase="initiation",
        phase_outputs=phase_outputs,
        project_state=project_state
    )

    assert result.decision == Decision.GO
    assert result.metadata["score"] >= 70


def test_phase_gate_no_go_critical_blocker():
    """Test NO_GO decision with critical blocker"""
    engine = DecisionEngine()

    phase_outputs = {
        "deliverables": [{"type": "test", "content": "test"}],
        "risks": [],
        "issues": []
    }

    project_state = {
        "risks": [],
        "blockers": [{
            "severity": "critical",
            "status": "unresolved",
            "description": "Cannot proceed"
        }],
        "tokens_remaining": 30000
    }

    result = engine.phase_gate_decision(
        phase="planning",
        phase_outputs=phase_outputs,
        project_state=project_state
    )

    assert result.decision == Decision.NO_GO
    assert "blocker" in result.rationale.lower()


def test_phase_gate_no_go_insufficient_tokens():
    """Test NO_GO decision with insufficient tokens"""
    engine = DecisionEngine()

    phase_outputs = {
        "deliverables": [{"type": "test", "content": "test"}],
        "risks": [],
        "issues": []
    }

    project_state = {
        "risks": [],
        "blockers": [],
        "tokens_remaining": 100  # Too low
    }

    result = engine.phase_gate_decision(
        phase="execution",
        phase_outputs=phase_outputs,
        project_state=project_state
    )

    assert result.decision == Decision.NO_GO
    assert "token" in result.rationale.lower()


def test_escalation_handling_technical_blocker():
    """Test handling technical blocker escalation"""
    engine = DecisionEngine()

    escalation = {
        "type": "technical_blocker",
        "severity": "critical",
        "description": "Cannot access database"
    }

    response = engine.handle_escalation(escalation)

    assert response["action"] == "pause_and_ask_user"
    assert "critical" in response["message"].lower() or "blocker" in response["message"].lower()


def test_escalation_handling_safety_concern():
    """Test handling safety concern escalation"""
    engine = DecisionEngine()

    escalation = {
        "type": "safety_concern",
        "severity": "critical",
        "description": "Potential security vulnerability detected"
    }

    response = engine.handle_escalation(escalation)

    assert response["action"] == "terminate_and_report"
    assert response.get("priority") == "critical"


def test_resource_estimation():
    """Test resource estimation"""
    engine = DecisionEngine()

    resources = engine._estimate_resources(
        "Create a simple frontend application",
        "frontend"
    )

    assert "tokens" in resources
    assert "estimated_time_seconds" in resources
    assert "estimated_cost_usd" in resources
    assert resources["tokens"] > 0


def test_quality_assessment():
    """Test quality assessment"""
    engine = DecisionEngine()

    # Good quality
    phase_outputs = {
        "deliverables": [
            {"type": "code", "content": "..."},
            {"type": "documentation", "content": "..."},
            {"type": "test", "content": "..."}
        ],
        "issues": []
    }

    quality = engine._assess_quality(phase_outputs)
    assert quality >= 75


    # Poor quality
    phase_outputs_bad = {
        "deliverables": [{"type": "code", "content": "..."}],
        "issues": [
            {"severity": "critical"},
            {"severity": "critical"}
        ]
    }

    quality_bad = engine._assess_quality(phase_outputs_bad)
    assert quality_bad < quality


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
