#!/usr/bin/env python3
"""
Claude Code Launcher

A Python application that:
1. Checks if Claude is installed, and installs it if not
2. Updates Claude
3. Manages settings.local.json configuration
4. Provides an interactive TUI for configuring environment variables for LLM runtime
5. Launches Claude in a new window

Supports: Windows, WSL, Linux, macOS
"""

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

# Initialize console for rich output
console = Console()

# ============================================================================
# Constants and Configuration
# ============================================================================

# LLM Runtime configurations
LLM_RUNTIME_OLLAMA = "ollama"
LLM_RUNTIME_VLLM = "vllm"
LLM_RUNTIME_MLX = "mlx"

# Default ports for each runtime
DEFAULT_PORTS = {
    LLM_RUNTIME_OLLAMA: 11434,
    LLM_RUNTIME_VLLM: 8000,
    LLM_RUNTIME_MLX: 8080,
}

# Environment variable defaults for each runtime
# Note: URLs should not include /v1 suffix - it will be added by the application when making API calls
RUNTIME_ENV_DEFAULTS = {
    LLM_RUNTIME_OLLAMA: {
        "ANTHROPIC_BASE_URL": "http://localhost:11434",
        "ANTHROPIC_AUTH_TOKEN": "",
        "ANTHROPIC_API_KEY": "not-needed",
    },
    LLM_RUNTIME_VLLM: {
        "ANTHROPIC_BASE_URL": "http://localhost:8000/v1",
        "ANTHROPIC_AUTH_TOKEN": "",
        "ANTHROPIC_API_KEY": "not-needed",
    },
    LLM_RUNTIME_MLX: {
        "ANTHROPIC_BASE_URL": "http://localhost:8080/v1",
        "ANTHROPIC_AUTH_TOKEN": "",
        "ANTHROPIC_API_KEY": "not-needed",
    },
}

# Claude configuration paths
CLAUDE_CONFIG_DIR = ".claude"
SETTINGS_LOCAL_JSON = "settings.local.json"

# Supported platforms
PLATFORM_WINDOWS = "windows"
PLATFORM_DARWIN = "darwin"
PLATFORM_LINUX = "linux"
PLATFORM_WSL = "wsl"


# ============================================================================
# Platform Detection
# ============================================================================

def get_platform() -> str:
    """Detect the current platform (Windows, Darwin, Linux, or WSL)."""
    if sys.platform == "win32":
        return PLATFORM_WINDOWS
    elif sys.platform == "darwin":
        return PLATFORM_DARWIN
    elif "microsoft" in sys.version.lower() or os.path.exists("/proc/version"):
        # Check for WSL
        try:
            with open("/proc/version", "r") as f:
                content = f.read().lower()
                if "microsoft" in content:
                    return PLATFORM_WSL
        except Exception:
            pass
        return PLATFORM_LINUX
    return PLATFORM_LINUX


def get_platform_name() -> str:
    """Get a user-friendly platform name."""
    platform = get_platform()
    platform_names = {
        PLATFORM_WINDOWS: "Windows",
        PLATFORM_DARWIN: "macOS",
        PLATFORM_LINUX: "Linux",
        PLATFORM_WSL: "WSL",
    }
    return platform_names.get(platform, "Unknown")


# ============================================================================
# Installation Scripts
# ============================================================================

def get_script_path(script_name: str) -> Path:
    """Get the full path to an installation script."""
    script_dir = Path(__file__).parent
    return script_dir / script_name


def check_claude_installed() -> bool:
    """Check if Claude is installed and available in PATH."""
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def run_install_script() -> bool:
    """Run the OS-specific installation script."""
    platform = get_platform()
    script_name = ""

    if platform == PLATFORM_WINDOWS:
        # Try PowerShell first, then CMD
        ps_script = get_script_path("install.ps1")
        if ps_script.exists():
            try:
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                console.print(Panel.fit("[green]Installation completed successfully[/green]"))
                return True
            except subprocess.CalledProcessError as e:
                console.print(Panel.fit(f"[yellow]PowerShell installation failed: {e}[/yellow]"))
                # Fall back to CMD
        cmd_script = get_script_path("install.cmd")
        if cmd_script.exists():
            try:
                result = subprocess.run(
                    ["cmd", "/c", str(cmd_script)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                console.print(Panel.fit("[green]Installation completed successfully[/green]"))
                return True
            except subprocess.CalledProcessError as e:
                console.print(Panel.fit(f"[red]CMD installation also failed: {e}[/red]"))
                return False
        return False
    else:
        # Unix-like systems (Linux, macOS, WSL)
        sh_script = get_script_path("install.sh")
        if sh_script.exists():
            try:
                result = subprocess.run(
                    ["bash", str(sh_script)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                console.print(Panel.fit("[green]Installation completed successfully[/green]"))
                return True
            except subprocess.CalledProcessError as e:
                console.print(Panel.fit(f"[red]Installation failed: {e}[/red]"))
                return False
        return False


def update_claude() -> bool:
    """Update Claude to the latest version."""
    try:
        result = subprocess.run(
            ["claude", "update"],
            check=True,
            capture_output=True,
            text=True
        )
        console.print(Panel.fit("[green]Claude updated successfully[/green]"))
        console.print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        console.print(Panel.fit(f"[red]Failed to update Claude: {e}[/red]"))
        console.print(e.stderr)
        return False


# ============================================================================
# Settings Management
# ============================================================================

def get_settings_paths() -> list[Path]:
    """Get all possible settings file paths (OS-specific)."""
    cwd = Path.cwd()
    if get_platform() == PLATFORM_WINDOWS:
        return [
            cwd / CLAUDE_CONFIG_DIR / SETTINGS_LOCAL_JSON,
            cwd / ".claude" / SETTINGS_LOCAL_JSON,
        ]
    else:
        return [
            cwd / CLAUDE_CONFIG_DIR / SETTINGS_LOCAL_JSON,
            cwd / ".claude" / SETTINGS_LOCAL_JSON,
        ]


def find_or_create_settings() -> Path:
    """Find existing settings file or create a new one."""
    paths = get_settings_paths()
    for path in paths:
        if path.exists():
            return path

    # Create the .claude directory if it doesn't exist
    config_dir = paths[0].parent
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create empty settings file
    with open(paths[0], "w") as f:
        json.dump({"env": {}}, f, indent=2)

    return paths[0]


def load_settings(path: Path | None = None) -> dict[str, Any]:
    """Load settings from file."""
    if path is None:
        path = find_or_create_settings()

    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        console.print(Panel.fit(f"[yellow]Warning: Could not load settings: {e}[/yellow]"))
        return {"env": {}}


def save_settings(data: dict[str, Any], path: Path | None = None) -> bool:
    """Save settings to file."""
    if path is None:
        path = find_or_create_settings()

    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        console.print(Panel.fit(f"[red]Failed to save settings: {e}[/red]"))
        return False


# ============================================================================
# LLM Runtime and Model Management
# ============================================================================

@dataclass
class AvailableModel:
    """Represents an available LLM model."""
    name: str
    provider: str


class LLMRuntimeManager:
    """Manages LLM runtime configuration and model fetching."""

    def __init__(self, runtime: str, base_url: str, api_key: str | None = None):
        self.runtime = runtime
        # Strip trailing slashes from base URL
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""

    def _make_request(self, endpoint: str) -> dict | list | None:
        """Make HTTP request to LLM runtime API."""
        import urllib.request
        import urllib.error

        url = f"{self.base_url}{endpoint}"
        headers = {}

        if self.api_key and self.api_key != "not-needed":
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            console.print(Panel.fit(f"[yellow]Warning: HTTP Error {e.code} connecting to {self.runtime}: {e}[/yellow]"))
            return None
        except urllib.error.URLError as e:
            console.print(Panel.fit(f"[yellow]Warning: Could not connect to {self.runtime}: {e}[/yellow]"))
            return None
        except json.JSONDecodeError as e:
            console.print(Panel.fit(f"[yellow]Warning: Could not parse response from {self.runtime}: {e}[/yellow]"))
            return None

    def fetch_models(self) -> list[AvailableModel]:
        """Fetch available models from the LLM runtime."""
        models: list[AvailableModel] = []

        if self.runtime == LLM_RUNTIME_OLLAMA:
            # Ollama API: GET /api/tags
            # Response: {"models": [{"name": "model-name"}, ...]}
            result = self._make_request("/api/tags")
            if result and "models" in result:
                for model in result["models"]:
                    name = model.get("name", "")
                    if name:
                        models.append(AvailableModel(name=name, provider="ollama"))

        elif self.runtime == LLM_RUNTIME_VLLM:
            # vLLM API: GET /v1/models (OpenAI-compatible)
            # Response: {"object": "list", "data": [{"id": "model-id", ...}]}
            result = self._make_request("/v1/models")
            if result and "data" in result:
                for model in result["data"]:
                    name = model.get("id", "")
                    if name:
                        models.append(AvailableModel(name=name, provider="vllm"))

        elif self.runtime == LLM_RUNTIME_MLX:
            # mlx LM API: GET /v1/models (OpenAI-compatible)
            # Response: {"object": "list", "data": [{"id": "model-id", ...}]}
            result = self._make_request("/v1/models")
            if result and "data" in result:
                for model in result["data"]:
                    name = model.get("id", "")
                    if name:
                        models.append(AvailableModel(name=name, provider="mlx"))

        return models


# ============================================================================
# Interactive Selection using Rich (proper terminal rendering)
# ============================================================================

def select_option(options: list[str], prompt: str = "Select an option:") -> str:
    """Select an option from a list using arrow keys.

    Uses rich's console rendering for proper alignment and terminal handling.
    """
    from rich.prompt import Prompt

    # For interactive selection with arrow keys, we use a simple prompt-based approach
    # since rich doesn't have a built-in interactive list selector with arrow keys
    # in the prompt module. We'll use a numbered list approach.

    console.print(prompt)
    for i, option in enumerate(options, 1):
        console.print(f"  [bold]{i}[/bold]. {option}")

    console.print()

    while True:
        response = Prompt.ask(
            "Enter choice (number)",
            choices=[str(i) for i in range(1, len(options) + 1)],
            show_choices=True
        )
        return options[int(response) - 1]


def confirm(prompt: str = "Continue?") -> bool:
    """Confirm an action with yes/no."""
    return Confirm.ask(prompt)


# ============================================================================
# Environment Variable Configuration
# ============================================================================

def configure_env_vars(current_env: dict[str, str] | None = None) -> dict[str, str]:
    """Configure environment variables for LLM runtime."""
    if current_env is None:
        current_env = {}

    env = current_env.copy()

    # 1. Select LLM Runtime
    console.print(Panel.fit("[bold]LLM Runtime Configuration[/bold]"))
    console.print()

    runtime_options = [LLM_RUNTIME_OLLAMA, LLM_RUNTIME_VLLM, LLM_RUNTIME_MLX]
    runtime = select_option(
        runtime_options,
        prompt="Select LLM Runtime Server:"
    )

    # 2. Get base URL
    default_port = DEFAULT_PORTS.get(runtime, 8000)
    default_url = RUNTIME_ENV_DEFAULTS.get(runtime, {}).get("ANTHROPIC_BASE_URL", f"http://your-llm-runtime:{default_port}")

    base_url = Prompt.ask(
        "Enter ANTHROPIC_BASE_URL",
        default=default_url
    )

    env["ANTHROPIC_BASE_URL"] = base_url

    # 3. Get auth token (optional)
    auth_token = Prompt.ask(
        "Enter ANTHROPIC_AUTH_TOKEN (press Enter to skip)",
        default="",
        show_default=False
    )
    if auth_token:
        env["ANTHROPIC_AUTH_TOKEN"] = auth_token
    elif "ANTHROPIC_AUTH_TOKEN" in env:
        del env["ANTHROPIC_AUTH_TOKEN"]

    # 4. Get API key (optional)
    api_key = Prompt.ask(
        "Enter ANTHROPIC_API_KEY (press Enter to skip)",
        default="",
        show_default=False
    )
    if api_key:
        env["ANTHROPIC_API_KEY"] = api_key
    elif "ANTHROPIC_API_KEY" in env:
        del env["ANTHROPIC_API_KEY"]

    # 5. Fetch and select models
    console.print()
    console.print(Panel.fit("[bold]Model Selection[/bold]"))
    console.print("Fetching available models...")

    manager = LLMRuntimeManager(
        runtime=runtime,
        base_url=base_url,
        api_key=api_key if api_key else None
    )

    models = manager.fetch_models()

    if models:
        console.print(Panel.fit(f"Found [green]{len(models)}[/green] models"))

        # Display models in a table
        table = Table(title="Available Models")
        table.add_column("Name", style="cyan")
        table.add_column("Provider", style="magenta")

        for model in models:
            table.add_row(model.name, model.provider)

        console.print(table)

        # Create model selector using numbered list
        model_names = [m.name for m in models]
        opus_model = select_option(
            model_names,
            prompt="Select ANTHROPIC_DEFAULT_OPUS_MODEL:"
        )
        env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = opus_model

        sonnet_model = select_option(
            model_names,
            prompt="Select ANTHROPIC_DEFAULT_SONNET_MODEL:"
        )
        env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = sonnet_model

        haiku_model = select_option(
            model_names,
            prompt="Select ANTHROPIC_DEFAULT_HAIKU_MODEL:"
        )
        env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = haiku_model
    else:
        console.print(Panel.fit("[yellow]No models found. You can configure models manually.[/yellow]"))
        for model_type in ["OPUS", "SONNET", "HAIKU"]:
            model_name = Prompt.ask(f"Enter ANTHROPIC_DEFAULT_{model_type}_MODEL")
            env[f"ANTHROPIC_DEFAULT_{model_type}_MODEL"] = model_name

    # 6. Set Claude disable traffic flag
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    # 7. Ask to review and confirm
    console.print()
    console.print(Panel.fit("[bold]Configuration Summary[/bold]"))
    config_table = Table(title="Environment Variables")
    config_table.add_column("Variable", style="cyan")
    config_table.add_column("Value", style="green")

    for key, value in sorted(env.items()):
        if key.startswith("ANTHROPIC_") or key == "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC":
            display_value = value if not key.endswith("_TOKEN") and not key.endswith("_KEY") else "***"
            config_table.add_row(key, display_value)

    console.print(config_table)

    if not confirm("Save this configuration?"):
        console.print("[yellow]Configuration cancelled.[/yellow]")
        return current_env

    return env


# ============================================================================
# Claude Launch
# ============================================================================

def launch_claude() -> bool:
    """Launch Claude in a new window."""
    platform = get_platform()

    try:
        cwd = Path.cwd()
        claude_cmd = "claude.exe" if platform == PLATFORM_WINDOWS else "claude"
        if platform == PLATFORM_WINDOWS:
            # On Windows, use 'start' to launch in new window, cd to current directory
            subprocess.Popen(
                ["start", "cmd", "/k", f"cd /d \"{cwd}\" && {claude_cmd}"],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif platform == PLATFORM_DARWIN:
            # On macOS, use osascript to open a new Terminal tab/window and cd to cwd
            script = f'tell app "Terminal" to do script "cd \\"{cwd}\\" && claude"'
            subprocess.Popen(
                ["osascript", "-e", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif platform == PLATFORM_LINUX or platform == PLATFORM_WSL:
            # On Linux/WSL, try to find a terminal emulator with working directory
            # Note: WSL uses Linux binaries, not .exe
            terminals = [
                ["gnome-terminal", "--", "bash", "-c", f"cd '{cwd}' && claude; exec bash"],
                ["konsole", "--workdir", str(cwd), "-e", "bash", "-c", "claude; exec bash"],
                ["xterm", "-e", "bash", "-c", f"cd '{cwd}' && claude; exec bash"],
                ["alacritty", "-e", "bash", "-c", f"cd '{cwd}' && claude; exec bash"],
                ["terminator", "-e", "bash", "-c", f"cd '{cwd}' && claude; exec bash"],
            ]

            launched = False
            for term in terminals:
                try:
                    subprocess.Popen(
                        term,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                    launched = True
                    break
                except (FileNotFoundError, OSError):
                    continue

            if not launched:
                # Fallback: just run in background
                subprocess.Popen(
                    ["claude"],
                    cwd=str(cwd),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
        else:
            # Generic fallback
            subprocess.Popen(
                ["claude"],
                cwd=str(cwd),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

        console.print(Panel.fit("[green]Claude is launching in a new window...[/green]"))
        console.print("[dim]This launcher will now exit.[/dim]")
        return True

    except Exception as e:
        console.print(Panel.fit(f"[red]Failed to launch Claude: {e}[/red]"))
        return False


# ============================================================================
# Main Application
# ============================================================================

def main() -> None:
    """Main entry point for the Claude Code Launcher."""
    console.print(Panel.fit(
        "[bold cyan]Claude Code Launcher[/bold cyan]\n"
        f"Platform: [bold]{get_platform_name()}[/bold]",
        subtitle="v1.0.0"
    ))
    console.print()

    # Step 1: Check if Claude is installed
    console.print("[bold]Step 1: Checking Claude installation...[/bold]")
    if not check_claude_installed():
        console.print(Panel.fit(
            "[yellow]Claude is not installed. Running installation...[/yellow]"
        ))

        # Step 2: Run installation
        console.print("[bold]Step 2: Installing Claude...[/bold]")
        if not run_install_script():
            console.print(Panel.fit(
                "[red]Installation failed. Please install Claude manually and try again.[/red]"
            ))
            raise typer.Exit(code=1)
    else:
        console.print(Panel.fit("[green]Claude is already installed.[/green]"))

    # Step 3: Update Claude
    console.print()
    console.print("[bold]Step 3: Updating Claude...[/bold]")
    if not update_claude():
        if not confirm("Continue anyway?"):
            raise typer.Exit(code=1)

    # Step 4: Find or create settings
    console.print()
    console.print("[bold]Step 4: Managing settings...[/bold]")
    settings_path = find_or_create_settings()
    console.print(f"[dim]Settings file: {settings_path}[/dim]")

    # Step 5 & 6: Load and configure environment variables
    console.print()
    console.print("[bold]Step 5-6: Configuring environment variables...[/bold]")

    settings = load_settings(settings_path)
    current_env = settings.get("env", {})

    if not current_env:
        console.print("[dim]No environment configuration found. Starting configuration...[/dim]")
        new_env = configure_env_vars({})
    else:
        console.print("[dim]Found existing environment configuration.[/dim]")
        if confirm("Would you like to modify the configuration?"):
            new_env = configure_env_vars(current_env)
        else:
            new_env = current_env

    # Save settings
    settings["env"] = new_env
    if not save_settings(settings, settings_path):
        console.print(Panel.fit("[red]Failed to save settings.[/red]"))
        raise typer.Exit(code=1)

    console.print(Panel.fit("[green]Configuration saved successfully![/green]"))

    # Step 7: Launch Claude
    console.print()
    console.print("[bold]Step 7: Launching Claude...[/bold]")
    if launch_claude():
        console.print()
        console.print("[dim]Thank you for using Claude Code Launcher![/dim]")
        raise typer.Exit(code=0)
    else:
        console.print(Panel.fit("[red]Launch failed![/red]"))
        raise typer.Exit(code=1)


app = typer.Typer(
    name="claude-launcher",
    help="Claude Code Launcher - Install, update, configure, and launch Claude Code",
    add_completion=False,
)


@app.command()
def install() -> None:
    """Run the installation script."""
    console.print(Panel.fit("[bold]Installing Claude Code[/bold]"))
    if run_install_script():
        console.print("[green]Installation completed![/green]")
    else:
        raise typer.Exit(code=1)


@app.command()
def update() -> None:
    """Update Claude to the latest version."""
    console.print(Panel.fit("[bold]Updating Claude Code[/bold]"))
    if update_claude():
        console.print("[green]Update completed![/green]")
    else:
        raise typer.Exit(code=1)


@app.command()
def configure() -> None:
    """Configure environment variables for LLM runtime."""
    console.print(Panel.fit("[bold]Configure Claude Environment[/bold]"))

    settings_path = find_or_create_settings()
    settings = load_settings(settings_path)

    current_env = settings.get("env", {})
    new_env = configure_env_vars(current_env)

    settings["env"] = new_env
    if save_settings(settings, settings_path):
        console.print("[green]Configuration saved![/green]")
    else:
        raise typer.Exit(code=1)


@app.command()
def launch() -> None:
    """Launch Claude in a new window."""
    console.print(Panel.fit("[bold]Launch Claude Code[/bold]"))

    if check_claude_installed():
        launch_claude()
    else:
        console.print(Panel.fit(
            "[yellow]Claude is not installed. Please run 'install' first.[/yellow]"
        ))
        raise typer.Exit(code=1)


@app.command()
def info() -> None:
    """Display system and installation information."""
    platform = get_platform()
    platform_name = get_platform_name()
    is_installed = check_claude_installed()

    table = Table(title="System Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Platform", platform_name)
    table.add_row("Platform ID", platform)
    table.add_row("Python Version", sys.version.split()[0])
    table.add_row("Claude Installed", "Yes" if is_installed else "No")

    if is_installed:
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            table.add_row("Claude Version", result.stdout.strip())
        except Exception:
            table.add_row("Claude Version", "Unknown")

    console.print(table)


@app.command()
def test_models(
    runtime: str = typer.Option(LLM_RUNTIME_OLLAMA, "--runtime", "-r", help="LLM runtime to test"),
    base_url: str = typer.Option(None, "--url", "-u", help="Base URL for the LLM runtime"),
) -> None:
    """Test connection to an LLM runtime and list available models."""
    console.print(Panel.fit(f"[bold]Testing {runtime} Connection[/bold]"))

    if base_url is None:
        default_port = DEFAULT_PORTS.get(runtime, 8000)
        base_url = f"http://localhost:{default_port}"

    console.print(f"[dim]Base URL: {base_url}[/dim]")

    manager = LLMRuntimeManager(runtime=runtime, base_url=base_url)
    models = manager.fetch_models()

    if models:
        table = Table(title=f"Found {len(models)} models")
        table.add_column("Name", style="cyan")
        table.add_column("Provider", style="magenta")

        for model in models[:20]:  # Limit to first 20
            table.add_row(model.name, model.provider)

        if len(models) > 20:
            table.add_row(f"... and {len(models) - 20} more", "")

        console.print(table)
    else:
        console.print(Panel.fit("[yellow]No models found or unable to connect.[/yellow]"))


if __name__ == "__main__":
    main()
