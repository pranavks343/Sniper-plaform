from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.models.database.base import Base
from app.models.database.namespaces import ALL_SCHEMAS

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_recycle=settings.database_pool_recycle_seconds,
    future=True,
)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    # Import models for metadata registration side-effects.
    import app.models.database  # noqa: F401
    from app.models.database.user import User, UserPreference

    async with engine.begin() as connection:
        for schema in ALL_SCHEMAS:
            await connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        # Drop hypertable candidates so they can be recreated with composite PK (id, as_of)
        # required by TimescaleDB: partitioning column must be in primary key
        await connection.execute(text('DROP TABLE IF EXISTS portfolio.position_snapshots CASCADE'))
        await connection.execute(text('DROP TABLE IF EXISTS analytics.pnl_intraday CASCADE'))
        await connection.run_sync(Base.metadata.create_all)
        await connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb') THEN
                        CREATE EXTENSION IF NOT EXISTS timescaledb;
                    END IF;
                END
                $$;
                """
            )
        )
        await connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
                        PERFORM create_hypertable('portfolio.position_snapshots', 'as_of', if_not_exists => TRUE, migrate_data => TRUE);
                        PERFORM create_hypertable('analytics.pnl_intraday', 'as_of', if_not_exists => TRUE, migrate_data => TRUE);
                    END IF;
                END
                $$;
                """
            )
        )

    # Ensure bootstrap/system user exists so default foreign keys always resolve.
    async with SessionLocal() as session:
        created_user = False
        created_pref = False
        result = await session.execute(select(User).where(User.id == settings.default_user_uuid))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                id=settings.default_user_uuid,
                email=f'{settings.default_user_uuid}@local.sniper',
                role='system',
                is_active=True,
            )
            session.add(user)
            created_user = True
        pref_result = await session.execute(select(UserPreference).where(UserPreference.user_id == settings.default_user_uuid))
        pref = pref_result.scalar_one_or_none()
        if pref is None:
            session.add(
                UserPreference(
                    id=str(uuid4()),
                    user_id=settings.default_user_uuid,
                    timezone='Asia/Kolkata',
                    theme='dark',
                    preferences_json='{}',
                )
            )
            created_pref = True
        if created_user or created_pref:
            await session.commit()
