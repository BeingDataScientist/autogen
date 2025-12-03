"""
Diagnosis Agent - Uses LLM to diagnose root causes
"""

import json
from typing import Dict, Any
from .agent_base import AgentBase


class DiagnosisAgent(AgentBase):
    """Agent that uses LLM to diagnose root causes"""
    
    def __init__(self, api_key: str, config=None):
        system_message = """You are a DiagnosisAgent specializing in aircraft system root cause analysis.
        You receive confirmed anomaly data and must identify:
        1. Root cause of the anomaly
        2. Severity level (low, medium, high, critical)
        3. Affected subsystem (engine, hydraulic, electrical, etc.)
        
        Provide clear, concise diagnosis based on the telemetry patterns.
        """
        model = config.get_model('diagnosis') if config else "gpt-4-turbo"
        super().__init__("DiagnosisAgent", system_message, api_key=api_key, model=model, config=config)
    
    def diagnose(self, anomaly_validation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose root cause of anomaly
        
        Args:
            anomaly_validation: Result from AnomalyAgent
            
        Returns:
            Diagnosis result dictionary
        """
        if not anomaly_validation['ml_confirmed']:
            return {
                'diagnosis': 'No diagnosis needed - false alarm',
                'severity': None,
                'subsystem': None
            }
        
        telemetry = anomaly_validation['telemetry']
        
        # Create prompt for LLM
        prompt = f"""Analyze this aircraft telemetry anomaly and provide diagnosis:

Telemetry Data:
- RPM: {telemetry['rpm']:.0f} rpm
- Pressure: {telemetry['pressure']:.0f} PSI
- Vibration: {telemetry['vibration']:.2f} mm/s
- EGT: {telemetry['egt']:.0f}°C
- ML Anomaly Score: {anomaly_validation['ml_score']:.2f}

Provide a JSON response with:
1. root_cause: Brief description of the likely root cause
2. severity: One of [low, medium, high, critical]
3. subsystem: Affected subsystem (e.g., "Engine", "Hydraulic System", "Electrical")

Respond ONLY with valid JSON, no additional text.
"""
        
        # Initialize diagnosis_data with default values
        diagnosis_data = {
            'root_cause': 'Unable to parse diagnosis',
            'severity': 'medium',
            'subsystem': 'Unknown'
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
                    diagnosis_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    self.log(f"JSON parse error: {str(e)}", style="yellow")
                    diagnosis_data = {
                        'root_cause': 'Unable to parse diagnosis - invalid JSON',
                        'severity': 'medium',
                        'subsystem': 'Unknown'
                    }
            elif not response_text:
                self.log("No response received from agent", style="yellow")
                
        except Exception as e:
            self.log(f"Error generating diagnosis: {str(e)}", style="red")
            diagnosis_data = {
                'root_cause': f'Diagnosis error: {str(e)}',
                'severity': 'medium',
                'subsystem': 'Unknown'
            }
        
        result = {
            'root_cause': diagnosis_data.get('root_cause', 'Unknown'),
            'severity': diagnosis_data.get('severity', 'medium'),
            'subsystem': diagnosis_data.get('subsystem', 'Unknown'),
            'telemetry': telemetry
        }
        
        self.log(f"Root cause: {result['root_cause']}", style="magenta")
        self.log(f"Severity: {result['severity']} | Subsystem: {result['subsystem']}", style="magenta")
        
        return result

