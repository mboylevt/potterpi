#!/usr/bin/env python3
"""
PotterPi - IR Wand Tracking System
Main application for detecting and recognizing Harry Potter-style spell gestures
"""

import time
import signal
import sys
import os
from .camera_capture import IRCamera
from .motion_tracker import WandTracker
from .spell_recognition import SpellRecognizer
from .spell_logger import SpellLogger
from .web_viewer import WebViewer
from .homeassistant_api import HomeAssistantAPI
from .config import Config

class PotterPi:
    """Main application for wand tracking and spell recognition"""

    def __init__(self, config_file="config.yaml"):
        """Initialize PotterPi components"""
        # Load configuration
        self.config = Config(config_file)

        # Set up logging with aggressive rotation
        self.logger = SpellLogger(
            log_dir=self.config.get("logging.dir", "/var/log/potterpi"),
            log_file=self.config.get("logging.file", "potterpi.log"),
            max_bytes=self.config.get("logging.max_bytes", 10*1024*1024),  # 10MB default
            backup_count=self.config.get("logging.backup_count", 5)
        )

        # Initialize camera
        self.camera = IRCamera(
            width=self.config.get("camera.width", 640),
            height=self.config.get("camera.height", 480),
            framerate=self.config.get("camera.framerate", 30)
        )

        # Initialize motion tracker
        self.tracker = WandTracker(
            brightness_threshold=self.config.get("tracker.brightness_threshold", 200),
            min_movement=self.config.get("tracker.min_movement", 5),
            path_length=self.config.get("tracker.path_length", 30)
        )

        # Initialize spell recognizer
        self.recognizer = SpellRecognizer(
            min_points=self.config.get("recognizer.min_points", 8),
            straightness_threshold=self.config.get("recognizer.straightness_threshold", 0.6)
        )

        # Initialize web viewer
        web_port = self.config.get("web_viewer.port", 5000)
        self.web_viewer = WebViewer(port=web_port)
        self.logger.log_info(f"Web viewer will be available at http://0.0.0.0:{web_port}")

        # Initialize Home Assistant API if configured
        self.ha_api = None
        ha_enabled = self.config.get("homeassistant.enabled", False)
        if ha_enabled:
            ha_url = self.config.get("homeassistant.url")
            ha_token = self.config.get("homeassistant.token")

            if ha_url and ha_token:
                self.ha_api = HomeAssistantAPI(ha_url, ha_token)
                self.logger.log_info("Home Assistant integration enabled")
                if self.ha_api.test_connection():
                    self.logger.log_info("Home Assistant connection successful")
                else:
                    self.logger.log_warning("Home Assistant connection failed - continuing without HA integration")
                    self.ha_api = None
            else:
                self.logger.log_warning("Home Assistant enabled but URL or token not configured")
        else:
            self.logger.log_info("Home Assistant integration disabled")

        self.running = False
        self.spell_cooldown = self.config.get("spell_cooldown", 1.0)
        self.last_spell_time = 0

    def start(self):
        """Start the PotterPi system"""
        self.logger.log_info("="*70)
        self.logger.log_info("PotterPi - IR Wand Tracking System")
        self.logger.log_info("="*70)
        self.logger.log_info("Starting up...")

        try:
            # Start web viewer
            self.web_viewer.start()
            self.logger.log_info("Web viewer started successfully")

            # Initialize camera
            self.camera.start()
            self.logger.log_info("Camera initialized successfully")

            # Set running flag
            self.running = True
            self.logger.log_info("="*70)
            self.logger.log_info("PotterPi is now active and watching for spells!")
            self.logger.log_info("="*70)

            # Run main loop
            self.run()

        except KeyboardInterrupt:
            self.logger.log_info("Keyboard interrupt received")
        except Exception as e:
            self.logger.log_exception(f"Failed to start PotterPi: {e}")
            raise
        finally:
            self.stop()

    def run(self):
        """Main processing loop"""
        frame_count = 0
        spell_count = 0

        try:
            while self.running:
                # Capture frame
                frame = self.camera.get_frame()
                frame_count += 1

                # Update tracker with new frame
                is_tracking = self.tracker.update(frame)

                # Update web viewer with current frame and tracking path
                current_path = self.tracker.get_path() if is_tracking else None
                self.web_viewer.update_frame(frame, current_path)

                # Check if spell casting just ended
                if not is_tracking and len(self.tracker.path) > 0:
                    # Get the completed path
                    path = self.tracker.get_path()
                    cast_duration = self.tracker.get_cast_duration()

                    self.logger.log_debug(f"Spell cast ended: {len(path)} points over {cast_duration:.2f}s")

                    # Check cooldown
                    current_time = time.time()
                    if current_time - self.last_spell_time < self.spell_cooldown:
                        self.logger.log_debug(f"Spell rejected: within cooldown period ({self.spell_cooldown}s)")
                        self.tracker.reset()
                        continue

                    # Try to recognize spell
                    spell = self.recognizer.recognize(path)

                    if spell and spell != SpellRecognizer.UNKNOWN:
                        # Get spell statistics
                        stats = self.recognizer.get_spell_stats(path)

                        # Log the spell
                        self.logger.log_spell(spell, stats)

                        # Update web viewer
                        self.web_viewer.log_spell(spell)

                        # Trigger Home Assistant action if configured
                        if self.ha_api:
                            try:
                                success = self.ha_api.trigger_spell_action(spell, stats)
                                if success:
                                    self.logger.log_info(f"Home Assistant action triggered for: {spell}")
                                else:
                                    self.logger.log_error(f"Failed to trigger Home Assistant action for: {spell}")
                            except Exception as e:
                                self.logger.log_error(f"Error triggering Home Assistant action: {e}")

                        # Update counters
                        spell_count += 1
                        self.last_spell_time = current_time

                    # Reset tracker for next spell
                    self.tracker.reset()

                # Small delay to control framerate
                time.sleep(0.03)  # ~30 fps

                # Periodic status update
                if frame_count % 900 == 0:  # Every 30 seconds at 30fps
                    self.logger.log_info(f"Status: {frame_count} frames processed, {spell_count} spells detected")

        except KeyboardInterrupt:
            self.logger.log_info("Keyboard interrupt received")
        except Exception as e:
            self.logger.log_exception(f"Error in main loop: {e}")
            raise

    def stop(self):
        """Stop the PotterPi system"""
        self.logger.log_info("="*70)
        self.logger.log_info("Shutting down PotterPi...")
        self.running = False

        if self.camera:
            self.camera.stop()

        self.logger.log_info("PotterPi stopped successfully")
        self.logger.log_info("="*70)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutdown signal received...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check for config file argument
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"

    # Create and start PotterPi
    potterpi = PotterPi(config_file)

    try:
        potterpi.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
