#!/usr/bin/env python3
"""
Unit tests for spell logger module
"""

import pytest
import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from potterpi.spell_logger import SpellLogger


class TestSpellLogger:
    """Test cases for SpellLogger class"""

    def setup_method(self):
        """Set up test fixture"""
        # Create a temporary directory for logs
        self.test_log_dir = tempfile.mkdtemp()
        self.logger = SpellLogger(log_dir=self.test_log_dir, log_file="test_spells.log")

    def teardown_method(self):
        """Clean up test fixture"""
        # Flush and close all handlers to ensure logs are written
        for handler in self.logger.logger.handlers[:]:
            handler.flush()
            handler.close()
            self.logger.logger.removeHandler(handler)

        # Remove temporary directory
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)

    def _flush_and_read_log(self):
        """Helper to flush handlers and read log file"""
        # Flush all handlers
        for handler in self.logger.logger.handlers:
            handler.flush()

        # Read log file
        with open(self.logger.log_path, 'r') as f:
            return f.read()

    def test_logger_initialization(self):
        """Test logger initialization"""
        assert self.logger.log_path == os.path.join(self.test_log_dir, "test_spells.log")
        assert os.path.exists(self.test_log_dir)

    def test_log_directory_creation(self):
        """Test that log directory is created if it doesn't exist"""
        new_dir = os.path.join(self.test_log_dir, "nested", "dir")
        logger = SpellLogger(log_dir=new_dir)

        assert os.path.exists(new_dir)

        # Cleanup
        shutil.rmtree(os.path.join(self.test_log_dir, "nested"))

    def test_log_spell_basic(self):
        """Test logging a basic spell"""
        self.logger.log_spell("Horizontal Line Right")

        # Check that log file exists
        assert os.path.exists(self.logger.log_path)

        # Read log file and verify content
        content = self._flush_and_read_log()

        assert "SPELL DETECTED: Horizontal Line Right" in content

    def test_log_spell_with_stats(self):
        """Test logging a spell with statistics"""
        stats = {
            "num_points": 25,
            "straightness": 0.87,
            "straight_distance": 145.3
        }

        self.logger.log_spell("Vertical Line Up", stats)

        content = self._flush_and_read_log()

        assert "SPELL DETECTED: Vertical Line Up" in content
        assert "Points: 25" in content
        assert "Straightness: 0.87" in content
        assert "Distance: 145.3px" in content

    def test_log_info(self):
        """Test logging info messages"""
        self.logger.log_info("Test info message")

        content = self._flush_and_read_log()

        assert "INFO" in content
        assert "Test info message" in content

    def test_log_error(self):
        """Test logging error messages"""
        self.logger.log_error("Test error message")

        content = self._flush_and_read_log()

        assert "ERROR" in content
        assert "Test error message" in content

    def test_multiple_spells_logged(self):
        """Test logging multiple spells"""
        spells = [
            "Horizontal Line Right",
            "Horizontal Line Left",
            "Vertical Line Up",
            "Vertical Line Down"
        ]

        for spell in spells:
            self.logger.log_spell(spell)

        content = self._flush_and_read_log()

        for spell in spells:
            assert f"SPELL DETECTED: {spell}" in content

    def test_log_format_includes_timestamp(self):
        """Test that logs include timestamp"""
        self.logger.log_info("Test message")

        content = self._flush_and_read_log()

        # Check for timestamp pattern (YYYY-MM-DD HH:MM:SS)
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.search(timestamp_pattern, content)

    def test_log_spell_with_partial_stats(self):
        """Test logging spell with incomplete statistics"""
        stats = {
            "num_points": 15,
            # Missing straightness and distance
        }

        self.logger.log_spell("Test Spell", stats)

        content = self._flush_and_read_log()

        assert "SPELL DETECTED: Test Spell" in content
        assert "Points: 15" in content

    def test_concurrent_logging(self):
        """Test that multiple log calls work correctly"""
        # Simulate rapid logging
        for i in range(10):
            self.logger.log_info(f"Message {i}")

        content = self._flush_and_read_log()
        lines = content.splitlines()

        # Should have at least 10 lines (may have more due to formatting)
        assert len([line for line in lines if "Message" in line]) == 10

    def test_logger_singleton_behavior(self):
        """Test that logger handles multiple log calls from same instance"""
        # Test that a single logger can handle multiple messages
        self.logger.log_info("From first call")
        self.logger.log_info("From second call")

        content = self._flush_and_read_log()

        assert "From first call" in content
        assert "From second call" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
