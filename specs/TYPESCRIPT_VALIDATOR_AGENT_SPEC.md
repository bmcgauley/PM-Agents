# TypeScript Validator Agent Specification

**Agent Type**: Specialist (Tier 3)
**Domain**: Code Quality & Validation (TypeScript/Python)
**Supervisor**: Supervisor Agent
**Version**: 1.0.0
**Last Updated**: 2025-10-28

---

## 1. Overview

### 1.1 Purpose
The TypeScript Validator Agent ensures code quality across TypeScript, JavaScript, and Python codebases. It performs type checking, linting, formatting, testing, security scanning, and accessibility validation.

### 1.2 Role in Hierarchy
- **Reports to**: Supervisor Agent
- **Collaborates with**: Frontend Coder Agent, Python ML/DL Agent, Reporter Agent
- **Primary responsibility**: Quality gates, validation, testing

### 1.3 Key Responsibilities
1. **Type Checking**: Validate TypeScript types, Python type hints
2. **Linting**: Run ESLint (TypeScript/JavaScript), Flake8/Black (Python), Stylelint (CSS)
3. **Formatting**: Apply Prettier, Black formatting
4. **Testing**: Run Jest, Vitest, Pytest test suites
5. **Coverage**: Measure and enforce test coverage thresholds
6. **Security**: Scan for vulnerabilities (npm audit, Safety, Bandit)
7. **Accessibility**: Validate WCAG compliance (axe-core)
8. **Performance**: Lighthouse audits, bundle size analysis

---

## 2. Input/Output Schemas

### 2.1 Input Schema: `ValidationRequest`

```json
{
  "request_id": "string (UUID)",
  "validation_type": "full|type-check|lint|format|test|security|accessibility|performance",
  "codebase_info": {
    "codebase_path": "string (absolute path)",
    "project_type": "frontend|backend|ml|analytics|fullstack",
    "language": "typescript|javascript|python|r",
    "framework": "nextjs|react|express|fastapi|shiny"
  },
  "validation_config": {
    "type_checking": {
      "enabled": "boolean",
      "strict": "boolean",
      "config_path": "string (tsconfig.json or pyproject.toml)"
    },
    "linting": {
      "enabled": "boolean",
      "rules": "recommended|strict|custom",
      "config_path": "string (.eslintrc, .flake8)"
    },
    "formatting": {
      "enabled": "boolean",
      "check_only": "boolean",
      "auto_fix": "boolean"
    },
    "testing": {
      "enabled": "boolean",
      "run_tests": "boolean",
      "coverage_threshold": "float (0.0-1.0, e.g., 0.8 for 80%)",
      "test_pattern": "string (glob pattern)"
    },
    "security": {
      "enabled": "boolean",
      "severity_threshold": "low|medium|high|critical"
    },
    "accessibility": {
      "enabled": "boolean",
      "wcag_level": "A|AA|AAA"
    },
    "performance": {
      "enabled": "boolean",
      "lighthouse_config": {
        "performance_threshold": "float (0-100)",
        "accessibility_threshold": "float (0-100)",
        "best_practices_threshold": "float (0-100)",
        "seo_threshold": "float (0-100)"
      },
      "bundle_size_limit_kb": "integer"
    }
  },
  "quality_gates": [
    {
      "name": "string (gate name)",
      "type": "zero_errors|coverage|security|performance",
      "threshold": "any (depends on type)",
      "blocking": "boolean (block deployment if fails)"
    }
  ]
}
```

### 2.2 Output Schema: `ValidationResponse`

```json
{
  "request_id": "string (UUID)",
  "status": "passed|failed|warning",
  "execution_time_seconds": "float",
  "validation_results": {
    "type_checking": {
      "enabled": "boolean",
      "passed": "boolean",
      "error_count": "integer",
      "warning_count": "integer",
      "errors": [
        {
          "file": "string",
          "line": "integer",
          "column": "integer",
          "code": "string (e.g., 'TS2322')",
          "message": "string",
          "severity": "error|warning"
        }
      ]
    },
    "linting": {
      "enabled": "boolean",
      "passed": "boolean",
      "error_count": "integer",
      "warning_count": "integer",
      "fixable_count": "integer",
      "violations": [
        {
          "file": "string",
          "line": "integer",
          "rule": "string",
          "message": "string",
          "severity": "error|warning",
          "fixable": "boolean"
        }
      ]
    },
    "formatting": {
      "enabled": "boolean",
      "passed": "boolean",
      "files_needing_format": "integer",
      "auto_fixed": "boolean"
    },
    "testing": {
      "enabled": "boolean",
      "passed": "boolean",
      "total_tests": "integer",
      "passed_tests": "integer",
      "failed_tests": "integer",
      "skipped_tests": "integer",
      "test_duration_seconds": "float",
      "coverage": {
        "line_coverage": "float (0.0-1.0)",
        "branch_coverage": "float (0.0-1.0)",
        "function_coverage": "float (0.0-1.0)",
        "statement_coverage": "float (0.0-1.0)",
        "threshold_met": "boolean"
      },
      "failed_test_details": [
        {
          "test_name": "string",
          "file": "string",
          "error_message": "string"
        }
      ]
    },
    "security": {
      "enabled": "boolean",
      "passed": "boolean",
      "vulnerabilities": [
        {
          "package": "string",
          "severity": "low|moderate|high|critical",
          "title": "string",
          "description": "string",
          "fixed_in": "string (version)"
        }
      ],
      "vulnerability_count_by_severity": {
        "critical": "integer",
        "high": "integer",
        "moderate": "integer",
        "low": "integer"
      }
    },
    "accessibility": {
      "enabled": "boolean",
      "passed": "boolean",
      "violations": [
        {
          "id": "string (e.g., 'color-contrast')",
          "impact": "minor|moderate|serious|critical",
          "description": "string",
          "nodes": [
            {
              "html": "string",
              "target": "string (CSS selector)"
            }
          ]
        }
      ],
      "violation_count_by_impact": {
        "critical": "integer",
        "serious": "integer",
        "moderate": "integer",
        "minor": "integer"
      }
    },
    "performance": {
      "enabled": "boolean",
      "passed": "boolean",
      "lighthouse_scores": {
        "performance": "float (0-100)",
        "accessibility": "float (0-100)",
        "best_practices": "float (0-100)",
        "seo": "float (0-100)"
      },
      "bundle_analysis": {
        "total_size_kb": "float",
        "gzipped_size_kb": "float",
        "largest_bundles": [
          {
            "name": "string",
            "size_kb": "float"
          }
        ]
      },
      "web_vitals": {
        "lcp": "float (seconds)",
        "fid": "float (milliseconds)",
        "cls": "float"
      }
    }
  },
  "quality_gates_status": [
    {
      "name": "string",
      "passed": "boolean",
      "actual_value": "any",
      "threshold": "any",
      "blocking": "boolean"
    }
  ],
  "overall_passed": "boolean",
  "summary": {
    "total_errors": "integer",
    "total_warnings": "integer",
    "total_tests": "integer",
    "test_pass_rate": "float",
    "coverage": "float",
    "security_vulnerabilities": "integer",
    "accessibility_violations": "integer"
  },
  "recommendations": [
    "string (actionable fix suggestions)",
    "e.g., 'Run npm audit fix to resolve 3 vulnerabilities'",
    "e.g., 'Add alt text to images in Header component'"
  ],
  "next_steps": [
    "string (follow-up actions)",
    "e.g., 'Fix 12 TypeScript errors before deployment'",
    "e.g., 'Increase test coverage to 80% threshold'"
  ],
  "auto_fixes_applied": [
    {
      "file": "string",
      "type": "formatting|lint",
      "description": "string"
    }
  ]
}
```

---

## 3. MCP Tools Required

### 3.1 Essential Tools

1. **filesystem** (MCP Server)
   - **Usage**: Read source files, configuration files
   - **Operations**: Read files, list directories

2. **bash** (Implicit via Bash tool)
   - **Usage**: Run validation commands
   - **Operations**:
     - TypeScript: `tsc --noEmit`
     - ESLint: `eslint . --ext .ts,.tsx,.js,.jsx`
     - Prettier: `prettier --check .`
     - Jest: `jest --coverage`
     - Python: `mypy .`, `black --check .`, `flake8 .`, `pytest --cov`
     - Security: `npm audit`, `safety check`, `bandit -r .`

---

## 4. Algorithms & Workflows

### 4.1 Full Validation Pipeline

```python
def perform_validation(request: ValidationRequest) -> ValidationResponse:
    """
    Run full validation pipeline.

    Steps:
    1. Type checking (TypeScript/mypy)
    2. Linting (ESLint/Flake8)
    3. Formatting (Prettier/Black)
    4. Testing (Jest/Pytest)
    5. Security scanning (npm audit/Safety)
    6. Accessibility (axe-core)
    7. Performance (Lighthouse)
    8. Evaluate quality gates
    9. Return aggregated results
    """

    results = ValidationResults()

    # Step 1: Type Checking
    if request.validation_config.type_checking.enabled:
        results.type_checking = run_type_checking(
            codebase_path=request.codebase_info.codebase_path,
            language=request.codebase_info.language,
            strict=request.validation_config.type_checking.strict
        )

    # Step 2: Linting
    if request.validation_config.linting.enabled:
        results.linting = run_linting(
            codebase_path=request.codebase_info.codebase_path,
            language=request.codebase_info.language,
            rules=request.validation_config.linting.rules
        )

    # Step 3: Formatting
    if request.validation_config.formatting.enabled:
        results.formatting = run_formatting(
            codebase_path=request.codebase_info.codebase_path,
            language=request.codebase_info.language,
            auto_fix=request.validation_config.formatting.auto_fix
        )

    # Step 4: Testing
    if request.validation_config.testing.enabled:
        results.testing = run_tests(
            codebase_path=request.codebase_info.codebase_path,
            language=request.codebase_info.language,
            coverage_threshold=request.validation_config.testing.coverage_threshold
        )

    # Step 5: Security
    if request.validation_config.security.enabled:
        results.security = run_security_scan(
            codebase_path=request.codebase_info.codebase_path,
            language=request.codebase_info.language,
            severity_threshold=request.validation_config.security.severity_threshold
        )

    # Step 6: Accessibility
    if request.validation_config.accessibility.enabled and request.codebase_info.project_type == "frontend":
        results.accessibility = run_accessibility_scan(
            codebase_path=request.codebase_info.codebase_path,
            wcag_level=request.validation_config.accessibility.wcag_level
        )

    # Step 7: Performance
    if request.validation_config.performance.enabled and request.codebase_info.project_type == "frontend":
        results.performance = run_performance_audit(
            codebase_path=request.codebase_info.codebase_path,
            lighthouse_config=request.validation_config.performance.lighthouse_config
        )

    # Step 8: Evaluate Quality Gates
    quality_gates_status = evaluate_quality_gates(
        results=results,
        quality_gates=request.quality_gates
    )

    overall_passed = all(gate.passed or not gate.blocking for gate in quality_gates_status)

    # Step 9: Return Results
    return create_response(
        status="passed" if overall_passed else "failed",
        validation_results=results,
        quality_gates_status=quality_gates_status,
        overall_passed=overall_passed
    )
```

### 4.2 Type Checking

```python
def run_type_checking(codebase_path: str, language: str, strict: bool) -> TypeCheckingResult:
    """
    Run type checking.

    TypeScript:
    - Run `tsc --noEmit --pretty false` for type checking
    - Parse errors from stdout

    Python:
    - Run `mypy . --strict` (if strict=True) or `mypy .`
    - Parse errors from stdout
    """

    if language in ["typescript", "javascript"]:
        cmd = "tsc --noEmit --pretty false"
        if strict:
            # Ensure tsconfig.json has strict: true
            pass

        result = subprocess.run(cmd, cwd=codebase_path, capture_output=True, text=True, shell=True)
        errors = parse_tsc_errors(result.stdout)

        return TypeCheckingResult(
            enabled=True,
            passed=len(errors) == 0,
            error_count=len([e for e in errors if e.severity == "error"]),
            warning_count=len([e for e in errors if e.severity == "warning"]),
            errors=errors
        )

    elif language == "python":
        cmd = "mypy . --strict" if strict else "mypy ."
        result = subprocess.run(cmd, cwd=codebase_path, capture_output=True, text=True, shell=True)
        errors = parse_mypy_errors(result.stdout)

        return TypeCheckingResult(
            enabled=True,
            passed=result.returncode == 0,
            error_count=len(errors),
            warning_count=0,
            errors=errors
        )
```

### 4.3 Testing with Coverage

```python
def run_tests(codebase_path: str, language: str, coverage_threshold: float) -> TestingResult:
    """
    Run test suite with coverage.

    TypeScript/JavaScript:
    - Run `jest --coverage --json --outputFile=test-results.json`
    - Parse JSON output

    Python:
    - Run `pytest --cov=. --cov-report=json --json-report --json-report-file=test-results.json`
    - Parse JSON output
    """

    if language in ["typescript", "javascript"]:
        cmd = "jest --coverage --json --outputFile=test-results.json"
        result = subprocess.run(cmd, cwd=codebase_path, capture_output=True, text=True, shell=True)

        # Parse Jest JSON output
        with open(os.path.join(codebase_path, "test-results.json")) as f:
            test_data = json.load(f)

        with open(os.path.join(codebase_path, "coverage/coverage-summary.json")) as f:
            coverage_data = json.load(f)

        line_coverage = coverage_data["total"]["lines"]["pct"] / 100
        branch_coverage = coverage_data["total"]["branches"]["pct"] / 100
        function_coverage = coverage_data["total"]["functions"]["pct"] / 100
        statement_coverage = coverage_data["total"]["statements"]["pct"] / 100

        return TestingResult(
            enabled=True,
            passed=test_data["success"] and line_coverage >= coverage_threshold,
            total_tests=test_data["numTotalTests"],
            passed_tests=test_data["numPassedTests"],
            failed_tests=test_data["numFailedTests"],
            skipped_tests=test_data["numPendingTests"],
            test_duration_seconds=test_data["testResults"][0]["perfStats"]["runtime"] / 1000,
            coverage=CoverageResult(
                line_coverage=line_coverage,
                branch_coverage=branch_coverage,
                function_coverage=function_coverage,
                statement_coverage=statement_coverage,
                threshold_met=line_coverage >= coverage_threshold
            )
        )

    elif language == "python":
        cmd = "pytest --cov=. --cov-report=json --json-report --json-report-file=test-results.json"
        result = subprocess.run(cmd, cwd=codebase_path, capture_output=True, text=True, shell=True)

        with open(os.path.join(codebase_path, "test-results.json")) as f:
            test_data = json.load(f)

        with open(os.path.join(codebase_path, "coverage.json")) as f:
            coverage_data = json.load(f)

        line_coverage = coverage_data["totals"]["percent_covered"] / 100

        return TestingResult(
            enabled=True,
            passed=test_data["exitcode"] == 0 and line_coverage >= coverage_threshold,
            total_tests=test_data["summary"]["total"],
            passed_tests=test_data["summary"]["passed"],
            failed_tests=test_data["summary"]["failed"],
            skipped_tests=test_data["summary"]["skipped"],
            coverage=CoverageResult(
                line_coverage=line_coverage,
                threshold_met=line_coverage >= coverage_threshold
            )
        )
```

---

## 5. Success Criteria

### 5.1 Validation Requirements
- ✅ Zero TypeScript/mypy errors (strict mode)
- ✅ Zero ESLint/Flake8 errors (warnings allowed)
- ✅ All code formatted (Prettier/Black)
- ✅ 80%+ test coverage
- ✅ All tests pass
- ✅ No critical/high security vulnerabilities
- ✅ Zero WCAG 2.1 AA violations
- ✅ Lighthouse performance >90

### 5.2 Performance Requirements
- ✅ Validation completes in <5 minutes for typical codebase
- ✅ Incremental validation (only changed files) <1 minute

---

## 6. Implementation Notes

### 6.1 Technology Stack
- **TypeScript**: tsc, ESLint, Prettier, Jest
- **Python**: mypy, Black, Flake8, Pytest
- **Security**: npm audit, Safety, Bandit
- **Accessibility**: axe-core, pa11y
- **Performance**: Lighthouse, webpack-bundle-analyzer

### 6.2 Dependencies
```json
{
  "typescript": "^5.4.0",
  "eslint": "^8.57.0",
  "prettier": "^3.2.0",
  "jest": "^29.7.0",
  "@axe-core/cli": "^4.9.0",
  "lighthouse": "^11.0.0"
}
```

```python
dependencies = [
    "mypy>=1.8.0",
    "black>=24.0.0",
    "flake8>=7.0.0",
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "safety>=3.0.0",
    "bandit>=1.7.0"
]
```

---

## 7. Future Enhancements

1. **Auto-Fix**: Automatically fix linting/formatting issues
2. **Progressive Validation**: Only validate changed files (git diff)
3. **Parallel Execution**: Run validations concurrently
4. **Custom Rules**: Support project-specific linting rules
5. **CI Integration**: Generate reports for GitHub Actions, GitLab CI

---

**Version History**:
- **v1.0.0** (2025-10-28): Initial specification
