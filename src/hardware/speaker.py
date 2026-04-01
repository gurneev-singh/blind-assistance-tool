import os
import tempfile
import logging
import threading
import queue
from gtts import gTTS
from playsound import playsound
from .interfaces import SpeakerInterface

logger = logging.getLogger(__name__)

class DesktopSpeaker(SpeakerInterface):
    """
    TTS using gTTS + playsound.
    Same architecture as Gurneev's original speaker.py:
    - say() is non-blocking (just queues the text)
    - Internal worker thread processes the queue
    - priority=True clears the queue first
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._stop_flag = False
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        logger.info("Speaker ready (gTTS).")

    def say(self, text: str, priority: bool = False):
        """Queue text for speech. Non-blocking. priority=True clears queue first."""
        if not text or self._stop_flag:
            return

        if priority:
            # Clear pending messages so this one plays next
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break

        logger.info(f"Queued: {text} (Priority: {priority})")
        self._queue.put(text)

    def clear(self):
        """Clear all pending speech."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def beep(self, frequency: int = 1200, duration: int = 150):
        """Play alert tone (disabled for now)."""
        pass

    def stop(self):
        self._stop_flag = True

    # ── Internal worker ──────────────────────────────────────

    def _worker(self):
        while not self._stop_flag:
            try:
                text = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                self._speak(text)
            except Exception as e:
                logger.error(f"TTS error: {e}")

    def _speak(self, text: str):
        """Generate MP3 via gTTS and play it."""
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.close()
        try:
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(tmp.name)
            logger.info(f"Speaking: {text}")
            playsound(tmp.name)
        finally:
            try:
                os.remove(tmp.name)
            except Exception:
                pass
