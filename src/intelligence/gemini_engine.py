import cv2
import PIL.Image
import logging
from google import genai
from src.utils.config import Config

logger = logging.getLogger(__name__)

class GeminiEngine:
    """Vision brain using Google's Gemini (new google-genai SDK)."""

    # Models to try in order of preference
    CANDIDATE_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
        "gemini-1.5-flash",
    ]

    def __init__(self):
        self.client = None
        self.model_name = None

        if not Config.GEMINI_API_KEY:
            logger.warning("No GEMINI_API_KEY found. Pro Vision disabled.")
            return

        try:
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            
            # Fetch available models (doesn't use generation quota)
            available_models = [m.name for m in self.client.models.list()]
            
            # Find the best available Flash model
            for name in self.CANDIDATE_MODELS:
                full_name = f"models/{name}"
                if full_name in available_models or name in available_models:
                    self.model_name = name
                    logger.info(f"Gemini Brain active: {name}")
                    break

            if not self.model_name:
                logger.error("No working Gemini model found for your API key.")
        except Exception as e:
            logger.error(f"Failed to init Gemini client: {e}")

    def analyze(self, frame, mode="describe") -> str:
        """Send a frame to Gemini and get a text response.
        Auto-falls back to other models if rate-limited (429)."""
        if not self.client:
            return "Gemini is not available. Check your API key."

        # Convert OpenCV BGR to RGB PIL Image
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(rgb)

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
        }
        prompt = prompts.get(mode, prompts["describe"])

        # Try the primary model first, then fall back to others on rate limit
        models_to_try = [self.model_name] + [
            m for m in self.CANDIDATE_MODELS if m != self.model_name
        ]

        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=[prompt, img],
                )
                if model != self.model_name:
                    logger.info(f"Switched to fallback model: {model}")
                    self.model_name = model
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"{model} is rate-limited. Trying next model...")
                    continue
                else:
                    logger.error(f"Gemini Vision failed: {e}")
                    return "Vision analysis failed. Please try again."

        return "All Gemini models are rate-limited. Please wait a minute and try again."
