"""
Frontend Coder Agent - React/Next.js Development Specialist
Generates production-ready frontend code with TypeScript and Supabase integration
Based on FRONTEND_CODER_AGENT_SPEC.md
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


class FrontendCoderAgent(BaseAgent):
    """
    Frontend Coder Agent - React/Next.js development specialist

    Responsibilities:
    - Generate React components with TypeScript
    - Implement state management (Zustand/Redux)
    - Create API integrations with Supabase
    - Build authentication flows
    - Set up data fetching (React Query/SWR)
    - Apply TailwindCSS and shadcn/ui styling
    - Configure Next.js App Router
    - Ensure WCAG 2.1 AA accessibility compliance

    Uses filesystem, github, and supabase MCP servers
    """

    def __init__(
        self,
        agent_id: str = "frontend-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Frontend Coder Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.FRONTEND_CODER,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers used by frontend coder agent
        self.required_mcp_servers = ["filesystem", "github", "supabase"]

        # Supported component types
        self.component_types = [
            "ui", "layout", "form", "data-display", "interactive"
        ]

        # Tech stack defaults
        self.default_tech_stack = {
            "framework": "nextjs",
            "version": "14.2.0",
            "router_type": "app",
            "language": "typescript",
            "state_management": "zustand",
            "data_fetching": "react-query",
            "styling": "tailwindcss",
            "ui_library": "shadcn/ui",
            "authentication": "supabase",
            "database": "supabase"
        }

        self.logger.info("Frontend Coder Agent initialized with React/Next.js support")

    def get_system_prompt(self) -> str:
        """Get frontend-coder-specific system prompt"""
        return """You are the Frontend Coder Agent, a React/Next.js development specialist in the PM-Agents system.

**Your Role**:
- Generate production-ready React components with TypeScript
- Implement state management using Zustand or Redux
- Build Supabase authentication and database integrations
- Create accessible, responsive UI components
- Set up data fetching with React Query or SWR
- Apply TailwindCSS styling with shadcn/ui components
- Configure Next.js App Router and routing
- Ensure WCAG 2.1 AA accessibility compliance

**Component Types You Generate**:
- **ui**: Reusable UI components (buttons, inputs, cards, etc.)
- **layout**: Page layout components (headers, sidebars, footers)
- **form**: Form components with validation and error handling
- **data-display**: Components for displaying data (tables, lists, grids)
- **interactive**: Interactive components (modals, dropdowns, tabs)

**Core Responsibilities**:
1. **Component Development**: Create functional React components with hooks
2. **TypeScript Types**: Generate strict TypeScript interfaces and types
3. **State Management**: Implement Zustand stores or Redux slices
4. **API Integration**: Connect to Supabase for auth, database, storage
5. **Accessibility**: Add ARIA labels, keyboard navigation, semantic HTML
6. **Testing**: Generate unit and integration tests
7. **Documentation**: Create usage examples and component documentation

**Tech Stack**:
- Framework: Next.js 14+ (App Router)
- Language: TypeScript (strict mode)
- Styling: TailwindCSS 3+
- UI Library: shadcn/ui (Radix UI primitives)
- State: Zustand or Redux Toolkit
- Data Fetching: React Query or SWR
- Backend: Supabase
- Testing: Jest + React Testing Library + axe

**Best Practices**:
- Use functional components with hooks (no class components)
- TypeScript strict mode with full type coverage
- Semantic HTML and proper ARIA attributes
- Mobile-first responsive design
- Error boundaries for error handling
- Memoization for performance optimization
- Proper key props for list rendering
- Compose complex UIs from simple components
- Generate comprehensive tests with high coverage

**Output Format**: Always provide structured JSON with:
```json
{
  "deliverables": [
    {
      "type": "component|hook|utility|type|style|test",
      "path": "string (relative path)",
      "content": "string (file content)"
    }
  ],
  "components_generated": [
    {
      "name": "string",
      "path": "string",
      "type": "ui|layout|form|data-display|interactive",
      "props": [
        {
          "name": "string",
          "type": "string (TypeScript type)",
          "required": boolean,
          "description": "string"
        }
      ],
      "exports": ["string (export names)"],
      "dependencies": ["string (imported components)"]
    }
  ],
  "validation": {
    "typescript_valid": boolean,
    "accessibility_score": float (0.0-1.0),
    "tests_exist": boolean
  },
  "next_steps": ["string"]
}
```

**Error Handling**:
- Wrap errors in error boundaries
- Add proper error states to components
- Log errors appropriately
- Provide user-friendly error messages
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return frontend coder capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "react",
                "nextjs",
                "typescript",
                "supabase",
                "component_generation",
                "state_management",
                "api_integration",
                "accessibility",
                "testing"
            ],
            "component_types": self.component_types,
            "default_tech_stack": self.default_tech_stack,
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute frontend component generation task"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Frontend Coder Agent generating: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_generation_prompt(task, context)
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
                task_id=self.current_task or "frontend-task",
                status=TaskStatus.COMPLETED,
                deliverables=result_data.get("deliverables", []),
                risks_identified=result_data.get("risks_identified", []),
                issues=result_data.get("issues", []),
                next_steps=result_data.get("next_steps", []),
                execution_time_seconds=execution_time,
                metadata={
                    "components_generated": len(result_data.get("components_generated", [])),
                    "files_created": len(result_data.get("deliverables", []))
                }
            )

            self.logger.info(f"Frontend Coder Agent completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Frontend Coder Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "frontend-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Component generation failed: {str(e)}",
                    "resolution": "Check task requirements and tech stack configuration"
                }],
                next_steps=["Review error details", "Adjust component specifications"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_generation_prompt(self, task: str, context: TaskContext) -> str:
        """Build component generation prompt for Claude"""
        prompt = f"""## Frontend Component Generation Request

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}
- Current Phase: {context.current_phase}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Available Tools**: filesystem, github, supabase

**Tech Stack Defaults**:
{json.dumps(self.default_tech_stack, indent=2)}

---

Please generate the requested frontend component(s) by:
1. Analyzing the requirements and component specifications
2. Designing the component API (props, state, events)
3. Generating TypeScript component code with proper types
4. Creating any necessary hooks or utilities
5. Implementing Supabase integrations if required
6. Adding TailwindCSS styling with accessibility in mind
7. Generating comprehensive unit tests
8. Creating component documentation with examples

Ensure all output meets:
- TypeScript strict mode compliance
- WCAG 2.1 AA accessibility standards
- React/Next.js 14+ best practices
- Full test coverage
- Semantic HTML and proper ARIA attributes

Provide your response as valid JSON following the schema in your system prompt.
"""
        return prompt

    async def _call_claude_api(self, messages: List[Dict[str, str]]) -> str:
        """Call Claude API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8000,
                    system=self.get_system_prompt(),
                    messages=messages
                )
                return response.content[0].text

            except Exception as e:
                self.logger.warning(
                    f"Claude API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}"
                )
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
                "components_generated": [],
                "risks_identified": [],
                "issues": [{
                    "severity": "high",
                    "description": "Failed to parse agent response",
                    "resolution": "Retry with clearer component specifications"
                }],
                "next_steps": []
            }
