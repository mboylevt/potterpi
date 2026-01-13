#!/usr/bin/env python3
"""
Unit tests for configuration module
"""

import pytest
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from potterpi.config import Config


class TestConfig:
    """Test cases for Config class"""

    def test_default_config(self):
        """Test that default configuration is created"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")

            # Check default values
            assert config.get("camera.width") == 640
            assert config.get("camera.height") == 480
            assert config.get("camera.framerate") == 30
            assert config.get("tracking.brightness_threshold") == 200
            assert config.get("recognition.min_points") == 8
            assert config.get("homeassistant.enabled") is False
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_load_existing_config(self):
        """Test loading from existing config file"""
        config_data = {
            "camera": {"width": 1280, "height": 720},
            "tracking": {"brightness_threshold": 180},
            "custom": {"value": "test"}
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")

            assert config.get("camera.width") == 1280
            assert config.get("camera.height") == 720
            assert config.get("tracking.brightness_threshold") == 180
            assert config.get("custom.value") == "test"
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_get_with_default(self):
        """Test getting value with default"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")

            # Existing key
            assert config.get("camera.width", 999) == 640

            # Non-existing key with default
            assert config.get("nonexistent.key", "default_value") == "default_value"

            # Non-existing key without default
            assert config.get("another.nonexistent") is None
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_set_new_value(self):
        """Test setting a new value"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")

            config.set("camera.width", 1920)
            assert config.get("camera.width") == 1920

            config.set("new.nested.value", 42)
            assert config.get("new.nested.value") == 42
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_set_deep_nested_value(self):
        """Test setting deeply nested values"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")

            config.set("level1.level2.level3.value", "deep")
            assert config.get("level1.level2.level3.value") == "deep"
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_save_config(self):
        """Test saving configuration to file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")
            config.set("camera.width", 1920)
            config.set("test.value", "saved")
            config.save_config()

            # Load the file and verify
            with open(config_file, 'r') as f:
                saved_data = json.load(f)

            assert saved_data["camera"]["width"] == 1920
            assert saved_data["test"]["value"] == "saved"
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_reload_saved_config(self):
        """Test that saved config can be reloaded"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            # Create and save config
            config1 = Config(config_file, secrets_file="/nonexistent/secrets.json")
            config1.set("camera.width", 1920)
            config1.set("custom.setting", "test123")
            config1.save_config()

            # Load in new instance
            config2 = Config(config_file, secrets_file="/nonexistent/secrets.json")
            assert config2.get("camera.width") == 1920
            assert config2.get("custom.setting") == "test123"
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_get_nested_dict(self):
        """Test getting entire nested dictionary"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")

            camera_config = config.get("camera")
            assert isinstance(camera_config, dict)
            assert camera_config["width"] == 640
            assert camera_config["height"] == 480
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_malformed_config_file(self):
        """Test handling of malformed config file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("{ this is not valid json }")
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")
            # Should fall back to defaults
            assert config.get("camera.width") == 640
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_overwrite_existing_value(self):
        """Test overwriting an existing value"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")

            assert config.get("camera.width") == 640
            config.set("camera.width", 1920)
            assert config.get("camera.width") == 1920
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_homeassistant_config_section(self):
        """Test Home Assistant configuration section"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name

        try:
            config = Config(config_file, secrets_file="/nonexistent/secrets.json")

            # Test default HA config
            assert config.get("homeassistant.enabled") is False
            assert config.get("homeassistant.url") == "http://192.168.2.103:8123"
            assert config.get("homeassistant.token") == ""

            # Set HA config
            config.set("homeassistant.enabled", True)
            config.set("homeassistant.token", "test_token_123")

            assert config.get("homeassistant.enabled") is True
            assert config.get("homeassistant.token") == "test_token_123"
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
