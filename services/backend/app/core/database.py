import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


# Engine creation with connection recycling
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining an isolated database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def scoped_tenant_session(
    principal_id: uuid.UUID | str,
) -> AsyncGenerator[AsyncSession, None]:
    """Context manager for establishing a session scoped to a specific tenant/principal.

    Sets transaction-local tenant context for RLS in PostgreSQL, and ensures
    clean context cleanup on release (preventing pool leakage - T03).
    """
    pid_str = str(principal_id)
    async with async_session_factory() as session:
        is_postgres = session.bind.dialect.name == "postgresql" if session.bind else False
        if is_postgres:
            # Set transaction-local setting for Postgres RLS
            await session.execute(
                text("SET LOCAL app.current_principal_id = :pid"),
                {"pid": pid_str},
            )
        # Store on session info dictionary for application-layer RLS enforcement
        session.info["current_principal_id"] = pid_str
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            if is_postgres:
                try:
                    await session.execute(text("RESET app.current_principal_id"))
                except SQLAlchemyError as exc:
                    logger.warning("Failed to reset app.current_principal_id: %s", exc)
            session.info.pop("current_principal_id", None)
            await session.close()
