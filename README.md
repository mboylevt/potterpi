# PotterPi - IR Wand Tracking System

PotterPi is a wand tracking system that mimics the Universal Studios Wizarding World interactive wands. It uses a Raspberry Pi with a Pi NoIR camera to detect IR-reflective wand movements and recognize spell patterns.

## Hardware Requirements

- Raspberry Pi 3B+ (or newer)
- Pi NoIR v2 Camera (8MP)
- IR LEDs (mounted behind camera)
- IR-reflective wand tip

## Software Requirements

- Python 3.7+
- picamera2
- OpenCV (python3-opencv)
- NumPy (python3-numpy)

## Installation

Dependencies should already be installed, but if needed:

```bash
sudo apt-get update
sudo apt-get install python3-opencv python3-numpy
```

## Supported Spells

The system recognizes four basic spell patterns:

1. **Horizontal Line Right** - Draw a line from left to right
2. **Horizontal Line Left** - Draw a line from right to left
3. **Vertical Line Up** - Draw a line from bottom to top
4. **Vertical Line Down** - Draw a line from top to bottom

## Usage

### Running the Main Application

```bash
cd /home/matt/potterpi
./potterpi.py
```

The application will:
- Initialize the camera in IR mode
- Start tracking bright IR reflections (wand tip)
- Recognize spell patterns
- Log detected spells to `/var/log/potterpi/spells.log`

Press Ctrl+C to stop.

### Testing Individual Modules

Test the camera:
```bash
./camera_capture.py
```

Test motion tracking:
```bash
./motion_tracker.py
```

Test spell recognition:
```bash
./spell_recognition.py
```

Test logging:
```bash
./spell_logger.py
```

## Configuration

### Camera Settings

Edit `camera_capture.py` to adjust:
- Resolution (default: 640x480 for speed)
- Framerate (default: 30fps)
- Exposure time (default: 10ms)
- Analog gain (default: 2.0)

### Motion Tracking

Edit `motion_tracker.py` to adjust:
- `brightness_threshold`: Minimum brightness for wand detection (default: 200/255)
- `min_movement`: Minimum pixel movement to record (default: 5px)
- `path_length`: Number of points to track (default: 30)

### Spell Recognition

Edit `spell_recognition.py` to adjust:
- `min_points`: Minimum points for spell (default: 8)
- `straightness_threshold`: How straight the line must be (default: 0.6)

## Logs

Spell detections are logged to:
```
/var/log/potterpi/spells.log
```

View logs in real-time:
```bash
tail -f /var/log/potterpi/spells.log
```

## Module Overview

- **camera_capture.py**: Camera initialization and frame capture optimized for IR
- **motion_tracker.py**: Tracks the bright IR reflection through frames
- **spell_recognition.py**: Identifies spell patterns from movement paths
- **spell_logger.py**: Logs detected spells with timestamps
- **potterpi.py**: Main application that integrates all modules

## Troubleshooting

### Camera not working
- Check camera is enabled: `sudo raspi-config` → Interface Options → Camera
- Verify camera connection: `vcgencmd get_camera`

### No wand detected
- Check IR LEDs are powered and working
- Adjust `brightness_threshold` in motion_tracker.py
- Ensure wand tip is IR-reflective
- Test wand distance (optimal: 2-10 feet)

### False detections
- Increase `min_points` in spell_recognition.py
- Increase `straightness_threshold` for stricter matching
- Increase `spell_cooldown` in potterpi.py

### Performance issues
- Reduce camera resolution in camera_capture.py
- Lower framerate
- Reduce `path_length` in motion_tracker.py

## Future Enhancements

- Home Assistant integration for triggering automations
- Additional spell patterns (circles, zigzags, etc.)
- Multiple wand tracking
- Visual feedback/display
- Configuration file for easy tuning

## License

This project is for personal/educational use.
