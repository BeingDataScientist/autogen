"""
Anomaly Agent - Uses ML model to confirm anomalies
"""

from typing import Dict, Any
from .agent_base import AgentBase


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

