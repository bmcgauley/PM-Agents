# Specify MCP Server Specification

## Overview

The **@pm-agents/mcp-specify** MCP server provides project initialization and scaffolding capabilities for the PM-Agents multi-agent system. It exposes Specify CLI operations through the Model Context Protocol, enabling agents to create new projects from templates, configure tech stacks, and generate boilerplate code.

### Purpose

- **Project initialization**: Bootstrap new projects with best practices
- **Template management**: List and use pre-configured project templates
- **Tech stack configuration**: Configure frameworks, libraries, and tools
- **Boilerplate generation**: Generate common project structures and files
- **Feature scaffolding**: Add authentication, database, API, testing, etc.

### Target Agents

- **Spec-Kit Agent**: Primary consumer, manages all project initialization
- **Coordinator Agent**: Initializes new projects based on user requirements
- **Supervisor Agent**: Scaffolds features for existing projects

---

## MCP Server Architecture

### Technology Stack

- **Runtime**: Node.js 18+ with TypeScript
- **MCP SDK**: `@modelcontextprotocol/sdk` (^1.0.0)
- **Specify CLI**: `@specify/cli` (via subprocess or programmatic API)
- **Template Engine**: Handlebars or EJS for template rendering
- **File System**: `fs-extra` for file operations
- **Transport**: stdio (standard input/output)

### Package Structure

```
@pm-agents/mcp-specify/
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── tools/
│   │   ├── templates.ts      # Template listing/info tools
│   │   ├── init.ts           # Project initialization tools
│   │   ├── features.ts       # Feature scaffolding tools
│   │   └── validation.ts     # Project validation tools
│   ├── specify/
│   │   ├── cli.ts            # Specify CLI wrapper
│   │   ├── templates.ts      # Template registry
│   │   └── config.ts         # Configuration builder
│   ├── templates/            # Built-in templates
│   │   ├── nextjs/
│   │   ├── react/
│   │   ├── fastapi/
│   │   ├── pytorch/
│   │   └── r-analytics/
│   ├── utils/
│   │   ├── validation.ts     # Input validation
│   │   ├── filesystem.ts     # File operations
│   │   └── errors.ts         # Error handling
│   └── config.ts             # Configuration management
├── tests/
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
├── package.json
├── tsconfig.json
└── README.md
```

---

## MCP Tools Specification

### 1. Template Discovery Tools

#### `specify_list_templates`

List all available project templates.

**Input Schema**: None (empty object)

```json
{}
```

**Output Schema**:
```json
{
  "templates": [
    {
      "id": "string (unique identifier)",
      "name": "string (display name)",
      "description": "string",
      "category": "frontend|backend|ml|analytics|fullstack",
      "tech_stack": {
        "framework": "string (Next.js, FastAPI, PyTorch, etc.)",
        "language": "string (TypeScript, Python, R)",
        "runtime": "string (Node.js, Python, R)"
      },
      "features": "string[] (available optional features)",
      "tags": "string[]"
    }
  ]
}
```

**Implementation**:
```typescript
interface Template {
  id: string
  name: string
  description: string
  category: 'frontend' | 'backend' | 'ml' | 'analytics' | 'fullstack'
  tech_stack: TechStack
  features: string[]
  tags: string[]
}

// Built-in templates
const TEMPLATES: Template[] = [
  {
    id: 'nextjs-supabase',
    name: 'Next.js + Supabase',
    description: 'Modern full-stack app with Next.js 14, TypeScript, Supabase, and TailwindCSS',
    category: 'fullstack',
    tech_stack: {
      framework: 'Next.js 14 (App Router)',
      language: 'TypeScript',
      runtime: 'Node.js 18+'
    },
    features: [
      'auth', 'database', 'storage', 'api', 'testing', 'ci-cd',
      'tailwindcss', 'radix-ui', 'zustand', 'react-query'
    ],
    tags: ['frontend', 'backend', 'auth', 'database', 'typescript']
  },
  {
    id: 'react-vite',
    name: 'React + Vite',
    description: 'Fast React development with Vite, TypeScript, and modern tooling',
    category: 'frontend',
    tech_stack: {
      framework: 'React 18 + Vite',
      language: 'TypeScript',
      runtime: 'Node.js 18+'
    },
    features: ['testing', 'eslint', 'prettier', 'tailwindcss', 'zustand'],
    tags: ['frontend', 'spa', 'typescript', 'vite']
  },
  {
    id: 'fastapi',
    name: 'FastAPI',
    description: 'Modern Python API with FastAPI, SQLAlchemy, and async support',
    category: 'backend',
    tech_stack: {
      framework: 'FastAPI',
      language: 'Python',
      runtime: 'Python 3.10+'
    },
    features: ['database', 'auth', 'testing', 'docker', 'alembic', 'celery'],
    tags: ['backend', 'api', 'python', 'async']
  },
  {
    id: 'pytorch-ml',
    name: 'PyTorch ML/DL',
    description: 'Machine learning project with PyTorch, TensorBoard, and Jupyter',
    category: 'ml',
    tech_stack: {
      framework: 'PyTorch 2.0+',
      language: 'Python',
      runtime: 'Python 3.10+'
    },
    features: [
      'tensorboard', 'jupyter', 'data-loaders', 'training-loops',
      'model-checkpointing', 'wandb', 'lightning'
    ],
    tags: ['ml', 'deep-learning', 'pytorch', 'python']
  },
  {
    id: 'r-analytics',
    name: 'R Analytics',
    description: 'Data analytics with R, tidyverse, ggplot2, and R Markdown',
    category: 'analytics',
    tech_stack: {
      framework: 'tidyverse + ggplot2',
      language: 'R',
      runtime: 'R 4.x'
    },
    features: [
      'rmarkdown', 'shiny', 'tidyverse', 'ggplot2', 'dplyr',
      'tidymodels', 'knitr'
    ],
    tags: ['analytics', 'data-science', 'r', 'visualization']
  }
]

async function listTemplates(): Promise<ListTemplatesResponse> {
  return { templates: TEMPLATES }
}
```

---

#### `specify_get_template_info`

Get detailed information about a specific template.

**Input Schema**:
```json
{
  "template_id": "string (required)"
}
```

**Output Schema**:
```json
{
  "template": {
    "id": "string",
    "name": "string",
    "description": "string",
    "category": "string",
    "tech_stack": "object",
    "features": "string[]",
    "file_structure": {
      "directories": "string[]",
      "files": "string[]"
    },
    "dependencies": "object",
    "setup_steps": "string[]",
    "documentation_url": "string"
  }
}
```

**Implementation**:
```typescript
async function getTemplateInfo(params: GetTemplateInfoParams): Promise<GetTemplateInfoResponse> {
  const { template_id } = params

  const template = TEMPLATES.find(t => t.id === template_id)
  if (!template) {
    throw new Error(`Template '${template_id}' not found`)
  }

  // Get detailed template information
  const templateDetails = await loadTemplateDetails(template_id)

  return {
    template: {
      ...template,
      file_structure: templateDetails.file_structure,
      dependencies: templateDetails.dependencies,
      setup_steps: templateDetails.setup_steps,
      documentation_url: `https://pm-agents.dev/templates/${template_id}`
    }
  }
}
```

---

### 2. Project Initialization Tools

#### `specify_init_project`

Initialize a new project from a template.

**Input Schema**:
```json
{
  "template_id": "string (required)",
  "project_name": "string (required, kebab-case)",
  "output_dir": "string (required, absolute path)",
  "features": "string[] (optional, features to include)",
  "config": {
    "description": "string (optional)",
    "author": "string (optional)",
    "license": "string (default: MIT)",
    "git_init": "boolean (default: true)",
    "install_dependencies": "boolean (default: true)"
  }
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "project_path": "string (absolute path to created project)",
  "files_created": "number",
  "setup_time_ms": "number",
  "next_steps": "string[]",
  "message": "string"
}
```

**Implementation**:
```typescript
async function initProject(params: InitProjectParams): Promise<InitProjectResponse> {
  const {
    template_id,
    project_name,
    output_dir,
    features = [],
    config = {}
  } = params

  // Validate project name (kebab-case)
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(project_name)) {
    throw new ValidationError('Project name must be kebab-case (lowercase, hyphens only)')
  }

  // Validate template exists
  const template = TEMPLATES.find(t => t.id === template_id)
  if (!template) {
    throw new Error(`Template '${template_id}' not found`)
  }

  // Validate features
  const invalidFeatures = features.filter(f => !template.features.includes(f))
  if (invalidFeatures.length > 0) {
    throw new ValidationError(
      `Invalid features for template '${template_id}': ${invalidFeatures.join(', ')}`
    )
  }

  // Create project directory
  const projectPath = path.join(output_dir, project_name)
  if (fs.existsSync(projectPath)) {
    throw new Error(`Directory '${projectPath}' already exists`)
  }

  fs.mkdirSync(projectPath, { recursive: true })

  const startTime = Date.now()

  // Copy template files
  const templatePath = path.join(__dirname, '../templates', template_id)
  const filesCreated = await copyTemplateFiles(templatePath, projectPath, {
    project_name,
    features,
    ...config
  })

  // Generate config files based on features
  await generateConfigFiles(projectPath, template, features, config)

  // Initialize Git repository
  if (config.git_init !== false) {
    await execAsync('git init', { cwd: projectPath })
    await execAsync('git add .', { cwd: projectPath })
    await execAsync('git commit -m "Initial commit from PM-Agents Specify template"', {
      cwd: projectPath
    })
  }

  // Install dependencies
  if (config.install_dependencies !== false) {
    await installDependencies(projectPath, template)
  }

  const setupTime = Date.now() - startTime

  return {
    success: true,
    project_path: projectPath,
    files_created: filesCreated,
    setup_time_ms: setupTime,
    next_steps: getNextSteps(template, features),
    message: `Project '${project_name}' created successfully at ${projectPath}`
  }
}

async function copyTemplateFiles(
  templatePath: string,
  projectPath: string,
  context: Record<string, any>
): Promise<number> {
  let filesCreated = 0

  // Recursively copy files with template rendering
  const files = glob.sync('**/*', {
    cwd: templatePath,
    nodir: true,
    dot: true
  })

  for (const file of files) {
    const srcPath = path.join(templatePath, file)
    const destPath = path.join(projectPath, file)

    // Create directory if needed
    fs.mkdirSync(path.dirname(destPath), { recursive: true })

    // Read template file
    const content = fs.readFileSync(srcPath, 'utf-8')

    // Render template (replace {{variable}} placeholders)
    const rendered = renderTemplate(content, context)

    // Write file
    fs.writeFileSync(destPath, rendered)
    filesCreated++
  }

  return filesCreated
}

function renderTemplate(content: string, context: Record<string, any>): string {
  return content.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return context[key] ?? match
  })
}

function getNextSteps(template: Template, features: string[]): string[] {
  const steps = []

  if (template.category === 'frontend' || template.category === 'fullstack') {
    steps.push('Run `npm install` to install dependencies (if not auto-installed)')
    steps.push('Run `npm run dev` to start development server')
  }

  if (template.category === 'backend' || template.tech_stack.language === 'Python') {
    steps.push('Create virtual environment: `python -m venv venv`')
    steps.push('Activate venv: `source venv/bin/activate` (Linux/Mac) or `venv\\Scripts\\activate` (Windows)')
    steps.push('Install dependencies: `pip install -r requirements.txt`')
  }

  if (features.includes('database')) {
    steps.push('Configure database connection in `.env` file')
    steps.push('Run database migrations: `npm run db:migrate` or `alembic upgrade head`')
  }

  if (features.includes('auth')) {
    steps.push('Configure authentication provider credentials in `.env`')
  }

  steps.push('Read README.md for detailed setup instructions')

  return steps
}
```

**Validation Rules**:
- `project_name`: Required, kebab-case, 1-64 characters
- `output_dir`: Must exist and be writable
- `template_id`: Must be a valid template ID
- `features`: Must be valid features for the selected template

---

#### `specify_scaffold_feature`

Add a feature to an existing project.

**Input Schema**:
```json
{
  "project_path": "string (required, path to existing project)",
  "feature": "string (required, feature to add)",
  "template_id": "string (optional, infer from project if not provided)",
  "config": "object (optional, feature-specific configuration)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "feature": "string",
  "files_created": "string[]",
  "files_modified": "string[]",
  "dependencies_added": "string[]",
  "message": "string",
  "next_steps": "string[]"
}
```

**Example Features**:
- `auth` - Add authentication (Supabase Auth, NextAuth.js, etc.)
- `database` - Add database integration (Prisma, SQLAlchemy, etc.)
- `api` - Add API routes/endpoints
- `testing` - Add testing framework (Jest, Pytest, etc.)
- `ci-cd` - Add GitHub Actions workflows
- `docker` - Add Dockerfile and docker-compose.yml

**Implementation**:
```typescript
async function scaffoldFeature(params: ScaffoldFeatureParams): Promise<ScaffoldFeatureResponse> {
  const { project_path, feature, template_id, config = {} } = params

  // Validate project exists
  if (!fs.existsSync(project_path)) {
    throw new Error(`Project directory '${project_path}' not found`)
  }

  // Detect project type if template_id not provided
  const detectedTemplateId = template_id || await detectProjectType(project_path)

  const template = TEMPLATES.find(t => t.id === detectedTemplateId)
  if (!template) {
    throw new Error(`Could not determine project type. Provide template_id.`)
  }

  // Validate feature is available for template
  if (!template.features.includes(feature)) {
    throw new Error(
      `Feature '${feature}' not available for template '${detectedTemplateId}'. ` +
      `Available features: ${template.features.join(', ')}`
    )
  }

  // Load feature scaffolding template
  const featurePath = path.join(__dirname, '../templates', detectedTemplateId, 'features', feature)
  if (!fs.existsSync(featurePath)) {
    throw new Error(`Feature '${feature}' template not found`)
  }

  // Copy feature files
  const filesCreated: string[] = []
  const featureFiles = glob.sync('**/*', { cwd: featurePath, nodir: true, dot: true })

  for (const file of featureFiles) {
    const srcPath = path.join(featurePath, file)
    const destPath = path.join(project_path, file)

    // Create directory if needed
    fs.mkdirSync(path.dirname(destPath), { recursive: true })

    // Read and render template
    const content = fs.readFileSync(srcPath, 'utf-8')
    const rendered = renderTemplate(content, config)

    fs.writeFileSync(destPath, rendered)
    filesCreated.push(file)
  }

  // Modify existing files (e.g., update package.json, add imports)
  const filesModified = await modifyFilesForFeature(project_path, feature, template, config)

  // Add dependencies
  const dependenciesAdded = await addDependenciesForFeature(project_path, feature, template)

  return {
    success: true,
    feature: feature,
    files_created: filesCreated,
    files_modified: filesModified,
    dependencies_added: dependenciesAdded,
    message: `Feature '${feature}' added successfully`,
    next_steps: getFeatureNextSteps(feature, template)
  }
}

async function detectProjectType(projectPath: string): Promise<string | null> {
  // Check for Next.js
  if (fs.existsSync(path.join(projectPath, 'next.config.js')) ||
      fs.existsSync(path.join(projectPath, 'next.config.ts'))) {
    return 'nextjs-supabase'
  }

  // Check for React
  if (fs.existsSync(path.join(projectPath, 'vite.config.ts'))) {
    return 'react-vite'
  }

  // Check for FastAPI
  if (fs.existsSync(path.join(projectPath, 'main.py')) &&
      fs.existsSync(path.join(projectPath, 'requirements.txt'))) {
    const requirements = fs.readFileSync(path.join(projectPath, 'requirements.txt'), 'utf-8')
    if (requirements.includes('fastapi')) {
      return 'fastapi'
    }
  }

  // Check for PyTorch
  if (fs.existsSync(path.join(projectPath, 'requirements.txt'))) {
    const requirements = fs.readFileSync(path.join(projectPath, 'requirements.txt'), 'utf-8')
    if (requirements.includes('torch')) {
      return 'pytorch-ml'
    }
  }

  // Check for R
  if (fs.existsSync(path.join(projectPath, 'DESCRIPTION')) ||
      fs.existsSync(path.join(projectPath, 'analysis.Rmd'))) {
    return 'r-analytics'
  }

  return null
}
```

---

### 3. Configuration Tools

#### `specify_generate_config`

Generate configuration files for a project (e.g., .env, config.yaml).

**Input Schema**:
```json
{
  "project_path": "string (required)",
  "config_type": "env|yaml|json|toml",
  "variables": {
    "key": "value"
  }
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "config_file": "string (path to created file)",
  "message": "string"
}
```

---

#### `specify_update_dependencies`

Update project dependencies (package.json, requirements.txt, etc.).

**Input Schema**:
```json
{
  "project_path": "string (required)",
  "dependencies": {
    "dependency_name": "version"
  },
  "dependency_type": "production|development|optional"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "dependencies_updated": "string[]",
  "message": "string"
}
```

---

### 4. Validation Tools

#### `specify_validate_project`

Validate project structure and configuration.

**Input Schema**:
```json
{
  "project_path": "string (required)",
  "template_id": "string (optional)"
}
```

**Output Schema**:
```json
{
  "valid": "boolean",
  "template_id": "string (detected or provided)",
  "issues": [
    {
      "severity": "error|warning|info",
      "message": "string",
      "file": "string (optional)",
      "suggestion": "string (optional)"
    }
  ],
  "missing_files": "string[]",
  "missing_dependencies": "string[]"
}
```

**Validation Checks**:
- Required files exist (package.json, requirements.txt, etc.)
- Dependencies installed
- Configuration files present (.env.example, etc.)
- Project structure matches template
- No conflicting dependencies

---

## Configuration

### Environment Variables

```bash
# Templates directory (optional, defaults to built-in)
SPECIFY_TEMPLATES_DIR=~/.specify/templates

# Default output directory (optional)
SPECIFY_OUTPUT_DIR=~/projects

# Auto-install dependencies (optional)
SPECIFY_AUTO_INSTALL=true

# Git initialization (optional)
SPECIFY_GIT_INIT=true
```

### Configuration File

`mcp-specify-config.json`:
```json
{
  "templates": {
    "directory": "~/.specify/templates",
    "custom_templates": []
  },
  "defaults": {
    "output_dir": "~/projects",
    "git_init": true,
    "install_dependencies": true,
    "license": "MIT"
  },
  "logging": {
    "level": "info",
    "log_file_operations": true
  }
}
```

---

## Error Handling

### Error Categories

#### 1. Template Errors
- **Cause**: Template not found or invalid
- **Recovery**: None (fail immediately)
- **User Message**: "Template '{id}' not found. Available templates: {list}"

#### 2. File System Errors
- **Cause**: Directory already exists, permission denied
- **Recovery**: None (fail immediately)
- **User Message**: "Directory '{path}' already exists. Choose a different name or location."

#### 3. Validation Errors
- **Cause**: Invalid project name, unsupported feature
- **Recovery**: None (fail immediately)
- **User Message**: "Project name must be kebab-case (e.g., 'my-project')"

#### 4. Dependency Installation Errors
- **Cause**: npm/pip install fails
- **Recovery**: Skip dependency installation, return warning
- **User Message**: "Dependency installation failed. Run manually: npm install"

### Error Response Schema

```json
{
  "error": {
    "code": "TEMPLATE_ERROR|FILESYSTEM_ERROR|VALIDATION_ERROR|DEPENDENCY_ERROR",
    "message": "string",
    "details": "object (optional)",
    "suggestion": "string (optional)"
  }
}
```

---

## Testing Strategy

### Unit Tests

**Test Coverage Targets**: 90%+ for all tool functions

**Key Test Cases**:
```typescript
describe('specify_init_project', () => {
  it('creates project from template', async () => {
    const result = await initProject({
      template_id: 'nextjs-supabase',
      project_name: 'test-project',
      output_dir: '/tmp',
      features: ['auth', 'database']
    })
    expect(result.success).toBe(true)
    expect(fs.existsSync('/tmp/test-project')).toBe(true)
  })

  it('rejects invalid project names', async () => {
    await expect(initProject({
      template_id: 'nextjs-supabase',
      project_name: 'Invalid Name',
      output_dir: '/tmp'
    })).rejects.toThrow(ValidationError)
  })

  it('rejects duplicate project names', async () => {
    await initProject({
      template_id: 'nextjs-supabase',
      project_name: 'test-project',
      output_dir: '/tmp'
    })
    await expect(initProject({
      template_id: 'nextjs-supabase',
      project_name: 'test-project',
      output_dir: '/tmp'
    })).rejects.toThrow(/already exists/)
  })
})

describe('specify_scaffold_feature', () => {
  it('adds feature to existing project', async () => {
    // Create project first
    await initProject({
      template_id: 'nextjs-supabase',
      project_name: 'test-project',
      output_dir: '/tmp',
      features: []
    })

    // Add auth feature
    const result = await scaffoldFeature({
      project_path: '/tmp/test-project',
      feature: 'auth'
    })

    expect(result.success).toBe(true)
    expect(result.files_created.length).toBeGreaterThan(0)
  })
})
```

### Integration Tests

**Test Cases**:
1. Create Next.js project → Verify file structure → Run build
2. Create FastAPI project → Verify dependencies → Run tests
3. Create PyTorch project → Verify TensorBoard integration → Run training
4. Add auth feature → Verify files created → Verify dependencies added

### Performance Benchmarks

**Target Metrics**:
- Project initialization: <2 minutes (with dependency installation)
- Feature scaffolding: <30 seconds
- Template rendering: <1 second for 100 files

---

## Installation

### NPM Package

```bash
npm install -g @pm-agents/mcp-specify
```

### Claude Code MCP Configuration

Add to `~/.claude/mcp_servers.json`:

```json
{
  "mcpServers": {
    "specify": {
      "command": "npx",
      "args": ["-y", "@pm-agents/mcp-specify"],
      "env": {
        "SPECIFY_OUTPUT_DIR": "~/projects",
        "SPECIFY_AUTO_INSTALL": "true"
      }
    }
  }
}
```

### Verification

```bash
# Test MCP server
echo '{"method":"tools/list"}' | npx @pm-agents/mcp-specify

# Expected output: List of all specify_* tools
```

---

## Integration with PM-Agents

### Spec-Kit Agent Usage

```python
# Spec-Kit Agent using MCP tool
async def initialize_project(self, request: SpecKitRequest) -> SpecKitResponse:
    # 1. Select template based on project type
    template_id = self.select_template(
        project_type=request.project_spec.project_type,
        framework=request.project_spec.framework
    )

    # 2. Initialize project via MCP
    result = await self.mcp_call("specify_init_project", {
        "template_id": template_id,
        "project_name": request.project_spec.project_name,
        "output_dir": request.output_dir,
        "features": request.project_spec.features,
        "config": {
            "description": request.project_spec.description,
            "author": "PM-Agents",
            "git_init": True,
            "install_dependencies": True
        }
    })

    # 3. Scaffold additional features if needed
    for feature in request.project_spec.custom_features:
        await self.mcp_call("specify_scaffold_feature", {
            "project_path": result["project_path"],
            "feature": feature,
            "template_id": template_id
        })

    # 4. Validate project structure
    validation = await self.mcp_call("specify_validate_project", {
        "project_path": result["project_path"],
        "template_id": template_id
    })

    if not validation["valid"]:
        # Handle validation issues
        pass

    return SpecKitResponse(
        success=True,
        project_path=result["project_path"],
        files_created=result["files_created"],
        next_steps=result["next_steps"]
    )
```

---

## Future Enhancements

### Post-MVP Features

1. **Custom Templates**: Allow users to create and share custom templates
2. **Template Marketplace**: Community-contributed templates
3. **Interactive Mode**: TUI for guided project setup
4. **Cloud Integration**: Deploy to Vercel, Netlify, Railway automatically
5. **Monorepo Support**: Initialize monorepo projects (Nx, Turborepo)
6. **Migration Tools**: Migrate between frameworks (e.g., CRA → Vite)
7. **Code Generation**: Generate components, routes, models from schemas

---

## Security Considerations

### Input Validation
- Sanitize project names (prevent path traversal)
- Validate template IDs (prevent arbitrary file access)
- Limit feature combinations (prevent conflicts)

### File System Access
- Only write to designated output directories
- Validate paths are within allowed directories
- No execution of arbitrary code during template rendering

---

## Monitoring and Logging

### Metrics to Track
- Projects created by template
- Feature usage frequency
- Setup time by template
- Success rate

### Logging Format
```json
{
  "timestamp": "2025-10-29T10:15:30Z",
  "level": "info",
  "tool": "specify_init_project",
  "template_id": "nextjs-supabase",
  "project_name": "my-app",
  "setup_time_ms": 45000,
  "files_created": 32
}
```

---

## Support and Maintenance

### Documentation
- API reference: https://pm-agents.dev/mcp/specify
- Template docs: https://pm-agents.dev/templates
- Troubleshooting: https://pm-agents.dev/docs/troubleshooting/specify

### Issue Reporting
- GitHub Issues: https://github.com/pm-agents/mcp-specify/issues

### Versioning
- Semantic versioning (semver)
- Template versioning separate from MCP server

---

## Implementation Checklist

- [ ] Set up TypeScript project structure
- [ ] Create built-in templates (5 templates)
- [ ] Implement template rendering engine
- [ ] Implement all 8 MCP tools
- [ ] Add input validation for all tools
- [ ] Add error handling with rollback on failure
- [ ] Write unit tests (90%+ coverage)
- [ ] Write integration tests
- [ ] Create template documentation
- [ ] Write README with usage examples
- [ ] Publish to npm registry
- [ ] Add to Claude Code MCP documentation
- [ ] Create video tutorial
- [ ] Set up CI/CD pipeline (GitHub Actions)

---

**Last Updated**: 2025-10-29
**Status**: Specification Complete - Ready for Implementation
