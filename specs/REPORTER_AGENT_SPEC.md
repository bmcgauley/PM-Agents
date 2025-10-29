# Reporter Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Documentation & Reporting
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The Reporter Agent generates comprehensive documentation, technical reports, and diagrams for projects. It creates README files, API documentation, architecture diagrams, and progress reports throughout the development lifecycle.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: All specialist agents (documents their outputs)
- **Primary responsibility**: Documentation generation, diagram creation, report aggregation

### 1.3 Key Responsibilities
1. **README Generation**: Create comprehensive project README files
2. **API Documentation**: Generate API reference documentation
3. **Architecture Diagrams**: Create system architecture visualizations
4. **Progress Reports**: Aggregate agent outputs into status reports
5. **User Guides**: Write end-user documentation
6. **Developer Guides**: Create setup and contribution guides
7. **Release Notes**: Compile changelogs and version summaries
8. **Code Documentation**: Generate inline code documentation

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `ReporterRequest`

```json
{
  "request_id": "string (UUID)",
  "report_type": "readme|api-docs|architecture|progress|user-guide|dev-guide|release-notes|code-docs",
  "project_info": {
    "project_name": "string",
    "project_type": "frontend|backend|ml|analytics|fullstack",
    "description": "string",
    "version": "string (semver)",
    "technologies": ["nextjs", "supabase", "pytorch", ...],
    "repository_url": "string",
    "license": "MIT|Apache-2.0|GPL-3.0|custom"
  },
  "source_data": {
    "codebase_path": "string (absolute path)",
    "agent_outputs": [
      {
        "agent_name": "string",
        "deliverables": "object (agent-specific outputs)",
        "metrics": "object (performance metrics)"
      }
    ],
    "existing_docs": ["string (paths to existing documentation)", ...],
    "code_metadata": {
      "components": ["string (component names)", ...],
      "apis": ["string (API endpoint descriptions)", ...],
      "models": ["string (model names)", ...]
    }
  },
  "documentation_config": {
    "format": "markdown|html|pdf|docx",
    "style": "github|microsoft|google|custom",
    "verbosity": "minimal|standard|comprehensive",
    "include_examples": "boolean",
    "include_diagrams": "boolean",
    "include_toc": "boolean",
    "target_audience": "developers|end-users|stakeholders|mixed"
  },
  "diagram_config": {
    "diagram_types": ["architecture|sequence|component|deployment|erd|class"],
    "format": "mermaid|plantuml|drawio|svg",
    "detail_level": "high-level|detailed"
  }
}
```

### 2.2 Output Schema: `ReporterResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "success|partial|failed",
  "execution_time_seconds": "float",
  "deliverables": {
    "documents": [
      {
        "type": "readme|api-docs|user-guide|dev-guide",
        "path": "string (file path)",
        "format": "markdown|html|pdf",
        "word_count": "integer",
        "sections": ["string (section titles)", ...],
        "content": "string (file content)"
      }
    ],
    "diagrams": [
      {
        "type": "architecture|sequence|component|deployment",
        "path": "string (file path)",
        "format": "mermaid|svg|png",
        "description": "string",
        "content": "string (diagram source code)"
      }
    ],
    "api_reference": {
      "endpoints": [
        {
          "path": "string",
          "method": "GET|POST|PUT|DELETE",
          "description": "string",
          "parameters": [
            {
              "name": "string",
              "type": "string",
              "required": "boolean",
              "description": "string"
            }
          ],
          "responses": [
            {
              "status": "integer",
              "description": "string",
              "schema": "object (JSON schema)"
            }
          ],
          "example": "string (code example)"
        }
      ]
    },
    "progress_report": {
      "phases_completed": ["string", ...],
      "phases_in_progress": ["string", ...],
      "phases_pending": ["string", ...],
      "total_progress": "float (0.0-1.0)",
      "key_achievements": ["string", ...],
      "blockers": ["string", ...],
      "next_steps": ["string", ...]
    }
  },
  "validation": {
    "links_valid": "boolean",
    "markdown_valid": "boolean",
    "diagrams_render": "boolean",
    "examples_executable": "boolean"
  },
  "metrics": {
    "total_documents": "integer",
    "total_word_count": "integer",
    "total_diagrams": "integer",
    "generation_time_seconds": "float"
  },
  "recommendations": [
    "string (documentation improvements)",
    "e.g., 'Add setup instructions for Windows users'",
    "e.g., 'Include troubleshooting section for common errors'"
  ]
}
```

---

## 3. MCP Tools Required

### 3.1 Essential Tools

1. **filesystem** (MCP Server)
   - **Usage**: Read codebase, write documentation
   - **Operations**:
     - `read_file`: Read source code, existing docs
     - `write_file`: Create README, guides, diagrams
     - `list_directory`: Discover project structure

2. **qdrant** (via Supervisor delegation)
   - **Usage**: Retrieve code examples and documentation patterns
   - **Operations**: Search for similar documentation

### 3.2 Optional Tools

1. **github** (MCP Server)
   - **Usage**: Fetch repository metadata, contributors
   - **Operations**: Get repository info, list contributors

2. **brave-search** (MCP Server)
   - **Usage**: Look up documentation best practices
   - **Operations**: Search for documentation examples

---

## 4. Algorithms & Workflows

### 4.1 README Generation

```python
def generate_readme(request: ReporterRequest) -> ReporterResponse:
    """
    Generate comprehensive README.md file.

    Sections:
    1. Project Title & Badges
    2. Description
    3. Features
    4. Tech Stack
    5. Prerequisites
    6. Installation
    7. Usage
    8. Configuration
    9. API Documentation (link)
    10. Contributing
    11. Testing
    12. Deployment
    13. License
    14. Acknowledgments

    Steps:
    1. Extract project information
    2. Analyze codebase structure
    3. Generate each section
    4. Add code examples
    5. Create diagrams (if enabled)
    6. Validate links and formatting
    7. Return README content
    """

    # Step 1: Extract Project Info
    project_info = request.project_info

    # Step 2: Analyze Codebase
    codebase_analysis = analyze_codebase(
        codebase_path=request.source_data.codebase_path,
        project_type=project_info.project_type
    )

    # Step 3: Generate Sections
    readme_sections = {
        "header": generate_header(project_info),
        "description": generate_description(project_info, codebase_analysis),
        "features": generate_features(codebase_analysis, request.source_data.agent_outputs),
        "tech_stack": generate_tech_stack(project_info.technologies),
        "prerequisites": generate_prerequisites(project_info.project_type, project_info.technologies),
        "installation": generate_installation_instructions(project_info, codebase_analysis),
        "usage": generate_usage_examples(codebase_analysis, request.documentation_config.include_examples),
        "configuration": generate_configuration_guide(codebase_analysis),
        "api_docs": generate_api_docs_link(project_info),
        "contributing": generate_contributing_section(),
        "testing": generate_testing_section(codebase_analysis),
        "deployment": generate_deployment_section(project_info.project_type),
        "license": generate_license_section(project_info.license),
        "acknowledgments": generate_acknowledgments(project_info)
    }

    # Step 4: Add Code Examples
    if request.documentation_config.include_examples:
        readme_sections["usage"] = add_code_examples(
            readme_sections["usage"],
            codebase_analysis
        )

    # Step 5: Create Diagrams
    diagrams = []
    if request.documentation_config.include_diagrams:
        architecture_diagram = generate_architecture_diagram(
            codebase_analysis,
            request.diagram_config
        )
        diagrams.append(architecture_diagram)

    # Step 6: Combine Sections
    readme_content = combine_sections(
        readme_sections,
        include_toc=request.documentation_config.include_toc
    )

    # Step 7: Validate
    validation = validate_documentation(
        content=readme_content,
        diagrams=diagrams
    )

    # Step 8: Return README
    return create_response(
        status="success",
        deliverables={
            "documents": [
                {
                    "type": "readme",
                    "path": "README.md",
                    "format": "markdown",
                    "word_count": count_words(readme_content),
                    "sections": list(readme_sections.keys()),
                    "content": readme_content
                }
            ],
            "diagrams": diagrams
        },
        validation=validation
    )
```

### 4.2 README Section Examples

```python
def generate_header(project_info: ProjectInfo) -> str:
    """
    Generate README header with title, badges, and description.

    Example Output:
    ```markdown
    # My SaaS App

    [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
    [![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue.svg)](https://www.typescriptlang.org/)
    [![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

    A modern SaaS application built with Next.js, TypeScript, and Supabase.

    [Demo](https://demo.example.com) | [Documentation](https://docs.example.com) | [Report Bug](https://github.com/user/repo/issues)
    ```
    """

    badges = generate_badges(project_info.technologies, project_info.license)

    header = f"""# {project_info.project_name}

{badges}

{project_info.description}

[Demo](https://demo.example.com) | [Documentation](https://docs.example.com) | [Report Bug]({project_info.repository_url}/issues)
"""

    return header


def generate_installation_instructions(
    project_info: ProjectInfo,
    codebase_analysis: CodebaseAnalysis
) -> str:
    """
    Generate installation instructions based on project type.

    Example Output (Next.js):
    ```markdown
    ## Installation

    ### Prerequisites

    - Node.js 20.x or higher
    - pnpm 8.x or higher
    - Supabase account

    ### Steps

    1. Clone the repository

    ```bash
    git clone https://github.com/user/repo.git
    cd repo
    ```

    2. Install dependencies

    ```bash
    pnpm install
    ```

    3. Set up environment variables

    Copy `.env.example` to `.env` and fill in your Supabase credentials:

    ```bash
    cp .env.example .env
    ```

    ```env
    NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
    NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
    ```

    4. Run database migrations

    ```bash
    pnpm supabase:migrate
    ```

    5. Start the development server

    ```bash
    pnpm dev
    ```

    Open [http://localhost:3000](http://localhost:3000) in your browser.
    ```
    """

    if project_info.project_type == "frontend":
        return generate_frontend_installation(codebase_analysis)
    elif project_info.project_type == "ml":
        return generate_ml_installation(codebase_analysis)
    elif project_info.project_type == "analytics":
        return generate_analytics_installation(codebase_analysis)
    else:
        return generate_generic_installation(codebase_analysis)


def generate_usage_examples(
    codebase_analysis: CodebaseAnalysis,
    include_examples: bool
) -> str:
    """
    Generate usage examples section.

    Example Output:
    ```markdown
    ## Usage

    ### Authentication

    ```typescript
    import { useAuth } from '@/hooks/useAuth'

    function LoginForm() {
      const { signIn, loading, error } = useAuth()

      const handleSubmit = async (email: string, password: string) => {
        await signIn(email, password)
      }

      // ...
    }
    ```

    ### Data Fetching

    ```typescript
    import { useTodos } from '@/hooks/useTodos'

    function TodoList() {
      const { data: todos, isLoading } = useTodos(userId)

      if (isLoading) return <Spinner />

      return (
        <ul>
          {todos.map(todo => (
            <li key={todo.id}>{todo.title}</li>
          ))}
        </ul>
      )
    }
    ```
    ```
    """

    usage_sections = []

    # Extract main features
    features = extract_main_features(codebase_analysis)

    for feature in features:
        section = f"### {feature.name}\n\n{feature.description}\n\n"

        if include_examples:
            example = extract_code_example(feature, codebase_analysis)
            section += f"```{feature.language}\n{example}\n```\n\n"

        usage_sections.append(section)

    return "## Usage\n\n" + "\n".join(usage_sections)
```

### 4.3 Diagram Generation

```python
def generate_architecture_diagram(
    codebase_analysis: CodebaseAnalysis,
    diagram_config: DiagramConfig
) -> Diagram:
    """
    Generate system architecture diagram using Mermaid.

    Example Output (Mermaid):
    ```mermaid
    graph TB
        subgraph "Client"
            A[Next.js App]
            B[React Components]
            C[Zustand Store]
        end

        subgraph "Backend"
            D[Supabase]
            E[PostgreSQL]
            F[Storage]
            G[Auth]
        end

        subgraph "External Services"
            H[Stripe]
            I[SendGrid]
        end

        A --> B
        B --> C
        A --> D
        D --> E
        D --> F
        D --> G
        A --> H
        A --> I

        style A fill:#61DAFB
        style D fill:#3ECF8E
        style E fill:#336791
    ```
    """

    if diagram_config.format == "mermaid":
        return generate_mermaid_diagram(codebase_analysis, diagram_config.detail_level)
    elif diagram_config.format == "plantuml":
        return generate_plantuml_diagram(codebase_analysis, diagram_config.detail_level)
    else:
        return generate_mermaid_diagram(codebase_analysis, diagram_config.detail_level)


def generate_mermaid_diagram(
    codebase_analysis: CodebaseAnalysis,
    detail_level: str
) -> Diagram:
    """Generate Mermaid diagram based on codebase analysis."""

    nodes = []
    edges = []

    # Identify major components
    components = identify_components(codebase_analysis)

    for component in components:
        nodes.append(f"{component.id}[{component.name}]")

        # Add dependencies as edges
        for dep in component.dependencies:
            edges.append(f"{component.id} --> {dep.id}")

    # Generate Mermaid syntax
    mermaid_code = "graph TB\n"
    mermaid_code += "\n".join(f"    {node}" for node in nodes)
    mermaid_code += "\n"
    mermaid_code += "\n".join(f"    {edge}" for edge in edges)

    return Diagram(
        type="architecture",
        path="docs/architecture.md",
        format="mermaid",
        description="System architecture diagram",
        content=mermaid_code
    )
```

### 4.4 API Documentation Generation

```python
def generate_api_documentation(request: ReporterRequest) -> APIReference:
    """
    Generate API reference documentation from code metadata.

    Example Output (Markdown):
    ```markdown
    # API Reference

    ## Authentication

    All API requests require authentication using Bearer token.

    ```bash
    curl -H "Authorization: Bearer YOUR_TOKEN" https://api.example.com/todos
    ```

    ## Endpoints

    ### GET /api/todos

    Retrieve all todos for the authenticated user.

    **Parameters:**

    | Name | Type | Required | Description |
    |------|------|----------|-------------|
    | status | string | No | Filter by status ('active', 'completed', 'all') |
    | limit | integer | No | Maximum number of results (default: 20) |

    **Response:**

    ```json
    {
      "todos": [
        {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "title": "Buy groceries",
          "status": "active",
          "created_at": "2025-10-28T10:00:00Z"
        }
      ],
      "total": 42,
      "page": 1
    }
    ```

    **Example:**

    ```typescript
    const response = await fetch('/api/todos?status=active&limit=10')
    const data = await response.json()
    console.log(data.todos)
    ```
    ```
    """

    api_endpoints = extract_api_endpoints(request.source_data.code_metadata.apis)

    api_docs = "# API Reference\n\n"
    api_docs += generate_auth_section(api_endpoints)
    api_docs += "\n## Endpoints\n\n"

    for endpoint in api_endpoints:
        api_docs += f"### {endpoint.method} {endpoint.path}\n\n"
        api_docs += f"{endpoint.description}\n\n"

        if endpoint.parameters:
            api_docs += "**Parameters:**\n\n"
            api_docs += generate_parameter_table(endpoint.parameters)
            api_docs += "\n"

        api_docs += "**Response:**\n\n"
        api_docs += f"```json\n{json.dumps(endpoint.response_schema, indent=2)}\n```\n\n"

        if request.documentation_config.include_examples:
            api_docs += "**Example:**\n\n"
            api_docs += f"```{endpoint.example_language}\n{endpoint.example_code}\n```\n\n"

    return APIReference(api_docs=api_docs, endpoints=api_endpoints)
```

---

## 5. Success Criteria

### 5.1 Documentation Requirements
- ✅ README includes all essential sections
- ✅ Code examples are accurate and executable
- ✅ All links are valid
- ✅ Diagrams render correctly
- ✅ API documentation complete with examples
- ✅ Installation instructions work on target platforms

### 5.2 Quality Requirements
- ✅ Clear, concise writing (Flesch Reading Ease >60)
- ✅ Consistent formatting (Markdown linting passes)
- ✅ No spelling/grammar errors
- ✅ Proper code syntax highlighting

### 5.3 Completeness Requirements
- ✅ All major features documented
- ✅ Troubleshooting section for common issues
- ✅ Configuration options explained
- ✅ Contributing guidelines included

---

## 6. Implementation Notes

### 6.1 Technology Stack
- **Documentation Format**: Markdown, HTML
- **Diagrams**: Mermaid, PlantUML
- **Code Parsing**: tree-sitter, TypeScript compiler API, AST

### 6.2 Dependencies
```json
{
  "marked": "^11.0.0",
  "mermaid": "^10.0.0",
  "markdown-it": "^14.0.0",
  "remark": "^15.0.0",
  "remark-gfm": "^4.0.0"
}
```

---

## 7. Example Outputs

### 7.1 README Structure (Next.js Project)
```markdown
# My SaaS App
[badges]

## Description
## Features
## Tech Stack
## Prerequisites
## Installation
## Usage
## Configuration
## API Documentation
## Testing
## Deployment
## Contributing
## License
```

### 7.2 Progress Report
```markdown
# Project Progress Report

**Date**: 2025-10-28
**Project**: My SaaS App
**Status**: Phase 3 In Progress

## Completed Phases ✅
- Phase 1: Project Initialization
- Phase 2: Architecture Design

## In Progress 🚧
- Phase 3: Implementation (60% complete)

## Key Achievements
- Project scaffolding complete
- Authentication implemented
- Database models defined
- 45% test coverage achieved

## Blockers
- None

## Next Steps
- Complete user dashboard
- Implement payment integration
- Increase test coverage to 80%
```

---

## 8. Future Enhancements

1. **Interactive Documentation**: Generate Docusaurus or VitePress sites
2. **Video Tutorials**: Auto-generate tutorial scripts
3. **Multilingual Support**: Translate documentation to multiple languages
4. **Automated Updates**: Re-generate docs on code changes
5. **Analytics**: Track documentation page views and helpfulness

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
