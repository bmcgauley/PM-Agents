"""
Reporter Agent - Documentation & Reporting Specialist
Generates comprehensive documentation, technical reports, and diagrams for projects
Based on REPORTER_AGENT_SPEC.md
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
import logging

from src.core.base_agent import (
    BaseAgent,
    AgentType,
    TaskContext,
    TaskResult,
    TaskStatus
)


class ReporterAgent(BaseAgent):
    """
    Reporter Agent - Documentation & Reporting specialist

    Responsibilities:
    - Generate comprehensive README.md files
    - Create API reference documentation
    - Design architecture diagrams (Mermaid, PlantUML)
    - Compile progress reports from agent outputs
    - Write user guides and tutorials
    - Produce developer contribution guides
    - Generate release notes and changelogs
    - Create inline code documentation (JSDoc, Sphinx)

    Uses filesystem MCP server for file operations and qdrant for documentation patterns
    """

    def __init__(
        self,
        agent_id: str = "reporter-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Reporter Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.REPORTER,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers required by reporter agent
        self.required_mcp_servers = ["filesystem"]

        # Supported report types
        self.report_types = [
            "readme", "api-docs", "architecture", "progress",
            "user-guide", "dev-guide", "release-notes", "code-docs"
        ]

        # Documentation formats
        self.documentation_formats = [
            "markdown", "html", "pdf", "docx"
        ]

        # Documentation styles
        self.documentation_styles = [
            "github", "microsoft", "google", "custom"
        ]

        # Diagram types
        self.diagram_types = [
            "architecture", "sequence", "component", "deployment", "erd", "class"
        ]

        # Diagram formats
        self.diagram_formats = [
            "mermaid", "plantuml", "drawio", "svg"
        ]

        # README sections (standard order)
        self.readme_sections = [
            "header", "description", "features", "tech_stack",
            "prerequisites", "installation", "usage", "configuration",
            "api_docs", "contributing", "testing", "deployment",
            "license", "acknowledgments"
        ]

        self.logger.info("Reporter Agent initialized with documentation generation capabilities")

    def get_system_prompt(self) -> str:
        """Get documentation-specific system prompt"""
        return """You are the Reporter Agent, a documentation and reporting specialist in the PM-Agents system.

**Your Role**:
- Generate comprehensive, professional project documentation
- Create clear, well-structured README files
- Produce detailed API reference documentation
- Design system architecture diagrams (Mermaid, PlantUML)
- Compile progress reports from agent outputs
- Write user-friendly guides and tutorials
- Produce developer contribution guides
- Generate release notes and changelogs

**Core Responsibilities**:
1. **README Generation**: Create comprehensive project README with all essential sections
2. **API Documentation**: Generate complete API reference with examples
3. **Architecture Diagrams**: Design visual system architecture representations
4. **Progress Reports**: Aggregate agent outputs into status reports
5. **User Guides**: Write end-user documentation and tutorials
6. **Developer Guides**: Create setup, contribution, and development guides
7. **Release Notes**: Compile changelogs and version summaries
8. **Code Documentation**: Generate inline documentation (JSDoc, Sphinx, roxygen2)

**README Structure** (Standard Order):
1. **Header**: Project title, badges, one-line description
2. **Description**: Detailed project overview (2-3 paragraphs)
3. **Features**: Bullet list of key features
4. **Tech Stack**: Technologies used with versions
5. **Prerequisites**: System requirements, dependencies
6. **Installation**: Step-by-step setup instructions
7. **Usage**: Code examples demonstrating main features
8. **Configuration**: Environment variables, config files
9. **API Documentation**: Link to detailed API docs
10. **Contributing**: How to contribute (link to CONTRIBUTING.md)
11. **Testing**: How to run tests
12. **Deployment**: Deployment instructions
13. **License**: License information
14. **Acknowledgments**: Credits, inspirations

**Documentation Best Practices**:
- Use clear, concise language (Flesch Reading Ease >60)
- Include code examples for all major features
- Provide working commands (bash, npm, etc.)
- Use consistent formatting (Markdown linting)
- Add badges for build status, coverage, version
- Include table of contents for long docs
- Link to external resources appropriately
- Use proper code syntax highlighting
- Add troubleshooting section for common issues
- Keep installation steps sequential and clear

**Diagram Generation**:
- **Architecture Diagrams**: Show high-level system components
- **Sequence Diagrams**: Illustrate API call flows
- **Component Diagrams**: Detail module relationships
- **Deployment Diagrams**: Show infrastructure layout
- **ERD**: Database schema visualization
- Use Mermaid for GitHub-compatible diagrams
- Use PlantUML for detailed technical diagrams

**API Documentation Format**:
For each endpoint, include:
- HTTP method and path
- Description of functionality
- Parameters (name, type, required, description)
- Request body schema (if applicable)
- Response schema with examples
- Status codes and error responses
- Code examples in relevant language (TypeScript, Python, cURL)

**Progress Report Format**:
- Project name and date
- Current phase and overall status
- Completed phases (with checkmarks)
- In-progress phases (with percentage)
- Pending phases
- Key achievements
- Current blockers
- Next steps

**Output Format**: Always provide structured JSON with:
```json
{
  "deliverables": {
    "documents": [
      {
        "type": "readme|api-docs|user-guide|dev-guide",
        "path": "string (file path)",
        "format": "markdown|html|pdf",
        "word_count": "integer",
        "sections": ["string (section titles)", ...],
        "content": "string (full document content)"
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
          "parameters": [...],
          "responses": [...],
          "example": "string"
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
  "recommendations": ["string (documentation improvements)", ...]
}
```

**Markdown Example (README Header)**:
```markdown
# My SaaS App

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue.svg)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

A modern SaaS application built with Next.js, TypeScript, and Supabase.

[Demo](https://demo.example.com) | [Documentation](https://docs.example.com) | [Report Bug](https://github.com/user/repo/issues)

## Features

- 🔐 Authentication with Supabase Auth
- 📊 Real-time dashboard with data visualization
- 💳 Stripe payment integration
- 🌐 Multi-tenant support
- 📱 Responsive mobile design
```

**Mermaid Diagram Example (Architecture)**:
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
    end

    A --> B
    B --> C
    A --> D
    D --> E
    D --> F
```

**Quality Standards**:
- All links must be valid
- Code examples must be executable
- Markdown must pass linting
- Diagrams must render correctly
- Installation steps must work on target platforms
- No spelling or grammar errors
- Consistent formatting throughout
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return reporter capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "readme_generation",
                "api_documentation",
                "architecture_diagrams",
                "progress_reporting",
                "user_guides",
                "developer_guides",
                "release_notes",
                "code_documentation"
            ],
            "report_types": self.report_types,
            "documentation_formats": self.documentation_formats,
            "documentation_styles": self.documentation_styles,
            "diagram_types": self.diagram_types,
            "diagram_formats": self.diagram_formats,
            "readme_sections": self.readme_sections,
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute documentation/reporting task (README, API docs, diagrams, etc.)"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Reporter Agent executing: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_reporter_prompt(task, context)
                }
            ]

            # Call Claude API
            response = await self._call_claude_api(messages)

            # Parse response
            result_data = self._parse_response(response)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Extract deliverables from documentation results
            deliverables = self._extract_deliverables(result_data)

            # Create result
            result = TaskResult(
                task_id=self.current_task or "reporter-task",
                status=TaskStatus.COMPLETED,
                deliverables=deliverables,
                risks_identified=result_data.get("risks_identified", []),
                issues=result_data.get("issues", []),
                next_steps=result_data.get("recommendations", []),
                execution_time_seconds=execution_time,
                metadata={
                    "deliverables": result_data.get("deliverables", {}),
                    "validation": result_data.get("validation", {}),
                    "metrics": result_data.get("metrics", {}),
                    "recommendations": result_data.get("recommendations", [])
                }
            )

            metrics = result_data.get("metrics", {})
            self.logger.info(f"Reporter Agent completed in {execution_time:.2f}s - {metrics.get('total_documents', 0)} docs, {metrics.get('total_diagrams', 0)} diagrams")
            return result

        except Exception as e:
            self.logger.error(f"Reporter Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "reporter-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Documentation generation task failed: {str(e)}",
                    "resolution": "Check project metadata and template availability"
                }],
                next_steps=["Review error details", "Verify filesystem access", "Retry"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_reporter_prompt(self, task: str, context: TaskContext) -> str:
        """Build documentation prompt for Claude"""
        prompt = f"""## Documentation & Reporting Task

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}
- Current Phase: {context.current_phase}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Previous Outputs**: {json.dumps(context.previous_outputs, indent=2) if context.previous_outputs else "None"}

**Documentation Configuration**:
- Supported Report Types: {', '.join(self.report_types)}
- Documentation Formats: {', '.join(self.documentation_formats)}
- Documentation Styles: {', '.join(self.documentation_styles)}
- Diagram Types: {', '.join(self.diagram_types)}
- Diagram Formats: {', '.join(self.diagram_formats)}
- README Sections: {', '.join(self.readme_sections)}

**Available MCP Tools**: {', '.join(context.mcp_tools_available)}

---

Please complete the documentation task by:
1. Identifying the report type (readme, api-docs, architecture, progress, user-guide, dev-guide, release-notes, code-docs)
2. Gathering project information (name, type, technologies, version)
3. Analyzing codebase structure (if applicable)
4. Generating documentation sections in correct order:
   - **README**: All standard sections with examples
   - **API Docs**: Complete endpoint reference with examples
   - **Architecture**: System design diagrams (Mermaid/PlantUML)
   - **Progress Report**: Phase status, achievements, blockers
   - **User Guide**: Step-by-step tutorials for end users
   - **Dev Guide**: Setup, contribution guidelines for developers
5. Creating diagrams (architecture, sequence, component, etc.)
6. Adding code examples for all major features
7. Validating all links and markdown syntax
8. Ensuring code examples are executable
9. Providing recommendations for improvements

**Documentation Quality**:
- Clear, concise language (Flesch Reading Ease >60)
- Consistent formatting (Markdown linting passes)
- Working installation instructions
- Runnable code examples
- Valid links
- Properly rendered diagrams
- No spelling/grammar errors
- Proper code syntax highlighting

**Diagram Best Practices**:
- Use Mermaid for GitHub compatibility
- Label all components clearly
- Show data flow direction
- Use subgraphs for logical grouping
- Apply consistent styling
- Keep diagrams simple and focused

Provide your response as valid JSON following the schema in your system prompt.
"""
        return prompt

    def _extract_deliverables(self, result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract deliverables from documentation results"""
        deliverables = []

        deliverable_data = result_data.get("deliverables", {})

        # Documents
        documents = deliverable_data.get("documents", [])
        for doc in documents:
            deliverables.append({
                "type": "document",
                "name": doc.get("type", "document").upper().replace("-", " "),
                "path": doc.get("path", ""),
                "format": doc.get("format", "markdown"),
                "word_count": doc.get("word_count", 0),
                "sections": doc.get("sections", []),
                "status": "completed"
            })

        # Diagrams
        diagrams = deliverable_data.get("diagrams", [])
        for diagram in diagrams:
            deliverables.append({
                "type": "diagram",
                "name": f"{diagram.get('type', 'diagram').capitalize()} Diagram",
                "path": diagram.get("path", ""),
                "format": diagram.get("format", "mermaid"),
                "description": diagram.get("description", ""),
                "status": "completed"
            })

        # API Reference
        api_reference = deliverable_data.get("api_reference", {})
        if api_reference and api_reference.get("endpoints"):
            deliverables.append({
                "type": "api_reference",
                "name": "API Reference Documentation",
                "description": f"{len(api_reference.get('endpoints', []))} endpoints documented",
                "endpoint_count": len(api_reference.get("endpoints", [])),
                "status": "completed"
            })

        # Progress Report
        progress_report = deliverable_data.get("progress_report", {})
        if progress_report:
            deliverables.append({
                "type": "progress_report",
                "name": "Project Progress Report",
                "description": f"{progress_report.get('total_progress', 0)*100:.0f}% complete",
                "phases_completed": len(progress_report.get("phases_completed", [])),
                "phases_in_progress": len(progress_report.get("phases_in_progress", [])),
                "phases_pending": len(progress_report.get("phases_pending", [])),
                "status": "completed"
            })

        return deliverables

    async def _call_claude_api(self, messages: List[Dict[str, str]]) -> str:
        """Call Claude API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    system=self.get_system_prompt(),
                    messages=messages
                )
                return response.content[0].text

            except Exception as e:
                self.logger.warning(f"Claude API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay_seconds * (attempt + 1))
                else:
                    raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response"""
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                json_str = response

            return json.loads(json_str)

        except json.JSONDecodeError:
            return {
                "deliverables": {
                    "documents": [],
                    "diagrams": [],
                    "api_reference": {},
                    "progress_report": {}
                },
                "validation": {
                    "links_valid": False,
                    "markdown_valid": False,
                    "diagrams_render": False,
                    "examples_executable": False
                },
                "metrics": {
                    "total_documents": 0,
                    "total_word_count": 0,
                    "total_diagrams": 0,
                    "generation_time_seconds": 0
                },
                "recommendations": [],
                "risks_identified": [],
                "issues": [{
                    "severity": "high",
                    "description": "Failed to parse Reporter agent response",
                    "resolution": "Retry documentation generation with simplified requirements"
                }],
                "next_steps": []
            }
