from app.core.config import settings
from loguru import logger
from typing import List

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed, embeddings will use fallback")


class EmbeddingService:
    _model = None

    @classmethod
    def get_model(cls):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return None
        if cls._model is None:
            try:
                cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL_NAME}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                return None
        return cls._model

    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        model = cls.get_model()
        if model is None:
            # Return zero vectors as fallback
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]
        embeddings = model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    @classmethod
    def embed_query(cls, query: str) -> List[float]:
        model = cls.get_model()
        if model is None:
            return [0.0] * settings.EMBEDDING_DIMENSION
        embedding = model.encode(query, show_progress_bar=False)
        return embedding.tolist()

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        return cls.embed_query(text)
