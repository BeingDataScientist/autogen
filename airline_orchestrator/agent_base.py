"""
Base Agent Class - Common functionality for all agents
"""

from typing import Any, Optional
from autogen import ConversableAgent
from rich.console import Console

console = Console()


class AgentBase:
    """Base class for all agents with common functionality"""
    
    def __init__(self, name: str, system_message: str, api_key: str, model: str = "gpt-4o-mini", config=None):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            system_message: System message for the agent
            api_key: OpenAI API key
            model: OpenAI model to use
            config: ConfigLoader instance (optional)
        """
        self.name = name
        self.console = console
        
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        # Create AutoGen agent
        # Some models (like gpt-5.1-chat-latest) only support default temperature (1)
        # Check if model supports custom temperature
        models_without_temp = ["gpt-5.1-chat-latest", "gpt-5.1", "gpt-5.1-2025-11-13"]
        
        # Build config list with proper structure
        config_list_item = {
            "model": model,
            "api_key": api_key,
        }
        
        # Only add temperature if model supports it
        if model not in models_without_temp:
            config_list_item["temperature"] = 0.3
        
        llm_config = {
            "config_list": [config_list_item]
        }
        
        # Workaround for Pydantic v2 compatibility issue with AutoGen's LLMConfig
        # The issue occurs during JSON schema generation in LLMConfig.__init__
        # Try normal initialization first, fallback to manual config if it fails
        try:
            self.agent = ConversableAgent(
                name=name,
                system_message=system_message,
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=2,  # Allow agent to respond in conversations
            )
        except (TypeError, AttributeError) as e:
            error_str = str(e)
            if "JsonSchema" in error_str or "typing.Literal" in error_str or "GenerateJsonSchema" in error_str:
                # Pydantic v2 compatibility issue - create agent without config, then set it manually
                # This bypasses the problematic schema validation
                self.agent = ConversableAgent(
                    name=name,
                    system_message=system_message,
                    llm_config=None,
                    human_input_mode="NEVER",
                    max_consecutive_auto_reply=2,  # Allow agent to respond in conversations
                )
                # Manually set the config (bypasses Pydantic validation)
                # Set both _llm_config (internal) and llm_config (public) if they exist
                if hasattr(self.agent, '_llm_config'):
                    self.agent._llm_config = llm_config
                # Also set the public property
                try:
                    self.agent.llm_config = llm_config
                except Exception:
                    # If setting llm_config property fails, try to set it directly
                    if hasattr(self.agent, '__dict__'):
                        self.agent.__dict__['llm_config'] = llm_config
            else:
                raise
    
    def log(self, message: str, style: str = "cyan"):
        """Log message with agent prefix"""
        self.console.print(f"[{self.name}] {message}", style=style)

