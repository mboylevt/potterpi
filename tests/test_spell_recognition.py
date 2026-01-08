#!/usr/bin/env python3
"""
Unit tests for spell recognition module
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spell_recognition import SpellRecognizer
import numpy as np


class TestSpellRecognizer:
    """Test cases for SpellRecognizer class"""

    def setup_method(self):
        """Set up test fixture"""
        self.recognizer = SpellRecognizer(min_points=8, straightness_threshold=0.6)

    def test_horizontal_right_perfect(self):
        """Test perfect horizontal right line"""
        path = [(x, 100) for x in range(50, 200, 5)]
        spell = self.recognizer.recognize(path)
        assert spell == SpellRecognizer.HORIZONTAL_RIGHT

    def test_horizontal_left_perfect(self):
        """Test perfect horizontal left line"""
        path = [(x, 100) for x in range(200, 50, -5)]
        spell = self.recognizer.recognize(path)
        assert spell == SpellRecognizer.HORIZONTAL_LEFT

    def test_vertical_up_perfect(self):
        """Test perfect vertical up line"""
        path = [(100, y) for y in range(200, 50, -5)]
        spell = self.recognizer.recognize(path)
        assert spell == SpellRecognizer.VERTICAL_UP

    def test_vertical_down_perfect(self):
        """Test perfect vertical down line"""
        path = [(100, y) for y in range(50, 200, 5)]
        spell = self.recognizer.recognize(path)
        assert spell == SpellRecognizer.VERTICAL_DOWN

    def test_insufficient_points(self):
        """Test with too few points"""
        path = [(x, 100) for x in range(50, 80, 5)]  # Only 6 points
        spell = self.recognizer.recognize(path)
        assert spell is None

    def test_too_curved(self):
        """Test curved path should be unknown"""
        path = [(50 + i, 100 + 30*np.sin(i/10)) for i in range(0, 100, 3)]
        spell = self.recognizer.recognize(path)
        assert spell == SpellRecognizer.UNKNOWN

    def test_too_small_movement(self):
        """Test movement that's too small"""
        path = [(x, 100) for x in range(50, 70, 2)]  # Only 20 pixels
        spell = self.recognizer.recognize(path)
        assert spell is None

    def test_diagonal_classified_as_horizontal(self):
        """Test diagonal with more horizontal component"""
        path = [(50 + i, 100 + i//3) for i in range(0, 100, 3)]
        spell = self.recognizer.recognize(path)
        # Should be horizontal since dx > dy
        assert spell in [SpellRecognizer.HORIZONTAL_RIGHT, SpellRecognizer.HORIZONTAL_LEFT]

    def test_diagonal_classified_as_vertical(self):
        """Test diagonal with more vertical component"""
        path = [(100 + i//3, 50 + i) for i in range(0, 100, 3)]
        spell = self.recognizer.recognize(path)
        # Should be vertical since dy > dx
        assert spell in [SpellRecognizer.VERTICAL_UP, SpellRecognizer.VERTICAL_DOWN]

    def test_get_spell_stats_valid(self):
        """Test getting statistics for valid path"""
        path = [(x, 100) for x in range(50, 200, 5)]
        stats = self.recognizer.get_spell_stats(path)

        assert stats is not None
        assert stats["num_points"] == 30
        assert stats["start"] == (50, 100)
        assert stats["end"] == (195, 100)
        assert stats["displacement"] == (145, 0)
        assert stats["straightness"] == 1.0

    def test_get_spell_stats_empty(self):
        """Test getting statistics for empty path"""
        path = []
        stats = self.recognizer.get_spell_stats(path)
        assert stats is None

    def test_get_spell_stats_single_point(self):
        """Test getting statistics for single point"""
        path = [(100, 100)]
        stats = self.recognizer.get_spell_stats(path)
        assert stats is None

    def test_slightly_wavy_horizontal_still_recognized(self):
        """Test that slightly wavy horizontal line is still recognized"""
        # Slight wave with small amplitude
        path = [(50 + i, 100 + 3*np.sin(i/20)) for i in range(0, 150, 3)]
        spell = self.recognizer.recognize(path)
        # Should still recognize as horizontal with 0.6 threshold
        assert spell == SpellRecognizer.HORIZONTAL_RIGHT

    def test_zero_movement(self):
        """Test no net movement (staying in same spot)"""
        path = [(100, 100)] * 20
        spell = self.recognizer.recognize(path)
        assert spell is None

    def test_custom_thresholds(self):
        """Test with custom straightness threshold"""
        recognizer_strict = SpellRecognizer(min_points=5, straightness_threshold=0.95)

        # More wavy path with larger amplitude and higher frequency
        path = [(50 + i, 100 + 15*np.sin(i/10)) for i in range(0, 150, 3)]

        # Default recognizer should accept it
        assert self.recognizer.recognize(path) == SpellRecognizer.HORIZONTAL_RIGHT

        # Strict recognizer should reject it
        assert recognizer_strict.recognize(path) == SpellRecognizer.UNKNOWN


@pytest.mark.parametrize("start_x,end_x,expected", [
    (50, 200, SpellRecognizer.HORIZONTAL_RIGHT),
    (200, 50, SpellRecognizer.HORIZONTAL_LEFT),
])
def test_horizontal_parametrized(start_x, end_x, expected):
    """Parametrized test for horizontal movements"""
    recognizer = SpellRecognizer()
    path = [(x, 100) for x in range(start_x, end_x, 5 if end_x > start_x else -5)]
    spell = recognizer.recognize(path)
    assert spell == expected


@pytest.mark.parametrize("start_y,end_y,expected", [
    (200, 50, SpellRecognizer.VERTICAL_UP),
    (50, 200, SpellRecognizer.VERTICAL_DOWN),
])
def test_vertical_parametrized(start_y, end_y, expected):
    """Parametrized test for vertical movements"""
    recognizer = SpellRecognizer()
    path = [(100, y) for y in range(start_y, end_y, -5 if end_y < start_y else 5)]
    spell = recognizer.recognize(path)
    assert spell == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
