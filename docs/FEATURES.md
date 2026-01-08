# PotterPi New Features

This document describes the new features added to PotterPi: web-based camera viewer, comprehensive logging with rotation, and Datadog integration.

## 1. Web-Based Camera Viewer

### Overview
A real-time browser-accessible camera feed with motion tracking overlay that shows what the camera sees while processing spells.

### Features
- **Live MJPEG stream** at ~30 FPS
- **Motion tracking overlay** showing wand path in green
- **Real-time statistics** (frames processed, spells detected, FPS, uptime)
- **Last spell display** with timestamp
- **Responsive design** works on desktop and mobile

### Accessing the Viewer
1. Start PotterPi: `python3 potterpi.py`
2. Open browser and navigate to: `http://potterpi.local:5000` (or `http://192.168.x.x:5000`)
3. The viewer updates automatically

### Configuration
Edit `config.yaml`:
```yaml
web_viewer:
  port: 5000  # Change port if needed
```

### What You'll See
- **Green line**: Wand tracking path
- **Red/yellow circles**: Current wand position
- **Top overlay**: FPS, frame count, spell count
- **Last spell panel**: Most recently detected spell with timestamp

## 2. Comprehensive Logging

### Overview
All modules now have detailed logging with aggressive log rotation to prevent SD card fill-up.

### Log Levels
- **INFO**: Normal operations (startup, spell detection, HA calls)
- **DEBUG**: Detailed tracking (wand position, path analysis)
- **WARNING**: Non-fatal issues (HA connection failures)
- **ERROR**: Failures requiring attention
- **EXCEPTION**: Stack traces for debugging

### Log Rotation
Logs are automatically rotated to prevent disk space issues:
- **Max file size**: 10MB per file (configurable)
- **Backup count**: 5 files kept (configurable)
- **Total max size**: ~50MB (with defaults)
- **Automatic cleanup**: Old logs deleted automatically

### Configuration
Edit `config.yaml`:
```yaml
logging:
  dir: "/var/log/potterpi"
  file: "potterpi.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5      # Keep 5 backups
```

### Log Location
- **Main log**: `/var/log/potterpi/potterpi.log`
- **Rotated logs**: `/var/log/potterpi/potterpi.log.1`, `.2`, etc.

### What Gets Logged

#### Startup/Shutdown
```
2026-01-08 10:15:30 - PotterPi - INFO - PotterPi starting up...
2026-01-08 10:15:32 - PotterPi - INFO - Camera started successfully: 640x480 @ 30fps
2026-01-08 10:15:32 - PotterPi - INFO - Web viewer started at http://0.0.0.0:5000
2026-01-08 10:15:33 - PotterPi - INFO - Home Assistant connection successful
2026-01-08 10:15:33 - PotterPi - INFO - PotterPi is now active and watching for spells!
```

#### Spell Detection
```
2026-01-08 10:16:45 - PotterPi - DEBUG - Wand detected at (320, 240) - starting spell cast tracking
2026-01-08 10:16:47 - PotterPi - DEBUG - Wand lost - spell cast ended with 25 points
2026-01-08 10:16:47 - PotterPi - INFO - Spell recognized: Horizontal Line Right (straightness=0.87)
2026-01-08 10:16:47 - PotterPi - INFO - SPELL DETECTED: Horizontal Line Right | Points: 25 | Straightness: 0.87 | Distance: 145.3px
```

#### Home Assistant Integration
```
2026-01-08 10:16:47 - PotterPi - DEBUG - Firing event 'potterpi_spell_cast' with data: {'spell': 'Horizontal Line Right', ...}
2026-01-08 10:16:47 - PotterPi - INFO - Successfully fired event: potterpi_spell_cast
2026-01-08 10:16:47 - PotterPi - INFO - Home Assistant action triggered for: Horizontal Line Right
```

#### Error Logging
```
2026-01-08 10:17:00 - PotterPi - ERROR - Failed to fire event potterpi_spell_cast: HTTP 500
2026-01-08 10:17:00 - PotterPi - ERROR - Error triggering Home Assistant action: Connection timeout
```

### Viewing Logs
```bash
# View live logs
tail -f /var/log/potterpi/potterpi.log

# View last 100 lines
tail -n 100 /var/log/potterpi/potterpi.log

# Search for spells
grep "SPELL DETECTED" /var/log/potterpi/potterpi.log

# Search for errors
grep "ERROR" /var/log/potterpi/potterpi.log

# View specific date range
grep "2026-01-08 10:" /var/log/potterpi/potterpi.log
```

## 3. Datadog Integration

### Overview
Forward all PotterPi logs to Datadog for centralized monitoring, alerting, and analytics.

### Installation Steps

#### Step 1: Install Datadog Agent on Raspberry Pi
```bash
# Get your API key from Datadog dashboard
DD_AGENT_MAJOR_VERSION=7 \
DD_API_KEY=YOUR_API_KEY_HERE \
DD_SITE="datadoghq.com" \
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
```

#### Step 2: Enable Log Collection
Edit `/etc/datadog-agent/datadog.yaml`:
```yaml
logs_enabled: true
```

#### Step 3: Configure PotterPi Integration
```bash
# Create config directory
sudo mkdir -p /etc/datadog-agent/conf.d/potterpi.d

# Copy PotterPi config
sudo cp /home/matt/potterpi/datadog-agent-config.yaml /etc/datadog-agent/conf.d/potterpi.d/conf.yaml

# Set permissions
sudo chown dd-agent:dd-agent /etc/datadog-agent/conf.d/potterpi.d/conf.yaml
```

#### Step 4: Grant Log Access
```bash
# Add datadog agent user to appropriate group
sudo usermod -a -G adm dd-agent

# Ensure log directory exists and has proper permissions
sudo mkdir -p /var/log/potterpi
sudo chmod 755 /var/log/potterpi
```

#### Step 5: Restart Agent
```bash
sudo systemctl restart datadog-agent
```

#### Step 6: Verify
```bash
# Check agent status
sudo datadog-agent status

# Look for "potterpi" in the logs section
# You should see:
#   potterpi (integration)
#   ----------------------
#     Type: file
#     Path: /var/log/potterpi/potterpi.log
#     Status: OK
```

### Datadog Dashboard Features

Once logs are flowing to Datadog:

1. **Log Explorer**: Search and filter all PotterPi logs
   - Filter by spell type: `@spell:Horizontal\ Line\ Right`
   - Filter by log level: `@status:error`
   - Time series visualization of spell detections

2. **Monitors**: Set up alerts
   - Alert when error rate increases
   - Alert when no spells detected for X minutes (system down?)
   - Alert when log file rotation issues occur

3. **Dashboards**: Create custom dashboards
   - Spell detection frequency over time
   - Most common spell types
   - System uptime and FPS metrics
   - Home Assistant integration success rate

4. **Tags**: All logs include tags for easy filtering
   - `env:production`
   - `application:potterpi`
   - `device:raspberry-pi`
   - `service:potterpi`

### Example Datadog Queries

```
# All spell detections
service:potterpi "SPELL DETECTED"

# Errors in the last hour
service:potterpi status:error

# Home Assistant failures
service:potterpi "Home Assistant" status:error

# Tracking starts
service:potterpi "Wand detected"

# System startup events
service:potterpi "PotterPi starting up"
```

## 4. Integrated Main Application

### Overview
The main `potterpi.py` now integrates all features:
- Web viewer
- Comprehensive logging
- Home Assistant integration (optional)
- Configuration file support

### Running PotterPi

```bash
# With default config.yaml
python3 potterpi.py

# With custom config
python3 potterpi.py /path/to/custom-config.yaml
```

### Configuration File

Copy the example and customize:
```bash
cp config.yaml.example config.yaml
nano config.yaml
```

Example configuration:
```yaml
# Logging with rotation
logging:
  dir: "/var/log/potterpi"
  file: "potterpi.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5

# Camera settings
camera:
  width: 640
  height: 480
  framerate: 30

# Tracking sensitivity
tracker:
  brightness_threshold: 200
  min_movement: 5
  path_length: 30

# Recognition parameters
recognizer:
  min_points: 8
  straightness_threshold: 0.6

# Web viewer port
web_viewer:
  port: 5000

# Home Assistant integration
homeassistant:
  enabled: true
  url: "http://192.168.2.103:8123"
  token: "YOUR_TOKEN_HERE"

# Detection cooldown
spell_cooldown: 1.0
```

### Startup Sequence

When you run `python3 potterpi.py`, the system will:

1. Load configuration from `config.yaml`
2. Initialize logging with rotation
3. Initialize camera, tracker, and recognizer
4. Start web viewer on configured port
5. Test Home Assistant connection (if enabled)
6. Start main processing loop
7. Log all activity

Example startup output:
```
======================================================================
PotterPi - IR Wand Tracking System
======================================================================
Starting up...
Web viewer started at http://0.0.0.0:5000
Camera initialized successfully
Home Assistant connection successful
======================================================================
PotterPi is now active and watching for spells!
======================================================================
```

## 5. Monitoring and Debugging

### Real-Time Monitoring

**Option 1: Web Viewer**
- Open `http://potterpi.local:5000`
- See live camera feed, tracking, and statistics

**Option 2: Live Logs**
```bash
# SSH into Pi
ssh matt@potterpi.local

# Watch logs in real-time
tail -f /var/log/potterpi/potterpi.log
```

**Option 3: Datadog**
- View logs in Datadog dashboard
- Set up monitors and alerts
- Create custom dashboards

### Troubleshooting

#### Web Viewer Not Accessible
```bash
# Check if Flask is running
ss -tlnp | grep 5000

# Check firewall
sudo ufw status

# Check logs for errors
grep "web_viewer" /var/log/potterpi/potterpi.log
```

#### Logs Not Rotating
```bash
# Check disk space
df -h /var/log/potterpi

# Check log file sizes
ls -lh /var/log/potterpi/

# Check permissions
ls -la /var/log/potterpi/
```

#### Datadog Not Receiving Logs
```bash
# Check agent status
sudo datadog-agent status

# Check agent logs
sudo tail -f /var/log/datadog/agent.log

# Test log collection
echo "Test message" >> /var/log/potterpi/potterpi.log
```

## 6. Performance Considerations

### Resource Usage
- **Web Viewer**: Minimal CPU overhead (~2-3%)
- **Logging**: Minimal disk I/O with rotation
- **Datadog Agent**: ~20MB RAM, minimal CPU

### Optimization Tips
1. Reduce web viewer frame rate if CPU usage is high
2. Increase log rotation threshold for less frequent writes
3. Disable debug logging in production for less log volume
4. Use Datadog sampling if log volume is too high

### Disk Space Management
With default settings (10MB × 5 backups = 50MB max):
- 16GB SD card: ~0.3% of total space
- Logs automatically cleaned up
- No manual maintenance required

## 7. Security Considerations

### Web Viewer
- Runs on all interfaces (0.0.0.0)
- No authentication by default
- Recommended: Use firewall or reverse proxy with auth

### Datadog
- API key required
- Logs transmitted over HTTPS
- Tags can include sensitive info - review config

### Log Files
- Contains detected spells and timestamps
- May contain network info (HA URLs)
- Ensure proper file permissions

## Summary

The enhanced PotterPi system now provides:

✅ **Real-time visual feedback** via web browser
✅ **Comprehensive logging** with automatic rotation
✅ **Centralized monitoring** via Datadog (optional)
✅ **Production-ready reliability** with proper error handling
✅ **Easy troubleshooting** with detailed logs and web viewer

All while maintaining the same core spell detection functionality!
