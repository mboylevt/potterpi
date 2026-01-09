# PotterPi - IR Wand Tracking System

PotterPi is a wand tracking system inspired by the Universal Studios Wizarding World interactive wands. It uses a Raspberry Pi with a Pi NoIR camera to detect IR-reflective wand movements and recognize spell patterns, with optional Home Assistant integration for home automation.

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
- Flask (for web viewer)
- Requests (for Home Assistant integration)

## Installation

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install python3-opencv python3-numpy python3-pip
```

### 2. Clone the Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/potterpi.git
cd potterpi
```

### 3. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Configure the Application

Copy the example configuration and customize it:

```bash
cp config.yaml.example config.yaml
nano config.yaml
```

Edit the configuration to match your setup (Home Assistant URL/token, camera settings, etc.).

### 5. Create Log Directory

```bash
sudo mkdir -p /var/log/potterpi
sudo chown $USER:$USER /var/log/potterpi
```

## Supported Spells

The system recognizes four basic spell patterns:

1. **Horizontal Line Right** (Lumos) - Draw a line from left to right
2. **Horizontal Line Left** (Nox) - Draw a line from right to left
3. **Vertical Line Up** (Wingardium Leviosa) - Draw a line from bottom to top
4. **Vertical Line Down** (Descendo) - Draw a line from top to bottom

## Usage

### Running the Main Application

```bash
cd ~/potterpi
python3 run_potterpi.py
```

Or with a custom configuration:

```bash
python3 run_potterpi.py /path/to/custom-config.yaml
```

The application will:
- Initialize the camera in IR mode
- Start tracking bright IR reflections (wand tip)
- Recognize spell patterns
- Log detected spells to `/var/log/potterpi/potterpi.log`
- Start web viewer at `http://potterpi.local:5000`
- Integrate with Home Assistant (if configured)

Press Ctrl+C to stop.

### Web Viewer

Access the live camera feed with tracking overlay:

```bash
http://potterpi.local:5000
```

Or using IP address:

```bash
http://192.168.x.x:5000
```

The viewer shows:
- Real-time camera feed with wand tracking overlay
- Current FPS and frame count
- Detected spells counter
- Last detected spell with timestamp

### Home Assistant Integration

If Home Assistant is configured in `config.yaml`, PotterPi will:
- Fire `potterpi_spell_cast` events when spells are detected
- Include spell details (name, straightness, distance, points)
- Allow you to create automations based on spell gestures

Example Home Assistant automation:
```yaml
automation:
  - alias: "Lumos - Turn on lights"
    trigger:
      platform: event
      event_type: potterpi_spell_cast
      event_data:
        spell: "Horizontal Line Right"
    action:
      service: light.turn_on
      target:
        entity_id: light.living_room
```

### Alternative Scripts

For Home Assistant-specific functionality without web viewer:

```bash
python3 scripts/potterpi_ha.py
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python3 -m pytest tests/

# Run with verbose output
python3 -m pytest tests/ -v

# Run specific test module
python3 -m pytest tests/test_spell_recognition.py
```

Test coverage:
- **70 tests** across 5 modules
- Configuration management
- Motion tracking
- Spell recognition
- Logging functionality
- Home Assistant API integration

## Configuration

### Configuration File Structure

The `config.yaml` file controls all aspects of PotterPi:

```yaml
# Logging with automatic rotation
logging:
  dir: "/var/log/potterpi"
  file: "potterpi.log"
  max_bytes: 10485760  # 10MB max per file
  backup_count: 5      # Keep 5 backup files

# Camera settings
camera:
  width: 640
  height: 480
  framerate: 30

# Motion tracking sensitivity
tracker:
  brightness_threshold: 200  # 0-255, brightness for wand detection
  min_movement: 5            # Minimum pixel movement to record
  path_length: 30            # Number of tracking points

# Spell recognition thresholds
recognizer:
  min_points: 8               # Minimum points for valid spell
  straightness_threshold: 0.6 # How straight line must be (0-1)

# Web viewer
web_viewer:
  port: 5000

# Home Assistant integration (optional)
homeassistant:
  enabled: true
  url: "http://192.168.1.100:8123"
  token: "your_long_lived_access_token_here"

# Detection cooldown (seconds between spell detections)
spell_cooldown: 1.0
```

### Tuning Tips

**For better detection:**
- Lower `brightness_threshold` for darker wands
- Decrease `min_points` for shorter gestures
- Lower `straightness_threshold` for more forgiving matching

**For fewer false positives:**
- Increase `brightness_threshold`
- Increase `min_points`
- Increase `straightness_threshold`
- Increase `spell_cooldown`

**For performance:**
- Reduce camera resolution
- Lower framerate
- Reduce `path_length`

## Logs

### Log Location

Spell detections and system events are logged to:
```
/var/log/potterpi/potterpi.log
```

Rotated logs:
```
/var/log/potterpi/potterpi.log.1
/var/log/potterpi/potterpi.log.2
...
```

### Viewing Logs

```bash
# View live logs
tail -f /var/log/potterpi/potterpi.log

# Search for spell detections
grep "SPELL DETECTED" /var/log/potterpi/potterpi.log

# View last 100 lines
tail -n 100 /var/log/potterpi/potterpi.log

# Search for errors
grep "ERROR" /var/log/potterpi/potterpi.log
```

### Log Rotation

Logs are automatically rotated to prevent SD card fill-up:
- **Max file size**: 10MB (configurable)
- **Backup files**: 5 (configurable)
- **Total max size**: ~50MB with defaults
- **Automatic cleanup**: Old logs deleted automatically

## Project Structure

```
potterpi/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── requirements-test.txt        # Test dependencies
├── pytest.ini                   # Pytest configuration
├── config.yaml.example          # Example configuration
├── run_potterpi.py             # Main entry point
│
├── potterpi/                   # Source package
│   ├── __init__.py
│   ├── potterpi.py             # Main application
│   ├── camera_capture.py       # Camera interface
│   ├── motion_tracker.py       # IR LED tracking
│   ├── spell_recognition.py    # Gesture recognition
│   ├── spell_logger.py         # Structured logging
│   ├── homeassistant_api.py    # Home Assistant integration
│   ├── config.py               # Configuration management
│   └── web_viewer.py           # Web interface
│
├── docs/                       # Documentation
│   └── FEATURES.md             # Detailed feature documentation
│
├── scripts/                    # Utility scripts
│   ├── potterpi_ha.py         # HA-specific variant
│   └── run_tests.py           # Test runner
│
├── templates/                  # HTML templates
│   └── viewer.html            # Web viewer template
│
└── tests/                      # Test suite
    ├── test_config.py
    ├── test_homeassistant_api.py
    ├── test_motion_tracker.py
    ├── test_spell_logger.py
    └── test_spell_recognition.py
```

## Troubleshooting

### Camera not working
- Check camera is enabled: `sudo raspi-config` → Interface Options → Camera
- Verify camera connection: `vcgencmd get_camera`
- Check permissions: Current user should be in `video` group

### No wand detected
- Check IR LEDs are powered and working
- Adjust `brightness_threshold` in config.yaml
- Ensure wand tip is IR-reflective
- Test wand distance (optimal: 2-10 feet)

### False detections
- Increase `min_points` in config.yaml
- Increase `straightness_threshold` for stricter matching
- Increase `spell_cooldown` to prevent rapid re-detection

### Web viewer not accessible
- Check Flask is running: `ss -tlnp | grep 5000`
- Verify firewall settings: `sudo ufw status`
- Try IP address instead of hostname

### Home Assistant integration not working
- Verify HA URL and token in config.yaml
- Check HA is accessible: `curl -H "Authorization: Bearer YOUR_TOKEN" http://HA_URL/api/`
- Check logs for connection errors

### Performance issues
- Reduce camera resolution in config.yaml
- Lower framerate
- Reduce `path_length` in tracker settings
- Disable web viewer if not needed

## Monitoring with Datadog (Optional)

PotterPi logs can be forwarded to Datadog for centralized monitoring. See `docs/FEATURES.md` for detailed setup instructions.

Quick setup:
1. Install Vector log forwarder on Raspberry Pi
2. Configure Vector to read `/var/log/potterpi/potterpi.log`
3. Set up Datadog API key
4. Logs will appear in Datadog Log Explorer

## Advanced Features

For detailed documentation on advanced features:
- Web viewer capabilities
- Log rotation and management
- Datadog integration
- Performance tuning

See: **[docs/FEATURES.md](docs/FEATURES.md)**

## Development

### Running Tests

```bash
# All tests
python3 -m pytest tests/ -v

# With coverage
python3 -m pytest tests/ --cov=potterpi

# Specific module
python3 -m pytest tests/test_spell_recognition.py -v
```

### Adding New Spells

1. Add pattern recognition logic to `potterpi/spell_recognition.py`
2. Add tests to `tests/test_spell_recognition.py`
3. Update spell mapping in `potterpi/potterpi.py`
4. Test with physical wand

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all tests pass: `python3 -m pytest tests/`
5. Submit pull request

## License

This project is for personal/educational use.

## Acknowledgments

- Inspired by Universal Studios interactive wands
- Built for Raspberry Pi and Home Assistant communities
- Uses OpenCV for computer vision

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
