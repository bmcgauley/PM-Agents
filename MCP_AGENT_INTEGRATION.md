# MCP Server and Agent Integration Reference

## Overview

This document provides a comprehensive mapping of **MCP servers** to **PM-Agents** and their specific tool usage patterns. It serves as the definitive reference for understanding which agents require which MCP tools and how they integrate.

### MCP Servers in PM-Agents Ecosystem

**Essential (Global)**:
1. **filesystem** - File operations (read, write, edit, list directories)
2. **github** - Repository operations (create repos, PRs, issues)
3. **brave-search** - Web research and documentation lookup
4. **memory** - Persistent agent memory and context
5. **puppeteer** - Browser automation for E2E testing and scraping

**Custom (PM-Agents Specific)**:
6. **@pm-agents/mcp-qdrant** - Semantic search and vector operations
7. **@pm-agents/mcp-tensorboard** - ML/DL experiment monitoring
8. **@pm-agents/mcp-specify** - Project initialization and scaffolding

**Optional/Feature-Specific**:
9. **supabase** - Database and auth operations (Frontend Coder Agent only)

---

## Agent-to-MCP Server Mapping

### Tier 1: Orchestration Agent

#### Coordinator Agent

**Purpose**: Top-level orchestration and task delegation

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)
- ✅ **memory** (Essential)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read project files for context
- `list_directory` - Understand project structure
- `directory_tree` - Get full project overview

**github**:
- `create_repository` - Initialize new projects
- `get_file_contents` - Retrieve GitHub-hosted files
- `create_issue` - Track tasks and blockers

**memory**:
- `create_entities` - Store project context
- `create_relations` - Link related concepts
- `search_nodes` - Retrieve relevant context

**@pm-agents/mcp-qdrant**:
- `qdrant_search` - Find relevant code/documentation
- `qdrant_list_collections` - Check available knowledge bases

**Usage Pattern**:
```python
# Coordinator retrieves context before delegating to Planner
async def coordinate_task(self, user_request: UserRequest):
    # 1. Retrieve relevant context from vector DB
    context = await self.mcp_call("qdrant_search", {
        "collection_name": f"{self.project_name}-context",
        "query_vector": self.embed(user_request.description),
        "limit": 5
    })

    # 2. Store task in memory
    await self.mcp_call("create_entities", {
        "entities": [{
            "name": user_request.task_id,
            "entityType": "task",
            "observations": [user_request.description]
        }]
    })

    # 3. Delegate to Planner
    plan = await self.delegate_to_planner(user_request, context)
```

---

### Tier 2: Planning Agent

#### Planner Agent

**Purpose**: Strategic planning and task decomposition

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **brave-search** (Essential)
- ✅ **memory** (Essential)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read existing code/documentation
- `list_directory` - Survey project structure

**brave-search**:
- `brave_web_search` - Research best practices and patterns

**memory**:
- `search_nodes` - Retrieve past plans and decisions
- `create_entities` - Store planning decisions

**@pm-agents/mcp-qdrant**:
- `qdrant_search` - Find similar past tasks
- `qdrant_get_collection_info` - Check knowledge base status

**Usage Pattern**:
```python
# Planner researches best practices before creating plan
async def create_plan(self, task: Task):
    # 1. Search for similar past tasks
    similar_tasks = await self.mcp_call("qdrant_search", {
        "collection_name": f"{self.project_name}-tasks",
        "query_vector": self.embed(task.description),
        "limit": 3
    })

    # 2. Research best practices
    research = await self.mcp_call("brave_web_search", {
        "query": f"{task.type} best practices {task.tech_stack}"
    })

    # 3. Decompose task
    subtasks = self.decompose_task(task, similar_tasks, research)

    # 4. Store plan in memory
    await self.mcp_call("create_entities", {
        "entities": [{
            "name": f"plan-{task.task_id}",
            "entityType": "plan",
            "observations": [json.dumps(subtasks)]
        }]
    })
```

---

### Tier 3: Supervisor Agent

#### Supervisor Agent

**Purpose**: Tactical management and specialist coordination

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)
- ✅ **memory** (Essential)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read code produced by specialists
- `write_file` - Aggregate results
- `list_directory` - Monitor file changes

**github**:
- `create_pull_request` - Create PRs for completed work
- `create_issue` - Track blockers and issues
- `list_issues` - Monitor open issues

**memory**:
- `create_entities` - Store task assignments
- `create_relations` - Link tasks to agents
- `search_nodes` - Retrieve agent capabilities

**@pm-agents/mcp-qdrant**:
- `qdrant_search` - Find relevant code for context
- `qdrant_upsert` - Index completed work

**Usage Pattern**:
```python
# Supervisor assigns task to specialist
async def assign_task(self, subtask: SubTask, agent: SpecialistAgent):
    # 1. Retrieve relevant context
    context = await self.mcp_call("qdrant_search", {
        "collection_name": f"{self.project_name}-codebase",
        "query_vector": self.embed(subtask.description),
        "limit": 10
    })

    # 2. Execute task with specialist
    result = await agent.execute_task(subtask, context)

    # 3. Index completed work
    await self.mcp_call("qdrant_upsert", {
        "collection_name": f"{self.project_name}-codebase",
        "points": [{
            "id": subtask.id,
            "vector": self.embed(result.code),
            "payload": {
                "file_path": result.file_path,
                "content": result.code,
                "agent": agent.name
            }
        }]
    })

    # 4. Create PR if needed
    if result.ready_for_review:
        await self.mcp_call("create_pull_request", {
            "owner": self.repo_owner,
            "repo": self.repo_name,
            "title": f"Implement {subtask.description}",
            "head": f"feature/{subtask.id}",
            "base": "main",
            "body": result.summary
        })
```

---

### Tier 4: Specialist Agents

#### 1. Spec-Kit Agent

**Purpose**: Project initialization using Specify CLI

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)
- ✅ **@pm-agents/mcp-specify** (Custom)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**filesystem**:
- `list_directory` - Verify project structure
- `read_text_file` - Check generated files

**github**:
- `create_repository` - Initialize repo
- `push_files` - Push initial commit

**@pm-agents/mcp-specify**:
- `specify_list_templates` - List available templates
- `specify_init_project` - Initialize project from template
- `specify_scaffold_feature` - Add features to project
- `specify_validate_project` - Validate project structure

**@pm-agents/mcp-qdrant**:
- `qdrant_create_collection` - Create project knowledge base
- `qdrant_upsert` - Index project templates and patterns

**Example Workflow**:
```python
async def initialize_project(self, request: SpecKitRequest):
    # 1. Select template
    templates = await self.mcp_call("specify_list_templates", {})
    template = self.select_template(templates, request.project_spec)

    # 2. Initialize project
    result = await self.mcp_call("specify_init_project", {
        "template_id": template.id,
        "project_name": request.project_spec.project_name,
        "output_dir": request.output_dir,
        "features": request.project_spec.features
    })

    # 3. Create GitHub repository
    repo = await self.mcp_call("create_repository", {
        "name": request.project_spec.project_name,
        "description": request.project_spec.description,
        "private": False
    })

    # 4. Create vector collection for project
    await self.mcp_call("qdrant_create_collection", {
        "name": f"{request.project_spec.project_name}-codebase",
        "vector_size": 384,
        "distance": "Cosine"
    })

    return result
```

---

#### 2. Qdrant Vector Agent

**Purpose**: Semantic search and codebase indexing

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read code files for indexing
- `list_directory` - Traverse codebase
- `directory_tree` - Get full codebase structure

**@pm-agents/mcp-qdrant** (ALL TOOLS):
- `qdrant_list_collections` - List available collections
- `qdrant_create_collection` - Create new collections
- `qdrant_get_collection_info` - Get collection metadata
- `qdrant_delete_collection` - Delete collections
- `qdrant_search` - Semantic search
- `qdrant_search_batch` - Batch search queries
- `qdrant_upsert` - Insert/update vectors
- `qdrant_delete_points` - Delete specific points
- `qdrant_scroll` - Paginated retrieval
- `qdrant_count` - Count points with filter

**Example Workflow**:
```python
async def index_codebase(self, project_path: str, project_name: str):
    collection_name = f"{project_name}-codebase"

    # 1. Create collection
    await self.mcp_call("qdrant_create_collection", {
        "name": collection_name,
        "vector_size": 384,
        "distance": "Cosine"
    })

    # 2. Get all code files
    file_tree = await self.mcp_call("directory_tree", {
        "path": project_path
    })

    code_files = self.filter_code_files(file_tree)

    # 3. Process files in batches
    for batch in self.batch(code_files, size=100):
        points = []

        for file_path in batch:
            # Read file
            content = await self.mcp_call("read_text_file", {
                "path": file_path
            })

            # Parse and chunk
            chunks = self.parse_code_file(content, file_path)

            # Generate embeddings
            for chunk in chunks:
                embedding = self.generate_embedding(chunk.content)
                points.append({
                    "id": chunk.id,
                    "vector": embedding,
                    "payload": {
                        "file_path": file_path,
                        "content": chunk.content,
                        "type": chunk.type,
                        "language": chunk.language
                    }
                })

        # 4. Upsert batch
        await self.mcp_call("qdrant_upsert", {
            "collection_name": collection_name,
            "points": points,
            "wait": True
        })

async def search_codebase(self, query: str, project_name: str):
    # Generate query embedding
    query_vector = self.generate_embedding(query)

    # Search Qdrant
    results = await self.mcp_call("qdrant_search", {
        "collection_name": f"{project_name}-codebase",
        "query_vector": query_vector,
        "limit": 10,
        "score_threshold": 0.7,
        "with_payload": True
    })

    return results
```

---

#### 3. Frontend Coder Agent

**Purpose**: React/Next.js code generation

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)
- ✅ **@pm-agents/mcp-qdrant** (Custom)
- ✅ **supabase** (Optional, feature-specific)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read existing components
- `write_file` - Create new components
- `edit_file` - Update existing files
- `list_directory` - Survey component structure

**github**:
- `create_branch` - Create feature branch
- `push_files` - Push component code
- `create_pull_request` - Create PR for review

**@pm-agents/mcp-qdrant**:
- `qdrant_search` - Find similar components
- `qdrant_upsert` - Index new components

**supabase** (when using Supabase features):
- `supabase_create_table` - Create database tables
- `supabase_generate_types` - Generate TypeScript types
- `supabase_configure_auth` - Set up authentication

**Example Workflow**:
```python
async def generate_component(self, request: FrontendCoderRequest):
    # 1. Retrieve context (similar components)
    context = await self.mcp_call("qdrant_search", {
        "collection_name": f"{request.project_name}-codebase",
        "query_vector": self.embed(request.component_spec.description),
        "limit": 5,
        "filter": {"type": "component"}
    })

    # 2. Generate component code
    component_code = self.generate_react_component(
        request.component_spec,
        context
    )

    # 3. Write component file
    component_path = self.resolve_component_path(request)
    await self.mcp_call("write_file", {
        "path": component_path,
        "content": component_code
    })

    # 4. Generate tests
    test_code = self.generate_component_tests(request.component_spec)
    test_path = component_path.replace('.tsx', '.test.tsx')
    await self.mcp_call("write_file", {
        "path": test_path,
        "content": test_code
    })

    # 5. If using Supabase, generate types
    if request.project_spec.uses_supabase:
        types = await self.mcp_call("supabase_generate_types", {
            "project_ref": request.supabase_project_ref
        })
        await self.mcp_call("write_file", {
            "path": "types/database.types.ts",
            "content": types
        })

    # 6. Index component
    await self.mcp_call("qdrant_upsert", {
        "collection_name": f"{request.project_name}-codebase",
        "points": [{
            "id": f"component-{request.component_spec.name}",
            "vector": self.embed(component_code),
            "payload": {
                "file_path": component_path,
                "content": component_code,
                "type": "component",
                "framework": "react"
            }
        }]
    })
```

---

#### 4. Python ML/DL Agent

**Purpose**: PyTorch model development and training

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)
- ✅ **@pm-agents/mcp-tensorboard** (Custom)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read training scripts
- `write_file` - Create model definitions
- `edit_file` - Update training code
- `list_directory` - Check logs/checkpoints

**github**:
- `push_files` - Push model code
- `create_pull_request` - Create PR with experiments

**@pm-agents/mcp-tensorboard** (ALL TOOLS):
- `tensorboard_start_server` - Launch TensorBoard
- `tensorboard_stop_server` - Stop TensorBoard
- `tensorboard_list_servers` - List active servers
- `tensorboard_get_server_status` - Check server status
- `tensorboard_list_experiments` - List training runs
- `tensorboard_get_scalars` - Get training metrics
- `tensorboard_get_latest_metrics` - Check convergence
- `tensorboard_get_histograms` - Get weight distributions
- `tensorboard_get_images` - Get logged images
- `tensorboard_get_model_graph` - Get model architecture
- `tensorboard_export_scalars` - Export metrics to CSV
- `tensorboard_export_summary` - Export training summary

**@pm-agents/mcp-qdrant**:
- `qdrant_search` - Find similar model architectures
- `qdrant_upsert` - Index model experiments

**Example Workflow**:
```python
async def train_model(self, config: MLTrainingConfig):
    # 1. Start TensorBoard
    tb_server = await self.mcp_call("tensorboard_start_server", {
        "logdir": config.logdir,
        "port": 6006,
        "name": f"{config.project_name}-training"
    })

    print(f"TensorBoard: {tb_server['url']}")

    # 2. Search for similar models
    context = await self.mcp_call("qdrant_search", {
        "collection_name": "ml-models",
        "query_vector": self.embed(config.model_description),
        "limit": 3
    })

    # 3. Generate model code
    model_code = self.generate_model_architecture(config, context)
    await self.mcp_call("write_file", {
        "path": f"{config.project_path}/model.py",
        "content": model_code
    })

    # 4. Generate training loop
    training_code = self.generate_training_loop(config)
    await self.mcp_call("write_file", {
        "path": f"{config.project_path}/train.py",
        "content": training_code
    })

    # 5. Run training (in background)
    # Training writes TensorBoard logs automatically

    # 6. Monitor training progress
    while not self.check_convergence():
        await asyncio.sleep(60)

        latest_metrics = await self.mcp_call("tensorboard_get_latest_metrics", {
            "logdir": config.logdir,
            "tags": ["loss", "accuracy", "val_loss", "val_accuracy"]
        })

        print(f"Loss: {latest_metrics['metrics'][0]['latest_value']}")

    # 7. Export training summary
    summary = await self.mcp_call("tensorboard_export_summary", {
        "logdir": config.logdir
    })

    # 8. Index experiment
    await self.mcp_call("qdrant_upsert", {
        "collection_name": "ml-models",
        "points": [{
            "id": config.experiment_id,
            "vector": self.embed(model_code),
            "payload": {
                "model_architecture": config.model_type,
                "final_loss": summary["summary"]["metrics"][0]["final_value"],
                "training_time": summary["summary"]["duration_seconds"]
            }
        }]
    })

    # 9. Keep TensorBoard running for inspection
    # (or stop with tensorboard_stop_server)
```

---

#### 5. R Analytics Agent

**Purpose**: Data analytics with R/tidyverse

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read data files and R scripts
- `write_file` - Create R scripts and R Markdown
- `list_directory` - Check data files

**github**:
- `push_files` - Push analysis code
- `create_pull_request` - Share analysis results

**@pm-agents/mcp-qdrant**:
- `qdrant_search` - Find similar analyses
- `qdrant_upsert` - Index analysis scripts

**Example Workflow**:
```python
async def create_analysis(self, request: RAnalyticsRequest):
    # 1. Find similar analyses
    context = await self.mcp_call("qdrant_search", {
        "collection_name": "r-analyses",
        "query_vector": self.embed(request.analysis_description),
        "limit": 3
    })

    # 2. Generate R script for data wrangling
    wrangling_code = self.generate_tidyverse_pipeline(
        request.data_spec,
        context
    )

    # 3. Generate ggplot2 visualizations
    viz_code = self.generate_ggplot2_visualizations(request.viz_spec)

    # 4. Create R Markdown report
    rmarkdown_content = self.generate_rmarkdown_report(
        request.report_spec,
        wrangling_code,
        viz_code
    )

    await self.mcp_call("write_file", {
        "path": f"{request.project_path}/analysis.Rmd",
        "content": rmarkdown_content
    })

    # 5. Index analysis
    await self.mcp_call("qdrant_upsert", {
        "collection_name": "r-analyses",
        "points": [{
            "id": request.analysis_id,
            "vector": self.embed(rmarkdown_content),
            "payload": {
                "analysis_type": request.analysis_type,
                "data_source": request.data_spec.source
            }
        }]
    })
```

---

#### 6. TypeScript Validator Agent

**Purpose**: Code quality validation

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read code files for validation
- `list_directory` - Find all files to validate
- `write_file` - Generate validation reports

**github**:
- `create_issue` - Report quality issues
- `create_pull_request_review` - Review PRs

**Example Workflow**:
```python
async def validate_code(self, request: ValidationRequest):
    # 1. Get all TypeScript files
    files = await self.mcp_call("list_directory", {
        "path": request.project_path
    })

    ts_files = [f for f in files if f.endswith('.ts') or f.endswith('.tsx')]

    # 2. Run validation pipeline
    type_errors = self.run_type_checking(ts_files)
    lint_errors = self.run_linting(ts_files)
    test_coverage = self.run_tests(request.project_path)
    security_issues = self.run_security_scan(request.project_path)

    # 3. Generate report
    report = self.generate_validation_report(
        type_errors,
        lint_errors,
        test_coverage,
        security_issues
    )

    await self.mcp_call("write_file", {
        "path": f"{request.project_path}/validation-report.md",
        "content": report
    })

    # 4. Create GitHub issues for critical errors
    for error in type_errors.critical:
        await self.mcp_call("create_issue", {
            "owner": request.repo_owner,
            "repo": request.repo_name,
            "title": f"Type Error: {error.message}",
            "body": f"File: {error.file}\\nLine: {error.line}\\n\\n{error.details}",
            "labels": ["bug", "type-error"]
        })
```

---

#### 7. Research Agent

**Purpose**: Technical research and documentation lookup

**Required MCP Servers**:
- ✅ **brave-search** (Essential)
- ✅ **github** (Essential)
- ✅ **filesystem** (Essential)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**brave-search**:
- `brave_web_search` - Search documentation and tutorials
- `brave_local_search` - Find local resources (if applicable)

**github**:
- `search_repositories` - Find relevant open-source projects
- `search_code` - Find code examples
- `get_file_contents` - Read code from GitHub repos

**filesystem**:
- `write_file` - Save research findings

**@pm-agents/mcp-qdrant**:
- `qdrant_upsert` - Index research findings

**Example Workflow**:
```python
async def research_topic(self, request: ResearchRequest):
    # 1. Web search
    web_results = await self.mcp_call("brave_web_search", {
        "query": f"{request.topic} {request.tech_stack} best practices 2024"
    })

    # 2. GitHub code search
    code_examples = await self.mcp_call("search_code", {
        "q": f"{request.topic} language:{request.language}"
    })

    # 3. Retrieve top code examples
    examples = []
    for result in code_examples["items"][:3]:
        content = await self.mcp_call("get_file_contents", {
            "owner": result["repository"]["owner"]["login"],
            "repo": result["repository"]["name"],
            "path": result["path"]
        })
        examples.append({
            "repo": result["repository"]["full_name"],
            "path": result["path"],
            "content": content
        })

    # 4. Synthesize findings
    synthesis = self.synthesize_research(
        web_results,
        code_examples,
        examples
    )

    # 5. Save research report
    await self.mcp_call("write_file", {
        "path": f"{request.output_path}/research-{request.topic}.md",
        "content": synthesis
    })

    # 6. Index findings
    await self.mcp_call("qdrant_upsert", {
        "collection_name": "research-findings",
        "points": [{
            "id": request.research_id,
            "vector": self.embed(synthesis),
            "payload": {
                "topic": request.topic,
                "tech_stack": request.tech_stack
            }
        }]
    })
```

---

#### 8. Browser Agent

**Purpose**: Web automation and E2E testing

**Required MCP Servers**:
- ✅ **puppeteer** (Essential)
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)

**MCP Tools Used**:

**puppeteer** (ALL TOOLS):
- `puppeteer_navigate` - Navigate to URLs
- `puppeteer_screenshot` - Capture screenshots
- `puppeteer_click` - Click elements
- `puppeteer_fill` - Fill form inputs
- `puppeteer_select` - Select dropdown options
- `puppeteer_hover` - Hover over elements
- `puppeteer_evaluate` - Execute JavaScript

**filesystem**:
- `write_file` - Save screenshots and test results

**github**:
- `create_issue` - Report test failures

**Example Workflow**:
```python
async def run_e2e_test(self, test_spec: E2ETestSpec):
    # 1. Navigate to app
    await self.mcp_call("puppeteer_navigate", {
        "url": test_spec.base_url
    })

    # 2. Execute test steps
    for step in test_spec.steps:
        if step.action == "click":
            await self.mcp_call("puppeteer_click", {
                "selector": step.selector
            })
        elif step.action == "fill":
            await self.mcp_call("puppeteer_fill", {
                "selector": step.selector,
                "value": step.value
            })
        elif step.action == "screenshot":
            screenshot = await self.mcp_call("puppeteer_screenshot", {
                "name": step.name,
                "selector": step.selector
            })
            await self.mcp_call("write_file", {
                "path": f"screenshots/{step.name}.png",
                "content": screenshot
            })

    # 3. Verify assertions
    passed = self.verify_assertions(test_spec.assertions)

    if not passed:
        # Create issue for failed test
        await self.mcp_call("create_issue", {
            "owner": test_spec.repo_owner,
            "repo": test_spec.repo_name,
            "title": f"E2E Test Failed: {test_spec.test_name}",
            "body": "Test failed. See attached screenshot.",
            "labels": ["test-failure"]
        })
```

---

#### 9. Reporter Agent

**Purpose**: Documentation generation

**Required MCP Servers**:
- ✅ **filesystem** (Essential)
- ✅ **github** (Essential)
- ✅ **@pm-agents/mcp-qdrant** (Custom)

**MCP Tools Used**:

**filesystem**:
- `read_text_file` - Read code for documentation
- `write_file` - Create README, API docs
- `list_directory` - Survey project structure

**github**:
- `push_files` - Push documentation
- `create_pull_request` - Submit docs for review

**@pm-agents/mcp-qdrant**:
- `qdrant_search` - Find similar documentation patterns

**Example Workflow**:
```python
async def generate_readme(self, project_path: str, project_name: str):
    # 1. Find similar README patterns
    context = await self.mcp_call("qdrant_search", {
        "collection_name": "documentation-templates",
        "query_vector": self.embed(f"README for {project_name}"),
        "limit": 3
    })

    # 2. Analyze project structure
    file_tree = await self.mcp_call("directory_tree", {
        "path": project_path
    })

    # 3. Read package.json or similar
    config = await self.mcp_call("read_text_file", {
        "path": f"{project_path}/package.json"
    })

    # 4. Generate README
    readme_content = self.generate_readme_content(
        project_name,
        config,
        file_tree,
        context
    )

    await self.mcp_call("write_file", {
        "path": f"{project_path}/README.md",
        "content": readme_content
    })

    # 5. Generate architecture diagrams (Mermaid)
    diagram = self.generate_architecture_diagram(file_tree)
    await self.mcp_call("write_file", {
        "path": f"{project_path}/docs/architecture.md",
        "content": f"# Architecture\\n\\n```mermaid\\n{diagram}\\n```"
    })
```

---

## Summary Tables

### Agent → MCP Server Matrix

| Agent | filesystem | github | brave-search | memory | puppeteer | qdrant | tensorboard | specify | supabase |
|-------|-----------|--------|--------------|--------|-----------|--------|-------------|---------|----------|
| Coordinator | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Planner | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Supervisor | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Spec-Kit | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
| Qdrant Vector | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Frontend Coder | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ (optional) |
| Python ML/DL | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| R Analytics | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| TypeScript Validator | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Research | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Browser | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Reporter | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |

---

### MCP Tool Usage by Category

#### Read Operations
- `filesystem.read_text_file` - Most agents
- `filesystem.list_directory` - Most agents
- `filesystem.directory_tree` - Qdrant Vector, Reporter
- `github.get_file_contents` - Research Agent
- `qdrant.qdrant_search` - Most agents

#### Write Operations
- `filesystem.write_file` - Most agents
- `filesystem.edit_file` - Frontend Coder
- `qdrant.qdrant_upsert` - Most agents indexing content
- `github.push_files` - Agents creating code

#### Search Operations
- `qdrant.qdrant_search` - Context retrieval (most agents)
- `brave_web_search` - Research, Planner
- `github.search_code` - Research Agent

#### Automation
- `puppeteer.*` - Browser Agent only
- `tensorboard.*` - Python ML/DL Agent only
- `specify.*` - Spec-Kit Agent only

---

## Integration Patterns

### Pattern 1: Context Retrieval Before Task Execution

**Used by**: All specialist agents

```python
# Retrieve relevant context from vector DB
context = await self.mcp_call("qdrant_search", {
    "collection_name": f"{project_name}-codebase",
    "query_vector": self.embed(task.description),
    "limit": 10
})

# Use context to inform task execution
result = self.execute_task_with_context(task, context)
```

---

### Pattern 2: Index After Creation

**Used by**: All agents creating new artifacts

```python
# Create artifact (code, documentation, etc.)
artifact = self.create_artifact(spec)

# Write to filesystem
await self.mcp_call("write_file", {...})

# Index for future searches
await self.mcp_call("qdrant_upsert", {
    "collection_name": collection_name,
    "points": [{
        "id": artifact.id,
        "vector": self.embed(artifact.content),
        "payload": artifact.metadata
    }]
})
```

---

### Pattern 3: Monitor → Analyze → Report

**Used by**: Python ML/DL Agent with TensorBoard

```python
# Start monitoring
tb_server = await self.mcp_call("tensorboard_start_server", {...})

# Perform task (training)
train_result = self.train_model(config)

# Analyze results
metrics = await self.mcp_call("tensorboard_get_latest_metrics", {...})

# Export summary
summary = await self.mcp_call("tensorboard_export_summary", {...})

# Report findings
return TrainingReport(metrics, summary, tb_server["url"])
```

---

### Pattern 4: Initialize → Configure → Validate

**Used by**: Spec-Kit Agent

```python
# Initialize project
result = await self.mcp_call("specify_init_project", {...})

# Add features
for feature in custom_features:
    await self.mcp_call("specify_scaffold_feature", {...})

# Validate structure
validation = await self.mcp_call("specify_validate_project", {...})

if not validation["valid"]:
    # Handle validation issues
    pass
```

---

## Best Practices

### 1. Error Handling

All agents should implement retry logic for transient MCP errors:

```python
async def mcp_call_with_retry(self, tool: str, params: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await self.mcp_call(tool, params)
        except MCPConnectionError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

### 2. Batch Operations

When performing multiple similar operations, use batch tools when available:

```python
# ❌ Bad: Multiple individual calls
for query in queries:
    results = await self.mcp_call("qdrant_search", {"query_vector": query, ...})

# ✅ Good: Single batch call
results = await self.mcp_call("qdrant_search_batch", {"queries": queries, ...})
```

---

### 3. Cleanup

Agents should clean up resources (TensorBoard servers, browser instances):

```python
try:
    # Start resource
    server = await self.mcp_call("tensorboard_start_server", {...})

    # Use resource
    result = self.perform_task()

finally:
    # Always cleanup
    await self.mcp_call("tensorboard_stop_server", {"server_id": server["server_id"]})
```

---

## Configuration Reference

### Global MCP Configuration

Add to `~/.claude/mcp_servers.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\brian"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "BSA..."
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "qdrant": {
      "command": "npx",
      "args": ["-y", "@pm-agents/mcp-qdrant"],
      "env": {
        "QDRANT_URL": "http://localhost:6333"
      }
    },
    "tensorboard": {
      "command": "npx",
      "args": ["-y", "@pm-agents/mcp-tensorboard"]
    },
    "specify": {
      "command": "npx",
      "args": ["-y", "@pm-agents/mcp-specify"]
    }
  }
}
```

---

## Testing MCP Integration

### Verification Script

```bash
#!/bin/bash

# Test each MCP server
echo "Testing filesystem..."
echo '{"method":"tools/list"}' | npx @modelcontextprotocol/server-filesystem

echo "Testing github..."
echo '{"method":"tools/list"}' | npx @modelcontextprotocol/server-github

echo "Testing brave-search..."
echo '{"method":"tools/list"}' | npx @modelcontextprotocol/server-brave-search

echo "Testing memory..."
echo '{"method":"tools/list"}' | npx @modelcontextprotocol/server-memory

echo "Testing puppeteer..."
echo '{"method":"tools/list"}' | npx @modelcontextprotocol/server-puppeteer

echo "Testing qdrant..."
echo '{"method":"tools/list"}' | npx @pm-agents/mcp-qdrant

echo "Testing tensorboard..."
echo '{"method":"tools/list"}' | npx @pm-agents/mcp-tensorboard

echo "Testing specify..."
echo '{"method":"tools/list"}' | npx @pm-agents/mcp-specify
```

---

**Last Updated**: 2025-10-29
**Status**: Complete - Ready for Implementation
