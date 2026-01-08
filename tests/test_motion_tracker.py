#!/usr/bin/env python3
"""
Unit tests for motion tracking module
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from potterpi.motion_tracker import WandTracker
import numpy as np


class TestWandTracker:
    """Test cases for WandTracker class"""

    def setup_method(self):
        """Set up test fixture"""
        self.tracker = WandTracker(
            brightness_threshold=200,
            min_movement=5,
            path_length=30
        )

    def create_test_frame(self, bright_spot=None, brightness=255):
        """
        Create a test frame with optional bright spot

        Args:
            bright_spot: (x, y) tuple for bright spot location
            brightness: Brightness value for the spot (0-255)

        Returns:
            numpy array representing a grayscale frame
        """
        frame = np.zeros((480, 640), dtype=np.uint8)

        if bright_spot:
            x, y = bright_spot
            # Create a bright region with enough pixels above threshold
            # Use a larger, flatter circle for better detection
            radius = 6
            for dy in range(-radius, radius+1):
                for dx in range(-radius, radius+1):
                    if 0 <= y+dy < 480 and 0 <= x+dx < 640:
                        distance = np.sqrt(dx**2 + dy**2)
                        if distance <= radius:
                            # Create solid brightness in center, slight falloff at edges
                            if distance < radius - 2:
                                frame[y+dy, x+dx] = brightness
                            else:
                                frame[y+dy, x+dx] = int(brightness * 0.85)

        return frame

    def test_find_wand_bright_spot(self):
        """Test finding a single bright spot"""
        frame = self.create_test_frame(bright_spot=(320, 240), brightness=255)
        position = self.tracker.find_wand(frame)

        assert position is not None
        # Should be close to (320, 240)
        assert abs(position[0] - 320) < 5
        assert abs(position[1] - 240) < 5

    def test_find_wand_no_bright_spot(self):
        """Test with no bright spots"""
        frame = self.create_test_frame()  # All zeros
        position = self.tracker.find_wand(frame)

        assert position is None

    def test_find_wand_below_threshold(self):
        """Test with spot below brightness threshold"""
        frame = self.create_test_frame(bright_spot=(320, 240), brightness=150)
        position = self.tracker.find_wand(frame)

        assert position is None

    def test_update_starts_tracking(self):
        """Test that update starts tracking when wand detected"""
        frame = self.create_test_frame(bright_spot=(100, 100))
        is_tracking = self.tracker.update(frame)

        assert is_tracking is True
        assert self.tracker.is_casting is True
        assert len(self.tracker.path) == 1

    def test_update_continues_tracking(self):
        """Test that update continues tracking across frames"""
        # First frame
        frame1 = self.create_test_frame(bright_spot=(100, 100))
        self.tracker.update(frame1)

        # Second frame (moved 10 pixels right)
        frame2 = self.create_test_frame(bright_spot=(110, 100))
        is_tracking = self.tracker.update(frame2)

        assert is_tracking is True
        assert len(self.tracker.path) == 2

    def test_update_ignores_small_movement(self):
        """Test that small movements are ignored"""
        # First frame
        frame1 = self.create_test_frame(bright_spot=(100, 100))
        self.tracker.update(frame1)

        # Second frame (moved only 2 pixels - below min_movement=5)
        frame2 = self.create_test_frame(bright_spot=(102, 100))
        self.tracker.update(frame2)

        # Should still have only 1 point
        assert len(self.tracker.path) == 1

    def test_update_stops_tracking_when_lost(self):
        """Test that tracking stops when wand is lost"""
        # Start tracking
        frame1 = self.create_test_frame(bright_spot=(100, 100))
        self.tracker.update(frame1)

        frame2 = self.create_test_frame(bright_spot=(110, 100))
        self.tracker.update(frame2)

        # Lose the wand
        frame3 = self.create_test_frame()  # No bright spot
        is_tracking = self.tracker.update(frame3)

        assert is_tracking is False
        assert self.tracker.is_casting is False

    def test_get_path_returns_list(self):
        """Test that get_path returns the tracked path"""
        positions = [(100, 100), (110, 100), (120, 100)]

        for pos in positions:
            frame = self.create_test_frame(bright_spot=pos)
            self.tracker.update(frame)

        path = self.tracker.get_path()

        assert isinstance(path, list)
        assert len(path) == 3

    def test_reset_clears_state(self):
        """Test that reset clears all tracking state"""
        frame = self.create_test_frame(bright_spot=(100, 100))
        self.tracker.update(frame)

        self.tracker.reset()

        assert len(self.tracker.path) == 0
        assert self.tracker.last_position is None
        assert self.tracker.is_casting is False
        assert self.tracker.cast_start_time is None

    def test_path_length_limit(self):
        """Test that path respects max length"""
        tracker = WandTracker(path_length=5)

        # Add more points than the limit
        for i in range(10):
            frame = self.create_test_frame(bright_spot=(100 + i*10, 100))
            tracker.update(frame)

        # Should only keep the last 5 points
        assert len(tracker.path) <= 5

    def test_get_cast_duration(self):
        """Test that cast duration is tracked"""
        import time

        frame = self.create_test_frame(bright_spot=(100, 100))
        self.tracker.update(frame)

        time.sleep(0.1)

        duration = self.tracker.get_cast_duration()
        assert duration >= 0.1
        assert duration < 0.2  # Should be close to 0.1 seconds

    def test_multiple_bright_spots_finds_brightest(self):
        """Test that tracker finds the brightest spot when multiple exist"""
        frame = np.zeros((480, 640), dtype=np.uint8)

        # Add two bright spots with different brightness
        # Dimmer spot at (100, 100)
        frame[98:103, 98:103] = 220

        # Brighter spot at (300, 300)
        frame[298:303, 298:303] = 255

        position = self.tracker.find_wand(frame)

        # Should find the brighter spot at (300, 300)
        assert position is not None
        assert abs(position[0] - 300) < 10
        assert abs(position[1] - 300) < 10

    def test_custom_brightness_threshold(self):
        """Test with custom brightness threshold"""
        tracker = WandTracker(brightness_threshold=230)

        # Spot with brightness 220 should not be detected
        frame = self.create_test_frame(bright_spot=(100, 100), brightness=220)
        position = tracker.find_wand(frame)
        assert position is None

        # Spot with brightness 240 should be detected
        frame = self.create_test_frame(bright_spot=(100, 100), brightness=240)
        position = tracker.find_wand(frame)
        assert position is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
