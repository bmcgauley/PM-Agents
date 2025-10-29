#!/usr/bin/env python3
"""
SQLite Database Initialization Script for PM-Agents System

Creates tables for:
- Projects (tracking active projects)
- Agents (agent registry and status)
- Tasks (task assignments and completion)
- Communications (agent-to-agent messages)
- Phase Gates (phase gate reviews and decisions)
- Risks (risk registry)
- Issues (issue tracking)
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = "pm_agents.db"


def init_database():
    """Initialize SQLite database with required tables."""

    # Remove existing database if present
    if os.path.exists(DB_PATH):
        print(f"Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Projects table
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            current_phase TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Agents table
    cursor.execute("""
        CREATE TABLE agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            capabilities TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP
        )
    """)

    # Tasks table
    cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            agent_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            priority TEXT,
            phase TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        )
    """)

    # Communications table (A2A messages)
    cursor.execute("""
        CREATE TABLE communications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_agent_id INTEGER NOT NULL,
            to_agent_id INTEGER NOT NULL,
            project_id INTEGER,
            message_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_agent_id) REFERENCES agents (id),
            FOREIGN KEY (to_agent_id) REFERENCES agents (id),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)

    # Phase Gates table
    cursor.execute("""
        CREATE TABLE phase_gates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase TEXT NOT NULL,
            decision TEXT NOT NULL,
            score INTEGER,
            criteria_met TEXT,
            reviewer TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)

    # Risks table
    cursor.execute("""
        CREATE TABLE risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase TEXT,
            title TEXT NOT NULL,
            description TEXT,
            probability TEXT,
            impact TEXT,
            mitigation TEXT,
            status TEXT NOT NULL,
            identified_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)

    # Issues table
    cursor.execute("""
        CREATE TABLE issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase TEXT,
            title TEXT NOT NULL,
            description TEXT,
            severity TEXT,
            status TEXT NOT NULL,
            assigned_to TEXT,
            resolution TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)

    # Create indexes for common queries
    cursor.execute("CREATE INDEX idx_projects_status ON projects(status)")
    cursor.execute("CREATE INDEX idx_tasks_project ON tasks(project_id)")
    cursor.execute("CREATE INDEX idx_tasks_status ON tasks(status)")
    cursor.execute("CREATE INDEX idx_communications_project ON communications(project_id)")
    cursor.execute("CREATE INDEX idx_phase_gates_project ON phase_gates(project_id)")
    cursor.execute("CREATE INDEX idx_risks_project ON risks(project_id)")
    cursor.execute("CREATE INDEX idx_issues_project ON issues(project_id)")

    # Insert default agents
    default_agents = [
        ("Coordinator", "orchestration", "active", "Project orchestration, phase management, strategic decisions"),
        ("Planner", "planning", "active", "Strategic planning, roadmap creation, resource allocation"),
        ("Supervisor", "management", "active", "Tactical management, task delegation, progress monitoring"),
        ("SpecKit", "specialist", "active", "Project initialization via Specify"),
        ("Qdrant", "specialist", "active", "Vector search, codebase/documentation search"),
        ("FrontendCoder", "specialist", "active", "React, Next.js, TypeScript, Supabase, Payload CMS"),
        ("PythonML", "specialist", "active", "PyTorch, TensorBoard, Jupyter, ML/DL"),
        ("RAnalytics", "specialist", "active", "R, tidyverse, ggplot2, Shiny, statistical analysis"),
        ("TypeScriptValidator", "specialist", "active", "Type safety, testing, code quality"),
        ("Research", "specialist", "active", "Technical research, documentation gathering"),
        ("Browser", "specialist", "active", "Web automation, scraping, testing"),
        ("Reporter", "specialist", "active", "Documentation generation, reporting"),
    ]

    cursor.executemany(
        "INSERT INTO agents (name, type, status, capabilities) VALUES (?, ?, ?, ?)",
        default_agents
    )

    conn.commit()
    print(f"Database initialized successfully: {DB_PATH}")
    print(f"Created {len(default_agents)} default agents")

    # Display summary
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\nCreated tables:")
    for table in tables:
        print(f"  - {table[0]}")

    conn.close()


if __name__ == "__main__":
    init_database()
