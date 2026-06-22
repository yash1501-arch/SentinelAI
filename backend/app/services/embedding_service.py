from sentence_transformers import SentenceTransformer
from app.core.config import settings
from loguru import logger
from typing import List


class EmbeddingService:
    _model: SentenceTransformer = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL_NAME}")
        return cls._model

    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        model = cls.get_model()
        embeddings = model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    @classmethod
    def embed_query(cls, query: str) -> List[float]:
        model = cls.get_model()
        embedding = model.encode(query, show_progress_bar=False)
        return embedding.tolist()

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        return cls.embed_query(text)
