# Project State Management Specification

## Overview

This document defines the **Project State Management** system for PM-Agents, providing persistent, recoverable, and observable state tracking across the entire project lifecycle. The system maintains comprehensive state information for all agents, tasks, deliverables, and decisions throughout PMBOK phases (Initiation → Planning → Execution → Monitoring → Closure).

### Purpose

- **Persistence**: Store project state across agent restarts and system interruptions
- **Recovery**: Resume work seamlessly after failures or interruptions
- **Observability**: Provide real-time visibility into project progress and status
- **Audit Trail**: Maintain complete history of decisions, changes, and events
- **Coordination**: Enable agents to share state and avoid conflicts

---

## State Architecture

### State Layers

```
┌─────────────────────────────────────────────────────────────┐
│              User Interface / Dashboard                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│            State Query & Visualization Layer                │
│  (Real-time queries, aggregations, status reports)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Application State Layer (In-Memory)             │
│  (Agent states, active tasks, message buffers, caches)      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│          Persistence Layer (SQLite + JSON + Redis)          │
│  (Project state, task history, deliverables, decisions)     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   File System Storage                        │
│  (Database files, JSON snapshots, logs, deliverables)       │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema (SQLite)

### Why SQLite?

- **Zero configuration**: Embedded database, no server required
- **Reliable**: ACID compliant, battle-tested
- **Portable**: Single file database, easy to backup/share
- **Fast**: Sufficient for PM-Agents scale (hundreds of tasks)
- **SQL queries**: Rich querying capabilities for state analysis

### Schema Design

```sql
-- ============================================================================
-- Projects Table
-- ============================================================================
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    project_type TEXT NOT NULL,  -- frontend, backend, ml, analytics, fullstack
    current_phase TEXT NOT NULL,  -- initiation, planning, execution, monitoring, closure
    status TEXT NOT NULL,  -- active, paused, completed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSON,  -- User preferences, tech stack, etc.

    CHECK (project_type IN ('frontend', 'backend', 'ml', 'analytics', 'fullstack')),
    CHECK (current_phase IN ('initiation', 'planning', 'execution', 'monitoring', 'closure')),
    CHECK (status IN ('active', 'paused', 'completed', 'failed'))
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_phase ON projects(current_phase);

-- ============================================================================
-- Tasks Table
-- ============================================================================
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    parent_task_id TEXT,  -- For subtasks
    task_type TEXT NOT NULL,  -- code_generation, research, validation, etc.
    description TEXT NOT NULL,
    status TEXT NOT NULL,  -- queued, in_progress, paused, completed, failed
    priority TEXT NOT NULL,  -- critical, high, normal, low
    assigned_agent_id TEXT,
    assigned_agent_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    deadline TIMESTAMP,
    progress_percent INTEGER DEFAULT 0,
    estimated_duration_seconds INTEGER,
    actual_duration_seconds INTEGER,
    retry_count INTEGER DEFAULT 0,
    metadata JSON,  -- Requirements, context, config

    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    CHECK (status IN ('queued', 'in_progress', 'paused', 'completed', 'failed')),
    CHECK (priority IN ('critical', 'high', 'normal', 'low')),
    CHECK (progress_percent BETWEEN 0 AND 100)
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_agent ON tasks(assigned_agent_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);

-- ============================================================================
-- Task Dependencies Table
-- ============================================================================
CREATE TABLE task_dependencies (
    dependency_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    dependency_type TEXT NOT NULL,  -- blocks, requires, optional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    CHECK (dependency_type IN ('blocks', 'requires', 'optional')),
    UNIQUE(task_id, depends_on_task_id)
);

CREATE INDEX idx_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_deps_depends_on ON task_dependencies(depends_on_task_id);

-- ============================================================================
-- Deliverables Table
-- ============================================================================
CREATE TABLE deliverables (
    deliverable_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id TEXT,
    deliverable_type TEXT NOT NULL,  -- file, code, documentation, report, artifact
    name TEXT NOT NULL,
    file_path TEXT,
    content TEXT,  -- Or reference to file storage
    content_hash TEXT,  -- SHA-256 for deduplication
    size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_agent_id TEXT,
    metadata JSON,

    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE SET NULL,
    CHECK (deliverable_type IN ('file', 'code', 'documentation', 'report', 'artifact'))
);

CREATE INDEX idx_deliverables_project ON deliverables(project_id);
CREATE INDEX idx_deliverables_task ON deliverables(task_id);
CREATE INDEX idx_deliverables_type ON deliverables(deliverable_type);

-- ============================================================================
-- Agents Table
-- ============================================================================
CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    agent_type TEXT NOT NULL,  -- Coordinator, Planner, Supervisor, Specialist
    agent_name TEXT NOT NULL,
    specialist_type TEXT,  -- For specialists: SpecKit, FrontendCoder, etc.
    status TEXT NOT NULL,  -- active, inactive, degraded, failed
    current_task_id TEXT,
    load_percent INTEGER DEFAULT 0,
    total_tasks_completed INTEGER DEFAULT 0,
    total_tasks_failed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,

    FOREIGN KEY (current_task_id) REFERENCES tasks(task_id) ON DELETE SET NULL,
    CHECK (agent_type IN ('Coordinator', 'Planner', 'Supervisor', 'Specialist')),
    CHECK (status IN ('active', 'inactive', 'degraded', 'failed')),
    CHECK (load_percent BETWEEN 0 AND 100)
);

CREATE INDEX idx_agents_type ON agents(agent_type);
CREATE INDEX idx_agents_status ON agents(status);

-- ============================================================================
-- Phase Gates Table
-- ============================================================================
CREATE TABLE phase_gates (
    gate_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    gate_number INTEGER NOT NULL,  -- 1-5
    from_phase TEXT NOT NULL,
    to_phase TEXT NOT NULL,
    decision TEXT NOT NULL,  -- GO, CONDITIONAL_GO, NO_GO
    overall_score REAL NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evaluated_by_agent_id TEXT,
    criteria_scores JSON NOT NULL,  -- {"charter": 85.0, "risks": 80.0, ...}
    critical_issues JSON,
    required_actions JSON,
    recommendations JSON,

    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    CHECK (gate_number BETWEEN 1 AND 5),
    CHECK (decision IN ('GO', 'CONDITIONAL_GO', 'NO_GO')),
    CHECK (overall_score BETWEEN 0 AND 100)
);

CREATE INDEX idx_gates_project ON phase_gates(project_id);
CREATE INDEX idx_gates_number ON phase_gates(gate_number);

-- ============================================================================
-- Decisions Table (Audit Trail)
-- ============================================================================
CREATE TABLE decisions (
    decision_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id TEXT,
    decision_type TEXT NOT NULL,  -- agent_selection, approach, escalation, retry, abort
    decision TEXT NOT NULL,
    rationale TEXT,
    made_by_agent_id TEXT NOT NULL,
    made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    impact TEXT,  -- high, medium, low
    metadata JSON,

    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    CHECK (decision_type IN ('agent_selection', 'approach', 'escalation', 'retry', 'abort')),
    CHECK (impact IN ('high', 'medium', 'low'))
);

CREATE INDEX idx_decisions_project ON decisions(project_id);
CREATE INDEX idx_decisions_task ON decisions(task_id);
CREATE INDEX idx_decisions_agent ON decisions(made_by_agent_id);

-- ============================================================================
-- Events Table (Activity Log)
-- ============================================================================
CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id TEXT,
    event_type TEXT NOT NULL,  -- task_created, task_started, task_completed, error, message_sent, etc.
    event_data JSON NOT NULL,
    severity TEXT NOT NULL,  -- info, warning, error, critical
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_id TEXT,

    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    CHECK (severity IN ('info', 'warning', 'error', 'critical'))
);

CREATE INDEX idx_events_project ON events(project_id);
CREATE INDEX idx_events_task ON events(task_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_timestamp ON events(occurred_at);

-- ============================================================================
-- Metrics Table (Performance Tracking)
-- ============================================================================
CREATE TABLE metrics (
    metric_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id TEXT,
    agent_id TEXT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,

    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX idx_metrics_project ON metrics(project_id);
CREATE INDEX idx_metrics_name ON metrics(metric_name);
CREATE INDEX idx_metrics_timestamp ON metrics(recorded_at);

-- ============================================================================
-- State Snapshots Table (Point-in-Time Recovery)
-- ============================================================================
CREATE TABLE state_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    snapshot_type TEXT NOT NULL,  -- manual, automatic, pre_gate, checkpoint
    snapshot_data JSON NOT NULL,  -- Full project state
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_agent_id TEXT,
    notes TEXT,

    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    CHECK (snapshot_type IN ('manual', 'automatic', 'pre_gate', 'checkpoint'))
);

CREATE INDEX idx_snapshots_project ON state_snapshots(project_id);
CREATE INDEX idx_snapshots_timestamp ON state_snapshots(created_at);
```

---

## State Manager Implementation

### Python State Manager Class

```python
# state_manager.py
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from contextlib import contextmanager

class ProjectStateManager:
    """
    Manages persistent project state using SQLite.

    Features:
    - ACID transactions for state consistency
    - Automatic snapshots at critical points
    - State recovery after interruptions
    - Query interface for state inspection
    """

    def __init__(self, db_path: str = "pm_agents_state.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self._initialize_database()

    def _initialize_database(self):
        """Create database schema if not exists."""
        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        self.connection.row_factory = sqlite3.Row

        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")

        # Execute schema creation
        with open("schema.sql", "r") as f:
            self.connection.executescript(f.read())

    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self.connection
        try:
            conn.execute("BEGIN")
            yield conn
            conn.execute("COMMIT")
        except Exception as e:
            conn.execute("ROLLBACK")
            raise e

    # ========================================================================
    # Project Operations
    # ========================================================================

    def create_project(
        self,
        name: str,
        description: str,
        project_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create a new project.

        Returns:
            project_id: UUID of created project
        """
        project_id = str(uuid.uuid4())

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO projects (
                    project_id, name, description, project_type,
                    current_phase, status, metadata
                )
                VALUES (?, ?, ?, ?, 'initiation', 'active', ?)
            """, (
                project_id,
                name,
                description,
                project_type,
                json.dumps(metadata or {})
            ))

        # Log event
        self.log_event(
            project_id=project_id,
            event_type="project_created",
            event_data={"name": name, "type": project_type},
            severity="info"
        )

        return project_id

    def update_project_phase(
        self,
        project_id: str,
        new_phase: str
    ):
        """Update project phase after gate approval."""
        with self.transaction() as conn:
            conn.execute("""
                UPDATE projects
                SET current_phase = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE project_id = ?
            """, (new_phase, project_id))

        self.log_event(
            project_id=project_id,
            event_type="phase_changed",
            event_data={"new_phase": new_phase},
            severity="info"
        )

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Retrieve project by ID."""
        cursor = self.connection.execute("""
            SELECT *
            FROM projects
            WHERE project_id = ?
        """, (project_id,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_projects(
        self,
        status: Optional[str] = None,
        phase: Optional[str] = None
    ) -> List[Dict]:
        """List projects with optional filters."""
        query = "SELECT * FROM projects WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if phase:
            query += " AND current_phase = ?"
            params.append(phase)

        query += " ORDER BY updated_at DESC"

        cursor = self.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Task Operations
    # ========================================================================

    def create_task(
        self,
        project_id: str,
        task_type: str,
        description: str,
        priority: str = "normal",
        parent_task_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Create a new task."""
        task_id = str(uuid.uuid4())

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO tasks (
                    task_id, project_id, parent_task_id, task_type,
                    description, status, priority, metadata
                )
                VALUES (?, ?, ?, ?, ?, 'queued', ?, ?)
            """, (
                task_id,
                project_id,
                parent_task_id,
                task_type,
                description,
                priority,
                json.dumps(metadata or {})
            ))

        self.log_event(
            project_id=project_id,
            task_id=task_id,
            event_type="task_created",
            event_data={"type": task_type, "priority": priority},
            severity="info"
        )

        return task_id

    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress_percent: Optional[int] = None
    ):
        """Update task status and progress."""
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]

        if status == "in_progress":
            updates.append("started_at = CURRENT_TIMESTAMP")
        elif status in ("completed", "failed"):
            updates.append("completed_at = CURRENT_TIMESTAMP")

        if progress_percent is not None:
            updates.append("progress_percent = ?")
            params.append(progress_percent)

        params.append(task_id)

        with self.transaction() as conn:
            conn.execute(f"""
                UPDATE tasks
                SET {', '.join(updates)}
                WHERE task_id = ?
            """, params)

        # Get project_id for event logging
        task = self.get_task(task_id)
        if task:
            self.log_event(
                project_id=task['project_id'],
                task_id=task_id,
                event_type=f"task_{status}",
                event_data={"status": status, "progress": progress_percent},
                severity="info"
            )

    def assign_task(
        self,
        task_id: str,
        agent_id: str,
        agent_type: str
    ):
        """Assign task to an agent."""
        with self.transaction() as conn:
            conn.execute("""
                UPDATE tasks
                SET assigned_agent_id = ?,
                    assigned_agent_type = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            """, (agent_id, agent_type, task_id))

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Retrieve task by ID."""
        cursor = self.connection.execute("""
            SELECT *
            FROM tasks
            WHERE task_id = ?
        """, (task_id,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_project_tasks(
        self,
        project_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get all tasks for a project."""
        query = "SELECT * FROM tasks WHERE project_id = ?"
        params = [project_id]

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor = self.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def add_task_dependency(
        self,
        task_id: str,
        depends_on_task_id: str,
        dependency_type: str = "requires"
    ):
        """Add dependency between tasks."""
        dependency_id = str(uuid.uuid4())

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO task_dependencies (
                    dependency_id, task_id, depends_on_task_id, dependency_type
                )
                VALUES (?, ?, ?, ?)
            """, (dependency_id, task_id, depends_on_task_id, dependency_type))

    def get_task_dependencies(self, task_id: str) -> List[Dict]:
        """Get all dependencies for a task."""
        cursor = self.connection.execute("""
            SELECT td.*, t.description, t.status
            FROM task_dependencies td
            JOIN tasks t ON td.depends_on_task_id = t.task_id
            WHERE td.task_id = ?
        """, (task_id,))

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Deliverable Operations
    # ========================================================================

    def create_deliverable(
        self,
        project_id: str,
        task_id: Optional[str],
        deliverable_type: str,
        name: str,
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        created_by_agent_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Create a new deliverable."""
        deliverable_id = str(uuid.uuid4())

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO deliverables (
                    deliverable_id, project_id, task_id, deliverable_type,
                    name, file_path, content, created_by_agent_id, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deliverable_id,
                project_id,
                task_id,
                deliverable_type,
                name,
                file_path,
                content,
                created_by_agent_id,
                json.dumps(metadata or {})
            ))

        return deliverable_id

    def get_project_deliverables(
        self,
        project_id: str,
        deliverable_type: Optional[str] = None
    ) -> List[Dict]:
        """Get all deliverables for a project."""
        query = "SELECT * FROM deliverables WHERE project_id = ?"
        params = [project_id]

        if deliverable_type:
            query += " AND deliverable_type = ?"
            params.append(deliverable_type)

        query += " ORDER BY created_at DESC"

        cursor = self.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Agent Operations
    # ========================================================================

    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        agent_name: str,
        specialist_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Register a new agent."""
        with self.transaction() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agents (
                    agent_id, agent_type, agent_name, specialist_type,
                    status, metadata, last_heartbeat
                )
                VALUES (?, ?, ?, ?, 'active', ?, CURRENT_TIMESTAMP)
            """, (
                agent_id,
                agent_type,
                agent_name,
                specialist_type,
                json.dumps(metadata or {})
            ))

    def update_agent_heartbeat(self, agent_id: str):
        """Update agent's last heartbeat timestamp."""
        with self.transaction() as conn:
            conn.execute("""
                UPDATE agents
                SET last_heartbeat = CURRENT_TIMESTAMP
                WHERE agent_id = ?
            """, (agent_id,))

    def update_agent_status(
        self,
        agent_id: str,
        status: str,
        current_task_id: Optional[str] = None
    ):
        """Update agent status and current task."""
        with self.transaction() as conn:
            conn.execute("""
                UPDATE agents
                SET status = ?,
                    current_task_id = ?,
                    last_heartbeat = CURRENT_TIMESTAMP
                WHERE agent_id = ?
            """, (status, current_task_id, agent_id))

    def get_active_agents(self) -> List[Dict]:
        """Get all active agents."""
        cursor = self.connection.execute("""
            SELECT *
            FROM agents
            WHERE status = 'active'
            ORDER BY agent_type, agent_name
        """)

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Phase Gate Operations
    # ========================================================================

    def record_phase_gate(
        self,
        project_id: str,
        gate_number: int,
        from_phase: str,
        to_phase: str,
        decision: str,
        overall_score: float,
        criteria_scores: Dict,
        critical_issues: Optional[List] = None,
        required_actions: Optional[List] = None,
        recommendations: Optional[List] = None,
        evaluated_by_agent_id: Optional[str] = None
    ) -> str:
        """Record phase gate evaluation."""
        gate_id = str(uuid.uuid4())

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO phase_gates (
                    gate_id, project_id, gate_number, from_phase, to_phase,
                    decision, overall_score, evaluated_by_agent_id,
                    criteria_scores, critical_issues, required_actions,
                    recommendations
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gate_id,
                project_id,
                gate_number,
                from_phase,
                to_phase,
                decision,
                overall_score,
                evaluated_by_agent_id,
                json.dumps(criteria_scores),
                json.dumps(critical_issues or []),
                json.dumps(required_actions or []),
                json.dumps(recommendations or [])
            ))

        self.log_event(
            project_id=project_id,
            event_type="phase_gate_evaluated",
            event_data={
                "gate_number": gate_number,
                "decision": decision,
                "score": overall_score
            },
            severity="info" if decision == "GO" else "warning"
        )

        return gate_id

    def get_project_phase_gates(self, project_id: str) -> List[Dict]:
        """Get all phase gate evaluations for a project."""
        cursor = self.connection.execute("""
            SELECT *
            FROM phase_gates
            WHERE project_id = ?
            ORDER BY gate_number ASC
        """, (project_id,))

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Decision Logging
    # ========================================================================

    def log_decision(
        self,
        project_id: str,
        decision_type: str,
        decision: str,
        rationale: str,
        made_by_agent_id: str,
        task_id: Optional[str] = None,
        impact: str = "medium",
        metadata: Optional[Dict] = None
    ) -> str:
        """Log a decision made by an agent."""
        decision_id = str(uuid.uuid4())

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO decisions (
                    decision_id, project_id, task_id, decision_type,
                    decision, rationale, made_by_agent_id, impact, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision_id,
                project_id,
                task_id,
                decision_type,
                decision,
                rationale,
                made_by_agent_id,
                impact,
                json.dumps(metadata or {})
            ))

        return decision_id

    # ========================================================================
    # Event Logging
    # ========================================================================

    def log_event(
        self,
        project_id: str,
        event_type: str,
        event_data: Dict,
        severity: str = "info",
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        """Log an event."""
        event_id = str(uuid.uuid4())

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO events (
                    event_id, project_id, task_id, event_type,
                    event_data, severity, agent_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                project_id,
                task_id,
                event_type,
                json.dumps(event_data),
                severity,
                agent_id
            ))

    def get_project_events(
        self,
        project_id: str,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get events for a project."""
        query = "SELECT * FROM events WHERE project_id = ?"
        params = [project_id]

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY occurred_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Metrics Operations
    # ========================================================================

    def record_metric(
        self,
        project_id: str,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Record a performance metric."""
        metric_id = str(uuid.uuid4())

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO metrics (
                    metric_id, project_id, task_id, agent_id,
                    metric_name, metric_value, metric_unit, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric_id,
                project_id,
                task_id,
                agent_id,
                metric_name,
                metric_value,
                metric_unit,
                json.dumps(metadata or {})
            ))

    def get_project_metrics(
        self,
        project_id: str,
        metric_name: Optional[str] = None
    ) -> List[Dict]:
        """Get metrics for a project."""
        query = "SELECT * FROM metrics WHERE project_id = ?"
        params = [project_id]

        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)

        query += " ORDER BY recorded_at DESC"

        cursor = self.connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # State Snapshots (Point-in-Time Recovery)
    # ========================================================================

    def create_snapshot(
        self,
        project_id: str,
        snapshot_type: str = "automatic",
        created_by_agent_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Create a full project state snapshot."""
        snapshot_id = str(uuid.uuid4())

        # Collect full project state
        snapshot_data = {
            'project': self.get_project(project_id),
            'tasks': self.get_project_tasks(project_id),
            'deliverables': self.get_project_deliverables(project_id),
            'phase_gates': self.get_project_phase_gates(project_id),
            'agents': self.get_active_agents(),
            'timestamp': datetime.utcnow().isoformat()
        }

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO state_snapshots (
                    snapshot_id, project_id, snapshot_type,
                    snapshot_data, created_by_agent_id, notes
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                project_id,
                snapshot_type,
                json.dumps(snapshot_data),
                created_by_agent_id,
                notes
            ))

        return snapshot_id

    def restore_snapshot(self, snapshot_id: str):
        """Restore project state from a snapshot."""
        cursor = self.connection.execute("""
            SELECT snapshot_data, project_id
            FROM state_snapshots
            WHERE snapshot_id = ?
        """, (snapshot_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        snapshot_data = json.loads(row['snapshot_data'])
        project_id = row['project_id']

        # TODO: Implement restore logic
        # This would involve recreating tasks, updating statuses, etc.
        # For safety, this should be a complex operation with validation

        self.log_event(
            project_id=project_id,
            event_type="snapshot_restored",
            event_data={"snapshot_id": snapshot_id},
            severity="warning"
        )

    # ========================================================================
    # Query & Analytics
    # ========================================================================

    def get_project_summary(self, project_id: str) -> Dict:
        """Get comprehensive project summary."""
        project = self.get_project(project_id)
        if not project:
            return {}

        # Task statistics
        tasks = self.get_project_tasks(project_id)
        task_stats = {
            'total': len(tasks),
            'queued': sum(1 for t in tasks if t['status'] == 'queued'),
            'in_progress': sum(1 for t in tasks if t['status'] == 'in_progress'),
            'completed': sum(1 for t in tasks if t['status'] == 'completed'),
            'failed': sum(1 for t in tasks if t['status'] == 'failed')
        }

        # Deliverable count
        deliverables = self.get_project_deliverables(project_id)

        # Phase gates
        phase_gates = self.get_project_phase_gates(project_id)

        # Recent events
        recent_events = self.get_project_events(project_id, limit=10)

        return {
            'project': project,
            'task_stats': task_stats,
            'deliverable_count': len(deliverables),
            'phase_gates_passed': len([g for g in phase_gates if g['decision'] == 'GO']),
            'recent_events': recent_events
        }

    def get_agent_workload(self) -> List[Dict]:
        """Get workload for all agents."""
        cursor = self.connection.execute("""
            SELECT
                a.agent_id,
                a.agent_name,
                a.agent_type,
                a.status,
                COUNT(t.task_id) as assigned_tasks,
                SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) as active_tasks
            FROM agents a
            LEFT JOIN tasks t ON a.agent_id = t.assigned_agent_id
            GROUP BY a.agent_id
            ORDER BY assigned_tasks DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Cleanup & Maintenance
    # ========================================================================

    def cleanup_old_events(self, days: int = 30):
        """Delete events older than specified days."""
        with self.transaction() as conn:
            conn.execute("""
                DELETE FROM events
                WHERE occurred_at < datetime('now', ? || ' days')
            """, (f"-{days}",))

    def vacuum_database(self):
        """Optimize database (reclaim space, reindex)."""
        self.connection.execute("VACUUM")
        self.connection.execute("ANALYZE")

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
```

---

## State Recovery After Interruptions

### Recovery Strategy

```python
# recovery.py
class StateRecovery:
    """
    Handles state recovery after system interruptions.
    """

    def __init__(self, state_manager: ProjectStateManager):
        self.state_manager = state_manager

    async def recover_project(self, project_id: str):
        """
        Recover project state after interruption.

        Steps:
        1. Verify database consistency
        2. Identify incomplete tasks
        3. Resume or retry incomplete tasks
        4. Restore agent states
        5. Resume message queue processing
        """
        print(f"Recovering project: {project_id}")

        # 1. Get project state
        project = self.state_manager.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # 2. Find tasks that were in progress
        in_progress_tasks = self.state_manager.get_project_tasks(
            project_id,
            status='in_progress'
        )

        print(f"Found {len(in_progress_tasks)} incomplete tasks")

        # 3. Decide recovery action for each task
        for task in in_progress_tasks:
            recovery_action = self._determine_recovery_action(task)

            if recovery_action == 'retry':
                # Reset task to queued for retry
                self.state_manager.update_task_status(
                    task['task_id'],
                    'queued',
                    progress_percent=0
                )
                print(f"Task {task['task_id']} queued for retry")

            elif recovery_action == 'resume':
                # Keep in_progress, will resume from last checkpoint
                print(f"Task {task['task_id']} will resume")

            elif recovery_action == 'fail':
                # Mark as failed
                self.state_manager.update_task_status(
                    task['task_id'],
                    'failed'
                )
                print(f"Task {task['task_id']} marked as failed")

        # 4. Re-register agents
        # (Agents will re-register on startup)

        # 5. Log recovery
        self.state_manager.log_event(
            project_id=project_id,
            event_type="project_recovered",
            event_data={
                'recovered_tasks': len(in_progress_tasks)
            },
            severity="info"
        )

        print("Recovery complete")

    def _determine_recovery_action(self, task: Dict) -> str:
        """
        Determine what to do with interrupted task.

        Returns:
            'retry', 'resume', or 'fail'
        """
        # Check retry count
        if task.get('retry_count', 0) >= 3:
            return 'fail'

        # Check progress
        progress = task.get('progress_percent', 0)
        if progress < 10:
            return 'retry'  # Barely started, just retry
        elif progress >= 80:
            return 'resume'  # Almost done, resume
        else:
            return 'retry'  # Middle ground, safer to retry

    def create_recovery_checkpoint(
        self,
        project_id: str,
        checkpoint_type: str = "pre_gate"
    ):
        """Create checkpoint before risky operations."""
        return self.state_manager.create_snapshot(
            project_id=project_id,
            snapshot_type=checkpoint_type,
            notes=f"Checkpoint before {checkpoint_type}"
        )
```

---

## JSON State Export (Alternative/Backup)

```python
# json_state_export.py
import json
from pathlib import Path

class JSONStateExporter:
    """
    Export project state to JSON for portability.

    Use cases:
    - Backup/restore across different databases
    - Share project state with team
    - Version control project state
    """

    def export_project_state(
        self,
        state_manager: ProjectStateManager,
        project_id: str,
        output_path: Path
    ):
        """Export full project state to JSON file."""
        state = {
            'version': '1.0',
            'exported_at': datetime.utcnow().isoformat(),
            'project': state_manager.get_project(project_id),
            'tasks': state_manager.get_project_tasks(project_id),
            'deliverables': state_manager.get_project_deliverables(project_id),
            'phase_gates': state_manager.get_project_phase_gates(project_id),
            'events': state_manager.get_project_events(project_id, limit=1000),
            'metrics': state_manager.get_project_metrics(project_id)
        }

        with open(output_path, 'w') as f:
            json.dump(state, f, indent=2, default=str)

        print(f"State exported to: {output_path}")

    def import_project_state(
        self,
        state_manager: ProjectStateManager,
        input_path: Path
    ) -> str:
        """Import project state from JSON file."""
        with open(input_path, 'r') as f:
            state = json.load(f)

        # Create project
        project = state['project']
        project_id = state_manager.create_project(
            name=project['name'],
            description=project['description'],
            project_type=project['project_type'],
            metadata=json.loads(project.get('metadata', '{}'))
        )

        # Import tasks
        for task in state['tasks']:
            state_manager.create_task(
                project_id=project_id,
                task_type=task['task_type'],
                description=task['description'],
                priority=task['priority'],
                metadata=json.loads(task.get('metadata', '{}'))
            )

        # Import deliverables
        for deliverable in state['deliverables']:
            state_manager.create_deliverable(
                project_id=project_id,
                task_id=deliverable.get('task_id'),
                deliverable_type=deliverable['deliverable_type'],
                name=deliverable['name'],
                file_path=deliverable.get('file_path'),
                content=deliverable.get('content')
            )

        print(f"State imported. New project ID: {project_id}")
        return project_id
```

---

## State Visualization Dashboard

### Dashboard Specification

```markdown
# PM-Agents State Dashboard

## Overview Panel
- Project name and description
- Current phase (with progress bar)
- Overall status (Active/Paused/Completed)
- Days in current phase
- Last updated timestamp

## Task Progress
- Total tasks: 25
  - ✅ Completed: 15 (60%)
  - 🔄 In Progress: 5 (20%)
  - ⏳ Queued: 3 (12%)
  - ❌ Failed: 2 (8%)

- Task timeline (Gantt chart)
- Critical path visualization
- Task dependency graph

## Agent Status
- Active agents: 8
  - Coordinator: Active (Load: 45%)
  - Planner: Active (Load: 30%)
  - Supervisor: Active (Load: 60%)
  - FrontendCoder: Active (Load: 80%, Task: "LoginForm component")
  - ...

## Phase Gates
- Gate 1 (Initiation → Planning): ✅ GO (Score: 87%)
- Gate 2 (Planning → Execution): ✅ GO (Score: 92%)
- Gate 3 (Execution → Monitoring): 🔄 Pending

## Deliverables
- Files created: 32
  - Code: 24
  - Documentation: 6
  - Reports: 2

## Recent Events (Live Feed)
- 10:45:32 - Task "LoginForm tests" completed by FrontendCoder
- 10:44:15 - Supervisor assigned task "API integration" to BackendCoder
- 10:42:03 - Phase Gate 2 evaluated: GO decision
- ...

## Metrics Charts
- Task completion rate over time
- Agent utilization over time
- Error rate trend
- API cost tracking
```

### Dashboard Implementation (Flask Web App)

```python
# dashboard.py
from flask import Flask, render_template, jsonify
from project_state_manager import ProjectStateManager

app = Flask(__name__)
state_manager = ProjectStateManager()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/projects')
def get_projects():
    """Get all projects."""
    projects = state_manager.list_projects(status='active')
    return jsonify(projects)

@app.route('/api/projects/<project_id>/summary')
def get_project_summary(project_id):
    """Get project summary."""
    summary = state_manager.get_project_summary(project_id)
    return jsonify(summary)

@app.route('/api/projects/<project_id>/tasks')
def get_project_tasks(project_id):
    """Get project tasks."""
    tasks = state_manager.get_project_tasks(project_id)
    return jsonify(tasks)

@app.route('/api/agents')
def get_agents():
    """Get all agents with workload."""
    agents = state_manager.get_agent_workload()
    return jsonify(agents)

@app.route('/api/projects/<project_id>/events')
def get_project_events(project_id):
    """Get recent events."""
    events = state_manager.get_project_events(project_id, limit=50)
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## Best Practices

### DO
- ✅ Use transactions for related state changes
- ✅ Create snapshots before risky operations (phase gates, major refactors)
- ✅ Log all significant events for audit trail
- ✅ Implement state recovery after interruptions
- ✅ Maintain agent heartbeats for health monitoring
- ✅ Clean up old events periodically (retain 30 days)
- ✅ Export state to JSON for backup
- ✅ Use foreign keys for referential integrity
- ✅ Index frequently queried columns
- ✅ Record metrics for performance analysis

### DON'T
- ❌ Store large binary data in database (use file system + references)
- ❌ Skip transaction boundaries for multi-step operations
- ❌ Forget to update updated_at timestamps
- ❌ Store sensitive data unencrypted
- ❌ Allow unbounded event log growth
- ❌ Skip state validation after recovery
- ❌ Ignore database maintenance (vacuum, analyze)

---

## Integration with Agents

### Coordinator Integration

```python
# coordinator_agent.py
class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.state_manager = ProjectStateManager()

        # Register agent
        self.state_manager.register_agent(
            agent_id=self.agent_id,
            agent_type='Coordinator',
            agent_name='MainCoordinator'
        )

    async def handle_user_request(self, user_request: dict):
        """Handle user request with state persistence."""
        # Create project
        project_id = self.state_manager.create_project(
            name=user_request['project_name'],
            description=user_request['description'],
            project_type=user_request['project_type']
        )

        # Create main task
        task_id = self.state_manager.create_task(
            project_id=project_id,
            task_type='orchestration',
            description=user_request['description'],
            priority='high'
        )

        # Update task status
        self.state_manager.update_task_status(task_id, 'in_progress')

        # Delegate to Planner
        result = await self.delegate_to_planner(user_request, project_id, task_id)

        # Update completion
        self.state_manager.update_task_status(task_id, 'completed', progress_percent=100)

        return result
```

---

**Last Updated**: 2025-10-29
**Status**: Complete - Ready for Implementation
