"""
Test OpenAI API Key - Simple script to verify API key is working
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

# Add typing patch for Python 3.9.0 compatibility
try:
    import airline_orchestrator.typing_patch
except ImportError:
    pass

from airline_orchestrator.config_loader import get_config

console = Console()


def test_api_key():
    """Test if OpenAI API key is valid and working"""
    
    console.print("\n")
    console.print(Panel.fit(
        "OpenAI API Key Test",
        style="bold cyan"
    ))
    console.print("")
    
    try:
        # Load configuration
        console.print("[yellow]Loading configuration...[/yellow]")
        config = get_config()
        api_key = config.get_openai_api_key()
        
        # Mask the API key for display (show first 7 and last 4 characters)
        if len(api_key) > 11:
            masked_key = api_key[:7] + "*" * (len(api_key) - 11) + api_key[-4:]
        else:
            masked_key = "*" * len(api_key)
        
        console.print(f"[green]✓[/green] API Key loaded: {masked_key}")
        console.print("")
        
        # Test the API key with OpenAI
        console.print("[yellow]Testing API key with OpenAI...[/yellow]")
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            # Make a simple test call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use a simple, cheap model for testing
                messages=[
                    {"role": "user", "content": "Say 'API key is working' if you can read this."}
                ],
                max_tokens=20,
                temperature=0
            )
            
            # Extract response
            if response.choices and len(response.choices) > 0:
                message = response.choices[0].message.content
                console.print(f"[green]✓[/green] API Response: {message}")
                console.print("")
                console.print(Panel.fit(
                    "[green]✓ API KEY IS WORKING![/green]\n\n"
                    "Your OpenAI API key is valid and can make API calls.",
                    title="Success",
                    style="bold green"
                ))
                return True
            else:
                console.print("[red]✗[/red] No response from API")
                return False
                
        except ImportError:
            console.print("[red]✗[/red] OpenAI library not installed")
            console.print("[yellow]Install it with: pip install openai[/yellow]")
            return False
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for common error types
            if "Invalid API key" in error_msg or "Incorrect API key" in error_msg:
                console.print("[red]✗[/red] Invalid API Key")
                console.print(Panel.fit(
                    "[red]API KEY IS INVALID[/red]\n\n"
                    "The API key in your config.json is not valid.\n"
                    "Please check your OpenAI API key and update config.json.",
                    title="Error",
                    border_style="red"
                ))
            elif "Insufficient quota" in error_msg or "quota" in error_msg.lower():
                console.print("[red]✗[/red] API Quota Exceeded")
                console.print(Panel.fit(
                    "[yellow]API QUOTA EXCEEDED[/yellow]\n\n"
                    "Your API key is valid but you've exceeded your quota.\n"
                    "Please check your OpenAI account billing and usage.",
                    title="Warning",
                    border_style="yellow"
                ))
            elif "rate limit" in error_msg.lower():
                console.print("[red]✗[/red] Rate Limit Exceeded")
                console.print(Panel.fit(
                    "[yellow]RATE LIMIT EXCEEDED[/yellow]\n\n"
                    "Too many requests. Please wait a moment and try again.",
                    title="Warning",
                    border_style="yellow"
                ))
            else:
                console.print(f"[red]✗[/red] API Error: {error_msg}")
                console.print(Panel.fit(
                    f"[red]API ERROR[/red]\n\n"
                    f"Error: {error_msg}\n\n"
                    "Please check your API key and network connection.",
                    title="Error",
                    border_style="red"
                ))
            return False
            
    except FileNotFoundError as e:
        console.print(Panel.fit(
            "[red]CONFIG FILE NOT FOUND[/red]\n\n"
            f"Error: {str(e)}\n\n"
            "Please create a config.json file in the project root.\n"
            "You can copy config.json.example and update it.",
            title="Error",
            border_style="red"
        ))
        return False
        
    except ValueError as e:
        console.print(Panel.fit(
            "[red]CONFIGURATION ERROR[/red]\n\n"
            f"Error: {str(e)}\n\n"
            "Please check your config.json file.",
            title="Error",
            border_style="red"
        ))
        return False
        
    except Exception as e:
        console.print(Panel.fit(
            "[red]UNEXPECTED ERROR[/red]\n\n"
            f"Error: {str(e)}\n\n"
            "Please check the error message above.",
            title="Error",
            border_style="red"
        ))
        import traceback
        console.print(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = test_api_key()
    sys.exit(0 if success else 1)

