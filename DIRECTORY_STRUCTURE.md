# Directory Structure

## Overview

```
PM-Agents/
├── .github/              # GitHub configuration
│   └── workflows/        # CI/CD pipelines
├── agents/               # Legacy agent implementations (to be migrated to src/)
├── config/               # Configuration files
├── data/                 # Data storage
│   ├── cache/           # Cached data
│   ├── vectors/         # Vector embeddings
│   └── projects/        # Project-specific data
├── docs/                 # Documentation
│   ├── api/             # API documentation
│   ├── guides/          # User guides
│   └── diagrams/        # Architecture diagrams
├── logs/                 # Application logs
├── notebooks/            # Jupyter notebooks for experimentation
├── scripts/              # Utility scripts
├── specs/                # Agent and MCP server specifications
├── src/                  # Source code (new structure)
│   ├── agents/          # Agent implementations
│   │   ├── coordinator/ # Coordinator agent
│   │   ├── planner/     # Planner agent
│   │   ├── supervisor/  # Supervisor agent
│   │   └── specialists/ # Specialized agents
│   ├── core/            # Core system components
│   ├── database/        # Database models and queries
│   ├── mcp_servers/     # Custom MCP server implementations
│   └── utils/           # Utility functions
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── docker-compose.yml    # Docker services (Qdrant, Redis)
├── init_db.py            # Database initialization
├── package.json          # Node.js dependencies (MCP servers)
├── requirements.txt      # Python dependencies
└── pm_agents.db          # SQLite database (generated)
```

## Directory Purposes

### `/agents` (Legacy)
Original agent implementations. Being migrated to `/src/agents/` for better organization.

### `/config`
Configuration files for different environments (dev, staging, prod).

### `/data`
Runtime data storage:
- `cache/`: Cached API responses, processed data
- `vectors/`: Qdrant vector embeddings backups
- `projects/`: Per-project data and artifacts

### `/docs`
Project documentation:
- `api/`: API reference documentation
- `guides/`: How-to guides and tutorials
- `diagrams/`: Architecture and workflow diagrams

### `/logs`
Application logs for debugging and monitoring.

### `/notebooks`
Jupyter notebooks for:
- ML/DL experimentation
- Data analysis
- Agent behavior testing

### `/scripts`
Utility scripts:
- MCP server installation
- Database migrations
- Development tools

### `/specs`
Detailed specifications:
- Agent behavior and capabilities
- MCP server interfaces
- Communication protocols

### `/src`
Main source code (new organized structure):

#### `/src/agents`
Agent implementations organized by hierarchy:
- `coordinator/`: Orchestration and phase management
- `planner/`: Strategic planning
- `supervisor/`: Tactical management
- `specialists/`: Domain-specific agents

#### `/src/core`
Core system components:
- Message bus
- State management
- Phase gate logic
- Configuration management

#### `/src/database`
Database layer:
- SQLite models
- Query builders
- Migrations

#### `/src/mcp_servers`
Custom MCP server implementations:
- Qdrant server
- Specify server
- TensorBoard server

#### `/src/utils`
Utility functions:
- Logging
- Serialization
- Validation
- Helpers

### `/tests`
Test suite organized by test type:
- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for system interactions
- `e2e/`: End-to-end workflow tests

## Migration Plan

The project is transitioning from flat structure (`/agents`) to organized structure (`/src/agents`).

**Current state**: Working implementations in `/agents`
**Target state**: Organized structure in `/src/agents`
**Migration**: Gradual, maintaining backward compatibility

## File Naming Conventions

- **Python modules**: lowercase_with_underscores.py
- **Classes**: PascalCase
- **Tests**: test_module_name.py
- **Config**: lowercase.yml or lowercase.json
- **Docs**: UPPERCASE.md (root), lowercase.md (subdirs)
