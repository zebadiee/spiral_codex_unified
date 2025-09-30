#!/usr/bin/env python3
"""
🌀 Spiral Codex Unified - Modern CLI Deployment Script

This script provides backward compatibility while transitioning to the new CLI system.
It wraps the new Typer-based CLI for seamless migration.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main deployment function - delegates to new CLI system"""
    print("🌀 Spiral Codex Unified - Transitioning to CLI system...")
    print("📋 This script now uses the new 'codex' CLI interface")
    print("🔄 For full functionality, use: 'codex ritual start --hud'")
    print()
    
    # Check if we're in a virtual environment or if CLI is available
    try:
        # Try to import and run the CLI directly
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from spiralcodex.cli import main as cli_main
        
        # Simulate the old deploy.py behavior with new CLI
        print("🚀 Starting ritual via new CLI system...")
        sys.argv = ["codex", "ritual", "start", "--debug"]
        cli_main()
        
    except ImportError:
        # Fallback: try to run via command line
        print("⚠️ CLI not available in current environment")
        print("🔧 Run 'codex config bootstrap' first, or use deploy_legacy.py")
        print()
        print("📋 Available commands:")
        print("  codex ritual start [--hud] [--port 8000]  # Start the spiral")
        print("  codex agent list                          # List active agents")
        print("  codex config bootstrap                    # Setup environment")
        print("  codex --help                              # Show all commands")
        
        # Try to run the legacy version as fallback
        legacy_path = Path(__file__).parent / "deploy_legacy.py"
        if legacy_path.exists():
            print()
            print("🔄 Falling back to legacy deployment...")
            subprocess.run([sys.executable, str(legacy_path)])
        else:
            print("❌ Legacy deployment not available")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
