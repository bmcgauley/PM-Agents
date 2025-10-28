# Comprehensive Multi-Agent Development System

A hierarchical multi-agent system for software development, research, and analytics. Features specialized agents for frontend development (React/Next.js), ML/DL (PyTorch), R analytics, and more, with integrated vector storage and comprehensive validation.

## Architecture Overview

The system implements a **Coordinator → Planner → Supervisor → Specialists** hierarchy:

### Orchestration Layer
- **Coordinator Agent**: Top-level orchestration and decision-making

### Planning Layer
- **Planner Agent**: Strategic planning and task decomposition

### Management Layer
- **Supervisor Agent**: Tactical management and coordination of specialized agents

### Specialized Agents

**Development Agents**:
- **Spec-Kit Agent**: Project initialization using Specify
- **Frontend Coder Agent**: React/Next.js/TypeScript/Supabase/Payload CMS
- **Python ML/DL Agent**: PyTorch/TensorBoard/Jupyter
- **R Analytics Agent**: tidyverse/ggplot2/R Markdown/Shiny

**Infrastructure Agents**:
- **Qdrant Vector Agent**: Codebase and documentation vector storage

**Quality Agents**:
- **TypeScript Validator Agent**: Type safety, testing, debugging

**Research Agents**:
- **Research Agent**: Technical research and best practices
- **Browser Agent**: Web browsing and automation
- **Reporter Agent**: Documentation and reporting

## Key Features

✅ **Hierarchical Multi-Agent Architecture**: Coordinator → Planner → Supervisor → Specialists
✅ **Specialized Development Agents**: Frontend, Python ML/DL, R Analytics
✅ **Vector-Powered Knowledge**: Qdrant integration for codebase search
✅ **Model Context Protocol (MCP)**: Standardized tool integration
✅ **Quality Validation**: TypeScript safety, testing, and debugging
✅ **Project Initialization**: Automated setup with Specify (spec-kit)
✅ **Multiple Tech Stacks**: React/Next.js, PyTorch, R, Supabase, Payload CMS
✅ **Comprehensive Documentation**: Automated reporting and documentation  

---

## Quick Start

### Prerequisites

**Required**:
- Python 3.10+
- Node.js 18+ or 20+
- Docker (for Qdrant)
- Anthropic API key

**Optional** (for specialized agents):
- R 4.x (for R Analytics Agent)
- Git and GitHub token

### Installation

See **[claudcodesetup.md](claudcodesetup.md)** for complete setup instructions.

**Quick install**:

```bash
# 1. Clone repository
git clone <your-repo-url>
cd PM-Agents

# 2. Install Python dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Install Node dependencies (for MCP servers)
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-brave-search

# 4. Start Qdrant (vector database)
docker run -p 6333:6333 qdrant/qdrant

# 5. Set environment variables
export ANTHROPIC_API_KEY="your-key"
export GITHUB_TOKEN="your-token"
export BRAVE_API_KEY="your-key"
```

---

## Implementation 1: Claude Code (Anthropic)

### Setup

1. **Get Anthropic API Key**
   - Sign up at https://console.anthropic.com/
   - Generate an API key from your account settings

2. **Set environment variable**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```
   
   Or on Windows:
   ```cmd
   set ANTHROPIC_API_KEY=your-api-key-here
   ```

### Usage

```python
from pm_coordinator_agent import PMCoordinatorAgent

# Initialize coordinator
coordinator = PMCoordinatorAgent()

# Define your project
project = "Develop an AI-powered customer service chatbot for e-commerce platform"

# Execute project management
result = coordinator.manage_project(project)

# View results
print(result)
```

### Run the example:
```bash
python pm_coordinator_agent.py
```

---

## Implementation 2: Ollama Gemma3 (Local)

### Setup

1. **Install Ollama**
   - Download from https://ollama.ai/
   - Follow installation instructions for your OS

2. **Pull Gemma2 model** (or Gemma3 when available)
   ```bash
   ollama pull gemma2
   ```

3. **Start Ollama server**
   ```bash
   ollama serve
   ```
   
   Keep this terminal open while running the agents.

### Usage

```python
from pm_ollama_agents import OllamaCoordinator

# Initialize coordinator (Ollama must be running)
coordinator = OllamaCoordinator()

# Define your project
project = """
Develop an AI-powered project management assistant that helps teams 
automate task scheduling, resource allocation, and risk monitoring.
"""

# Execute project management
result = coordinator.manage_project(project)

# Results are automatically saved to pm_project_results.json
```

### Run the example:
```bash
# Make sure Ollama is running first!
python pm_ollama_agents.py
```

---

## System Workflow

```
User Request
     ↓
Coordinator Agent (Analyzes request, determines strategy)
     ↓
Planner Agent (Creates detailed plan, assigns agents)
     ↓
Supervisor Agent (Manages execution, coordinates specialists)
     ↓
┌────────────┬────────────┬────────────┬────────────┬────────────┐
│ Spec-Kit   │ Frontend   │ Python ML  │ R          │ Qdrant     │
│ Agent      │ Coder      │ Agent      │ Analytics  │ Vector     │
└────────────┴────────────┴────────────┴────────────┴────────────┘
     ↓            ↓            ↓            ↓            ↓
     └────────────┴────────────┴────────────┴────────────┘
                              ↓
                    TypeScript Validator
                    (Reviews code quality)
                              ↓
     ┌────────────┬────────────┬────────────┐
     │ Research   │ Browser    │ Reporter   │
     │ Agent      │ Agent      │ Agent      │
     └────────────┴────────────┴────────────┘
                              ↓
                    Final Deliverables
                              ↓
                    Back to Coordinator
                              ↓
                    User receives results
```

### Example Flow: Web Application Project

1. **User Request**: "Build a customer portal with authentication and dashboard"
2. **Coordinator**: Analyzes → determines it's a full-stack web project
3. **Planner**: Creates plan:
   - Initialize project with Spec-Kit
   - Index codebase with Qdrant
   - Implement frontend with Next.js/Supabase
   - Validate TypeScript safety
   - Document with Reporter
4. **Supervisor**: Delegates tasks to specialists
5. **Specialists Execute**:
   - Spec-Kit: Creates Next.js project structure
   - Qdrant: Indexes boilerplate and docs
   - Frontend Coder: Implements components, auth, dashboard
   - TypeScript Validator: Reviews code, runs tests
   - Reporter: Generates documentation
6. **Results** flow back through Supervisor → Planner → Coordinator
7. **User** receives complete, tested, documented application

---

## Agent Communication Patterns

### A2A (Agent-to-Agent) Communication

```python
# Coordinator → Planner
analysis = coordinator.analyze_request(user_request)
plan = coordinator.delegate_to_planner(analysis)

# Planner → Supervisor
execution_plan = planner.create_detailed_plan(analysis)
results = planner.delegate_to_supervisor(execution_plan)

# Supervisor → Specialists
for task in execution_plan.tasks:
    specialist = supervisor.get_specialist(task.agent_type)
    result = specialist.process_task(task)
    supervisor.aggregate_result(result)

# Results flow back up the hierarchy
```

### MCP (Model Context Protocol) Integration

Agents use MCP servers for specialized operations:

- **Filesystem MCP**: File operations (read, write, edit)
- **GitHub MCP**: Repository operations (clone, PR, issues)
- **Brave Search MCP**: Web research
- **Qdrant MCP** (custom): Vector storage and semantic search
- **Supabase MCP** (custom): Database and auth operations
- **TensorBoard MCP** (custom): ML visualization

All communication includes:
- **Task**: Detailed task description
- **Context**: Project state and dependencies
- **Tools**: Available MCP tools
- **Response Format**: Expected deliverable structure

---

## Documentation

### Core Documents

1. **[AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md)**: Comprehensive agent specifications
   - Detailed agent responsibilities
   - Communication patterns
   - Technology stacks
   - Quality gates
   - Use cases and examples

2. **[MCP_SETUP.md](MCP_SETUP.md)**: MCP Server Configuration Guide **(NEW)**
   - Essential vs optional MCP servers
   - User-level (global) configuration
   - Qdrant custom MCP server setup
   - Per-project collection strategy
   - Service vs MCP clarification

3. **[RECOMMENDED_AGENTS.md](RECOMMENDED_AGENTS.md)**: Agent Extension Recommendations **(NEW)**
   - High-priority agent additions (DevOps, Database, Security, API)
   - Medium-priority additions (Code Review, Dependency Mgmt, Performance)
   - Specialized agents (Mobile, Desktop, Data Science)
   - Implementation templates and priorities

4. **[claudcodesetup.md](claudcodesetup.md)**: Complete initial setup guide
   - Step-by-step MCP server installation
   - Qdrant vector database setup
   - Agent implementation code
   - Technology stack configuration
   - Verification and troubleshooting

5. **[architecture.drawio](architecture.drawio)**: Visual architecture diagram
   - Hierarchical agent structure
   - Communication flow
   - Agent relationships
   - Open with Draw.io (https://app.diagrams.net/)

6. **[TOOLS.md](TOOLS.md)**: Complete tools installation list
   - All required software and packages
   - Installation commands
   - Verification steps
   - Quick install scripts

7. **[CLAUDE.md](CLAUDE.md)**: Project instructions for Claude Code
   - Overview and quick reference
   - MCP server guidance
   - Development patterns
   - Troubleshooting tips

### Key Architectural Concepts

1. **Hierarchical Multi-Agent System**
   - Four-tier architecture: Coordinator → Planner → Supervisor → Specialists
   - Clear separation of concerns
   - Bidirectional feedback loops
   - Escalation paths for blockers

2. **Specialized Agent Roles**
   - **Development**: Frontend (React/Next.js), Python ML/DL, R Analytics
   - **Infrastructure**: Spec-Kit, Qdrant Vector Storage
   - **Quality**: TypeScript Validator
   - **Research**: Research, Browser, Reporter agents

3. **MCP Integration**
   - Standardized tool protocol
   - Custom MCP servers (Qdrant, Supabase, TensorBoard)
   - Filesystem, GitHub, Web Search integration

4. **Vector-Powered Knowledge**
   - Qdrant for semantic code search
   - Automatic codebase indexing
   - Documentation retrieval
   - Context-aware suggestions

---

## Troubleshooting

### Claude Code Issues

**Problem**: "Invalid API key"
- Solution: Verify your ANTHROPIC_API_KEY environment variable is set correctly

**Problem**: "Rate limit exceeded"
- Solution: Wait a few minutes or upgrade your Anthropic plan

### Ollama Issues

**Problem**: "Connection refused to localhost:11434"
- Solution: Make sure Ollama is running with `ollama serve`

**Problem**: "Model not found: gemma2"
- Solution: Pull the model first with `ollama pull gemma2`

**Problem**: "Slow responses"
- Solution: Ollama runs locally - performance depends on your hardware. Consider using a smaller model or cloud alternative.

---

## Comparison: Claude Code vs Ollama

| Feature | Claude Code | Ollama Gemma3 |
|---------|-------------|---------------|
| **Deployment** | Cloud API | Local |
| **Cost** | Pay per token | Free (after setup) |
| **Speed** | Fast (cloud servers) | Depends on hardware |
| **Privacy** | Data sent to Anthropic | Fully private |
| **Model Quality** | Claude Sonnet 4.5 (very high) | Gemma2 (good) |
| **Setup Complexity** | Low (just API key) | Medium (install Ollama) |
| **Best For** | Production, high quality | Development, privacy |

---

## Project Structure

```
PM-Agents/
├── README.md                          # This file
├── AGENT_ARCHITECTURE.md              # Detailed agent specifications
├── claudcodesetup.md                  # Complete setup guide
├── TOOLS.md                           # All required tools and installation
├── architecture.drawio                # Architecture diagram (open in Draw.io)
├── requirements.txt                   # Python dependencies
├── package.json                       # Node.js dependencies (MCP servers)
│
├── agents/                            # Agent implementations
│   ├── base_agent.py                  # Base agent class
│   ├── coordinator/
│   │   └── coordinator_agent.py
│   ├── planner/
│   │   └── planner_agent.py
│   ├── supervisor/
│   │   └── supervisor_agent.py
│   └── specialists/
│       ├── speckit/                   # Project initialization
│       ├── qdrant/                    # Vector storage
│       ├── frontend/                  # React/Next.js development
│       ├── python_ml/                 # PyTorch ML/DL
│       ├── r_analytics/               # R statistical analysis
│       ├── ts_validator/              # TypeScript validation
│       ├── research/                  # Research tasks
│       ├── browser/                   # Web automation
│       └── reporter/                  # Documentation
│
├── configs/                           # Configuration files
│   ├── mcp_config.json                # MCP server configuration
│   └── agent_prompts.json             # Agent prompt templates
│
├── tools/                             # Utility scripts
│   ├── init_qdrant.py                 # Initialize Qdrant collections
│   └── index_codebase.py              # Index project code
│
├── templates/                         # Project templates
│   ├── nextjs-supabase/               # Frontend template
│   ├── pytorch-ml/                    # ML project template
│   └── r-analysis/                    # R analysis template
│
└── examples/                          # Example projects
    ├── web_app_example/
    ├── ml_pipeline_example/
    └── analytics_dashboard_example/
```

---

## References

1. **PMBOK Guide** (7th Edition) - Project Management Institute
2. **AI Agents, MCP, and A2A Communication** - Dr. Stephen Choi, CSUF
3. **Anthropic Claude Documentation** - https://docs.anthropic.com/
4. **Ollama Documentation** - https://ollama.ai/
5. **Model Context Protocol** - Anthropic MCP Specification

---

## License

Educational use for academic assignment.

## Author

Created for IS course assignment - Multi-Agent Project Management System

## Contact

For questions about this implementation, contact your course instructor.
