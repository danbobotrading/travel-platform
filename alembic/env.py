"""
Alembic migration environment for Travel Platform.

This module configures the Alembic migration environment for SQLAlchemy 2.0
with async support for PostgreSQL.
"""

import asyncio
from logging.config import fileConfig
from typing import Any

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Import your models and Base
from src.database.models.base import Base
from src.database.models.user import User
from src.database.models.flight import Flight, FlightSearch, FlightBooking
from src.database.models.hotel import Hotel, HotelSearch, HotelBooking
from src.database.models.payment import Payment, PaymentMethod
from src.database.models.session import Session
from src.core.config.settings import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set sqlalchemy.url from settings if not already set
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", str(settings.database_url_decrypted))

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        version_table="alembic_version",
        version_table_schema=None,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Any) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        version_table="alembic_version",
        version_table_schema=None,
        # Enable batch mode for SQLite (not needed for PostgreSQL but safe)
        render_as_batch=True,
        # Include table comments
        include_object_comments=True,
        # Don't include schemas we don't own
        include_schemas=False,
        # Add these for better autogenerate
        user_module_prefix="src.database.models.",
        process_revision_directives=None,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
