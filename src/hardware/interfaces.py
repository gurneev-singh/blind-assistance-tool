import cv2
import numpy as np
from abc import ABC, abstractmethod

class CameraInterface(ABC):
    """Abstract interface for any camera hardware (Webcam, RPi Camera, etc.)"""
    
    @abstractmethod
    def start(self):
        """Initialize the camera."""
        pass

    @abstractmethod
    def read(self) -> np.ndarray:
        """Capture a frame from the camera."""
        pass

    @abstractmethod
    def release(self):
        """Release the camera resources."""
        pass

class SpeakerInterface(ABC):
    """Abstract interface for any audio output (System Audio, Bluetooth, etc.)"""

    @abstractmethod
    def say(self, message: str, priority: bool = False):
        """Output a text message as speech."""
        pass

    @abstractmethod
    def beep(self, frequency: int = 1000, duration: int = 100):
        """Play a short alert tone."""
        pass

    @abstractmethod
    def stop(self):
        """Stop any ongoing speech."""
        pass
