"""
PotterPi - IR Wand Tracking System for Raspberry Pi

A motion tracking system that detects and recognizes magic spells cast with an IR LED wand,
integrating with Home Assistant for home automation.
"""

__version__ = "1.0.0"
__author__ = "Matt Boyle"

# Import only what's needed - let users import specific modules
# This avoids importing camera dependencies on non-Raspberry Pi systems

__all__ = [
    "main",
    "SpellRecognizer",
    "MotionTracker",
    "SpellLogger",
    "HomeAssistantAPI",
]

# Lazy imports for testing compatibility
def _get_main():
    from .potterpi import main
    return main

def _get_spell_recognizer():
    from .spell_recognition import SpellRecognizer
    return SpellRecognizer

def _get_motion_tracker():
    from .motion_tracker import MotionTracker
    return MotionTracker

def _get_spell_logger():
    from .spell_logger import SpellLogger
    return SpellLogger

def _get_homeassistant_api():
    from .homeassistant_api import HomeAssistantAPI
    return HomeAssistantAPI
