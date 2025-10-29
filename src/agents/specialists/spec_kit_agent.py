"""
Spec-Kit Agent - Project Initialization Specialist
Handles project bootstrapping using Specify CLI
Based on SPEC_KIT_AGENT_SPEC.md
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


class SpecKitAgent(BaseAgent):
    """
    Spec-Kit Agent - Project initialization specialist

    Responsibilities:
    - Initialize projects using Specify CLI
    - Generate project templates and boilerplate
    - Configure tech stacks and dependencies
    - Set up development environments
    - Generate configuration files

    Uses Specify MCP server for project scaffolding
    """

    def __init__(
        self,
        agent_id: str = "spec-kit-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Spec-Kit Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.SPEC_KIT,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers used by spec-kit agent
        self.required_mcp_servers = ["specify", "filesystem", "github"]

        # Available tech stack templates
        self.templates = {
            "nextjs-supabase": "Next.js 14 + Supabase + TypeScript + TailwindCSS",
            "react-spa": "React SPA + Vite + TypeScript",
            "pytorch-ml": "PyTorch + TensorBoard + Jupyter",
            "r-analytics": "R + tidyverse + R Markdown + Shiny",
            "nodejs-api": "Node.js + Express + TypeScript",
            "python-api": "FastAPI + Pydantic + SQLAlchemy"
        }

        self.logger.info("Spec-Kit Agent initialized with templates")

    def get_system_prompt(self) -> str:
        """Get spec-kit-specific system prompt"""
        return """You are the Spec-Kit Agent, a project initialization specialist in the PM-Agents system.

**Your Role**:
- Initialize new projects using Specify CLI
- Generate project templates and boilerplate code
- Configure tech stacks and dependencies
- Set up development environments
- Create configuration files (tsconfig, package.json, etc.)

**Available Templates**:
- **nextjs-supabase**: Next.js 14 + Supabase + TypeScript + TailwindCSS
- **react-spa**: React SPA + Vite + TypeScript
- **pytorch-ml**: PyTorch + TensorBoard + Jupyter notebooks
- **r-analytics**: R + tidyverse + R Markdown + Shiny
- **nodejs-api**: Node.js + Express + TypeScript
- **python-api**: FastAPI + Pydantic + SQLAlchemy

**Core Responsibilities**:
1. **Template Selection**: Choose appropriate template based on requirements
2. **Project Generation**: Use Specify CLI to generate project structure
3. **Configuration**: Set up package.json, tsconfig.json, pyproject.toml, etc.
4. **Dependency Management**: Install required packages and libraries
5. **Documentation**: Generate initial README and setup instructions

**Tools Available**:
- Specify MCP server for project scaffolding
- Filesystem MCP server for file operations
- GitHub MCP server for repository initialization

**Output Format**: Always provide structured JSON with:
```json
{
  "deliverables": [
    {
      "type": "project_structure",
      "name": "generated_project",
      "content": {
        "template_used": "string",
        "files_created": ["string"],
        "directories_created": ["string"],
        "dependencies_installed": ["string"]
      }
    }
  ],
  "risks_identified": [
    {"severity": "string", "category": "string", "description": "string", "mitigation": "string"}
  ],
  "issues": [
    {"severity": "string", "description": "string", "resolution": "string"}
  ],
  "next_steps": ["string"]
}
```

**Best Practices**:
- Use TypeScript strict mode for frontend projects
- Enable ESLint and Prettier for code quality
- Set up Git hooks for pre-commit checks
- Include .env.example for environment variables
- Generate comprehensive README with setup instructions
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return spec-kit capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "project_initialization",
                "template_generation",
                "tech_stack_configuration",
                "boilerplate_generation",
                "dependency_management"
            ],
            "templates": list(self.templates.keys()),
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute project initialization task"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Spec-Kit Agent initializing project: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_initialization_prompt(task, context)
                }
            ]

            # Call Claude API
            response = await self._call_claude_api(messages)

            # Parse response
            result_data = self._parse_response(response)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Create result
            result = TaskResult(
                task_id=self.current_task or "spec-kit-task",
                status=TaskStatus.COMPLETED,
                deliverables=result_data.get("deliverables", []),
                risks_identified=result_data.get("risks_identified", []),
                issues=result_data.get("issues", []),
                next_steps=result_data.get("next_steps", []),
                execution_time_seconds=execution_time,
                metadata={"template_used": result_data.get("template_used")}
            )

            self.logger.info(f"Spec-Kit Agent completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Spec-Kit Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "spec-kit-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Project initialization failed: {str(e)}",
                    "resolution": "Check Specify CLI installation and permissions"
                }],
                next_steps=["Retry with manual project setup"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_initialization_prompt(self, task: str, context: TaskContext) -> str:
        """Build initialization prompt for Claude"""
        prompt = f"""## Project Initialization Request

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Available Templates**: {', '.join(self.templates.keys())}

---

Please initialize the project by:
1. Selecting the most appropriate template
2. Generating project structure and files
3. Configuring dependencies and tools
4. Creating initial documentation

Provide your response as valid JSON following the schema in your system prompt.
"""
        return prompt

    async def _call_claude_api(self, messages: List[Dict[str, str]]) -> str:
        """Call Claude API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
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
                "deliverables": [],
                "risks_identified": [],
                "issues": [{
                    "severity": "high",
                    "description": "Failed to parse agent response",
                    "resolution": "Retry task"
                }],
                "next_steps": []
            }
