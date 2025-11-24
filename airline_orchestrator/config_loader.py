"""
Config Loader - Reads configuration from config.json file
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel

console = Console()


class ConfigLoader:
    """Loads and manages configuration from config.json"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize config loader
        
        Args:
            config_path: Path to config.json file (if None, searches for config.json in project root)
        """
        if config_path is None:
            # Try to find config.json in project root
            # Look for it in current directory, then parent directories
            current = Path.cwd()
            config_path = current / "config.json"
            
            # If not found, try parent directory (in case running from airline_orchestrator/)
            if not config_path.exists():
                parent_config = current.parent / "config.json"
                if parent_config.exists():
                    config_path = parent_config
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from config.json file"""
        if not self.config_path.exists():
            console.print(
                Panel.fit(
                    f"[red]ERROR: Config file not found: {self.config_path}[/red]\n\n"
                    f"Please create a config.json file in the project root.\n"
                    f"You can copy config.json.example and update it with your settings:\n"
                    f"  cp config.json.example config.json\n\n"
                    f"Then edit config.json and add your OpenAI API key.",
                    title="Config File Missing",
                    border_style="red"
                )
            )
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            console.print(
                Panel.fit(
                    f"[red]ERROR: Invalid JSON in config file[/red]\n\n"
                    f"Error: {str(e)}\n\n"
                    f"Please check your config.json file syntax.",
                    title="Config Error",
                    border_style="red"
                )
            )
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'openai_api_key' or 'models.diagnosis')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_openai_api_key(self) -> str:
        """Get OpenAI API key from config"""
        api_key = self.get('openai_api_key')
        
        if not api_key or api_key == "your-openai-api-key-here":
            console.print(
                Panel.fit(
                    "[red]ERROR: OpenAI API key not configured[/red]\n\n"
                    "Please edit config.json and set your 'openai_api_key' value.\n"
                    "Replace 'your-openai-api-key-here' with your actual API key.",
                    title="API Key Required",
                    border_style="red"
                )
            )
            raise ValueError("OpenAI API key not configured in config.json")
        
        return api_key
    
    def get_model(self, agent_type: str) -> str:
        """Get model name for specific agent type"""
        model = self.get(f'models.{agent_type}')
        if not model:
            # Default models
            defaults = {
                'diagnosis': 'gpt-4-turbo',
                'resolution': 'gpt-4-turbo',
                'monitoring': 'gpt-4o-mini'
            }
            return defaults.get(agent_type, 'gpt-4o-mini')
        return model
    
    def get_orchestrator_config(self) -> Dict[str, Any]:
        """Get orchestrator configuration"""
        return {
            'num_cycles': self.get('orchestrator.num_cycles', 8),
            'anomaly_probability': self.get('orchestrator.anomaly_probability', 0.15)
        }
    
    def get_ml_config(self) -> Dict[str, Any]:
        """Get ML model configuration"""
        return {
            'n_samples': self.get('ml_model.n_samples', 1000),
            'contamination': self.get('ml_model.contamination', 0.1)
        }


# Global config instance
_config_instance: ConfigLoader = None


def get_config(config_path: str = "config.json") -> ConfigLoader:
    """
    Get global config instance (singleton pattern)
    
    Args:
        config_path: Path to config.json file
        
    Returns:
        ConfigLoader instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance

