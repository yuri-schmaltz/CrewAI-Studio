"""Database helpers built on top of SQLAlchemy."""

from functools import lru_cache
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

from .config import load_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine instance."""

    settings = load_settings()
    return create_engine(settings.database.url, echo=settings.database.echo, future=True)


def get_db_connection() -> Connection:
    """Provide a raw SQLAlchemy connection."""

    return get_engine().connect()


def iter_rows(result_proxy) -> Iterator[dict]:
    """Yield result rows as dictionaries, normalising SQLAlchemy versions."""

    if hasattr(result_proxy, "mappings"):
        yield from result_proxy.mappings()
    else:  # pragma: no cover - compatibility path for older SQLAlchemy
        columns = result_proxy.keys()
        for row in result_proxy:
            yield dict(zip(columns, row))
