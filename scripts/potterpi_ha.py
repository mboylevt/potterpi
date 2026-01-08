#!/usr/bin/env python3
"""
PotterPi - IR Wand Tracking System with Home Assistant Integration
Main application for detecting and recognizing Harry Potter-style spell gestures
"""

import time
import signal
import sys
from potterpi.camera_capture import IRCamera
from potterpi.motion_tracker import WandTracker
from potterpi.spell_recognition import SpellRecognizer
from potterpi.spell_logger import SpellLogger
from potterpi.config import Config
from potterpi.homeassistant_api import HomeAssistantAPI

class PotterPi:
    """Main application for wand tracking and spell recognition"""
    
    def __init__(self, config_file="/home/matt/potterpi/config.json"):
        """Initialize PotterPi components"""
        # Load configuration
        self.config = Config(config_file)
        
        # Initialize logger
        log_dir = self.config.get("logging.log_dir", "/var/log/potterpi")
        self.logger = SpellLogger(log_dir=log_dir)
        
        # Initialize camera (skip if not available)
        self.camera_available = False
        self.camera = None
        # Initialize tracker
        self.tracker = WandTracker(
            brightness_threshold=self.config.get("tracking.brightness_threshold", 200),
            min_movement=self.config.get("tracking.min_movement", 5),
            path_length=self.config.get("tracking.path_length", 30)
        )
        
        # Initialize recognizer
        self.recognizer = SpellRecognizer(
            min_points=self.config.get("recognition.min_points", 8),
            straightness_threshold=self.config.get("recognition.straightness_threshold", 0.6)
        )
        
        # Initialize Home Assistant integration
        self.ha_enabled = self.config.get("homeassistant.enabled", False)
        self.ha_api = None
        
        if self.ha_enabled:
            ha_url = self.config.get("homeassistant.url")
            ha_token = self.config.get("homeassistant.token")
            
            if ha_url and ha_token:
                self.ha_api = HomeAssistantAPI(ha_url, ha_token)
                self.logger.log_info(f"Home Assistant integration enabled: {ha_url}")
            else:
                self.logger.log_error("Home Assistant enabled but missing URL or token")
                self.ha_enabled = False
        
        self.running = False
        self.spell_cooldown = self.config.get("logging.spell_cooldown", 1.0)
        self.last_spell_time = 0
        
    def start(self):
        """Start the PotterPi system"""
        self.logger.log_info("="*50)
        self.logger.log_info("PotterPi starting up...")
        self.logger.log_info("="*50)
        
        if self.ha_enabled:
            self.logger.log_info("Testing Home Assistant connection...")
            if self.ha_api.test_connection():
                self.logger.log_info("Home Assistant connection successful!")
            else:
                self.logger.log_error("Home Assistant connection failed!")
        
        try:
            # Initialize camera if available
            if self.camera_available:
                self.camera.start()
                self.logger.log_info("Camera initialized successfully")
            else:
                self.logger.log_info("Running in test mode without camera")
            
            # Set running flag
            self.running = True
            self.logger.log_info("PotterPi is now active and watching for spells!")
            
            # Run main loop
            if self.camera_available:
                self.run()
            else:
                self.run_test_mode()
            
        except Exception as e:
            self.logger.log_error(f"Failed to start PotterPi: {e}")
            raise
    
    def run(self):
        """Main processing loop"""
        frame_count = 0
        
        try:
            while self.running:
                # Capture frame
                frame = self.camera.get_frame()
                frame_count += 1
                
                # Update tracker with new frame
                is_tracking = self.tracker.update(frame)
                
                # Check if spell casting just ended
                if not is_tracking and len(self.tracker.path) > 0:
                    self.process_completed_spell()
                
                # Small delay to control framerate
                time.sleep(0.03)  # ~30 fps
                
                # Periodic status update
                if frame_count % 300 == 0:  # Every 10 seconds at 30fps
                    self.logger.log_info(f"System running - {frame_count} frames processed")
                    
        except KeyboardInterrupt:
            self.logger.log_info("Keyboard interrupt received")
        except Exception as e:
            self.logger.log_error(f"Error in main loop: {e}")
            raise
    
    def run_test_mode(self):
        """Run in test mode for testing Home Assistant integration without camera"""
        self.logger.log_info("Test mode: Simulating spell detection every 5 seconds")
        self.logger.log_info("Press Ctrl+C to stop")
        
        spells = [
            SpellRecognizer.HORIZONTAL_RIGHT,
            SpellRecognizer.HORIZONTAL_LEFT,
            SpellRecognizer.VERTICAL_UP,
            SpellRecognizer.VERTICAL_DOWN
        ]
        
        spell_index = 0
        
        try:
            while self.running:
                time.sleep(5)
                
                # Simulate a spell
                spell = spells[spell_index]
                spell_index = (spell_index + 1) % len(spells)
                
                # Create fake stats
                stats = {
                    "num_points": 20,
                    "straightness": 0.85,
                    "straight_distance": 120.0
                }
                
                # Log and trigger
                self.logger.log_spell(spell, stats)
                
                if self.ha_enabled and self.ha_api:
                    success = self.ha_api.trigger_spell_action(spell, stats)
                    if success:
                        self.logger.log_info(f"  → Triggered Home Assistant event")
                    else:
                        self.logger.log_error(f"  → Failed to trigger Home Assistant event")
                        
        except KeyboardInterrupt:
            self.logger.log_info("Keyboard interrupt received")
    
    def process_completed_spell(self):
        """Process a completed spell gesture"""
        # Get the completed path
        path = self.tracker.get_path()
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_spell_time < self.spell_cooldown:
            self.tracker.reset()
            return
        
        # Try to recognize spell
        spell = self.recognizer.recognize(path)
        
        if spell and spell != SpellRecognizer.UNKNOWN:
            # Get spell statistics
            stats = self.recognizer.get_spell_stats(path)
            
            # Log the spell
            self.logger.log_spell(spell, stats)
            
            # Trigger Home Assistant if enabled
            if self.ha_enabled and self.ha_api:
                success = self.ha_api.trigger_spell_action(spell, stats)
                if success:
                    self.logger.log_info(f"  → Triggered Home Assistant event")
                else:
                    self.logger.log_error(f"  → Failed to trigger Home Assistant event")
            
            # Update last spell time
            self.last_spell_time = current_time
        
        # Reset tracker for next spell
        self.tracker.reset()
    
    def stop(self):
        """Stop the PotterPi system"""
        self.logger.log_info("Shutting down PotterPi...")
        self.running = False
        
        if self.camera and self.camera_available:
            self.camera.stop()
        
        self.logger.log_info("PotterPi stopped")
        self.logger.log_info("="*50)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutdown signal received...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start PotterPi
    potterpi = PotterPi()
    
    try:
        potterpi.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        potterpi.stop()


if __name__ == "__main__":
    main()
