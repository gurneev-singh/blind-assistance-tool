import cv2
import base64
import logging
from groq import Groq
from src.utils.config import Config

logger = logging.getLogger(__name__)

class VisionEngine:
    """Cloud Vision using Groq (primary) with Gemini fallback."""

    # Groq vision models (LLaMA 3.3 70B is text-only, so we use the vision variants)
    GROQ_VISION_MODELS = [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.2-90b-vision-preview",
        "llama-3.2-11b-vision-preview",
    ]

    def __init__(self):
        self.groq_client = None
        self.groq_model = None

        if Config.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
                # Find first available vision model
                models = self.groq_client.models.list()
                available = [m.id for m in models.data]
                for candidate in self.GROQ_VISION_MODELS:
                    if candidate in available:
                        self.groq_model = candidate
                        logger.info(f"Groq Vision active: {candidate}")
                        break
                if not self.groq_model:
                    logger.warning("No Groq vision model found.")
            except Exception as e:
                logger.error(f"Failed to init Groq: {e}")
        else:
            logger.warning("No GROQ_API_KEY found. Cloud Vision disabled.")

    def analyze(self, frame, mode="describe") -> str:
        """Analyze frame using Groq vision."""
        if not self.groq_client or not self.groq_model:
            return "Cloud vision is not available. Check your API key."

        # Encode frame as base64 JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        b64_image = base64.b64encode(buffer).decode('utf-8')

        prompts = {
            "describe": (
                "You help a blind person. In ONE short sentence, "
                "say what is directly in front of them and any danger."
            ),
            "color": (
                "Name the main color you see in the center. "
                "Reply in 2 words only."
            ),
            "currency": (
                "What currency note is this? Reply like: '500 Rupee'. "
                "If none visible, say 'No note visible'."
            ),
            "read_text": (
                "Read ALL text visible in this image. Just say the text, nothing else. "
                "If no text is visible, say 'No text found'."
            ),
        }
        prompt = prompts.get(mode, prompts["describe"])

        # Try each vision model, fallback on rate limit
        models_to_try = [self.groq_model] + [
            m for m in self.GROQ_VISION_MODELS if m != self.groq_model
        ]

        for model in models_to_try:
            try:
                response = self.groq_client.chat.completions.create(
                    model=model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}"
                            }}
                        ]
                    }],
                    max_tokens=150,
                )
                result = response.choices[0].message.content.strip()
                if model != self.groq_model:
                    logger.info(f"Switched to fallback: {model}")
                    self.groq_model = model
                return result
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "rate" in error_str.lower():
                    logger.warning(f"{model} rate-limited. Trying next...")
                    continue
                else:
                    logger.error(f"Groq Vision failed: {e}")
                    return "Vision analysis failed. Please try again."

        return "All models are busy. Please wait and try again."
