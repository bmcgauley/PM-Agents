# Phase Gate Criteria Specification

## Overview

This document defines **Phase Gate Criteria** for the PM-Agents multi-agent system. Phase gates are critical control points between PMBOK project phases where GO/NO-GO decisions are made before proceeding. They ensure deliverable completeness, quality standards, risk acceptability, and stakeholder alignment.

### PMBOK Phases

The PM-Agents system follows the PMI PMBOK Guide (7th Edition) process groups:

1. **Initiation** - Define project scope, identify stakeholders, assess feasibility
2. **Planning** - Develop detailed plans, specifications, and resource allocation
3. **Execution** - Implement plans, create deliverables, build the system
4. **Monitoring & Control** - Track progress, measure quality, manage changes
5. **Closure** - Finalize deliverables, conduct retrospectives, transfer knowledge

### Phase Gate Purpose

Each phase gate evaluates:
- **Deliverable Completeness**: All required outputs produced
- **Quality Standards**: Deliverables meet acceptance criteria
- **Risk Level**: Risks identified and mitigated appropriately
- **Resource Availability**: Next phase resources secured
- **Stakeholder Approval**: Key stakeholders endorse continuation

---

## Phase Gate 1: Initiation → Planning

### Gate Objective

Verify that the project is properly defined, feasible, and ready for detailed planning.

### Entry Criteria

- User request received and parsed
- Project type identified (frontend, backend, ML, analytics, fullstack)
- Initial scope defined

### Evaluation Criteria

#### 1. Project Charter Quality (Weight: 30%)

**Quantitative Metrics**:
- Project description length: ≥ 100 characters
- Objectives defined: ≥ 3
- Success criteria specified: ≥ 3
- Stakeholders identified: ≥ 2

**Qualitative Assessment**:
- Clear problem statement (Yes/No)
- Measurable success criteria (Yes/No)
- Realistic scope boundaries (Yes/No)
- Adequate context provided (Yes/No)

**Automated Checks**:
```python
def check_project_charter(charter: dict) -> dict:
    """
    Evaluate project charter quality.

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'issues': List[str],
            'recommendations': List[str]
        }
    """
    score = 0
    issues = []
    recommendations = []

    # Check description length
    if len(charter.get('description', '')) >= 100:
        score += 10
    else:
        issues.append("Project description too short (< 100 characters)")
        recommendations.append("Expand project description with more detail")

    # Check objectives count
    objectives = charter.get('objectives', [])
    if len(objectives) >= 3:
        score += 10
    else:
        issues.append(f"Only {len(objectives)} objectives defined (need ≥ 3)")
        recommendations.append("Define at least 3 clear project objectives")

    # Check success criteria
    success_criteria = charter.get('success_criteria', [])
    if len(success_criteria) >= 3:
        score += 10
    else:
        issues.append(f"Only {len(success_criteria)} success criteria (need ≥ 3)")
        recommendations.append("Define at least 3 measurable success criteria")

    # Check stakeholders
    stakeholders = charter.get('stakeholders', [])
    if len(stakeholders) >= 2:
        score += 10
    else:
        issues.append(f"Only {len(stakeholders)} stakeholders identified (need ≥ 2)")
        recommendations.append("Identify at least 2 key stakeholders")

    # Qualitative checks (simplified for automation)
    if charter.get('problem_statement'):
        score += 15
    else:
        issues.append("Missing problem statement")

    if charter.get('scope_boundaries'):
        score += 15
    else:
        issues.append("Missing scope boundaries")

    if charter.get('constraints'):
        score += 15
    else:
        issues.append("Missing project constraints")

    if charter.get('assumptions'):
        score += 15
    else:
        issues.append("Missing project assumptions")

    return {
        'score': score,
        'pass': score >= 70,  # 70% threshold
        'issues': issues,
        'recommendations': recommendations
    }
```

#### 2. Risk Assessment Completeness (Weight: 25%)

**Quantitative Metrics**:
- Risks identified: ≥ 5
- High/critical risks: < 3
- Mitigation strategies defined: 100% of risks
- Risk probability assessed: 100% of risks

**Qualitative Assessment**:
- Risk categories covered (technical, resource, schedule, scope)
- Mitigation strategies are actionable
- Contingency plans for critical risks

**Automated Checks**:
```python
def check_risk_assessment(risks: List[dict]) -> dict:
    """
    Evaluate risk assessment quality.

    Args:
        risks: List of risk objects with fields:
            - id, description, category, probability, impact,
              severity, mitigation, contingency

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'critical_risks': List[dict],
            'issues': List[str]
        }
    """
    score = 0
    issues = []
    critical_risks = []

    # Check number of risks
    if len(risks) >= 5:
        score += 20
    else:
        issues.append(f"Only {len(risks)} risks identified (need ≥ 5)")

    # Check risk severity distribution
    high_critical_count = sum(
        1 for r in risks
        if r.get('severity') in ['high', 'critical']
    )

    if high_critical_count < 3:
        score += 20
    else:
        issues.append(f"{high_critical_count} high/critical risks (threshold: < 3)")
        critical_risks = [r for r in risks if r.get('severity') in ['high', 'critical']]

    # Check mitigation strategies
    risks_with_mitigation = sum(
        1 for r in risks
        if r.get('mitigation') and len(r['mitigation']) > 0
    )

    if risks_with_mitigation == len(risks):
        score += 20
    else:
        missing = len(risks) - risks_with_mitigation
        issues.append(f"{missing} risks missing mitigation strategies")

    # Check risk probability assessment
    risks_with_probability = sum(
        1 for r in risks
        if r.get('probability') in ['low', 'medium', 'high']
    )

    if risks_with_probability == len(risks):
        score += 20
    else:
        missing = len(risks) - risks_with_probability
        issues.append(f"{missing} risks missing probability assessment")

    # Check category coverage
    categories_covered = set(r.get('category', '') for r in risks)
    required_categories = {'technical', 'resource', 'schedule', 'scope'}

    if categories_covered >= required_categories:
        score += 20
    else:
        missing_categories = required_categories - categories_covered
        issues.append(f"Missing risk categories: {', '.join(missing_categories)}")

    return {
        'score': score,
        'pass': score >= 70 and high_critical_count < 3,
        'critical_risks': critical_risks,
        'issues': issues
    }
```

#### 3. Stakeholder Alignment (Weight: 20%)

**Quantitative Metrics**:
- Stakeholder register complete: Yes/No
- Communication plan defined: Yes/No
- Stakeholder roles assigned: 100% of stakeholders

**Qualitative Assessment**:
- Key decision-makers identified
- Approval authority clearly defined
- Communication frequency appropriate

**Automated Checks**:
```python
def check_stakeholder_alignment(stakeholders: List[dict]) -> dict:
    """
    Evaluate stakeholder alignment.

    Args:
        stakeholders: List with fields:
            - name, role, influence, engagement_level,
              communication_frequency, approval_authority

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'issues': List[str]
        }
    """
    score = 0
    issues = []

    if len(stakeholders) == 0:
        return {
            'score': 0,
            'pass': False,
            'issues': ['No stakeholders identified']
        }

    # Check roles assigned
    stakeholders_with_roles = sum(
        1 for s in stakeholders
        if s.get('role') and len(s['role']) > 0
    )

    if stakeholders_with_roles == len(stakeholders):
        score += 30
    else:
        missing = len(stakeholders) - stakeholders_with_roles
        issues.append(f"{missing} stakeholders missing role assignment")

    # Check influence assessment
    stakeholders_with_influence = sum(
        1 for s in stakeholders
        if s.get('influence') in ['high', 'medium', 'low']
    )

    if stakeholders_with_influence == len(stakeholders):
        score += 20
    else:
        missing = len(stakeholders) - stakeholders_with_influence
        issues.append(f"{missing} stakeholders missing influence level")

    # Check communication plan
    stakeholders_with_comm_plan = sum(
        1 for s in stakeholders
        if s.get('communication_frequency')
    )

    if stakeholders_with_comm_plan == len(stakeholders):
        score += 30
    else:
        missing = len(stakeholders) - stakeholders_with_comm_plan
        issues.append(f"{missing} stakeholders missing communication plan")

    # Check for decision-makers
    decision_makers = [
        s for s in stakeholders
        if s.get('approval_authority') == True
    ]

    if len(decision_makers) >= 1:
        score += 20
    else:
        issues.append("No decision-makers with approval authority identified")

    return {
        'score': score,
        'pass': score >= 70,
        'issues': issues
    }
```

#### 4. Feasibility Validation (Weight: 25%)

**Quantitative Metrics**:
- Technical feasibility confirmed: Yes/No
- Resource availability verified: Yes/No
- Timeline estimated: Yes/No
- Budget estimated: Yes/No

**Qualitative Assessment**:
- Technical approach is sound
- Required skills are available
- Dependencies are manageable
- Timeline is realistic

**Automated Checks**:
```python
def check_feasibility(feasibility: dict) -> dict:
    """
    Evaluate project feasibility.

    Args:
        feasibility: Dict with fields:
            - technical_approach, required_skills, dependencies,
              timeline_estimate, budget_estimate, constraints

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'blockers': List[str],
            'issues': List[str]
        }
    """
    score = 0
    issues = []
    blockers = []

    # Check technical approach
    if feasibility.get('technical_approach'):
        score += 25
    else:
        issues.append("Missing technical approach")
        blockers.append("Technical approach must be defined")

    # Check required skills
    required_skills = feasibility.get('required_skills', [])
    if len(required_skills) > 0:
        score += 25
    else:
        issues.append("Required skills not identified")

    # Check dependencies
    dependencies = feasibility.get('dependencies', [])
    if len(dependencies) >= 0:  # Can be empty
        # Check if external dependencies are available
        unavailable = [
            d for d in dependencies
            if d.get('available') == False
        ]
        if len(unavailable) == 0:
            score += 25
        else:
            issues.append(f"{len(unavailable)} dependencies unavailable")
            blockers.extend([d['name'] for d in unavailable])

    # Check timeline estimate
    if feasibility.get('timeline_estimate'):
        score += 15
    else:
        issues.append("Missing timeline estimate")

    # Check budget estimate
    if feasibility.get('budget_estimate'):
        score += 10
    else:
        issues.append("Missing budget estimate")

    return {
        'score': score,
        'pass': score >= 70 and len(blockers) == 0,
        'blockers': blockers,
        'issues': issues
    }
```

### Gate Decision Logic

```python
def phase_gate_1_evaluation(project_state: dict) -> dict:
    """
    Evaluate Phase Gate 1: Initiation → Planning.

    Args:
        project_state: Dict containing:
            - charter, risks, stakeholders, feasibility

    Returns:
        {
            'decision': 'GO' | 'CONDITIONAL_GO' | 'NO_GO',
            'overall_score': float (0-100),
            'criteria_scores': dict,
            'critical_issues': List[str],
            'recommendations': List[str],
            'required_actions': List[str]
        }
    """
    # Evaluate each criterion
    charter_result = check_project_charter(project_state['charter'])
    risk_result = check_risk_assessment(project_state['risks'])
    stakeholder_result = check_stakeholder_alignment(project_state['stakeholders'])
    feasibility_result = check_feasibility(project_state['feasibility'])

    # Calculate weighted overall score
    weights = {
        'charter': 0.30,
        'risks': 0.25,
        'stakeholders': 0.20,
        'feasibility': 0.25
    }

    overall_score = (
        charter_result['score'] * weights['charter'] +
        risk_result['score'] * weights['risks'] +
        stakeholder_result['score'] * weights['stakeholders'] +
        feasibility_result['score'] * weights['feasibility']
    )

    # Collect all issues
    all_issues = (
        charter_result.get('issues', []) +
        risk_result.get('issues', []) +
        stakeholder_result.get('issues', []) +
        feasibility_result.get('issues', [])
    )

    # Identify blockers
    blockers = feasibility_result.get('blockers', [])
    critical_risks = risk_result.get('critical_risks', [])

    # Make decision
    if len(blockers) > 0:
        decision = 'NO_GO'
        required_actions = [f"Resolve blocker: {b}" for b in blockers]
    elif overall_score >= 85 and len(critical_risks) == 0:
        decision = 'GO'
        required_actions = []
    elif overall_score >= 70:
        decision = 'CONDITIONAL_GO'
        required_actions = [
            f"Address: {issue}" for issue in all_issues[:3]  # Top 3 issues
        ]
    else:
        decision = 'NO_GO'
        required_actions = [
            "Overall score too low. Address all critical issues.",
            *all_issues
        ]

    return {
        'decision': decision,
        'overall_score': overall_score,
        'criteria_scores': {
            'charter': charter_result['score'],
            'risks': risk_result['score'],
            'stakeholders': stakeholder_result['score'],
            'feasibility': feasibility_result['score']
        },
        'critical_issues': blockers + [r['description'] for r in critical_risks],
        'recommendations': charter_result.get('recommendations', []),
        'required_actions': required_actions
    }
```

### Exit Criteria (GO Decision)

- Overall score ≥ 85% (for unconditional GO)
- Overall score ≥ 70% (for conditional GO with action plan)
- No unresolved blockers
- Critical risks < 3
- All weighted criteria pass (≥ 70%)

### Reporting Template

```markdown
# Phase Gate 1 Report: Initiation → Planning

**Project**: {project_name}
**Date**: {evaluation_date}
**Decision**: {GO | CONDITIONAL_GO | NO_GO}
**Overall Score**: {score}% / 100%

## Summary

{Brief summary of evaluation}

## Criteria Evaluation

### 1. Project Charter Quality (Weight: 30%)
- **Score**: {score}%
- **Status**: {PASS | FAIL}
- **Issues**:
  - {issue_1}
  - {issue_2}

### 2. Risk Assessment (Weight: 25%)
- **Score**: {score}%
- **Status**: {PASS | FAIL}
- **Critical Risks**: {count}
- **Issues**:
  - {issue_1}

### 3. Stakeholder Alignment (Weight: 20%)
- **Score**: {score}%
- **Status**: {PASS | FAIL}
- **Issues**:
  - {issue_1}

### 4. Feasibility Validation (Weight: 25%)
- **Score**: {score}%
- **Status**: {PASS | FAIL}
- **Blockers**: {count}
- **Issues**:
  - {issue_1}

## Decision Rationale

{Explanation of GO/NO-GO decision}

## Required Actions (for CONDITIONAL_GO or NO_GO)

1. {action_1}
2. {action_2}

## Recommendations

1. {recommendation_1}
2. {recommendation_2}

## Sign-off

- **Coordinator Agent**: {signature}
- **Date**: {date}
```

---

## Phase Gate 2: Planning → Execution

### Gate Objective

Verify that comprehensive plans, specifications, and designs are complete and ready for implementation.

### Entry Criteria

- Phase 1 (Initiation) completed with GO decision
- Planning phase activities completed
- All agent specifications drafted

### Evaluation Criteria

#### 1. Specification Completeness (Weight: 35%)

**Quantitative Metrics**:
- Agent specifications created: 100% (12 agents)
- MCP server specifications: 100% (3 custom servers)
- API schemas defined: Yes/No
- Integration documented: Yes/No

**Automated Checks**:
```python
def check_specification_completeness(specs: dict) -> dict:
    """
    Evaluate specification completeness.

    Args:
        specs: Dict with:
            - agent_specs: List of agent specification files
            - mcp_specs: List of MCP server specification files
            - schemas: API schemas
            - integration_docs: Integration documentation

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'missing': List[str],
            'issues': List[str]
        }
    """
    score = 0
    missing = []
    issues = []

    # Check agent specifications (12 required)
    required_agents = [
        'Coordinator', 'Planner', 'Supervisor',
        'SpecKit', 'QdrantVector', 'FrontendCoder',
        'PythonMLDL', 'RAnalytics', 'TypeScriptValidator',
        'Research', 'Browser', 'Reporter'
    ]

    agent_specs = specs.get('agent_specs', [])
    if len(agent_specs) == len(required_agents):
        score += 30
    else:
        missing_agents = set(required_agents) - set(agent_specs)
        missing.extend(missing_agents)
        issues.append(f"Missing {len(missing_agents)} agent specifications")

    # Check MCP server specifications (3 required)
    required_mcp = ['qdrant', 'tensorboard', 'specify']
    mcp_specs = specs.get('mcp_specs', [])

    if len(mcp_specs) == len(required_mcp):
        score += 20
    else:
        missing_mcp = set(required_mcp) - set(mcp_specs)
        missing.extend([f"MCP: {m}" for m in missing_mcp])
        issues.append(f"Missing {len(missing_mcp)} MCP server specifications")

    # Check API schemas
    if specs.get('schemas'):
        score += 25
    else:
        missing.append("API schemas")
        issues.append("API schemas not defined")

    # Check integration documentation
    if specs.get('integration_docs'):
        score += 25
    else:
        missing.append("Integration documentation")
        issues.append("Integration documentation missing")

    return {
        'score': score,
        'pass': score >= 80,
        'missing': missing,
        'issues': issues
    }
```

#### 2. Technical Architecture (Weight: 30%)

**Quantitative Metrics**:
- Communication protocol defined: Yes/No
- Message schemas complete: 100%
- Error handling patterns documented: Yes/No
- Testing strategy defined: Yes/No

**Automated Checks**:
```python
def check_technical_architecture(architecture: dict) -> dict:
    """
    Evaluate technical architecture quality.

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'issues': List[str]
        }
    """
    score = 0
    issues = []

    # Check communication protocol
    if architecture.get('communication_protocol'):
        protocol = architecture['communication_protocol']

        # Check message schemas
        required_messages = [
            'TaskRequest', 'TaskResult', 'StatusUpdate',
            'ErrorReport', 'ContextShare'
        ]
        defined_messages = protocol.get('message_schemas', [])

        if set(required_messages).issubset(set(defined_messages)):
            score += 30
        else:
            missing = set(required_messages) - set(defined_messages)
            issues.append(f"Missing message schemas: {', '.join(missing)}")
    else:
        issues.append("Communication protocol not defined")

    # Check error handling
    if architecture.get('error_handling'):
        score += 20
    else:
        issues.append("Error handling patterns not documented")

    # Check testing strategy
    if architecture.get('testing_strategy'):
        testing = architecture['testing_strategy']
        if ('unit' in testing and 'integration' in testing and 'e2e' in testing):
            score += 25
        else:
            issues.append("Incomplete testing strategy (need unit, integration, E2E)")
    else:
        issues.append("Testing strategy not defined")

    # Check monitoring/observability
    if architecture.get('observability'):
        score += 25
    else:
        issues.append("Observability/monitoring plan missing")

    return {
        'score': score,
        'pass': score >= 70,
        'issues': issues
    }
```

#### 3. Resource Planning (Weight: 20%)

**Quantitative Metrics**:
- API keys secured: 100%
- Dependencies documented: Yes/No
- Infrastructure planned: Yes/No
- Timeline estimated: Yes/No

**Automated Checks**:
```python
def check_resource_planning(resources: dict) -> dict:
    """
    Evaluate resource planning completeness.

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'missing_resources': List[str],
            'issues': List[str]
        }
    """
    score = 0
    missing_resources = []
    issues = []

    # Check API keys
    required_keys = ['ANTHROPIC_API_KEY', 'GITHUB_TOKEN']
    secured_keys = resources.get('api_keys', [])

    if set(required_keys).issubset(set(secured_keys)):
        score += 30
    else:
        missing = set(required_keys) - set(secured_keys)
        missing_resources.extend(missing)
        issues.append(f"Missing API keys: {', '.join(missing)}")

    # Check dependencies
    if resources.get('dependencies'):
        score += 20
    else:
        issues.append("Dependencies not documented")

    # Check infrastructure
    if resources.get('infrastructure'):
        infra = resources['infrastructure']
        required_infra = ['qdrant', 'redis']

        if all(i in infra for i in required_infra):
            score += 25
        else:
            missing = [i for i in required_infra if i not in infra]
            missing_resources.extend(missing)
            issues.append(f"Missing infrastructure: {', '.join(missing)}")
    else:
        issues.append("Infrastructure not planned")

    # Check timeline
    if resources.get('timeline'):
        score += 25
    else:
        issues.append("Implementation timeline not estimated")

    return {
        'score': score,
        'pass': score >= 70,
        'missing_resources': missing_resources,
        'issues': issues
    }
```

#### 4. Quality Assurance Plan (Weight: 15%)

**Quantitative Metrics**:
- Test coverage target defined: Yes/No
- Quality gates defined: Yes/No
- Code review process: Yes/No
- CI/CD pipeline planned: Yes/No

### Gate Decision Logic

```python
def phase_gate_2_evaluation(project_state: dict) -> dict:
    """
    Evaluate Phase Gate 2: Planning → Execution.

    Returns: Same structure as phase_gate_1_evaluation
    """
    # Similar structure to Phase Gate 1
    # with different criteria and weights
    pass
```

### Exit Criteria (GO Decision)

- Overall score ≥ 85%
- All specifications complete (100%)
- Communication protocol fully defined
- No missing critical resources
- Testing strategy comprehensive

---

## Phase Gate 3: Execution → Monitoring

### Gate Objective

Verify that core system is implemented, tested, and ready for deployment/monitoring.

### Entry Criteria

- Phase 2 (Planning) completed with GO decision
- Implementation phase completed
- All agents implemented

### Evaluation Criteria

#### 1. Implementation Completeness (Weight: 40%)

**Quantitative Metrics**:
- Agents implemented: 100% (12 agents)
- MCP servers implemented: 100% (3 servers)
- Tests written: ≥ 80% coverage
- Documentation complete: Yes/No

**Automated Checks**:
```python
def check_implementation_completeness(implementation: dict) -> dict:
    """
    Evaluate implementation completeness.

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'missing_implementations': List[str],
            'issues': List[str]
        }
    """
    score = 0
    missing = []
    issues = []

    # Check agent implementations
    required_agents = 12
    implemented_agents = implementation.get('agents_implemented', 0)

    if implemented_agents == required_agents:
        score += 30
    else:
        missing.append(f"{required_agents - implemented_agents} agents")
        issues.append(f"Only {implemented_agents}/{required_agents} agents implemented")

    # Check MCP servers
    required_mcp = 3
    implemented_mcp = implementation.get('mcp_servers_implemented', 0)

    if implemented_mcp == required_mcp:
        score += 20
    else:
        missing.append(f"{required_mcp - implemented_mcp} MCP servers")
        issues.append(f"Only {implemented_mcp}/{required_mcp} MCP servers implemented")

    # Check test coverage
    test_coverage = implementation.get('test_coverage', 0)

    if test_coverage >= 80:
        score += 30
    else:
        issues.append(f"Test coverage only {test_coverage}% (need ≥ 80%)")

    # Check documentation
    if implementation.get('documentation_complete'):
        score += 20
    else:
        missing.append("Documentation")
        issues.append("Documentation incomplete")

    return {
        'score': score,
        'pass': score >= 80,
        'missing_implementations': missing,
        'issues': issues
    }
```

#### 2. Quality Metrics (Weight: 35%)

**Quantitative Metrics**:
- Test pass rate: 100%
- Code coverage: ≥ 80%
- Linting errors: 0
- Type errors: 0 (TypeScript/Python type checking)
- Security vulnerabilities: 0 critical

**Automated Checks**:
```python
def check_quality_metrics(quality: dict) -> dict:
    """
    Evaluate code quality metrics.

    Returns:
        {
            'score': float (0-100),
            'pass': bool,
            'quality_issues': List[dict],
            'critical_issues': List[str]
        }
    """
    score = 0
    quality_issues = []
    critical_issues = []

    # Check test pass rate
    test_pass_rate = quality.get('test_pass_rate', 0)
    if test_pass_rate == 100:
        score += 25
    else:
        issue = f"Test pass rate only {test_pass_rate}% (need 100%)"
        quality_issues.append({'severity': 'high', 'issue': issue})
        if test_pass_rate < 90:
            critical_issues.append(issue)

    # Check code coverage
    coverage = quality.get('code_coverage', 0)
    if coverage >= 80:
        score += 20
    else:
        issue = f"Code coverage only {coverage}% (need ≥ 80%)"
        quality_issues.append({'severity': 'medium', 'issue': issue})

    # Check linting errors
    lint_errors = quality.get('lint_errors', 0)
    if lint_errors == 0:
        score += 15
    else:
        issue = f"{lint_errors} linting errors"
        quality_issues.append({'severity': 'low', 'issue': issue})

    # Check type errors
    type_errors = quality.get('type_errors', 0)
    if type_errors == 0:
        score += 20
    else:
        issue = f"{type_errors} type errors"
        quality_issues.append({'severity': 'high', 'issue': issue})
        if type_errors > 10:
            critical_issues.append(issue)

    # Check security vulnerabilities
    critical_vulns = quality.get('critical_vulnerabilities', 0)
    if critical_vulns == 0:
        score += 20
    else:
        issue = f"{critical_vulns} critical security vulnerabilities"
        quality_issues.append({'severity': 'critical', 'issue': issue})
        critical_issues.append(issue)

    return {
        'score': score,
        'pass': score >= 80 and len(critical_issues) == 0,
        'quality_issues': quality_issues,
        'critical_issues': critical_issues
    }
```

#### 3. Integration Testing (Weight: 15%)

**Quantitative Metrics**:
- Integration tests pass: 100%
- Agent-to-agent communication working: Yes/No
- MCP server integration working: Yes/No
- End-to-end workflows tested: ≥ 3

#### 4. Performance Benchmarks (Weight: 10%)

**Quantitative Metrics**:
- API response time: < 5s for planning tasks
- MCP query latency: < 500ms
- Memory usage: Within acceptable limits
- Concurrent agent support: ≥ 5

### Exit Criteria (GO Decision)

- Overall score ≥ 90%
- All implementations complete (100%)
- No critical quality issues
- All integration tests passing
- Performance benchmarks met

---

## Phase Gate 4: Monitoring → Closure

### Gate Objective

Verify that the system is stable, documented, and ready for knowledge transfer and closure.

### Entry Criteria

- Phase 3 (Execution) completed with GO decision
- System deployed and monitored
- Initial feedback collected

### Evaluation Criteria

#### 1. System Stability (Weight: 30%)

**Quantitative Metrics**:
- Uptime: ≥ 99%
- Error rate: < 1%
- Performance degradation: < 10%
- User-reported issues: < 5 critical

#### 2. Documentation Completeness (Weight: 25%)

**Quantitative Metrics**:
- User guides: Complete
- API documentation: 100% coverage
- Architecture diagrams: Present
- Troubleshooting guide: Complete

#### 3. Knowledge Transfer (Weight: 25%)

**Quantitative Metrics**:
- Training materials created: Yes/No
- Knowledge base populated: Yes/No
- Support documentation: Complete
- Maintenance plan documented: Yes/No

#### 4. Lessons Learned (Weight: 20%)

**Quantitative Metrics**:
- Retrospective conducted: Yes/No
- Action items documented: ≥ 5
- Success metrics reviewed: Yes/No
- Future enhancements listed: ≥ 10

### Exit Criteria (GO Decision)

- Overall score ≥ 85%
- System stable with < 1% error rate
- All documentation complete
- Knowledge transfer completed
- Retrospective conducted

---

## Phase Gate 5: Closure → Complete

### Gate Objective

Verify that all project activities are complete, deliverables accepted, and project can be formally closed.

### Entry Criteria

- Phase 4 (Monitoring) completed with GO decision
- All deliverables finalized
- Stakeholder acceptance received

### Evaluation Criteria

#### 1. Deliverable Acceptance (Weight: 40%)

**Quantitative Metrics**:
- All deliverables submitted: 100%
- Stakeholder sign-off received: Yes/No
- Acceptance criteria met: 100%
- Known issues documented: Yes/No

#### 2. Final Documentation (Weight: 30%)

**Quantitative Metrics**:
- Project closure report: Complete
- Final budget report: Complete
- Final schedule report: Complete
- Lessons learned document: Complete

#### 3. Resource Release (Weight: 20%)

**Quantitative Metrics**:
- Team members reassigned: 100%
- Infrastructure decommissioned (if applicable): Yes/No
- Contracts closed: 100%
- Budget closed: Yes/No

#### 4. Archive and Handoff (Weight: 10%)

**Quantitative Metrics**:
- Project files archived: Yes/No
- Source code repository finalized: Yes/No
- Maintenance team identified: Yes/No
- Handoff complete: Yes/No

### Exit Criteria (GO Decision)

- Overall score ≥ 90%
- All deliverables accepted
- Stakeholder sign-off received
- All resources released
- Project formally closed

---

## Automated Gate Evaluation System

### System Architecture

```python
# phase_gate_evaluator.py
from typing import Dict, List
from enum import Enum

class PhaseGateDecision(Enum):
    GO = "GO"
    CONDITIONAL_GO = "CONDITIONAL_GO"
    NO_GO = "NO_GO"

class PhaseGateEvaluator:
    """
    Automated phase gate evaluation system.
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.evaluations = []

    def evaluate_gate(
        self,
        gate_number: int,
        project_state: dict
    ) -> dict:
        """
        Evaluate a phase gate.

        Args:
            gate_number: 1-5 (corresponding to phase gates)
            project_state: Current project state with all artifacts

        Returns:
            Gate evaluation result with decision and recommendations
        """
        if gate_number == 1:
            result = phase_gate_1_evaluation(project_state)
        elif gate_number == 2:
            result = phase_gate_2_evaluation(project_state)
        elif gate_number == 3:
            result = phase_gate_3_evaluation(project_state)
        elif gate_number == 4:
            result = phase_gate_4_evaluation(project_state)
        elif gate_number == 5:
            result = phase_gate_5_evaluation(project_state)
        else:
            raise ValueError(f"Invalid gate number: {gate_number}")

        # Store evaluation
        self.evaluations.append({
            'gate_number': gate_number,
            'timestamp': datetime.utcnow().isoformat(),
            'result': result
        })

        # Log evaluation
        self.log_evaluation(gate_number, result)

        return result

    def generate_report(self, gate_number: int, result: dict) -> str:
        """
        Generate phase gate report in Markdown format.

        Returns:
            Formatted Markdown report
        """
        report = f"""# Phase Gate {gate_number} Report

**Project**: {self.project_id}
**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
**Decision**: {result['decision']}
**Overall Score**: {result['overall_score']:.1f}% / 100%

## Summary

"""

        if result['decision'] == PhaseGateDecision.GO.value:
            report += "✅ **Approved to proceed to next phase.**\n\n"
        elif result['decision'] == PhaseGateDecision.CONDITIONAL_GO.value:
            report += "⚠️ **Conditionally approved.** Complete required actions before proceeding.\n\n"
        else:
            report += "❌ **Not approved.** Critical issues must be resolved.\n\n"

        report += "## Criteria Evaluation\n\n"

        for criterion, score in result['criteria_scores'].items():
            status = "✅ PASS" if score >= 70 else "❌ FAIL"
            report += f"### {criterion.title()}\n"
            report += f"- **Score**: {score:.1f}%\n"
            report += f"- **Status**: {status}\n\n"

        if result.get('critical_issues'):
            report += "## Critical Issues\n\n"
            for issue in result['critical_issues']:
                report += f"- ❌ {issue}\n"
            report += "\n"

        if result.get('required_actions'):
            report += "## Required Actions\n\n"
            for i, action in enumerate(result['required_actions'], 1):
                report += f"{i}. {action}\n"
            report += "\n"

        if result.get('recommendations'):
            report += "## Recommendations\n\n"
            for i, rec in enumerate(result['recommendations'], 1):
                report += f"{i}. {rec}\n"
            report += "\n"

        report += "## Sign-off\n\n"
        report += f"- **Coordinator Agent**: PM-Agents System\n"
        report += f"- **Date**: {datetime.utcnow().strftime('%Y-%m-%d')}\n"

        return report

    def log_evaluation(self, gate_number: int, result: dict):
        """Log evaluation to monitoring system."""
        logger.info({
            'event': 'phase_gate_evaluation',
            'project_id': self.project_id,
            'gate_number': gate_number,
            'decision': result['decision'],
            'overall_score': result['overall_score'],
            'timestamp': datetime.utcnow().isoformat()
        })
```

---

## Usage in PM-Agents

### Coordinator Integration

```python
# coordinator_agent.py
class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.gate_evaluator = PhaseGateEvaluator(self.project_id)

    async def complete_phase(self, phase_number: int):
        """
        Complete a project phase and conduct phase gate review.
        """
        # Collect project state
        project_state = await self.collect_project_state()

        # Evaluate phase gate
        gate_result = self.gate_evaluator.evaluate_gate(
            gate_number=phase_number,
            project_state=project_state
        )

        # Generate report
        report = self.gate_evaluator.generate_report(
            gate_number=phase_number,
            result=gate_result
        )

        # Save report
        await self.save_report(f"phase_gate_{phase_number}_report.md", report)

        # Make decision
        if gate_result['decision'] == PhaseGateDecision.GO.value:
            logger.info(f"Phase Gate {phase_number}: GO - Proceeding to next phase")
            return True
        elif gate_result['decision'] == PhaseGateDecision.CONDITIONAL_GO.value:
            logger.warning(
                f"Phase Gate {phase_number}: CONDITIONAL_GO - "
                f"Actions required: {gate_result['required_actions']}"
            )
            # Execute required actions or prompt user
            await self.handle_conditional_go(gate_result)
            return False
        else:
            logger.error(
                f"Phase Gate {phase_number}: NO_GO - "
                f"Critical issues: {gate_result['critical_issues']}"
            )
            # Escalate to user
            await self.escalate_no_go(gate_result)
            return False
```

---

## Best Practices

### DO
- ✅ Conduct phase gate reviews at the end of each phase
- ✅ Use quantitative metrics where possible
- ✅ Document all evaluation criteria
- ✅ Generate formal reports for each gate
- ✅ Involve stakeholders in critical decisions
- ✅ Address conditional GO actions promptly
- ✅ Learn from NO-GO decisions
- ✅ Archive all gate reports for audit trail

### DON'T
- ❌ Skip phase gates to save time
- ❌ Override NO-GO decisions without addressing issues
- ❌ Use subjective criteria without clear definitions
- ❌ Ignore low scores in non-critical areas
- ❌ Proceed with unresolved blockers
- ❌ Fail to document decision rationale

---

**Last Updated**: 2025-10-29
**Status**: Complete - Ready for Implementation
