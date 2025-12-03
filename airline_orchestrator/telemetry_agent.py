"""
Telemetry Agent - Monitors telemetry and detects threshold-based anomalies
"""

from typing import Dict, Any
from .agent_base import AgentBase


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

