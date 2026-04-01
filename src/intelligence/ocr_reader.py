import cv2
import numpy as np
import pytesseract
import logging
from src.utils.config import Config

logger = logging.getLogger(__name__)

class OCRReader:
    """Extracts and cleans text from a camera frame using Tesseract OCR."""

    def __init__(self):
        # Point to the Tesseract executable path specified in config
        if Config.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
            
        # --psm 11: Sparse text with OSD (good for real world signs/labels)
        # --oem 3: Default OCR engine mode
        self._config = "--psm 11 --oem 3"
        logger.info("OCR Reader initialized.")

    def read(self, frame) -> str:
        """Extract text from frame. Returns the text or a failure message."""
        try:
            processed = self._preprocess(frame)
            raw_text = pytesseract.image_to_string(processed, config=self._config)
            cleaned = self._clean(raw_text)

            if cleaned:
                # Cap at 100 chars so it doesn't speak forever
                if len(cleaned) > 100:
                    cleaned = cleaned[:100]
                return f"I can read: {cleaned}"
            else:
                return "No readable text found in view."

        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract not found. Path might be wrong.")
            return "Text reading failed. Please install Tesseract on your computer."
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return "I could not read the text right now."

    def _preprocess(self, frame) -> np.ndarray:
        """Improve OCR accuracy with image processing (grayscale + thresholding)."""
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        scaled = cv2.resize(grey, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        # Adaptive Threshold to handle shadows / varied lighting
        thresh = cv2.adaptiveThreshold(
            scaled, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh

    def _clean(self, text: str) -> str:
        """Remove noise characters and single letters from OCR output."""
        lines = [
            line.strip()
            for line in text.splitlines()
            if len(line.strip()) > 2  # Skip tiny noise
        ]
        return " ".join(lines)
