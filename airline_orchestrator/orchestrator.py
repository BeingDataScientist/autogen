"""
Orchestrator - MCP-style pipeline orchestration with shared memory
"""

import time
from typing import Dict, Any, Iterator
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout

from .telemetry_simulator import TelemetrySimulator
from .ml_model import AnomalyDetector
from .telemetry_agent import TelemetryAgent
from .anomaly_agent import AnomalyAgent
from .diagnosis_agent import DiagnosisAgent
from .resolution_agent import ResolutionAgent
from .orchestrator_agent import OrchestratorAgent

console = Console()


class PipelineOrchestrator:
    """Orchestrates the multi-agent pipeline with MCP-style shared memory"""
    
    def __init__(self, num_cycles: int = 8, anomaly_probability: float = 0.15, config=None):
        """
        Initialize orchestrator
        
        Args:
            num_cycles: Number of telemetry cycles to process
            anomaly_probability: Probability of injecting anomalies
            config: ConfigLoader instance
        """
        self.num_cycles = num_cycles
        self.shared_memory: Dict[str, Any] = {}
        self.config = config
        
        # Initialize components
        console.print(Panel.fit("Initializing Multi-Agent System", style="bold cyan"))
        
        # Get ML config
        if config:
            ml_config = config.get_ml_config()
            n_samples = ml_config['n_samples']
            contamination = ml_config['contamination']
        else:
            n_samples = 1000
            contamination = 0.1
        
        # Initialize ML model
        console.print("[yellow]Training ML anomaly detector...[/yellow]")
        self.ml_model = AnomalyDetector()
        self.ml_model.train(n_samples=n_samples, contamination=contamination)
        console.print("[green][OK] ML model trained[/green]\n")
        
        # Get API key from config
        if config:
            api_key = config.get_openai_api_key()
        else:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found in config or environment")
        
        # Initialize agents
        console.print("[yellow]Initializing agents...[/yellow]")
        self.telemetry_agent = TelemetryAgent(api_key=api_key, config=config)
        self.anomaly_agent = AnomalyAgent(self.ml_model, api_key=api_key, config=config)
        self.diagnosis_agent = DiagnosisAgent(api_key=api_key, config=config)
        self.resolution_agent = ResolutionAgent(api_key=api_key, config=config)
        self.orchestrator_agent = OrchestratorAgent(api_key=api_key, config=config)
        console.print("[green][OK] All agents initialized[/green]\n")
        
        # Initialize telemetry simulator
        self.telemetry_simulator = TelemetrySimulator(anomaly_probability=anomaly_probability)
        
        # Pipeline history
        self.pipeline_history = []
    
    def _update_shared_memory(self, stage: str, data: Any):
        """Update shared memory (MCP-style)"""
        self.shared_memory[stage] = data
        self.orchestrator_agent.update_memory(stage, data)
    
    def _run_pipeline(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Run the complete pipeline for a single telemetry reading
        
        Args:
            telemetry: Telemetry dictionary
            
        Returns:
            Complete pipeline result
        """
        console.print(Panel.fit(
            f"Pipeline Cycle #{telemetry['cycle']}",
            style="bold blue"
        ))
        
        # Stage 1: Telemetry Agent
        console.print("\n[bold cyan]Stage 1: Telemetry Analysis[/bold cyan]")
        telemetry_result = self.telemetry_agent.analyze(telemetry)
        self._update_shared_memory('telemetry_analysis', telemetry_result)
        
        # Stage 2: Anomaly Agent (ML-based)
        console.print("\n[bold cyan]Stage 2: ML Anomaly Validation[/bold cyan]")
        anomaly_result = self.anomaly_agent.validate(telemetry_result)
        self._update_shared_memory('anomaly_validation', anomaly_result)
        
        # Stage 3: Diagnosis Agent (LLM-based)
        diagnosis_result = None
        resolution_result = None
        
        if anomaly_result['ml_confirmed']:
            console.print("\n[bold cyan]Stage 3: Root Cause Diagnosis[/bold cyan]")
            diagnosis_result = self.diagnosis_agent.diagnose(anomaly_result)
            self._update_shared_memory('diagnosis', diagnosis_result)
            
            # Stage 4: Resolution Agent (LLM-based)
            console.print("\n[bold cyan]Stage 4: Maintenance Resolution[/bold cyan]")
            resolution_result = self.resolution_agent.generate_resolution(diagnosis_result)
            self._update_shared_memory('resolution', resolution_result)
        else:
            console.print("\n[yellow]Skipping diagnosis/resolution (false alarm)[/yellow]")
            diagnosis_result = {'diagnosis': 'False alarm - no action needed'}
            resolution_result = {'recommendation': 'No action required'}
        
        # Compile complete result
        pipeline_result = {
            'cycle': telemetry['cycle'],
            'telemetry': telemetry,
            'telemetry_analysis': telemetry_result,
            'anomaly_validation': anomaly_result,
            'diagnosis': diagnosis_result,
            'resolution': resolution_result,
            'shared_memory_snapshot': self.shared_memory.copy()
        }
        
        self.pipeline_history.append(pipeline_result)
        
        # Print summary
        self._print_pipeline_summary(pipeline_result)
        
        return pipeline_result
    
    def _print_pipeline_summary(self, result: Dict[str, Any]):
        """Print pipeline summary to CLI"""
        console.print("\n" + "="*70)
        console.print("[bold]Pipeline Summary[/bold]")
        console.print("="*70)
        
        telemetry = result['telemetry']
        console.print(f"\n[cyan]Telemetry:[/cyan] RPM={telemetry['rpm']:.0f} | "
                     f"Pressure={telemetry['pressure']:.0f} | "
                     f"Vibration={telemetry['vibration']:.2f} | "
                     f"EGT={telemetry['egt']:.0f}")
        
        if result['anomaly_validation']['ml_confirmed']:
            console.print(f"\n[red][!] ANOMALY CONFIRMED[/red]")
            console.print(f"[yellow]ML Score: {result['anomaly_validation']['ml_score']:.2f}[/yellow]")
            
            if result.get('diagnosis'):
                diag = result['diagnosis']
                console.print(f"\n[magenta]Root Cause:[/magenta] {diag.get('root_cause', 'Unknown')}")
                console.print(f"[magenta]Severity:[/magenta] {diag.get('severity', 'Unknown')} | "
                            f"[magenta]Subsystem:[/magenta] {diag.get('subsystem', 'Unknown')}")
            
            if result.get('resolution'):
                res = result['resolution']
                console.print(f"\n[blue]Recommended Action:[/blue] {res.get('recommendation', 'N/A')}")
                console.print(f"[blue]Priority:[/blue] {res.get('priority', 'N/A')} | "
                            f"[blue]Time:[/blue] {res.get('estimated_time', 'N/A')}")
        else:
            console.print("\n[green][OK] No anomalies detected - System normal[/green]")
        
        console.print("="*70 + "\n")
    
    def run(self):
        """Run the orchestrator for specified number of cycles"""
        console.print(Panel.fit(
            f"Starting Orchestrator - {self.num_cycles} cycles",
            style="bold green"
        ))
        
        # Get telemetry generator
        telemetry_gen = self.telemetry_simulator.generate_telemetry()
        
        # Process cycles
        for cycle in range(1, self.num_cycles + 1):
            # Get next telemetry reading
            telemetry = next(telemetry_gen)
            
            # Display telemetry
            self.telemetry_simulator.print_telemetry(telemetry)
            
            # Run pipeline
            result = self._run_pipeline(telemetry)
            
            # Wait between cycles (simulate real-time)
            if cycle < self.num_cycles:
                time.sleep(1)
        
        # Print final summary
        self._print_final_summary()
    
    def _print_final_summary(self):
        """Print final summary of all cycles"""
        console.print("\n" + "="*70)
        console.print(Panel.fit("Final Pipeline Summary", style="bold green"))
        console.print("="*70)
        
        total_anomalies = sum(1 for r in self.pipeline_history 
                            if r['anomaly_validation']['ml_confirmed'])
        
        console.print(f"\n[cyan]Total Cycles Processed:[/cyan] {len(self.pipeline_history)}")
        console.print(f"[cyan]Anomalies Detected:[/cyan] {total_anomalies}")
        console.print(f"[cyan]False Alarms:[/cyan] {len(self.pipeline_history) - total_anomalies}")
        
        if total_anomalies > 0:
            console.print("\n[bold yellow]Anomaly Breakdown:[/bold yellow]")
            for result in self.pipeline_history:
                if result['anomaly_validation']['ml_confirmed']:
                    diag = result.get('diagnosis', {})
                    console.print(f"  Cycle {result['cycle']}: {diag.get('root_cause', 'Unknown')} "
                                f"({diag.get('severity', 'Unknown')})")
        
        console.print("\n[green][OK] Pipeline execution complete[/green]")
        console.print("="*70 + "\n")
    
    def get_shared_memory(self) -> Dict[str, Any]:
        """Get current shared memory state"""
        return self.shared_memory.copy()
    
    def get_pipeline_history(self) -> list:
        """Get complete pipeline history"""
        return self.pipeline_history.copy()

