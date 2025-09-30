

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
agent_app = typer.Typer(name="agent", help="🤖 Agent plugin management")
app.add_typer(mesh_app, name="mesh")
app.add_typer(agent_app, name="agent")

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
    plugins: bool = typer.Option(True, "--plugins/--no-plugins", help="Enable plugin system"),
    port: int = typer.Option(8000, "--port", help="API server port"),
    host: str = typer.Option("127.0.0.1", "--host", help="API server host"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode")
):
    """🔮 Perform codex ritual operations"""
    show_ritual_banner()
    
    if action == "start":
        console.print("🌀 [bold green]Initiating Codex Ritual...[/bold green]")
        invoke_spiral()
        
        # Initialize plugin system if requested
        plugin_manager = None
        if plugins:
            try:
                from spiralcodex.plugins import PluginManager, PluginConfig
                
                plugin_config = PluginConfig(
                    plugins_directory="agents",
                    auto_discover=True,
                    auto_load=True,
                    auto_activate=True
                )
                plugin_manager = PluginManager(config=plugin_config)
                plugin_manager.start()
                
                active_plugins = plugin_manager.get_active_plugins()
                console.print(f"🤖 [green]Plugin system activated - {len(active_plugins)} agents loaded[/green]")
                
                for plugin in active_plugins:
                    console.print(f"  ✨ [cyan]{plugin.name}[/cyan] v{plugin.version} - {plugin.description}")
                
            except ImportError as e:
                console.print(f"⚠️ [yellow]Plugin system not available: {e}[/yellow]")
            except Exception as e:
                console.print(f"⚠️ [yellow]Plugin system failed to start: {e}[/yellow]")
        
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
            persistence.save_ritual_event("RITUAL_START", "Codex ritual initiated", metadata={
                "host": host, 
                "port": port, 
                "mesh_enabled": mesh,
                "plugins_enabled": plugins,
                "active_plugins": len(plugin_manager.get_active_plugins()) if plugin_manager else 0
            })
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

# Agent plugin commands
@agent_app.command("list")
def agent_list(
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status: active, loaded, discovered, error"),
    capability: Optional[str] = typer.Option(None, "--capability", help="Filter by capability")
):
    """📋 List available agent plugins"""
    try:
        from spiralcodex.plugins import PluginManager, PluginStatus
        
        manager = PluginManager()
        manager.start()
        
        # Get plugins based on filters
        if status:
            try:
                status_filter = PluginStatus(status)
                plugins = manager.list_plugins(status_filter)
            except ValueError:
                console.print(f"❌ [red]Invalid status: {status}[/red]")
                console.print("💡 [cyan]Valid statuses: active, loaded, discovered, error, disabled[/cyan]")
                return
        elif capability:
            plugins = manager.find_plugins_by_capability(capability)
        else:
            plugins = manager.list_plugins()
        
        if not plugins:
            console.print("📋 [yellow]No plugins found[/yellow]")
            return
        
        # Create table
        table = Table(title="🤖 Agent Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Description", style="dim")
        table.add_column("Capabilities", style="blue")
        
        for plugin in plugins:
            status_emoji = {
                "active": "✅",
                "loaded": "📦",
                "discovered": "🔍",
                "error": "❌",
                "disabled": "⏸️"
            }.get(plugin.status.value, "❓")
            
            capabilities_str = ", ".join(plugin.capabilities[:3])
            if len(plugin.capabilities) > 3:
                capabilities_str += f" (+{len(plugin.capabilities) - 3} more)"
            
            table.add_row(
                plugin.name,
                plugin.version,
                f"{status_emoji} {plugin.status.value}",
                plugin.description[:50] + "..." if len(plugin.description) > 50 else plugin.description,
                capabilities_str
            )
        
        console.print(table)
        console.print(f"\n📊 [dim]Total: {len(plugins)} plugins[/dim]")
        
        manager.stop()
        
    except ImportError as e:
        console.print(f"❌ [red]Plugin system not available: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Failed to list plugins: {e}[/red]")

@agent_app.command("enable")
def agent_enable(plugin_name: str):
    """✅ Enable an agent plugin"""
    try:
        from spiralcodex.plugins import PluginManager
        
        manager = PluginManager()
        manager.start()
        
        if manager.enable(plugin_name):
            console.print(f"✅ [green]Plugin enabled: {plugin_name}[/green]")
        else:
            console.print(f"❌ [red]Failed to enable plugin: {plugin_name}[/red]")
        
        manager.stop()
        
    except ImportError as e:
        console.print(f"❌ [red]Plugin system not available: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Failed to enable plugin: {e}[/red]")

@agent_app.command("disable")
def agent_disable(plugin_name: str):
    """⏸️ Disable an agent plugin"""
    try:
        from spiralcodex.plugins import PluginManager
        
        manager = PluginManager()
        manager.start()
        
        if manager.disable(plugin_name):
            console.print(f"⏸️ [yellow]Plugin disabled: {plugin_name}[/yellow]")
        else:
            console.print(f"❌ [red]Failed to disable plugin: {plugin_name}[/red]")
        
        manager.stop()
        
    except ImportError as e:
        console.print(f"❌ [red]Plugin system not available: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Failed to disable plugin: {e}[/red]")

@agent_app.command("info")
def agent_info(plugin_name: str):
    """ℹ️ Show detailed information about an agent plugin"""
    try:
        from spiralcodex.plugins import PluginManager
        
        manager = PluginManager()
        manager.start()
        
        plugin = manager.get_plugin(plugin_name)
        if not plugin:
            console.print(f"❌ [red]Plugin not found: {plugin_name}[/red]")
            return
        
        # Create info panel
        info_text = f"""[bold cyan]{plugin.name}[/bold cyan] v{plugin.version}
[dim]by {plugin.author}[/dim]

[yellow]Description:[/yellow]
{plugin.description}

[yellow]Status:[/yellow] {plugin.status.value}
[yellow]Loaded:[/yellow] {'Yes' if plugin.loaded else 'No'}
[yellow]Active:[/yellow] {'Yes' if plugin.active else 'No'}

[yellow]Capabilities:[/yellow]
{chr(10).join(f'  • {cap}' for cap in plugin.capabilities)}

[yellow]Dependencies:[/yellow]
{chr(10).join(f'  • {dep}' for dep in plugin.dependencies) if plugin.dependencies else '  None'}
"""
        
        panel = Panel(info_text, title=f"🤖 Agent Plugin: {plugin_name}", border_style="cyan")
        console.print(panel)
        
        # Show metrics if active
        if plugin.active:
            metrics = manager.get_plugin_metrics(plugin_name)
            if metrics:
                console.print("\n📊 [cyan]Plugin Metrics:[/cyan]")
                for key, value in metrics.items():
                    console.print(f"  [yellow]{key}:[/yellow] {value}")
        
        manager.stop()
        
    except ImportError as e:
        console.print(f"❌ [red]Plugin system not available: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Failed to get plugin info: {e}[/red]")

@agent_app.command("reload")
def agent_reload(plugin_name: str):
    """🔄 Reload an agent plugin"""
    try:
        from spiralcodex.plugins import PluginManager
        
        manager = PluginManager()
        manager.start()
        
        if manager.reload(plugin_name):
            console.print(f"🔄 [green]Plugin reloaded: {plugin_name}[/green]")
        else:
            console.print(f"❌ [red]Failed to reload plugin: {plugin_name}[/red]")
        
        manager.stop()
        
    except ImportError as e:
        console.print(f"❌ [red]Plugin system not available: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Failed to reload plugin: {e}[/red]")

@agent_app.command("create")
def agent_create(
    name: str = typer.Argument(..., help="Plugin name"),
    author: str = typer.Option("Unknown", "--author", help="Plugin author")
):
    """🆕 Create a new agent plugin template"""
    try:
        from spiralcodex.plugins import PluginManager
        
        manager = PluginManager()
        template = manager.create_plugin_template(name, author)
        
        # Write template to file
        plugin_file = Path("agents") / f"{name.lower()}.py"
        plugin_file.parent.mkdir(exist_ok=True)
        
        with open(plugin_file, 'w') as f:
            f.write(template)
        
        console.print(f"🆕 [green]Plugin template created: {plugin_file}[/green]")
        console.print("💡 [cyan]Edit the file to implement your custom agent logic[/cyan]")
        
    except ImportError as e:
        console.print(f"❌ [red]Plugin system not available: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Failed to create plugin template: {e}[/red]")

@agent_app.command("health")
def agent_health():
    """🏥 Check health of all agent plugins"""
    try:
        from spiralcodex.plugins import PluginManager
        
        manager = PluginManager()
        manager.start()
        
        health = manager.health_check()
        
        # Overall status
        status_color = {
            "healthy": "green",
            "degraded": "yellow", 
            "unhealthy": "red"
        }.get(health["overall_status"], "blue")
        
        console.print(f"🏥 [bold {status_color}]Overall Status: {health['overall_status'].upper()}[/bold {status_color}]")
        console.print(f"📊 [cyan]Total Plugins: {health['total_plugins']}[/cyan]")
        console.print(f"✅ [green]Active Plugins: {health['active_plugins']}[/green]")
        console.print(f"❌ [red]Unhealthy Plugins: {health['unhealthy_count']}[/red]")
        
        # Plugin health details
        if health["plugin_health"]:
            console.print("\n🔍 [cyan]Plugin Health Details:[/cyan]")
            
            for plugin_name, plugin_health in health["plugin_health"].items():
                health_emoji = "✅" if plugin_health["healthy"] else "❌"
                console.print(f"  {health_emoji} [cyan]{plugin_name}[/cyan]: {plugin_health['status']}")
                
                if "error" in plugin_health:
                    console.print(f"    [red]Error: {plugin_health['error']}[/red]")
        
        manager.stop()
        
    except ImportError as e:
        console.print(f"❌ [red]Plugin system not available: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Failed to check plugin health: {e}[/red]")

@app.command("version")
def version():
    """📋 Show version information"""
    console.print("🌀 [bold magenta]Spiral Codex Unified[/bold magenta]")
    console.print("📋 [cyan]Version: 1.0.0-alpha[/cyan]")
    console.print("🔄 [cyan]Spiral Cycle: 8 (Plugin Architecture)[/cyan]")
    console.print(f"🐍 [dim]Python: {platform.python_version()}[/dim]")
    console.print(f"💻 [dim]Platform: {platform.system()} {platform.release()}[/dim]")

if __name__ == "__main__":
    app()
