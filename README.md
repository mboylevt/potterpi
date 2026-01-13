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

The application uses two configuration files:
- `config.json` - Main configuration (camera, tracking, spell settings)
- `secrets.json` - Sensitive credentials (tokens, API keys) - **excluded from git**

Create your configuration:

```bash
# Main config (can be checked into git)
nano ~/potterpi/config.json

# Secrets file (NEVER check into git - already in .gitignore)
nano ~/potterpi/secrets.json
```

See the Configuration section below for detailed structure and options.

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

The application will:
- Initialize the camera in IR mode
- Start tracking bright IR reflections (wand tip)
- Recognize spell patterns
- Log detected spells to `/var/log/potterpi/potterpi.log`
- Start web viewer at `http://potterpi.local:8080`
- Integrate with Home Assistant (if configured)

Press Ctrl+C to stop.

### Web Viewer

Access the live camera feed with tracking overlay:

```bash
http://potterpi.local:8080
```

Or using IP address:

```bash
http://192.168.x.x:8080
```

The viewer shows:
- Real-time camera feed with wand tracking overlay
- Current FPS and frame count
- Detected spells counter
- Last detected spell with timestamp

### Home Assistant Integration

#### Setup

1. Create a long-lived access token in Home Assistant:
   - Profile → Security → Long-Lived Access Tokens → Create Token

2. Add credentials to `secrets.json`:
```json
{
  "homeassistant_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "homeassistant_url": "http://192.168.1.100:8123"
}
```

3. Enable integration in `config.json`:
```json
{
  "homeassistant": {
    "enabled": true,
    "spell_actions": {
      "Vertical Line Down": {
        "domain": "switch",
        "service": "turn_on",
        "entity_id": "switch.ceiling_fan"
      }
    }
  }
}
```

#### Features

If Home Assistant is configured, PotterPi will:
- Call Home Assistant services when spells are detected
- Log all actions and responses
- Automatically retry on failures

Example spell action configuration:
```json
{
  "spell_actions": {
    "Horizontal Line Right": {
      "domain": "light",
      "service": "turn_on",
      "entity_id": "light.living_room"
    },
    "Horizontal Line Left": {
      "domain": "light",
      "service": "turn_off",
      "entity_id": "light.living_room"
    }
  }
}
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

### Configuration Files

PotterPi uses two JSON configuration files for security:

1. **`config.json`** - Main configuration (safe to commit to git)
2. **`secrets.json`** - Sensitive credentials (excluded from git via .gitignore)

### config.json Structure

This file contains all non-sensitive settings:

```json
{
  "camera": {
    "width": 640,
    "height": 480,
    "framerate": 30,
    "exposure_time": 10000,
    "analog_gain": 2.0
  },
  "tracking": {
    "brightness_threshold": 200,
    "min_movement": 5,
    "path_length": 30
  },
  "recognition": {
    "min_points": 8,
    "straightness_threshold": 0.6,
    "min_distance": 30
  },
  "homeassistant": {
    "enabled": true,
    "spell_actions": {
      "Vertical Line Down": {
        "domain": "switch",
        "service": "turn_on",
        "entity_id": "switch.ceiling_fan"
      },
      "Vertical Line Up": {
        "domain": "switch",
        "service": "turn_off",
        "entity_id": "switch.ceiling_fan"
      }
    }
  },
  "logging": {
    "log_dir": "/var/log/potterpi",
    "spell_cooldown": 1.0
  },
  "web_viewer": {
    "port": 8080
  },
  "datadog": {
    "enabled": false
  }
}
```

### secrets.json Structure

**IMPORTANT:** This file contains sensitive credentials and should **NEVER** be committed to git.

Create this file at `~/potterpi/secrets.json`:

```json
{
  "homeassistant_token": "your_long_lived_access_token_here",
  "homeassistant_url": "http://192.168.1.100:8123",
  "datadog_api_key": "your_datadog_api_key",
  "datadog_app_key": "your_datadog_app_key"
}
```

The secrets file is automatically loaded at startup and merged with config.json.

### Environment Variable Overrides

You can override secrets using environment variables (highest priority):

```bash
export POTTERPI_HA_TOKEN="your_token"
export POTTERPI_HA_URL="http://192.168.1.100:8123"
export POTTERPI_DD_API_KEY="your_datadog_key"
export POTTERPI_DD_APP_KEY="your_datadog_app_key"

python3 run_potterpi.py
```

### Configuration Priority

Settings are loaded in this priority order (highest to lowest):
1. **Environment Variables** - `POTTERPI_*` vars
2. **Secrets File** - `~/potterpi/secrets.json`
3. **Config File** - `~/potterpi/config.json`
4. **Defaults** - Built-in defaults

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
- Check Flask is running: `ss -tlnp | grep 8080`
- Verify firewall settings: `sudo ufw status`
- Try IP address instead of hostname

### Home Assistant integration not working
- Verify credentials in `secrets.json`:
  ```bash
  cat ~/potterpi/secrets.json
  ```
- Check HA is accessible:
  ```bash
  curl -H "Authorization: Bearer YOUR_TOKEN" http://HA_URL/api/
  ```
- Verify `homeassistant.enabled` is `true` in config.json
- Check logs for connection errors:
  ```bash
  grep "Home Assistant" /var/log/potterpi/potterpi.log
  ```

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
