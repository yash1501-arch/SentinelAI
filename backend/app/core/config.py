from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    APP_NAME: str = "SentinelAI"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "change-this-to-a-secure-random-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Zoho Catalyst
    CATALYST_PROJECT_ID: Optional[str] = None
    CATALYST_CLIENT_ID: Optional[str] = None
    CATALYST_CLIENT_SECRET: Optional[str] = None
    CATALYST_REFRESH_TOKEN: Optional[str] = None
    CATALYST_REGION: str = "us_west"


    # PostgreSQL (direct URL takes precedence over individual fields)
    POSTGRES_URL: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sentinelai"
    POSTGRES_USER: str = "sentinelai"
    POSTGRES_PASSWORD: str = "sentinelai_pass"

    # Neo4j Aura
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "sentinelai_neo4j"

    # Qdrant Cloud
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # OpenAI / Groq
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    MAPBOX_ACCESS_TOKEN: str = ""

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    LOG_LEVEL: str = "INFO"

    @property
    def DATABASE_URL(self) -> str:
        if self.POSTGRES_URL:
            url = self.POSTGRES_URL
            if url.startswith("postgres://"):
                url = "postgresql+asyncpg://" + url[len("postgres://"):]
            elif url.startswith("postgresql://"):
                url = "postgresql+asyncpg://" + url[len("postgresql://"):]
            # asyncpg uses ssl=require instead of sslmode=require
            url = url.replace("sslmode=require", "ssl=require")
            return url
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        if self.POSTGRES_URL:
            url = self.POSTGRES_URL
            if url.startswith("postgres://"):
                url = "postgresql+psycopg2://" + url[len("postgres://"):]
            return url
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def QDRANT_URL(self) -> str:
        host = self.QDRANT_HOST
        if host.startswith("http://") or host.startswith("https://"):
            return host
        return f"http://{host}:{self.QDRANT_PORT}"

    @property
    def REDIS_URL(self) -> str:
        host = self.REDIS_HOST
        # Cloud Redis typically uses rediss:// (TLS)
        scheme = "rediss" if "." in host and host != "localhost" else "redis"
        if self.REDIS_PASSWORD:
            return f"{scheme}://:{self.REDIS_PASSWORD}@{host}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"{scheme}://{host}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
