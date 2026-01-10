#!/usr/bin/env python3
"""
Configuration management for PotterPi
Loads settings from config file and environment variables
"""

import os
import json
from typing import Optional

class Config:
    """Manages PotterPi configuration"""
    
    def __init__(self, config_file: str = "/home/matt/potterpi/config.json"):
        """
        Initialize configuration
        
        Args:
            config_file: Path to JSON configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file or create defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return self._default_config()
        else:
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            "camera": {
                "width": 640,
                "height": 480,
                "framerate": 30,
                "exposure_time": 10000,
                "analog_gain": 2.0
            },
            "tracking": {
                "brightness_threshold": 200,
                "min_movement": 5,
                "path_length": 30
            },
            "recognition": {
                "min_points": 8,
                "straightness_threshold": 0.6,
                "min_distance": 30
            },
            "homeassistant": {
                "enabled": False,
                "url": "http://192.168.2.103:8123",
                "token": ""
            },
            "logging": {
                "log_dir": "/var/log/potterpi",
                "spell_cooldown": 1.0
            },
            "web_viewer": {
                "port": 8080
            }
        }
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get(self, key_path: str, default=None):
        """
        Get a configuration value using dot notation
        
        Args:
            key_path: Path to config value (e.g., "camera.width")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value):
        """
        Set a configuration value using dot notation
        
        Args:
            key_path: Path to config value (e.g., "camera.width")
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value


def setup_homeassistant():
    """Interactive setup for Home Assistant integration"""
    config = Config()
    
    print("Home Assistant Integration Setup")
    print("=" * 50)
    
    # Get URL
    url = input(f"Home Assistant URL [{config.get(homeassistant.url)}]: ").strip()
    if url:
        config.set(homeassistant.url, url)
    
    # Get token
    token = input("Home Assistant Token (long-lived access token): ").strip()
    if token:
        config.set(homeassistant.token, token)
    
    # Enable integration
    enable = input("Enable Home Assistant integration? [y/N]: ").strip().lower()
    config.set(homeassistant.enabled, enable == y)
    
    # Save config
    config.save_config()
    
    print("\nConfiguration saved!")
    print(f"Home Assistant integration: {ENABLED if config.get(homeassistant.enabled) else DISABLED}")


if __name__ == "__main__":
    setup_homeassistant()
