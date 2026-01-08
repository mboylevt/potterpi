#!/usr/bin/env python3
"""
Spell logging module for PotterPi
Logs detected spells with timestamps and aggressive log rotation
"""

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os

class SpellLogger:
    """Handles logging of detected spells with aggressive rotation"""

    def __init__(self, log_dir="/var/log/potterpi", log_file="potterpi.log",
                 max_bytes=10*1024*1024, backup_count=5):
        """
        Initialize the spell logger with rotating file handlers

        Args:
            log_dir: Directory for log files
            log_file: Name of the log file
            max_bytes: Maximum size per log file (default 10MB)
            backup_count: Number of backup files to keep (default 5)
        """
        self.log_path = os.path.join(log_dir, log_file)

        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger("PotterPi")
        self.logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs

        # Rotating file handler - aggressive rotation to prevent SD card fill
        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)

        # Console handler for debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Enhanced formatter with module name for better debugging
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_spell(self, spell_name, stats=None):
        """
        Log a detected spell

        Args:
            spell_name: Name of the spell that was detected
            stats: Optional dict of spell statistics
        """
        message = f"SPELL DETECTED: {spell_name}"

        if stats:
            message += f" | Points: {stats.get('num_points', 'N/A')}"
            message += f" | Straightness: {stats.get('straightness', 0):.2f}"
            message += f" | Distance: {stats.get('straight_distance', 0):.1f}px"

        self.logger.info(message)

    def log_info(self, message):
        """Log an informational message"""
        self.logger.info(message)

    def log_warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)

    def log_error(self, message):
        """Log an error message"""
        self.logger.error(message)

    def log_debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)

    def log_exception(self, message):
        """Log an exception with stack trace"""
        self.logger.exception(message)


def test_logger():
    """Test the spell logger"""
    logger = SpellLogger()

    logger.log_info("PotterPi spell logger test started")

    # Test spell logging
    test_stats = {
        "num_points": 25,
        "straightness": 0.87,
        "straight_distance": 145.3
    }

    logger.log_spell("Horizontal Line Right", test_stats)
    logger.log_spell("Vertical Line Up", test_stats)
    logger.log_spell("Horizontal Line Left")

    logger.log_info("Test completed successfully")

    print(f"\nLog file location: {logger.log_path}")
    print("Check the log file for output")


if __name__ == "__main__":
    test_logger()
