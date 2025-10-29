"""
Browser Agent - Web Automation & Testing Specialist
Automates web interactions using Puppeteer for scraping, testing, and screenshot capture
Based on BROWSER_AGENT_SPEC.md
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


class BrowserAgent(BaseAgent):
    """
    Browser Agent - Web Automation & Testing specialist

    Responsibilities:
    - Scrape data from websites using Puppeteer
    - Capture screenshots of pages and components
    - Generate PDFs from web pages
    - Run end-to-end (E2E) tests for user flows
    - Perform visual regression testing
    - Conduct accessibility audits with axe-core
    - Measure performance metrics and web vitals
    - Automate form filling and submission

    Uses puppeteer MCP server for browser automation and filesystem MCP server for file operations
    """

    def __init__(
        self,
        agent_id: str = "browser-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize Browser Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.BROWSER,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers required by browser agent
        self.required_mcp_servers = ["puppeteer", "filesystem"]

        # Supported task types
        self.task_types = [
            "scrape", "screenshot", "pdf", "e2e-test",
            "visual-test", "accessibility", "performance", "form-fill"
        ]

        # Supported browser actions
        self.browser_actions = [
            "navigate", "click", "type", "select", "wait",
            "scroll", "hover", "screenshot", "evaluate"
        ]

        # Supported assertion types
        self.assertion_types = [
            "element_exists", "text_contains", "url_contains",
            "count_equals", "attribute_equals"
        ]

        # Default browser configuration
        self.default_config = {
            "headless": True,
            "viewport": {"width": 1920, "height": 1080},
            "timeout_ms": 30000,
            "wait_for": "networkidle0"
        }

        self.logger.info("Browser Agent initialized with Puppeteer automation")

    def get_system_prompt(self) -> str:
        """Get browser automation-specific system prompt"""
        return """You are the Browser Agent, a web automation and testing specialist in the PM-Agents system.

**Your Role**:
- Automate web interactions using Puppeteer
- Scrape data from websites reliably and ethically
- Capture high-quality screenshots and generate PDFs
- Run comprehensive end-to-end tests for user flows
- Perform visual regression testing to detect UI changes
- Conduct accessibility audits using axe-core
- Measure performance metrics (FCP, LCP, CLS, TTI, etc.)
- Automate form filling and submission

**Core Responsibilities**:
1. **Web Scraping**: Extract data from websites using CSS selectors
2. **Screenshot Capture**: Take full-page, viewport, or element screenshots
3. **PDF Generation**: Generate PDFs from web pages with formatting
4. **E2E Testing**: Automate user flows with assertions
5. **Visual Testing**: Compare screenshots for UI regressions
6. **Accessibility**: Run axe-core audits for WCAG compliance
7. **Performance**: Measure web vitals and performance metrics
8. **Form Automation**: Fill and submit forms programmatically

**Browser Automation Pipeline**:
1. Launch browser (headless or headed)
2. Configure viewport, user agent, authentication
3. Navigate to target URL
4. Wait for content to load (selector, network idle, etc.)
5. Execute task-specific actions (scrape, test, capture)
6. Handle errors and capture failure screenshots
7. Close browser and return results

**Puppeteer Actions**:
- **navigate**: Go to URL
- **click**: Click element by selector
- **type**: Type text into input field
- **select**: Select option from dropdown
- **wait**: Wait for selector or condition
- **scroll**: Scroll element into view
- **hover**: Hover over element
- **screenshot**: Capture screenshot
- **evaluate**: Execute JavaScript in browser context

**E2E Test Strategy**:
- Execute steps sequentially (fail-fast on errors)
- Capture screenshot on each failure
- Run assertions after all steps complete
- Support multiple assertion types (element exists, text contains, URL contains)
- Provide detailed error messages with step index

**Visual Regression Testing**:
- Compare current screenshot with baseline
- Calculate pixel-by-pixel similarity score
- Generate diff image highlighting changes
- Support ignore regions (dynamic content like dates, ads)
- Configurable similarity threshold

**Accessibility Testing**:
- Run axe-core in browser context
- Support WCAG 2.0/2.1 Level A, AA, AAA
- Report violations by impact (critical, serious, moderate, minor)
- Provide remediation guidance with help URLs

**Performance Testing**:
- Measure Core Web Vitals (LCP, FID, CLS)
- Track FCP, TTFB, TTI metrics
- Run multiple iterations for average
- Monitor network requests and response times

**Output Format**: Always provide structured JSON with:
```json
{
  "results": {
    "scraped_data": {"key": "extracted data", ...},
    "screenshot": {
      "path": "string",
      "size_bytes": "integer",
      "dimensions": {"width": 1920, "height": 1080}
    },
    "pdf": {
      "path": "string",
      "size_bytes": "integer",
      "num_pages": "integer"
    },
    "e2e_test": {
      "test_name": "string",
      "passed": "boolean",
      "duration_seconds": "float",
      "steps_executed": "integer",
      "steps_passed": "integer",
      "steps_failed": "integer",
      "failed_step_details": [
        {
          "step_index": "integer",
          "action": "string",
          "error_message": "string",
          "screenshot_path": "string"
        }
      ],
      "assertions_passed": "integer",
      "assertions_failed": "integer"
    },
    "visual_test": {
      "similarity_score": "float (0.0-1.0)",
      "passed": "boolean",
      "diff_path": "string",
      "changed_pixels": "integer",
      "total_pixels": "integer"
    },
    "accessibility": {
      "passed": "boolean",
      "violations": [
        {
          "id": "string",
          "impact": "minor|moderate|serious|critical",
          "description": "string",
          "help_url": "string",
          "nodes": [{"html": "string", "target": "string"}]
        }
      ],
      "violation_count": "integer"
    },
    "performance": {
      "metrics": {
        "fcp": "float (ms)",
        "lcp": "float (ms)",
        "ttfb": "float (ms)",
        "tti": "float (ms)",
        "cls": "float",
        "fid": "float (ms)"
      }
    },
    "form_fill": {
      "submitted": "boolean",
      "fields_filled": "integer",
      "final_url": "string"
    }
  },
  "console_logs": [
    {"type": "log|warn|error", "message": "string", "timestamp": "string"}
  ],
  "network_requests": [
    {"url": "string", "method": "string", "status": "integer", "response_time_ms": "float"}
  ],
  "errors": [
    {"type": "string", "message": "string", "step": "string"}
  ]
}
```

**Best Practices**:
- Use `waitForSelector` instead of fixed delays
- Run in headless mode for CI/CD (headed mode for debugging)
- Set appropriate timeouts based on network conditions
- Always close browser instances to avoid memory leaks
- Capture screenshots on failures for debugging
- Use stealth mode to avoid bot detection (when ethical)
- Handle dynamic content with proper wait strategies
- Implement retry logic for transient network errors
- Monitor console logs and network requests for issues
- Respect robots.txt and rate limits when scraping
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return browser automation capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "web_scraping",
                "screenshot_capture",
                "pdf_generation",
                "e2e_testing",
                "visual_regression_testing",
                "accessibility_testing",
                "performance_testing",
                "form_automation"
            ],
            "task_types": self.task_types,
            "browser_actions": self.browser_actions,
            "assertion_types": self.assertion_types,
            "default_config": self.default_config,
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute browser automation task (scraping, testing, screenshot, etc.)"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"Browser Agent executing: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_browser_prompt(task, context)
                }
            ]

            # Call Claude API
            response = await self._call_claude_api(messages)

            # Parse response
            result_data = self._parse_response(response)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Extract deliverables from browser results
            deliverables = self._extract_deliverables(result_data)

            # Extract issues from errors
            issues = self._extract_issues(result_data)

            # Create result
            result = TaskResult(
                task_id=self.current_task or "browser-task",
                status=TaskStatus.COMPLETED if not issues else TaskStatus.FAILED,
                deliverables=deliverables,
                risks_identified=result_data.get("risks_identified", []),
                issues=issues,
                next_steps=result_data.get("next_steps", []),
                execution_time_seconds=execution_time,
                metadata={
                    "results": result_data.get("results", {}),
                    "console_logs": result_data.get("console_logs", []),
                    "network_requests": result_data.get("network_requests", []),
                    "errors": result_data.get("errors", [])
                }
            )

            self.logger.info(f"Browser Agent completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Browser Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "browser-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Browser automation task failed: {str(e)}",
                    "resolution": "Check target URL and browser configuration"
                }],
                next_steps=["Review error details", "Verify Puppeteer MCP server is running", "Retry"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_browser_prompt(self, task: str, context: TaskContext) -> str:
        """Build browser automation prompt for Claude"""
        prompt = f"""## Web Automation & Testing Task

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}
- Current Phase: {context.current_phase}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Previous Outputs**: {json.dumps(context.previous_outputs, indent=2) if context.previous_outputs else "None"}

**Browser Automation Configuration**:
- Supported Task Types: {', '.join(self.task_types)}
- Browser Actions: {', '.join(self.browser_actions)}
- Assertion Types: {', '.join(self.assertion_types)}
- Default Config: {json.dumps(self.default_config, indent=2)}

**Available MCP Tools**: {', '.join(context.mcp_tools_available)}

---

Please complete the browser automation task by:
1. Identifying the task type (scrape, screenshot, e2e-test, visual-test, accessibility, performance, form-fill)
2. Configuring browser settings (headless, viewport, timeout)
3. Navigating to target URL with appropriate wait strategy
4. Executing task-specific actions:
   - **Scraping**: Extract data using CSS selectors
   - **Screenshot**: Capture full-page, viewport, or element screenshot
   - **PDF**: Generate PDF with formatting options
   - **E2E Test**: Execute steps and run assertions
   - **Visual Test**: Compare with baseline screenshot
   - **Accessibility**: Run axe-core audit
   - **Performance**: Measure web vitals
   - **Form Fill**: Fill fields and submit
5. Handling errors gracefully and capturing failure screenshots
6. Monitoring console logs and network requests
7. Closing browser and returning structured results

**Error Handling**:
- Capture screenshot on any failure
- Log console errors and warnings
- Track failed network requests
- Provide detailed error messages with step context
- Suggest remediation steps

Provide your response as valid JSON following the schema in your system prompt.
"""
        return prompt

    def _extract_deliverables(self, result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract deliverables from browser automation results"""
        deliverables = []

        results = result_data.get("results", {})

        # Scraped data
        if "scraped_data" in results and results["scraped_data"]:
            deliverables.append({
                "type": "data",
                "name": "Scraped Data",
                "description": "Data extracted from website",
                "status": "completed"
            })

        # Screenshot
        if "screenshot" in results and results["screenshot"]:
            deliverables.append({
                "type": "image",
                "name": "Screenshot",
                "path": results["screenshot"].get("path", ""),
                "size_bytes": results["screenshot"].get("size_bytes", 0),
                "status": "completed"
            })

        # PDF
        if "pdf" in results and results["pdf"]:
            deliverables.append({
                "type": "document",
                "name": "PDF Document",
                "path": results["pdf"].get("path", ""),
                "size_bytes": results["pdf"].get("size_bytes", 0),
                "num_pages": results["pdf"].get("num_pages", 0),
                "status": "completed"
            })

        # E2E Test Results
        if "e2e_test" in results and results["e2e_test"]:
            test = results["e2e_test"]
            deliverables.append({
                "type": "test_report",
                "name": f"E2E Test: {test.get('test_name', 'Unknown')}",
                "description": f"{'PASSED' if test.get('passed') else 'FAILED'} - {test.get('steps_passed', 0)}/{test.get('steps_executed', 0)} steps",
                "status": "passed" if test.get("passed") else "failed"
            })

        # Visual Test Results
        if "visual_test" in results and results["visual_test"]:
            visual = results["visual_test"]
            deliverables.append({
                "type": "visual_test",
                "name": "Visual Regression Test",
                "description": f"Similarity: {visual.get('similarity_score', 0)*100:.1f}%",
                "status": "passed" if visual.get("passed") else "failed"
            })

        # Accessibility Report
        if "accessibility" in results and results["accessibility"]:
            a11y = results["accessibility"]
            deliverables.append({
                "type": "accessibility_report",
                "name": "Accessibility Audit",
                "description": f"{a11y.get('violation_count', 0)} violations found",
                "status": "passed" if a11y.get("passed") else "failed"
            })

        # Performance Report
        if "performance" in results and results["performance"]:
            deliverables.append({
                "type": "performance_report",
                "name": "Performance Metrics",
                "description": "Web vitals and performance data",
                "status": "completed"
            })

        return deliverables

    def _extract_issues(self, result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract issues from browser automation errors"""
        issues = []

        errors = result_data.get("errors", [])
        for error in errors:
            issues.append({
                "severity": "high" if error.get("type") == "assertion_error" else "medium",
                "description": error.get("message", "Unknown error"),
                "resolution": f"Check step: {error.get('step', 'N/A')}"
            })

        # E2E test failures
        results = result_data.get("results", {})
        if "e2e_test" in results:
            e2e = results["e2e_test"]
            if not e2e.get("passed"):
                for failure in e2e.get("failed_step_details", []):
                    issues.append({
                        "severity": "high",
                        "description": f"E2E test failed at step {failure.get('step_index')}: {failure.get('error_message')}",
                        "resolution": f"See screenshot: {failure.get('screenshot_path', 'N/A')}"
                    })

        # Accessibility violations
        if "accessibility" in results:
            a11y = results["accessibility"]
            critical_violations = [v for v in a11y.get("violations", []) if v.get("impact") in ["critical", "serious"]]
            for violation in critical_violations[:5]:  # Limit to top 5
                issues.append({
                    "severity": "high" if violation.get("impact") == "critical" else "medium",
                    "description": f"Accessibility: {violation.get('description', 'Unknown')}",
                    "resolution": f"Fix {len(violation.get('nodes', []))} occurrences - {violation.get('help_url', '')}"
                })

        return issues

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
                "results": {},
                "console_logs": [],
                "network_requests": [],
                "errors": [{
                    "type": "parse_error",
                    "message": "Failed to parse Browser agent response",
                    "step": "response_parsing"
                }],
                "risks_identified": [],
                "issues": [],
                "next_steps": []
            }
