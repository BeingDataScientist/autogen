"""
Orchestrator Agent - Orchestrates the pipeline and maintains shared memory
"""

from typing import Dict, Any, Optional
from .agent_base import AgentBase


class OrchestratorAgent(AgentBase):
    """Agent that orchestrates the pipeline and maintains shared memory"""
    
    def __init__(self, api_key: str, config=None):
        system_message = """You are an OrchestratorAgent managing the multi-agent pipeline.
        You coordinate data flow between agents and maintain shared memory.
        Your role is to route telemetry through the analysis pipeline efficiently.
        """
        model = config.get_model('monitoring') if config else "gpt-4o-mini"
        super().__init__("OrchestratorAgent", system_message, api_key=api_key, model=model, config=config)
        self.shared_memory: Dict[str, Any] = {}
    
    def update_memory(self, key: str, value: Any):
        """Update shared memory"""
        self.shared_memory[key] = value
    
    def get_memory(self, key: str) -> Optional[Any]:
        """Get value from shared memory"""
        return self.shared_memory.get(key)
    
    def clear_memory(self):
        """Clear shared memory"""
        self.shared_memory.clear()

