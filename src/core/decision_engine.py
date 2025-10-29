"""
Decision Engine for Coordinator Agent
Implements decision logic for request acceptance, phase gates, and escalation handling
Based on COORDINATOR_AGENT_SPEC.md decision algorithms
"""

from enum import Enum
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


class Decision(Enum):
    """Decision outcomes"""
    ACCEPT = "accept"
    REJECT = "reject"
    CLARIFY = "clarify"
    GO = "GO"
    CONDITIONAL_GO = "CONDITIONAL_GO"
    NO_GO = "NO_GO"


@dataclass
class DecisionResult:
    """Result of a decision with rationale"""
    decision: Decision
    rationale: str
    confidence: float  # 0.0 to 1.0
    required_actions: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.required_actions is None:
            self.required_actions = []
        if self.metadata is None:
            self.metadata = {}


class DecisionEngine:
    """
    Decision engine for Coordinator Agent
    Implements algorithms from COORDINATOR_AGENT_SPEC.md
    """

    # Supported project types
    SUPPORTED_TYPES = [
        "frontend",
        "backend",
        "ml",
        "analytics",
        "fullstack",
        "research"
    ]

    # Quality thresholds
    QUALITY_THRESHOLD = 70.0  # Minimum quality score for phase gate
    MIN_TOKENS_FOR_NEXT_PHASE = 5000  # Minimum tokens remaining to proceed

    def __init__(self):
        """Initialize decision engine"""
        self.decision_history: List[Dict[str, Any]] = []

    def accept_request(
        self,
        user_request: str,
        context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> DecisionResult:
        """
        Decide whether to accept a user request
        Algorithm from COORDINATOR_AGENT_SPEC.md section "Request Acceptance Decision"

        Args:
            user_request: Natural language request
            context: Request context (project_path, project_type, etc.)
            preferences: User preferences (model, max_budget_tokens, max_time_seconds)

        Returns:
            DecisionResult with accept/reject/clarify decision
        """

        # 1. Parse and analyze request
        intent = self._parse_intent(user_request)
        project_type = self._detect_project_type(user_request, context)

        # 2. Safety check
        if not self._is_safe(user_request):
            return DecisionResult(
                decision=Decision.REJECT,
                rationale="Request violates safety policies",
                confidence=1.0,
                metadata={"reason": "safety_violation"}
            )

        # 3. Clarity check
        if self._is_ambiguous(user_request):
            clarifications = self._generate_clarification_questions(user_request, context)
            return DecisionResult(
                decision=Decision.CLARIFY,
                rationale="Request requires clarification",
                confidence=0.8,
                required_actions=clarifications,
                metadata={"ambiguity_reasons": ["unclear_requirements", "multiple_interpretations"]}
            )

        # 4. Feasibility check
        estimated_resources = self._estimate_resources(user_request, project_type)
        max_budget = preferences.get("max_budget_tokens", 50000)

        if estimated_resources["tokens"] > max_budget:
            return DecisionResult(
                decision=Decision.REJECT,
                rationale=f"Exceeds token budget: {estimated_resources['tokens']} > {max_budget}",
                confidence=0.9,
                metadata={"estimated_tokens": estimated_resources["tokens"], "budget": max_budget}
            )

        # 5. Support check
        if project_type not in self.SUPPORTED_TYPES:
            return DecisionResult(
                decision=Decision.REJECT,
                rationale=f"Project type '{project_type}' not supported. Supported types: {', '.join(self.SUPPORTED_TYPES)}",
                confidence=1.0,
                metadata={"detected_type": project_type, "supported_types": self.SUPPORTED_TYPES}
            )

        # All checks passed
        return DecisionResult(
            decision=Decision.ACCEPT,
            rationale="Request approved for processing",
            confidence=0.95,
            metadata={
                "intent": intent,
                "project_type": project_type,
                "estimated_resources": estimated_resources
            }
        )

    def phase_gate_decision(
        self,
        phase: str,
        phase_outputs: Dict[str, Any],
        project_state: Dict[str, Any]
    ) -> DecisionResult:
        """
        Make GO/NO-GO decision for phase gate
        Algorithm from COORDINATOR_AGENT_SPEC.md section "Phase Gate Decision"

        Args:
            phase: Phase being reviewed
            phase_outputs: Outputs from the phase
            project_state: Current project state

        Returns:
            DecisionResult with GO/CONDITIONAL_GO/NO_GO decision
        """

        score = 100.0
        issues_found = []
        required_actions = []

        # 1. Check deliverables
        required_deliverables = self._get_required_deliverables(phase)
        deliverables_complete = self._check_deliverables_complete(phase_outputs, required_deliverables)

        if not deliverables_complete:
            return DecisionResult(
                decision=Decision.NO_GO,
                rationale="Missing required deliverables",
                confidence=1.0,
                required_actions=["Complete all required deliverables before proceeding"],
                metadata={"missing_deliverables": required_deliverables}
            )

        # 2. Check quality
        quality_score = self._assess_quality(phase_outputs)
        if quality_score < self.QUALITY_THRESHOLD:
            score -= 30
            issues_found.append(f"Quality below threshold: {quality_score:.1f} < {self.QUALITY_THRESHOLD}")
            required_actions.append(f"Improve quality to at least {self.QUALITY_THRESHOLD}")

        # 3. Check risks
        risks = project_state.get('risks', [])
        critical_risks = [r for r in risks if r.get('severity') == 'critical' and not r.get('mitigated')]

        if critical_risks:
            score -= 25
            issues_found.append(f"Critical risks not mitigated: {len(critical_risks)}")
            required_actions.append("Mitigate all critical risks")

        # 4. Check blockers
        blockers = project_state.get('blockers', [])
        critical_blockers = [b for b in blockers if b.get('severity') == 'critical' and b.get('status') != 'resolved']

        if critical_blockers:
            return DecisionResult(
                decision=Decision.NO_GO,
                rationale=f"Critical blockers must be resolved: {critical_blockers}",
                confidence=1.0,
                required_actions=["Resolve all critical blockers"],
                metadata={"blockers": critical_blockers}
            )

        # 5. Check resources
        tokens_remaining = project_state.get('tokens_remaining', 0)
        if tokens_remaining < self.MIN_TOKENS_FOR_NEXT_PHASE:
            return DecisionResult(
                decision=Decision.NO_GO,
                rationale=f"Insufficient tokens remaining: {tokens_remaining} < {self.MIN_TOKENS_FOR_NEXT_PHASE}",
                confidence=1.0,
                required_actions=["Request additional token budget or reduce scope"],
                metadata={"tokens_remaining": tokens_remaining}
            )

        # Determine final decision
        if score >= 90:
            decision = Decision.GO
            rationale = "All criteria met, proceed to next phase"
        elif score >= 70:
            decision = Decision.CONDITIONAL_GO
            rationale = f"Proceed with conditions. Score: {score:.1f}/100. Issues: {', '.join(issues_found)}"
        else:
            decision = Decision.NO_GO
            rationale = f"Quality insufficient. Score: {score:.1f}/100. Issues: {', '.join(issues_found)}"

        confidence = min(score / 100.0, 1.0)

        return DecisionResult(
            decision=decision,
            rationale=rationale,
            confidence=confidence,
            required_actions=required_actions,
            metadata={"score": score, "issues": issues_found}
        )

    def handle_escalation(self, escalation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle escalation from lower-tier agents
        Algorithm from COORDINATOR_AGENT_SPEC.md section "Escalation Handling"

        Args:
            escalation: Escalation information

        Returns:
            Escalation response with actions
        """

        escalation_type = escalation.get('type')
        severity = escalation.get('severity', 'medium')

        if escalation_type == 'technical_blocker':
            if severity == 'critical':
                return {
                    "action": "pause_and_ask_user",
                    "message": "Critical technical blocker requires user guidance",
                    "escalation": escalation
                }
            else:
                return {
                    "action": "try_alternative_approach",
                    "message": "Delegating to alternative specialist agent",
                    "escalation": escalation
                }

        elif escalation_type == 'resource_exhaustion':
            return {
                "action": "request_budget_increase_or_terminate",
                "message": "Resource budget exhausted, requesting increase or terminating",
                "escalation": escalation
            }

        elif escalation_type == 'clarification_needed':
            return {
                "action": "ask_user_for_clarification",
                "message": "Agent requires user clarification",
                "escalation": escalation
            }

        elif escalation_type == 'quality_failure':
            return {
                "action": "retry_with_alternative",
                "message": "Quality check failed, retrying with different approach",
                "escalation": escalation
            }

        elif escalation_type == 'safety_concern':
            return {
                "action": "terminate_and_report",
                "message": "Safety concern detected, terminating immediately",
                "escalation": escalation,
                "priority": "critical"
            }

        else:
            return {
                "action": "ask_user_for_decision",
                "message": f"Unknown escalation type: {escalation_type}",
                "escalation": escalation
            }

    # Helper methods

    def _parse_intent(self, request: str) -> str:
        """Parse user intent from request"""
        request_lower = request.lower()

        if any(word in request_lower for word in ["create", "build", "generate", "develop"]):
            return "create_project"
        elif any(word in request_lower for word in ["enhance", "improve", "optimize", "refactor"]):
            return "enhance_project"
        elif any(word in request_lower for word in ["research", "analyze", "investigate", "study"]):
            return "research"
        elif any(word in request_lower for word in ["fix", "debug", "solve", "resolve"]):
            return "fix_issue"
        else:
            return "unknown"

    def _detect_project_type(self, request: str, context: Dict[str, Any]) -> str:
        """Detect project type from request and context"""
        # Check context first
        if context.get("project_type"):
            return context["project_type"]

        request_lower = request.lower()

        # Frontend indicators
        if any(word in request_lower for word in ["react", "next.js", "vue", "angular", "frontend", "ui", "website"]):
            return "frontend"

        # Backend indicators
        if any(word in request_lower for word in ["api", "backend", "server", "express", "fastapi", "flask"]):
            return "backend"

        # ML indicators
        if any(word in request_lower for word in ["machine learning", "ml", "model", "pytorch", "tensorflow", "neural network"]):
            return "ml"

        # Analytics indicators
        if any(word in request_lower for word in ["analytics", "data analysis", "ggplot", "tidyverse", "shiny", "r markdown"]):
            return "analytics"

        # Fullstack indicators
        if any(word in request_lower for word in ["fullstack", "full-stack", "full stack"]):
            return "fullstack"

        # Research indicators
        if any(word in request_lower for word in ["research", "study", "analyze", "investigate"]):
            return "research"

        return "unknown"

    def _is_safe(self, request: str) -> bool:
        """Check if request is safe (no malicious intent)"""
        request_lower = request.lower()

        # Check for obviously malicious keywords
        malicious_keywords = [
            "malware", "virus", "ransomware", "keylogger",
            "exploit", "vulnerability scanner", "password cracker",
            "ddos", "botnet", "backdoor"
        ]

        return not any(keyword in request_lower for keyword in malicious_keywords)

    def _is_ambiguous(self, request: str) -> bool:
        """Check if request is ambiguous"""
        # Very simple check - in production would use more sophisticated NLP
        return len(request.split()) < 5 or "?" in request

    def _generate_clarification_questions(self, request: str, context: Dict[str, Any]) -> List[str]:
        """Generate clarification questions for ambiguous request"""
        questions = []

        if not context.get("project_type"):
            questions.append("What type of project is this? (frontend/backend/ml/analytics/fullstack)")

        if len(request.split()) < 10:
            questions.append("Could you provide more details about the requirements?")

        if "?" in request:
            questions.append("Please rephrase your request as a statement rather than a question")

        return questions or ["Could you provide more details about what you'd like to accomplish?"]

    def _estimate_resources(self, request: str, project_type: str) -> Dict[str, int]:
        """Estimate resource requirements"""
        # Simple heuristic - in production would use ML model
        base_tokens = {
            "frontend": 15000,
            "backend": 20000,
            "ml": 30000,
            "analytics": 25000,
            "fullstack": 40000,
            "research": 10000,
            "unknown": 15000
        }

        tokens = base_tokens.get(project_type, 15000)

        # Adjust based on complexity indicators
        complexity_keywords = ["complex", "advanced", "comprehensive", "detailed", "multiple"]
        if any(keyword in request.lower() for keyword in complexity_keywords):
            tokens *= 1.5

        return {
            "tokens": int(tokens),
            "estimated_time_seconds": int(tokens / 10),  # Rough estimate
            "estimated_cost_usd": tokens * 0.00003  # Rough Claude cost estimate
        }

    def _get_required_deliverables(self, phase: str) -> List[str]:
        """Get required deliverables for a phase"""
        deliverables = {
            "initiation": [
                "feasibility_assessment",
                "scope_definition",
                "stakeholder_identification",
                "initial_risk_assessment"
            ],
            "planning": [
                "project_plan",
                "resource_allocation",
                "schedule",
                "risk_management_plan"
            ],
            "execution": [
                "implementation",
                "code_deliverables",
                "documentation"
            ],
            "monitoring": [
                "progress_reports",
                "quality_metrics",
                "issue_logs"
            ],
            "closure": [
                "final_deliverables",
                "lessons_learned",
                "project_closure_report"
            ]
        }

        return deliverables.get(phase, [])

    def _check_deliverables_complete(
        self,
        phase_outputs: Dict[str, Any],
        required_deliverables: List[str]
    ) -> bool:
        """Check if required deliverables are complete"""
        # Simple check - verify that outputs contain required deliverable types
        output_types = [output.get("type") for output in phase_outputs.get("deliverables", [])]

        # At least 70% of required deliverables should be present
        present_count = sum(1 for req in required_deliverables if any(req in str(ot).lower() for ot in output_types))

        return present_count >= (len(required_deliverables) * 0.7)

    def _assess_quality(self, phase_outputs: Dict[str, Any]) -> float:
        """Assess quality of phase outputs"""
        # Simple quality scoring - in production would use more sophisticated analysis
        score = 75.0  # Base score

        deliverables = phase_outputs.get("deliverables", [])
        if not deliverables:
            return 0.0

        # Bonus for documentation
        has_documentation = any("documentation" in str(d.get("type", "")).lower() for d in deliverables)
        if has_documentation:
            score += 10

        # Bonus for tests
        has_tests = any("test" in str(d.get("type", "")).lower() for d in deliverables)
        if has_tests:
            score += 10

        # Penalty for issues
        issues = phase_outputs.get("issues", [])
        critical_issues = [i for i in issues if i.get("severity") == "critical"]
        score -= len(critical_issues) * 10

        return min(max(score, 0.0), 100.0)
