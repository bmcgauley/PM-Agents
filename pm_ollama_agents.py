"""
Project Manager Multi-Agent System using Ollama Gemma3
For academic assignment - uses local LLM inference
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime

class OllamaPMAgent:
    """
    Base agent class using Ollama Gemma3 for local inference
    """
    
    def __init__(self, agent_type: str, ollama_url: str = "http://localhost:11434"):
        self.agent_type = agent_type
        self.ollama_url = ollama_url
        self.model = "gemma2:latest"  # or "gemma3" when available
        self.conversation_history = []
        
    def call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """
        Call Ollama API for inference
        
        Args:
            prompt: User prompt
            system_prompt: System instructions for the model
            
        Returns:
            Model response text
        """
        url = f"{self.ollama_url}/api/generate"
        
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser Request:\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent-specific task
        
        Args:
            task: Task description
            context: Project context
            
        Returns:
            Task execution results
        """
        system_prompt = self.get_system_prompt()
        
        prompt = f"""Task: {task}

Project Context:
{json.dumps(context, indent=2)}

Please complete this task following PMBOK {self.agent_type} phase best practices.
Provide your response in the following format:

DELIVERABLES:
[List key outputs]

RISKS IDENTIFIED:
[Any risks found]

ISSUES:
[Any issues encountered]

NEXT STEPS:
[Recommendations]

READY FOR NEXT PHASE: [Yes/No]
"""

        response = self.call_ollama(prompt, system_prompt)
        
        return {
            "agent": self.agent_type,
            "task": task,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_system_prompt(self) -> str:
        """Override in subclasses for agent-specific prompts"""
        return f"You are a {self.agent_type} agent in a project management system."


class InitiationAgent(OllamaPMAgent):
    """Agent responsible for project initiation phase"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        super().__init__("initiation", ollama_url)
    
    def get_system_prompt(self) -> str:
        return """You are an INITIATION AGENT in a project management system.

Your responsibilities include:
1. Conducting feasibility studies
2. Developing project charters
3. Identifying stakeholders and their requirements
4. Creating business cases
5. Defining high-level objectives, scope, and constraints

You follow PMI PMBOK Guide standards for the Initiation phase.

Key deliverables you produce:
- Project Charter (authorization document)
- Stakeholder Register (identified stakeholders)
- Feasibility Report (viability assessment)

Always structure your output clearly and professionally."""


class PlanningAgent(OllamaPMAgent):
    """Agent responsible for project planning phase"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        super().__init__("planning", ollama_url)
    
    def get_system_prompt(self) -> str:
        return """You are a PLANNING AGENT in a project management system.

Your responsibilities include:
1. Defining detailed scope and creating Work Breakdown Structure (WBS)
2. Developing project schedule with Gantt charts
3. Creating budget and cost baseline
4. Planning quality management, risk management, and resource allocation
5. Developing comprehensive Project Management Plan

You follow PMI PMBOK Guide standards for the Planning phase.

Key deliverables you produce:
- Project Management Plan (integrated plan)
- Scope Statement & WBS (detailed scope definition)
- Schedule (Gantt chart with dependencies)
- Budget/Cost Baseline (financial plan)
- Risk Register (identified risks and responses)
- RACI Matrix (responsibility assignment)

Always structure your output clearly and professionally."""


class ExecutionAgent(OllamaPMAgent):
    """Agent responsible for project execution phase"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        super().__init__("execution", ollama_url)
    
    def get_system_prompt(self) -> str:
        return """You are an EXECUTION AGENT in a project management system.

Your responsibilities include:
1. Executing project tasks as defined in the Project Management Plan
2. Managing team performance and coordination
3. Quality assurance and quality control
4. Managing procurements and vendor relationships
5. Producing project deliverables

You follow PMI PMBOK Guide standards for the Execution phase.

Key deliverables you produce:
- Project Deliverables (actual outputs)
- Work Performance Data (execution metrics)
- Quality Reports (QA/QC results)
- Issue Log (problems encountered)
- Team Performance Assessments

Always structure your output clearly and professionally."""


class MonitoringAgent(OllamaPMAgent):
    """Agent responsible for monitoring & control phase"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        super().__init__("monitoring", ollama_url)
    
    def get_system_prompt(self) -> str:
        return """You are a MONITORING & CONTROL AGENT in a project management system.

Your responsibilities include:
1. Tracking project progress against baselines
2. Monitoring risks and implementing risk responses
3. Controlling scope, cost, and schedule (change control)
4. Validating quality and managing issues
5. Generating performance reports and variance analysis

You follow PMI PMBOK Guide standards for the Monitoring & Control phase.

Key deliverables you produce:
- Performance Reports (status updates)
- Status Reports (current state)
- Updated Risk Register (risk status)
- Change Request Log (approved changes)
- Variance Reports (EVM analysis)

Always structure your output clearly and professionally."""


class ClosureAgent(OllamaPMAgent):
    """Agent responsible for project closure phase"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        super().__init__("closure", ollama_url)
    
    def get_system_prompt(self) -> str:
        return """You are a CLOSURE AGENT in a project management system.

Your responsibilities include:
1. Obtaining final stakeholder acceptance and sign-off
2. Releasing project resources and closing contracts
3. Documenting lessons learned and best practices
4. Creating final project report and closure documentation
5. Archiving project artifacts for organizational learning

You follow PMI PMBOK Guide standards for the Closure phase.

Key deliverables you produce:
- Final Project Report (comprehensive summary)
- Lessons Learned Document (knowledge capture)
- Project Closure Report (formal closure)
- Archived Documentation (historical records)
- Final Acceptance Sign-off (stakeholder approval)

Always structure your output clearly and professionally."""


class OllamaCoordinator:
    """
    Coordinator agent that manages all PM phase agents using Ollama
    Implements MCP and A2A communication patterns
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "gemma2:latest"
        
        # Initialize phase agents
        self.agents = {
            "initiation": InitiationAgent(ollama_url),
            "planning": PlanningAgent(ollama_url),
            "execution": ExecutionAgent(ollama_url),
            "monitoring": MonitoringAgent(ollama_url),
            "closure": ClosureAgent(ollama_url)
        }
        
        self.project_state = {
            "current_phase": "initiation",
            "phase_outputs": {},
            "go_decisions": {},
            "risks": [],
            "issues": [],
            "completed_phases": []
        }
    
    def delegate_task(self, phase: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate task to appropriate phase agent (A2A communication)
        
        Args:
            phase: Target phase agent
            task: Task description
            context: Project context
            
        Returns:
            Agent execution results
        """
        print(f"\n📤 COORDINATOR → {phase.upper()} AGENT")
        print(f"   Task: {task[:80]}...")
        
        agent = self.agents.get(phase)
        if not agent:
            return {"error": f"Unknown phase: {phase}"}
        
        # A2A communication via MCP-style delegation
        result = agent.execute_task(task, context)
        
        # Store results
        if phase not in self.project_state['phase_outputs']:
            self.project_state['phase_outputs'][phase] = []
        self.project_state['phase_outputs'][phase].append(result)
        
        print(f"✅ {phase.upper()} AGENT → COORDINATOR")
        print(f"   Response received: {len(result['response'])} characters")
        
        return result
    
    def phase_gate_review(self, phase: str) -> bool:
        """
        Conduct phase gate review using coordinator's judgment
        
        Args:
            phase: Phase to review
            
        Returns:
            True if GO, False if NO-GO
        """
        print(f"\n🔍 PHASE GATE REVIEW: {phase.upper()}")
        
        phase_outputs = self.project_state['phase_outputs'].get(phase, [])
        
        system_prompt = """You are a Project Manager Coordinator conducting a phase gate review.

Your role is to:
1. Review phase deliverables for completeness
2. Assess quality and adherence to standards
3. Evaluate risks and issues
4. Make GO/NO-GO decision for next phase

Provide a clear GO or NO-GO decision with brief rationale."""

        prompt = f"""Review the following {phase.upper()} phase outputs:

{json.dumps(phase_outputs, indent=2)}

Conduct a phase gate review and provide:
1. Your GO or NO-GO decision
2. Brief rationale (2-3 sentences)
3. Any conditions for proceeding

Decision:"""

        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{prompt}",
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            decision_text = response.json().get("response", "")
            
            self.project_state['go_decisions'][phase] = decision_text
            
            # Parse decision
            is_go = "GO" in decision_text.upper() and "NO-GO" not in decision_text.upper()
            
            if is_go:
                print(f"✅ Decision: GO")
                print(f"   Rationale: {decision_text[:150]}...")
            else:
                print(f"❌ Decision: NO-GO")
                print(f"   Rationale: {decision_text[:150]}...")
            
            return is_go
            
        except Exception as e:
            print(f"⚠️  Error in phase gate review: {str(e)}")
            return False
    
    def manage_project(self, project_description: str) -> Dict[str, Any]:
        """
        Manage complete project lifecycle through all phases
        
        Args:
            project_description: High-level project description
            
        Returns:
            Complete project results
        """
        print("\n" + "="*70)
        print(f"🚀 PROJECT MANAGEMENT MULTI-AGENT SYSTEM (Ollama Gemma3)")
        print("="*70)
        print(f"\nProject: {project_description}\n")
        
        phases = ["initiation", "planning", "execution", "monitoring", "closure"]
        
        for phase in phases:
            print("\n" + "="*70)
            print(f"📋 PHASE: {phase.upper()}")
            print("="*70)
            
            # Update current phase
            self.project_state['current_phase'] = phase
            
            # Create phase-specific task
            task = f"Complete all {phase} phase activities for the project: {project_description}"
            
            context = {
                "project_description": project_description,
                "current_phase": phase,
                "previous_outputs": self.project_state['phase_outputs']
            }
            
            # Delegate to phase agent (A2A communication)
            result = self.delegate_task(phase, task, context)
            
            # Display agent output
            print(f"\n📄 {phase.upper()} PHASE OUTPUT:")
            print("-" * 70)
            print(result['response'][:500])
            if len(result['response']) > 500:
                print(f"\n... (truncated, {len(result['response'])} characters total)")
            print("-" * 70)
            
            # Conduct phase gate review
            approved = self.phase_gate_review(phase)
            
            if not approved:
                print(f"\n❌ PROJECT HALTED AT {phase.upper()} PHASE")
                return {
                    "status": "halted",
                    "halted_at_phase": phase,
                    "reason": "Phase gate review failed - requires revision",
                    "project_state": self.project_state
                }
            
            # Mark phase as completed
            self.project_state['completed_phases'].append(phase)
        
        print("\n" + "="*70)
        print("🎉 PROJECT COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\nCompleted Phases: {', '.join(self.project_state['completed_phases'])}")
        print(f"Total Outputs Generated: {sum(len(outputs) for outputs in self.project_state['phase_outputs'].values())}")
        
        return {
            "status": "completed",
            "project_state": self.project_state
        }


# Main execution for assignment
if __name__ == "__main__":
    print("PM Multi-Agent System - Ollama Gemma3 Implementation")
    print("=" * 70)
    print("\nInitializing system...")
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        print("✅ Ollama is running")
    except:
        print("❌ Error: Ollama is not running")
        print("\nPlease start Ollama first:")
        print("  1. Install Ollama: https://ollama.ai/")
        print("  2. Run: ollama pull gemma2")
        print("  3. Run: ollama serve")
        exit(1)
    
    # Initialize coordinator
    coordinator = OllamaCoordinator()
    
    # Sample project for assignment
    project = """
    Develop an AI-powered project management assistant that helps teams 
    automate task scheduling, resource allocation, and risk monitoring using 
    machine learning algorithms.
    """
    
    # Execute project management
    result = coordinator.manage_project(project)
    
    # Save results to file
    with open('/home/claude/pm_project_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n📁 Results saved to: pm_project_results.json")
