# PotterPi Test Suite

Comprehensive test suite for the PotterPi wand tracking system.

## Test Coverage

### Unit Tests

1. **test_spell_recognition.py** - Spell pattern recognition
   - All 4 spell types (horizontal left/right, vertical up/down)
   - Edge cases (insufficient points, curved paths, small movements)
   - Statistics calculation
   - Custom thresholds
   - Parametrized tests

2. **test_motion_tracker.py** - Wand motion tracking
   - Bright spot detection
   - Path tracking and recording
   - Movement filtering
   - Path length limits
   - Multiple bright spots handling

3. **test_config.py** - Configuration management
   - Default configuration
   - Loading/saving configuration files
   - Nested value access
   - Malformed file handling
   - Home Assistant configuration

4. **test_homeassistant_api.py** - Home Assistant integration
   - Connection testing
   - Event firing
   - Service calls
   - State retrieval
   - Spell action triggering
   - Error handling and timeouts

5. **test_spell_logger.py** - Spell logging
   - Basic logging
   - Statistics logging
   - Multiple spells
   - Timestamp formatting
   - Concurrent logging

## Running Tests

### Install Test Dependencies

```bash
pip3 install -r requirements-test.txt
```

### Run All Tests

```bash
# Using the test runner
./run_tests.py

# Or directly with pytest
pytest tests/ -v

# On the Raspberry Pi
cd /home/matt/potterpi
python3 run_tests.py
```

### Run Specific Test File

```bash
pytest tests/test_spell_recognition.py -v
```

### Run Specific Test

```bash
pytest tests/test_spell_recognition.py::TestSpellRecognizer::test_horizontal_right_perfect -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html
```

## Test Organization

```
tests/
├── __init__.py                      # Test package initialization
├── README.md                        # This file
├── test_spell_recognition.py        # Spell recognition tests
├── test_motion_tracker.py           # Motion tracking tests
├── test_config.py                   # Configuration tests
├── test_homeassistant_api.py        # Home Assistant API tests
└── test_spell_logger.py             # Logging tests
```

## Writing New Tests

### Test File Template

```python
#!/usr/bin/env python3
"""
Tests for [module_name]
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from [module_name] import [ClassName]


class Test[ClassName]:
    """Test cases for [ClassName]"""

    def setup_method(self):
        """Set up test fixture"""
        pass

    def teardown_method(self):
        """Clean up test fixture"""
        pass

    def test_something(self):
        """Test description"""
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_is_being_tested>`

### Fixtures

Use `setup_method()` and `teardown_method()` for test setup and cleanup:

```python
def setup_method(self):
    """Set up before each test"""
    self.obj = MyClass()

def teardown_method(self):
    """Clean up after each test"""
    del self.obj
```

## Test Markers

Tests can be marked with custom markers:

```python
@pytest.mark.slow
def test_long_running_operation():
    pass
```

Run only specific markers:

```bash
pytest -m slow       # Run only slow tests
pytest -m "not slow" # Skip slow tests
```

## Mocking

For testing code with external dependencies (like Home Assistant API):

```python
from unittest.mock import Mock, patch

@patch('module.requests.get')
def test_api_call(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    # Test code here
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest tests/ -v
```

## Test Results

Expected output:

```
==================== test session starts ====================
collected 50 items

tests/test_spell_recognition.py::TestSpellRecognizer::test_horizontal_right_perfect PASSED [ 2%]
tests/test_spell_recognition.py::TestSpellRecognizer::test_horizontal_left_perfect PASSED [ 4%]
...
==================== 50 passed in 2.34s ====================
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the potterpi directory:

```bash
cd /home/matt/potterpi
python3 run_tests.py
```

### Missing Dependencies

Install test dependencies:

```bash
pip3 install pytest numpy
```

### OpenCV Tests Failing

Motion tracker tests require OpenCV. Install it:

```bash
sudo apt-get install python3-opencv
```
