#!/usr/bin/env python3
"""
Test file for Claude Launcher functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
import json

# Add the current directory to the path so we can import claude_launcher
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import claude_launcher

class TestClaudeLauncher(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary settings file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.settings_file = Path(self.temp_dir.name) / "settings.json"

        # Monkey patch the settings file path for testing
        self.launcher = claude_launcher.ClaudeLauncher()
        # Override the settings file path for testing
        self.launcher.settings_file = self.settings_file
        self.launcher.settings_dir = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up after each test method."""
        self.temp_dir.cleanup()

    def test_load_settings_empty(self):
        """Test loading settings when file doesn't exist."""
        # This should create a default settings structure
        settings = self.launcher._load_settings()
        self.assertIn("env", settings)
        self.assertEqual(settings["env"], {})

    def test_save_and_load_settings(self):
        """Test saving and loading settings."""
        # Set a test environment variable
        self.launcher.set_env_var("TEST_VAR", "test_value")

        # Load settings
        loaded_settings = self.launcher._load_settings()
        self.assertIn("env", loaded_settings)
        self.assertEqual(loaded_settings["env"]["TEST_VAR"], "test_value")

    def test_get_and_set_env_var(self):
        """Test getting and setting environment variables."""
        # Set a variable
        self.launcher.set_env_var("API_KEY", "test_key_123")

        # Get the variable
        value = self.launcher.get_env_var("API_KEY")
        self.assertEqual(value, "test_key_123")

        # Test getting non-existent variable
        value = self.launcher.get_env_var("NONEXISTENT")
        self.assertIsNone(value)

    def test_list_env_vars(self):
        """Test listing environment variables."""
        # Set some variables
        self.launcher.set_env_var("VAR1", "value1")
        self.launcher.set_env_var("VAR2", "value2")

        # List all variables
        env_vars = self.launcher.list_env_vars()
        self.assertIn("VAR1", env_vars)
        self.assertIn("VAR2", env_vars)
        self.assertEqual(env_vars["VAR1"], "value1")
        self.assertEqual(env_vars["VAR2"], "value2")

if __name__ == '__main__':
    unittest.main()