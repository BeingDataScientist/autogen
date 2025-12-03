"""
Resolution Agent - Generates maintenance recommendations
"""

import json
from typing import Dict, Any
from .agent_base import AgentBase


class ResolutionAgent(AgentBase):
    """Agent that generates maintenance recommendations"""
    
    def __init__(self, api_key: str, config=None):
        system_message = """You are a ResolutionAgent that creates maintenance action plans.
        You receive diagnosis information and must generate:
        1. Step-by-step maintenance recommendations
        2. Priority level
        3. Estimated time to resolution
        4. Required resources/tools
        
        Always respond in valid JSON format with clear action items.
        """
        model = config.get_model('resolution') if config else "gpt-4-turbo"
        super().__init__("ResolutionAgent", system_message, api_key=api_key, model=model, config=config)
    
    def generate_resolution(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate maintenance recommendations
        
        Args:
            diagnosis: Result from DiagnosisAgent
            
        Returns:
            Resolution result dictionary
        """
        if diagnosis.get('severity') is None:
            return {
                'recommendation': 'No action required - false alarm',
                'priority': None,
                'estimated_time': None
            }
        
        # Create prompt for LLM with JSON mode requirement
        prompt = f"""Based on this diagnosis, provide maintenance recommendations:

Diagnosis:
- Root Cause: {diagnosis['root_cause']}
- Severity: {diagnosis['severity']}
- Subsystem: {diagnosis['subsystem']}

Provide a JSON response with:
1. recommendation: Detailed step-by-step maintenance actions
2. priority: One of [low, medium, high, urgent]
3. estimated_time: Estimated time to complete (e.g., "2 hours", "next maintenance window")
4. required_resources: List of required tools/parts/personnel

Respond ONLY with valid JSON, no additional text.
"""
        
        # Initialize resolution_data with default values
        resolution_data = {
            'recommendation': 'Unable to generate recommendation',
            'priority': 'medium',
            'estimated_time': 'Unknown',
            'required_resources': []
        }
        
        # Use OpenAI client directly to avoid AutoGen turn management issues
        response_text = ""
        try:
            from openai import OpenAI
            
            # Get API key from agent's config
            api_key = None
            if hasattr(self.agent, 'llm_config') and self.agent.llm_config:
                if isinstance(self.agent.llm_config, dict):
                    config_list = self.agent.llm_config.get('config_list', [])
                    if config_list and len(config_list) > 0:
                        api_key = config_list[0].get('api_key')
                elif hasattr(self.agent.llm_config, 'config_list'):
                    config_list = self.agent.llm_config.config_list
                    if config_list and len(config_list) > 0:
                        api_key = config_list[0].get('api_key')
            
            if not api_key:
                raise ValueError("Could not extract API key from agent config")
            
            # Get model from agent's config
            model = "gpt-4-turbo"  # Default
            if hasattr(self.agent, 'llm_config') and self.agent.llm_config:
                if isinstance(self.agent.llm_config, dict):
                    config_list = self.agent.llm_config.get('config_list', [])
                    if config_list and len(config_list) > 0:
                        model = config_list[0].get('model', model)
                elif hasattr(self.agent.llm_config, 'config_list'):
                    config_list = self.agent.llm_config.config_list
                    if config_list and len(config_list) > 0:
                        model = config_list[0].get('model', model)
            
            # Create OpenAI client and make direct API call
            client = OpenAI(api_key=api_key)
            
            # Get system message from agent
            system_message = self.agent.system_message if hasattr(self.agent, 'system_message') else ""
            
            # Prepare API call parameters
            # GPT-5.1 models require max_completion_tokens instead of max_tokens
            # and only support default temperature (1), not custom values
            models_without_temp = ["gpt-5.1-chat-latest", "gpt-5.1", "gpt-5.1-2025-11-13"]
            is_gpt5_model = any(m in model.lower() for m in ["gpt-5.1", "gpt-5"])
            
            api_params = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Only add temperature if model supports custom values
            # GPT-5.1 models only support default temperature (1), so omit it
            if not is_gpt5_model:
                api_params["temperature"] = 0.3
            
            # Use max_completion_tokens for gpt-5.1 models, max_tokens for others
            if is_gpt5_model:
                api_params["max_completion_tokens"] = 500
            else:
                api_params["max_tokens"] = 500
            
            # Make API call
            response = client.chat.completions.create(**api_params)
            
            if response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content
            
            # Parse JSON from response
            if response_text and '{' in response_text:
                try:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_str = response_text[json_start:json_end]
                    resolution_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    self.log(f"JSON parse error: {str(e)}", style="yellow")
                    resolution_data = {
                        'recommendation': 'Unable to generate recommendation - invalid JSON',
                        'priority': 'medium',
                        'estimated_time': 'Unknown',
                        'required_resources': []
                    }
            elif not response_text:
                self.log("No response received from agent", style="yellow")
                
        except Exception as e:
            self.log(f"Error generating resolution: {str(e)}", style="red")
            resolution_data = {
                'recommendation': f'Resolution error: {str(e)}',
                'priority': 'medium',
                'estimated_time': 'Unknown',
                'required_resources': []
            }
        
        result = {
            'recommendation': resolution_data.get('recommendation', 'No recommendation available'),
            'priority': resolution_data.get('priority', 'medium'),
            'estimated_time': resolution_data.get('estimated_time', 'Unknown'),
            'required_resources': resolution_data.get('required_resources', [])
        }
        
        self.log(f"Recommended Action: {result['recommendation'][:100]}...", style="blue")
        self.log(f"Priority: {result['priority']} | Time: {result['estimated_time']}", style="blue")
        
        return result

