from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db, async_session_factory
from app.db.seed import seed_database
from app.api.v1.endpoints import auth, chat, cases, analytics, network, export, admin, voice
from app.api.v1.endpoints import catalyst_func
from app.api.v1.endpoints import alerts as alerts_router
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}")
    await init_db()
    async with async_session_factory() as session:
        await seed_database(session)

    # Seed official Karnataka Police schema tables
    async with async_session_factory() as session:
        from app.db.seed_official import seed_official_schema
        await seed_official_schema(session)

    # Initialize optional services (don't crash if unavailable)
    try:
        from app.services.qdrant_service import QdrantService
        await QdrantService.initialize_collections()
        logger.info("Qdrant collections initialized")
    except Exception as e:
        logger.warning(f"Qdrant initialization skipped: {e}")

    try:
        from app.services.neo4j_service import Neo4jService
        driver = await Neo4jService.get_driver()
        logger.info("Neo4j connection established")
    except Exception as e:
        logger.warning(f"Neo4j initialization skipped: {e}")

    # Initialize Redis
    try:
        from app.services.redis_service import RedisService
        await RedisService.get_client()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis initialization skipped: {e}")

    yield

    # Cleanup
    try:
        from app.services.redis_service import RedisService
        await RedisService.close()
    except Exception:
        pass
    try:
        from app.services.neo4j_service import Neo4jService
        await Neo4jService.close()
    except Exception:
        pass
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="Connecting Crimes, Predicting Threats, Empowering Investigations",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Custom middleware (these run AFTER CORS in request flow)
from app.core.middleware import RateLimitMiddleware, AuditLogMiddleware
app.add_middleware(AuditLogMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(chat.router, prefix=f"{settings.API_V1_PREFIX}/chat", tags=["Conversational AI"])
app.include_router(cases.router, prefix=f"{settings.API_V1_PREFIX}/cases", tags=["Cases"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics"])
app.include_router(network.router, prefix=f"{settings.API_V1_PREFIX}/network", tags=["Network Analysis"])
app.include_router(export.router, prefix=f"{settings.API_V1_PREFIX}/export", tags=["Export"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(catalyst_func.router, prefix=f"{settings.API_V1_PREFIX}/catalyst", tags=["Zoho Catalyst"])
app.include_router(voice.router, prefix=f"{settings.API_V1_PREFIX}/voice", tags=["Voice Processing"])
app.include_router(alerts_router.router, prefix=f"{settings.API_V1_PREFIX}/alerts", tags=["Smart Alerts"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "tagline": "Connecting Crimes, Predicting Threats, Empowering Investigations",
        "version": "1.0.0",
    }
