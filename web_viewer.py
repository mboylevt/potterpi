#!/usr/bin/env python3
"""
Web-based camera stream viewer for PotterPi
Provides a browser-accessible view of the camera feed with motion tracking overlay
"""

import cv2
import numpy as np
from flask import Flask, Response, render_template, jsonify
import threading
import time
from datetime import datetime

class WebViewer:
    """Manages web-based streaming of camera feed with overlays"""

    def __init__(self, port=5000):
        """
        Initialize the web viewer

        Args:
            port: Port number for the web server (default 5000)
        """
        self.port = port
        self.app = Flask(__name__)
        self.current_frame = None
        self.tracking_path = []
        self.last_spell = None
        self.last_spell_time = None
        self.frame_lock = threading.Lock()
        self.stats = {
            "frames_processed": 0,
            "spells_detected": 0,
            "fps": 0,
            "uptime": 0
        }
        self.start_time = time.time()
        self.last_fps_time = time.time()
        self.fps_frame_count = 0

        # Set up Flask routes
        self._setup_routes()

    def _setup_routes(self):
        """Set up Flask routes"""

        @self.app.route('/')
        def index():
            """Main viewer page"""
            return render_template('viewer.html')

        @self.app.route('/video_feed')
        def video_feed():
            """Video streaming route"""
            return Response(
                self._generate_frames(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )

        @self.app.route('/stats')
        def stats():
            """Get current statistics"""
            with self.frame_lock:
                return jsonify({
                    **self.stats,
                    "last_spell": self.last_spell,
                    "last_spell_time": self.last_spell_time.isoformat() if self.last_spell_time else None
                })

    def _generate_frames(self):
        """Generate frames for MJPEG streaming"""
        while True:
            with self.frame_lock:
                if self.current_frame is None:
                    # Send a placeholder frame
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "Waiting for camera...", (180, 240),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                else:
                    frame = self.current_frame.copy()

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue

            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

            time.sleep(0.033)  # ~30 fps

    def update_frame(self, gray_frame, tracking_path=None):
        """
        Update the current frame with optional tracking overlay

        Args:
            gray_frame: Grayscale frame from camera (numpy array)
            tracking_path: Optional list of (x,y) tracking points
        """
        # Convert grayscale to BGR for display
        display_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        # Draw tracking path if available
        if tracking_path and len(tracking_path) > 1:
            # Draw path line
            points = np.array(tracking_path, dtype=np.int32)
            for i in range(len(points) - 1):
                thickness = max(1, int((i / len(points)) * 5))  # Thicker towards end
                cv2.line(display_frame, tuple(points[i]), tuple(points[i+1]),
                        (0, 255, 0), thickness)

            # Draw current position (brightest point)
            if tracking_path:
                current_pos = tracking_path[-1]
                cv2.circle(display_frame, current_pos, 8, (0, 0, 255), -1)
                cv2.circle(display_frame, current_pos, 12, (0, 255, 255), 2)

        # Add info overlay
        self._add_info_overlay(display_frame)

        # Update frame and stats
        with self.frame_lock:
            self.current_frame = display_frame
            self.stats["frames_processed"] += 1
            self.stats["uptime"] = int(time.time() - self.start_time)

            # Calculate FPS
            self.fps_frame_count += 1
            elapsed = time.time() - self.last_fps_time
            if elapsed >= 1.0:
                self.stats["fps"] = round(self.fps_frame_count / elapsed, 1)
                self.fps_frame_count = 0
                self.last_fps_time = time.time()

    def _add_info_overlay(self, frame):
        """Add information overlay to frame"""
        height, width = frame.shape[:2]

        # Semi-transparent info panel at top
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Add text info
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"PotterPi - FPS: {self.stats['fps']}", (10, 25),
                   font, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Frames: {self.stats['frames_processed']} | Spells: {self.stats['spells_detected']}",
                   (10, 50), font, 0.5, (255, 255, 255), 1)

        if self.last_spell:
            cv2.putText(frame, f"Last: {self.last_spell}", (10, 70),
                       font, 0.5, (0, 255, 0), 1)

    def log_spell(self, spell_name):
        """
        Log a detected spell

        Args:
            spell_name: Name of the detected spell
        """
        with self.frame_lock:
            self.last_spell = spell_name
            self.last_spell_time = datetime.now()
            self.stats["spells_detected"] += 1

    def start(self):
        """Start the Flask web server"""
        # Run Flask in a separate thread
        server_thread = threading.Thread(
            target=lambda: self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=False,
                threaded=True,
                use_reloader=False
            ),
            daemon=True
        )
        server_thread.start()
        print(f"Web viewer started at http://0.0.0.0:{self.port}")
        return server_thread


if __name__ == "__main__":
    # Test the viewer with synthetic data
    viewer = WebViewer()
    viewer.start()

    print("Generating test frames...")
    try:
        for i in range(1000):
            # Create test frame
            frame = np.random.randint(0, 50, (480, 640), dtype=np.uint8)

            # Simulate tracking path
            if i % 100 < 50:
                path = [(320 + int(j * 2), 240 + int(j)) for j in range(i % 50)]
            else:
                path = None

            # Simulate spell detection
            if i % 100 == 99:
                viewer.log_spell("Horizontal Line Right")

            viewer.update_frame(frame, path)
            time.sleep(0.033)

    except KeyboardInterrupt:
        print("\nTest stopped")
