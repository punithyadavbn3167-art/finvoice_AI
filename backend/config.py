
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "FinVoice AI")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL = os.getenv("DATABASE_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    def validate(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is required.")

        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required.")


settings = Settings()
