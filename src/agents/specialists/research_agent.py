"""
Research Agent - Technical Research & Information Gathering Specialist
Performs technical research, gathers documentation, and synthesizes information from multiple sources
Based on RESEARCH_AGENT_SPEC.md
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


class ResearchAgent(BaseAgent):
    """
    Research Agent - Technical Research & Information Gathering specialist

    Responsibilities:
    - Find official API documentation for libraries and frameworks
    - Research best practices and industry standards
    - Compare technical alternatives and analyze trade-offs
    - Resolve error messages by finding solutions
    - Discover relevant code examples and implementations
    - Locate and summarize research papers (ML/AI topics)
    - Investigate dependencies, versions, and compatibility

    Uses brave-search MCP server for web search and github MCP server for code examples
    """

    def __init__(
        self,
        agent_id: str = "research-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Research Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.RESEARCH,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers required by research agent
        self.required_mcp_servers = ["brave-search", "github"]

        # Supported research types
        self.research_types = [
            "documentation", "best-practices", "comparison",
            "error-resolution", "code-examples", "paper-summary", "dependency"
        ]

        # Source types for classification
        self.source_types = [
            "documentation", "github", "stackoverflow", "blog", "academic", "other"
        ]

        # Default constraints
        self.default_constraints = {
            "recency": "latest",
            "source_preference": "official",
            "depth": "standard",
            "max_results": 10
        }

        self.logger.info("Research Agent initialized with search capabilities")

    def get_system_prompt(self) -> str:
        """Get research-specific system prompt"""
        return """You are the Research Agent, a technical research and information gathering specialist in the PM-Agents system.

**Your Role**:
- Perform comprehensive technical research using Brave Search and GitHub
- Find official documentation for libraries, frameworks, and APIs
- Research best practices and industry standards
- Compare technical alternatives with detailed trade-off analysis
- Resolve errors by finding solutions from multiple sources
- Discover relevant code examples and implementations
- Locate and summarize academic research papers (ML/AI topics)
- Investigate package dependencies, versions, and compatibility

**Core Responsibilities**:
1. **Documentation Lookup**: Find official docs for technologies
2. **Best Practices Research**: Identify recommended patterns and standards
3. **Technology Comparison**: Analyze trade-offs between alternatives
4. **Error Resolution**: Research error messages and find solutions
5. **Code Example Discovery**: Find relevant code snippets and implementations
6. **Paper Summaries**: Locate and summarize academic papers
7. **Dependency Research**: Investigate packages, versions, compatibility

**Research Pipeline**:
1. Formulate effective search query from user request
2. Search Brave for web content (documentation, blogs, StackOverflow)
3. Search GitHub for code examples (if requested)
4. Filter and rank results by relevance and source quality
5. Extract code examples from top results
6. Synthesize findings into actionable summary
7. Generate recommendations and follow-up queries
8. Return structured research report

**Search Strategy**:
- **Official Documentation**: Prioritize official docs (docs.*, official sites)
- **GitHub**: Search for code examples, star count matters
- **StackOverflow**: Good for error resolution and practical advice
- **Blogs**: Dev.to, Medium for tutorials and best practices
- **Academic**: arXiv, Google Scholar for research papers (ML/AI)

**Query Formulation**:
- Include technology names from context
- Add recency constraints (e.g., "2024", "latest")
- Include source preferences (e.g., "official documentation", "github example")
- Optimize for technical content (avoid marketing material)

**Result Ranking Factors**:
1. Source type (official docs > github > stackoverflow > blogs)
2. Recency (newer is better for fast-moving tech)
3. Reputation (official sources, high stars/votes)
4. Content quality (length, code examples, clarity)

**Synthesis Requirements**:
- 2-3 paragraph summary of key findings
- Bullet points for key takeaways
- Comparison tables for technology comparisons
- Code examples with explanations
- Actionable recommendations
- Follow-up research suggestions

**Output Format**: Always provide structured JSON with:
```json
{
  "research_findings": {
    "query_used": "string (actual search query)",
    "sources_searched": ["brave-search", "github"],
    "num_results": "integer",
    "results": [
      {
        "title": "string",
        "url": "string",
        "source_type": "documentation|github|stackoverflow|blog|paper",
        "relevance_score": "float (0.0-1.0)",
        "snippet": "string (excerpt)",
        "publication_date": "string (ISO 8601)",
        "content_summary": "string"
      }
    ],
    "code_examples": [
      {
        "language": "typescript|python|r|javascript",
        "code": "string",
        "source_url": "string",
        "description": "string"
      }
    ],
    "key_findings": ["string (insights)", ...],
    "best_practices": ["string (patterns)", ...],
    "recommendations": ["string (actionable advice)", ...],
    "warnings": ["string (potential issues)", ...]
  },
  "synthesis": {
    "summary": "string (2-3 paragraphs)",
    "key_takeaways": ["string", ...],
    "comparison_table": {
      "headers": ["Feature", "Option A", "Option B"],
      "rows": [["Performance", "Fast", "Faster"]]
    }
  },
  "citations": [
    {
      "text": "string",
      "url": "string",
      "accessed_date": "string (ISO 8601)"
    }
  ],
  "follow_up_queries": ["string (related searches)", ...]
}
```

**Best Practices**:
- Always include citations with URLs and access dates
- Prioritize official documentation over blog posts
- Check recency for fast-moving technologies (React, Next.js, etc.)
- Extract runnable code examples when available
- Provide comparison tables for "comparison" research type
- Suggest follow-up queries for deeper research
- Warn about deprecated packages or breaking changes
- Include multiple perspectives (not just one source)
- Verify information across multiple sources
- Use semantic search for better relevance
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return research capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "documentation_lookup",
                "best_practices_research",
                "technology_comparison",
                "error_resolution",
                "code_examples",
                "paper_summaries",
                "dependency_research"
            ],
            "research_types": self.research_types,
            "source_types": self.source_types,
            "default_constraints": self.default_constraints,
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute research task (documentation lookup, best practices, comparison, etc.)"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Research Agent executing: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_research_prompt(task, context)
                }
            ]

            # Call Claude API
            response = await self._call_claude_api(messages)

            # Parse response
            result_data = self._parse_response(response)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Extract deliverables from research findings
            deliverables = self._extract_deliverables(result_data)

            # Create result
            result = TaskResult(
                task_id=self.current_task or "research-task",
                status=TaskStatus.COMPLETED,
                deliverables=deliverables,
                risks_identified=result_data.get("risks_identified", []),
                issues=result_data.get("issues", []),
                next_steps=result_data.get("follow_up_queries", []),
                execution_time_seconds=execution_time,
                metadata={
                    "num_results": result_data.get("research_findings", {}).get("num_results", 0),
                    "num_code_examples": len(result_data.get("research_findings", {}).get("code_examples", [])),
                    "sources_searched": result_data.get("research_findings", {}).get("sources_searched", []),
                    "research_findings": result_data.get("research_findings", {}),
                    "synthesis": result_data.get("synthesis", {}),
                    "citations": result_data.get("citations", [])
                }
            )

            self.logger.info(f"Research Agent completed in {execution_time:.2f}s with {result_data.get('research_findings', {}).get('num_results', 0)} results")
            return result

        except Exception as e:
            self.logger.error(f"Research Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "research-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Research task failed: {str(e)}",
                    "resolution": "Check search API availability and query formulation"
                }],
                next_steps=["Review error details", "Verify MCP servers are configured", "Retry"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_research_prompt(self, task: str, context: TaskContext) -> str:
        """Build research prompt for Claude"""
        prompt = f"""## Technical Research Task

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}
- Current Phase: {context.current_phase}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Previous Outputs**: {json.dumps(context.previous_outputs, indent=2) if context.previous_outputs else "None"}

**Research Configuration**:
- Supported Research Types: {', '.join(self.research_types)}
- Source Types: {', '.join(self.source_types)}
- Default Constraints: {json.dumps(self.default_constraints, indent=2)}

**Available MCP Tools**: {', '.join(context.mcp_tools_available)}

---

Please complete the research task by:
1. Identifying the research type (documentation, best-practices, comparison, error-resolution, etc.)
2. Formulating an effective search query (include technology names, recency, source preference)
3. Searching Brave for web content (documentation, blogs, StackOverflow)
4. Searching GitHub for code examples (if relevant)
5. Filtering and ranking results by relevance and source quality
6. Extracting code examples from top results
7. Synthesizing findings into actionable summary (2-3 paragraphs)
8. Generating recommendations and follow-up queries
9. Including proper citations with URLs and access dates

**Search Strategy**:
- Prioritize official documentation for API/library questions
- Use GitHub for code examples and implementation patterns
- Check StackOverflow for error messages and troubleshooting
- Consider blogs (Dev.to, Medium) for tutorials and best practices
- Search arXiv/Google Scholar for academic papers (ML/AI topics)

**Result Ranking**:
- Official docs get highest relevance score
- Recent content (2023-2024) ranked higher for fast-moving tech
- High-quality sources (high GitHub stars, upvotes) ranked higher
- Content with code examples ranked higher

Provide your response as valid JSON following the schema in your system prompt.
"""
        return prompt

    def _extract_deliverables(self, result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract deliverables from research results"""
        deliverables = []

        research_findings = result_data.get("research_findings", {})
        synthesis = result_data.get("synthesis", {})

        # Research report
        num_results = research_findings.get("num_results", 0)
        deliverables.append({
            "type": "research_report",
            "name": "Research Findings Report",
            "description": f"Research results with {num_results} sources",
            "status": "completed"
        })

        # Code examples
        code_examples = research_findings.get("code_examples", [])
        if code_examples:
            deliverables.append({
                "type": "code_examples",
                "name": "Code Examples",
                "description": f"{len(code_examples)} code examples extracted",
                "count": len(code_examples)
            })

        # Synthesis summary
        if synthesis.get("summary"):
            deliverables.append({
                "type": "synthesis",
                "name": "Research Synthesis",
                "description": "Synthesized summary of research findings",
                "status": "completed"
            })

        # Comparison table
        if synthesis.get("comparison_table"):
            deliverables.append({
                "type": "comparison",
                "name": "Technology Comparison Table",
                "description": "Detailed comparison of alternatives",
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
                "research_findings": {
                    "query_used": "",
                    "sources_searched": [],
                    "num_results": 0,
                    "results": [],
                    "code_examples": [],
                    "key_findings": [],
                    "best_practices": [],
                    "recommendations": [],
                    "warnings": []
                },
                "synthesis": {
                    "summary": "",
                    "key_takeaways": []
                },
                "citations": [],
                "follow_up_queries": [],
                "risks_identified": [],
                "issues": [{
                    "severity": "high",
                    "description": "Failed to parse Research agent response",
                    "resolution": "Retry research with simplified query"
                }],
                "next_steps": []
            }
