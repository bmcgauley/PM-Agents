"""
Qdrant Vector Agent - Semantic Search Specialist
Handles codebase and documentation search using vector embeddings
Based on QDRANT_VECTOR_AGENT_SPEC.md
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


class QdrantVectorAgent(BaseAgent):
    """
    Qdrant Vector Agent - Semantic search specialist

    Responsibilities:
    - Index codebase and documentation in Qdrant
    - Perform semantic search for relevant code/docs
    - Retrieve context for other agents
    - Update indices when code changes
    - Manage vector collections per project

    Uses Qdrant MCP server for vector operations
    """

    def __init__(
        self,
        agent_id: str = "qdrant-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Qdrant Vector Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.QDRANT_VECTOR,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers used by qdrant agent
        self.required_mcp_servers = ["qdrant", "filesystem"]

        # Supported file types for indexing
        self.supported_extensions = [
            ".ts", ".tsx", ".js", ".jsx",  # TypeScript/JavaScript
            ".py",  # Python
            ".r", ".R", ".Rmd",  # R
            ".md", ".mdx",  # Markdown
            ".json", ".yaml", ".yml"  # Config files
        ]

        self.logger.info("Qdrant Vector Agent initialized")

    def get_system_prompt(self) -> str:
        """Get qdrant-specific system prompt"""
        return """You are the Qdrant Vector Agent, a semantic search specialist in the PM-Agents system.

**Your Role**:
- Index codebase and documentation in Qdrant vector database
- Perform semantic search for code, functions, and documentation
- Retrieve relevant context for other specialist agents
- Maintain and update vector indices
- Manage collections per project for isolation

**Core Responsibilities**:
1. **Indexing**: Parse and index source code and documentation
2. **Semantic Search**: Find similar code/docs based on embeddings
3. **Context Retrieval**: Provide relevant context to agents
4. **Index Management**: Create, update, delete collections
5. **Query Optimization**: Refine search queries for best results

**Supported File Types**:
- TypeScript/JavaScript: .ts, .tsx, .js, .jsx
- Python: .py
- R: .r, .R, .Rmd
- Markdown: .md, .mdx
- Config: .json, .yaml, .yml

**Search Strategies**:
- **Semantic**: Find conceptually similar code
- **Keyword**: Traditional text-based search
- **Hybrid**: Combine semantic + keyword for precision

**Tools Available**:
- Qdrant MCP server for vector operations
- Filesystem MCP server for file reading

**Output Format**: Always provide structured JSON with:
```json
{
  "deliverables": [
    {
      "type": "search_results | index_status",
      "name": "string",
      "content": {
        "results": [
          {
            "file_path": "string",
            "line_range": "string",
            "code_snippet": "string",
            "relevance_score": float,
            "context": "string"
          }
        ],
        "total_results": integer,
        "search_query": "string"
      }
    }
  ],
  "risks_identified": [],
  "issues": [],
  "next_steps": ["string"]
}
```

**Best Practices**:
- Use separate collections per project for isolation
- Re-index incrementally when files change
- Optimize chunk sizes for code context (500-1000 tokens)
- Include function/class signatures in embeddings
- Cache frequently accessed embeddings
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return qdrant capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "semantic_search",
                "codebase_indexing",
                "documentation_search",
                "context_retrieval",
                "collection_management"
            ],
            "supported_extensions": self.supported_extensions,
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute semantic search task"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Qdrant Vector Agent executing: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_search_prompt(task, context)
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
                task_id=self.current_task or "qdrant-task",
                status=TaskStatus.COMPLETED,
                deliverables=result_data.get("deliverables", []),
                risks_identified=result_data.get("risks_identified", []),
                issues=result_data.get("issues", []),
                next_steps=result_data.get("next_steps", []),
                execution_time_seconds=execution_time,
                metadata={"search_type": "semantic"}
            )

            self.logger.info(f"Qdrant Vector Agent completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Qdrant Vector Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "qdrant-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "high",
                    "description": f"Vector search failed: {str(e)}",
                    "resolution": "Check Qdrant connection and collection status"
                }],
                next_steps=["Verify Qdrant service is running"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_search_prompt(self, task: str, context: TaskContext) -> str:
        """Build search prompt for Claude"""
        prompt = f"""## Semantic Search Request

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Available Collections**: {context.project_id}-codebase, {context.project_id}-documentation

---

Please perform the search and provide relevant code/documentation results.
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
                    "severity": "medium",
                    "description": "Failed to parse search results",
                    "resolution": "Retry search"
                }],
                "next_steps": []
            }
