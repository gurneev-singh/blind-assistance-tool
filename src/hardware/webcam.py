import cv2
import numpy as np
import logging
from .interfaces import CameraInterface

logger = logging.getLogger(__name__)

class WebcamDriver(CameraInterface):
    """Implementation of CameraInterface for standard USB webcams."""

    def __init__(self, device_index=0):
        self.device_index = device_index
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            logger.error(f"Failed to open webcam at index {self.device_index}")
            raise RuntimeError("Camera not found")
        logger.info(f"Webcam started at index {self.device_index}")

    def read(self) -> np.ndarray:
        if self.cap is None:
            return None
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to capture frame from webcam")
            return None
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            logger.info("Webcam released")
