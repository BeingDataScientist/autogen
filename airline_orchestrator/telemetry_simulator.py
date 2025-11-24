"""
Telemetry Simulator - Generates continuous aircraft telemetry with anomaly injection
"""

import time
import random
from typing import Dict, Iterator
from rich.console import Console
from rich.table import Table

console = Console()


class TelemetrySimulator:
    """Simulates aircraft telemetry data with anomaly injection"""
    
    def __init__(self, anomaly_probability: float = 0.15):
        """
        Initialize telemetry simulator
        
        Args:
            anomaly_probability: Probability of injecting an anomaly (0.0 to 1.0)
        """
        self.anomaly_probability = anomaly_probability
        self.cycle_count = 0
        
        # Normal operating ranges
        self.normal_ranges = {
            'rpm': (8500, 9500),
            'pressure': (1800, 2000),  # PSI
            'vibration': (0.1, 0.8),   # mm/s
            'egt': (700, 800)           # Celsius
        }
        
    def _generate_normal_telemetry(self) -> Dict[str, float]:
        """Generate normal telemetry within expected ranges"""
        return {
            'rpm': random.uniform(*self.normal_ranges['rpm']),
            'pressure': random.uniform(*self.normal_ranges['pressure']),
            'vibration': random.uniform(*self.normal_ranges['vibration']),
            'egt': random.uniform(*self.normal_ranges['egt'])
        }
    
    def _inject_anomaly(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """Inject a random anomaly into telemetry"""
        anomaly_type = random.choice(['pressure_drop', 'vibration_spike', 'egt_jump'])
        
        if anomaly_type == 'pressure_drop':
            # Pressure drops to 40-60% of normal
            telemetry['pressure'] = random.uniform(700, 1200)
            telemetry['anomaly_type'] = 'pressure_drop'
            telemetry['anomaly_severity'] = 'high'
            
        elif anomaly_type == 'vibration_spike':
            # Vibration spikes to 2-4x normal
            telemetry['vibration'] = random.uniform(1.5, 3.5)
            telemetry['anomaly_type'] = 'vibration_spike'
            telemetry['anomaly_severity'] = 'high'
            
        elif anomaly_type == 'egt_jump':
            # EGT jumps to 1.3-1.6x normal
            telemetry['egt'] = random.uniform(950, 1200)
            telemetry['anomaly_type'] = 'egt_jump'
            telemetry['anomaly_severity'] = 'critical'
        
        return telemetry
    
    def generate_telemetry(self) -> Iterator[Dict[str, float]]:
        """
        Generate continuous telemetry data
        
        Yields:
            Dictionary containing telemetry readings
        """
        while True:
            self.cycle_count += 1
            
            # Generate base telemetry
            telemetry = self._generate_normal_telemetry()
            
            # Inject anomaly based on probability
            if random.random() < self.anomaly_probability:
                telemetry = self._inject_anomaly(telemetry)
            else:
                telemetry['anomaly_type'] = None
                telemetry['anomaly_severity'] = None
            
            # Add metadata
            telemetry['timestamp'] = time.time()
            telemetry['cycle'] = self.cycle_count
            
            yield telemetry
    
    def print_telemetry(self, telemetry: Dict[str, float]):
        """Print telemetry to CLI with Rich formatting"""
        table = Table(title="Aircraft Telemetry", show_header=True, header_style="bold magenta")
        table.add_column("Parameter", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Unit", style="yellow")
        
        table.add_row("RPM", f"{telemetry['rpm']:.0f}", "rpm")
        table.add_row("Pressure", f"{telemetry['pressure']:.0f}", "PSI")
        table.add_row("Vibration", f"{telemetry['vibration']:.2f}", "mm/s")
        table.add_row("EGT", f"{telemetry['egt']:.0f}", "°C")
        
        if telemetry.get('anomaly_type'):
            table.add_row("[!] Anomaly", telemetry['anomaly_type'], telemetry['anomaly_severity'])
        
        console.print("\n" + "="*60)
        console.print(table)
        console.print("="*60 + "\n")

