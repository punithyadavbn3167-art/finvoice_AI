
from sqlalchemy import create_engine
from backend.config import settings

if not settings.DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. Check your environment configuration."
    )

engine = create_engine(settings.DATABASE_URL)
