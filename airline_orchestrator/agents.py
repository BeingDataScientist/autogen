"""
AutoGen Agents - Multi-agent system for telemetry analysis
"""

import os
import json
from typing import Dict, Any, Optional
from autogen import ConversableAgent
from rich.console import Console
from rich.panel import Panel

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
        self.agent = ConversableAgent(
            name=name,
            system_message=system_message,
            llm_config={
                "config_list": [{
                    "model": model,
                    "api_key": api_key,
                }],
                "temperature": 0.3,
            },
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )
    
    def log(self, message: str, style: str = "cyan"):
        """Log message with agent prefix"""
        self.console.print(f"[{self.name}] {message}", style=style)


class TelemetryAgent(AgentBase):
    """Agent that monitors telemetry and detects threshold-based anomalies"""
    
    def __init__(self, api_key: str, config=None):
        system_message = """You are a TelemetryAgent monitoring aircraft sensor data.
        Your role is to analyze telemetry readings and detect anomalies based on threshold violations.
        
        Thresholds:
        - RPM: Normal range 8500-9500 rpm
        - Pressure: Normal range 1800-2000 PSI (alert if < 1500 or > 2100)
        - Vibration: Normal range 0.1-0.8 mm/s (alert if > 1.0)
        - EGT: Normal range 700-800°C (alert if > 900)
        
        When you detect an anomaly, report it clearly with the parameter name and value.
        """
        model = config.get_model('monitoring') if config else "gpt-4o-mini"
        super().__init__("TelemetryAgent", system_message, api_key=api_key, model=model, config=config)
    
    def analyze(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze telemetry for threshold violations
        
        Args:
            telemetry: Telemetry dictionary
            
        Returns:
            Analysis result dictionary
        """
        anomalies = []
        
        # Check RPM
        if telemetry['rpm'] < 8500 or telemetry['rpm'] > 9500:
            anomalies.append(f"RPM out of range: {telemetry['rpm']:.0f} rpm")
        
        # Check Pressure
        if telemetry['pressure'] < 1500:
            anomalies.append(f"Pressure drop detected: {telemetry['pressure']:.0f} PSI")
        elif telemetry['pressure'] > 2100:
            anomalies.append(f"Pressure spike detected: {telemetry['pressure']:.0f} PSI")
        
        # Check Vibration
        if telemetry['vibration'] > 1.0:
            anomalies.append(f"High vibration detected: {telemetry['vibration']:.2f} mm/s")
        
        # Check EGT
        if telemetry['egt'] > 900:
            anomalies.append(f"EGT temperature jump: {telemetry['egt']:.0f}°C")
        
        result = {
            'anomalies_detected': len(anomalies) > 0,
            'anomaly_details': anomalies,
            'telemetry': telemetry
        }
        
        if anomalies:
            self.log(f"Threshold anomaly detected: {', '.join(anomalies)}", style="yellow")
        else:
            self.log("All parameters within normal thresholds", style="green")
        
        return result


class AnomalyAgent(AgentBase):
    """Agent that uses ML model to confirm anomalies"""
    
    def __init__(self, ml_model, api_key: str, config=None):
        """
        Initialize AnomalyAgent with ML model
        
        Args:
            ml_model: AnomalyDetector instance
            api_key: OpenAI API key
            config: ConfigLoader instance (optional)
        """
        system_message = """You are an AnomalyAgent that validates anomalies using machine learning.
        You receive telemetry data and threshold-based anomaly reports.
        Your role is to use the ML anomaly detection model to confirm or reject potential anomalies.
        
        When the ML model confirms an anomaly, escalate it to the diagnosis agent.
        If the ML model indicates normal operation, mark it as a false alarm.
        """
        model = config.get_model('monitoring') if config else "gpt-4o-mini"
        super().__init__("AnomalyAgent", system_message, api_key=api_key, model=model, config=config)
        self.ml_model = ml_model
    
    def validate(self, telemetry_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate anomaly using ML model
        
        Args:
            telemetry_analysis: Result from TelemetryAgent
            
        Returns:
            Validation result dictionary
        """
        telemetry = telemetry_analysis['telemetry']
        
        # Use ML model to detect anomaly
        is_anomaly, anomaly_score = self.ml_model.detect_anomaly(telemetry)
        
        result = {
            'ml_confirmed': is_anomaly,
            'ml_score': anomaly_score,
            'threshold_detected': telemetry_analysis['anomalies_detected'],
            'telemetry': telemetry
        }
        
        if is_anomaly:
            self.log(f"ML confirms anomaly (score={anomaly_score:.2f}) → Escalating", style="red")
        else:
            self.log(f"ML indicates normal operation (score={anomaly_score:.2f}) → False alarm", style="green")
        
        return result


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
        
        # Use agent to get diagnosis via initiate_chat
        from autogen import UserProxyAgent
        
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0
        )
        
        # Initiate chat and get response
        chat_result = user_proxy.initiate_chat(
            recipient=self.agent,
            message=prompt,
            max_turns=1,
            silent=True
        )
        
        # Parse response
        try:
            # Get the last message from the agent
            response_text = ""
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                for msg in reversed(chat_result.chat_history):
                    if isinstance(msg, dict):
                        if msg.get('name') == self.name or msg.get('role') == 'assistant':
                            response_text = msg.get('content', '')
                            break
                    elif hasattr(msg, 'content'):
                        response_text = msg.content
                        break
            
            # Extract JSON from response
            if '{' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                diagnosis_data = json.loads(json_str)
            else:
                diagnosis_data = {'root_cause': 'Unable to parse diagnosis', 'severity': 'medium', 'subsystem': 'Unknown'}
        except Exception as e:
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
        
        # Use agent to get resolution via initiate_chat
        from autogen import UserProxyAgent
        
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0
        )
        
        # Initiate chat and get response
        chat_result = user_proxy.initiate_chat(
            recipient=self.agent,
            message=prompt,
            max_turns=1,
            silent=True
        )
        
        # Parse response
        try:
            # Get the last message from the agent
            response_text = ""
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                for msg in reversed(chat_result.chat_history):
                    if isinstance(msg, dict):
                        if msg.get('name') == self.name or msg.get('role') == 'assistant':
                            response_text = msg.get('content', '')
                            break
                    elif hasattr(msg, 'content'):
                        response_text = msg.content
                        break
            
            if '{' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                resolution_data = json.loads(json_str)
            else:
                resolution_data = {
                    'recommendation': 'Unable to generate recommendation',
                    'priority': 'medium',
                    'estimated_time': 'Unknown'
                }
        except Exception as e:
            resolution_data = {
                'recommendation': f'Resolution error: {str(e)}',
                'priority': 'medium',
                'estimated_time': 'Unknown'
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

