from openai import AsyncOpenAI
from app.core.config import settings


def create_openai_client() -> AsyncOpenAI:
    kwargs = {"api_key": settings.OPENAI_API_KEY}
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL
    return AsyncOpenAI(**kwargs)
