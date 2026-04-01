import logging
import threading
import queue

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages audio prioritization and queuing for Gurneev's glasses."""

    def __init__(self, speaker):
        self.speaker = speaker
        self.msg_queue = queue.PriorityQueue()
        self._stop_event = threading.Event()
        self._process_thread = threading.Thread(target=self._worker, daemon=True)
        self._process_thread.start()

    def submit(self, level: str, message: str):
        """Submit a message to the queue based on level."""
        # Priority mapping for queue (lower number = higher priority)
        prio_map = {
            'CRITICAL': 1,
            'WARNING': 2,
            'INFO': 3
        }
        prio = prio_map.get(level, 4)
        self.msg_queue.put((prio, message))

    def clear(self):
        """Clear all pending messages from the queue."""
        logger.info("Clearing speech queue.")
        while not self.msg_queue.empty():
            try:
                self.msg_queue.get_nowait()
                self.msg_queue.task_done()
            except queue.Empty:
                break
        self.speaker.stop()

    def _worker(self):
        """Background worker to process the speech queue."""
        while not self._stop_event.is_set():
            try:
                # Wait for next message
                prio, message = self.msg_queue.get(timeout=1.0)
                
                # Critical messages (prio 1) get a beep and immediate output
                is_critical = (prio == 1)
                
                # Request speech from speaker driver
                self.speaker.say(message, priority=is_critical)
                
                self.msg_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"AudioManager worker error: {e}")

    def stop(self):
        self._stop_event.set()
        self._process_thread.join()
        self.speaker.stop()
