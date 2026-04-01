import cv2
import base64
import logging
from groq import Groq
from src.utils.config import Config

logger = logging.getLogger(__name__)

class VLMEngine:
    """The 'Cloud Brain' for详细 detailed scene, color, and currency analysis."""

    def __init__(self):
        self.client = None
        if Config.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("Groq VLM Engine initialized.")
            except Exception as e:
                logger.error(f"Failed to init Groq client: {e}")

    def _encode_image(self, frame):
        """Convert OpenCV frame to base64 for Groq."""
        # Resize for faster upload (MobileNet-SSD size or slightly larger)
        small_frame = cv2.resize(frame, (640, 480))
        _, buffer = cv2.imencode(".jpg", small_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        return base64.b64encode(buffer).decode("utf-8")

    def analyze(self, frame, mode="describe") -> str:
        """Send a request to LLaVA via Groq."""
        if not self.client:
            return "Sorry, Groq API key is missing. Please check your .env file."

        base64_image = self._encode_image(frame)
        
        # Prompts based on Gurneev's requirements
        prompts = {
            "describe": "You are a helpful assistant for a blind person. Concisely describe this scene, focusing on people and obstacles.",
            "color": "Look at the object in the very center of this image. What is its dominant color? Answer in 2-3 words.",
            "currency": "Identify the currency note and its value seen in this image. If no note is visible, say 'I cannot see any currency'."
        }
        
        prompt = prompts.get(mode, prompts["describe"])

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model="llava-v1.5-7b-4096-preview", # High-speed vision model on Groq
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"VLM Analysis failed: {e}")
            return "Vision analysis failed."
