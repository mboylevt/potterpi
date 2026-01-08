#!/usr/bin/env python3
"""
Motion tracking module for PotterPi
Tracks the IR-reflective wand tip movement through the frame
"""

import numpy as np
import cv2
from collections import deque
import time
import logging

# Set up module-level logger
logger = logging.getLogger("PotterPi")

class WandTracker:
    """Tracks the bright IR reflection from the wand tip"""

    def __init__(self, brightness_threshold=200, min_movement=5, path_length=30):
        """
        Initialize the wand tracker

        Args:
            brightness_threshold: Minimum brightness to consider as wand (0-255)
            min_movement: Minimum pixel movement to record a point
            path_length: Maximum number of points to keep in path history
        """
        self.brightness_threshold = brightness_threshold
        self.min_movement = min_movement
        self.path_length = path_length

        # Store the path of wand movement
        self.path = deque(maxlen=path_length)
        self.last_position = None
        self.is_casting = False
        self.cast_start_time = None

        logger.debug(f"WandTracker initialized: threshold={brightness_threshold}, min_movement={min_movement}, path_length={path_length}")
        
    def find_wand(self, frame):
        """
        Find the brightest point in the frame (wand tip)
        
        Args:
            frame: Grayscale numpy array
            
        Returns:
            tuple: (x, y) position of wand, or None if not found
        """
        # Apply threshold to find very bright points
        _, thresh = cv2.threshold(frame, self.brightness_threshold, 255, cv2.THRESH_BINARY)
        
        # Find contours of bright regions
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # Find the brightest region (likely the wand tip)
        brightest_region = None
        max_brightness = 0
        
        for contour in contours:
            # Create mask for this contour
            mask = np.zeros(frame.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            
            # Get mean brightness of this region
            mean_brightness = cv2.mean(frame, mask=mask)[0]
            
            if mean_brightness > max_brightness:
                max_brightness = mean_brightness
                brightest_region = contour
        
        if brightest_region is not None:
            # Get center of the brightest region
            M = cv2.moments(brightest_region)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy)
        
        return None
    
    def update(self, frame):
        """
        Update tracker with a new frame

        Args:
            frame: Grayscale numpy array

        Returns:
            bool: True if actively tracking a cast
        """
        position = self.find_wand(frame)

        if position is None:
            # Lost the wand
            if self.is_casting and len(self.path) > 0:
                # Spell might be complete
                logger.debug(f"Wand lost - spell cast ended with {len(self.path)} points")
                self.is_casting = False
            self.last_position = None
            return False

        # Check if this is meaningful movement
        if self.last_position is not None:
            distance = np.sqrt((position[0] - self.last_position[0])**2 +
                             (position[1] - self.last_position[1])**2)

            if distance < self.min_movement:
                # Not enough movement, skip
                return self.is_casting

        # Record this position
        if not self.is_casting:
            # Starting a new cast
            logger.debug(f"Wand detected at {position} - starting spell cast tracking")
            self.is_casting = True
            self.cast_start_time = time.time()
            self.path.clear()

        self.path.append(position)
        self.last_position = position

        return True
    
    def get_path(self):
        """
        Get the current wand path
        
        Returns:
            list: List of (x, y) tuples representing the path
        """
        return list(self.path)
    
    def reset(self):
        """Reset the tracker to prepare for a new spell"""
        self.path.clear()
        self.last_position = None
        self.is_casting = False
        self.cast_start_time = None
    
    def get_cast_duration(self):
        """Get the duration of the current cast in seconds"""
        if self.cast_start_time:
            return time.time() - self.cast_start_time
        return 0


def test_tracker():
    """Test the tracker with the camera"""
    from camera_capture import IRCamera
    
    camera = IRCamera()
    tracker = WandTracker()
    
    try:
        camera.start()
        print("Tracking wand movement. Wave wand in front of camera...")
        print("Press Ctrl+C to stop")
        
        while True:
            frame = camera.get_frame()
            is_tracking = tracker.update(frame)
            
            if is_tracking:
                path = tracker.get_path()
                print(f"Tracking: {len(path)} points, Duration: {tracker.get_cast_duration():.2f}s")
            elif len(tracker.path) == 0 and not is_tracking:
                # Spell completed
                path = tracker.get_path()
                if len(path) > 5:  # Minimum points for a spell
                    print(f"Spell completed! {len(path)} points over {tracker.get_cast_duration():.2f}s")
                tracker.reset()
            
            time.sleep(0.03)  # ~30 fps
            
    except KeyboardInterrupt:
        print("\nStopping tracker test")
    finally:
        camera.stop()


if __name__ == "__main__":
    test_tracker()
