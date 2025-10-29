"""
TypeScript Validator Agent - Code Quality & Validation Specialist
Ensures code quality through type checking, linting, testing, security scanning, and accessibility validation
Based on TYPESCRIPT_VALIDATOR_AGENT_SPEC.md
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


class TypeScriptValidatorAgent(BaseAgent):
    """
    TypeScript Validator Agent - Code Quality & Validation specialist

    Responsibilities:
    - Run type checking (TypeScript tsc, Python mypy)
    - Execute linting (ESLint, Flake8, Stylelint)
    - Enforce code formatting (Prettier, Black)
    - Run test suites with coverage reporting (Jest, Pytest)
    - Perform security scans (npm audit, Safety, Bandit)
    - Validate accessibility compliance (axe-core, WCAG 2.1)
    - Audit performance (Lighthouse, bundle analysis)
    - Enforce quality gates with configurable thresholds

    Uses filesystem MCP server for code access and bash for running validation tools
    """

    def __init__(
        self,
        agent_id: str = "typescript-validator-001",
        api_key: Optional[str] = None,
        message_bus: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize TypeScript Validator Agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.TYPESCRIPT_VALIDATOR,
            api_key=api_key,
            message_bus=message_bus,
            logger=logger
        )

        # MCP servers required by validator agent
        self.required_mcp_servers = ["filesystem"]

        # Supported validation types
        self.validation_types = [
            "full", "type-check", "lint", "format", "test",
            "security", "accessibility", "performance"
        ]

        # Supported languages
        self.supported_languages = [
            "typescript", "javascript", "python", "r"
        ]

        # Supported project types
        self.project_types = [
            "frontend", "backend", "ml", "analytics", "fullstack"
        ]

        # Default quality gate thresholds
        self.default_thresholds = {
            "type_errors": 0,
            "lint_errors": 0,
            "test_coverage": 0.8,  # 80%
            "test_pass_rate": 1.0,  # 100%
            "security_critical": 0,
            "security_high": 0,
            "accessibility_violations": 0,
            "lighthouse_performance": 90,
            "lighthouse_accessibility": 95
        }

        self.logger.info("TypeScript Validator Agent initialized with quality standards")

    def get_system_prompt(self) -> str:
        """Get validation-specific system prompt"""
        return """You are the TypeScript Validator Agent, a code quality and validation specialist in the PM-Agents system.

**Your Role**:
- Ensure code quality across TypeScript, JavaScript, Python, and R codebases
- Run type checking, linting, formatting, testing, security, and accessibility validation
- Enforce quality gates with configurable thresholds
- Provide actionable recommendations for code improvements
- Auto-fix issues when possible (formatting, linting)

**Core Responsibilities**:
1. **Type Checking**: Validate TypeScript (tsc), Python (mypy) type correctness
2. **Linting**: Run ESLint (TS/JS), Flake8 (Python), Stylelint (CSS)
3. **Formatting**: Check/apply Prettier (TS/JS), Black (Python)
4. **Testing**: Execute Jest (TS/JS), Pytest (Python) with coverage
5. **Security**: Scan with npm audit (Node), Safety (Python), Bandit (Python)
6. **Accessibility**: Validate WCAG 2.1 compliance with axe-core
7. **Performance**: Audit with Lighthouse, analyze bundle sizes
8. **Quality Gates**: Evaluate against thresholds and block deployment if needed

**Validation Pipeline**:
1. Type checking (catch type errors early)
2. Linting (enforce code style and best practices)
3. Formatting (ensure consistent code style)
4. Testing (verify functionality and coverage)
5. Security scanning (detect vulnerabilities)
6. Accessibility validation (ensure WCAG compliance)
7. Performance auditing (optimize load times)
8. Quality gate evaluation (GO/NO-GO decision)

**TypeScript/JavaScript Tools**:
- **Type Checking**: `tsc --noEmit --strict`
- **Linting**: `eslint . --ext .ts,.tsx,.js,.jsx`
- **Formatting**: `prettier --check .` or `prettier --write .`
- **Testing**: `jest --coverage --json`
- **Security**: `npm audit`
- **Accessibility**: `axe-core` (for web apps)
- **Performance**: `lighthouse` (for web apps)

**Python Tools**:
- **Type Checking**: `mypy . --strict`
- **Linting**: `flake8 .`
- **Formatting**: `black --check .` or `black .`
- **Testing**: `pytest --cov=. --cov-report=json`
- **Security**: `safety check`, `bandit -r .`

**Quality Gate Thresholds** (Default):
- Type errors: 0 (zero tolerance)
- Lint errors: 0 (zero tolerance)
- Test coverage: 80% minimum
- Test pass rate: 100% (all tests must pass)
- Security: 0 critical/high vulnerabilities
- Accessibility: 0 WCAG 2.1 AA violations
- Performance: Lighthouse >90 (frontend)

**Output Format**: Always provide structured JSON with:
```json
{
  "validation_results": {
    "type_checking": {
      "passed": "boolean",
      "error_count": "integer",
      "warning_count": "integer",
      "errors": [{"file": "string", "line": "integer", "message": "string"}]
    },
    "linting": {
      "passed": "boolean",
      "error_count": "integer",
      "warning_count": "integer",
      "fixable_count": "integer",
      "violations": [{"file": "string", "line": "integer", "rule": "string", "message": "string"}]
    },
    "formatting": {
      "passed": "boolean",
      "files_needing_format": "integer",
      "auto_fixed": "boolean"
    },
    "testing": {
      "passed": "boolean",
      "total_tests": "integer",
      "passed_tests": "integer",
      "failed_tests": "integer",
      "coverage": {
        "line_coverage": "float",
        "branch_coverage": "float",
        "threshold_met": "boolean"
      }
    },
    "security": {
      "passed": "boolean",
      "vulnerabilities": [{"package": "string", "severity": "string", "title": "string"}],
      "vulnerability_count_by_severity": {"critical": 0, "high": 0, "moderate": 0, "low": 0}
    },
    "accessibility": {
      "passed": "boolean",
      "violations": [{"id": "string", "impact": "string", "description": "string"}],
      "violation_count_by_impact": {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    },
    "performance": {
      "passed": "boolean",
      "lighthouse_scores": {"performance": 0, "accessibility": 0, "best_practices": 0, "seo": 0},
      "bundle_analysis": {"total_size_kb": 0, "gzipped_size_kb": 0}
    }
  },
  "quality_gates_status": [
    {"name": "string", "passed": "boolean", "actual_value": "any", "threshold": "any", "blocking": "boolean"}
  ],
  "overall_passed": "boolean",
  "summary": {
    "total_errors": "integer",
    "total_warnings": "integer",
    "test_pass_rate": "float",
    "coverage": "float",
    "security_vulnerabilities": "integer"
  },
  "recommendations": ["string (actionable fixes)"],
  "auto_fixes_applied": [{"file": "string", "type": "string", "description": "string"}],
  "next_steps": ["string"]
}
```

**Best Practices**:
- Run validation in order: type → lint → format → test → security → accessibility → performance
- Auto-fix formatting and safe linting issues when enabled
- Provide clear, actionable error messages with file/line numbers
- Suggest specific commands to resolve issues
- Prioritize critical issues (type errors, security vulnerabilities)
- Include context for why validation failed
- Report metrics (coverage %, error counts, vulnerability counts)
- Always evaluate quality gates before returning results
"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return validator capabilities"""
        return {
            "agent_type": self.agent_type.value,
            "agent_id": self.agent_id,
            "capabilities": [
                "type_checking",
                "linting",
                "formatting",
                "testing",
                "security_scanning",
                "accessibility_validation",
                "performance_auditing",
                "quality_gates"
            ],
            "validation_types": self.validation_types,
            "supported_languages": self.supported_languages,
            "project_types": self.project_types,
            "default_thresholds": self.default_thresholds,
            "mcp_tools_required": self.required_mcp_servers
        }

    async def execute_task(self, task: str, context: TaskContext) -> TaskResult:
        """Execute validation task (type checking, linting, testing, etc.)"""
        start_time = datetime.now()
        self.current_task = task

        try:
            self.logger.info(f"TypeScript Validator Agent executing: {task[:100]}...")

            # Build messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": self._build_validation_prompt(task, context)
                }
            ]

            # Call Claude API
            response = await self._call_claude_api(messages)

            # Parse response
            result_data = self._parse_response(response)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Determine status based on validation results
            overall_passed = result_data.get("overall_passed", False)
            status = TaskStatus.COMPLETED if overall_passed else TaskStatus.FAILED

            # Create result
            result = TaskResult(
                task_id=self.current_task or "validation-task",
                status=status,
                deliverables=self._extract_deliverables(result_data),
                risks_identified=self._extract_risks(result_data),
                issues=self._extract_issues(result_data),
                next_steps=result_data.get("next_steps", []),
                execution_time_seconds=execution_time,
                metadata={
                    "overall_passed": overall_passed,
                    "total_errors": result_data.get("summary", {}).get("total_errors", 0),
                    "total_warnings": result_data.get("summary", {}).get("total_warnings", 0),
                    "test_coverage": result_data.get("summary", {}).get("coverage", 0),
                    "security_vulnerabilities": result_data.get("summary", {}).get("security_vulnerabilities", 0),
                    "validation_results": result_data.get("validation_results", {})
                }
            )

            self.logger.info(f"TypeScript Validator Agent completed in {execution_time:.2f}s - {'PASSED' if overall_passed else 'FAILED'}")
            return result

        except Exception as e:
            self.logger.error(f"TypeScript Validator Agent error: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                task_id=self.current_task or "validation-task",
                status=TaskStatus.FAILED,
                deliverables=[],
                risks_identified=[],
                issues=[{
                    "severity": "critical",
                    "description": f"Validation task failed: {str(e)}",
                    "resolution": "Check validation configuration and tool availability"
                }],
                next_steps=["Review error details", "Verify tools are installed", "Retry"],
                execution_time_seconds=execution_time,
                metadata={"error": str(e)}
            )

    def _build_validation_prompt(self, task: str, context: TaskContext) -> str:
        """Build validation prompt for Claude"""
        prompt = f"""## Code Quality Validation Task

**Task**: {task}

**Project Context**:
- Project ID: {context.project_id}
- Description: {context.project_description}
- Current Phase: {context.current_phase}

**Requirements**: {json.dumps(context.requirements, indent=2)}

**Constraints**: {json.dumps(context.constraints, indent=2)}

**Previous Outputs**: {json.dumps(context.previous_outputs, indent=2) if context.previous_outputs else "None"}

**Validation Configuration**:
- Supported Validation Types: {', '.join(self.validation_types)}
- Supported Languages: {', '.join(self.supported_languages)}
- Default Quality Thresholds: {json.dumps(self.default_thresholds, indent=2)}

**Available MCP Tools**: {', '.join(context.mcp_tools_available)}

---

Please complete the validation task by:
1. Identifying the codebase language and project type
2. Determining which validation checks to run (type, lint, format, test, security, accessibility, performance)
3. Executing validation pipeline in correct order
4. Parsing validation results from each tool
5. Evaluating results against quality gate thresholds
6. Providing actionable recommendations for fixes
7. Auto-fixing issues where safe (formatting, some linting)
8. Returning structured validation report

**Validation Pipeline Order**:
1. Type Checking (catch type errors first)
2. Linting (enforce code standards)
3. Formatting (ensure consistency)
4. Testing (verify functionality + coverage)
5. Security (detect vulnerabilities)
6. Accessibility (WCAG compliance for web apps)
7. Performance (Lighthouse audit for web apps)
8. Quality Gates (final GO/NO-GO decision)

Provide your response as valid JSON following the schema in your system prompt.
"""
        return prompt

    def _extract_deliverables(self, result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract deliverables from validation results"""
        deliverables = []

        # Validation report
        deliverables.append({
            "type": "report",
            "name": "Validation Report",
            "description": "Complete code quality validation results",
            "status": "passed" if result_data.get("overall_passed") else "failed"
        })

        # Auto-fixes applied
        auto_fixes = result_data.get("auto_fixes_applied", [])
        if auto_fixes:
            deliverables.append({
                "type": "fixes",
                "name": "Auto-Applied Fixes",
                "description": f"Applied {len(auto_fixes)} automatic fixes (formatting, linting)",
                "count": len(auto_fixes)
            })

        return deliverables

    def _extract_risks(self, result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract risks from validation results"""
        risks = []

        summary = result_data.get("summary", {})

        # High error count risk
        total_errors = summary.get("total_errors", 0)
        if total_errors > 10:
            risks.append({
                "severity": "high",
                "description": f"High number of errors detected: {total_errors}",
                "impact": "May require significant refactoring to fix",
                "mitigation": "Prioritize fixing errors by severity and impact"
            })

        # Low test coverage risk
        coverage = summary.get("coverage", 1.0)
        if coverage < 0.6:
            risks.append({
                "severity": "medium",
                "description": f"Low test coverage: {coverage*100:.1f}%",
                "impact": "Untested code may contain undetected bugs",
                "mitigation": "Add unit tests for critical paths and uncovered code"
            })

        # Security vulnerabilities risk
        security_vulns = summary.get("security_vulnerabilities", 0)
        if security_vulns > 0:
            risks.append({
                "severity": "critical",
                "description": f"Security vulnerabilities found: {security_vulns}",
                "impact": "Potential security breaches or exploits",
                "mitigation": "Update vulnerable dependencies immediately"
            })

        return risks

    def _extract_issues(self, result_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract issues from validation results"""
        issues = []

        validation_results = result_data.get("validation_results", {})

        # Type checking issues
        type_check = validation_results.get("type_checking", {})
        if not type_check.get("passed", True):
            issues.append({
                "severity": "high",
                "description": f"Type checking failed with {type_check.get('error_count', 0)} errors",
                "resolution": "Fix type errors before proceeding"
            })

        # Linting issues
        linting = validation_results.get("linting", {})
        if not linting.get("passed", True):
            issues.append({
                "severity": "medium",
                "description": f"Linting failed with {linting.get('error_count', 0)} errors",
                "resolution": f"Run linter with --fix flag ({linting.get('fixable_count', 0)} auto-fixable)"
            })

        # Testing issues
        testing = validation_results.get("testing", {})
        if not testing.get("passed", True):
            failed_tests = testing.get("failed_tests", 0)
            coverage_met = testing.get("coverage", {}).get("threshold_met", True)

            if failed_tests > 0:
                issues.append({
                    "severity": "high",
                    "description": f"{failed_tests} tests failed",
                    "resolution": "Fix failing tests before deployment"
                })

            if not coverage_met:
                line_coverage = testing.get("coverage", {}).get("line_coverage", 0)
                issues.append({
                    "severity": "medium",
                    "description": f"Test coverage below threshold: {line_coverage*100:.1f}%",
                    "resolution": "Add tests to increase coverage to 80%+"
                })

        # Security issues
        security = validation_results.get("security", {})
        if not security.get("passed", True):
            vuln_counts = security.get("vulnerability_count_by_severity", {})
            critical = vuln_counts.get("critical", 0)
            high = vuln_counts.get("high", 0)

            if critical > 0 or high > 0:
                issues.append({
                    "severity": "critical",
                    "description": f"Security vulnerabilities: {critical} critical, {high} high",
                    "resolution": "Run 'npm audit fix' or update vulnerable packages"
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
                "validation_results": {},
                "quality_gates_status": [],
                "overall_passed": False,
                "summary": {
                    "total_errors": 0,
                    "total_warnings": 0,
                    "test_pass_rate": 0,
                    "coverage": 0,
                    "security_vulnerabilities": 0
                },
                "recommendations": [],
                "next_steps": [],
                "auto_fixes_applied": []
            }
