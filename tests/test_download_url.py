#!/usr/bin/env python3
"""
Unit tests for Claude Code download URL generation.

Tests verify that download URLs are correctly constructed for all
supported platform combinations.
"""

import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from claude_launcher import OSChecker, CLAUDE_DOWNLOAD_BASE


class TestOSChecker:
    """Tests for OSChecker class."""

    def test_get_os_platform_darwin(self):
        """Test OS detection for macOS."""
        with patch("sys.platform", "darwin"):
            assert OSChecker.get_os_platform() == "darwin"

    def test_get_os_platform_linux(self):
        """Test OS detection for Linux."""
        with patch("sys.platform", "linux"):
            assert OSChecker.get_os_platform() == "linux"

    def test_get_os_platform_windows(self):
        """Test OS detection for Windows."""
        with patch("sys.platform", "win32"):
            assert OSChecker.get_os_platform() == "win32"

    def test_get_os_platform_unknown(self):
        """Test OS detection for unknown platform."""
        with patch("sys.platform", "freebsd"):
            assert OSChecker.get_os_platform() == "unknown"

    def test_get_architecture_x64(self):
        """Test architecture detection for x86_64."""
        with patch("platform.machine", return_value="x86_64"):
            assert OSChecker.get_architecture() == "x64"

    def test_get_architecture_amd64(self):
        """Test architecture detection for amd64."""
        with patch("platform.machine", return_value="amd64"):
            assert OSChecker.get_architecture() == "x64"

    def test_get_architecture_arm64(self):
        """Test architecture detection for arm64."""
        with patch("platform.machine", return_value="arm64"):
            assert OSChecker.get_architecture() == "arm64"

    def test_get_architecture_aarch64(self):
        """Test architecture detection for aarch64."""
        with patch("platform.machine", return_value="aarch64"):
            assert OSChecker.get_architecture() == "arm64"


class TestDownloadURLGeneration:
    """Tests for download URL generation across all platforms."""

    def test_darwin_x64_url(self):
        """Test download URL for macOS x64."""
        with patch("sys.platform", "darwin"):
            with patch("platform.machine", return_value="x86_64"):
                platform_name, _ = OSChecker.get_download_info()
                assert platform_name == "darwin-x64"

    def test_darwin_arm64_url(self):
        """Test download URL for macOS ARM64."""
        with patch("sys.platform", "darwin"):
            with patch("platform.machine", return_value="arm64"):
                platform_name, _ = OSChecker.get_download_info()
                assert platform_name == "darwin-arm64"

    def test_linux_x64_url(self):
        """Test download URL for Linux x64."""
        with patch("sys.platform", "linux"):
            with patch("platform.machine", return_value="x86_64"):
                platform_name, _ = OSChecker.get_download_info()
                assert platform_name == "linux-x64"

    def test_linux_arm64_url(self):
        """Test download URL for Linux ARM64."""
        with patch("sys.platform", "linux"):
            with patch("platform.machine", return_value="arm64"):
                platform_name, _ = OSChecker.get_download_info()
                assert platform_name == "linux-arm64"

    def test_linux_arm64_musl_url(self):
        """Test download URL for Linux ARM64 with musl libc."""
        with patch("sys.platform", "linux"):
            with patch("platform.machine", return_value="arm64"):
                with patch.object(OSChecker, "_is_musl_linux", return_value=True):
                    platform_name, _ = OSChecker.get_download_info()
                    assert platform_name == "linux-arm64-musl"

    def test_linux_x64_musl_url(self):
        """Test download URL for Linux x64 with musl libc."""
        with patch("sys.platform", "linux"):
            with patch("platform.machine", return_value="x86_64"):
                with patch.object(OSChecker, "_is_musl_linux", return_value=True):
                    platform_name, _ = OSChecker.get_download_info()
                    assert platform_name == "linux-x64-musl"

    def test_windows_x64_url(self):
        """Test download URL for Windows x64."""
        with patch("sys.platform", "win32"):
            with patch("platform.machine", return_value="x86_64"):
                platform_name, _ = OSChecker.get_download_info()
                assert platform_name == "win32-x64"

    def test_windows_arm64_url(self):
        """Test download URL for Windows ARM64."""
        with patch("sys.platform", "win32"):
            with patch("platform.machine", return_value="arm64"):
                platform_name, _ = OSChecker.get_download_info()
                assert platform_name == "win32-arm64"


class TestDownloadURLBuilder:
    """Tests for ClaudeInstaller URL building."""

    def test_build_darwin_x64_url(self):
        """Build and verify macOS x64 download URL."""
        with patch("sys.platform", "darwin"):
            with patch("platform.machine", return_value="x86_64"):
                version = "2.1.42"
                expected_url = f"{CLAUDE_DOWNLOAD_BASE}/{version}/darwin-x64/claude"

                from claude_launcher import ClaudeInstaller
                installer = ClaudeInstaller(MagicMock())
                installer._latest_version = version

                url = installer.get_download_url()
                assert url == expected_url

    def test_build_darwin_arm64_url(self):
        """Build and verify macOS ARM64 download URL."""
        with patch("sys.platform", "darwin"):
            with patch("platform.machine", return_value="arm64"):
                version = "2.1.42"
                expected_url = f"{CLAUDE_DOWNLOAD_BASE}/{version}/darwin-arm64/claude"

                from claude_launcher import ClaudeInstaller
                installer = ClaudeInstaller(MagicMock())
                installer._latest_version = version

                url = installer.get_download_url()
                assert url == expected_url

    def test_build_linux_x64_url(self):
        """Build and verify Linux x64 download URL."""
        with patch("sys.platform", "linux"):
            with patch("platform.machine", return_value="x86_64"):
                version = "2.1.42"
                expected_url = f"{CLAUDE_DOWNLOAD_BASE}/{version}/linux-x64/claude"

                from claude_launcher import ClaudeInstaller
                installer = ClaudeInstaller(MagicMock())
                installer._latest_version = version

                url = installer.get_download_url()
                assert url == expected_url

    def test_build_linux_arm64_url(self):
        """Build and verify Linux ARM64 download URL."""
        with patch("sys.platform", "linux"):
            with patch("platform.machine", return_value="arm64"):
                version = "2.1.42"
                expected_url = f"{CLAUDE_DOWNLOAD_BASE}/{version}/linux-arm64/claude"

                from claude_launcher import ClaudeInstaller
                installer = ClaudeInstaller(MagicMock())
                installer._latest_version = version

                url = installer.get_download_url()
                assert url == expected_url

    def test_build_linux_x64_musl_url(self):
        """Build and verify Linux x64 musl download URL."""
        with patch("sys.platform", "linux"):
            with patch("platform.machine", return_value="x86_64"):
                version = "2.1.42"
                expected_url = f"{CLAUDE_DOWNLOAD_BASE}/{version}/linux-x64-musl/claude"

                from claude_launcher import ClaudeInstaller
                installer = ClaudeInstaller(MagicMock())
                installer._latest_version = version

                with patch.object(OSChecker, "_is_musl_linux", return_value=True):
                    url = installer.get_download_url()
                    assert url == expected_url

    def test_build_windows_x64_url(self):
        """Build and verify Windows x64 download URL."""
        with patch("sys.platform", "win32"):
            with patch("platform.machine", return_value="x86_64"):
                version = "2.1.42"
                expected_url = f"{CLAUDE_DOWNLOAD_BASE}/{version}/win32-x64/claude"

                from claude_launcher import ClaudeInstaller
                installer = ClaudeInstaller(MagicMock())
                installer._latest_version = version

                url = installer.get_download_url()
                assert url == expected_url

    def test_build_windows_arm64_url(self):
        """Build and verify Windows ARM64 download URL."""
        with patch("sys.platform", "win32"):
            with patch("platform.machine", return_value="arm64"):
                version = "2.1.42"
                expected_url = f"{CLAUDE_DOWNLOAD_BASE}/{version}/win32-arm64/claude"

                from claude_launcher import ClaudeInstaller
                installer = ClaudeInstaller(MagicMock())
                installer._latest_version = version

                url = installer.get_download_url()
                assert url == expected_url


class TestURLFormat:
    """Tests to verify URL format matches official install script pattern."""

    def test_url_pattern_matches_bootstrap_sh(self):
        """
        Verify URL pattern matches: $GCS_BUCKET/$version/$platform/claude

        From bootstrap.sh:
            download_file "$GCS_BUCKET/$version/$platform/claude"
        """
        with patch("sys.platform", "darwin"):
            with patch("platform.machine", return_value="x86_64"):
                version = "2.1.42"
                platform_name, _ = OSChecker.get_download_info()

                from claude_launcher import ClaudeInstaller
                installer = ClaudeInstaller(MagicMock())
                installer._latest_version = version

                url = installer.get_download_url()

                # Verify URL components
                assert url.startswith(CLAUDE_DOWNLOAD_BASE)
                assert f"/{version}/" in url
                assert f"/{platform_name}/" in url
                assert url.endswith("/claude")

                # Verify no archive extension
                assert not url.endswith(".tar.gz")
                assert not url.endswith(".zip")


class TestIsMuslLinux:
    """Tests for musl libc detection."""

    def test_is_musl_linux_detects_musl(self):
        """Test musl detection when libc contains musl."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="musl", stderr="", returncode=0)
            assert OSChecker._is_musl_linux() is True

    def test_is_musl_linux_detects_glibc(self):
        """Test musl detection when libc is glibc."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="glibc", stderr="", returncode=0)
            assert OSChecker._is_musl_linux() is False

    def test_is_musl_linux_handles_error(self):
        """Test musl detection falls back to file check on error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("ldd failed")
            with patch("os.path.exists", return_value=False):
                assert OSChecker._is_musl_linux() is False
