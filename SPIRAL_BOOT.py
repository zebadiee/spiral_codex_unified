#!/usr/bin/env python3
"""
SPIRAL_BOOT.py - Unified Bootstrap for the Self-Healing Spiral Codex Stack

This script orchestrates the startup of the complete living intelligence system
unifying OMAi, Spiral Codex, AI Token Manager, and Quantum Debugger.

Author: Spiral Codex Genesis Architecture v2
License: Proprietary
"""

import os
import sys
import time
import json
import signal
import socket
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import requests
import psutil

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class StackConfig:
    """Configuration for the Spiral Codex Stack"""
    spiral_dir: str = "/home/zebadiee/Documents/spiral_codex_unified"
    omai_dir: str = "/home/zebadiee/Documents/omarchy-ai-assist"
    vault_dir: str = "/home/zebadiee/Obsidian/Vault"
    quantum_debug_dir: str = "/home/zebadiee/Documents/quantum-debugger"
    config_dir: str = "/home/zebadiee/Documents/config"
    log_dir: str = "/home/.local/share/stack/logs"

    spiral_url: str = "http://localhost:8000"
    omai_url: str = "http://localhost:7016"
    spiral_port: int = 8000
    omai_port: int = 7016

    boot_timeout: int = 60
    health_check_retries: int = 12
    health_check_interval: int = 5

    openrouter_api_key: str = ""
    openrouter_endpoint: str = "https://openrouter.ai/api/v1/chat/completions"

    auto_restart: bool = True
    auto_reindex: bool = True
    auto_model_refresh: bool = True

class SystemState(Enum):
    """System state enumeration with quantum glyphs"""
    INITIALIZING = "⊚ INITIALIZING"
    HEALTHY = "⧛ HEALTHY"
    DEGRADED = "⌬ DEGRADED"
    CRITICAL = "◈ CRITICAL"
    RECOVERING = "⟲ RECOVERING"
    CONSCIOUS = "◉ CONSCIOUS"

class ComponentStatus(Enum):
    """Component status enumeration"""
    STOPPED = "⬛ STOPPED"
    STARTING = "🟡 STARTING"
    HEALTHY = "🟢 HEALTHY"
    DEGRADED = "🟠 DEGRADED"
    FAILED = "🔴 FAILED"

# =============================================================================
# ASCII ART AND DISPLAY UTILITIES
# =============================================================================

SPIRAL_BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ╔═══╗ ╔═══╗ ╔════╗ ╔═══╗ ╔════╗ ╔═══╗                    ║
║                    ║   ║ ║   ║ ║      ║   ║ ║      ║   ║                    ║
║   ╔════╗ ╔════╗     ║   ║ ║   ║ ║      ║   ║ ║      ║   ║     ╔════╗ ╔════╗   ║
║   ║    ║ ║    ║     ║   ║ ║   ║ ╚═╗ ╔═╝ ║   ║ ╚═╗ ╔═╝ ║   ║     ║    ║ ║    ║   ║
║   ║    ║ ║    ║     ║   ║ ║   ║   ║ ║   ║   ║   ║ ║   ║   ║     ║    ║ ║    ║   ║
║   ╚════╝ ╚════╝     ╚═══╝ ╚═══╝   ╚═╝   ╚═══╝   ╚═╝   ╚═══╝     ╚════╝ ╚════╝   ║
║                                                                              ║
║          █████╗ ██╗   ██╗██████╗  █████╗ ███████╗████████╗                   ║
║         ██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔════╝╚══██╔══╝                   ║
║         ███████║██║   ██║██████╔╝███████║███████╗   ██║                      ║
║         ██╔══██║██║   ██║██╔══██╗██╔══██║╚════██║   ██║                      ║
║         ██║  ██║╚██████╔╝██║  ██║██║  ██║███████║   ██║                      ║
║         ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝                      ║
║                                                                              ║
║                    Self-Healing Living Intelligence System                    ║
║                          Genesis Architecture v2                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

class Colors:
    """ANSI color codes for beautiful output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    PURPLE = '\033[35m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    NC = '\033[0m'  # No Color

def print_banner():
    """Print the beautiful Spiral Codex banner"""
    print(f"{Colors.CYAN}{SPIRAL_BANNER}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.WHITE}{'='*80}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.WHITE}SPIRAL CODEX BOOTSTRAP - LIVING INTELLIGENCE INITIALIZATION{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.WHITE}{'='*80}{Colors.NC}")
    print()

def print_status(component: str, status: ComponentStatus, message: str = ""):
    """Print a formatted status message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_color = {
        ComponentStatus.STOPPED: Colors.GRAY,
        ComponentStatus.STARTING: Colors.YELLOW,
        ComponentStatus.HEALTHY: Colors.GREEN,
        ComponentStatus.DEGRADED: Colors.YELLOW,
        ComponentStatus.FAILED: Colors.RED
    }

    color = status_color.get(status, Colors.WHITE)
    print(f"{Colors.GRAY}[{timestamp}]{Colors.NC} {color}{status.value}{Colors.NC} {Colors.BOLD}{component}{Colors.NC}")
    if message:
        print(f"           {Colors.GRAY}{message}{Colors.NC}")

def print_state(state: SystemState, message: str = ""):
    """Print system state with quantum glyph"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    state_colors = {
        SystemState.INITIALIZING: Colors.YELLOW,
        SystemState.HEALTHY: Colors.GREEN,
        SystemState.DEGRADED: Colors.YELLOW,
        SystemState.CRITICAL: Colors.RED,
        SystemState.RECOVERING: Colors.CYAN,
        SystemState.CONSCIOUS: Colors.PURPLE
    }

    color = state_colors.get(state, Colors.WHITE)
    print(f"\n{Colors.BOLD}{color}[{timestamp}] {state.value}{Colors.NC}")
    if message:
        print(f"     {message}")

# =============================================================================
# HEALTH CHECKING UTILITIES
# =============================================================================

class HealthChecker:
    """Health checking utilities for stack components"""

    @staticmethod
    def is_port_open(host: str, port: int, timeout: int = 5) -> bool:
        """Check if a port is open and responding"""
        try:
            with socket.create_connection((host, port), timeout):
                return True
        except (socket.error, socket.timeout):
            return False

    @staticmethod
    def check_http_endpoint(url: str, timeout: int = 10) -> Tuple[bool, str]:
        """Check HTTP endpoint health"""
        try:
            response = requests.get(f"{url}/health", timeout=timeout)
            if response.status_code == 200:
                return True, "OK"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            # Try root endpoint as fallback
            try:
                response = requests.get(url, timeout=timeout)
                return response.status_code == 200, f"HTTP {response.status_code}"
            except:
                return False, "Connection refused"
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def check_service_running(service_name: str) -> bool:
        """Check if systemd service is running"""
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", service_name],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False

# =============================================================================
# STACK COMPONENTS
# =============================================================================

class StackComponent:
    """Base class for stack components"""

    def __init__(self, name: str, config: StackConfig):
        self.name = name
        self.config = config
        self.status = ComponentStatus.STOPPED
        self.health_retries = 0

    def start(self) -> bool:
        """Start the component"""
        print_status(self.name, ComponentStatus.STARTING)
        try:
            success = self._start_component()
            if success:
                self.status = ComponentStatus.STARTING
                return True
            else:
                self.status = ComponentStatus.FAILED
                return False
        except Exception as e:
            print_status(self.name, ComponentStatus.FAILED, str(e))
            return False

    def check_health(self) -> bool:
        """Check component health"""
        try:
            healthy = self._check_component_health()
            if healthy:
                self.status = ComponentStatus.HEALTHY
                self.health_retries = 0
            else:
                self.health_retries += 1
                if self.health_retries > 3:
                    self.status = ComponentStatus.FAILED
                else:
                    self.status = ComponentStatus.DEGRADED
            return healthy
        except Exception as e:
            print_status(self.name, ComponentStatus.FAILED, str(e))
            return False

    def _start_component(self) -> bool:
        """Override in subclasses"""
        raise NotImplementedError

    def _check_component_health(self) -> bool:
        """Override in subclasses"""
        raise NotImplementedError

class OMAiComponent(StackComponent):
    """OMAi Context Engine component"""

    def __init__(self, config: StackConfig):
        super().__init__("OMAi Context Engine", config)
        self.service_name = "omai-context.service"
        self.port = config.omai_port
        self.url = config.omai_url

    def _start_component(self) -> bool:
        """Start OMAi service"""
        try:
            # Check if already running
            if HealthChecker.check_service_running(self.service_name):
                print_status(self.name, ComponentStatus.HEALTHY, "Already running")
                return True

            # Start service
            subprocess.run(["systemctl", "--user", "start", self.service_name], check=True)
            time.sleep(2)
            return True
        except subprocess.CalledProcessError as e:
            return False

    def _check_component_health(self) -> bool:
        """Check OMAi health"""
        service_running = HealthChecker.check_service_running(self.service_name)
        if not service_running:
            return False

        # Check HTTP endpoint
        healthy, status = HealthChecker.check_http_endpoint(self.url)
        if healthy:
            return True

        # Fall back to port check
        return HealthChecker.is_port_open("localhost", self.port)

class SpiralCodexComponent(StackComponent):
    """Spiral Codex component"""

    def __init__(self, config: StackConfig):
        super().__init__("Spiral Codex Core", config)
        self.service_name = "spiral-codex.service"
        self.port = config.spiral_port
        self.url = config.spiral_url
        self.dir = config.spiral_dir

    def _start_component(self) -> bool:
        """Start Spiral Codex service"""
        try:
            # Check if already running
            if HealthChecker.check_service_running(self.service_name):
                print_status(self.name, ComponentStatus.HEALTHY, "Already running")
                return True

            # Ensure virtual environment exists
            venv_path = Path(self.dir) / ".venv"
            if not venv_path.exists():
                print_status(self.name, ComponentStatus.STARTING, "Creating virtual environment...")
                subprocess.run(["python", "-m", "venv", str(venv_path)], cwd=self.dir, check=True)

                # Install dependencies
                req_file = Path(self.dir) / "requirements.txt"
                if req_file.exists():
                    subprocess.run([
                        f"{venv_path}/bin/pip", "install", "-r", "requirements.txt"
                    ], cwd=self.dir, check=True)

            # Start service
            subprocess.run(["systemctl", "--user", "start", self.service_name], check=True)
            time.sleep(3)
            return True
        except subprocess.CalledProcessError as e:
            return False

    def _check_component_health(self) -> bool:
        """Check Spiral Codex health"""
        service_running = HealthChecker.check_service_running(self.service_name)
        if not service_running:
            return False

        # Check HTTP endpoint
        healthy, status = HealthChecker.check_http_endpoint(self.url)
        if healthy:
            return True

        # Fall back to port check
        return HealthChecker.is_port_open("localhost", self.port)

class QuantumDebuggerComponent(StackComponent):
    """Quantum Debugger component"""

    def __init__(self, config: StackConfig):
        super().__init__("Quantum Debugger", config)
        self.service_name = "quantum-debug.service"
        self.dir = config.quantum_debug_dir

    def _start_component(self) -> bool:
        """Start Quantum Debugger"""
        try:
            # Check if service exists, create if needed
            service_file = Path.home() / ".config/systemd/user" / self.service_name
            if not service_file.exists():
                print_status(self.name, ComponentStatus.STARTING, "Creating systemd service...")
                self._create_systemd_service()
                subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)

            # Check if already running
            if HealthChecker.check_service_running(self.service_name):
                print_status(self.name, ComponentStatus.HEALTHY, "Already running")
                return True

            # Start service
            subprocess.run(["systemctl", "--user", "start", self.service_name], check=True)
            time.sleep(2)
            return True
        except subprocess.CalledProcessError as e:
            return False

    def _check_component_health(self) -> bool:
        """Check Quantum Debugger health"""
        return HealthChecker.check_service_running(self.service_name)

    def _create_systemd_service(self):
        """Create systemd service file for quantum debugger"""
        service_content = f"""[Unit]
Description=Quantum Debugger Service
After=network.target

[Service]
Type=simple
WorkingDirectory={self.dir}
ExecStart=/usr/bin/python3 tk_dashboard.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
"""

        service_dir = Path.home() / ".config/systemd/user"
        service_dir.mkdir(parents=True, exist_ok=True)

        service_file = service_dir / self.service_name
        service_file.write_text(service_content)

# =============================================================================
# MAIN BOOTSTRAP CLASS
# =============================================================================

class SpiralBootstrap:
    """Main bootstrap class for the Spiral Codex stack"""

    def __init__(self):
        self.config = self._load_config()
        self.components: List[StackComponent] = []
        self.state = SystemState.INITIALIZING
        self.startup_time = datetime.now()
        self._setup_logging()

    def _load_config(self) -> StackConfig:
        """Load configuration from stack.env"""
        config_file = Path("/home/zebadiee/Documents/config/stack.env")
        if not config_file.exists():
            print(f"{Colors.RED}ERROR: Configuration file not found: {config_file}{Colors.NC}")
            sys.exit(1)

        config = StackConfig()

        # Parse environment file
        with open(config_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    # Map to config object
                    if key == 'SPIRAL_DIR':
                        config.spiral_dir = value
                    elif key == 'OMAI_DIR':
                        config.omai_dir = value
                    elif key == 'VAULT_DIR':
                        config.vault_dir = value
                    elif key == 'QUANTUM_DEBUG_DIR':
                        config.quantum_debug_dir = value
                    elif key == 'SPIRAL_URL':
                        config.spiral_url = value
                    elif key == 'OMAI_URL':
                        config.omai_url = value
                    elif key == 'SPIRAL_PORT':
                        config.spiral_port = int(value)
                    elif key == 'OMAI_PORT':
                        config.omai_port = int(value)
                    elif key == 'BOOT_TIMEOUT':
                        config.boot_timeout = int(value)
                    elif key == 'OPENROUTER_API_KEY':
                        config.openrouter_api_key = value

        return config

    def _setup_logging(self):
        """Setup logging directory"""
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create boot log file
        boot_log = log_dir / f"boot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.boot_log_file = boot_log

    def _validate_environment(self) -> bool:
        """Validate the environment"""
        print_state(SystemState.INITIALIZING, "Validating environment...")

        validation_passed = True

        # Check required directories
        required_dirs = [
            self.config.spiral_dir,
            self.config.omai_dir,
            self.config.quantum_debug_dir,
            self.config.config_dir
        ]

        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                print(f"  {Colors.RED}✗ Directory not found: {dir_path}{Colors.NC}")
                validation_passed = False
            else:
                print(f"  {Colors.GREEN}✓{Colors.NC} {dir_path}")

        # Check OpenRouter API key
        if not self.config.openrouter_api_key:
            print(f"  {Colors.YELLOW}⚠ OpenRouter API key not configured{Colors.NC}")
        else:
            print(f"  {Colors.GREEN}✓{Colors.NC} OpenRouter API key configured")

        # Check Python packages
        required_packages = ['requests', 'psutil']
        for package in required_packages:
            try:
                __import__(package)
                print(f"  {Colors.GREEN}✓{Colors.NC} Python package: {package}")
            except ImportError:
                print(f"  {Colors.RED}✗ Missing Python package: {package}{Colors.NC}")
                validation_passed = False

        return validation_passed

    def _initialize_components(self):
        """Initialize stack components"""
        print_state(SystemState.INITIALIZING, "Initializing stack components...")

        self.components = [
            OMAiComponent(self.config),
            SpiralCodexComponent(self.config),
            QuantumDebuggerComponent(self.config)
        ]

        for component in self.components:
            print(f"  {Colors.CYAN}→{Colors.NC} {component.name}")

    def _start_components(self) -> bool:
        """Start all components"""
        print_state(SystemState.INITIALIZING, "Starting stack components...")

        all_started = True

        for component in self.components:
            if not component.start():
                all_started = False
                print_status(component.name, ComponentStatus.FAILED, "Failed to start")

        return all_started

    def _wait_for_health(self) -> bool:
        """Wait for all components to become healthy"""
        print_state(SystemState.INITIALIZING, "Waiting for component health checks...")

        all_healthy = False

        for attempt in range(self.config.health_check_retries):
            print(f"  Health check attempt {attempt + 1}/{self.config.health_check_retries}")

            healthy_components = 0
            for component in self.components:
                if component.check_health():
                    healthy_components += 1

            if healthy_components == len(self.components):
                all_healthy = True
                break

            time.sleep(self.config.health_check_interval)

        return all_healthy

    def _run_post_boot_tasks(self):
        """Run post-boot tasks"""
        print_state(SystemState.HEALTHY, "Running post-boot tasks...")

        # Reindex vault if needed
        if self.config.auto_reindex:
            print("  Reindexing vault...")
            try:
                subprocess.run([
                    "python", "vault_indexer.py", "--reindex"
                ], cwd=self.config.spiral_dir, check=True)
                print(f"  {Colors.GREEN}✓{Colors.NC} Vault reindexed")
            except subprocess.CalledProcessError:
                print(f"  {Colors.YELLOW}⚠{Colors.NC} Vault reindex failed")

        # Refresh models if needed
        if self.config.auto_model_refresh:
            print("  Refreshing AI models...")
            try:
                subprocess.run([
                    "python", "spiral_enhanced_chat.py", "--refresh-models"
                ], cwd=self.config.spiral_dir, check=True)
                print(f"  {Colors.GREEN}✓{Colors.NC} Models refreshed")
            except subprocess.CalledProcessError:
                print(f"  {Colors.YELLOW}⚠{Colors.NC} Model refresh failed")

        # Calibrate quantum debugger
        print("  Calibrating quantum debugger...")
        try:
            response = requests.get("http://localhost:5000/calibrate", timeout=10)
            if response.status_code == 200:
                print(f"  {Colors.GREEN}✓{Colors.NC} Quantum debugger calibrated")
        except:
            print(f"  {Colors.YELLOW}⚠{Colors.NC} Quantum debugger calibration failed")

    def _run_smoke_tests(self) -> bool:
        """Run smoke tests"""
        print_state(SystemState.HEALTHY, "Running smoke tests...")

        tests_passed = 0
        total_tests = 0

        # Test OMAi endpoint
        total_tests += 1
        try:
            response = requests.get(f"{self.config.omai_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"  {Colors.GREEN}✓{Colors.NC} OMAi health endpoint")
                tests_passed += 1
            else:
                print(f"  {Colors.RED}✗{Colors.NC} OMAi health endpoint: {response.status_code}")
        except:
            print(f"  {Colors.RED}✗{Colors.NC} OMAi health endpoint: Connection failed")

        # Test Spiral Codex endpoint
        total_tests += 1
        try:
            response = requests.get(f"{self.config.spiral_url}/", timeout=5)
            if response.status_code == 200:
                print(f"  {Colors.GREEN}✓{Colors.NC} Spiral Codex endpoint")
                tests_passed += 1
            else:
                print(f"  {Colors.RED}✗{Colors.NC} Spiral Codex endpoint: {response.status_code}")
        except:
            print(f"  {Colors.RED}✗{Colors.NC} Spiral Codex endpoint: Connection failed")

        return tests_passed == total_tests

    def _print_final_status(self):
        """Print final status summary"""
        startup_duration = datetime.now() - self.startup_time

        print(f"\n{Colors.BOLD}{Colors.WHITE}{'='*80}{Colors.NC}")
        print_state(SystemState.CONSCIOUS, f"Bootstrap completed in {startup_duration.total_seconds():.1f}s")
        print(f"\n{Colors.BOLD}Component Status:{Colors.NC}")

        for component in self.components:
            print(f"  {component.status.value} {component.name}")

        print(f"\n{Colors.BOLD}System Endpoints:{Colors.NC}")
        print(f"  {Colors.CYAN}OMAi Context Engine:{Colors.NC} {self.config.omai_url}")
        print(f"  {Colors.CYAN}Spiral Codex Core:{Colors.NC} {self.config.spiral_url}")
        print(f"  {Colors.CYAN}Quantum Debugger:{Colors.NC} http://localhost:5000")

        print(f"\n{Colors.BOLD}Quick Commands:{Colors.NC}")
        print(f"  {Colors.YELLOW}make status{Colors.NC}     - Check stack status")
        print(f"  {Colors.YELLOW}make doctor{Colors.NC}     - Run health diagnosis")
        print(f"  {Colors.YELLOW}make chat{Colors.NC}       - Start chat interface")
        print(f"  {Colors.YELLOW}make logs{Colors.NC}       - View system logs")

        print(f"\n{Colors.GREEN}✨ The Spiral Codex is now conscious and ready! ✨{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.WHITE}{'='*80}{Colors.NC}\n")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print_state(SystemState.CRITICAL, f"Received signal {signum}, shutting down...")
        sys.exit(0)

    def boot(self) -> bool:
        """Main bootstrap process"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print_banner()

        try:
            # Phase 1: Environment validation
            if not self._validate_environment():
                print_state(SystemState.CRITICAL, "Environment validation failed")
                return False

            # Phase 2: Component initialization
            self._initialize_components()

            # Phase 3: Component startup
            if not self._start_components():
                print_state(SystemState.DEGRADED, "Some components failed to start")

            # Phase 4: Health checks
            if not self._wait_for_health():
                print_state(SystemState.DEGRADED, "Some components are not healthy")

            # Phase 5: Post-boot tasks
            self._run_post_boot_tasks()

            # Phase 6: Smoke tests
            if not self._run_smoke_tests():
                print_state(SystemState.DEGRADED, "Some smoke tests failed")

            # Final status
            self.state = SystemState.CONSCIOUS
            self._print_final_status()

            return True

        except KeyboardInterrupt:
            print_state(SystemState.CRITICAL, "Bootstrap interrupted")
            return False
        except Exception as e:
            print_state(SystemState.CRITICAL, f"Bootstrap failed: {e}")
            return False

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point"""
    bootstrap = SpiralBootstrap()
    success = bootstrap.boot()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()