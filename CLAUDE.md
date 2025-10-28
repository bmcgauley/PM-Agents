# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **hierarchical multi-agent system** for software development, research, and project management. The system follows a Coordinator → Planner → Supervisor → Specialists architecture pattern with agent-to-agent (A2A) communication.

## System Architecture

### Agent Hierarchy

```
Coordinator Agent (Orchestration)
    ↓
Planner Agent (Strategic Planning)
    ↓
Supervisor Agent (Tactical Management)
    ↓
Specialized Agents:
├─ Spec-Kit Agent (Project initialization via Specify)
├─ Qdrant Vector Agent (Codebase/documentation search)
├─ Frontend Coder Agent (React/Next.js/TypeScript/Supabase/Payload CMS)
├─ Python ML/DL Agent (PyTorch/TensorBoard/Jupyter)
├─ R Analytics Agent (tidyverse/ggplot2/R Markdown/Shiny)
├─ TypeScript Validator Agent (Type safety/testing/quality)
├─ Research Agent (Technical research)
├─ Browser Agent (Web automation)
└─ Reporter Agent (Documentation generation)
```

### Communication Pattern

- **Downward flow**: Tasks are delegated from Coordinator → Planner → Supervisor → Specialists
- **Upward flow**: Results flow back Specialists → Supervisor → Planner → Coordinator
- **Feedback loops**: Blockers escalate upward for strategic decisions
- **MCP integration**: Agents use Model Context Protocol servers for tool access

## Key Implementation Files

### Two Implementations Available

1. **pm_coordinator_agent.py**: Anthropic Claude-based implementation
   - Uses `anthropic` Python SDK
   - Requires `ANTHROPIC_API_KEY` environment variable
   - Model: `claude-sonnet-4-5-20250929`
   - Agent-to-agent communication via message passing

2. **pm_ollama_agents.py**: Local Ollama-based implementation
   - Uses Ollama API (http://localhost:11434)
   - Model: `gemma2:latest` (Gemma3 when available)
   - Separate agent classes: InitiationAgent, PlanningAgent, ExecutionAgent, MonitoringAgent, ClosureAgent
   - Coordinator class manages all phase agents

### Core Agent Architecture

- **BaseAgent pattern**: Each agent extends a base class with `process_task()` and `_execute()` methods
- **Phase agents**: PMBOK-aligned (Initiation → Planning → Execution → Monitoring → Closure)
- **Phase gates**: Coordinator makes GO/NO-GO decisions between phases
- **Project state tracking**: Maintains phase outputs, decisions, risks, and issues

## Development Commands

### Running the System

```bash
# Using Anthropic Claude
python pm_coordinator_agent.py

# Using Ollama (requires Ollama running)
ollama serve  # In separate terminal
python pm_ollama_agents.py
```

### Environment Setup

```bash
# Set API key for Anthropic version
export ANTHROPIC_API_KEY="your-key-here"

# Start Qdrant vector database (required for full system)
docker run -p 6333:6333 qdrant/qdrant

# Install Python dependencies
pip install -r requirements.txt
```

### Testing

```bash
# Run Python formatter
black .

# Run linter
flake8 .

# Run type checker
mypy .

# Run tests (when test suite exists)
pytest
```

## Technology Stack

### Core Technologies
- **Python 3.10+**: Primary language
- **Anthropic Claude API**: LLM orchestration (or Ollama for local)
- **Qdrant**: Vector database for codebase/documentation search
- **Docker**: Container runtime for Qdrant

### Specialized Agent Technologies

**Frontend Coder Agent**:
- React 18+, Next.js 14+ (App Router)
- TypeScript (strict mode)
- Supabase (Auth, Database, Storage)
- Payload CMS
- TailwindCSS, Radix UI/shadcn/ui
- Zustand/Redux (state), React Query/SWR (data fetching)

**Python ML/DL Agent**:
- PyTorch 2.0+, TensorBoard, Tensor Playground
- NumPy, Pandas, scikit-learn
- Jupyter/JupyterLab notebooks
- wandb (experiment tracking), pytorch-lightning

**R Analytics Agent**:
- R 4.x, tidyverse, ggplot2, dplyr, tidyr
- R Markdown, knitr
- Shiny (interactive dashboards)
- caret/tidymodels (modeling)

**Infrastructure**:
- MCP servers: filesystem, github, brave-search
- Custom MCP servers: Qdrant, Supabase, TensorBoard

## Important Patterns

### Agent Delegation Pattern

```python
# Coordinator delegates to phase agent
result = self.delegate_to_agent(
    agent_type="planning",
    task="Create detailed project plan",
    context={"project_description": "...", "current_phase": "planning"}
)

# Store outputs
self.project_state['phase_outputs'][agent_type].append(result)

# Conduct phase gate review
approved = self.phase_gate_review(agent_type)
```

### Agent System Prompts

Each agent has a specialized system prompt defining:
- **Role and responsibilities**
- **PMBOK phase alignment**
- **Key deliverables expected**
- **Best practices to follow**

See `get_agent_system_prompt()` method for examples.

### Project State Management

The system maintains:
- `current_phase`: Active project phase
- `phase_outputs`: Dictionary of agent outputs per phase
- `go_decisions`: Phase gate review decisions
- `risks`: Identified risks across phases
- `issues`: Encountered issues

## Vector Storage Integration

### Qdrant Setup

```bash
# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Initialize collections (see claudcodesetup.md:314-333)
python init_qdrant.py

# Index codebase (see claudcodesetup.md:343-388)
python index_codebase.py
```

### Vector Agent Usage

- **Semantic search**: Find similar code/documentation
- **Context retrieval**: Provide relevant context to other agents
- **Knowledge base**: Maintain project patterns and standards
- **Automatic updates**: Re-index on code changes

## MCP Server Configuration

MCP servers provide tool access to agents. Use **user-level (global)** configuration for multi-project use.

### Essential MCP Servers (Always Needed)

These servers are configured globally and available to all projects:

1. **filesystem** - File operations across your workspace
2. **github** - Repository operations (requires `GITHUB_TOKEN`)
3. **brave-search** - Web research capabilities (requires `BRAVE_API_KEY`)
4. **memory** - Persistent memory/context storage for agents
5. **qdrant** - Vector database for semantic code/documentation search
6. **puppeteer** - Browser automation for web scraping/testing

**Setup**: Run `claude mcp add --scope user` for each server (see MCP_SETUP.md)

### Optional/Specialized MCP Servers (Add When Needed)

- **supabase** - Only for Frontend Coder Agent when building Supabase-based apps
- **slack/discord** - For notification/collaboration agents (future)
- **postgres/mysql** - For database-specific agents (alternative to Supabase)
- **sequential-thinking** - Enhanced reasoning for complex planning tasks
- **fetch** - Alternative web fetching (Brave Search already covers this)

### Qdrant Collection Strategy

Use **separate collections per project** for clean isolation:
- `{project-name}-codebase` - Source code vectors
- `{project-name}-documentation` - Documentation vectors

This prevents agents from accidentally searching the wrong project context.

**Note**: TensorBoard is NOT an MCP server. The Python ML/DL Agent launches it as a background service when training models.

See **MCP_SETUP.md** for detailed configuration and **claudcodesetup.md** for initial setup.

## Quality Gates

### Code Quality (TypeScript Validator Agent)
- Zero TypeScript errors
- 80%+ test coverage
- ESLint/Prettier compliance
- Security scan passed
- Accessibility compliance (WCAG 2.1 AA)

### ML Quality (Python ML/DL Agent)
- Model performance thresholds met
- TensorBoard logs generated
- Reproducibility validated
- Code quality standards met

### Documentation (Reporter Agent)
- All public APIs documented
- README complete with examples
- Architecture diagrams included
- User guides provided

## Common Workflows

### Creating a New Agent

1. Create agent class extending `BaseAgent` (Anthropic) or `OllamaPMAgent` (Ollama)
2. Implement `_execute()` or `execute_task()` method
3. Define `get_system_prompt()` with role and responsibilities
4. Register with Supervisor in initialization
5. Define MCP tools required for agent operations

### Adding a New Phase

1. Create phase-specific agent class
2. Define PMBOK-aligned responsibilities and deliverables
3. Add to phases list in `manage_project()` method
4. Implement phase gate criteria
5. Update project state tracking

### Implementing A2A Communication

- Use `delegate_to_agent()` for hierarchical delegation
- Pass context including project description and previous outputs
- Return structured results with deliverables, risks, issues, next steps
- Escalate blockers upward through hierarchy

## Documentation Reference

- **README.md**: Overview, quick start, system workflow
- **AGENT_ARCHITECTURE.md**: Detailed agent specifications, communication patterns, use cases
- **claudcodesetup.md**: Complete setup instructions for MCP servers, Qdrant, agent implementations
- **TOOLS.md**: Required tools and installation commands
- **COMPARISON_ANALYSIS.md**: Claude vs Ollama comparison
- **architecture.drawio**: Visual architecture diagram (open in Draw.io)

## API Keys Required

```bash
# Anthropic (for Claude implementation)
export ANTHROPIC_API_KEY="sk-ant-..."

# GitHub (for repository operations)
export GITHUB_TOKEN="ghp_..."

# Brave Search (optional, for web research)
export BRAVE_API_KEY="..."

# Supabase (for frontend projects)
export SUPABASE_URL="https://..."
export SUPABASE_ANON_KEY="..."
```

## Development Notes

- This is an **academic/educational project** demonstrating hierarchical multi-agent systems
- Follows **PMI PMBOK Guide (7th Edition)** standards for project management phases
- Uses **Model Context Protocol (MCP)** for standardized tool integration
- Implements **agent-to-agent (A2A) communication** patterns
- When extending the system, maintain clear separation between orchestration (Coordinator), planning (Planner), management (Supervisor), and execution (Specialists)
- All agents should follow their PMBOK phase responsibilities and produce standard deliverables
- Phase gates are critical control points - implement thorough reviews before proceeding

## Troubleshooting

**API Key Issues**: Verify `ANTHROPIC_API_KEY` is set correctly
**Ollama Connection**: Ensure `ollama serve` is running on localhost:11434
**Qdrant Connection**: Check Docker container is running on port 6333
**Import Errors**: Activate virtual environment and install requirements.txt
**Model Not Found** (Ollama): Run `ollama pull gemma2` first

## Next Steps for Development

1. Implement specialist agents (currently stubbed in agent architecture)
2. Add MCP tool integration for filesystem, GitHub, and Qdrant operations
3. Create project templates for common tech stacks
4. Implement comprehensive test suite
5. Add logging and monitoring for agent communication
6. Create example projects demonstrating full system capabilities
