# Planner Agent Specification

**Agent Type**: Strategic Planning Layer (Tier 2)
**Version**: 1.0
**Status**: Planning Phase
**Date**: 2025-10-28

---

## Overview

The Planner Agent is the strategic planning layer in the PM-Agents hierarchical system. It receives high-level objectives from the Coordinator Agent, decomposes them into detailed plans, determines which specialist agents are needed, and delegates execution to the Supervisor Agent.

---

## Role and Responsibilities

### Primary Responsibilities

1. **Receive objectives from Coordinator**
   - Parse high-level objectives and requirements
   - Understand project context and constraints
   - Identify success criteria

2. **Task decomposition**
   - Break down objectives into actionable tasks
   - Create work breakdown structure (WBS)
   - Identify task dependencies
   - Estimate effort and resources per task

3. **Agent selection**
   - Determine which specialist agents are needed
   - Assign tasks to appropriate agents
   - Plan agent coordination and handoffs

4. **Planning artifacts creation**
   - Generate project plans with phases and tasks
   - Create resource allocation plans
   - Develop risk mitigation strategies
   - Define quality gates and success criteria

5. **Delegate to Supervisor Agent**
   - Pass detailed plan to Supervisor
   - Provide task assignments and dependencies
   - Specify validation criteria

6. **Monitor and adapt**
   - Receive progress updates from Supervisor
   - Adapt plan based on actual progress
   - Escalate blockers to Coordinator
   - Replan when necessary

### Responsibilities Outside Scope

- ❌ Direct management of specialist agents (Supervisor Agent)
- ❌ Code generation or technical implementation (Specialist Agents)
- ❌ Top-level GO/NO-GO decisions (Coordinator Agent)
- ❌ Direct user communication (via Coordinator only)

---

## Input/Output Schemas

### Input: Planning Request (from Coordinator)

```json
{
  "message_id": "string (UUID)",
  "from": "coordinator",
  "to": "planner",
  "type": "planning_request",
  "timestamp": "ISO8601 datetime",
  "payload": {
    "request_id": "string",
    "objective": "string (high-level goal)",
    "requirements": [
      {
        "id": "string",
        "requirement": "string",
        "priority": "string (must_have|should_have|nice_to_have)",
        "acceptance_criteria": ["string"]
      }
    ],
    "constraints": {
      "max_tokens": "integer",
      "max_time_seconds": "integer",
      "technologies": ["string"],
      "project_type": "string (frontend|ml|analytics|fullstack|research)",
      "existing_codebase": "boolean"
    },
    "context": {
      "project_path": "string (optional)",
      "existing_files": ["string (optional)"],
      "user_preferences": {}
    }
  }
}
```

**Example**:
```json
{
  "message_id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
  "from": "coordinator",
  "to": "planner",
  "type": "planning_request",
  "timestamp": "2025-10-28T10:30:00Z",
  "payload": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "objective": "Create a Next.js application with Supabase authentication and product catalog",
    "requirements": [
      {
        "id": "REQ-001",
        "requirement": "User authentication with email/password and OAuth",
        "priority": "must_have",
        "acceptance_criteria": [
          "Users can register with email/password",
          "Users can log in with Google OAuth",
          "Sessions persist across page reloads"
        ]
      },
      {
        "id": "REQ-002",
        "requirement": "Product catalog with CRUD operations",
        "priority": "must_have",
        "acceptance_criteria": [
          "Admin can create/edit/delete products",
          "Users can view product list with pagination",
          "Products have images, title, description, price"
        ]
      }
    ],
    "constraints": {
      "max_tokens": 50000,
      "max_time_seconds": 300,
      "technologies": ["Next.js 14", "Supabase", "TypeScript", "TailwindCSS"],
      "project_type": "frontend",
      "existing_codebase": false
    },
    "context": {
      "project_path": "/home/user/projects/my-ecommerce",
      "user_preferences": {
        "component_library": "shadcn/ui",
        "state_management": "zustand"
      }
    }
  }
}
```

### Output: Planning Response (to Coordinator)

```json
{
  "message_id": "string (UUID)",
  "from": "planner",
  "to": "coordinator",
  "type": "planning_response",
  "timestamp": "ISO8601 datetime",
  "in_reply_to": "string (request message_id)",
  "payload": {
    "status": "string (success|partial|failed)",
    "plan": {
      "plan_id": "string (UUID)",
      "objective": "string",
      "phases": [
        {
          "phase_id": "string",
          "phase_name": "string (initialization|development|validation|documentation)",
          "order": "integer",
          "tasks": [
            {
              "task_id": "string",
              "description": "string",
              "assigned_to": "string (agent type)",
              "dependencies": ["string (task_ids)"],
              "estimated_tokens": "integer",
              "estimated_time_seconds": "integer",
              "priority": "string (critical|high|medium|low)",
              "deliverables": ["string"],
              "validation_criteria": ["string"]
            }
          ],
          "phase_gate_criteria": ["string"]
        }
      ],
      "agent_assignments": {
        "spec_kit": ["task_ids"],
        "frontend_coder": ["task_ids"],
        "qdrant_vector": ["task_ids"],
        "typescript_validator": ["task_ids"],
        "reporter": ["task_ids"]
      },
      "total_estimated_tokens": "integer",
      "total_estimated_time_seconds": "integer",
      "confidence": "float (0.0-1.0)"
    },
    "risks": [
      {
        "risk_id": "string",
        "description": "string",
        "severity": "string (critical|high|medium|low)",
        "probability": "string (likely|possible|unlikely)",
        "impact": "string (severe|moderate|minor)",
        "mitigation": "string",
        "owner": "string (agent type)"
      }
    ],
    "assumptions": ["string"],
    "recommendations": ["string"],
    "alternatives_considered": [
      {
        "alternative": "string",
        "pros": ["string"],
        "cons": ["string"],
        "reason_not_selected": "string"
      }
    ]
  }
}
```

---

## Task Decomposition Algorithm

### Step 1: Requirement Analysis

```python
def analyze_requirements(objective, requirements, constraints, context):
    """
    Analyze requirements and extract key information

    Returns:
        RequirementAnalysis with categorized requirements
    """
    analysis = RequirementAnalysis()

    # Categorize requirements by type
    for req in requirements:
        category = categorize_requirement(req.requirement)
        analysis.add_requirement(category, req)

    # Categories: frontend_ui, backend_api, database, auth, infrastructure, testing, docs

    # Identify technical stack
    analysis.tech_stack = infer_tech_stack(requirements, constraints.technologies)

    # Identify complexity level
    analysis.complexity = estimate_complexity(requirements, context)

    return analysis
```

### Step 2: Agent Selection

```python
def select_agents(requirement_analysis, project_type, existing_codebase):
    """
    Determine which specialist agents are needed

    Returns:
        List of agent types required
    """
    selected_agents = []

    # Always needed
    selected_agents.append('qdrant_vector')  # For knowledge management

    # Project initialization (if new project)
    if not existing_codebase:
        selected_agents.append('spec_kit')

    # Based on project type
    if project_type in ['frontend', 'fullstack']:
        selected_agents.append('frontend_coder')
        selected_agents.append('typescript_validator')

        # Check if Supabase mentioned
        if 'supabase' in requirement_analysis.tech_stack.lower():
            # Frontend agent handles Supabase integration
            pass

    if project_type in ['ml', 'data_science']:
        selected_agents.append('python_ml')

    if project_type in ['analytics', 'data_viz']:
        selected_agents.append('r_analytics')

    # Check if research needed
    if requirement_analysis.needs_research:
        selected_agents.append('research')

    # Check if browser automation needed
    if requirement_analysis.needs_browser_automation:
        selected_agents.append('browser')

    # Always add reporter for documentation
    selected_agents.append('reporter')

    return selected_agents
```

### Step 3: Task Creation

```python
def create_tasks(requirement_analysis, selected_agents, constraints):
    """
    Create detailed tasks from requirements

    Returns:
        List of Task objects with dependencies
    """
    tasks = []
    task_id_counter = 1

    # Phase 1: Initialization
    if 'spec_kit' in selected_agents:
        task = Task(
            task_id=f"TASK-{task_id_counter:03d}",
            description="Initialize project structure using Specify",
            assigned_to="spec_kit",
            dependencies=[],
            estimated_tokens=5000,
            estimated_time_seconds=30,
            priority="critical",
            deliverables=["Project structure", "Configuration files", "Dependencies"],
            validation_criteria=["Project builds successfully", "All dependencies install"]
        )
        tasks.append(task)
        task_id_counter += 1

    # Phase 2: Knowledge Indexing
    if 'qdrant_vector' in selected_agents:
        dependencies = [tasks[-1].task_id] if tasks else []
        task = Task(
            task_id=f"TASK-{task_id_counter:03d}",
            description="Index codebase and documentation in Qdrant",
            assigned_to="qdrant_vector",
            dependencies=dependencies,
            estimated_tokens=3000,
            estimated_time_seconds=20,
            priority="high",
            deliverables=["Indexed codebase", "Search capability"],
            validation_criteria=["Semantic search returns relevant results"]
        )
        tasks.append(task)
        task_id_counter += 1

    # Phase 3: Development (per requirement)
    for req in requirement_analysis.must_have_requirements:
        agent = determine_agent_for_requirement(req, selected_agents)
        dependencies = get_dependencies_for_requirement(req, tasks)

        task = Task(
            task_id=f"TASK-{task_id_counter:03d}",
            description=f"Implement: {req.requirement}",
            assigned_to=agent,
            dependencies=dependencies,
            estimated_tokens=estimate_tokens_for_requirement(req),
            estimated_time_seconds=estimate_time_for_requirement(req),
            priority=map_priority(req.priority),
            deliverables=extract_deliverables(req),
            validation_criteria=req.acceptance_criteria
        )
        tasks.append(task)
        task_id_counter += 1

    # Phase 4: Validation
    if 'typescript_validator' in selected_agents:
        dev_tasks = [t.task_id for t in tasks if t.assigned_to == 'frontend_coder']
        task = Task(
            task_id=f"TASK-{task_id_counter:03d}",
            description="Validate TypeScript code quality and run tests",
            assigned_to="typescript_validator",
            dependencies=dev_tasks,
            estimated_tokens=4000,
            estimated_time_seconds=40,
            priority="high",
            deliverables=["Test results", "Type checking report", "Quality report"],
            validation_criteria=["Zero TypeScript errors", "80%+ test coverage"]
        )
        tasks.append(task)
        task_id_counter += 1

    # Phase 5: Documentation
    if 'reporter' in selected_agents:
        all_dev_tasks = [t.task_id for t in tasks if t.assigned_to != 'reporter']
        task = Task(
            task_id=f"TASK-{task_id_counter:03d}",
            description="Generate project documentation",
            assigned_to="reporter",
            dependencies=all_dev_tasks,
            estimated_tokens=3000,
            estimated_time_seconds=25,
            priority="medium",
            deliverables=["README.md", "API documentation", "User guide"],
            validation_criteria=["Documentation completeness > 90%"]
        )
        tasks.append(task)
        task_id_counter += 1

    return tasks
```

### Step 4: Dependency Resolution

```python
def resolve_dependencies(tasks):
    """
    Ensure dependencies are valid and optimize execution order

    Returns:
        Tasks sorted by execution order (topological sort)
    """
    # Build dependency graph
    graph = {}
    for task in tasks:
        graph[task.task_id] = task.dependencies

    # Detect cycles
    if has_cycle(graph):
        raise ValueError("Circular dependency detected in task graph")

    # Topological sort
    sorted_tasks = topological_sort(tasks, graph)

    # Calculate parallel execution opportunities
    execution_levels = assign_execution_levels(sorted_tasks, graph)

    return sorted_tasks, execution_levels
```

### Step 5: Resource Estimation

```python
def estimate_resources(tasks, constraints):
    """
    Estimate total resources needed

    Returns:
        ResourceEstimate with tokens, time, cost
    """
    total_tokens = sum(task.estimated_tokens for task in tasks)
    total_time = calculate_critical_path_time(tasks)
    estimated_cost = estimate_cost(total_tokens, model='claude-sonnet-4-5')

    # Add buffer (20%)
    total_tokens_with_buffer = int(total_tokens * 1.2)
    total_time_with_buffer = int(total_time * 1.2)

    # Check against constraints
    if total_tokens_with_buffer > constraints.max_tokens:
        raise ResourceExceededError(
            f"Estimated tokens ({total_tokens_with_buffer}) exceeds budget ({constraints.max_tokens})"
        )

    if total_time_with_buffer > constraints.max_time_seconds:
        raise ResourceExceededError(
            f"Estimated time ({total_time_with_buffer}s) exceeds limit ({constraints.max_time_seconds}s)"
        )

    return ResourceEstimate(
        tokens=total_tokens_with_buffer,
        time_seconds=total_time_with_buffer,
        cost_usd=estimated_cost,
        confidence=0.75  # 75% confidence in estimate
    )
```

---

## Planning Strategies

### Strategy 1: Incremental Planning (Default)

**When to use**: Standard projects with clear requirements

**Approach**:
- Plan all phases upfront
- Create detailed tasks for must-have requirements
- Outline tasks for should-have and nice-to-have
- Execute in strict phase order

**Pros**: Predictable, easy to track progress
**Cons**: Less flexible, may waste effort on later tasks

### Strategy 2: Agile Planning

**When to use**: Projects with evolving requirements

**Approach**:
- Plan only the next 2-3 tasks in detail
- Replan after each task completion
- Adapt based on learnings
- Allow requirement changes

**Pros**: Highly flexible, adapts to learnings
**Cons**: Less predictable, harder to estimate total effort

### Strategy 3: Critical Path Planning

**When to use**: Time-constrained projects

**Approach**:
- Identify critical path (longest dependency chain)
- Prioritize tasks on critical path
- Parallelize non-critical tasks
- Minimize overall completion time

**Pros**: Fastest completion time
**Cons**: May require more resources (parallel agents)

### Strategy Selection Algorithm

```python
def select_planning_strategy(requirements, constraints, context):
    """
    Select appropriate planning strategy
    """
    # If tight time constraint: Critical Path
    if constraints.max_time_seconds < 180:  # < 3 minutes
        return PlanningStrategy.CRITICAL_PATH

    # If many unknowns or research needed: Agile
    if context.get('has_unknowns', False) or 'research' in requirements:
        return PlanningStrategy.AGILE

    # Default: Incremental
    return PlanningStrategy.INCREMENTAL
```

---

## Risk Identification

### Common Risks by Project Type

**Frontend Projects**:
- R1: Incompatible package versions
- R2: TypeScript errors not caught until runtime
- R3: State management complexity
- R4: Supabase schema mismatch

**ML Projects**:
- R5: Dataset quality issues
- R6: Model training time exceeds budget
- R7: Overfitting/underfitting
- R8: Hardware limitations (GPU required)

**Analytics Projects**:
- R9: Data cleaning takes longer than expected
- R10: Visualization requirements unclear
- R11: R package conflicts

**General Risks**:
- R12: Requirement ambiguity
- R13: Token budget insufficient
- R14: Agent communication timeout
- R15: Quality standards not met

### Risk Assessment Algorithm

```python
def assess_risks(plan, requirements, constraints, context):
    """
    Identify and assess risks for the plan
    """
    risks = []

    # Check token budget adequacy
    if plan.total_estimated_tokens > constraints.max_tokens * 0.8:
        risks.append(Risk(
            risk_id="RISK-001",
            description="Token budget may be insufficient",
            severity="high",
            probability="likely",
            impact="severe",
            mitigation="Request budget increase or reduce scope",
            owner="coordinator"
        ))

    # Check for complex dependencies
    if has_long_dependency_chains(plan):
        risks.append(Risk(
            risk_id="RISK-002",
            description="Long dependency chains increase failure risk",
            severity="medium",
            probability="possible",
            impact="moderate",
            mitigation="Identify alternative paths, add checkpoints",
            owner="supervisor"
        ))

    # Check for new/experimental technologies
    if uses_experimental_tech(requirements, constraints):
        risks.append(Risk(
            risk_id="RISK-003",
            description="Experimental technologies may have limited documentation",
            severity="medium",
            probability="likely",
            impact="moderate",
            mitigation="Allocate extra time for research agent",
            owner="research"
        ))

    return risks
```

---

## Communication Patterns

### To Supervisor Agent

**Message Type**: ExecutionRequest

```json
{
  "message_id": "string (UUID)",
  "from": "planner",
  "to": "supervisor",
  "type": "execution_request",
  "timestamp": "ISO8601 datetime",
  "payload": {
    "plan_id": "string",
    "tasks": [...],  // Full task list with dependencies
    "agent_assignments": {...},
    "validation_criteria": [...],
    "risks": [...]
  }
}
```

### From Supervisor Agent

**Message Type**: ExecutionUpdate

```json
{
  "message_id": "string (UUID)",
  "from": "supervisor",
  "to": "planner",
  "type": "execution_update",
  "timestamp": "ISO8601 datetime",
  "payload": {
    "plan_id": "string",
    "status": "string",
    "tasks_completed": [...],
    "tasks_in_progress": [...],
    "tasks_blocked": [...],
    "requires_replanning": "boolean",
    "reason": "string"
  }
}
```

---

## MCP Tools Required

The Planner Agent **does not directly use MCP tools**. It operates at the planning abstraction level.

**Indirect MCP Tool Usage** (via delegation):
- All tools used via Supervisor → Specialists

**Optional**: May use `memory` MCP server to:
- Store planning templates
- Retrieve similar past plans
- Learn from historical data

---

## Success Criteria

1. **Planning Accuracy**: ≥80% of plans complete within estimated resources
2. **Task Granularity**: Tasks are appropriately sized (5-15 min each)
3. **Dependency Correctness**: Zero circular dependencies, all dependencies valid
4. **Agent Selection**: ≥95% correct agent assignments (validated post-execution)
5. **Risk Prediction**: ≥70% of actual issues were identified as risks
6. **Planning Speed**: <10 seconds to generate plan for typical project

---

## Implementation Notes

### Key Classes

```python
class PlannerAgent:
    def __init__(self, config: Config):
        self.config = config
        self.strategy_selector = StrategySelector()
        self.task_decomposer = TaskDecomposer()
        self.agent_selector = AgentSelector()
        self.resource_estimator = ResourceEstimator()
        self.risk_assessor = RiskAssessor()

    async def plan(self, request: PlanningRequest) -> PlanningResponse:
        """Main planning method"""
        # 1. Analyze requirements
        analysis = self.analyze_requirements(request)

        # 2. Select planning strategy
        strategy = self.strategy_selector.select(analysis, request.constraints)

        # 3. Select agents
        agents = self.agent_selector.select(analysis, request.payload.project_type)

        # 4. Create tasks
        tasks = self.task_decomposer.decompose(analysis, agents, strategy)

        # 5. Resolve dependencies
        tasks, levels = self.resolve_dependencies(tasks)

        # 6. Estimate resources
        resources = self.resource_estimator.estimate(tasks, request.constraints)

        # 7. Assess risks
        risks = self.risk_assessor.assess(tasks, analysis, request.constraints)

        # 8. Create plan
        plan = self.create_plan(tasks, agents, resources, risks)

        return PlanningResponse(plan=plan, risks=risks)
```

---

**Document Owner**: PM-Agents Architecture Team
**Last Updated**: 2025-10-28
**Status**: ✅ APPROVED for Implementation (Phase 3)
**Next**: Create Supervisor Agent Specification
