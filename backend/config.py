"""
TrendPulse Configuration
Loads environment variables and exposes a single settings object.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # LinkedIn API
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    LINKEDIN_PERSON_URN: str = os.getenv("LINKEDIN_PERSON_URN", "")

    # Reddit (legacy, kept for fallback)
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USERNAME: str = os.getenv("REDDIT_USERNAME", "")
    REDDIT_PASSWORD: str = os.getenv("REDDIT_PASSWORD", "")
    REDDIT_TARGET_SUBREDDIT: str = os.getenv("REDDIT_TARGET_SUBREDDIT", "test")

    POST_SCHEDULE_HOUR: int = int(os.getenv("POST_SCHEDULE_HOUR", "9"))
    POST_SCHEDULE_MINUTE: int = int(os.getenv("POST_SCHEDULE_MINUTE", "0"))
    SWYTCHCODE_AVAILABLE: bool = False

    def __init__(self):
        try:
            import swytchcode_runtime  # noqa: F401
            self.SWYTCHCODE_AVAILABLE = True
        except ImportError:
            self.SWYTCHCODE_AVAILABLE = False

    def validate(self) -> dict:
        return {
            "newsapi": bool(self.NEWSAPI_KEY and self.NEWSAPI_KEY != "your_newsapi_key_here"),
            "groq": bool(self.GROQ_API_KEY and self.GROQ_API_KEY != "your_groq_api_key_here"),
            "linkedin": bool(self.LINKEDIN_ACCESS_TOKEN),
            "swytchcode": self.SWYTCHCODE_AVAILABLE,
        }


settings = Settings()
