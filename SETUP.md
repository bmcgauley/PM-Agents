# Setup Guide

Quick setup instructions for the PM-Agents multi-agent system.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for MCP servers)
- **Docker** (for Qdrant and Redis)
- **Git**

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/bmcgauley/PM-Agents.git
cd PM-Agents
```

### 2. Set Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_TOKEN="ghp_..."

# Optional
export BRAVE_API_KEY="..."  # For web research
```

### 3. Install Python Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies (MCP Servers)

```bash
npm install
# Or install globally:
npm run mcp:install
```

### 5. Start Docker Services

```bash
docker-compose up -d
```

Verify services:
```bash
curl http://localhost:6333/health  # Qdrant
docker exec pm-agents-redis redis-cli ping  # Redis
```

### 6. Initialize Database

```bash
python init_db.py
```

### 7. Run the System

```bash
python pm_coordinator_agent.py
```

## Detailed Setup

### MCP Server Configuration

Configure MCP servers for Claude Code (user-level/global):

```bash
# Filesystem access
claude mcp add --scope user --transport stdio filesystem -- \
  npx -y @modelcontextprotocol/server-filesystem "/path/to/workspace"

# GitHub integration
claude mcp add --scope user --transport stdio \
  --env GITHUB_TOKEN=ghp_... github -- \
  npx -y @modelcontextprotocol/server-github

# Brave Search
claude mcp add --scope user --transport stdio \
  --env BRAVE_API_KEY=... brave-search -- \
  npx -y @modelcontextprotocol/server-brave-search

# Memory server
claude mcp add --scope user --transport stdio memory -- \
  npx -y @modelcontextprotocol/server-memory
```

See [MCP_SETUP.md](MCP_SETUP.md) for complete configuration.

### Qdrant Collection Setup

Initialize Qdrant collections for vector search:

```bash
python init_qdrant.py
```

### Directory Permissions

Ensure data directories are writable:

```bash
chmod -R 755 data/ logs/
```

## Development Setup

### Install Development Tools

```bash
pip install black flake8 mypy pytest pytest-cov pylint
```

### Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
black .              # Format
flake8 .             # Lint
mypy .               # Type check
```

## Docker Services

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f
```

### Service URLs

- **Qdrant**: http://localhost:6333
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Redis**: localhost:6379

## Troubleshooting

### Docker Issues

```bash
# Restart services
docker-compose restart

# Rebuild containers
docker-compose up -d --build

# Check logs
docker-compose logs qdrant
docker-compose logs redis
```

### Python Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+
```

### MCP Server Issues

```bash
# List configured servers
claude mcp list

# Verify server health
claude doctor
```

### Database Issues

```bash
# Reset database
rm pm_agents.db
python init_db.py
```

## Configuration

### Environment Variables

Create `.env` file (not tracked in Git):

```bash
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
BRAVE_API_KEY=...
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

### Project Configuration

Edit `config/development.yml` for dev settings.

## Next Steps

1. Review [CLAUDE.md](CLAUDE.md) for Git workflow and project guidance
2. Check [AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md) for system design
3. Read [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md) for code organization
4. Start with example project: `python pm_coordinator_agent.py`

## Additional Resources

- [README.md](README.md) - Project overview
- [MCP_SETUP.md](MCP_SETUP.md) - Detailed MCP configuration
- [claudcodesetup.md](claudcodesetup.md) - Complete setup walkthrough
- [TOOLS.md](TOOLS.md) - Required tools and installation
