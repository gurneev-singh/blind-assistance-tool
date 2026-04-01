import cv2
import logging

logger = logging.getLogger(__name__)

class FaceDetector:
    """Detects human faces and estimates their position without internet."""

    def __init__(self):
        # We use the built-in OpenCV Haar Cascade (no download needed)
        try:
            self.cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            logger.info("FaceDetector (Offline) ready.")
        except Exception as e:
            logger.error(f"Failed to load Face Cascade: {e}")
            self.cascade = None

    def describe(self, frame) -> str:
        """Scan image and return a spoken summary of what it sees."""
        if self.cascade is None:
            return "Face detection system is unavailable."

        # Convert to grayscale for faster processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        # scaleFactor=1.1, minNeighbors=5, minSize=(40,40)
        rects = self.cascade.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))

        if len(rects) == 0:
            return "No people detected nearby."

        h, w = frame.shape[:2]
        faces = []

        for (x, y, fw, fh) in rects:
            area_ratio = (fw * fh) / (w * h)
            position = self._get_position(x, fw, w)
            size_label = self._get_size(area_ratio)
            faces.append({"position": position, "size": size_label})

        count = len(faces)
        if count == 1:
            f = faces[0]
            return f"One person detected {f['size']} on your {f['position']}."
        else:
            positions = ", ".join(f"{f['size']} on your {f['position']}" for f in faces[:3])
            return f"{count} people detected. {positions}."

    def _get_position(self, x: int, fw: int, frame_width: int) -> str:
        centre_x = x + fw / 2
        third = frame_width / 3
        if centre_x < third:
            return "left"
        elif centre_x < 2 * third:
            return "center"
        else:
            return "right"

    def _get_size(self, area_ratio: float) -> str:
        if area_ratio > 0.25:
            return "very close"
        elif area_ratio > 0.05: # FACE_CLOSE_THRESHOLD
            return "nearby"
        else:
            return "at a distance"
