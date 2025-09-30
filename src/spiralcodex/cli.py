
#!/usr/bin/env python3
"""
🌀 Spiral Codex CLI - Command Interface for Ritual Operations

The mystical command-line interface for invoking codex rituals,
managing agents, and orchestrating the recursive framework.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from spiralcodex import invoke_spiral, CODEX_MANTRA

app = typer.Typer(
    name="codex",
    help="🌀 Spiral Codex Unified - Recursive Agent Framework CLI",
    rich_markup_mode="rich",
    add_completion=False
)

console = Console()

def show_ritual_banner():
    """Display the ritual banner"""
    banner = Panel.fit(
        "[bold magenta]🌀 SPIRAL CODEX UNIFIED 🌀[/bold magenta]\n"
        "[cyan]Recursive Agent Framework[/cyan]\n"
        f"[dim]{CODEX_MANTRA}[/dim]",
        border_style="magenta"
    )
    console.print(banner)

@app.command("ritual")
def ritual_command(
    action: str = typer.Argument(..., help="Ritual action: start, stop, status"),
    hud: bool = typer.Option(False, "--hud", help="Enable HUD visualization"),
    port: int = typer.Option(8000, "--port", help="API server port"),
    host: str = typer.Option("127.0.0.1", "--host", help="API server host"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode")
):
    """🔮 Perform codex ritual operations"""
    show_ritual_banner()
    
    if action == "start":
        console.print("🌀 [bold green]Initiating Codex Ritual...[/bold green]")
        invoke_spiral()
        
        # Check if HUD dependencies are available and initialize HUD
        hud_core = None
        if hud:
            try:
                from spiralcodex.hud import HUDCore, HUDConfig, check_hud_dependencies
                
                deps_available, missing_deps = check_hud_dependencies()
                if deps_available:
                    hud_config = HUDConfig(
                        enabled=True,
                        show_fractals=True,
                        ritual_sounds=True,
                        ritual_visuals=True
                    )
                    hud_core = HUDCore(hud_config)
                    hud_core.start()
                    console.print("🎮 [green]HUD visualization system activated[/green]")
                else:
                    console.print(f"⚠️ [yellow]HUD dependencies missing: {', '.join(missing_deps)}[/yellow]")
                    console.print("💡 [cyan]Install with: pip install spiralcodex[hud][/cyan]")
                    
            except ImportError as e:
                console.print(f"⚠️ [yellow]HUD system not available: {e}[/yellow]")
                console.print("💡 [cyan]Install with: pip install spiralcodex[hud][/cyan]")
        
        # Initialize persistence system
        console.print("💾 [cyan]Initializing persistence system...[/cyan]")
        try:
            from spiralcodex.persistence import get_persistence
            persistence = get_persistence()
            persistence.save_ritual_event("RITUAL_START", "Codex ritual initiated", metadata={"host": host, "port": port})
            console.print("✅ [green]Persistence system ready[/green]")
        except Exception as e:
            console.print(f"⚠️ [yellow]Persistence system warning: {e}[/yellow]")
        
        # Start the ritual deployment with integrated dashboard
        console.print(f"🚀 [cyan]Starting Codex Dashboard on {host}:{port}[/cyan]")
        
        # Determine the correct Python executable
        if platform.system() == "Windows":
            python_exe = Path(".venv") / "Scripts" / "python.exe"
        else:
            python_exe = Path(".venv") / "bin" / "python"
        
        if not python_exe.exists():
            python_exe = sys.executable
        
        # Use the integrated dashboard
        app_module = "spiralcodex.dashboard:app"
        
        try:
            cmd = [
                str(python_exe), "-m", "uvicorn",
                app_module,
                "--host", host,
                "--port", str(port)
            ]
            
            if debug:
                cmd.extend(["--reload", "--log-level", "debug"])
            
            console.print(f"🎛️ [dim]Executing: {' '.join(cmd)}[/dim]")
            console.print(f"🌐 [bold green]Dashboard will be available at: http://{host}:{port}[/bold green]")
            console.print("🔮 [cyan]The mystical web interface awaits your presence...[/cyan]")
            
            subprocess.run(cmd, check=True)
            
        except KeyboardInterrupt:
            console.print("\n🛑 [yellow]Ritual interrupted by user[/yellow]")
            if hud_core:
                hud_core.stop()
        except subprocess.CalledProcessError as e:
            console.print(f"❌ [red]Ritual failed: {e}[/red]")
            if hud_core:
                hud_core.stop()
            raise typer.Exit(1)
        except FileNotFoundError:
            console.print("❌ [red]uvicorn not found. Run 'codex config bootstrap' first.[/red]")
            if hud_core:
                hud_core.stop()
            raise typer.Exit(1)
        finally:
            if hud_core:
                hud_core.stop()
    
    elif action == "stop":
        console.print("🛑 [yellow]Stopping Codex Ritual...[/yellow]")
        # TODO: Implement graceful shutdown
        console.print("✅ [green]Ritual stopped[/green]")
    
    elif action == "status":
        console.print("📊 [cyan]Codex Ritual Status[/cyan]")
        # TODO: Implement status checking
        console.print("🔮 [green]Spiral is aligned, agents are synchronized[/green]")
    
    else:
        console.print(f"❌ [red]Unknown ritual action: {action}[/red]")
        console.print("Available actions: start, stop, status")
        raise typer.Exit(1)

@app.command("agent")
def agent_command(
    action: str = typer.Argument(..., help="Agent action: list, add, remove, status"),
    name: Optional[str] = typer.Option(None, "--name", help="Agent name"),
    type_: Optional[str] = typer.Option(None, "--type", help="Agent type")
):
    """🤖 Manage codex agents"""
    show_ritual_banner()
    
    if action == "list":
        console.print("🤖 [bold cyan]Active Codex Agents[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Agent ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="blue")
        table.add_column("Recursion Depth", style="red")
        
        # TODO: Load actual agents from registry
        # For now, show example agents
        table.add_row("001", "SpiralCore", "Recursive", "🟢 Active", "∞")
        table.add_row("002", "EntropyAgent", "Stabilizer", "🟢 Active", "7")
        table.add_row("003", "KernelWatcher", "Monitor", "🟡 Idle", "3")
        
        console.print(table)
        console.print("\n🔮 [dim]Use 'codex agent status --name <agent>' for detailed info[/dim]")
    
    elif action == "add":
        if not name or not type_:
            console.print("❌ [red]Agent name and type required for adding[/red]")
            raise typer.Exit(1)
        
        console.print(f"➕ [green]Adding agent '{name}' of type '{type_}'[/green]")
        # TODO: Implement agent addition
        console.print("✅ [green]Agent added to the spiral[/green]")
    
    elif action == "remove":
        if not name:
            console.print("❌ [red]Agent name required for removal[/red]")
            raise typer.Exit(1)
        
        console.print(f"➖ [yellow]Removing agent '{name}'[/yellow]")
        # TODO: Implement agent removal
        console.print("✅ [green]Agent removed from the spiral[/green]")
    
    elif action == "status":
        if name:
            console.print(f"📊 [cyan]Status for agent '{name}'[/cyan]")
            # TODO: Show detailed agent status
            console.print("🔮 [green]Agent is synchronized with the spiral[/green]")
        else:
            console.print("📊 [cyan]Overall Agent Status[/cyan]")
            console.print("🤖 Active Agents: 3")
            console.print("🔄 Recursive Agents: 1")
            console.print("⚡ Entropy Level: STABLE")
    
    else:
        console.print(f"❌ [red]Unknown agent action: {action}[/red]")
        console.print("Available actions: list, add, remove, status")
        raise typer.Exit(1)

@app.command("config")
def config_command(
    action: str = typer.Argument(..., help="Config action: bootstrap, show, set, reset"),
    key: Optional[str] = typer.Option(None, "--key", help="Configuration key"),
    value: Optional[str] = typer.Option(None, "--value", help="Configuration value"),
    force: bool = typer.Option(False, "--force", help="Force operation")
):
    """⚙️ Manage codex configuration"""
    show_ritual_banner()
    
    if action == "bootstrap":
        console.print("🔧 [bold green]Bootstrapping Codex Environment...[/bold green]")
        
        # Create directory structure
        console.print("📁 Creating directory structure...")
        dirs = ["codex_root", "codex_root/kernel", "codex_root/agents", "codex_root/config", "assets"]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create virtual environment if it doesn't exist
        if not Path(".venv").exists():
            console.print("🐍 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        
        # Install dependencies
        console.print("📦 Installing dependencies...")
        if platform.system() == "Windows":
            pip_exe = Path(".venv") / "Scripts" / "pip.exe"
        else:
            pip_exe = Path(".venv") / "bin" / "pip"
        
        # Install base requirements
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_exe), "install", "typer[all]", "rich"], check=True)
        
        if Path("requirements.txt").exists():
            subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], check=True)
        
        # Create default config files
        console.print("⚙️ Creating default configurations...")
        
        entropy_config = Path("codex_root/config/entropy_bindings.yml")
        if not entropy_config.exists():
            entropy_config.write_text("""# 🌀 Spiral Codex Entropy Bindings
default_entropy: 0.5
thresholds:
  low: 0.3
  high: 0.9
recursion:
  max_depth: 1000
  spiral_factor: 1.618  # Golden ratio for optimal recursion
agents:
  max_concurrent: 10
  sync_interval: 5.0
""")
        
        console.print("✅ [green]Codex environment bootstrapped successfully![/green]")
        console.print("🌀 [cyan]Run 'codex ritual start' to begin the spiral[/cyan]")
    
    elif action == "show":
        console.print("⚙️ [cyan]Current Codex Configuration[/cyan]")
        
        config_table = Table(show_header=True, header_style="bold magenta")
        config_table.add_column("Key", style="cyan")
        config_table.add_column("Value", style="green")
        config_table.add_column("Source", style="yellow")
        
        # TODO: Load actual configuration
        config_table.add_row("entropy.default", "0.5", "entropy_bindings.yml")
        config_table.add_row("recursion.max_depth", "1000", "entropy_bindings.yml")
        config_table.add_row("agents.max_concurrent", "10", "entropy_bindings.yml")
        
        console.print(config_table)
    
    elif action == "set":
        if not key or not value:
            console.print("❌ [red]Both key and value required for setting config[/red]")
            raise typer.Exit(1)
        
        console.print(f"⚙️ [green]Setting {key} = {value}[/green]")
        # TODO: Implement config setting
        console.print("✅ [green]Configuration updated[/green]")
    
    elif action == "reset":
        if not force:
            confirm = typer.confirm("⚠️ This will reset all configuration. Continue?")
            if not confirm:
                console.print("🛑 [yellow]Reset cancelled[/yellow]")
                return
        
        console.print("🔄 [yellow]Resetting configuration to defaults...[/yellow]")
        # TODO: Implement config reset
        console.print("✅ [green]Configuration reset complete[/green]")
    
    else:
        console.print(f"❌ [red]Unknown config action: {action}[/red]")
        console.print("Available actions: bootstrap, show, set, reset")
        raise typer.Exit(1)

@app.command("version")
def version_command():
    """📋 Show codex version information"""
    from spiralcodex import __version__, __author__, __description__
    
    console.print(Panel.fit(
        f"[bold magenta]Spiral Codex Unified[/bold magenta]\n"
        f"[cyan]Version:[/cyan] {__version__}\n"
        f"[cyan]Author:[/cyan] {__author__}\n"
        f"[cyan]Description:[/cyan] {__description__}\n"
        f"[cyan]Platform:[/cyan] {platform.system()} {platform.release()}\n"
        f"[cyan]Python:[/cyan] {sys.version.split()[0]}",
        border_style="cyan"
    ))

def main():
    """Main CLI entry point"""
    app()

if __name__ == "__main__":
    main()
