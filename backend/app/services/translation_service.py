"""
Translation service for SentinelAI.

Provides Kannada ↔ English translation using LLM-based translation
with fallback. IndicTrans2 would be the ideal production solution
for offline/high-throughput, but LLM translation works well for
interactive conversational use.
"""
from typing import Optional
from loguru import logger

from app.core.config import settings
from app.services.openai_client import create_openai_client

SUPPORTED_LANGUAGES = {"en", "kn", "hi", "ta", "te", "mr"}

TRANSLATE_TO_EN_PROMPT = """Translate the following {source_lang} text to English. 
Return ONLY the English translation, nothing else.

Text: {text}"""

TRANSLATE_FROM_EN_PROMPT = """Translate the following English text to {target_lang}. 
Return ONLY the {target_lang} translation, nothing else.
Maintain the markdown formatting if present.

Text: {text}"""

LANGUAGE_NAMES = {
    "kn": "Kannada",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
}


class TranslationService:
    """LLM-based translation service for multilingual support."""

    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            cls._client = create_openai_client()
        return cls._client

    @classmethod
    async def translate_to_english(cls, text: str, source_lang: str) -> str:
        """Translate input text from source language to English."""
        if source_lang == "en" or not text.strip():
            return text

        lang_name = LANGUAGE_NAMES.get(source_lang, source_lang)

        try:
            client = cls._get_client()
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": TRANSLATE_TO_EN_PROMPT.format(
                        source_lang=lang_name, text=text
                    )},
                ],
                temperature=0.1,
                max_tokens=500,
            )
            translated = response.choices[0].message.content.strip()
            logger.debug(f"Translated {source_lang}→en: '{text[:50]}' → '{translated[:50]}'")
            return translated
        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            return text  # Return original if translation fails

    @classmethod
    async def translate_from_english(cls, text: str, target_lang: str) -> str:
        """Translate English text to target language."""
        if target_lang == "en" or not text.strip():
            return text

        lang_name = LANGUAGE_NAMES.get(target_lang, target_lang)

        try:
            client = cls._get_client()
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": TRANSLATE_FROM_EN_PROMPT.format(
                        target_lang=lang_name, text=text
                    )},
                ],
                temperature=0.1,
                max_tokens=1500,
            )
            translated = response.choices[0].message.content.strip()
            logger.debug(f"Translated en→{target_lang}: '{text[:50]}' → '{translated[:50]}'")
            return translated
        except Exception as e:
            logger.error(f"Translation from English failed: {e}")
            return text  # Return English if translation fails

    @classmethod
    async def detect_language(cls, text: str) -> str:
        """Detect the language of input text."""
        # Simple heuristic: check for Kannada Unicode range (U+0C80-U+0CFF)
        kannada_chars = sum(1 for c in text if '\u0C80' <= c <= '\u0CFF')
        hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        telugu_chars = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')

        total = len(text)
        if total == 0:
            return "en"

        if kannada_chars / total > 0.3:
            return "kn"
        if hindi_chars / total > 0.3:
            return "hi"
        if tamil_chars / total > 0.3:
            return "ta"
        if telugu_chars / total > 0.3:
            return "te"

        return "en"

    @classmethod
    def is_supported(cls, lang: str) -> bool:
        """Check if a language is supported."""
        return lang in SUPPORTED_LANGUAGES
