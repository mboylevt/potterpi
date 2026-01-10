#!/usr/bin/env python3
"""
Camera capture module for PotterPi
Handles Pi NoIR camera configuration and frame capture optimized for IR wand detection
"""

from picamera2 import Picamera2
import numpy as np
import time
import logging

# Set up module-level logger
logger = logging.getLogger("PotterPi")

class IRCamera:
    """Manages camera configuration and frame capture for IR wand tracking"""

    def __init__(self, width=640, height=480, framerate=30):
        """
        Initialize the IR camera with optimized settings

        Args:
            width: Frame width in pixels (default 640 for speed)
            height: Frame height in pixels (default 480 for speed)
            framerate: Target framerate (default 30 fps)
        """
        self.width = width
        self.height = height
        self.framerate = framerate
        self.camera = None
        logger.debug(f"IRCamera initialized: {width}x{height} @ {framerate}fps")
        
    def start(self):
        """Initialize and start the camera with IR-optimized settings"""
        logger.info("Initializing IR camera...")
        try:
            self.camera = Picamera2()

            # Configure for grayscale (faster processing, IR is monochrome anyway)
            config = self.camera.create_preview_configuration(
                main={"size": (self.width, self.height), "format": "RGB888"},
                controls={
                    "FrameRate": self.framerate,
                    # Higher exposure to capture IR reflections better
                    "ExposureTime": 10000,  # 10ms exposure
                    # Disable auto white balance (not useful for IR)
                    "AwbEnable": False,
                    # Higher analog gain for better IR sensitivity
                    "AnalogueGain": 2.0,
                }
            )

            self.camera.configure(config)
            self.camera.start()

            # Let camera settle
            time.sleep(2)
            logger.info(f"Camera started successfully: {self.width}x{self.height} @ {self.framerate}fps")
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            raise
        
    def get_frame(self):
        """
        Capture and return a single frame as grayscale numpy array

        Returns:
            numpy.ndarray: Grayscale frame (height x width)
        """
        if self.camera is None:
            raise RuntimeError("Camera not started. Call start() first.")

        # Capture frame using request-based API for proper buffer management
        request = self.camera.capture_request()
        try:
            # Get the frame data
            frame = request.make_array("main")

            # Convert RGB to grayscale for faster processing
            # For IR camera, all channels should be similar anyway
            gray = np.mean(frame, axis=2).astype(np.uint8)

            # Make a copy so we can release the request buffer
            gray_copy = gray.copy()

            return gray_copy
        finally:
            # Always release the request to free the buffer
            request.release()
        
    def stop(self):
        """Stop and cleanup the camera"""
        if self.camera:
            try:
                self.camera.stop()
                self.camera.close()
                logger.info("Camera stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping camera: {e}")


def test_camera():
    """Test function to verify camera operation"""
    camera = IRCamera()
    
    try:
        camera.start()
        
        print("Capturing 10 test frames...")
        for i in range(10):
            frame = camera.get_frame()
            # Find brightest point (should be IR reflection)
            max_val = frame.max()
            max_pos = np.unravel_index(frame.argmax(), frame.shape)
            print(f"Frame {i+1}: Shape={frame.shape}, Max brightness={max_val} at {max_pos}")
            time.sleep(0.1)
            
        print("Camera test successful!")
        
    finally:
        camera.stop()


if __name__ == "__main__":
    test_camera()
