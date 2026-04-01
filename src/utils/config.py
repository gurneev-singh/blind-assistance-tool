import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration for the project."""
    
    # API KEYS
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # SYSTEM SETTINGS
    DEBUG = os.getenv("DEBUG", "False") == "True"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    BEEP_ENABLED = os.getenv("BEEP_ENABLED", "False") == "True"
    
    # HARDWARE
    CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", 0))
    
    # OFFLINE INTELLIGENCE
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
