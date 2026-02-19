#!/usr/bin/env python3
"""
Claude Code Launcher - Cross-platform TUI application for managing Claude Code
installation and environment variables.
"""

import os
import sys
import json
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
import curses
from curses import wrapper
import getpass

# Environment variable definitions
ENV_VARS = {
    "ANTHROPIC_API_KEY": "Anthropic API 키 (X-Api-Key 헤더로 전송)",
    "ANTHROPIC_AUTH_TOKEN": "Authorization: Bearer 헤더에 사용할 커스텀 값",
    "ANTHROPIC_CUSTOM_HEADERS": "요청에 추가할 커스텀 헤더 (Name: Value 형식)",
    "CLAUDE_CODE_CLIENT_CERT": "mTLS 인증용 클라이언트 인증서 파일 경로",
    "CLAUDE_CODE_CLIENT_KEY": "mTLS 인증용 클라이언트 개인 키 파일 경로",
    "CLAUDE_CODE_CLIENT_KEY_PASSPHRASE": "암호화된 클라이언트 키의 패스프레이즈",
    "ANTHROPIC_MODEL": "사용할 모델 이름 지정",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "Sonnet 모델 별칭 오버라이드",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "Opus 모델 별칭 오버라이드",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "Haiku 모델 별칭 오버라이드",
    "CLAUDE_CODE_SUBAGENT_MODEL": "서브에이전트에서 사용할 모델",
    "ANTHROPIC_SMALL_FAST_MODEL": "*(Deprecated)* 백그라운드 작업용 Haiku 클래스 모델",
    "ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION": "Bedrock에서 Haiku 모델의 AWS 리전 오버라이드",
    "MAX_THINKING_TOKENS": "Extended thinking 활성화 및 토큰 예산 설정",
    "CLAUDE_CODE_USE_BEDROCK": "AWS Bedrock 사용",
    "CLAUDE_CODE_USE_VERTEX": "Google Vertex AI 사용",
    "CLAUDE_CODE_USE_FOUNDRY": "Microsoft Foundry 사용",
    "AWS_BEARER_TOKEN_BEDROCK": "Bedrock API 키 인증",
    "ANTHROPIC_FOUNDRY_API_KEY": "Microsoft Foundry 인증 API 키",
    "CLAUDE_CODE_SKIP_BEDROCK_AUTH": "Bedrock AWS 인증 스킵 (LLM 게이트웨이 사용 시)",
    "CLAUDE_CODE_SKIP_VERTEX_AUTH": "Vertex Google 인증 스킵",
    "CLAUDE_CODE_SKIP_FOUNDRY_AUTH": "Foundry Azure 인증 스킵",
    "VERTEX_REGION_CLAUDE_3_5_HAIKU": "Vertex AI에서 Claude 3.5 Haiku 리전 오버라이드",
    "VERTEX_REGION_CLAUDE_3_7_SONNET": "Vertex AI에서 Claude 3.7 Sonnet 리전 오버라이드",
    "VERTEX_REGION_CLAUDE_4_0_SONNET": "Vertex AI에서 Claude 4.0 Sonnet 리전 오버라이드",
    "VERTEX_REGION_CLAUDE_4_0_OPUS": "Vertex AI에서 Claude 4.0 Opus 리전 오버라이드",
    "VERTEX_REGION_CLAUDE_4_1_OPUS": "Vertex AI에서 Claude 4.1 Opus 리전 오버라이드",
    "BASH_DEFAULT_TIMEOUT_MS": "장시간 실행 Bash 명령의 기본 타임아웃",
    "BASH_MAX_TIMEOUT_MS": "모델이 설정할 수 있는 최대 타임아웃",
    "BASH_MAX_OUTPUT_LENGTH": "Bash 출력 최대 문자 수 (초과 시 중간 잘림)",
    "CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR": "각 Bash 명령 후 프로젝트 루트 디렉토리로 복귀",
    "CLAUDE_ENV_FILE": "Bash 명령 실행 전 소싱할 환경 설정 쉘 스크립트 경로",
    "CLAUDE_CODE_SHELL_PREFIX": "모든 Bash 명령에 붙일 접두 명령 (로깅/감사용)",
    "MCP_TIMEOUT": "MCP 서버 시작 타임아웃 (ms)",
    "MCP_TOOL_TIMEOUT": "MCP 툴 실행 타임아웃 (ms)",
    "MAX_MCP_OUTPUT_TOKENS": "MCP 툴 응답 최대 토큰 수 (기본: 25,000)",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "대부분의 요청에 대한 최대 출력 토큰 수",
    "DISABLE_COST_WARNINGS": "`1`로 설정 시 비용 경고 메시지 비활성화",
    "DISABLE_PROMPT_CACHING": "`1`로 설정 시 모든 모델 프롬프트 캐싱 비활성화",
    "DISABLE_PROMPT_CACHING_SONNET": "Sonnet 모델 프롬프트 캐싱 비활성화",
    "DISABLE_PROMPT_CACHING_OPUS": "Opus 모델 프롬프트 캐싱 비활성화",
    "DISABLE_PROMPT_CACHING_HAIKU": "Haiku 모델 프롬프트 캐싱 비활성화",
    "SLASH_COMMAND_TOOL_CHAR_BUDGET": "슬래시 커맨드 메타데이터 최대 문자 수 (기본: 15,000)",
    "DISABLE_TELEMETRY": "`1`로 설정 시 Statsig 텔레메트리 비활성화",
    "DISABLE_ERROR_REPORTING": "`1`로 설정 시 Sentry 오류 보고 비활성화",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "`DISABLE_AUTOUPDATER` + `DISABLE_BUG_COMMAND` + `DISABLE_ERROR_REPORTING` + `DISABLE_TELEMETRY` 일괄 설정",
    "CLAUDE_CODE_ENABLE_TELEMETRY": "`1`로 설정 시 OpenTelemetry 활성화",
    "CLAUDE_CONFIG_DIR": "Claude Code 설정 및 데이터 파일 저장 경로 커스텀",
    "DISABLE_AUTOUPDATER": "`1`로 설정 시 자동 업데이트 비활성화",
    "DISABLE_BUG_COMMAND": "`1`로 설정 시 `/bug` 명령 비활성화",
    "DISABLE_NON_ESSENTIAL_MODEL_CALLS": "`1`로 설정 시 flavor text 등 비필수 모델 호출 비활성화",
    "CLAUDE_CODE_DISABLE_TERMINAL_TITLE": "`1`로 설정 시 대화 내용 기반 터미널 제목 자동 업데이트 비활성화",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "`1`로 설정 시 `anthropic-beta` 헤더 비활성화 (LLM 게이트웨이 연동 시 유용)",
    "CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL": "IDE 확장 자동 설치 스킵",
    "CLAUDE_CODE_API_KEY_HELPER_TTL_MS": "`apiKeyHelper` 사용 시 자격 증명 갱신 주기 (ms)",
    "USE_BUILTIN_RIPGREP": "`0`으로 설정 시 내장 `rg` 대신 시스템 `rg` 사용",
    "HTTP_PROXY": "HTTP 프록시 서버 지정",
    "HTTPS_PROXY": "HTTPS 프록시 서버 지정",
    "NO_PROXY": "프록시 우회할 도메인/IP 목록"
}

class ClaudeLauncher:
    """Main Claude Code launcher class."""

    def __init__(self):
        self.settings_dir = Path.home() / ".claude"
        self.settings_file = self.settings_dir / "settings.json"
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"env": {}}
        else:
            # Create settings directory if it doesn't exist
            self.settings_dir.mkdir(exist_ok=True)
            return {"env": {}}

    def _save_settings(self) -> None:
        """Save settings to JSON file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save settings: {e}")

    def install_claude(self) -> None:
        """Install Claude Code using the recommended native installation method."""
        print("Installing Claude Code...")
        try:
            # Use the recommended native installation method from https://code.claude.com/docs/en/setup
            if platform.system() == "Windows":
                # Windows installation using PowerShell
                if shutil.which("powershell") is not None:
                    # Use PowerShell with explicit command execution to avoid injection
                    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", "irm https://claude.ai/install.ps1 | iex"], check=True)
                else:
                    # Fallback to CMD if PowerShell is not available
                    # Use direct download and execution without shell injection
                    subprocess.run(["cmd", "/c", "curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd"], check=True)
            elif platform.system() in ["Linux", "Darwin"]:
                # Linux/macOS installation using curl bash script
                # Use shell=False for better security
                subprocess.run(["bash", "-c", "curl -fsSL https://claude.ai/install.sh | bash"], check=True, shell=False)
            else:
                raise Exception("Unsupported platform")
            print("Claude Code installed successfully!")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Installation failed: {e}")

    def uninstall_claude(self) -> None:
        """Uninstall Claude Code using the recommended uninstallation method."""
        print("Uninstalling Claude Code...")
        try:
            # Use the recommended uninstallation method from https://code.claude.com/docs/en/setup
            if platform.system() == "Windows":
                # Windows uninstallation - remove the binary and version files
                # Manual removal approach as specified in official documentation
                print("Running Windows uninstall commands...")
                subprocess.run(["powershell", "-Command", "Remove-Item -Path \"$env:USERPROFILE\\.local\\bin\\claude.exe\" -Force; Remove-Item -Path \"$env:USERPROFILE\\.local\\share\\claude\" -Recurse -Force"], check=True)
            elif platform.system() in ["Linux", "Darwin"]:
                # Linux/macOS uninstallation - remove the binary and version files
                # Manual removal approach as specified in official documentation
                print("Running Linux/macOS uninstall commands...")
                # Use os.path.expanduser to properly expand the home directory
                local_bin = os.path.expanduser("~/.local/bin/claude")
                local_share = os.path.expanduser("~/.local/share/claude")
                print(f"Removing files from: {local_bin} and {local_share}")
                subprocess.run(["rm", "-f", local_bin], check=True)
                subprocess.run(["rm", "-rf", local_share], check=True)
            else:
                raise Exception("Unsupported platform")
            print("Claude Code uninstalled successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Uninstallation failed with subprocess error: {e}")
            raise Exception(f"Uninstallation failed: {e}")
        except Exception as e:
            print(f"Unexpected error during uninstall: {e}")
            raise

    def get_env_var(self, var_name: str) -> Optional[str]:
        """Get environment variable value."""
        return self.settings.get("env", {}).get(var_name)

    def set_env_var(self, var_name: str, value: str) -> None:
        """Set environment variable value."""
        if "env" not in self.settings:
            self.settings["env"] = {}
        self.settings["env"][var_name] = value
        self._save_settings()

    def list_env_vars(self) -> Dict[str, str]:
        """List all environment variables."""
        return self.settings.get("env", {})

    def get_system_info(self) -> Dict[str, str]:
        """Get system information."""
        return {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "architecture": platform.machine()
        }

def create_tui():
    """Create the TUI interface."""
    def main(stdscr):
        # Clear screen
        stdscr.clear()

        # Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        # Display main menu
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Header
            stdscr.addstr(0, 0, "Claude Code Launcher", curses.A_BOLD)
            if width > 0:
                stdscr.addstr(1, 0, "=" * min(width, 80))  # Limit line length to prevent overflow

            # Menu options
            menu_options = [
                "1. Install Claude Code",
                "2. Uninstall Claude Code",
                "3. Set Environment Variables",
                "4. List Environment Variables",
                "5. System Information",
                "6. Exit"
            ]

            # Ensure we don't write beyond screen boundaries
            max_menu_lines = min(len(menu_options), height - 5)  # Leave space for header and prompt
            for i in range(max_menu_lines):
                if i + 3 < height:  # Ensure we don't exceed screen height
                    stdscr.addstr(i + 3, 5, menu_options[i])

            if height > 1:
                stdscr.addstr(height - 1, 0, "Select an option (1-6): ")
            stdscr.refresh()

            # Get user input
            key = stdscr.getch()

            if key == ord('1'):
                handle_install(stdscr)
            elif key == ord('2'):
                handle_uninstall(stdscr)
            elif key == ord('3'):
                handle_set_env_vars(stdscr)
            elif key == ord('4'):
                handle_list_env_vars(stdscr)
            elif key == ord('5'):
                handle_system_info(stdscr)
            elif key == ord('6'):
                break
            else:
                if height > 2:
                    stdscr.addstr(height - 2, 0, "Invalid option. Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()

    def handle_install(stdscr):
        stdscr.clear()
        stdscr.addstr(0, 0, "Installing Claude Code...")
        stdscr.refresh()

        try:
            launcher = ClaudeLauncher()
            launcher.install_claude()
            stdscr.addstr(2, 0, "Installation completed successfully!")
        except Exception as e:
            stdscr.addstr(2, 0, f"Installation failed: {e}")

        stdscr.addstr(4, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()

    def handle_uninstall(stdscr):
        stdscr.clear()
        stdscr.addstr(0, 0, "Uninstalling Claude Code...")
        stdscr.refresh()

        try:
            launcher = ClaudeLauncher()
            print("Debug: About to call uninstall_claude from TUI")
            launcher.uninstall_claude()
            stdscr.addstr(2, 0, "Uninstallation completed successfully!")
            print("Debug: Uninstall completed successfully")
        except Exception as e:
            stdscr.addstr(2, 0, f"Uninstallation failed: {e}")
            print(f"Debug: Uninstall failed with error: {e}")

        stdscr.addstr(4, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()

    def handle_set_env_vars(stdscr):
        stdscr.clear()
        stdscr.addstr(0, 0, "Set Environment Variables")
        stdscr.addstr(1, 0, "=" * 40)

        # Display all environment variables
        env_vars = list(ENV_VARS.keys())
        current_selection = 0
        scroll_offset = 0

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Set Environment Variables")
            stdscr.addstr(1, 0, "=" * 40)

            # Get screen dimensions
            height, width = stdscr.getmaxyx()

            # Calculate how many variables we can display
            max_display_lines = height - 8  # Leave space for instructions and header

            # Adjust scroll offset if needed
            if current_selection < scroll_offset:
                scroll_offset = current_selection
            if current_selection >= scroll_offset + max_display_lines:
                scroll_offset = current_selection - max_display_lines + 1

            # Display variables within scroll bounds
            for i, var_name in enumerate(env_vars[scroll_offset:scroll_offset + max_display_lines]):
                display_index = i + 3
                if display_index >= height - 2:  # Prevent writing beyond screen
                    break

                if i + scroll_offset == current_selection:
                    stdscr.addstr(display_index, 2, f"> {var_name}", curses.A_REVERSE)
                else:
                    stdscr.addstr(display_index, 2, f"  {var_name}")

            stdscr.addstr(height - 2, 0, "Use arrow keys to navigate, Enter to set value, ESC to return")
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_selection = max(0, current_selection - 1)
            elif key == curses.KEY_DOWN:
                current_selection = min(len(env_vars) - 1, current_selection + 1)
            elif key == 10:  # Enter key
                # Get the current value
                var_name = env_vars[current_selection]
                current_value = ClaudeLauncher().get_env_var(var_name) or ""

                # Get new value from user
                stdscr.clear()
                stdscr.addstr(0, 0, f"Set value for {var_name}:")
                stdscr.addstr(2, 0, f"Current value: {current_value}")
                stdscr.addstr(4, 0, "Enter new value (or press Enter to keep current): ")
                stdscr.refresh()

                # Get input
                curses.echo()
                new_value = stdscr.getstr(5, 0, 100).decode('utf-8')
                curses.noecho()

                if new_value != "":
                    launcher = ClaudeLauncher()
                    launcher.set_env_var(var_name, new_value)
                    stdscr.addstr(7, 0, f"Value for {var_name} set to: {new_value}")
                else:
                    stdscr.addstr(7, 0, "Value unchanged.")

                stdscr.addstr(9, 0, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
            elif key == 27:  # ESC key
                break

    def handle_list_env_vars(stdscr):
        stdscr.clear()
        stdscr.addstr(0, 0, "Environment Variables")
        stdscr.addstr(1, 0, "=" * 40)

        launcher = ClaudeLauncher()
        env_vars = launcher.list_env_vars()

        if not env_vars:
            stdscr.addstr(3, 0, "No environment variables set.")
        else:
            for i, (var_name, var_value) in enumerate(env_vars.items()):
                stdscr.addstr(i + 3, 0, f"{var_name}: {var_value}")

        stdscr.addstr(len(env_vars) + 5, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()

    def handle_system_info(stdscr):
        stdscr.clear()
        stdscr.addstr(0, 0, "System Information")
        stdscr.addstr(1, 0, "=" * 40)

        launcher = ClaudeLauncher()
        info = launcher.get_system_info()

        stdscr.addstr(3, 0, f"Platform: {info['platform']}")
        stdscr.addstr(4, 0, f"Python Version: {info['python_version']}")
        stdscr.addstr(5, 0, f"Architecture: {info['architecture']}")

        stdscr.addstr(8, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()

    wrapper(main)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Claude Code Launcher')
    parser.add_argument('--tui', action='store_true', help='Run in TUI mode')
    parser.add_argument('--install', action='store_true', help='Install Claude Code')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall Claude Code')
    parser.add_argument('--set-env', nargs=2, metavar=('VAR', 'VALUE'),
                       help='Set environment variable')
    parser.add_argument('--list-env', action='store_true', help='List environment variables')

    args = parser.parse_args()

    launcher = ClaudeLauncher()

    print(f"Debug: Arguments received - tui:{args.tui}, install:{args.install}, uninstall:{args.uninstall}, set_env:{args.set_env}, list_env:{args.list_env}")
    print(f"Debug: Platform detected - {platform.system()}")

    if args.tui:
        print("Starting TUI mode...")
        create_tui()
    elif args.install:
        print("Starting installation...")
        try:
            launcher.install_claude()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.uninstall:
        print("Starting uninstallation...")
        try:
            launcher.uninstall_claude()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.set_env:
        var_name, value = args.set_env
        launcher.set_env_var(var_name, value)
        print(f"Set {var_name} to {value}")
    elif args.list_env:
        env_vars = launcher.list_env_vars()
        for var_name, var_value in env_vars.items():
            print(f"{var_name}: {var_value}")
    else:
        print("Starting TUI mode (default)...")
        # Default to TUI mode
        create_tui()

if __name__ == "__main__":
    main()