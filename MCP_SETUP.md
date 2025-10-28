# MCP Server Setup Guide

Complete guide for configuring Model Context Protocol (MCP) servers for the multi-agent system.

## Quick Start

All MCP servers should be configured at **user-level (global scope)** so they're available across all projects:

```bash
claude mcp add --scope user --transport stdio <name> -- <command>
```

---

## Essential MCP Servers

These servers are **required** for core multi-agent functionality and should be configured globally.

### 1. Filesystem Server

**Purpose**: File operations across your workspace
**Required by**: All agents
**Setup**:
```bash
claude mcp add --scope user --transport stdio filesystem -- npx -y @modelcontextprotocol/server-filesystem "C:\Users\<username>"
```

**Tools Provided**:
- Read/write files
- List directories
- Move/copy/delete files
- Search files

---

### 2. GitHub Server

**Purpose**: Repository operations and version control
**Required by**: All agents working with Git repositories
**Requires**: `GITHUB_TOKEN` (create at https://github.com/settings/tokens)
**Scopes needed**: `repo`, `read:org`, `read:user`

**Setup**:
```bash
claude mcp add --scope user --transport stdio --env GITHUB_TOKEN=ghp_your_token_here -- github npx -y @modelcontextprotocol/server-github
```

**Tools Provided**:
- Create/manage issues and PRs
- Search repositories
- Manage branches
- Access repository metadata
- Create commits and releases

---

### 3. Brave Search Server

**Purpose**: Web research and information gathering
**Required by**: Research Agent, all agents needing current information
**Requires**: `BRAVE_API_KEY` (get from https://brave.com/search/api/)

**Setup**:
```bash
claude mcp add --scope user --transport stdio --env BRAVE_API_KEY=your_key_here -- brave-search npx -y @modelcontextprotocol/server-brave-search
```

**Tools Provided**:
- Web search
- News search
- Up-to-date information retrieval

---

### 4. Memory Server

**Purpose**: Persistent memory and context storage for agents
**Required by**: All agents for maintaining state across sessions
**Requires**: None

**Setup**:
```bash
claude mcp add --scope user --transport stdio memory -- npx -y @modelcontextprotocol/server-memory
```

**Tools Provided**:
- Store/retrieve key-value pairs
- Maintain agent context
- Share information between agent invocations

---

### 5. Qdrant Vector Database (Custom)

**Purpose**: Semantic search across codebase and documentation
**Required by**: Qdrant Vector Agent, all agents needing code context
**Requires**: Qdrant running on localhost:6333 (Docker)

**Setup**:
```bash
# 1. Start Qdrant (if not already running)
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant

# 2. Install Qdrant MCP server (custom implementation)
# Already created at: C:\Users\<username>\.config\claude-code\mcp-servers\qdrant-mcp\

# 3. Add to MCP config
claude mcp add --scope user --transport stdio --env QDRANT_URL=http://localhost:6333 -- qdrant node "C:\Users\<username>\.config\claude-code\mcp-servers\qdrant-mcp\index.js"

# 4. Initialize collections for each project
python init_qdrant.py  # Creates {project}-codebase and {project}-documentation collections
```

**Tools Provided**:
- `qdrant_list_collections` - List all collections
- `qdrant_create_collection` - Create new collection for a project
- `qdrant_search` - Semantic search for similar code/docs
- `qdrant_upsert` - Add/update vectors
- `qdrant_get_collection_info` - Get collection metadata
- `qdrant_delete_collection` - Remove collections

**Collection Naming Strategy**:
- `{project-name}-codebase` - For source code vectors
- `{project-name}-documentation` - For documentation vectors

Example: `pm-agents-codebase`, `pm-agents-documentation`

---

### 6. Puppeteer Server

**Purpose**: Browser automation and web scraping
**Required by**: Browser Agent, Frontend Coder Agent for testing
**Requires**: None

**Setup**:
```bash
# Install Puppeteer globally first
npm install -g puppeteer

# Add MCP server
claude mcp add --scope user --transport stdio puppeteer -- npx -y @modelcontextprotocol/server-puppeteer
```

**Tools Provided**:
- Navigate to URLs
- Take screenshots
- Click elements
- Fill forms
- Extract page content
- Run JavaScript in browser

---

## Optional MCP Servers

Add these servers **only when needed** for specific use cases.

### Supabase Server

**Purpose**: Backend services for web apps (auth, database, storage)
**Required by**: Frontend Coder Agent (only when building Supabase apps)
**Requires**: `SUPABASE_URL`, `SUPABASE_ANON_KEY`

**When to add**:
- Building a Next.js/React app with Supabase backend
- Need database schema management
- Using Supabase Auth or Storage

**Setup**:
```bash
# Custom implementation needed - see claudcodesetup.md
```

**Skip if**: Using different backend (PostgreSQL, MongoDB, Firebase, etc.)

---

### Sequential Thinking Server

**Purpose**: Enhanced reasoning for complex multi-step problems
**Required by**: Planner Agent for complex architectural decisions
**Requires**: None

**When to add**:
- Complex system design tasks
- Multi-stage problem solving
- Advanced reasoning needed

**Setup**:
```bash
claude mcp add --scope user --transport stdio sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

### PostgreSQL/MySQL Servers

**Purpose**: Direct database operations
**Required by**: Database-specific agents
**Requires**: Database connection credentials

**When to add**:
- Need direct database queries
- Schema migrations
- Data analysis tasks
- Alternative to Supabase for backend

**Setup**:
```bash
# PostgreSQL
claude mcp add --scope user --transport stdio --env DATABASE_URL=postgresql://user:pass@localhost:5432/db -- postgres npx -y @modelcontextprotocol/server-postgres

# MySQL (if available)
claude mcp add --scope user --transport stdio --env DATABASE_URL=mysql://user:pass@localhost:3306/db -- mysql npx -y @modelcontextprotocol/server-mysql
```

---

### Slack/Discord Servers

**Purpose**: Team notifications and collaboration
**Required by**: Notification/collaboration agents (future)
**Requires**: Bot tokens

**When to add**:
- Agents need to send notifications
- Team collaboration workflows
- CI/CD notifications

**Setup**: (Future implementation)

---

### Fetch Server

**Purpose**: Simple HTTP requests
**Required by**: Alternative to Brave Search for web fetching
**Requires**: None

**When to add**:
- Need to fetch specific URLs without search
- API integration testing
- Web scraping without full browser

**Note**: Brave Search already covers most use cases. Puppeteer provides full browser capabilities.

**Setup**:
```bash
claude mcp add --scope user --transport stdio fetch -- npx -y @modelcontextprotocol/server-fetch
```

---

### Time Server

**Purpose**: Timezone conversions and scheduling
**Required by**: Agents dealing with time-sensitive operations
**Requires**: None

**When to add**:
- International team coordination
- Scheduling tasks across timezones
- Time-based automation

**Setup**:
```bash
claude mcp add --scope user --transport stdio time -- npx -y @modelcontextprotocol/server-time
```

---

## Specialized Services (Not MCP Servers)

These are services that agents launch or interact with, but are NOT MCP servers.

### TensorBoard

**Purpose**: ML experiment tracking and visualization
**Used by**: Python ML/DL Agent during model training
**Type**: Background service, NOT an MCP server

**Usage**:
```python
# Python ML/DL Agent starts TensorBoard when training
subprocess.Popen(["tensorboard", "--logdir=./logs", "--port=6006"])
```

**Install**:
```bash
pip install tensorboard
```

---

### Jupyter/JupyterLab

**Purpose**: Interactive notebooks for data analysis
**Used by**: Python ML/DL Agent, R Analytics Agent
**Type**: Interactive service, NOT an MCP server

**Install**:
```bash
pip install jupyter jupyterlab
```

---

### RStudio Server

**Purpose**: Interactive R development
**Used by**: R Analytics Agent
**Type**: IDE service, NOT an MCP server

---

## Verification

Check all configured MCP servers:

```bash
# List all configured servers with health check
claude mcp list

# View details of a specific server
claude mcp get <server-name>

# Remove a server if needed
claude mcp remove <server-name>
```

---

## Current Configuration Status

**Configured (User-Level)**:
- [x] filesystem
- [x] github
- [x] brave-search
- [x] memory
- [x] puppeteer
- [x] qdrant (custom)

**Not Yet Configured**:
- [ ] supabase (add when needed)
- [ ] sequential-thinking (add when needed)
- [ ] postgres/mysql (add when needed)
- [ ] slack/discord (future)
- [ ] fetch (optional)
- [ ] time (optional)

---

## Recommended Additions for Multi-Agent PM System

Based on your project architecture, consider adding these in the future:

### 1. Linear/Jira MCP Server (Future)

**Purpose**: Project management tool integration
**Why**: Your Coordinator Agent could integrate with PM tools
**When**: Building team workflows

### 2. Git MCP Server (Alternative to GitHub)

**Purpose**: Local Git operations without GitHub API
**Why**: Some agents may need local Git without network calls
**When**: Working offline or with non-GitHub repos

### 3. Everything Search MCP Server (Windows)

**Purpose**: Ultra-fast file searching on Windows
**Why**: Faster than glob for large codebases
**When**: Working with massive repositories

### 4. Confluence/Notion MCP Servers

**Purpose**: Documentation management
**Why**: Reporter Agent could publish docs to these platforms
**When**: Enterprise documentation workflows

---

## Architecture Notes

### Why User-Level (Global) Configuration?

All MCP servers are configured at **user-level** rather than project-level because:

1. **Reusability**: Same servers work across all projects
2. **API keys**: Store sensitive credentials once globally
3. **Consistency**: All agents have the same tool access
4. **Efficiency**: No need to reconfigure per project

### Per-Project Isolation via Qdrant Collections

While MCP servers are global, **project context is isolated** using Qdrant collections:

- Each project gets its own `{project}-codebase` collection
- Agents filter searches to the current project
- No cross-contamination between projects

### MCP vs Background Services

**MCP Servers**: Tools that agents can call via the MCP protocol
- filesystem, github, memory, qdrant, etc.

**Background Services**: Processes agents launch/monitor, NOT MCP
- TensorBoard (for ML training visualization)
- Jupyter (for interactive notebooks)
- Dev servers (npm run dev, etc.)

---

## Troubleshooting

### Server Won't Connect

```bash
# Check if MCP server package is installed
npm list -g @modelcontextprotocol/server-<name>

# Reinstall if needed
npm install -g @modelcontextprotocol/server-<name>

# Check logs
claude mcp list  # Shows connection status
```

### API Key Issues

```bash
# Verify environment variables
claude mcp get <server-name>

# Update API key
claude mcp remove <server-name>
claude mcp add --scope user --transport stdio --env KEY=new_value -- <server-name> <command>
```

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Check Qdrant API
curl http://localhost:6333/collections

# Restart Qdrant if needed
docker restart qdrant
```

---

## Next Steps

1. **Index your codebase**: Run `python index_codebase.py` to enable semantic search
2. **Test agents**: Try delegating tasks to different agents
3. **Add optional servers**: Install specialized servers as needed
4. **Monitor usage**: Use `/mcp` command to see which tools agents are using

---

## Related Documentation

- **CLAUDE.md**: Project overview and MCP server list
- **claudcodesetup.md**: Detailed initial setup instructions
- **TOOLS.md**: All required tools and installation commands
- **AGENT_ARCHITECTURE.md**: Agent specifications and communication patterns
