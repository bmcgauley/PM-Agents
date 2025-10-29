"""
Project State Management
Tracks complete project state including progress, resources, risks, issues, and decisions
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


@dataclass
class ProjectState:
    """
    Complete project state tracking
    Based on COORDINATOR_AGENT_SPEC.md state management requirements
    """

    # Identity
    request_id: str
    project_name: str
    project_description: str
    project_type: str  # frontend|backend|ml|analytics|fullstack|research

    # Status
    status: str = "pending"  # pending|in_progress|completed|failed|blocked
    phase: str = "initiation"  # initiation|planning|execution|monitoring|closure

    # Progress tracking
    progress_percentage: int = 0  # 0-100
    tasks_completed: int = 0
    tasks_remaining: int = 0
    start_time: Optional[str] = None
    last_update_time: Optional[str] = None

    # Resource tracking
    tokens_budget: int = 50000
    tokens_used: int = 0
    tokens_remaining: int = 50000
    api_calls: int = 0
    cost_usd: float = 0.0

    # Plan and outputs
    plan: Dict[str, Any] = field(default_factory=dict)
    phase_outputs: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {
        "initiation": [],
        "planning": [],
        "execution": [],
        "monitoring": [],
        "closure": []
    })
    deliverables: List[Dict[str, Any]] = field(default_factory=list)

    # Risk and issue tracking
    risks: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    blockers: List[Dict[str, Any]] = field(default_factory=list)

    # Agent communication
    messages: List[Dict[str, Any]] = field(default_factory=list)
    active_agents: List[str] = field(default_factory=list)

    # Decisions
    go_decisions: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if not self.start_time:
            self.start_time = datetime.now().isoformat()
        if not self.last_update_time:
            self.last_update_time = datetime.now().isoformat()

    def update_progress(self, tasks_completed: Optional[int] = None, tasks_remaining: Optional[int] = None):
        """Update progress tracking"""
        if tasks_completed is not None:
            self.tasks_completed = tasks_completed
        if tasks_remaining is not None:
            self.tasks_remaining = tasks_remaining

        # Calculate progress percentage
        total_tasks = self.tasks_completed + self.tasks_remaining
        if total_tasks > 0:
            self.progress_percentage = int((self.tasks_completed / total_tasks) * 100)

        self.last_update_time = datetime.now().isoformat()

    def add_deliverable(self, deliverable: Dict[str, Any]):
        """Add a deliverable"""
        self.deliverables.append({
            **deliverable,
            "timestamp": datetime.now().isoformat()
        })
        self.last_update_time = datetime.now().isoformat()

    def add_risk(self, risk: Dict[str, Any]):
        """Add a risk"""
        self.risks.append({
            **risk,
            "identified_at": datetime.now().isoformat()
        })
        self.last_update_time = datetime.now().isoformat()

    def add_issue(self, issue: Dict[str, Any]):
        """Add an issue"""
        self.issues.append({
            **issue,
            "reported_at": datetime.now().isoformat()
        })
        self.last_update_time = datetime.now().isoformat()

    def add_blocker(self, blocker: Dict[str, Any]):
        """Add a blocker"""
        self.blockers.append({
            **blocker,
            "blocked_at": datetime.now().isoformat()
        })
        self.status = "blocked"
        self.last_update_time = datetime.now().isoformat()

    def resolve_blocker(self, blocker_index: int):
        """Resolve a blocker"""
        if 0 <= blocker_index < len(self.blockers):
            self.blockers[blocker_index]["resolved_at"] = datetime.now().isoformat()
            self.blockers[blocker_index]["status"] = "resolved"

            # If no more unresolved blockers, change status back
            unresolved = [b for b in self.blockers if b.get("status") != "resolved"]
            if not unresolved:
                self.status = "in_progress"

        self.last_update_time = datetime.now().isoformat()

    def add_phase_output(self, phase: str, output: Dict[str, Any]):
        """Add output for a specific phase"""
        if phase not in self.phase_outputs:
            self.phase_outputs[phase] = []

        self.phase_outputs[phase].append({
            **output,
            "timestamp": datetime.now().isoformat()
        })
        self.last_update_time = datetime.now().isoformat()

    def record_phase_gate_decision(self, phase: str, decision: str, score: float, notes: str):
        """Record a phase gate decision"""
        self.go_decisions[phase] = {
            "decision": decision,  # GO|CONDITIONAL_GO|NO_GO
            "score": score,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }

        if decision == "GO":
            self.advance_phase()

        self.last_update_time = datetime.now().isoformat()

    def advance_phase(self):
        """Move to next phase"""
        phases = ["initiation", "planning", "execution", "monitoring", "closure"]
        try:
            current_index = phases.index(self.phase)
            if current_index < len(phases) - 1:
                self.phase = phases[current_index + 1]
            else:
                self.status = "completed"
        except ValueError:
            pass

        self.last_update_time = datetime.now().isoformat()

    def update_token_usage(self, tokens: int, cost: float):
        """Update resource usage"""
        self.tokens_used += tokens
        self.tokens_remaining = max(0, self.tokens_budget - self.tokens_used)
        self.cost_usd += cost
        self.api_calls += 1
        self.last_update_time = datetime.now().isoformat()

    def add_message(self, message: Dict[str, Any]):
        """Record A2A message"""
        self.messages.append({
            **message,
            "recorded_at": datetime.now().isoformat()
        })

    def register_agent(self, agent_id: str):
        """Register an active agent"""
        if agent_id not in self.active_agents:
            self.active_agents.append(agent_id)

    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.active_agents:
            self.active_agents.remove(agent_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectState':
        """Deserialize state from dictionary"""
        return cls(**data)

    def save(self, path: str):
        """Persist state to disk"""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'ProjectState':
        """Load state from disk"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_summary(self) -> Dict[str, Any]:
        """Get concise state summary"""
        return {
            "project_name": self.project_name,
            "status": self.status,
            "phase": self.phase,
            "progress": f"{self.progress_percentage}%",
            "tasks": f"{self.tasks_completed}/{self.tasks_completed + self.tasks_remaining}",
            "tokens": f"{self.tokens_used}/{self.tokens_budget}",
            "cost": f"${self.cost_usd:.2f}",
            "risks": len([r for r in self.risks if r.get("severity") in ["high", "critical"]]),
            "issues": len([i for i in self.issues if i.get("severity") in ["high", "critical"]]),
            "blockers": len([b for b in self.blockers if b.get("status") != "resolved"])
        }

    def is_healthy(self) -> bool:
        """Check if project is in healthy state"""
        # Check for critical blockers
        if any(b.get("severity") == "critical" and b.get("status") != "resolved" for b in self.blockers):
            return False

        # Check token budget
        if self.tokens_remaining < (self.tokens_budget * 0.1):  # Less than 10% remaining
            return False

        # Check for critical unresolved issues
        critical_issues = [i for i in self.issues
                           if i.get("severity") == "critical" and i.get("status") != "resolved"]
        if len(critical_issues) > 2:
            return False

        return True

    def get_phase_completion(self, phase: str) -> float:
        """Get completion percentage for a specific phase"""
        outputs = self.phase_outputs.get(phase, [])
        decision = self.go_decisions.get(phase, {})

        if decision.get("decision") == "GO":
            return 100.0
        elif outputs:
            return 50.0  # Phase in progress
        else:
            return 0.0  # Phase not started
