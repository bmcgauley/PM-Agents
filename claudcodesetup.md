# Claude Code Setup Guide - Multi-Agent System

Complete setup instructions for implementing the hierarchical multi-agent system in Claude Code.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [MCP Server Setup](#mcp-server-setup)
3. [Agent Implementation](#agent-implementation)
4. [Vector Database Setup (Qdrant)](#vector-database-setup-qdrant)
5. [Technology Stack Configuration](#technology-stack-configuration)
6. [Verification Steps](#verification-steps)

---

## Prerequisites

**See [TOOLS.md](TOOLS.md) for the complete list of all required tools and installation instructions.**

### Quick Verification

Before proceeding, verify you have these core tools installed:

```bash
# Node.js and npm (for Frontend development)
node --version  # Should be v18+ or v20+
npm --version

# Python (for ML/DL development)
python --version  # Should be 3.10+
pip --version

# R (for analytics - optional)
R --version  # Should be 4.x

# Git
git --version

# Docker (for Qdrant)
docker --version
```

**If any are missing, refer to [TOOLS.md](TOOLS.md) for installation instructions.**

### Claude Code CLI

Ensure Claude Code is installed and authenticated:

```bash
# Check Claude Code installation
claude --version

# Authenticate (if not already done)
claude auth login
```

---

## MCP Server Setup

### Step 1: Install Core MCP Servers

```bash
# Create a directory for MCP configurations
mkdir -p ~/.config/claude-code/mcp-servers
cd ~/.config/claude-code/mcp-servers

# Install filesystem MCP server
npm install -g @modelcontextprotocol/server-filesystem

# Install GitHub MCP server
npm install -g @modelcontextprotocol/server-github

# Install Brave Search MCP server (for web research)
npm install -g @modelcontextprotocol/server-brave-search
```

### Step 2: Configure MCP Servers in Claude Code

Create or edit `~/.config/claude-code/mcp_config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/workspace"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-github-token-here"
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-brave-api-key-here"
      }
    }
  }
}
```

**Get API Keys**:
- **GitHub Token**: https://github.com/settings/tokens (need `repo` and `read:org` scopes)
- **Brave Search API**: https://brave.com/search/api/

### Step 3: Install Custom MCP Servers

#### Qdrant MCP Server

```bash
# Clone or create Qdrant MCP server
cd ~/.config/claude-code/mcp-servers
mkdir qdrant-mcp && cd qdrant-mcp

# Create package.json
cat > package.json << 'EOF'
{
  "name": "qdrant-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "@qdrant/js-client-rest": "^1.9.0"
  }
}
EOF

# Install dependencies
npm install
```

Create `index.js`:

```javascript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { QdrantClient } from '@qdrant/js-client-rest';

const server = new Server({
  name: 'qdrant-mcp-server',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {}
  }
});

const qdrant = new QdrantClient({
  url: process.env.QDRANT_URL || 'http://localhost:6333'
});

// Define tools
server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'qdrant_search',
      description: 'Search for similar code or documentation in vector database',
      inputSchema: {
        type: 'object',
        properties: {
          collection: { type: 'string', description: 'Collection name' },
          query: { type: 'string', description: 'Search query' },
          limit: { type: 'number', description: 'Number of results', default: 10 }
        },
        required: ['collection', 'query']
      }
    },
    {
      name: 'qdrant_index',
      description: 'Index code or documentation into vector database',
      inputSchema: {
        type: 'object',
        properties: {
          collection: { type: 'string', description: 'Collection name' },
          content: { type: 'string', description: 'Content to index' },
          metadata: { type: 'object', description: 'Metadata' }
        },
        required: ['collection', 'content']
      }
    }
  ]
}));

// Tool handlers
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'qdrant_search') {
    // Implement search logic
    const results = await qdrant.search(args.collection, {
      vector: await embedText(args.query),
      limit: args.limit || 10
    });
    return { content: [{ type: 'text', text: JSON.stringify(results, null, 2) }] };
  }

  if (name === 'qdrant_index') {
    // Implement indexing logic
    await qdrant.upsert(args.collection, {
      points: [{
        id: Date.now(),
        vector: await embedText(args.content),
        payload: args.metadata
      }]
    });
    return { content: [{ type: 'text', text: 'Indexed successfully' }] };
  }

  throw new Error(`Unknown tool: ${name}`);
});

async function embedText(text) {
  // Use OpenAI or other embedding service
  // For now, return mock embedding
  return new Array(384).fill(0).map(() => Math.random());
}

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

Add to `mcp_config.json`:

```json
{
  "mcpServers": {
    "qdrant": {
      "command": "node",
      "args": ["/Users/youruser/.config/claude-code/mcp-servers/qdrant-mcp/index.js"],
      "env": {
        "QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

#### Supabase MCP Server

```bash
cd ~/.config/claude-code/mcp-servers
npm install -g @supabase/supabase-js

# Create Supabase MCP wrapper
mkdir supabase-mcp && cd supabase-mcp
npm init -y
npm install @modelcontextprotocol/sdk @supabase/supabase-js
```

Create `index.js` (similar pattern to Qdrant above, exposing Supabase operations as MCP tools)

Add to `mcp_config.json`:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "node",
      "args": ["/Users/youruser/.config/claude-code/mcp-servers/supabase-mcp/index.js"],
      "env": {
        "SUPABASE_URL": "your-project-url",
        "SUPABASE_ANON_KEY": "your-anon-key"
      }
    }
  }
}
```

---

## Vector Database Setup (Qdrant)

### Step 1: Install and Run Qdrant

```bash
# Using Docker (recommended)
docker pull qdrant/qdrant

# Run Qdrant
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant
```

Or install locally:

```bash
# macOS
brew install qdrant

# Start Qdrant
qdrant
```

### Step 2: Create Collections for Code and Docs

```bash
# Create a Python script to initialize collections
cat > init_qdrant.py << 'EOF'
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url="http://localhost:6333")

# Create collection for codebase
client.create_collection(
    collection_name="codebase",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Create collection for documentation
client.create_collection(
    collection_name="documentation",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

print("Collections created successfully!")
EOF

# Install Python client and run
pip install qdrant-client
python init_qdrant.py
```

### Step 3: Index Your Codebase

```bash
# Create a script to index your codebase
cat > index_codebase.py << 'EOF'
import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('all-MiniLM-L6-v2')

def index_directory(directory, collection="codebase"):
    points = []
    point_id = 0

    for root, dirs, files in os.walk(directory):
        # Skip node_modules, .git, etc.
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'dist', 'build', '__pycache__']]

        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx', '.py', '.r', '.md')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            vector = encoder.encode(content).tolist()
                            points.append({
                                "id": point_id,
                                "vector": vector,
                                "payload": {
                                    "file_path": file_path,
                                    "file_name": file,
                                    "content": content[:1000]  # Store snippet
                                }
                            })
                            point_id += 1
                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")

    # Upload to Qdrant
    if points:
        client.upsert(collection_name=collection, points=points)
        print(f"Indexed {len(points)} files")

# Index your project
index_directory("/path/to/your/project")
EOF

# Install dependencies and run
pip install sentence-transformers
python index_codebase.py
```

---

## Agent Implementation

### Step 1: Create Agent Directory Structure

```bash
# Create directory structure
mkdir -p ~/pm-agents/{agents,configs,tools,templates}
cd ~/pm-agents

# Create subdirectories for each agent type
mkdir -p agents/{coordinator,planner,supervisor}
mkdir -p agents/specialists/{speckit,qdrant,frontend,python-ml,r-analytics,ts-validator,research,browser,reporter}
```

### Step 2: Create Base Agent Class

Create `agents/base_agent.py`:

```python
from anthropic import Anthropic
from typing import Dict, Any, List
import json

class BaseAgent:
    def __init__(self, name: str, role: str, model: str = "claude-sonnet-4-5-20250929"):
        self.name = name
        self.role = role
        self.model = model
        self.client = Anthropic()
        self.context = []
        self.status = "idle"

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results"""
        self.status = "busy"
        try:
            result = self._execute(task)
            self.status = "completed"
            return result
        except Exception as e:
            self.status = "blocked"
            return {"error": str(e), "status": "blocked"}

    def _execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Override this in specialized agents"""
        raise NotImplementedError

    def call_llm(self, messages: List[Dict], tools: List[Dict] = None):
        """Make LLM call with optional tools"""
        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }
        if tools:
            kwargs["tools"] = tools

        return self.client.messages.create(**kwargs)
```

### Step 3: Implement Coordinator Agent

Create `agents/coordinator/coordinator_agent.py`:

```python
from ..base_agent import BaseAgent
from typing import Dict, Any

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Coordinator",
            role="Top-level orchestration and decision-making"
        )
        self.planner = None

    def set_planner(self, planner):
        self.planner = planner

    def manage_project(self, user_request: str) -> Dict[str, Any]:
        """Main entry point for project management"""

        # Analyze request
        messages = [{
            "role": "user",
            "content": f"""You are the Coordinator Agent. Analyze this request and determine:
1. Project type (web app, ML/DL, research, analytics, etc.)
2. Key objectives
3. High-level strategy

Request: {user_request}

Respond in JSON format:
{{
    "project_type": "...",
    "objectives": [...],
    "strategy": "..."
}}"""
        }]

        response = self.call_llm(messages)
        analysis = response.content[0].text

        # Delegate to Planner
        plan = self.planner.create_plan(analysis)

        # Monitor execution
        result = self.planner.supervisor.execute_plan(plan)

        return {
            "status": "completed",
            "analysis": analysis,
            "plan": plan,
            "result": result
        }
```

### Step 4: Implement Planner Agent

Create `agents/planner/planner_agent.py`:

```python
from ..base_agent import BaseAgent
from typing import Dict, Any, List

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Planner",
            role="Strategic planning and task decomposition"
        )
        self.supervisor = None

    def set_supervisor(self, supervisor):
        self.supervisor = supervisor

    def create_plan(self, analysis: str) -> Dict[str, Any]:
        """Create detailed project plan"""

        messages = [{
            "role": "user",
            "content": f"""You are the Planner Agent. Based on this analysis, create a detailed plan:

{analysis}

Create a plan with:
1. Phases (init, implement, validate, document, deploy)
2. Tasks for each phase
3. Required agents for each task
4. Success criteria
5. Dependencies

Respond in JSON format."""
        }]

        response = self.call_llm(messages)
        plan = response.content[0].text

        return plan
```

### Step 5: Implement Supervisor Agent

Create `agents/supervisor/supervisor_agent.py`:

```python
from ..base_agent import BaseAgent
from typing import Dict, Any, List

class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Supervisor",
            role="Tactical management of specialized agents"
        )
        self.specialists = {}

    def register_specialist(self, agent_type: str, agent):
        """Register a specialized agent"""
        self.specialists[agent_type] = agent

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plan by delegating to specialists"""

        results = {}

        # Parse plan and delegate tasks
        for phase in plan.get("phases", []):
            phase_results = []

            for task in phase.get("tasks", []):
                agent_type = task.get("agent")

                if agent_type in self.specialists:
                    agent = self.specialists[agent_type]
                    result = agent.process_task(task)
                    phase_results.append(result)
                else:
                    phase_results.append({
                        "error": f"Agent {agent_type} not found",
                        "status": "blocked"
                    })

            results[phase["name"]] = phase_results

        return results
```

### Step 6: Implement Specialized Agents

#### Frontend Coder Agent

Create `agents/specialists/frontend/frontend_agent.py`:

```python
from ...base_agent import BaseAgent
from typing import Dict, Any

class FrontendCoderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Frontend-Coder",
            role="Frontend development with React/Next.js/TypeScript"
        )

    def _execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implement frontend features"""

        task_description = task.get("description", "")

        messages = [{
            "role": "user",
            "content": f"""You are a Frontend Coder Agent specializing in:
- React 18+
- Next.js 14+ (App Router)
- TypeScript
- Supabase
- Payload CMS
- TailwindCSS

Implement this feature:
{task_description}

Provide:
1. Component code
2. Type definitions
3. Supabase integration (if needed)
4. Tests

Ensure type safety and best practices."""
        }]

        # Use MCP tools for filesystem operations
        tools = [
            {
                "name": "write_file",
                "description": "Write code to file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["path", "content"]
                }
            }
        ]

        response = self.call_llm(messages, tools)

        return {
            "status": "completed",
            "output": response.content[0].text,
            "files_created": []  # Extract from tool calls
        }
```

#### Python ML/DL Agent

Create `agents/specialists/python-ml/python_ml_agent.py`:

```python
from ...base_agent import BaseAgent
from typing import Dict, Any

class PythonMLAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Python-ML",
            role="Machine Learning and Deep Learning with PyTorch"
        )

    def _execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implement ML/DL models"""

        task_description = task.get("description", "")

        messages = [{
            "role": "user",
            "content": f"""You are a Python ML/DL Agent specializing in:
- PyTorch 2.0+
- TensorBoard
- Tensor Playground
- NumPy, Pandas
- scikit-learn

Implement this:
{task_description}

Provide:
1. Model architecture code
2. Training pipeline
3. TensorBoard logging
4. Evaluation metrics
5. Jupyter notebook (if applicable)"""
        }]

        response = self.call_llm(messages)

        return {
            "status": "completed",
            "output": response.content[0].text
        }
```

#### Similar implementations for other specialists (R Analytics, TypeScript Validator, etc.)

### Step 7: Wire Everything Together

Create `main.py`:

```python
from agents.coordinator.coordinator_agent import CoordinatorAgent
from agents.planner.planner_agent import PlannerAgent
from agents.supervisor.supervisor_agent import SupervisorAgent
from agents.specialists.frontend.frontend_agent import FrontendCoderAgent
from agents.specialists.python_ml.python_ml_agent import PythonMLAgent
# Import other specialists...

def initialize_system():
    """Initialize the multi-agent system"""

    # Create agents
    coordinator = CoordinatorAgent()
    planner = PlannerAgent()
    supervisor = SupervisorAgent()

    # Create specialists
    frontend_agent = FrontendCoderAgent()
    python_ml_agent = PythonMLAgent()
    # Create other specialists...

    # Wire up the hierarchy
    coordinator.set_planner(planner)
    planner.set_supervisor(supervisor)

    # Register specialists with supervisor
    supervisor.register_specialist("frontend", frontend_agent)
    supervisor.register_specialist("python-ml", python_ml_agent)
    # Register other specialists...

    return coordinator

def main():
    # Initialize system
    coordinator = initialize_system()

    # Example usage
    user_request = """
    Build a customer analytics dashboard with:
    - Next.js frontend with TypeScript
    - Supabase for authentication and data
    - Python backend for ML predictions
    - R for statistical analysis
    """

    result = coordinator.manage_project(user_request)
    print(result)

if __name__ == "__main__":
    main()
```

---

## Technology Stack Configuration

### Frontend Development Setup

```bash
# Install global tools
npm install -g typescript @types/node
npm install -g eslint prettier
npm install -g vercel  # For deployment

# Create Next.js project template (for Spec-Kit Agent)
npx create-next-app@latest project-template \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"

cd project-template

# Install frontend dependencies
npm install @supabase/supabase-js
npm install @payloadcms/db-mongodb @payloadcms/richtext-slate payload
npm install zustand  # State management
npm install @tanstack/react-query  # Data fetching
npm install @radix-ui/react-*  # UI components
```

### Python ML/DL Setup

```bash
# Create virtual environment
python -m venv ~/venvs/ml-env
source ~/venvs/ml-env/bin/activate

# Install ML/DL dependencies
pip install torch torchvision torchaudio
pip install tensorboard
pip install jupyter jupyterlab
pip install numpy pandas scikit-learn
pip install matplotlib seaborn
pip install wandb  # Experiment tracking
pip install pytorch-lightning  # Training framework

# Install code quality tools
pip install black flake8 mypy pytest
```

### R Analytics Setup

```bash
# Install R packages
R -e "install.packages(c('tidyverse', 'ggplot2', 'dplyr', 'tidyr', 'readr', 'rmarkdown', 'knitr', 'shiny', 'caret', 'tidymodels'), repos='https://cloud.r-project.org')"

# Install RStudio (optional but recommended)
# Download from https://posit.co/download/rstudio-desktop/
```

### Spec-Kit (Specify) Setup

```bash
# Install Specify CLI
npm install -g @specify/cli

# Or use directly with npx
npx @specify/cli init
```

---

## Verification Steps

### Step 1: Verify MCP Servers

```bash
# Test filesystem MCP
npx @modelcontextprotocol/server-filesystem /tmp

# Test GitHub MCP (requires GITHUB_TOKEN)
export GITHUB_TOKEN="your-token"
npx @modelcontextprotocol/server-github

# Test Brave Search MCP (requires BRAVE_API_KEY)
export BRAVE_API_KEY="your-key"
npx @modelcontextprotocol/server-brave-search
```

### Step 2: Verify Qdrant

```bash
# Check Qdrant is running
curl http://localhost:6333/collections

# Should return list of collections (codebase, documentation)
```

### Step 3: Test Agent Communication

```bash
# Run a simple test
cd ~/pm-agents
python main.py

# Should see agent communication logs
```

### Step 4: Verify Technology Stacks

```bash
# Frontend
node -v  # v18+ or v20+
npm -v
npx next -v

# Python ML
python -c "import torch; print(torch.__version__)"  # Should print PyTorch version
python -c "import tensorboard; print('TensorBoard OK')"

# R
R --version
R -e "library(tidyverse); print('tidyverse OK')"

# Qdrant
python -c "from qdrant_client import QdrantClient; print('Qdrant client OK')"
```

---

## Quick Start Commands

Once everything is set up, use these commands to start the system:

```bash
# Terminal 1: Start Qdrant
docker start qdrant  # Or: qdrant

# Terminal 2: Start the agent system
cd ~/pm-agents
source venv/bin/activate  # If using virtual env
python main.py

# Or use Claude Code directly
claude code chat "Build a Next.js app with Supabase authentication"
```

---

## Troubleshooting

### MCP Server Issues

**Problem**: MCP servers not connecting

```bash
# Check MCP config
cat ~/.config/claude-code/mcp_config.json

# Verify node modules are installed
npm list -g @modelcontextprotocol/server-filesystem
```

**Problem**: Qdrant connection refused

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Check Qdrant logs
docker logs qdrant
```

### Agent Issues

**Problem**: Agent imports failing

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:~/pm-agents"
```

**Problem**: API rate limits

```bash
# Use environment variable to set API key
export ANTHROPIC_API_KEY="your-key"

# Monitor usage at https://console.anthropic.com/
```

---

## Advanced Configuration

### Custom Agent Prompts

Create `configs/agent_prompts.json`:

```json
{
  "frontend_agent": {
    "system_prompt": "You are an expert Frontend Developer...",
    "code_style": "Use functional components, TypeScript strict mode...",
    "libraries": ["React", "Next.js", "Supabase", "TailwindCSS"]
  },
  "python_ml_agent": {
    "system_prompt": "You are an expert ML Engineer...",
    "code_style": "Use type hints, docstrings, black formatting...",
    "libraries": ["PyTorch", "NumPy", "Pandas"]
  }
}
```

### Agent Templates

Create reusable templates in `templates/`:

```bash
templates/
├── nextjs-supabase/       # Frontend project template
├── pytorch-ml/            # ML project template
├── r-analysis/            # R analysis template
└── full-stack/            # Combined template
```

---

## Next Steps

1. Read [AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md) for detailed agent specifications
2. Review example projects in `examples/`
3. Customize agent prompts in `configs/`
4. Extend with additional specialized agents as needed

---

## Support and Resources

- **Claude Code Docs**: https://docs.anthropic.com/claude-code
- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Supabase Docs**: https://supabase.com/docs
- **PyTorch Docs**: https://pytorch.org/docs/
- **Next.js Docs**: https://nextjs.org/docs

---

## License

MIT License - Educational and commercial use permitted.
