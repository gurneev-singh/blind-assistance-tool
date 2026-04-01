import cv2
import time
import logging
import threading
from src.hardware.webcam import WebcamDriver
from src.hardware.speaker import DesktopSpeaker
from src.utils.config import setup_logging, Config
from src.intelligence.detector import MobileNetDetector
from src.intelligence.priority_engine import PriorityEngine
from src.intelligence.vision_engine import VisionEngine
from src.intelligence.face_detector import FaceDetector
from src.intelligence.ocr_reader import OCRReader

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    speaker = DesktopSpeaker()
    camera = WebcamDriver(device_index=Config.CAMERA_INDEX)
    detector = MobileNetDetector()
    engine = PriorityEngine()
    vlm = VisionEngine()
    
    # Offline Intelligence
    face_det = FaceDetector()
    ocr = OCRReader()

    # VLM state
    camera_lock = threading.Lock()
    vlm_busy = False
    vlm_lock = threading.Lock()

    def trigger_vlm(frame, mode, task_name):
        nonlocal vlm_busy
        with vlm_lock:
            if vlm_busy:
                return
            vlm_busy = True

        def run_task():
            nonlocal vlm_busy
            try:
                # Clear danger alerts, speak feedback
                speaker.clear()
                speaker.say(f"{task_name}...")

                # Ask Gemini (frame was captured BEFORE this thread started)
                result = vlm.analyze(frame, mode=mode)

                # Clear anything that queued during wait, speak result
                speaker.clear()
                speaker.say(result)
            except Exception as e:
                logger.error(f"VLM error: {e}")
            finally:
                # Keep muted a bit so the result finishes speaking
                time.sleep(2.0)
                with vlm_lock:
                    vlm_busy = False

        threading.Thread(target=run_task, daemon=True).start()

    try:
        speaker.say("Gurneev's Smart Glasses Active.")
        camera.start()

        while True:
            with camera_lock:
                frame = camera.read()
            if frame is None:
                continue

            # Local detection
            detections = detector.detect(frame)

            # Hazard alerts — MUTED when VLM is active
            if not vlm_busy:
                alerts = engine.process_detections(detections)
                for alert in alerts:
                    speaker.say(alert['msg'], priority=(alert['level'] == 'CRITICAL'))

            # On-request intelligence (capture frame NOW, process in background)
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' '):
                trigger_vlm(frame.copy(), "describe", "Describing scene")
            elif key == ord('c'):
                trigger_vlm(frame.copy(), "color", "Checking color")
            elif key == ord('n'):
                trigger_vlm(frame.copy(), "currency", "Checking currency")
            elif key == ord('f'):
                # Face Detection (Local, instant)
                with vlm_lock:
                    if not vlm_busy:
                        speaker.clear()
                        speaker.say(face_det.describe(frame))
            elif key == ord('r'):
                # Text Reading (Cloud - much more accurate than offline OCR)
                trigger_vlm(frame.copy(), "read_text", "Reading text")

            # UI overlay
            for d in detections:
                cv2.rectangle(frame, (d['box'][0], d['box'][1]),
                              (d['box'][2], d['box'][3]), (0, 255, 0), 2)
            cv2.imshow("Gurneev's Smart Glasses", frame)

            if key == ord('q'):
                break

    except Exception as e:
        logger.error(f"System error: {e}")

    finally:
        speaker.stop()
        camera.release()
        cv2.destroyAllWindows()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down gracefully.")
