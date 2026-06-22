from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from loguru import logger


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    def __init__(self, **kwargs):
        for col in self.__table__.columns:
            if col.name not in kwargs and col.default is not None:
                val = col.default.arg
                if not callable(val):
                    kwargs.setdefault(col.name, val)
        for k, v in kwargs.items():
            setattr(self, k, v)


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def get_catalyst_db():
    try:
        from zcatalyst import datastore
        datastore_table = datastore.table(settings.CATALYST_DATABASE_KEY)
        yield datastore_table
    except ImportError:
        logger.warning("Zoho Catalyst SDK not available, using SQLAlchemy fallback")
        async for session in get_db():
            yield session
    except Exception as e:
        logger.error(f"Catalyst DataStore error: {e}")
        async for session in get_db():
            yield session
