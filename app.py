"""
Main Entry Point - Initializes environment and starts orchestrator
Merged from run.py and airline_orchestrator/main.py
"""

import os
import sys
from pathlib import Path

# Apply typing patch for Python 3.9.0 compatibility (not needed for Python 3.12.3+)
try:
    import airline_orchestrator.typing_patch
except ImportError:
    pass

from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from airline_orchestrator.config_loader import get_config
from airline_orchestrator.orchestrator import PipelineOrchestrator

console = Console()


def check_virtual_environment():
    """Check if running in virtual environment"""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if not in_venv:
        console.print(
            Panel.fit(
                "[yellow]Warning: Not running in virtual environment[/yellow]\n"
                "It's recommended to activate the virtual environment first:\n"
                "  Windows: venv\\Scripts\\activate\n"
                "  Linux/macOS: source venv/bin/activate",
                title="Virtual Environment",
                border_style="yellow"
            )
        )
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    else:
        console.print("[green][OK] Running in virtual environment[/green]")


def load_config():
    """Load configuration from config.json"""
    try:
        config = get_config()
        api_key = config.get_openai_api_key()
        console.print("[green][OK] Configuration loaded successfully[/green]")
        return config, api_key
    except Exception as e:
        console.print(f"[red]Failed to load configuration: {str(e)}[/red]")
        sys.exit(1)


def main():
    """Main entry point"""
    console.print("\n")
    console.print(Panel.fit(
        "Airline Multi-Agent Orchestration System",
        style="bold cyan"
    ))
    console.print("AutoGen + MCP Pattern Demonstration\n")
    
    # Check environment
    console.print("[yellow]Checking environment...[/yellow]")
    check_virtual_environment()
    config, api_key = load_config()
    console.print("")
    
    # Get orchestrator config
    orchestrator_config = config.get_orchestrator_config()
    
    # Initialize orchestrator
    try:
        console.print("[yellow]Initializing orchestrator...[/yellow]\n")
        orchestrator = PipelineOrchestrator(
            num_cycles=orchestrator_config['num_cycles'],
            anomaly_probability=orchestrator_config['anomaly_probability'],
            config=config
        )
        
        # Run orchestrator
        orchestrator.run()
        
        console.print(Panel.fit(
            "[green][OK] Execution completed successfully[/green]",
            style="bold green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Execution interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

