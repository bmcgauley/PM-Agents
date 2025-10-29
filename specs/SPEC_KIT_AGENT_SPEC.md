# Spec-Kit Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Project Initialization & Scaffolding
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The Spec-Kit Agent automates project initialization using the Specify CLI tool. It creates standardized project structures, configuration files, and boilerplate code based on project templates and user requirements.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: Frontend Coder Agent, Python ML/DL Agent, R Analytics Agent, TypeScript Validator Agent
- **Primary responsibility**: Rapid project scaffolding and setup automation

### 1.3 Key Responsibilities
1. **Project Initialization**: Create project structures using Specify templates
2. **Configuration Generation**: Generate package.json, tsconfig.json, requirements.txt, etc.
3. **Dependency Management**: Set up initial dependencies and dev dependencies
4. **Boilerplate Creation**: Generate starter code, components, utilities
5. **Tool Setup**: Configure linters, formatters, testing frameworks
6. **Documentation Scaffolding**: Create README, CONTRIBUTING, LICENSE files

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `SpecKitRequest`

```json
{
  "request_id": "string (UUID)",
  "task_type": "initialize|scaffold|configure|extend",
  "project_spec": {
    "project_name": "string (kebab-case)",
    "project_type": "frontend|backend|ml|analytics|fullstack",
    "framework": "nextjs|react|express|fastapi|shiny|jupyter",
    "language": "typescript|python|r|javascript",
    "features": ["auth", "database", "api", "testing", "ci/cd"],
    "template": "minimal|standard|full",
    "target_directory": "string (absolute path)"
  },
  "configuration": {
    "package_manager": "npm|pnpm|yarn|pip|conda|renv",
    "node_version": "string (e.g., '20.x')",
    "python_version": "string (e.g., '3.10')",
    "r_version": "string (e.g., '4.3')",
    "linters": ["eslint", "prettier", "black", "flake8", "styler"],
    "test_frameworks": ["jest", "pytest", "testthat", "vitest"],
    "ci_cd": "github-actions|gitlab-ci|none"
  },
  "dependencies": {
    "required": ["dependency-name@version", ...],
    "optional": ["dependency-name@version", ...],
    "dev": ["dependency-name@version", ...]
  },
  "context": {
    "existing_codebase": "boolean",
    "codebase_path": "string (if existing_codebase=true)",
    "integration_points": ["database", "auth", "api"]
  }
}
```

### 2.2 Output Schema: `SpecKitResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "success|partial|failed",
  "execution_time_seconds": "float",
  "deliverables": {
    "project_structure": {
      "root_directory": "string (absolute path)",
      "created_files": ["string (relative paths)", ...],
      "created_directories": ["string (relative paths)", ...],
      "total_files": "integer",
      "total_size_bytes": "integer"
    },
    "configurations": {
      "package_json": "object (if applicable)",
      "tsconfig_json": "object (if applicable)",
      "requirements_txt": "string (if applicable)",
      "eslintrc": "object (if applicable)",
      "prettier_config": "object (if applicable)",
      "jest_config": "object (if applicable)"
    },
    "dependencies_installed": {
      "production": ["package@version", ...],
      "development": ["package@version", ...]
    },
    "boilerplate_code": {
      "entry_point": "string (e.g., 'src/index.ts')",
      "components": ["string (paths)", ...],
      "utilities": ["string (paths)", ...],
      "tests": ["string (paths)", ...]
    },
    "documentation": {
      "readme_path": "string",
      "contributing_path": "string",
      "license_path": "string"
    }
  },
  "validation": {
    "structure_valid": "boolean",
    "dependencies_resolved": "boolean",
    "build_succeeds": "boolean",
    "tests_pass": "boolean"
  },
  "metrics": {
    "setup_time_seconds": "float",
    "files_generated": "integer",
    "lines_of_code": "integer",
    "template_used": "string"
  },
  "next_steps": [
    "string (actionable recommendations)",
    "e.g., 'Run npm install to install dependencies'",
    "e.g., 'Configure environment variables in .env'"
  ],
  "errors": [
    {
      "type": "dependency_error|template_error|filesystem_error",
      "message": "string",
      "file": "string (optional)",
      "severity": "critical|warning|info"
    }
  ]
}
```

---

## 3. MCP Tools Required

### 3.1 Essential Tools

1. **filesystem** (MCP Server)
   - **Usage**: Create directories, write configuration files, generate boilerplate code
   - **Operations**:
     - `create_directory`: Create project structure
     - `write_file`: Generate config files and boilerplate
     - `list_directory`: Validate project structure
     - `read_file`: Check existing files (if extending project)

2. **github** (MCP Server)
   - **Usage**: Initialize git repository, create .gitignore, set up GitHub Actions
   - **Operations**:
     - Initialize git repo
     - Create .gitignore from templates
     - Generate GitHub Actions workflows

### 3.2 Optional Tools

1. **brave-search** (MCP Server)
   - **Usage**: Look up latest package versions, framework best practices
   - **Operations**: Search for dependency versions, template patterns

---

## 4. Algorithms & Workflows

### 4.1 Project Initialization Algorithm

```python
def initialize_project(request: SpecKitRequest) -> SpecKitResponse:
    """
    Initialize a new project from scratch using Specify templates.

    Steps:
    1. Validate project specification
    2. Select appropriate template
    3. Create directory structure
    4. Generate configuration files
    5. Generate boilerplate code
    6. Install dependencies
    7. Initialize git repository
    8. Validate setup
    9. Return deliverables
    """

    # Step 1: Validate Specification
    validation_result = validate_project_spec(request.project_spec)
    if not validation_result.valid:
        return create_error_response(validation_result.errors)

    # Step 2: Select Template
    template = select_template(
        project_type=request.project_spec.project_type,
        framework=request.project_spec.framework,
        template_level=request.project_spec.template
    )

    # Step 3: Create Directory Structure
    structure = create_directory_structure(
        template=template,
        target_dir=request.project_spec.target_directory,
        project_name=request.project_spec.project_name
    )

    # Step 4: Generate Configuration Files
    configs = generate_configurations(
        project_type=request.project_spec.project_type,
        language=request.project_spec.language,
        configuration=request.configuration,
        structure=structure
    )

    # Step 5: Generate Boilerplate Code
    boilerplate = generate_boilerplate(
        template=template,
        features=request.project_spec.features,
        language=request.project_spec.language,
        structure=structure
    )

    # Step 6: Install Dependencies
    dependencies = install_dependencies(
        package_manager=request.configuration.package_manager,
        dependencies=request.dependencies,
        target_dir=structure.root_directory
    )

    # Step 7: Initialize Git Repository
    git_result = initialize_git(
        target_dir=structure.root_directory,
        project_name=request.project_spec.project_name
    )

    # Step 8: Validate Setup
    validation = validate_setup(
        structure=structure,
        configs=configs,
        dependencies=dependencies
    )

    # Step 9: Return Response
    return create_success_response(
        structure=structure,
        configs=configs,
        boilerplate=boilerplate,
        dependencies=dependencies,
        validation=validation
    )
```

### 4.2 Template Selection Logic

```python
def select_template(project_type: str, framework: str, template_level: str) -> Template:
    """
    Select the appropriate Specify template based on project requirements.

    Template Mapping:
    - Frontend (Next.js): @specify/nextjs-app-template
    - Frontend (React): @specify/react-vite-template
    - Backend (FastAPI): @specify/fastapi-template
    - ML (PyTorch): @specify/pytorch-research-template
    - Analytics (R): @specify/r-shiny-template
    - Fullstack: @specify/fullstack-nextjs-supabase-template
    """

    templates = {
        ("frontend", "nextjs", "minimal"): "@specify/nextjs-minimal",
        ("frontend", "nextjs", "standard"): "@specify/nextjs-app-template",
        ("frontend", "nextjs", "full"): "@specify/nextjs-supabase-full",
        ("frontend", "react", "minimal"): "@specify/react-vite-minimal",
        ("frontend", "react", "standard"): "@specify/react-vite-template",
        ("backend", "fastapi", "minimal"): "@specify/fastapi-minimal",
        ("backend", "fastapi", "standard"): "@specify/fastapi-template",
        ("ml", "jupyter", "minimal"): "@specify/jupyter-notebook",
        ("ml", "jupyter", "standard"): "@specify/pytorch-research-template",
        ("analytics", "shiny", "minimal"): "@specify/r-shiny-minimal",
        ("analytics", "shiny", "standard"): "@specify/r-shiny-template",
        ("fullstack", "nextjs", "full"): "@specify/fullstack-nextjs-supabase-template"
    }

    key = (project_type, framework, template_level)
    return templates.get(key, "@specify/generic-template")
```

### 4.3 Configuration Generation

```python
def generate_configurations(
    project_type: str,
    language: str,
    configuration: Configuration,
    structure: DirectoryStructure
) -> Dict[str, Any]:
    """
    Generate all configuration files based on project type and language.

    Configurations by Project Type:
    - TypeScript/JavaScript: package.json, tsconfig.json, eslintrc, prettier
    - Python: requirements.txt, pyproject.toml, setup.py, pytest.ini
    - R: DESCRIPTION, renv.lock, .Rprofile
    """

    configs = {}

    if language in ["typescript", "javascript"]:
        configs["package.json"] = generate_package_json(configuration)
        if language == "typescript":
            configs["tsconfig.json"] = generate_tsconfig(configuration)
        configs["eslintrc"] = generate_eslint_config(configuration)
        configs["prettier"] = generate_prettier_config(configuration)

        if "jest" in configuration.test_frameworks:
            configs["jest.config.js"] = generate_jest_config(configuration)
        elif "vitest" in configuration.test_frameworks:
            configs["vitest.config.ts"] = generate_vitest_config(configuration)

    elif language == "python":
        configs["requirements.txt"] = generate_requirements_txt(configuration)
        configs["pyproject.toml"] = generate_pyproject_toml(configuration)
        if "pytest" in configuration.test_frameworks:
            configs["pytest.ini"] = generate_pytest_config(configuration)
        configs[".flake8"] = generate_flake8_config(configuration)

    elif language == "r":
        configs["DESCRIPTION"] = generate_description_file(configuration)
        configs["renv.lock"] = generate_renv_lock(configuration)
        configs[".Rprofile"] = generate_rprofile(configuration)

    # CI/CD Configuration
    if configuration.ci_cd == "github-actions":
        configs[".github/workflows/ci.yml"] = generate_github_actions_workflow(
            project_type, language, configuration
        )

    return configs
```

### 4.4 Boilerplate Generation

```python
def generate_boilerplate(
    template: Template,
    features: List[str],
    language: str,
    structure: DirectoryStructure
) -> BoilerplateCode:
    """
    Generate starter code based on selected features.

    Feature Boilerplate:
    - auth: Authentication components, hooks, API routes
    - database: Database models, migrations, seed data
    - api: API clients, request handlers, types
    - testing: Test files, mocks, fixtures
    """

    boilerplate = BoilerplateCode(language=language)

    # Entry Point
    boilerplate.entry_point = generate_entry_point(template, language)

    # Feature-Specific Boilerplate
    for feature in features:
        if feature == "auth":
            boilerplate.add_auth_boilerplate(language)
        elif feature == "database":
            boilerplate.add_database_boilerplate(language)
        elif feature == "api":
            boilerplate.add_api_boilerplate(language)
        elif feature == "testing":
            boilerplate.add_testing_boilerplate(language)

    # Utilities
    boilerplate.utilities = generate_utilities(language)

    # Tests
    boilerplate.tests = generate_test_files(language, features)

    return boilerplate
```

---

## 5. Success Criteria

### 5.1 Functional Requirements
- ✅ Project structure created in <30 seconds
- ✅ All configuration files valid and lintable
- ✅ Dependencies install without errors
- ✅ Generated code compiles/runs without errors
- ✅ Tests pass (if testing framework configured)
- ✅ Git repository initialized with proper .gitignore

### 5.2 Quality Requirements
- ✅ 100% configuration file validity (parseable JSON/YAML/TOML)
- ✅ Generated code follows language best practices
- ✅ No security vulnerabilities in default dependencies
- ✅ README includes quick start and development instructions

### 5.3 Performance Requirements
- ✅ Setup completes in <2 minutes for standard templates
- ✅ Setup completes in <5 minutes for full templates with dependency installation
- ✅ Generated codebase size: <50MB for minimal, <200MB for full

### 5.4 Integration Requirements
- ✅ Compatible with Frontend Coder Agent for Next.js projects
- ✅ Compatible with Python ML/DL Agent for PyTorch projects
- ✅ Compatible with R Analytics Agent for Shiny projects
- ✅ TypeScript Validator Agent can lint generated code without modifications

---

## 6. Error Handling

### 6.1 Error Categories

1. **Filesystem Errors**
   - Target directory already exists
   - Insufficient permissions
   - Disk space exhausted
   - **Recovery**: Prompt user for alternative directory or cleanup

2. **Template Errors**
   - Template not found
   - Invalid template structure
   - Template version incompatible
   - **Recovery**: Fall back to generic template, warn user

3. **Dependency Errors**
   - Package not found
   - Version conflict
   - Network error during installation
   - **Recovery**: Retry with backoff, suggest manual installation

4. **Configuration Errors**
   - Invalid configuration syntax
   - Conflicting settings
   - **Recovery**: Use safe defaults, log warnings

### 6.2 Validation Checks

```python
def validate_setup(
    structure: DirectoryStructure,
    configs: Dict[str, Any],
    dependencies: DependencyInstallResult
) -> ValidationResult:
    """
    Validate the complete project setup.

    Checks:
    1. All required directories exist
    2. All configuration files are valid (parseable)
    3. Dependencies resolved without conflicts
    4. Build/compile succeeds
    5. Tests pass (if applicable)
    """

    results = ValidationResult()

    # Check directory structure
    results.structure_valid = all(
        os.path.exists(os.path.join(structure.root_directory, dir))
        for dir in structure.required_directories
    )

    # Check configuration files
    results.configs_valid = all(
        validate_config_file(config_path, config_content)
        for config_path, config_content in configs.items()
    )

    # Check dependencies
    results.dependencies_resolved = dependencies.success and len(dependencies.errors) == 0

    # Check build/compile
    results.build_succeeds = run_build_command(structure.root_directory)

    # Check tests (if test framework configured)
    if has_test_framework(configs):
        results.tests_pass = run_tests(structure.root_directory)

    return results
```

---

## 7. Implementation Notes

### 7.1 Technology Stack
- **Specify CLI**: Project scaffolding tool
- **Template Repository**: @specify/templates (npm registry)
- **Package Managers**: npm, pnpm, yarn, pip, conda, renv
- **Version Control**: Git

### 7.2 Design Patterns
- **Template Method Pattern**: Standardize project initialization flow
- **Factory Pattern**: Create project structures based on type
- **Builder Pattern**: Compose configuration files incrementally

### 7.3 Dependencies
```python
# Python Implementation Dependencies
dependencies = [
    "anthropic>=0.40.0",  # Claude API
    "pydantic>=2.0.0",    # Schema validation
    "jinja2>=3.1.0",      # Template rendering
    "toml>=0.10.2",       # TOML config parsing
    "pyyaml>=6.0",        # YAML config parsing
]
```

### 7.4 Configuration
```python
class SpecKitConfig:
    """Configuration for Spec-Kit Agent"""

    # Template repository
    template_registry = "https://registry.npmjs.org/@specify"

    # Default versions
    default_node_version = "20.x"
    default_python_version = "3.10"
    default_r_version = "4.3"

    # Timeout settings
    setup_timeout_seconds = 300  # 5 minutes
    dependency_install_timeout_seconds = 600  # 10 minutes

    # Directory structure templates
    directory_templates = {
        "frontend": ["src", "public", "tests", "docs"],
        "backend": ["src", "tests", "migrations", "docs"],
        "ml": ["src", "notebooks", "data", "models", "tests"],
        "analytics": ["R", "data", "reports", "tests"]
    }
```

### 7.5 Example Usage

```python
# Initialize a Next.js project with Supabase
request = SpecKitRequest(
    request_id="123e4567-e89b-12d3-a456-426614174000",
    task_type="initialize",
    project_spec=ProjectSpec(
        project_name="my-saas-app",
        project_type="frontend",
        framework="nextjs",
        language="typescript",
        features=["auth", "database", "api", "testing"],
        template="full",
        target_directory="/home/user/projects/my-saas-app"
    ),
    configuration=Configuration(
        package_manager="pnpm",
        node_version="20.x",
        linters=["eslint", "prettier"],
        test_frameworks=["jest"],
        ci_cd="github-actions"
    ),
    dependencies=Dependencies(
        required=[
            "next@14.2.0",
            "@supabase/supabase-js@2.43.0",
            "react@18.3.0",
            "react-dom@18.3.0"
        ],
        dev=[
            "typescript@5.4.0",
            "eslint@8.57.0",
            "prettier@3.2.0",
            "jest@29.7.0",
            "@testing-library/react@14.3.0"
        ]
    ),
    context=Context(
        existing_codebase=False
    )
)

response = spec_kit_agent.execute(request)
```

---

## 8. Testing Strategy

### 8.1 Unit Tests
- ✅ Template selection logic
- ✅ Configuration generation
- ✅ Boilerplate code generation
- ✅ Validation checks

### 8.2 Integration Tests
- ✅ Full project initialization (all project types)
- ✅ Dependency installation
- ✅ Build process
- ✅ Git repository initialization

### 8.3 End-to-End Tests
- ✅ Initialize Next.js project → build succeeds
- ✅ Initialize FastAPI project → server starts
- ✅ Initialize PyTorch project → notebook runs
- ✅ Initialize R Shiny project → app launches

---

## 9. Monitoring & Metrics

### 9.1 Key Metrics
- **Setup Time**: Average time to complete project initialization
- **Success Rate**: % of successful setups without errors
- **Template Usage**: Most popular templates
- **Dependency Install Time**: Average time for dependency installation

### 9.2 Logging
```python
# Log format
{
    "timestamp": "2025-10-28T10:00:00Z",
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "agent": "spec_kit",
    "action": "initialize_project",
    "project_type": "frontend",
    "framework": "nextjs",
    "template": "full",
    "execution_time_seconds": 45.2,
    "status": "success",
    "files_generated": 87,
    "lines_of_code": 3452
}
```

---

## 10. Future Enhancements

1. **Custom Template Creation**: Allow users to save their own project templates
2. **Interactive Setup Wizard**: CLI wizard for guided project setup
3. **Multi-Project Workspaces**: Initialize monorepos with multiple projects
4. **Cloud Integration**: Deploy infrastructure (Supabase, Vercel) during setup
5. **AI-Powered Recommendations**: Suggest optimal dependencies and configurations
6. **Live Reload**: Watch for specification changes and auto-update project

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
