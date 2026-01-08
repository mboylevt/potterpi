#!/usr/bin/env python3
"""
Spell recognition module for PotterPi
Identifies spell patterns from wand movement paths
"""

import numpy as np
import logging

# Set up module-level logger
logger = logging.getLogger("PotterPi")

class SpellRecognizer:
    """Recognizes spell patterns from wand paths"""

    # Spell type constants
    HORIZONTAL_RIGHT = "Horizontal Line Right"
    HORIZONTAL_LEFT = "Horizontal Line Left"
    VERTICAL_UP = "Vertical Line Up"
    VERTICAL_DOWN = "Vertical Line Down"
    UNKNOWN = "Unknown"

    def __init__(self, min_points=8, straightness_threshold=0.6):
        """
        Initialize spell recognizer

        Args:
            min_points: Minimum points required to recognize a spell
            straightness_threshold: How straight the line must be (0-1, higher = stricter)
        """
        self.min_points = min_points
        self.straightness_threshold = straightness_threshold
        logger.debug(f"SpellRecognizer initialized: min_points={min_points}, straightness_threshold={straightness_threshold}")
    
    def recognize(self, path):
        """
        Recognize a spell from a movement path

        Args:
            path: List of (x, y) tuples representing wand movement

        Returns:
            str: Name of the recognized spell, or UNKNOWN
        """
        if len(path) < self.min_points:
            logger.debug(f"Path rejected: only {len(path)} points (need {self.min_points})")
            return None  # Not enough points

        # Convert to numpy array for easier math
        points = np.array(path)

        # Calculate start and end points
        start = points[0]
        end = points[-1]

        # Calculate total displacement
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        # Calculate total distance traveled
        total_distance = np.sum(np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1)))

        # Calculate straight-line distance
        straight_distance = np.sqrt(dx**2 + dy**2)

        # Check if movement is reasonably straight
        if straight_distance == 0:
            logger.debug("Path rejected: no net movement")
            return None  # No net movement

        straightness = straight_distance / total_distance

        if straightness < self.straightness_threshold:
            logger.debug(f"Path rejected: straightness {straightness:.2f} < threshold {self.straightness_threshold}")
            return self.UNKNOWN  # Too curved/erratic

        # Determine if primarily horizontal or vertical
        abs_dx = abs(dx)
        abs_dy = abs(dy)

        # Need significant movement in at least one direction
        if max(abs_dx, abs_dy) < 30:  # Minimum 30 pixel movement
            logger.debug(f"Path rejected: movement too small (dx={dx:.1f}, dy={dy:.1f})")
            return None  # Movement too small

        # Classify the spell
        if abs_dx > abs_dy:
            # Horizontal movement
            if dx > 0:
                logger.info(f"Spell recognized: {self.HORIZONTAL_RIGHT} (straightness={straightness:.2f})")
                return self.HORIZONTAL_RIGHT
            else:
                logger.info(f"Spell recognized: {self.HORIZONTAL_LEFT} (straightness={straightness:.2f})")
                return self.HORIZONTAL_LEFT
        else:
            # Vertical movement
            # Note: Y increases downward in image coordinates
            if dy > 0:
                logger.info(f"Spell recognized: {self.VERTICAL_DOWN} (straightness={straightness:.2f})")
                return self.VERTICAL_DOWN
            else:
                logger.info(f"Spell recognized: {self.VERTICAL_UP} (straightness={straightness:.2f})")
                return self.VERTICAL_UP
    
    def get_spell_stats(self, path):
        """
        Get detailed statistics about a spell path
        
        Args:
            path: List of (x, y) tuples
            
        Returns:
            dict: Statistics about the path
        """
        if len(path) < 2:
            return None
            
        points = np.array(path)
        start = points[0]
        end = points[-1]
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        total_distance = np.sum(np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1)))
        straight_distance = np.sqrt(dx**2 + dy**2)
        
        return {
            "num_points": len(path),
            "start": tuple(start),
            "end": tuple(end),
            "displacement": (dx, dy),
            "total_distance": total_distance,
            "straight_distance": straight_distance,
            "straightness": straight_distance / total_distance if total_distance > 0 else 0
        }


def test_recognizer():
    """Test spell recognition with synthetic paths"""
    recognizer = SpellRecognizer()
    
    # Test horizontal right
    path_h_right = [(x, 100) for x in range(50, 200, 5)]
    spell = recognizer.recognize(path_h_right)
    print(f"Horizontal right test: {spell}")
    print(f"  Stats: {recognizer.get_spell_stats(path_h_right)}")
    
    # Test horizontal left
    path_h_left = [(x, 100) for x in range(200, 50, -5)]
    spell = recognizer.recognize(path_h_left)
    print(f"\nHorizontal left test: {spell}")
    print(f"  Stats: {recognizer.get_spell_stats(path_h_left)}")
    
    # Test vertical up
    path_v_up = [(100, y) for y in range(200, 50, -5)]
    spell = recognizer.recognize(path_v_up)
    print(f"\nVertical up test: {spell}")
    print(f"  Stats: {recognizer.get_spell_stats(path_v_up)}")
    
    # Test vertical down
    path_v_down = [(100, y) for y in range(50, 200, 5)]
    spell = recognizer.recognize(path_v_down)
    print(f"\nVertical down test: {spell}")
    print(f"  Stats: {recognizer.get_spell_stats(path_v_down)}")
    
    # Test curved path (should be unknown or rejected)
    path_curved = [(50 + i, 100 + 30*np.sin(i/10)) for i in range(0, 100, 3)]
    spell = recognizer.recognize(path_curved)
    print(f"\nCurved path test: {spell}")
    print(f"  Stats: {recognizer.get_spell_stats(path_curved)}")


if __name__ == "__main__":
    test_recognizer()
