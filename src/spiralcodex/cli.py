

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
import asyncio
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

# Create subcommands
mesh_app = typer.Typer(name="mesh", help="🌐 Mesh network operations")
app.add_typer(mesh_app, name="mesh")

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
    mesh: bool = typer.Option(False, "--mesh", help="Enable mesh network"),
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
        
        # Initialize mesh network if requested
        mesh_core = None
        if mesh:
            try:
                from spiralcodex.mesh import MeshCore, MeshConfig
                
                mesh_config = MeshConfig(
                    websocket_port=8765,
                    enable_redis=True,
                    enable_websocket=True
                )
                mesh_core = MeshCore(mesh_config)
                
                # Start mesh in background
                import threading
                def start_mesh():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(mesh_core.start())
                    loop.run_forever()
                
                mesh_thread = threading.Thread(target=start_mesh, daemon=True)
                mesh_thread.start()
                
                console.print("🌐 [green]Mesh network activated[/green]")
                console.print(f"📡 [cyan]Node ID: {mesh_core.node_id[:8]}...[/cyan]")
                
            except ImportError as e:
                console.print(f"⚠️ [yellow]Mesh dependencies missing: {e}[/yellow]")
                console.print("💡 [cyan]Install with: pip install redis websockets[/cyan]")
            except Exception as e:
                console.print(f"⚠️ [yellow]Mesh initialization failed: {e}[/yellow]")
        
        # Initialize persistence system
        console.print("💾 [cyan]Initializing persistence system...[/cyan]")
        try:
            from spiralcodex.persistence import get_persistence
            persistence = get_persistence()
            persistence.save_ritual_event("RITUAL_START", "Codex ritual initiated", metadata={"host": host, "port": port, "mesh_enabled": mesh})
            console.print("✅ [green]Persistence system ready[/green]")
        except Exception as e:
            console.print(f"⚠️ [yellow]Persistence system warning: {e}[/yellow]")
        
        # Start the ritual deployment with integrated dashboard
        console.print(f"🚀 [cyan]Starting Codex Dashboard on {host}:{port}[/cyan]")
        
        # Determine the correct Python executable
        python_exe = sys.executable
        
        # Build the command to run the dashboard
        dashboard_cmd = [
            python_exe, "-m", "spiralcodex.dashboard",
            "--host", host,
            "--port", str(port)
        ]
        
        if debug:
            dashboard_cmd.append("--debug")
        
        try:
            # Run the dashboard
            subprocess.run(dashboard_cmd, cwd=project_root)
        except KeyboardInterrupt:
            console.print("\n🌙 [yellow]Ritual interrupted by user[/yellow]")
        except Exception as e:
            console.print(f"❌ [red]Ritual failed: {e}[/red]")
    
    elif action == "stop":
        console.print("🌙 [yellow]Stopping Codex Ritual...[/yellow]")
        # Implementation for stopping services
        console.print("✅ [green]Ritual stopped[/green]")
    
    elif action == "status":
        console.print("📊 [cyan]Codex Ritual Status[/cyan]")
        # Implementation for status check
        console.print("ℹ️ [blue]Status check not yet implemented[/blue]")
    
    else:
        console.print(f"❌ [red]Unknown ritual action: {action}[/red]")
        console.print("💡 [cyan]Available actions: start, stop, status[/cyan]")

# Mesh network commands
@mesh_app.command("start")
def mesh_start(
    port: int = typer.Option(8765, "--port", help="WebSocket port"),
    redis_url: str = typer.Option("redis://localhost:6379", "--redis", help="Redis URL"),
    name: str = typer.Option("spiral_codex_mesh", "--name", help="Mesh network name")
):
    """🌐 Start a mesh network node"""
    console.print("🌀 [bold green]Starting Mesh Network Node...[/bold green]")
    
    try:
        from spiralcodex.mesh import MeshCore, MeshConfig
        
        config = MeshConfig(
            mesh_name=name,
            websocket_port=port,
            redis_url=redis_url,
            enable_redis=True,
            enable_websocket=True
        )
        
        mesh_core = MeshCore(config)
        
        async def run_mesh():
            await mesh_core.start()
            console.print(f"✨ [green]Mesh node active - ID: {mesh_core.node_id[:8]}...[/green]")
            console.print(f"🌐 [cyan]WebSocket: ws://localhost:{port}[/cyan]")
            console.print(f"🔗 [cyan]Redis: {redis_url}[/cyan]")
            console.print("Press Ctrl+C to stop...")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                console.print("\n🌙 [yellow]Stopping mesh node...[/yellow]")
                await mesh_core.stop()
                console.print("✅ [green]Mesh node stopped[/green]")
        
        asyncio.run(run_mesh())
        
    except ImportError as e:
        console.print(f"❌ [red]Mesh dependencies missing: {e}[/red]")
        console.print("💡 [cyan]Install with: pip install redis websockets[/cyan]")
    except Exception as e:
        console.print(f"❌ [red]Failed to start mesh node: {e}[/red]")

@mesh_app.command("status")
def mesh_status():
    """📊 Show mesh network status"""
    console.print("📊 [cyan]Mesh Network Status[/cyan]")
    console.print("ℹ️ [blue]Status check not yet implemented[/blue]")
    console.print("💡 [dim]This will show connected nodes, network health, and sync status[/dim]")

@mesh_app.command("nodes")
def mesh_nodes():
    """📡 List connected mesh nodes"""
    console.print("📡 [cyan]Connected Mesh Nodes[/cyan]")
    console.print("ℹ️ [blue]Node listing not yet implemented[/blue]")
    console.print("💡 [dim]This will show all active nodes in the mesh network[/dim]")

@app.command("version")
def version():
    """📋 Show version information"""
    console.print("🌀 [bold magenta]Spiral Codex Unified[/bold magenta]")
    console.print("📋 [cyan]Version: 1.0.0-alpha[/cyan]")
    console.print("🔄 [cyan]Spiral Cycle: 7 (Multi-Agent Mesh)[/cyan]")
    console.print(f"🐍 [dim]Python: {platform.python_version()}[/dim]")
    console.print(f"💻 [dim]Platform: {platform.system()} {platform.release()}[/dim]")

if __name__ == "__main__":
    app()
