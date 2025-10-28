"""
Project Manager Coordinator Agent
Main orchestrator for the PM-MAS system using Anthropic Claude
"""

import anthropic
import os
from typing import Dict, List, Any
import json

class PMCoordinatorAgent:
    """
    Primary coordinator agent that manages all PM phase agents
    Implements hierarchical multi-agent coordination
    """
    
    def __init__(self, api_key: str = None):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model = "claude-sonnet-4-5-20250929"
        self.conversation_history = []
        self.phase_agents = {
            "initiation": None,
            "planning": None,
            "execution": None,
            "monitoring": None,
            "closure": None
        }
        self.project_state = {
            "current_phase": "initiation",
            "phase_outputs": {},
            "go_decisions": {},
            "risks": [],
            "issues": []
        }
        
    def system_prompt(self) -> str:
        """Define the coordinator agent's role and capabilities"""
        return """You are a Project Manager Coordinator AI Agent responsible for:
        
1. Orchestrating five specialized PM phase agents (Initiation, Planning, Execution, Monitoring, Closure)
2. Making phase gate decisions (go/no-go)
3. Managing agent-to-agent (A2A) communication via Model Context Protocol (MCP)
4. Escalating issues and resolving conflicts between agents
5. Ensuring project deliverables meet quality standards
6. Maintaining project state and documentation

You follow PMI PMBOK standards and best practices. You coordinate agents hierarchically,
delegating tasks to appropriate phase agents and synthesizing their outputs into
actionable project management decisions.

When analyzing project requests:
- Break down complex tasks into phase-specific subtasks
- Assign tasks to appropriate phase agents
- Review agent outputs for quality and completeness
- Make informed go/no-go decisions at phase gates
- Track risks, issues, and dependencies
"""

    def delegate_to_agent(self, agent_type: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate task to specific phase agent using A2A communication
        
        Args:
            agent_type: One of [initiation, planning, execution, monitoring, closure]
            task: Specific task description
            context: Project context and previous outputs
            
        Returns:
            Agent response with task results
        """
        agent_prompt = f"""You are a specialized {agent_type.upper()} Agent in a project management system.

Task: {task}

Project Context:
{json.dumps(context, indent=2)}

Previous Phase Outputs:
{json.dumps(self.project_state.get('phase_outputs', {}), indent=2)}

Please complete this task following PMBOK {agent_type} phase best practices.
Provide your response in JSON format with:
- deliverables: list of outputs produced
- risks_identified: any risks found
- issues: any issues encountered
- next_steps: recommendations for next actions
- ready_for_next_phase: boolean indicating readiness
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=self.get_agent_system_prompt(agent_type),
            messages=[{
                "role": "user",
                "content": agent_prompt
            }]
        )
        
        # Parse agent response
        agent_output = response.content[0].text
        
        # Store in phase outputs
        if agent_type not in self.project_state['phase_outputs']:
            self.project_state['phase_outputs'][agent_type] = []
        self.project_state['phase_outputs'][agent_type].append({
            "task": task,
            "output": agent_output
        })
        
        return {
            "agent": agent_type,
            "task": task,
            "response": agent_output,
            "timestamp": self._get_timestamp()
        }
    
    def get_agent_system_prompt(self, agent_type: str) -> str:
        """Get specialized system prompt for each agent type"""
        prompts = {
            "initiation": """You are an INITIATION Agent specializing in:
- Conducting feasibility studies
- Developing project charters
- Identifying stakeholders
- Creating business cases
- Defining high-level objectives and constraints

Follow PMBOK Initiation phase best practices.""",
            
            "planning": """You are a PLANNING Agent specializing in:
- Defining detailed scope and creating WBS
- Developing schedules (Gantt charts)
- Creating budgets and cost baselines
- Planning quality, risk management, and resources
- Developing comprehensive project management plans

Follow PMBOK Planning phase best practices.""",
            
            "execution": """You are an EXECUTION Agent specializing in:
- Executing project tasks as defined in plans
- Managing team performance
- Quality assurance and procurement
- Producing deliverables
- Coordinating work across teams

Follow PMBOK Execution phase best practices.""",
            
            "monitoring": """You are a MONITORING & CONTROL Agent specializing in:
- Tracking progress and monitoring risks
- Controlling scope, cost, and schedule
- Validating quality and managing issues
- Generating performance and variance reports
- Implementing change control processes

Follow PMBOK Monitoring & Control phase best practices.""",
            
            "closure": """You are a CLOSURE Agent specializing in:
- Obtaining final stakeholder acceptance
- Releasing resources and closing contracts
- Documenting lessons learned
- Creating project closure reports
- Archiving project documentation

Follow PMBOK Closure phase best practices."""
        }
        return prompts.get(agent_type, "You are a project management agent.")
    
    def phase_gate_review(self, phase: str) -> bool:
        """
        Conduct phase gate review to determine if project can proceed
        
        Returns:
            True if approved to proceed, False otherwise
        """
        phase_output = self.project_state['phase_outputs'].get(phase, [])
        
        gate_prompt = f"""As Project Manager Coordinator, review the {phase.upper()} phase outputs:

{json.dumps(phase_output, indent=2)}

Conduct a phase gate review considering:
1. Are all required deliverables complete?
2. Are quality standards met?
3. Are risks acceptable?
4. Is the project ready for the next phase?

Provide a GO/NO-GO decision with rationale."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=self.system_prompt(),
            messages=[{
                "role": "user",
                "content": gate_prompt
            }]
        )
        
        decision = response.content[0].text
        self.project_state['go_decisions'][phase] = decision
        
        # Simple parsing - in production use structured output
        return "GO" in decision and "NO-GO" not in decision
    
    def manage_project(self, project_description: str) -> Dict[str, Any]:
        """
        Main method to manage entire project lifecycle
        
        Args:
            project_description: High-level project description
            
        Returns:
            Complete project execution results
        """
        print(f"🚀 Starting Project: {project_description}\n")
        
        phases = ["initiation", "planning", "execution", "monitoring", "closure"]
        
        for phase in phases:
            print(f"\n{'='*60}")
            print(f"📋 PHASE: {phase.upper()}")
            print(f"{'='*60}\n")
            
            # Create phase-specific task
            task = f"Complete {phase} phase activities for: {project_description}"
            context = {
                "project_description": project_description,
                "current_phase": phase
            }
            
            # Delegate to phase agent
            result = self.delegate_to_agent(phase, task, context)
            print(f"✅ {phase.upper()} Agent completed task")
            print(f"Output: {result['response'][:200]}...\n")
            
            # Conduct phase gate review
            print(f"🔍 Conducting {phase.upper()} Phase Gate Review...")
            approved = self.phase_gate_review(phase)
            
            if approved:
                print(f"✅ GO Decision - Proceeding to next phase\n")
            else:
                print(f"❌ NO-GO Decision - Project requires revision\n")
                return {
                    "status": "halted",
                    "phase": phase,
                    "reason": "Phase gate review failed",
                    "outputs": self.project_state
                }
        
        print(f"\n{'='*60}")
        print("🎉 PROJECT COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        
        return {
            "status": "completed",
            "outputs": self.project_state
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Example usage
if __name__ == "__main__":
    # Initialize coordinator agent
    coordinator = PMCoordinatorAgent()
    
    # Define a sample project
    project = "Develop an AI-powered customer service chatbot for e-commerce platform"
    
    # Manage the project through all phases
    result = coordinator.manage_project(project)
    
    # Print final results
    print("\n" + "="*60)
    print("FINAL PROJECT STATE")
    print("="*60)
    print(json.dumps(result, indent=2))
