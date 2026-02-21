#!/usr/bin/env python3
"""
Claude Code Launcher

A Python application that:
1. Checks if Claude is installed, and installs it if not
2. Updates Claude
3. Manages settings.local.json configuration
4. Provides an interactive TUI for configuring environment variables for LLM runtime
5. Launches Claude in the current terminal process

Supports: Windows, WSL, Linux, macOS

Note: Claude runs in the current process (not a new terminal), making it work seamlessly
in SSH sessions, local terminals, and other interactive environments.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from rich.live import Live

PANEL_WIDTH = 640

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

def get_claude_executable_name() -> str:
    """Return the appropriate Claude executable name for the current platform."""
    platform = get_platform()
    if platform == PLATFORM_WINDOWS:
        return "claude.exe"
    return "claude"

# ============================================================================
# Installation Scripts
# ============================================================================

def get_script_path(script_name: str) -> Path:
    """Get the full path to an installation script."""
    script_dir = Path(__file__).parent
    return script_dir / script_name


def check_claude_installed() -> bool:
    """Check if Claude is installed and available in PATH."""
    return run_subprocess_with_spinner(
        ["claude", "--version"],
        spinner_text="Checking if Claude is installed..."
    )


def run_install_script() -> bool:
    """Run the OS-specific installation script."""
    platform = get_platform()

    if platform == PLATFORM_WINDOWS:
        # Try PowerShell first, then CMD
        ps_script = get_script_path("install.ps1")
        if ps_script.exists():
            return run_subprocess_with_spinner(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)],
                spinner_text="Installing Claude with PowerShell..."
            )
        cmd_script = get_script_path("install.cmd")
        if cmd_script.exists():
            return run_subprocess_with_spinner(
                ["cmd", "/c", str(cmd_script)],
                spinner_text="Installing Claude with CMD..."
            )
        return False
    else:
        # Unix-like systems (Linux, macOS, WSL)
        sh_script = get_script_path("install.sh")
        if sh_script.exists():
            return run_subprocess_with_spinner(
                ["bash", str(sh_script)],
                spinner_text="Installing Claude with Shell Script..."
            )
        return False

class SpinnerlessStatus:
    """
    console.status() 대신 사용하는 커스텀 상태 표시기.
    스피너는 1개만 (내부 Panel에 포함된 것), 중복 없음.
    """
    def __init__(self, console, panel):
        self.console = console
        self.panel = panel
        self.live = Live(panel, console=console, refresh_per_second=10, transient=True)

    def start(self):
        self.live.start()

    def stop(self):
        self.live.stop()

    def update_text(self, text: str):
        """Panel 안의 Spinner 텍스트만 변경"""
        self.panel.renderable.text = Text(text, style="bold cyan")
        self.live.update(self.panel)

    def update_subtitle(self, subtitle: str):
        """Panel subtitle 변경"""
        self.panel.subtitle = subtitle
        self.live.update(self.panel)

def run_subprocess_with_spinner(command: list[str], spinner_text: str, timeout: int = 120) -> bool:
    """Run a subprocess command while displaying a spinner with the given text."""
    text = Text.from_markup(spinner_text)
    panel = Panel.fit(
        Spinner("dots", text=text),
        subtitle="Please wait...",
        width=PANEL_WIDTH,
        border_style="green",
        subtitle_align="right",
        padding=(1, 2),
    )

    status = SpinnerlessStatus(console, panel)
    status.start()

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        status.stop()
        return True
    except FileNotFoundError:
        status.stop()
        return False
    except subprocess.CalledProcessError as e:
        status.stop()
        return False
    except subprocess.TimeoutExpired:
        status.stop()
        return False


def update_claude() -> bool:
    """Update Claude to the latest version."""
    return run_subprocess_with_spinner(
        [get_claude_executable_name(), "update"],
        spinner_text="Updating Claude..."
    )


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
            text = Text.from_markup(f"[yellow]Warning: HTTP Error {e.code} connecting to {self.runtime}: {e}[/yellow]")
            console.print(create_panel(text))
            return None
        except urllib.error.URLError as e:
            text = Text.from_markup(f"[yellow]Warning: Could not connect to {self.runtime}: {e}[/yellow]")
            console.print(create_panel(text))
            return None
        except json.JSONDecodeError as e:
            text = Text.from_markup(f"[yellow]Warning: Could not parse response from {self.runtime}: {e}[/yellow]")
            console.print(create_panel(text))
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

    Uses rich's console rendering with Panel.fit for a clean, boxed interface.
    """
    from rich.prompt import Prompt

    # Build the options list as a Rich Text/Panel content
    options_text = Text()
    for i, option in enumerate(options, 1):
        newline = "\n" if i < len(options) else ""
        options_text.append(f"  {i}. ", style="bold")
        options_text.append(f"{option}{newline}")

    # Create a panel for the options
    options_panel = create_panel(options_text)
    console.print(options_panel)

    while True:
        response = Prompt.ask(
            prompt,
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

    manager = LLMRuntimeManager(
        runtime=runtime,
        base_url=base_url,
        api_key=api_key if api_key else None
    )

    models = manager.fetch_models()

    if models:
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
        text = Text.from_markup("[yellow]No models found. You can configure models manually.[/yellow]")
        console.print(create_panel(text))
        for model_type in ["OPUS", "SONNET", "HAIKU"]:
            model_name = Prompt.ask(f"Enter ANTHROPIC_DEFAULT_{model_type}_MODEL")
            env[f"ANTHROPIC_DEFAULT_{model_type}_MODEL"] = model_name

    # 6. Set Claude disable traffic flag
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    # 7. Ask to review and confirm
    console.print(claude_code_display_settings_panel(env, subtitle="Configuration Summary"))

    if not confirm("Save this configuration?"):
        console.print("[yellow]Configuration cancelled.[/yellow]")
        return current_env

    return env


# ============================================================================
# Claude Launch
# ============================================================================

def launch_claude() -> bool:
    """Launch Claude in the current terminal process.

    Claude runs directly in the current process, allowing it to work seamlessly
    in SSH sessions, local terminals, and other interactive environments.
    The launcher will exit after launching Claude to avoid interfering with
    Claude's input/output handling.
    """
    try:
        cwd = Path.cwd()
        claude_cmd = get_claude_executable_name()

        # Load the environment settings from config file
        settings_path = find_or_create_settings()
        settings = load_settings(settings_path)
        env_vars = settings.get("env", {})

        # Build environment with Claude settings
        env = os.environ.copy()
        env.update(env_vars)

        # Run Claude in the current process with configured environment
        result = subprocess.run(
            [claude_cmd],
            cwd=str(cwd),
            env=env,
        )

        return result.returncode == 0

    except FileNotFoundError:
        text = Text.from_markup("[red]Claude executable not found. Please install Claude first.[/red]")
        console.print(create_panel(text))
        return False
    except Exception as e:
        text = Text.from_markup(f"[red]Failed to launch Claude: {e}[/red]")
        console.print(create_panel(text))
        return False


# ============================================================================
# Panel Helpers - Factory Pattern
# ============================================================================
def create_panel(renderable: Text | Table, subtitle: str = "", title: str = "") -> Panel:
    """Factory function to create consistent panels with the launcher style."""
    return Panel.fit(
        renderable,
        title=title,
        subtitle=subtitle,
        width=PANEL_WIDTH,
        subtitle_align="right",
        padding=(1, 2)
    )


def claude_code_launcher_info_panel() -> Panel:
    """Return a formatted panel for the Claude Code Launcher."""
    text = Text.from_markup(
        "[bold cyan]Claude Code Launcher[/bold cyan]\n"
        f"Platform: [bold]{get_platform_name()}[/bold]"
    )
    return create_panel(text, subtitle="v1.0.0")


def claude_code_install_panel() -> Panel:
    """Return a formatted panel for the installation step."""
    if not check_claude_installed():
        # Run installation
        if not run_install_script():
            text = Text.from_markup(
                "[red]Installation failed. Please install Claude manually and try again.[/red]"
            )
            return create_panel(text, subtitle="Installing Claude Code")
        else:
            text = Text.from_markup(
                "[green]Claude installed successfully![/green]"
            )
            return create_panel(text, subtitle="Installing Claude Code")
    else:
        text = Text.from_markup(
            "[green]Claude is already installed.[/green]"
        )
        return create_panel(text, subtitle="Installing Claude Code")

def claude_code_update_panel() -> Panel:
    """Return a formatted panel for the update step."""
    if  update_claude():
        text = Text.from_markup(
            "[green]Claude updated successfully![/green]"
        )
        return create_panel(text, subtitle="Updating Claude Code")
    else:
        text = Text.from_markup(
            "[yellow]Failed to update Claude. You can continue with the existing version or try updating manually.[/yellow]"
        )
        return create_panel(text, subtitle="Updating Claude Code")


def claude_code_display_settings_panel(env: dict[str, str], subtitle: str) -> Panel:
    """Return a formatted panel displaying current environment variable settings."""
    table = Table(title="Environment Variable Settings")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="green")

    for key, value in sorted(env.items()):
        display_value = value if not key.endswith("_TOKEN") and not key.endswith("_KEY") else "***"
        table.add_row(key, display_value)

    return create_panel(table, subtitle=subtitle)

def claude_code_settings_table_panel() -> Panel:
    """Return a formatted panel with a table of current settings."""
    settings_path = find_or_create_settings()
    settings = load_settings(settings_path)

    env = settings.get("env", {})

    if not env:
        new_env = configure_env_vars({})
    else:
        console.print(claude_code_display_settings_panel(env, subtitle="Current Configuration"))
        if confirm("Would you like to modify the configuration?"):
            new_env = configure_env_vars(env)
        else:
            new_env = env

    # Save settings
    settings["env"] = new_env
    if not save_settings(settings, settings_path):
        text = Text.from_markup("[red]Failed to save settings.[/red]")
        return create_panel(text, subtitle="Settings Management")
    text = Text.from_markup("[green]Configuration saved successfully![/green]")
    return create_panel(text, subtitle="Settings Management")
    
# ============================================================================
# Main Application
# ============================================================================

def main() -> None:
    """Main entry point for the Claude Code Launcher."""
    console.print(claude_code_launcher_info_panel())

    # Check if Claude is installed
    console.print(claude_code_install_panel())
    if not check_claude_installed():
        raise typer.Exit(code=1)

    # Update Claude
    console.print(claude_code_update_panel())

    # Display and configure settings
    console.print(claude_code_settings_table_panel())

    # Launch Claude in current terminal
    console.print("[bold]Launching Claude...[/bold]")
    if not launch_claude():
        text = Text.from_markup("[red]Launch failed![/red]")
        console.print(create_panel(text))
        raise typer.Exit(code=1)


app = typer.Typer(
    name="claude-launcher",
    help="Claude Code Launcher - Install, update, configure, and launch Claude Code in current terminal",
    add_completion=False,
)


if __name__ == "__main__":
    main()
