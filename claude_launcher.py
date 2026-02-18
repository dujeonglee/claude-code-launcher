#!/usr/bin/env python3
"""
Claude Code Launcher - Simple Config & Launch
==============================================
Generates a shell script to run Claude Code with on-premise LLM settings
and launches it in a new terminal window.

Features:
- Automatic OS and architecture detection
- Claude Code version checking and automatic updates
- GUI-based installation management
"""

import sys
import os
import stat
import time
import shutil
import subprocess
# json import removed - not used
import re
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
# datetime import removed - datetime.datetime not used

import yaml
import requests

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QGroupBox, QFormLayout,
    QStatusBar, QMessageBox, QFileDialog, QScrollArea, QPlainTextEdit,
    QSpinBox, QProgressBar,
)
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QFont, QFontDatabase


# ============================================================================
# Constants
# ============================================================================

# Claude Code download base URL pattern
# Format: {base_url}/{version}/{platform}/claude
# Platform examples: darwin-arm64, darwin-amd64, linux-arm64, linux-amd64, linux-arm64-musl, etc.
CLAUDE_DOWNLOAD_BASE = "https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases"

# CHANGELOG URL for fetching latest version
CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Download platform names by OS and architecture
# Platform format varies by OS:
#   - macOS: darwin-x64, darwin-arm64
#   - Linux: linux-x64, linux-arm64, linux-x64-musl, linux-arm64-musl
#   - Windows: win32-x64, win32-arm64
OS_ARCH_MAP = {
    ("darwin", "x64"): "darwin-x64",
    ("darwin", "arm64"): "darwin-arm64",
    ("linux", "x64"): "linux-x64",
    ("linux", "arm64"): "linux-arm64",
    ("win32", "x64"): "win32-x64",
    ("win32", "arm64"): "win32-arm64",
}

# Claude Code launcher constants
APP_NAME = "Claude Code Launcher"
APP_VERSION = "2.0.0"

DEFAULT_CONFIG_DIR = Path.home() / ".claude"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "launcher_config.yaml"

SUPPORTED_RUNTIMES = {
    "ollama": {
        "name": "Ollama",
        "default_port": 11434,
        "api_path": "/api/tags",
        "models_key": "models",
        "model_name_key": "name",
        "health_path": "/api/tags",
        "env_base_url": "http://localhost:11434",
    },
    "vllm": {
        "name": "vLLM",
        "default_port": 8000,
        "api_path": "/v1/models",
        "models_key": "data",
        "model_name_key": "id",
        "health_path": "/health",
        "env_base_url": "http://localhost:8000",
    },
    "mlx": {
        "name": "MLX Serve",
        "default_port": 8080,
        "api_path": "/v1/models",
        "models_key": "data",
        "model_name_key": "id",
        "health_path": "/v1/models",
        "env_base_url": "http://localhost:8080",
    },
    "llama_cpp": {
        "name": "llama.cpp (llama-server)",
        "default_port": 8080,
        "api_path": "/v1/models",
        "models_key": "data",
        "model_name_key": "id",
        "health_path": "/health",
        "env_base_url": "http://localhost:8080",
    },
    "lm_studio": {
        "name": "LM Studio",
        "default_port": 1234,
        "api_path": "/v1/models",
        "models_key": "data",
        "model_name_key": "id",
        "health_path": "/v1/models",
        "env_base_url": "http://localhost:1234",
    },
    "tgi": {
        "name": "Text Generation Inference (TGI)",
        "default_port": 8080,
        "api_path": "/v1/models",
        "models_key": "data",
        "model_name_key": "id",
        "health_path": "/health",
        "env_base_url": "http://localhost:8080",
    },
}

DEFAULT_CONFIG = {
    "server": {
        "runtime": "ollama",
        "base_url": "http://localhost:11434",
    },
    "models": {
        "haiku": "",
        "sonnet": "",
        "opus": "",
    },
    "claude_code": {
        "path": "claude",
        "permission_mode": "default",
        "max_turns": 0,
    },
    "working_directory": str(Path.home()),
}


# ============================================================================
# OS Detection
# ============================================================================

class OSChecker:
    """Handles OS and architecture detection for Claude Code downloads."""

    @staticmethod
    def get_os_platform() -> str:
        """Return the OS platform name."""
        if sys.platform == "darwin":
            return "darwin"
        elif sys.platform == "linux":
            return "linux"
        elif sys.platform == "win32":
            return "win32"
        return "unknown"

    @staticmethod
    def get_architecture() -> str:
        """Return the CPU architecture in GCS format (x64 or arm64)."""
        import platform
        arch = platform.machine().lower()
        if arch in ("x86_64", "amd64"):
            return "x64"
        elif arch in ("arm64", "aarch64"):
            return "arm64"
        return arch

    @staticmethod
    def _is_musl_linux() -> bool:
        """Check if running on musl libc Linux."""
        import subprocess
        try:
            # Check for musl libc
            result = subprocess.run(
                ["ldd", "/bin/ls"], capture_output=True, text=True, timeout=5
            )
            return "musl" in result.stdout.lower()
        except Exception:
            # Fallback: check for musl files
            import os
            return os.path.exists("/lib/libc.musl-x86_64.so.1") or os.path.exists("/lib/libc.musl-aarch64.so.1")

    @staticmethod
    def get_download_info() -> Tuple[str, Optional[str]]:
        """
        Return (platform_name, arch_name) for download URL.
        Returns (None, None) if platform not supported.
        """
        os_name = OSChecker.get_os_platform()
        arch = OSChecker.get_architecture()

        key = (os_name, arch)
        if key in OS_ARCH_MAP:
            platform_name = OS_ARCH_MAP[key]
            # For Linux, check for musl and append -musl if needed
            if os_name == "linux" and OSChecker._is_musl_linux():
                platform_name = f"{platform_name}-musl"
            return platform_name, arch
        return None, None

    @staticmethod
    def is_supported_platform() -> bool:
        """Check if current platform is supported for automatic download."""
        return OSChecker.get_download_info()[0] is not None


# ============================================================================
# Version Management
# ============================================================================

class VersionManager:
    """Manages Claude Code version checking and fetching from CHANGELOG."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._cache: Optional[Dict] = None
        self._cache_time: Optional[float] = None
        self._cache_ttl = 3600  # 1 hour

    def _fetch_changelog(self) -> Optional[str]:
        """Fetch raw CHANGELOG content from GitHub."""
        try:
            resp = requests.get(CHANGELOG_URL, timeout=self.timeout)
            resp.raise_for_status()
            return resp.text
        except Exception:
            return None

    def get_latest_version(self) -> Optional[str]:
        """Fetch the latest stable version from CHANGELOG."""
        # Check cache
        now = time.time()
        if self._cache and self._cache_time:
            if now - self._cache_time < self._cache_ttl:
                return self._cache.get("latest")

        changelog = self._fetch_changelog()
        if not changelog:
            print('Failed to fetch CHANGELOG for version checking.')
            return None

        # Parse version from CHANGELOG (look for version headers like ## 0.x.x or ## v0.x.x)
        # The Claude Code changelog uses format: ## 2.1.42 (no 'v' prefix)
        match = re.search(r"^##\s+v?([0-9]+\.[0-9]+\.[0-9]+)", changelog, re.MULTILINE)
        if match:
            version = match.group(1)
            self._cache = {"latest": version}
            self._cache_time = now
            return version

        # Try alternative pattern (some changelogs use different format)
        match = re.search(r"Released:\s*v?([0-9]+\.[0-9]+\.[0-9]+)", changelog)
        if match:
            version = match.group(1)
            self._cache = {"latest": version}
            self._cache_time = now
            return version

        return None

    def get_installed_version(self, claude_path: str) -> Tuple[Optional[str], str]:
        """
        Get the installed Claude version.
        Returns (version, status_message) tuple.
        """
        # First check if the binary exists
        binary_path = shutil.which(claude_path)
        if not binary_path:
            # Try as absolute/relative path
            p = Path(claude_path)
            if p.exists() and p.is_file():
                binary_path = str(p.resolve())
            else:
                return None, f"Not found: {claude_path}"

        try:
            result = subprocess.run(
                [binary_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                # Clean up version string (might have 'v' prefix or extra text)
                match = re.search(r"v?([0-9]+\.[0-9]+\.[0-9]+)", version)
                if match:
                    return match.group(1), "OK"
                return version if version else None, "Parsed OK"
            else:
                return None, f"Command failed with exit code {result.returncode}: {result.stderr}"
        except FileNotFoundError:
            return None, f"Binary not found at {binary_path}"
        except subprocess.TimeoutExpired:
            return None, "Command timed out"
        except Exception as e:
            return None, f"Error: {str(e)}"

    def check_update_needed(self, claude_path: str) -> Dict[str, Any]:
        """
        Check if Claude needs update.
        Returns dict with: needs_update (bool), installed (str), latest (str)
        """
        result = {
            "needs_update": False,
            "installed": None,
            "latest": None,
            "can_check": False,
            "status": "checking",
            "status_message": ""
        }

        # Get installed version with detailed status
        installed, status_msg = self.get_installed_version(claude_path)
        result["installed"] = installed
        result["status_message"] = status_msg

        if not installed:
            # Check if binary exists but version check failed
            if shutil.which(claude_path) or Path(claude_path).exists():
                result["status"] = "version_check_failed"
                return result
            else:
                result["status"] = "not_installed"
                return result

        result["can_check"] = True

        # Get latest version
        latest = self.get_latest_version()
        result["latest"] = latest

        if latest:
            if installed != latest:
                result["needs_update"] = True
                result["status"] = "update_available"
            else:
                result["status"] = "up_to_date"
        else:
            result["status"] = "latest_check_failed"

        return result


# ============================================================================
# Configuration Manager
# ============================================================================

class ConfigManager:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_FILE):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
                self.config = self._deep_merge(DEFAULT_CONFIG.copy(), loaded)
                return self.config
            except Exception as e:
                print(f"Error loading config: {e}")
        self.config = DEFAULT_CONFIG.copy()
        return self.config

    def save(self, config: Optional[Dict] = None) -> bool:
        if config:
            self.config = config
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False,
                          allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def exists(self) -> bool:
        return self.config_path.exists()

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
        return result


# ============================================================================
# Download and Installation
# ============================================================================


def get_download_dir() -> Path:
    """Get the download directory based on OS."""
    if sys.platform == "win32":
        return Path(os.environ.get("USERPROFILE", Path.home())) / ".claude" / "downloads"
    else:
        return Path.home() / ".claude" / "downloads"


def get_platform_name() -> Optional[str]:
    """Get the platform name for download."""
    os_name, arch_name = OSChecker.get_download_info()
    if not os_name or not arch_name:
        return None
    return os_name


def get_binary_name_for_platform(platform_name: str) -> str:
    """Get the binary filename for a platform."""
    if platform_name.startswith("win32"):
        return "claude.exe"
    return "claude"


def compute_sha256(file_path: Path) -> Optional[str]:
    """Compute SHA256 hash of a file."""
    import hashlib
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception:
        return None


class ClaudeInstaller(QThread):
    """Background thread for downloading and installing Claude Code."""

    progress = Signal(int, str)  # percentage, message
    finished = Signal(bool, str)  # success, message
    error = Signal(str)  # error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_dir = get_download_dir()
        self.cancelled = False
        self._latest_version = None
        self._manifest = None

    def set_version(self, version: str):
        """Set the version to download."""
        self._latest_version = version

    def cancel(self):
        """Cancel the download."""
        self.cancelled = True

    def get_download_url(self) -> Optional[str]:
        """Build the download URL for current platform."""
        platform_name, _ = OSChecker.get_download_info()
        if not platform_name or not self._latest_version:
            return None

        # URL pattern: .../{version}/{platform}/claude(.exe)
        # Windows binaries have .exe extension
        if platform_name.startswith("win32"):
            binary_name = "claude.exe"
        else:
            binary_name = "claude"
        return f"{CLAUDE_DOWNLOAD_BASE}/{self._latest_version}/{platform_name}/{binary_name}"

    def _download_file(self, url: str, dest_path: Path) -> bool:
        """Download file with progress reporting."""
        try:
            self.progress.emit(0, f"Downloading from {url}...")

            with requests.get(url, stream=True, timeout=30) as resp:
                resp.raise_for_status()
                total_size = int(resp.headers.get('content-length', 0))
                downloaded = 0

                with open(dest_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if self.cancelled:
                            return False
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = int((downloaded / total_size) * 100)
                                self.progress.emit(percent, f"Downloading... {percent}%")
            return True
        except Exception as e:
            self.error.emit(str(e))
            return False

    def _fetch_latest_version(self) -> Optional[str]:
        """Fetch the latest version from GCS bucket."""
        try:
            resp = requests.get(f"{CLAUDE_DOWNLOAD_BASE}/latest", timeout=10)
            resp.raise_for_status()
            return resp.text.strip()
        except Exception as e:
            self.error.emit(f"Failed to fetch latest version: {e}")
            return None

    def _fetch_manifest(self, version: str) -> Optional[Dict]:
        """Fetch manifest.json for a given version."""
        try:
            resp = requests.get(f"{CLAUDE_DOWNLOAD_BASE}/{version}/manifest.json", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self.error.emit(f"Failed to fetch manifest: {e}")
            return None

    def _get_checksum(self, platform_name: str, manifest: Dict) -> Optional[str]:
        """Get checksum for a platform from manifest."""
        platforms = manifest.get("platforms", {})
        platform_info = platforms.get(platform_name)
        if platform_info:
            return platform_info.get("checksum")
        return None

    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify SHA256 checksum of a file."""
        actual_checksum = compute_sha256(file_path)
        if actual_checksum and actual_checksum.lower() == expected_checksum.lower():
            return True
        return False

    def _run_claude_install(self, binary_path: Path) -> Tuple[bool, str]:
        """Run claude install to set up launcher and shell integration."""
        try:
            self.progress.emit(0, "Setting up Claude Code...")
            result = subprocess.run(
                [str(binary_path), "install"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                return True, "Installation complete"
            else:
                return False, f"Install command failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Install command timed out"
        except Exception as e:
            return False, f"Install command error: {e}"

    def _cleanup(self, binary_path: Path) -> None:
        """Clean up downloaded binary."""
        try:
            if binary_path.exists():
                binary_path.unlink()
        except Exception:
            pass

    def run(self):
        """Main download and install workflow."""
        if not self._latest_version:
            self.finished.emit(False, "No version specified")
            return

        # Get platform info
        platform_name, _ = OSChecker.get_download_info()
        if not platform_name:
            self.finished.emit(False, "Unsupported platform for automatic download")
            return

        binary_name = get_binary_name_for_platform(platform_name)

        # Create download directory
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.error.emit(f"Failed to create download directory: {e}")
            self.finished.emit(False, str(e))
            return

        # Step 1: Fetch manifest
        self.progress.emit(0, "Fetching manifest...")
        manifest = self._fetch_manifest(self._latest_version)
        if not manifest:
            self.finished.emit(False, "Failed to fetch manifest")
            return

        # Step 2: Get checksum
        checksum = self._get_checksum(platform_name, manifest)
        if not checksum:
            self.finished.emit(False, f"Platform {platform_name} not found in manifest")
            return

        # Step 3: Build download URL and download binary
        url = f"{CLAUDE_DOWNLOAD_BASE}/{self._latest_version}/{platform_name}/{binary_name}"
        binary_path = self.download_dir / f"{binary_name}"

        if not self._download_file(url, binary_path):
            if not self.cancelled:
                self.finished.emit(False, "Download failed")
            return

        # Step 4: Verify checksum
        self.progress.emit(80, "Verifying checksum...")
        if not self._verify_checksum(binary_path, checksum):
            self._cleanup(binary_path)
            self.finished.emit(False, "Checksum verification failed")
            return

        # Step 5: Set executable permission on Unix-like systems
        if sys.platform != "win32":
            try:
                binary_path.chmod(binary_path.stat().st_mode | stat.S_IXUSR)
            except Exception:
                pass

        # Step 6: Run claude install
        success, message = self._run_claude_install(binary_path)

        # Step 7: Cleanup
        self._cleanup(binary_path)

        if success:
            self.finished.emit(True, "Claude Code installed successfully")
        else:
            self.finished.emit(False, message)


class ClaudeUninstaller(QThread):
    """Background thread for uninstalling Claude Code."""

    progress = Signal(int, str)  # percentage, message
    finished = Signal(bool, str)  # success, message
    error = Signal(str)  # error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_dir = get_download_dir()
        self.cancelled = False

    def cancel(self):
        """Cancel the uninstall."""
        self.cancelled = True

    def _find_claude_binary(self) -> Optional[Path]:
        """Find any Claude binary in the download directory."""
        if not self.download_dir.exists():
            return None

        for item in self.download_dir.iterdir():
            if item.is_file() and item.name in ("claude", "claude.exe"):
                return item

        return None

    def _run_claude_uninstall(self) -> Tuple[bool, str]:
        """Run claude uninstall to clean up launcher and shell integration."""
        try:
            self.progress.emit(0, "Uninstalling Claude Code...")

            # Try to find the binary first
            binary_path = self._find_claude_binary()
            if not binary_path:
                # Binary not found, just clean up downloads directory
                self._cleanup_downloads()
                return True, "Uninstall complete"

            result = subprocess.run(
                [str(binary_path), "uninstall"],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Clean up downloads directory regardless of result
            self._cleanup_downloads()

            if result.returncode == 0:
                return True, "Uninstall complete"
            else:
                return True, f"Uninstall complete (with warnings): {result.stderr}"
        except subprocess.TimeoutExpired:
            self._cleanup_downloads()
            return True, "Uninstall complete (with timeout)"
        except Exception as e:
            self._cleanup_downloads()
            return False, f"Uninstall error: {e}"

    def _cleanup_downloads(self) -> None:
        """Clean up the downloads directory."""
        try:
            if self.download_dir.exists():
                for item in self.download_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                # Try to remove empty directory
                try:
                    self.download_dir.rmdir()
                except OSError:
                    pass
        except Exception:
            pass

    def run(self):
        """Main uninstall workflow."""
        success, message = self._run_claude_uninstall()

        if success:
            self.finished.emit(True, message)
        else:
            self.finished.emit(False, message)


# ============================================================================
# Server Probe
# ============================================================================

class ServerProbe:
    @staticmethod
    def validate_url(base_url: str, runtime: str, timeout: float = 5.0) -> Dict:
        result = {"ok": False, "message": "", "response_time_ms": 0}
        rt = SUPPORTED_RUNTIMES.get(runtime, {})
        health_path = rt.get("health_path", "/health")
        url = base_url.rstrip("/") + health_path
        try:
            start = time.time()
            resp = requests.get(url, timeout=timeout)
            elapsed = (time.time() - start) * 1000
            result["response_time_ms"] = round(elapsed, 1)
            if resp.status_code == 200:
                result["ok"] = True
                result["message"] = f"Server OK ({elapsed:.0f}ms)"
            else:
                result["message"] = f"HTTP {resp.status_code}"
        except requests.ConnectionError:
            result["message"] = "Connection refused — is the server running?"
        except requests.Timeout:
            result["message"] = f"Timeout after {timeout}s"
        except Exception as e:
            result["message"] = str(e)
        return result

    @staticmethod
    def fetch_models(base_url: str, runtime: str, timeout: float = 10.0) -> List[str]:
        rt = SUPPORTED_RUNTIMES.get(runtime, {})
        api_path = rt.get("api_path", "/v1/models")
        models_key = rt.get("models_key", "data")
        name_key = rt.get("model_name_key", "id")
        url = base_url.rstrip("/") + api_path
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                models_list = data.get(models_key, [])
                names = []
                for m in models_list:
                    if isinstance(m, dict):
                        names.append(m.get(name_key, "unknown"))
                    elif isinstance(m, str):
                        names.append(m)
                return names
        except Exception:
            pass
        return []


# ============================================================================
# Script Generator
# ============================================================================

class ScriptGenerator:
    @staticmethod
    def generate(config: Dict) -> str:
        base_url = config.get("server", {}).get("base_url", "")
        api_key = config.get("server", {}).get("api_key", "")
        runtime = config.get("server", {}).get("runtime", "ollama")
        models = config.get("models", {})
        cc = config.get("claude_code", {})
        workdir = config.get("working_directory", str(Path.home()))
        claude_path = cc.get("path", "claude")

        rt_name = SUPPORTED_RUNTIMES.get(runtime, {}).get("name", runtime)

        lines = [
            "#!/bin/bash",
            f"# Generated by {APP_NAME} v{APP_VERSION}",
            f"# Runtime: {rt_name}",
            "",
            "# --- Environment ---",
            f'export ANTHROPIC_BASE_URL="{base_url}"',
        ]

        # Auth: use ANTHROPIC_AUTH_TOKEN for runtimes that don't need real keys,
        # use ANTHROPIC_API_KEY for runtimes that may require one.
        if runtime == "ollama":
            lines.append('export ANTHROPIC_AUTH_TOKEN="ollama"')
        else:
            # Use API key from config if provided, otherwise leave as placeholder
            if api_key:
                lines.append(f'export ANTHROPIC_API_KEY="{api_key}"')
            else:
                lines.append('# Set your API key (required for non-Ollama runtimes):')
                lines.append('# export ANTHROPIC_API_KEY="your-key-here"')

        for role in ("haiku", "sonnet", "opus"):
            model = models.get(role, "")
            if model:
                lines.append(
                    f'export ANTHROPIC_DEFAULT_{role.upper()}_MODEL="{model}"'
                )

        lines += ["", f'cd "{workdir}"', ""]

        # Build claude command (no --model needed; env vars handle model selection)
        cmd_parts = [claude_path]

        perm_mode = cc.get("permission_mode", "default")
        if perm_mode and perm_mode != "default":
            cmd_parts.extend(["--permission-mode", perm_mode])

        max_turns = cc.get("max_turns", 0)
        if max_turns and max_turns > 0:
            cmd_parts.extend(["--max-turns", str(max_turns)])

        lines += ["# --- Launch Claude Code ---", " ".join(cmd_parts), ""]
        return "\n".join(lines)

    @staticmethod
    def save_script(script_content: str, path: Path) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(script_content)
            path.chmod(path.stat().st_mode | stat.S_IEXEC)
            return True
        except Exception as e:
            print(f"Error saving script: {e}")
            return False

    @staticmethod
    def launch_in_terminal(script_path: Path):
        script = str(script_path.resolve())

        if sys.platform == "darwin":
            apple_script = (
                f'tell application "Terminal"\n'
                f'    do script "{script}"\n'
                f'    activate\n'
                f'end tell'
            )
            subprocess.Popen(["osascript", "-e", apple_script])

        elif sys.platform == "win32":
            subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k", script],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            terminals = [
                ["gnome-terminal", "--", "bash", script],
                ["konsole", "-e", "bash", script],
                ["xfce4-terminal", "-e", f"bash {script}"],
                ["xterm", "-e", f"bash {script}"],
            ]
            for cmd in terminals:
                if shutil.which(cmd[0]):
                    subprocess.Popen(cmd)
                    return
            subprocess.Popen(["bash", script])


# ============================================================================
# Main GUI
# ============================================================================

class ClaudeLauncherWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setFixedSize(680, 780)

        self.config_mgr = ConfigManager()
        self.config = self.config_mgr.load()

        self._build_ui()
        self._apply_config_to_ui()
        self._apply_style()

        if not self.config_mgr.exists():
            self.status_bar.showMessage(
                "No config found — set up your server and click Save.", 10000
            )

        # Check Claude status after a short delay
        self._check_initial_claude_status()

    # --- helpers ---

    def _get_platform_info(self) -> str:
        """Return platform information string."""
        os_name = OSChecker.get_os_platform()
        arch = OSChecker.get_architecture()
        supported = OSChecker.is_supported_platform()
        status = "supported" if supported else "unsupported"
        return f"{os_name}/{arch} ({status})"

    def _get_download_url(self, version: str) -> Optional[str]:
        """Build the full download URL for a given version."""
        platform, _ = OSChecker.get_download_info()
        if not platform:
            return None
        # Windows binaries have .exe extension
        binary_name = "claude.exe" if platform.startswith("win32") else "claude"
        return f"{CLAUDE_DOWNLOAD_BASE}/{version}/{platform}/{binary_name}"

    @staticmethod
    def _mono_font(size: int = 11) -> QFont:
        if sys.platform == "darwin":
            candidates = ["Menlo", "SF Mono", "Monaco"]
        elif sys.platform == "win32":
            candidates = ["Cascadia Mono", "Consolas", "Courier New"]
        else:
            candidates = ["DejaVu Sans Mono", "Liberation Mono", "Monospace"]
        available = set(QFontDatabase.families())
        for name in candidates:
            if name in available:
                return QFont(name, size)
        font = QFont()
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(size)
        return font

    # --- build ui ---

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # ---- Server ----
        srv_grp = QGroupBox("Server")
        srv_lay = QFormLayout(srv_grp)

        self.runtime_combo = QComboBox()
        for key, info in SUPPORTED_RUNTIMES.items():
            self.runtime_combo.addItem(info["name"], key)
        self.runtime_combo.currentIndexChanged.connect(self._on_runtime_changed)
        srv_lay.addRow("Runtime:", self.runtime_combo)

        url_row = QHBoxLayout()
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("http://localhost:11434")
        url_row.addWidget(self.base_url_edit)
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self._validate_server)
        self.validate_btn.setMinimumWidth(80)
        url_row.addWidget(self.validate_btn)
        srv_lay.addRow("Base URL:", url_row)

        self.server_status = QLabel("")
        srv_lay.addRow("", self.server_status)

        # API Key input (shown for runtimes that require it)
        api_key_row = QHBoxLayout()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("ANTHROPIC_API_KEY (required for non-Ollama runtimes)")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        api_key_row.addWidget(self.api_key_edit)
        srv_lay.addRow("API Key:", api_key_row)

        layout.addWidget(srv_grp)

        # ---- Models ----
        mdl_grp = QGroupBox("Model Mapping  (ANTHROPIC_DEFAULT_*_MODEL)")
        mdl_lay = QFormLayout(mdl_grp)

        self.refresh_btn = QPushButton("Refresh Models from Server")
        self.refresh_btn.clicked.connect(self._refresh_models)
        self.refresh_btn.setMinimumWidth(180)
        mdl_lay.addRow("", self.refresh_btn)

        self.models_label = QLabel("(not loaded)")
        self.models_label.setWordWrap(True)
        self.models_label.setStyleSheet("color: #888;")
        mdl_lay.addRow("Available:", self.models_label)

        self.haiku_combo = QComboBox()
        self.haiku_combo.setEditable(True)
        self.haiku_combo.setMinimumWidth(320)
        mdl_lay.addRow("Haiku:", self.haiku_combo)

        self.sonnet_combo = QComboBox()
        self.sonnet_combo.setEditable(True)
        self.sonnet_combo.setMinimumWidth(320)
        mdl_lay.addRow("Sonnet:", self.sonnet_combo)

        self.opus_combo = QComboBox()
        self.opus_combo.setEditable(True)
        self.opus_combo.setMinimumWidth(320)
        mdl_lay.addRow("Opus:", self.opus_combo)

        layout.addWidget(mdl_grp)

        # ---- Claude Code CLI ----
        cli_grp = QGroupBox("Claude Code CLI")
        cli_lay = QFormLayout(cli_grp)

        path_row = QHBoxLayout()
        self.claude_path_edit = QLineEdit()
        self.claude_path_edit.setPlaceholderText("claude")
        path_row.addWidget(self.claude_path_edit)
        detect_btn = QPushButton("Detect")
        detect_btn.clicked.connect(self._auto_detect_claude)
        detect_btn.setMinimumWidth(70)
        path_row.addWidget(detect_btn)
        cli_lay.addRow("CLI Path:", path_row)

        self.perm_combo = QComboBox()
        self.perm_combo.addItems(["default", "plan", "delegate",
                                   "trust", "bypassPermissions"])
        cli_lay.addRow("Permission:", self.perm_combo)

        self.max_turns_spin = QSpinBox()
        self.max_turns_spin.setRange(0, 100)
        self.max_turns_spin.setSpecialValueText("Unlimited")
        cli_lay.addRow("Max Turns:", self.max_turns_spin)

        layout.addWidget(cli_grp)

        # ---- Claude Code Installation Status ----
        inst_grp = QGroupBox("Claude Code Installation")
        inst_lay = QVBoxLayout(inst_grp)

        # Status row
        status_row = QHBoxLayout()
        self.claude_status_label = QLabel("Checking...")
        self.claude_status_label.setStyleSheet("color: #f9e2af;")
        status_row.addWidget(self.claude_status_label)
        self.install_version_label = QLabel("")
        self.install_version_label.setStyleSheet("color: #89b4fa;")
        status_row.addWidget(self.install_version_label)
        inst_lay.addLayout(status_row)

        # Download progress
        progress_row = QHBoxLayout()
        self.download_progress = QProgressBar()
        self.download_progress.setRange(0, 100)
        self.download_progress.setValue(0)
        self.download_progress.setVisible(False)
        progress_row.addWidget(self.download_progress)
        inst_lay.addLayout(progress_row)

        # Action buttons
        btn_row = QHBoxLayout()
        self.install_btn = QPushButton("Install Claude")
        self.install_btn.clicked.connect(self._install_claude)
        self.install_btn.setMinimumWidth(140)
        btn_row.addWidget(self.install_btn)

        self.update_btn = QPushButton("Update Claude")
        self.update_btn.clicked.connect(self._update_claude)
        self.update_btn.setMinimumWidth(140)
        btn_row.addWidget(self.update_btn)

        self.uninstall_btn = QPushButton("Uninstall Claude")
        self.uninstall_btn.clicked.connect(self._uninstall_claude)
        self.uninstall_btn.setMinimumWidth(140)
        btn_row.addWidget(self.uninstall_btn)

        btn_row.addStretch()
        inst_lay.addLayout(btn_row)

        # Platform info
        info_label = QLabel("")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-size: 11px;")
        platform, _ = OSChecker.get_download_info()
        if platform:
            url = self._get_download_url("vX.Y.Z")
            info_text = f"Platform: {platform} | Download URL: {url or 'N/A'}"
        else:
            info_text = f"Platform: Unsupported ({self._get_platform_info()})"
        info_label.setText(info_text)
        inst_lay.addWidget(info_label)

        layout.addWidget(inst_grp)

        # ---- Working Directory ----
        wd_grp = QGroupBox("Working Directory")
        wd_lay = QHBoxLayout(wd_grp)
        self.workdir_edit = QLineEdit(str(Path.home()))
        wd_lay.addWidget(self.workdir_edit)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_workdir)
        browse_btn.setMinimumWidth(80)
        wd_lay.addWidget(browse_btn)
        layout.addWidget(wd_grp)

        # ---- Script Preview ----
        prev_grp = QGroupBox("Generated Script Preview")
        prev_lay = QVBoxLayout(prev_grp)
        self.preview_text = QPlainTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(self._mono_font(11))
        self.preview_text.setMaximumHeight(170)
        prev_lay.addWidget(self.preview_text)
        layout.addWidget(prev_grp)

        # ---- Buttons ----
        btn_row = QHBoxLayout()

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self._save_config)
        save_btn.setMinimumWidth(100)
        btn_row.addWidget(save_btn)

        preview_btn = QPushButton("Preview Script")
        preview_btn.clicked.connect(self._preview_script)
        preview_btn.setMinimumWidth(110)
        btn_row.addWidget(preview_btn)

        btn_row.addStretch()

        self.roll_btn = QPushButton("  Let's Roll  🚀")
        self.roll_btn.setStyleSheet(
            "QPushButton { background-color: #16a34a; color: white; "
            "padding: 10px 32px; font-size: 15px; font-weight: bold; "
            "border-radius: 6px; }"
            "QPushButton:hover { background-color: #15803d; }"
            "QPushButton:pressed { background-color: #166534; }"
        )
        self.roll_btn.clicked.connect(self._lets_roll)
        btn_row.addWidget(self.roll_btn)

        layout.addLayout(btn_row)
        layout.addStretch()

        scroll.setWidget(inner)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _check_initial_claude_status(self):
        """Check Claude status after UI is shown."""
        QTimer.singleShot(500, self._check_claude_update)

    # --- config <-> ui ---

    def _apply_config_to_ui(self):
        srv = self.config.get("server", {})
        mdl = self.config.get("models", {})
        cc = self.config.get("claude_code", {})

        idx = self.runtime_combo.findData(srv.get("runtime", "ollama"))
        if idx >= 0:
            self.runtime_combo.setCurrentIndex(idx)
        self.base_url_edit.setText(srv.get("base_url", ""))
        self.api_key_edit.setText(srv.get("api_key", ""))

        # Show/hide API key based on runtime
        runtime = srv.get("runtime", "ollama")
        if runtime == "ollama":
            self.api_key_edit.setVisible(False)
        else:
            self.api_key_edit.setVisible(True)

        self.haiku_combo.setCurrentText(mdl.get("haiku", ""))
        self.sonnet_combo.setCurrentText(mdl.get("sonnet", ""))
        self.opus_combo.setCurrentText(mdl.get("opus", ""))

        self.claude_path_edit.setText(cc.get("path", "claude"))
        pidx = self.perm_combo.findText(cc.get("permission_mode", "default"))
        if pidx >= 0:
            self.perm_combo.setCurrentIndex(pidx)
        self.max_turns_spin.setValue(cc.get("max_turns", 0))

        self.workdir_edit.setText(
            self.config.get("working_directory", str(Path.home()))
        )

    def _collect_config(self) -> Dict:
        return {
            "server": {
                "runtime": self.runtime_combo.currentData(),
                "base_url": self.base_url_edit.text().strip(),
                "api_key": self.api_key_edit.text().strip(),
            },
            "models": {
                "haiku": self.haiku_combo.currentText().strip(),
                "sonnet": self.sonnet_combo.currentText().strip(),
                "opus": self.opus_combo.currentText().strip(),
            },
            "claude_code": {
                "path": self.claude_path_edit.text().strip() or "claude",
                "permission_mode": self.perm_combo.currentText(),
                "max_turns": self.max_turns_spin.value(),
            },
            "working_directory": self.workdir_edit.text().strip()
                                 or str(Path.home()),
        }

    # --- actions ---

    def _on_runtime_changed(self):
        runtime = self.runtime_combo.currentData()
        if runtime and runtime in SUPPORTED_RUNTIMES:
            defaults = [r["env_base_url"] for r in SUPPORTED_RUNTIMES.values()]
            current = self.base_url_edit.text().strip()
            if not current or current in defaults:
                self.base_url_edit.setText(
                    SUPPORTED_RUNTIMES[runtime]["env_base_url"]
                )

        # Show/hide API key field based on runtime
        runtime = self.runtime_combo.currentData()
        if runtime == "ollama":
            # Ollama doesn't require API key
            self.api_key_edit.setVisible(False)
        else:
            # Other runtimes may require API key
            self.api_key_edit.setVisible(True)

    def _validate_server(self):
        url = self.base_url_edit.text().strip()
        runtime = self.runtime_combo.currentData()
        if not url:
            self._set_status("❌  Enter a URL first", "red")
            return

        self._set_status("⏳  Checking…", "orange")
        QApplication.processEvents()

        result = ServerProbe.validate_url(url, runtime)
        if result["ok"]:
            self._set_status(f"✅  {result['message']}", "#22c55e")
            QTimer.singleShot(300, self._refresh_models)
        else:
            self._set_status(f"❌  {result['message']}", "red")

    def _set_status(self, text: str, color: str):
        self.server_status.setText(text)
        self.server_status.setStyleSheet(f"color: {color};")

    def _refresh_models(self):
        url = self.base_url_edit.text().strip()
        runtime = self.runtime_combo.currentData()
        if not url:
            return

        self.models_label.setText("⏳  Fetching…")
        QApplication.processEvents()

        names = ServerProbe.fetch_models(url, runtime)
        if names:
            disp = ", ".join(names[:15])
            if len(names) > 15:
                disp += f" … (+{len(names)-15})"
            self.models_label.setText(f"({len(names)}) {disp}")

            for combo in (self.haiku_combo, self.sonnet_combo,
                          self.opus_combo):
                cur = combo.currentText()
                combo.clear()
                combo.addItem("")
                combo.addItems(names)
                if cur:
                    combo.setCurrentText(cur)
        else:
            self.models_label.setText("⚠  No models found")

    def _auto_detect_claude(self):
        # Check for claude.exe on Windows first
        binary_name = "claude.exe" if sys.platform == "win32" else "claude"
        path = shutil.which(binary_name)
        if path:
            self.claude_path_edit.setText(path)
            self.status_bar.showMessage(f"Found: {path}", 5000)
            return
        # Check common Unix paths
        for p in [Path.home() / ".npm-global" / "bin" / "claude",
                  Path.home() / ".local" / "bin" / "claude",
                  Path("/usr/local/bin/claude")]:
            if p.exists():
                self.claude_path_edit.setText(str(p))
                self.status_bar.showMessage(f"Found: {p}", 5000)
                return
        self.status_bar.showMessage("Claude CLI not found in PATH", 5000)

    # --- Claude installation management ---

    def _update_button_states(self, claude_path: str, result: Dict):
        """Update button states based on Claude installation status."""
        installed = result.get("installed") is not None

        if installed:
            # Claude is installed - show uninstall button, hide install button
            self.install_btn.setVisible(False)
            self.update_btn.setVisible(True)
            self.uninstall_btn.setVisible(True)
            if result.get("needs_update"):
                # Update available
                self.update_btn.setEnabled(True)
                self.uninstall_btn.setEnabled(True)
            else:
                # Up to date
                self.update_btn.setEnabled(False)
                self.uninstall_btn.setEnabled(True)
        else:
            # Claude not installed - show install button
            self.install_btn.setVisible(True)
            self.update_btn.setVisible(False)
            self.uninstall_btn.setVisible(False)
            if result.get("status") == "update_available":
                self.install_btn.setEnabled(True)
            elif result.get("status") == "not_installed":
                self.install_btn.setEnabled(True)
            else:
                self.install_btn.setEnabled(False)

    def _check_claude_update(self):
        """Check Claude version and update status."""
        claude_path = self.claude_path_edit.text().strip() or "claude"
        version_mgr = VersionManager()

        self.claude_status_label.setText("Checking...")
        self.claude_status_label.setStyleSheet("color: #f9e2af;")
        QApplication.processEvents()

        result = version_mgr.check_update_needed(claude_path)

        # Update button states
        self._update_button_states(claude_path, result)

        if result["status"] == "not_installed":
            self.claude_status_label.setText("Not installed")
            self.claude_status_label.setStyleSheet("color: #f38ba8;")
            self.install_version_label.setText("")
            self.status_bar.showMessage("Claude Code not found. Click 'Install Claude' to download.", 10000)
        elif result["status"] == "version_check_failed":
            self.claude_status_label.setText("Found but version check failed")
            self.claude_status_label.setStyleSheet("color: #fab387;")
            self.install_version_label.setText(f"({result.get('status_message', '')})")
            self.status_bar.showMessage(f"Binary found but version check failed: {result.get('status_message', '')}", 10000)
        elif result["status"] == "latest_check_failed":
            self.claude_status_label.setText("Version check failed (can't fetch CHANGELOG)")
            self.claude_status_label.setStyleSheet("color: #fab387;")
            self.install_version_label.setText(f"(installed: v{result['installed']})")
            self.status_bar.showMessage("Could not fetch latest version from CHANGELOG", 10000)
        elif result["status"] == "checking":
            self.claude_status_label.setText("Unknown version / not found")
            self.claude_status_label.setStyleSheet("color: #f9e2af;")
            self.install_version_label.setText("")
        elif result["status"] == "up_to_date":
            self.claude_status_label.setText("Up to date")
            self.claude_status_label.setStyleSheet("color: #a6e3a1;")
            self.install_version_label.setText(f"(v{result['installed']})")
            self.status_bar.showMessage("Claude Code is up to date", 5000)
        elif result["status"] == "update_available":
            self.claude_status_label.setText("Update available")
            self.claude_status_label.setStyleSheet("color: #fab387;")
            self.install_version_label.setText(f"(installed: v{result['installed']}, latest: v{result['latest']})")
            self.status_bar.showMessage(f"Update available: v{result['latest']}", 10000)
        elif result["status"] == "install_outdated":
            self.claude_status_label.setText("Need to install")
            self.claude_status_label.setStyleSheet("color: #fab387;")
            self.install_version_label.setText(f"(latest: v{result['latest']})")
        else:
            self.claude_status_label.setText(result.get("status", "Unknown"))
            self.install_version_label.setText("")
            if result.get("status_message"):
                self.status_bar.showMessage(result["status_message"], 5000)

    def _install_claude(self):
        """Open installation dialog or start download."""
        version_mgr = VersionManager()

        # Get latest version
        latest_version = version_mgr.get_latest_version()
        if not latest_version:
            QMessageBox.warning(
                self, "Version Check Failed",
                "Could not fetch latest version from CHANGELOG.\n"
                "Please check your internet connection."
            )
            return

        # Check if platform is supported
        if not OSChecker.is_supported_platform():
            os_name = OSChecker.get_os_platform()
            QMessageBox.warning(
                self, "Unsupported Platform",
                f"Claude Code automatic installation is not supported on {os_name}.\n\n"
                "Please manually install Claude Code using:\n"
                "  npm install -g @anthropic-ai/claude-code"
            )
            return

        # Confirm installation
        platform, _ = OSChecker.get_download_info()
        # Windows binaries have .exe extension
        binary_name = "claude.exe" if platform.startswith("win32") else "claude"
        msg = f"Install Claude Code v{latest_version}?\n\n"
        msg += f"Platform: {platform}\n"
        msg += f"Download URL: {CLAUDE_DOWNLOAD_BASE}/{latest_version}/{platform}/{binary_name}\n"
        msg += "This will download approximately 20-30 MB."

        reply = QMessageBox.question(
            self, "Install Claude Code",
            msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        # Start download in background
        self._start_claude_download(latest_version)

    def _start_claude_download(self, version: str):
        """Start the download thread for Claude Code."""
        self.installer = ClaudeInstaller(self)
        self.installer.set_version(version)

        # Connect signals
        self.installer.progress.connect(self._on_install_progress)
        self.installer.finished.connect(self._on_install_finished)
        self.installer.error.connect(self._on_install_error)

        # Update UI
        self.claude_status_label.setText("Downloading...")
        self.claude_status_label.setStyleSheet("color: #f9e2af;")
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        self.install_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)
        self.status_bar.showMessage("Downloading Claude Code...")

        # Start thread
        self.installer.start()

    def _on_install_progress(self, percent: int, message: str):
        """Handle download progress updates."""
        self.download_progress.setValue(percent)
        self.status_bar.showMessage(message)

    def _on_install_finished(self, success: bool, message: str):
        """Handle download completion."""
        self.download_progress.setVisible(False)

        if success:
            # Update path to installed binary
            if message:
                self.claude_path_edit.setText(message)
            self.claude_status_label.setText("Installed successfully")
            self.claude_status_label.setStyleSheet("color: #a6e3a1;")
            self.install_version_label.setText("")
            self.status_bar.showMessage(f"Claude Code installed: {message}", 10000)
            QMessageBox.information(self, "Installation Complete", message)
        else:
            self.claude_status_label.setText("Installation failed")
            self.claude_status_label.setStyleSheet("color: #f38ba8;")
            self.status_bar.showMessage(f"Installation failed: {message}", 10000)
            QMessageBox.warning(self, "Installation Failed", message)

        self.install_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        self._check_claude_update()  # Refresh status

    def _update_claude(self):
        """Update Claude Code to latest version."""
        claude_path = self.claude_path_edit.text().strip() or "claude"
        version_mgr = VersionManager()

        # Get latest version
        latest_version = version_mgr.get_latest_version()
        if not latest_version:
            QMessageBox.warning(
                self, "Version Check Failed",
                "Could not fetch latest version from CHANGELOG.\n"
                "Please check your internet connection."
            )
            return

        # Check if platform is supported
        if not OSChecker.is_supported_platform():
            os_name = OSChecker.get_os_platform()
            QMessageBox.warning(
                self, "Unsupported Platform",
                f"Claude Code automatic installation is not supported on {os_name}.\n\n"
                "Please manually install Claude Code using:\n"
                "  npm install -g @anthropic-ai/claude-code"
            )
            return

        # Get installed version
        installed, _ = version_mgr.get_installed_version(claude_path)

        # Confirm update
        platform, _ = OSChecker.get_download_info()
        binary_name = "claude.exe" if platform.startswith("win32") else "claude"
        msg = f"Update Claude Code from v{installed} to v{latest_version}?\n\n"
        msg += f"Platform: {platform}\n"
        msg += f"Download URL: {CLAUDE_DOWNLOAD_BASE}/{latest_version}/{platform}/{binary_name}\n"
        msg += "This will download approximately 20-30 MB."

        reply = QMessageBox.question(
            self, "Update Claude Code",
            msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        # Start download in background
        self._start_claude_download(latest_version)

    def _uninstall_claude(self):
        """Uninstall Claude Code."""
        claude_path = self.claude_path_edit.text().strip() or "claude"

        # Check if binary exists
        binary_path = shutil.which(claude_path)
        if not binary_path:
            p = Path(claude_path)
            if not (p.exists() and p.is_file()):
                QMessageBox.information(
                    self, "Already Uninstalled",
                    "Claude Code does not appear to be installed."
                )
                return

        # Confirm uninstallation
        reply = QMessageBox.question(
            self, "Uninstall Claude Code",
            "Are you sure you want to uninstall Claude Code?\n\n"
            "This will remove the Claude Code CLI and all downloaded files.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # Start uninstall in background
        self._start_claude_uninstall()

    def _start_claude_uninstall(self):
        """Start the uninstall thread for Claude Code."""
        self.uninstaller = ClaudeUninstaller(self)

        # Connect signals
        self.uninstaller.progress.connect(self._on_uninstall_progress)
        self.uninstaller.finished.connect(self._on_uninstall_finished)
        self.uninstaller.error.connect(self._on_uninstall_error)

        # Update UI
        self.claude_status_label.setText("Uninstalling...")
        self.claude_status_label.setStyleSheet("color: #f9e2af;")
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        self.install_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)
        self.status_bar.showMessage("Uninstalling Claude Code...")

        # Start thread
        self.uninstaller.start()

    def _on_install_progress(self, percent: int, message: str):
        """Handle download progress updates."""
        self.download_progress.setValue(percent)
        self.status_bar.showMessage(message)

    def _on_uninstall_progress(self, percent: int, message: str):
        """Handle uninstall progress updates."""
        self.download_progress.setValue(percent)
        self.status_bar.showMessage(message)

    def _on_uninstall_finished(self, success: bool, message: str):
        """Handle uninstall completion."""
        self.download_progress.setVisible(False)

        if success:
            self.claude_status_label.setText("Uninstalled successfully")
            self.claude_status_label.setStyleSheet("color: #a6e3a1;")
            self.install_version_label.setText("")
            self.claude_path_edit.setText("claude")
            self.status_bar.showMessage(f"Claude Code uninstalled: {message}", 10000)
            QMessageBox.information(self, "Uninstallation Complete", message)
        else:
            self.claude_status_label.setText("Uninstallation failed")
            self.claude_status_label.setStyleSheet("color: #f38ba8;")
            self.status_bar.showMessage(f"Uninstallation failed: {message}", 10000)
            QMessageBox.warning(self, "Uninstallation Failed", message)

        # Refresh button states
        self._check_claude_update()

    def _on_uninstall_error(self, error: str):
        """Handle uninstall error."""
        self.download_progress.setVisible(False)
        self.claude_status_label.setText("Uninstall error")
        self.claude_status_label.setStyleSheet("color: #f38ba8;")
        self.status_bar.showMessage(f"Uninstall error: {error}", 10000)
        self.install_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        QMessageBox.critical(self, "Uninstall Error", error)

    def _browse_workdir(self):
        d = QFileDialog.getExistingDirectory(
            self, "Select Working Directory",
            self.workdir_edit.text() or str(Path.home()),
        )
        if d:
            self.workdir_edit.setText(d)

    def _save_config(self):
        self.config = self._collect_config()
        if self.config_mgr.save(self.config):
            self.status_bar.showMessage(
                f"✅ Saved → {self.config_mgr.config_path}", 5000
            )
        else:
            QMessageBox.warning(self, "Error", "Failed to save config.")

    def _preview_script(self):
        self.config = self._collect_config()
        self.preview_text.setPlainText(ScriptGenerator.generate(self.config))

    def _lets_roll(self):
        self.config = self._collect_config()

        # Validate working dir
        wd = Path(self.config["working_directory"])
        if not wd.is_dir():
            QMessageBox.warning(
                self, "Invalid Directory",
                f"Working directory does not exist:\n{wd}",
            )
            return

        # Validate URL present
        url = self.config["server"]["base_url"]
        runtime = self.config["server"]["runtime"]
        if not url:
            QMessageBox.warning(self, "Missing URL", "Set the server Base URL.")
            return

        # Server health check
        self.status_bar.showMessage("⏳ Checking server…")
        QApplication.processEvents()

        check = ServerProbe.validate_url(url, runtime, timeout=3.0)
        if not check["ok"]:
            reply = QMessageBox.question(
                self, "Server Unreachable",
                f"Server check failed: {check['message']}\n\nLaunch anyway?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                self.status_bar.showMessage("Cancelled.", 3000)
                return

        # Generate script
        script = ScriptGenerator.generate(self.config)
        script_path = DEFAULT_CONFIG_DIR / "launch_claude.sh"

        if not ScriptGenerator.save_script(script, script_path):
            QMessageBox.critical(
                self, "Error", f"Failed to write script:\n{script_path}"
            )
            return

        self.config_mgr.save(self.config)
        self.preview_text.setPlainText(script)

        # Launch in new terminal
        ScriptGenerator.launch_in_terminal(script_path)
        self.status_bar.showMessage(
            f"🚀 Launched!  Script → {script_path}", 10000
        )

    # --- style ---

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 6px;
                margin-top: 14px;
                padding: 14px 10px 8px 10px;
                font-weight: bold;
                color: #89b4fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px; padding: 0 6px;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px 8px;
                color: #cdd6f4;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #89b4fa;
            }
            QComboBox::drop-down { border-left: 1px solid #45475a; }
            QComboBox QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #45475a;
            }
            QPlainTextEdit {
                background-color: #11111b;
                border: 1px solid #45475a;
                border-radius: 4px;
                color: #a6e3a1;
            }
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 6px 14px;
            }
            QPushButton:hover { background-color: #45475a; }
            QStatusBar {
                background-color: #11111b;
                color: #a6adc8;
                border-top: 1px solid #45475a;
            }
            QScrollBar:vertical {
                background-color: #1e1e2e; width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #45475a;
                border-radius: 4px; min-height: 20px;
            }
            QLabel { color: #cdd6f4; }
        """)


# ============================================================================
# Entry Point
# ============================================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    window = ClaudeLauncherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()