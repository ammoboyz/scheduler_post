import logging

from app.database.models import Base, Config

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)


log = logging.getLogger('database.engine')

async def create_tables(engine: AsyncEngine) -> None:
    """
    Create tables from models.

    :param AsyncEngine engine: Async engine
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        config = await conn.scalar(
            select(Config)
        )

        if not config:
            await conn.execute(
                insert(Config)
            )

        log.info('Tables created successfully')


async def create_sessionmaker() -> async_sessionmaker:
    """
    Create an async sessionmaker for the database and create tables if they don't exist.

    :param str database: Postgres database credentials
    :param bool debug: Debug mode, defaults to False
    :return async_sessionmaker: Async sessionmaker (sessionmaker with AsyncSession class)
    """

    engine = create_async_engine(
        url="sqlite+aiosqlite:///app/database/database.db",
        future=True,
    )
    log.info('Connected to database')

    await create_tables(engine)
    return async_sessionmaker(engine, expire_on_commit=False)
